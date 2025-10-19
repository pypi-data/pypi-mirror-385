'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..utils import (CONFIG_NAME, FLAX_WEIGHTS_NAME, SAFE_WEIGHTS_INDEX_NAME, SAFETENSORS_WEIGHTS_NAME, WEIGHTS_INDEX_NAME, WEIGHTS_NAME, _add_variant, _get_checkpoint_shard_files, _get_model_file,
deprecate, is_sapiens_accelerator_available, is_sapiens_machine_available, is_sapiens_machine_version, is_torch_version)
from .model_loading_utils import _determine_device_map, _fetch_index_file, _fetch_index_file_legacy, _load_state_dict_into_model, _merge_sharded_checkpoints, load_model_dict_into_meta, load_state_dict
from ..utils.hub_utils import PushToHubMixin, load_or_create_model_card, populate_model_card
from huggingface_hub import create_repo, split_torch_state_dict_into_shards
from ..quantizers import DiffusersAutoQuantizer, DiffusersQuantizer
from ..quantizers.quantization_config import QuantizationMethod
from typing import Any, Callable, List, Optional, Tuple, Union
from huggingface_hub.utils import validate_hf_hub_args
from functools import partial, wraps
from collections import OrderedDict
from torch import Tensor, nn
from .. import __version__
from pathlib import Path
import safetensors
import itertools
import inspect
import torch
import json
import copy
import os
import re
_REGEX_SHARD = re.compile('(.*?)-\\d{5}-of-\\d{5}')
if is_torch_version('>=', '1.9.0'): _LOW_CPU_MEM_USAGE_DEFAULT = True
else: _LOW_CPU_MEM_USAGE_DEFAULT = False
if is_sapiens_accelerator_available(): import sapiens_accelerator
def get_parameter_device(parameter: torch.nn.Module) -> torch.device:
    try:
        parameters_and_buffers = itertools.chain(parameter.parameters(), parameter.buffers())
        return next(parameters_and_buffers).device
    except StopIteration:
        def find_tensor_attributes(module: torch.nn.Module) -> List[Tuple[str, Tensor]]:
            tuples = [(k, v) for k, v in module.__dict__.items() if torch.is_tensor(v)]
            return tuples
        gen = parameter._named_members(get_members_fn=find_tensor_attributes)
        first_tuple = next(gen)
        return first_tuple[1].device
def get_parameter_dtype(parameter: torch.nn.Module) -> torch.dtype:
    last_dtype = None
    for param in parameter.parameters():
        last_dtype = param.dtype
        if param.is_floating_point(): return param.dtype
    for buffer in parameter.buffers():
        last_dtype = buffer.dtype
        if buffer.is_floating_point(): return buffer.dtype
    if last_dtype is not None: return last_dtype
    def find_tensor_attributes(module: nn.Module) -> List[Tuple[str, Tensor]]:
        tuples = [(k, v) for k, v in module.__dict__.items() if torch.is_tensor(v)]
        return tuples
    gen = parameter._named_members(get_members_fn=find_tensor_attributes)
    last_tuple = None
    for tuple in gen:
        last_tuple = tuple
        if tuple[1].is_floating_point(): return tuple[1].dtype
    if last_tuple is not None: return last_tuple[1].dtype
class ModelMixin(torch.nn.Module, PushToHubMixin):
    config_name = CONFIG_NAME
    _automatically_saved_args = ['_diffusers_version', '_class_name', '_name_or_path']
    _supports_gradient_checkpointing = False
    _keys_to_ignore_on_load_unexpected = None
    _no_split_modules = None
    _keep_in_fp32_modules = None
    def __init__(self): super().__init__()
    def __getattr__(self, name: str) -> Any:
        is_in_config = '_internal_dict' in self.__dict__ and hasattr(self.__dict__['_internal_dict'], name)
        is_attribute = name in self.__dict__
        if is_in_config and (not is_attribute):
            deprecation_message = f"Accessing config attribute `{name}` directly via '{type(self).__name__}' object attribute is deprecated. Please access '{name}' over '{type(self).__name__}'s config object instead, e.g. 'unet.config.{name}'."
            deprecate('direct config name access', '1.0.0', deprecation_message, standard_warn=False, stacklevel=3)
            return self._internal_dict[name]
        return super().__getattr__(name)
    @property
    def is_gradient_checkpointing(self) -> bool: return any((hasattr(m, 'gradient_checkpointing') and m.gradient_checkpointing for m in self.modules()))
    def enable_gradient_checkpointing(self) -> None:
        if not self._supports_gradient_checkpointing: raise ValueError(f'{self.__class__.__name__} does not support gradient checkpointing.')
        self.apply(partial(self._set_gradient_checkpointing, value=True))
    def disable_gradient_checkpointing(self) -> None:
        if self._supports_gradient_checkpointing: self.apply(partial(self._set_gradient_checkpointing, value=False))
    def set_use_npu_flash_attention(self, valid: bool) -> None:
        def fn_recursive_set_npu_flash_attention(module: torch.nn.Module):
            if hasattr(module, 'set_use_npu_flash_attention'): module.set_use_npu_flash_attention(valid)
            for child in module.children(): fn_recursive_set_npu_flash_attention(child)
        for module in self.children():
            if isinstance(module, torch.nn.Module): fn_recursive_set_npu_flash_attention(module)
    def enable_npu_flash_attention(self) -> None: self.set_use_npu_flash_attention(True)
    def disable_npu_flash_attention(self) -> None: self.set_use_npu_flash_attention(False)
    def set_use_xla_flash_attention(self, use_xla_flash_attention: bool, partition_spec: Optional[Callable]=None) -> None:
        def fn_recursive_set_flash_attention(module: torch.nn.Module):
            if hasattr(module, 'set_use_xla_flash_attention'): module.set_use_xla_flash_attention(use_xla_flash_attention, partition_spec)
            for child in module.children(): fn_recursive_set_flash_attention(child)
        for module in self.children():
            if isinstance(module, torch.nn.Module): fn_recursive_set_flash_attention(module)
    def enable_xla_flash_attention(self, partition_spec: Optional[Callable]=None): self.set_use_xla_flash_attention(True, partition_spec)
    def disable_xla_flash_attention(self): self.set_use_xla_flash_attention(False)
    def set_use_memory_efficient_attention_xformers(self, valid: bool, attention_op: Optional[Callable]=None) -> None:
        def fn_recursive_set_mem_eff(module: torch.nn.Module):
            if hasattr(module, 'set_use_memory_efficient_attention_xformers'): module.set_use_memory_efficient_attention_xformers(valid, attention_op)
            for child in module.children(): fn_recursive_set_mem_eff(child)
        for module in self.children():
            if isinstance(module, torch.nn.Module): fn_recursive_set_mem_eff(module)
    def enable_xformers_memory_efficient_attention(self, attention_op: Optional[Callable]=None) -> None:
        """Examples:"""
        self.set_use_memory_efficient_attention_xformers(True, attention_op)
    def disable_xformers_memory_efficient_attention(self) -> None: self.set_use_memory_efficient_attention_xformers(False)
    def save_pretrained(self, save_directory: Union[str, os.PathLike], is_main_process: bool=True, save_function: Optional[Callable]=None, safe_serialization: bool=True, variant: Optional[str]=None,
    max_shard_size: Union[int, str]='10GB', push_to_hub: bool=False, **kwargs):
        if os.path.isfile(save_directory): return
        hf_quantizer = getattr(self, 'hf_quantizer', None)
        if hf_quantizer is not None:
            quantization_serializable = hf_quantizer is not None and isinstance(hf_quantizer, DiffusersQuantizer) and hf_quantizer.is_serializable
            if not quantization_serializable: raise ValueError(f'The model is quantized with {hf_quantizer.quantization_config.quant_method} and is not serializable - check out the warnings from the logger on the traceback to understand the reason why the quantized model is not serializable.')
        weights_name = SAFETENSORS_WEIGHTS_NAME if safe_serialization else WEIGHTS_NAME
        weights_name = _add_variant(weights_name, variant)
        weights_name_pattern = weights_name.replace('.bin', '{suffix}.bin').replace('.safetensors', '{suffix}.safetensors')
        os.makedirs(save_directory, exist_ok=True)
        if push_to_hub:
            commit_message = kwargs.pop('commit_message', None)
            private = kwargs.pop('private', None)
            create_pr = kwargs.pop('create_pr', False)
            token = kwargs.pop('token', None)
            repo_id = kwargs.pop('repo_id', save_directory.split(os.path.sep)[-1])
            repo_id = create_repo(repo_id, exist_ok=True, private=private, token=token).repo_id
        model_to_save = self
        if is_main_process: model_to_save.save_config(save_directory)
        state_dict = model_to_save.state_dict()
        state_dict_split = split_torch_state_dict_into_shards(state_dict, max_shard_size=max_shard_size, filename_pattern=weights_name_pattern)
        if is_main_process:
            for filename in os.listdir(save_directory):
                if filename in state_dict_split.filename_to_tensors.keys(): continue
                full_filename = os.path.join(save_directory, filename)
                if not os.path.isfile(full_filename): continue
                weights_without_ext = weights_name_pattern.replace('.bin', '').replace('.safetensors', '')
                weights_without_ext = weights_without_ext.replace('{suffix}', '')
                filename_without_ext = filename.replace('.bin', '').replace('.safetensors', '')
                if filename.startswith(weights_without_ext) and _REGEX_SHARD.fullmatch(filename_without_ext) is not None: os.remove(full_filename)
        for filename, tensors in state_dict_split.filename_to_tensors.items():
            shard = {tensor: state_dict[tensor] for tensor in tensors}
            filepath = os.path.join(save_directory, filename)
            if safe_serialization: safetensors.torch.save_file(shard, filepath, metadata={'format': 'pt'})
            else: torch.save(shard, filepath)
        if state_dict_split.is_sharded:
            index = {'metadata': state_dict_split.metadata, 'weight_map': state_dict_split.tensor_to_filename}
            save_index_file = SAFE_WEIGHTS_INDEX_NAME if safe_serialization else WEIGHTS_INDEX_NAME
            save_index_file = os.path.join(save_directory, _add_variant(save_index_file, variant))
            with open(save_index_file, 'w', encoding='utf-8') as f:
                content = json.dumps(index, indent=2, sort_keys=True) + '\n'
                f.write(content)
        else: path_to_weights = os.path.join(save_directory, weights_name)
        if push_to_hub:
            model_card = load_or_create_model_card(repo_id, token=token)
            model_card = populate_model_card(model_card)
            model_card.save(Path(save_directory, 'README.md').as_posix())
            self._upload_folder(save_directory, repo_id, token=token, commit_message=commit_message, create_pr=create_pr)
    def dequantize(self):
        hf_quantizer = getattr(self, 'hf_quantizer', None)
        if hf_quantizer is None: raise ValueError('You need to first quantize your model in order to dequantize it')
        return hf_quantizer.dequantize(self)
    @classmethod
    @validate_hf_hub_args
    def from_pretrained(cls, pretrained_model_name_or_path: Optional[Union[str, os.PathLike]], **kwargs):
        cache_dir = kwargs.pop('cache_dir', None)
        ignore_mismatched_sizes = kwargs.pop('ignore_mismatched_sizes', False)
        force_download = kwargs.pop('force_download', False)
        from_flax = kwargs.pop('from_flax', False)
        proxies = kwargs.pop('proxies', None)
        output_loading_info = kwargs.pop('output_loading_info', False)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        torch_dtype = kwargs.pop('torch_dtype', None)
        subfolder = kwargs.pop('subfolder', None)
        device_map = kwargs.pop('device_map', None)
        max_memory = kwargs.pop('max_memory', None)
        offload_folder = kwargs.pop('offload_folder', None)
        offload_state_dict = kwargs.pop('offload_state_dict', False)
        low_cpu_mem_usage = kwargs.pop('low_cpu_mem_usage', _LOW_CPU_MEM_USAGE_DEFAULT)
        variant = kwargs.pop('variant', None)
        use_safetensors = kwargs.pop('use_safetensors', None)
        quantization_config = kwargs.pop('quantization_config', None)
        allow_pickle = False
        if use_safetensors is None:
            use_safetensors = True
            allow_pickle = True
        if low_cpu_mem_usage and (not is_sapiens_accelerator_available()): low_cpu_mem_usage = False
        if device_map is not None and (not is_sapiens_accelerator_available()): raise NotImplementedError('Loading and dispatching requires `sapiens_accelerator`. Please make sure to install sapiens_accelerator or set `device_map=None`. You can install sapiens_accelerator with `pip install sapiens_accelerator`.')
        if device_map is not None and (not is_torch_version('>=', '1.9.0')): raise NotImplementedError('Loading and dispatching requires torch >= 1.9.0. Please either update your PyTorch version or set `device_map=None`.')
        if low_cpu_mem_usage is True and (not is_torch_version('>=', '1.9.0')): raise NotImplementedError('Low memory initialization requires torch >= 1.9.0. Please either update your PyTorch version or set `low_cpu_mem_usage=False`.')
        if low_cpu_mem_usage is False and device_map is not None: raise ValueError(f'You cannot set `low_cpu_mem_usage` to `False` while using device_map={device_map} for loading and dispatching. Please make sure to set `low_cpu_mem_usage=True`.')
        if isinstance(device_map, torch.device): device_map = {'': device_map}
        elif isinstance(device_map, str) and device_map not in ['auto', 'balanced', 'balanced_low_0', 'sequential']:
            try: device_map = {'': torch.device(device_map)}
            except RuntimeError: raise ValueError(f"When passing device_map as a string, the value needs to be a device name (e.g. cpu, cuda:0) or 'auto', 'balanced', 'balanced_low_0', 'sequential' but found {device_map}.")
        elif isinstance(device_map, int):
            if device_map < 0: raise ValueError("You can't pass device_map as a negative int. If you want to put the model on the cpu, pass device_map = 'cpu' ")
            else: device_map = {'': device_map}
        if device_map is not None:
            if low_cpu_mem_usage is None: low_cpu_mem_usage = True
            elif not low_cpu_mem_usage: raise ValueError('Passing along a `device_map` requires `low_cpu_mem_usage=True`')
        if low_cpu_mem_usage:
            if device_map is not None and (not is_torch_version('>=', '1.10')): raise ValueError('`low_cpu_mem_usage` and `device_map` require PyTorch >= 1.10.')
        config_path = pretrained_model_name_or_path
        user_agent = {'sapiens_transformers.diffusers': __version__, 'file_type': 'model', 'framework': 'pytorch'}
        config, unused_kwargs, commit_hash = cls.load_config(config_path, cache_dir=cache_dir, return_unused_kwargs=True, return_commit_hash=True, force_download=force_download, proxies=proxies,
        local_files_only=local_files_only, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent, **kwargs)
        config = copy.deepcopy(config)
        pre_quantized = 'quantization_config' in config and config['quantization_config'] is not None
        if pre_quantized or quantization_config is not None:
            if pre_quantized: config['quantization_config'] = DiffusersAutoQuantizer.merge_quantization_configs(config['quantization_config'], quantization_config)
            else: config['quantization_config'] = quantization_config
            hf_quantizer = DiffusersAutoQuantizer.from_config(config['quantization_config'], pre_quantized=pre_quantized)
        else: hf_quantizer = None
        if hf_quantizer is not None:
            if device_map is not None: raise NotImplementedError('Currently, providing `device_map` is not supported for quantized models. Providing `device_map` as an input will be added in the future.')
            hf_quantizer.validate_environment(torch_dtype=torch_dtype, from_flax=from_flax, device_map=device_map)
            torch_dtype = hf_quantizer.update_torch_dtype(torch_dtype)
            user_agent['quant'] = hf_quantizer.quantization_config.quant_method.value
            if low_cpu_mem_usage is None: low_cpu_mem_usage = True
            elif not low_cpu_mem_usage: raise ValueError('`low_cpu_mem_usage` cannot be False or None when using quantization.')
        use_keep_in_fp32_modules = cls._keep_in_fp32_modules is not None and (torch_dtype == torch.float16 or hasattr(hf_quantizer, 'use_keep_in_fp32_modules'))
        if use_keep_in_fp32_modules:
            keep_in_fp32_modules = cls._keep_in_fp32_modules
            if not isinstance(keep_in_fp32_modules, list): keep_in_fp32_modules = [keep_in_fp32_modules]
            if low_cpu_mem_usage is None: low_cpu_mem_usage = True
            elif not low_cpu_mem_usage: raise ValueError('`low_cpu_mem_usage` cannot be False when `keep_in_fp32_modules` is True.')
        else: keep_in_fp32_modules = []
        is_sharded = False
        index_file = None
        is_local = os.path.isdir(pretrained_model_name_or_path)
        index_file_kwargs = {'is_local': is_local, 'pretrained_model_name_or_path': pretrained_model_name_or_path, 'subfolder': subfolder or '', 'use_safetensors': use_safetensors, 'cache_dir': cache_dir, 'variant': variant, 'force_download': force_download, 'proxies': proxies, 'local_files_only': local_files_only, 'token': token, 'revision': revision, 'user_agent': user_agent, 'commit_hash': commit_hash}
        index_file = _fetch_index_file(**index_file_kwargs)
        if variant is not None and (index_file is None or not os.path.exists(index_file)): index_file = _fetch_index_file_legacy(**index_file_kwargs)
        if index_file is not None and index_file.is_file(): is_sharded = True
        if is_sharded and from_flax: raise ValueError('Loading of sharded checkpoints is not supported when `from_flax=True`.')
        model_file = None
        if from_flax:
            model_file = _get_model_file(pretrained_model_name_or_path, weights_name=FLAX_WEIGHTS_NAME, cache_dir=cache_dir, force_download=force_download, proxies=proxies, local_files_only=local_files_only,
            token=token, revision=revision, subfolder=subfolder, user_agent=user_agent, commit_hash=commit_hash)
            model = cls.from_config(config, **unused_kwargs)
            from .modeling_pytorch_flax_utils import load_flax_checkpoint_in_pytorch_model
            model = load_flax_checkpoint_in_pytorch_model(model, model_file)
        else:
            if is_sharded:
                sharded_ckpt_cached_folder, sharded_metadata = _get_checkpoint_shard_files(pretrained_model_name_or_path, index_file, cache_dir=cache_dir, proxies=proxies, local_files_only=local_files_only,
                token=token, user_agent=user_agent, revision=revision, subfolder=subfolder or '')
                def count_safetensors(dir_path: str) -> int:
                    try:
                        n_safetensors = 0
                        from os import path as _path
                        if not _path.isdir(dir_path): n_safetensors = 0
                        n_safetensors = sum(1 for file in os.listdir(dir_path) if file.endswith('.safetensors'))
                        return n_safetensors
                    except: return 0
                if hf_quantizer is not None or count_safetensors(pretrained_model_name_or_path) > 1:
                    model_file = _merge_sharded_checkpoints(sharded_ckpt_cached_folder, sharded_metadata)
                    is_sharded = False
            elif use_safetensors and (not is_sharded):
                try: model_file = _get_model_file(pretrained_model_name_or_path, weights_name=_add_variant(SAFETENSORS_WEIGHTS_NAME, variant), cache_dir=cache_dir, force_download=force_download, proxies=proxies,
                local_files_only=local_files_only, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent, commit_hash=commit_hash)
                except IOError as e:
                    if not allow_pickle: raise
            if model_file is None and (not is_sharded): model_file = _get_model_file(pretrained_model_name_or_path, weights_name=_add_variant(WEIGHTS_NAME, variant), cache_dir=cache_dir, force_download=force_download,
            proxies=proxies, local_files_only=local_files_only, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent, commit_hash=commit_hash)
            if low_cpu_mem_usage:
                with sapiens_accelerator.init_empty_weights(): model = cls.from_config(config, **unused_kwargs)
                if hf_quantizer is not None: hf_quantizer.preprocess_model(model=model, device_map=device_map, keep_in_fp32_modules=keep_in_fp32_modules)
                if device_map is None and (not is_sharded):
                    if hf_quantizer is None: param_device = 'cpu'
                    else: param_device = torch.device(torch.cuda.current_device())
                    state_dict = load_state_dict(model_file, variant=variant)
                    model._convert_deprecated_attention_blocks(state_dict)
                    missing_keys = set(model.state_dict().keys()) - set(state_dict.keys())
                    if hf_quantizer is not None: missing_keys = hf_quantizer.update_missing_keys(model, missing_keys, prefix='')
                    if len(missing_keys) > 0: raise ValueError(f"Cannot load {cls} from {pretrained_model_name_or_path} because the following keys are missing: \n {', '.join(missing_keys)}. \n Please make sure to pass `low_cpu_mem_usage=False` and `device_map=None` if you want to randomly initialize those weights or else make sure your checkpoint file is correct.")
                    unexpected_keys = load_model_dict_into_meta(model, state_dict, device=param_device, dtype=torch_dtype, model_name_or_path=pretrained_model_name_or_path, hf_quantizer=hf_quantizer, keep_in_fp32_modules=keep_in_fp32_modules)
                    if cls._keys_to_ignore_on_load_unexpected is not None:
                        for pat in cls._keys_to_ignore_on_load_unexpected: unexpected_keys = [k for k in unexpected_keys if re.search(pat, k) is None]
                else:
                    force_hook = True
                    device_map = _determine_device_map(model, device_map, max_memory, torch_dtype, keep_in_fp32_modules, hf_quantizer)
                    if device_map is None and is_sharded:
                        device_map = {'': 'cpu'}
                        force_hook = False
                    try: sapiens_accelerator.load_checkpoint_and_dispatch(model, model_file if not is_sharded else index_file, device_map, max_memory=max_memory, offload_folder=offload_folder, offload_state_dict=offload_state_dict,
                    dtype=torch_dtype, force_hooks=force_hook, strict=True)
                    except AttributeError as e:
                        if "'Attention' object has no attribute" in str(e):
                            model._temp_convert_self_to_deprecated_attention_blocks()
                            sapiens_accelerator.load_checkpoint_and_dispatch(model, model_file if not is_sharded else index_file, device_map, max_memory=max_memory, offload_folder=offload_folder,
                            offload_state_dict=offload_state_dict, dtype=torch_dtype, force_hooks=force_hook, strict=True)
                            model._undo_temp_convert_self_to_deprecated_attention_blocks()
                        else: raise e
                loading_info = {'missing_keys': [], 'unexpected_keys': [], 'mismatched_keys': [], 'error_msgs': []}
            else:
                model = cls.from_config(config, **unused_kwargs)
                try: state_dict = load_state_dict(model_file, variant=variant)
                except:
                    model_file = _merge_sharded_checkpoints(sharded_ckpt_cached_folder, sharded_metadata)
                    state_dict, is_sharded = load_state_dict(model_file, variant=variant), False
                model._convert_deprecated_attention_blocks(state_dict)
                model, missing_keys, unexpected_keys, mismatched_keys, error_msgs = cls._load_pretrained_model(model, state_dict, model_file, pretrained_model_name_or_path, ignore_mismatched_sizes=ignore_mismatched_sizes)
                loading_info = {'missing_keys': missing_keys, 'unexpected_keys': unexpected_keys, 'mismatched_keys': mismatched_keys, 'error_msgs': error_msgs}
        if hf_quantizer is not None:
            hf_quantizer.postprocess_model(model)
            model.hf_quantizer = hf_quantizer
        if torch_dtype is not None and (not isinstance(torch_dtype, torch.dtype)): raise ValueError(f'{torch_dtype} needs to be of type `torch.dtype`, e.g. `torch.float16`, but is {type(torch_dtype)}.')
        elif torch_dtype is not None and hf_quantizer is None and (not use_keep_in_fp32_modules): model = model.to(torch_dtype)
        if hf_quantizer is not None: model.register_to_config(_name_or_path=pretrained_model_name_or_path, _pre_quantization_dtype=torch_dtype)
        else: model.register_to_config(_name_or_path=pretrained_model_name_or_path)
        model.eval()
        if output_loading_info: return (model, loading_info)
        return model
    @wraps(torch.nn.Module.cuda)
    def cuda(self, *args, **kwargs):
        if getattr(self, 'quantization_method', None) == QuantizationMethod.SAPIENS_MACHINE:
            if getattr(self, 'is_loaded_in_8bit', False): raise ValueError('Calling `cuda()` is not supported for `8-bit` quantized models.  Please use the model as it is, since the model has already been set to the correct devices.')
            elif is_sapiens_machine_version('<', '0.43.2'): raise ValueError(f'Calling `cuda()` is not supported for `4-bit` quantized models with the installed version of sapiens_machine. The current device is `{self.device}`. If you intended to move the model, please install sapiens_machine >= 0.43.2.')
        return super().cuda(*args, **kwargs)
    @wraps(torch.nn.Module.to)
    def to(self, *args, **kwargs):
        dtype_present_in_args = 'dtype' in kwargs
        if not dtype_present_in_args:
            for arg in args:
                if isinstance(arg, torch.dtype):
                    dtype_present_in_args = True
                    break
        if getattr(self, 'is_quantized', False):
            if dtype_present_in_args: raise ValueError('Casting a quantized model to a new `dtype` is unsupported. To set the dtype of unquantized layers, please use the `torch_dtype` argument when loading the model using `from_pretrained` or `from_single_file`')
        if getattr(self, 'quantization_method', None) == QuantizationMethod.SAPIENS_MACHINE:
            if getattr(self, 'is_loaded_in_8bit', False): raise ValueError('`.to` is not supported for `8-bit` sapiens_machine models. Please use the model as it is, since the model has already been set to the correct devices and casted to the correct `dtype`.')
            elif is_sapiens_machine_version('<', '0.43.2'): raise ValueError(f'Calling `to()` is not supported for `4-bit` quantized models with the installed version of sapiens_machine. The current device is `{self.device}`. If you intended to move the model, please install sapiens_machine >= 0.43.2.')
        return super().to(*args, **kwargs)
    def half(self, *args):
        if getattr(self, 'is_quantized', False): raise ValueError('`.half()` is not supported for quantized model. Please use the model as it is, since the model has already been cast to the correct `dtype`.')
        else: return super().half(*args)
    def float(self, *args):
        if getattr(self, 'is_quantized', False): raise ValueError('`.float()` is not supported for quantized model. Please use the model as it is, since the model has already been cast to the correct `dtype`.')
        else: return super().float(*args)
    @classmethod
    def _load_pretrained_model(cls, model, state_dict: OrderedDict, resolved_archive_file, pretrained_model_name_or_path: Union[str, os.PathLike], ignore_mismatched_sizes: bool=False):
        model_state_dict = model.state_dict()
        loaded_keys = list(state_dict.keys())
        expected_keys = list(model_state_dict.keys())
        original_loaded_keys = loaded_keys
        missing_keys = list(set(expected_keys) - set(loaded_keys))
        unexpected_keys = list(set(loaded_keys) - set(expected_keys))
        model_to_load = model
        def _find_mismatched_keys(state_dict, model_state_dict, loaded_keys, ignore_mismatched_sizes):
            mismatched_keys = []
            if ignore_mismatched_sizes:
                for checkpoint_key in loaded_keys:
                    model_key = checkpoint_key
                    if model_key in model_state_dict and state_dict[checkpoint_key].shape != model_state_dict[model_key].shape:
                        mismatched_keys.append((checkpoint_key, state_dict[checkpoint_key].shape, model_state_dict[model_key].shape))
                        del state_dict[checkpoint_key]
            return mismatched_keys
        if state_dict is not None:
            mismatched_keys = _find_mismatched_keys(state_dict, model_state_dict, original_loaded_keys, ignore_mismatched_sizes)
            error_msgs = _load_state_dict_into_model(model_to_load, state_dict)
        if len(error_msgs) > 0:
            error_msg = '\n\t'.join(error_msgs)
            if 'size mismatch' in error_msg: error_msg += '\n\tYou may consider adding `ignore_mismatched_sizes=True` in the model `from_pretrained` method.'
            raise RuntimeError(f'Error(s) in loading state_dict for {model.__class__.__name__}:\n\t{error_msg}')
        if len(mismatched_keys) > 0: mismatched_warning = '\n'.join([f'- {key}: found shape {shape1} in the checkpoint and {shape2} in the model instantiated' for key, shape1, shape2 in mismatched_keys])
        return (model, missing_keys, unexpected_keys, mismatched_keys, error_msgs)
    @classmethod
    def _get_signature_keys(cls, obj):
        parameters = inspect.signature(obj.__init__).parameters
        required_parameters = {k: v for k, v in parameters.items() if v.default == inspect._empty}
        optional_parameters = set({k for k, v in parameters.items() if v.default != inspect._empty})
        expected_modules = set(required_parameters.keys()) - {'self'}
        return (expected_modules, optional_parameters)
    def _get_no_split_modules(self, device_map: str):
        """Returns:"""
        _no_split_modules = set()
        modules_to_check = [self]
        while len(modules_to_check) > 0:
            module = modules_to_check.pop(-1)
            if module.__class__.__name__ not in _no_split_modules:
                if isinstance(module, ModelMixin):
                    if module._no_split_modules is None: raise ValueError(f"{module.__class__.__name__} does not support `device_map='{device_map}'`. To implement support, the model class needs to implement the `_no_split_modules` attribute.")
                    else: _no_split_modules = _no_split_modules | set(module._no_split_modules)
                modules_to_check += list(module.children())
        return list(_no_split_modules)
    @property
    def device(self) -> torch.device: return get_parameter_device(self)
    @property
    def dtype(self) -> torch.dtype: return get_parameter_dtype(self)
    def num_parameters(self, only_trainable: bool=False, exclude_embeddings: bool=False) -> int:
        """Returns:"""
        is_loaded_in_4bit = getattr(self, 'is_loaded_in_4bit', False)
        if is_loaded_in_4bit:
            if is_sapiens_machine_available(): import sapiens_machine as sapiens
            else: raise ValueError('sapiens_machine is not installed but it seems that the model has been loaded in 4bit precision, something went wrong make sure to install sapiens_machine with `pip install sapiens_machine`. You also need a GPU. ')
        if exclude_embeddings:
            embedding_param_names = [f'{name}.weight' for name, module_type in self.named_modules() if isinstance(module_type, nn.Embedding)]
            total_parameters = [parameter for name, parameter in self.named_parameters() if name not in embedding_param_names]
        else: total_parameters = list(self.parameters())
        total_numel = []
        for param in total_parameters:
            if param.requires_grad or not only_trainable:
                if is_loaded_in_4bit and isinstance(param, sapiens.nn.Params4bit):
                    if hasattr(param, 'element_size'): num_bytes = param.element_size()
                    elif hasattr(param, 'quant_storage'): num_bytes = param.quant_storage.itemsize
                    else: num_bytes = 1
                    total_numel.append(param.numel() * 2 * num_bytes)
                else: total_numel.append(param.numel())
        return sum(total_numel)
    def get_memory_footprint(self, return_buffers=True):
        mem = sum([param.nelement() * param.element_size() for param in self.parameters()])
        if return_buffers:
            mem_bufs = sum([buf.nelement() * buf.element_size() for buf in self.buffers()])
            mem = mem + mem_bufs
        return mem
    def _convert_deprecated_attention_blocks(self, state_dict: OrderedDict) -> None:
        deprecated_attention_block_paths = []
        def recursive_find_attn_block(name, module):
            if hasattr(module, '_from_deprecated_attn_block') and module._from_deprecated_attn_block: deprecated_attention_block_paths.append(name)
            for sub_name, sub_module in module.named_children():
                sub_name = sub_name if name == '' else f'{name}.{sub_name}'
                recursive_find_attn_block(sub_name, sub_module)
        recursive_find_attn_block('', self)
        for path in deprecated_attention_block_paths:
            if f'{path}.query.weight' in state_dict: state_dict[f'{path}.to_q.weight'] = state_dict.pop(f'{path}.query.weight')
            if f'{path}.query.bias' in state_dict: state_dict[f'{path}.to_q.bias'] = state_dict.pop(f'{path}.query.bias')
            if f'{path}.key.weight' in state_dict: state_dict[f'{path}.to_k.weight'] = state_dict.pop(f'{path}.key.weight')
            if f'{path}.key.bias' in state_dict: state_dict[f'{path}.to_k.bias'] = state_dict.pop(f'{path}.key.bias')
            if f'{path}.value.weight' in state_dict: state_dict[f'{path}.to_v.weight'] = state_dict.pop(f'{path}.value.weight')
            if f'{path}.value.bias' in state_dict: state_dict[f'{path}.to_v.bias'] = state_dict.pop(f'{path}.value.bias')
            if f'{path}.proj_attn.weight' in state_dict: state_dict[f'{path}.to_out.0.weight'] = state_dict.pop(f'{path}.proj_attn.weight')
            if f'{path}.proj_attn.bias' in state_dict: state_dict[f'{path}.to_out.0.bias'] = state_dict.pop(f'{path}.proj_attn.bias')
    def _temp_convert_self_to_deprecated_attention_blocks(self) -> None:
        deprecated_attention_block_modules = []
        def recursive_find_attn_block(module):
            if hasattr(module, '_from_deprecated_attn_block') and module._from_deprecated_attn_block: deprecated_attention_block_modules.append(module)
            for sub_module in module.children(): recursive_find_attn_block(sub_module)
        recursive_find_attn_block(self)
        for module in deprecated_attention_block_modules:
            module.query = module.to_q
            module.key = module.to_k
            module.value = module.to_v
            module.proj_attn = module.to_out[0]
            del module.to_q
            del module.to_k
            del module.to_v
            del module.to_out
    def _undo_temp_convert_self_to_deprecated_attention_blocks(self) -> None:
        deprecated_attention_block_modules = []
        def recursive_find_attn_block(module) -> None:
            if hasattr(module, '_from_deprecated_attn_block') and module._from_deprecated_attn_block: deprecated_attention_block_modules.append(module)
            for sub_module in module.children(): recursive_find_attn_block(sub_module)
        recursive_find_attn_block(self)
        for module in deprecated_attention_block_modules:
            module.to_q = module.query
            module.to_k = module.key
            module.to_v = module.value
            module.to_out = nn.ModuleList([module.proj_attn, nn.Dropout(module.dropout)])
            del module.query
            del module.key
            del module.value
            del module.proj_attn
class LegacyModelMixin(ModelMixin):
    @classmethod
    @validate_hf_hub_args
    def from_pretrained(cls, pretrained_model_name_or_path: Optional[Union[str, os.PathLike]], **kwargs):
        from .model_loading_utils import _fetch_remapped_cls_from_config
        kwargs_copy = kwargs.copy()
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        subfolder = kwargs.pop('subfolder', None)
        config_path = pretrained_model_name_or_path
        user_agent = {'sapiens_transformers.diffusers': __version__, 'file_type': 'model', 'framework': 'pytorch'}
        config, _, _ = cls.load_config(config_path, cache_dir=cache_dir, return_unused_kwargs=True, return_commit_hash=True, force_download=force_download, proxies=proxies,
        local_files_only=local_files_only, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent, **kwargs)
        remapped_class = _fetch_remapped_cls_from_config(config, cls)
        return remapped_class.from_pretrained(pretrained_model_name_or_path, **kwargs_copy)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
