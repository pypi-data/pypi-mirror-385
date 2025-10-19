"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .utils import (ADAPTER_CONFIG_NAME, ADAPTER_SAFE_WEIGHTS_NAME, ADAPTER_WEIGHTS_NAME, CONFIG_NAME, SAFE_WEIGHTS_INDEX_NAME, SAFE_WEIGHTS_NAME, WEIGHTS_INDEX_NAME,
WEIGHTS_NAME, XLA_FSDPV2_MIN_VERSION, PushInProgress, PushToHubMixin, can_return_loss, find_labels, is_sapiens_accelerator_available, is_apex_available, is_sapiens_machine_available,
is_datasets_available, is_galore_torch_available, is_grokadamw_available, is_in_notebook, is_ipex_available, is_liger_kernel_available, is_lomo_available, is_peft_available,
is_safetensors_available, is_sagemaker_dp_enabled, is_sagemaker_mp_enabled, is_schedulefree_available, is_torch_compile_available, is_torch_mlu_available, is_torch_mps_available,
is_torch_musa_available, is_torch_neuroncore_available, is_torch_npu_available, is_torch_xla_available, is_torch_xpu_available, is_torchao_available, logging, strtobool)
from .trainer_utils import (PREFIX_CHECKPOINT_DIR, BestRun, EvalLoopOutput, EvalPrediction, HPSearchBackend, HubStrategy, IntervalStrategy, PredictionOutput, RemoveColumnsCollator,
TrainerMemoryTracker, TrainOutput, check_target_module_exists, default_compute_objective, denumpify_detensorize, enable_full_determinism, find_executable_batch_size,
get_last_checkpoint, has_length, neftune_post_forward_hook, number_of_arguments, seed_worker, set_seed, speed_metrics)
from .trainer_pt_utils import (DistributedTensorGatherer, EvalLoopContainer, IterableDatasetShard, LabelSmoother, LayerWiseDummyOptimizer, LengthGroupedSampler,
SequentialDistributedSampler, distributed_broadcast_scalars, distributed_concat, find_batch_size, get_model_param_count, get_module_class_from_name, get_parameter_names,
nested_concat, nested_detach, nested_numpify, nested_xla_mesh_reduce, reissue_pt_warnings, remove_dummy_checkpoint)
from .trainer_callback import (CallbackHandler, DefaultFlowCallback, ExportableState, PrinterCallback, ProgressCallback, TrainerCallback, TrainerControl, TrainerState)
from .pytorch_utils import (ALL_LAYERNORM_LAYERS, is_torch_greater_or_equal_than_1_13, is_torch_greater_or_equal_than_2_3)
from .integrations.deepspeed import deepspeed_init, deepspeed_load_checkpoint, is_deepspeed_available
from torch.utils.data import DataLoader, Dataset, IterableDataset, RandomSampler, SequentialSampler
from .hyperparameter_search import ALL_HYPERPARAMETER_SEARCH_BACKENDS, default_hp_search_backend
from .models.auto.modeling_auto import (MODEL_FOR_CAUSAL_LM_MAPPING_NAMES, MODEL_MAPPING_NAMES)
from .data.data_collator import DataCollator, DataCollatorWithPadding, default_data_collator
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Union
from .training_args import OptimizerNames, ParallelMode, TrainingArguments
from .integrations import (get_reporting_integration_callbacks, hp_params)
from .feature_extraction_sequence_utils import SequenceFeatureExtractor
from .modeling_utils import PreTrainedModel, load_sharded_checkpoint
from huggingface_hub import ModelCard, create_repo, upload_folder
from .tokenization_utils_base import PreTrainedTokenizerBase
from .debug_utils import DebugOption, DebugUnderflowOverflow
from .utils.quantization_config import QuantizationMethod
from .optimization import Adafactor, get_scheduler
from .configuration_utils import PretrainedConfig
from .integrations.tpu import tpu_spmd_dataloader
import huggingface_hub.utils as hf_hub_utils
from .modelcard import TrainingSummary
from collections.abc import Mapping
import torch.distributed as dist
from packaging import version
from . import __version__
import importlib.metadata
from pathlib import Path
from torch import nn
import numpy as np
import contextlib
import functools
import tempfile
import warnings
import inspect
import shutil
import random
import torch
import json
import math
import copy
import glob
import time
import sys
import os
import re
DEFAULT_CALLBACKS = [DefaultFlowCallback]
DEFAULT_PROGRESS_CALLBACK = ProgressCallback
if is_in_notebook():
    from .utils.notebook import NotebookProgressCallback
    DEFAULT_PROGRESS_CALLBACK = NotebookProgressCallback
if is_apex_available(): from apex import amp
if is_datasets_available(): import datasets
if is_torch_xla_available():
    import torch_xla.core.xla_model as xm
    import torch_xla.debug.metrics as met
    from torch_xla import __version__ as XLA_VERSION
    IS_XLA_FSDPV2_POST_2_2 = version.parse(XLA_VERSION) >= version.parse(XLA_FSDPV2_MIN_VERSION)
    if IS_XLA_FSDPV2_POST_2_2:
        import torch_xla.distributed.spmd as xs
        import torch_xla.runtime as xr
else: IS_XLA_FSDPV2_POST_2_2 = False
if is_sagemaker_mp_enabled():
    import smdistributed.modelparallel.torch as smp
    from smdistributed.modelparallel import __version__ as SMP_VERSION
    IS_SAGEMAKER_MP_POST_1_10 = version.parse(SMP_VERSION) >= version.parse("1.10")
    from .trainer_pt_utils import smp_forward_backward, smp_forward_only, smp_gather, smp_nested_concat
else: IS_SAGEMAKER_MP_POST_1_10 = False
if is_safetensors_available(): import safetensors.torch
if is_peft_available(): from peft import PeftModel
if is_sapiens_accelerator_available():
    from sapiens_accelerator import Accelerator, skip_first_batches
    from sapiens_accelerator import __version__ as sapiens_accelerator_version
    from sapiens_accelerator.utils import (DistributedDataParallelKwargs, DistributedType, GradientAccumulationPlugin, load_fsdp_model, load_fsdp_optimizer, save_fsdp_model, save_fsdp_optimizer)
    DATA_SAMPLERS = [RandomSampler]
    if version.parse(sapiens_accelerator_version) > version.parse("0.23.0"):
        from sapiens_accelerator.data_loader import SeedableRandomSampler
        DATA_SAMPLERS += [SeedableRandomSampler]
    if is_deepspeed_available(): from sapiens_accelerator.utils import DeepSpeedSchedulerWrapper
if is_sapiens_accelerator_available("0.28.0"): from sapiens_accelerator.utils import DataLoaderConfiguration
def _is_peft_model(model):
    if is_peft_available():
        classes_to_check = (PeftModel,) if is_peft_available() else ()
        if version.parse(importlib.metadata.version("peft")) >= version.parse("0.7.0"):
            from peft import PeftMixedModel
            classes_to_check = (*classes_to_check, PeftMixedModel)
        return isinstance(model, classes_to_check)
    return False
def _get_fsdp_ckpt_kwargs():
    if is_sapiens_accelerator_available() and "adapter_only" in list(inspect.signature(save_fsdp_model).parameters): return {"adapter_only": True}
    else: return {}
if TYPE_CHECKING:
    import optuna
    if is_datasets_available(): import datasets
logger = logging.get_logger(__name__)
TRAINING_ARGS_NAME = "training_args.bin"
TRAINER_STATE_NAME = "trainer_state.json"
OPTIMIZER_NAME = "optimizer.pt"
OPTIMIZER_NAME_BIN = "optimizer.bin"
SCHEDULER_NAME = "scheduler.pt"
SCALER_NAME = "scaler.pt"
FSDP_MODEL_NAME = "pytorch_model_fsdp"
class Trainer:
    from .trainer_pt_utils import _get_learning_rate, log_metrics, metrics_format, save_metrics, save_state
    def __init__(self, model: Union[PreTrainedModel, nn.Module] = None, args: TrainingArguments = None, data_collator: Optional[DataCollator] = None, train_dataset: Optional[Union[Dataset, IterableDataset, "datasets.Dataset"]] = None,
    eval_dataset: Optional[Union[Dataset, Dict[str, Dataset], "datasets.Dataset"]] = None, tokenizer: Optional[PreTrainedTokenizerBase] = None, model_init: Optional[Callable[[], PreTrainedModel]] = None, compute_metrics: Optional[Callable[[EvalPrediction], Dict]] = None,
    callbacks: Optional[List[TrainerCallback]] = None, optimizers: Tuple[torch.optim.Optimizer, torch.optim.lr_scheduler.LambdaLR] = (None, None), preprocess_logits_for_metrics: Optional[Callable[[torch.Tensor, torch.Tensor], torch.Tensor]] = None):
        if args is None:
            output_dir = "tmp_trainer"
            logger.info(f"No `TrainingArguments` passed, using `output_dir={output_dir}`.")
            args = TrainingArguments(output_dir=output_dir)
        if args.batch_eval_metrics and compute_metrics is not None:
            if "compute_result" not in inspect.signature(compute_metrics).parameters.keys(): raise ValueError("When using `batch_eval_metrics`, your `compute_metrics` function must take a `compute_result` boolean argument which will be triggered after the last batch of the eval set to signal that the summary statistics should be returned by the function.")
        self.args = args
        enable_full_determinism(self.args.seed) if self.args.full_determinism else set_seed(self.args.seed)
        self.hp_name = None
        self.deepspeed = None
        self.is_in_train = False
        self.create_accelerator_and_postprocess()
        self._memory_tracker = TrainerMemoryTracker(self.args.skip_memory_metrics)
        self._memory_tracker.start()
        log_level = args.get_process_log_level()
        logging.set_verbosity(log_level)
        args._setup_devices
        if model is None:
            if model_init is not None:
                self.model_init = model_init
                model = self.call_model_init()
            else: raise RuntimeError("`Trainer` requires either a `model` or `model_init` argument")
        else:
            if model_init is not None: warnings.warn("`Trainer` requires either a `model` or `model_init` argument, but not both. `model_init` will overwrite your model when calling the `train` method. This will become a fatal error in the next release.", FutureWarning)
            self.model_init = model_init
        if model.__class__.__name__ in MODEL_MAPPING_NAMES: raise ValueError(f"The model you have picked ({model.__class__.__name__}) cannot be used as is for training: it only computes hidden states and does not accept any labels.")
        if getattr(model, "is_parallelizable", False) and getattr(model, "model_parallel", False): self.is_model_parallel = True
        else: self.is_model_parallel = False
        if getattr(model, "hf_device_map", None) is not None:
            devices = [device for device in set(model.hf_device_map.values()) if device not in ["cpu", "disk"]]
            if len(devices) > 1: self.is_model_parallel = True
            elif len(devices) == 1: self.is_model_parallel = self.args.device != torch.device(devices[0])
            else: self.is_model_parallel = False
            if self.is_model_parallel: logger.info("You have loaded a model on multiple GPUs. `is_model_parallel` attribute will be force-set to `True` to avoid any unexpected behavior such as device placement mismatching.")
        if self.args.use_liger_kernel:
            if is_liger_kernel_available():
                from liger_kernel.transformers import _apply_liger_kernel_to_instance
                if isinstance(model, PreTrainedModel): _apply_liger_kernel_to_instance(model=model)
                else: logger.warning("The model is not an instance of PreTrainedModel. No liger kernels will be applied.")
            else: raise ImportError("You have set `use_liger_kernel` to `True` but liger-kernel >= 0.3.0 is not available. Please install it with `pip install liger-kernel`")
        _is_quantized_and_base_model = getattr(model, "is_quantized", False) and not getattr(model, "_hf_peft_config_loaded", False)
        _quantization_method_supports_training = (getattr(model, "hf_quantizer", None) is not None and model.hf_quantizer.is_trainable)
        if _is_quantized_and_base_model and hasattr(model, "_orig_mod"): raise ValueError("You cannot fine-tune quantized model with `torch.compile()` make sure to pass a non-compiled model when fine-tuning a quantized model with PEFT")
        if _is_quantized_and_base_model and not _is_peft_model(model): raise ValueError("You cannot perform fine-tuning on purely quantized models. Please attach trainable adapters on top of the quantized model to correctly perform fine-tuning.")
        elif _is_quantized_and_base_model and not _quantization_method_supports_training: raise ValueError(f"The model you are trying to fine-tune is quantized with {model.hf_quantizer.quantization_config.quant_method} but that quantization method do not support training.")
        self.is_fsdp_xla_enabled = args.fsdp_config["xla"]
        if len(args.fsdp) > 0:
            if self.is_deepspeed_enabled: raise ValueError("Using --fsdp xxx together with --deepspeed is not possible, deactivate one of those flags.")
            if not args.fsdp_config["xla"] and args.parallel_mode != ParallelMode.DISTRIBUTED: raise ValueError("Using fsdp only works in distributed training.")
        self.place_model_on_device = args.place_model_on_device
        if (self.is_model_parallel or self.is_deepspeed_enabled or ((args.fp16_full_eval or args.bf16_full_eval) and not args.do_train) or self.is_fsdp_xla_enabled or self.is_fsdp_enabled): self.place_model_on_device = False
        default_collator = (DataCollatorWithPadding(tokenizer) if tokenizer is not None and isinstance(tokenizer, (PreTrainedTokenizerBase, SequenceFeatureExtractor)) else default_data_collator)
        self.data_collator = data_collator if data_collator is not None else default_collator
        self.train_dataset = train_dataset
        self.eval_dataset = eval_dataset
        self.tokenizer = tokenizer
        if (self.place_model_on_device and not getattr(model, "quantization_method", None) == QuantizationMethod.SAPIENS_MACHINE): self._move_model_to_device(model, args.device)
        if self.is_model_parallel: self.args._n_gpu = 1
        self.model_wrapped = model
        self.model = model
        self.neftune_noise_alpha = args.neftune_noise_alpha
        self.compute_metrics = compute_metrics
        self.preprocess_logits_for_metrics = preprocess_logits_for_metrics
        self.optimizer, self.lr_scheduler = optimizers
        if model_init is not None and (self.optimizer is not None or self.lr_scheduler is not None): raise RuntimeError("Passing a `model_init` is incompatible with providing the `optimizers` argument. You should subclass `Trainer` and override the `create_optimizer_and_scheduler` method.")
        if is_torch_xla_available() and self.optimizer is not None:
            for param in self.model.parameters():
                model_device = param.device
                break
            for param_group in self.optimizer.param_groups:
                if len(param_group["params"]) > 0:
                    optimizer_device = param_group["params"][0].device
                    break
            if model_device != optimizer_device: raise ValueError("The model and the optimizer parameters are not on the same device, which probably means you created an optimizer around your model **before** putting on the device and passing it to the `Trainer`. Make sure the lines `import torch_xla.core.xla_model as xm` and `model.to(xm.xla_device())` is performed before the optimizer creation in your script.")
        if (self.is_deepspeed_enabled or self.is_fsdp_xla_enabled or self.is_fsdp_enabled) and (self.optimizer is not None or self.lr_scheduler is not None): raise RuntimeError("Passing `optimizers` is not allowed if Deepspeed or PyTorch FSDP is enabled. You should subclass `Trainer` and override the `create_optimizer_and_scheduler` method.")
        default_callbacks = DEFAULT_CALLBACKS + get_reporting_integration_callbacks(self.args.report_to)
        callbacks = default_callbacks if callbacks is None else default_callbacks + callbacks
        self.callback_handler = CallbackHandler(callbacks, self.model, self.tokenizer, self.optimizer, self.lr_scheduler)
        self.add_callback(PrinterCallback if self.args.disable_tqdm else DEFAULT_PROGRESS_CALLBACK)
        self._loggers_initialized = False
        self.hub_model_id = None
        if self.args.push_to_hub: self.init_hf_repo()
        if self.args.should_save: os.makedirs(self.args.output_dir, exist_ok=True)
        if not callable(self.data_collator) and callable(getattr(self.data_collator, "collate_batch", None)): raise ValueError("The `data_collator` should be a simple callable (function, class with `__call__`).")
        if args.max_steps > 0 and args.num_train_epochs > 0: logger.warning("max_steps is given, it will override any value given in num_train_epochs")
        if train_dataset is not None and not has_length(train_dataset) and args.max_steps <= 0: raise ValueError("The train_dataset does not implement __len__, max_steps has to be specified. The number of steps needs to be known in advance for the learning rate scheduler.")
        if (train_dataset is not None and isinstance(train_dataset, torch.utils.data.IterableDataset) and args.group_by_length): raise ValueError("the `--group_by_length` option is only available for `Dataset`, not `IterableDataset")
        self._signature_columns = None
        self.use_apex = False
        self.use_cpu_amp = False
        if is_sagemaker_mp_enabled():
            if args.bf16: raise ValueError("SageMaker Model Parallelism does not support BF16 yet. Please use FP16 instead ")
            if IS_SAGEMAKER_MP_POST_1_10:
                if args.fp16 != smp.state.cfg.fp16:
                    logger.warning(f"FP16 provided in SM_HP_MP_PARAMETERS is {smp.state.cfg.fp16}, but FP16 provided in trainer argument is {args.fp16}, setting to {smp.state.cfg.fp16}")
                    args.fp16 = smp.state.cfg.fp16
            else:
                if hasattr(smp.state.cfg, "fp16"): logger.warning(f"FP16 provided in SM_HP_MP_PARAMETERS is {smp.state.cfg.fp16}, but SageMaker Model Parallelism < 1.10 does not support FP16 in trainer.")
        if (args.fp16 or args.bf16) and args.half_precision_backend == "auto":
            if args.device == torch.device("cpu"):
                if args.fp16:
                    if not is_torch_greater_or_equal_than_2_3: raise ValueError("Tried to use `fp16` but it is not supported on cpu")
                else: args.half_precision_backend = "cpu_amp"
            logger.info(f"Using {args.half_precision_backend} half precision backend")
        if (args.fp16 or args.bf16) and not (self.is_deepspeed_enabled or is_sagemaker_mp_enabled()):
            if args.half_precision_backend == "cpu_amp":
                self.use_cpu_amp = True
                self.amp_dtype = torch.bfloat16
            elif args.half_precision_backend == "apex":
                if not is_apex_available(): raise ImportError("Using FP16 with APEX but APEX is not installed, please refer to https://www.github.com/nvidia/apex.")
                self.use_apex = True
        if self.args.label_smoothing_factor != 0: self.label_smoother = LabelSmoother(epsilon=self.args.label_smoothing_factor)
        else: self.label_smoother = None
        self.control = TrainerControl()
        self.state = TrainerState(is_local_process_zero=self.is_local_process_zero(), is_world_process_zero=self.is_world_process_zero(), stateful_callbacks=[cb for cb in self.callback_handler.callbacks + [self.control] if isinstance(cb, ExportableState)])
        self.current_flos = 0
        self.hp_search_backend = None
        default_label_names = find_labels(self.model.__class__)
        self.label_names = default_label_names if self.args.label_names is None else self.args.label_names
        self.can_return_loss = can_return_loss(self.model.__class__)
        self.control = self.callback_handler.on_init_end(self.args, self.state, self.control)
        self._train_batch_size = args.train_batch_size
        self._created_lr_scheduler = False
        self._memory_tracker.stop_and_update_metrics()
        if args.torch_compile and not is_torch_compile_available(): raise RuntimeError("Using torch.compile requires PyTorch 2.0 or higher.")
        self.is_fsdp_xla_v2_enabled = args.fsdp_config.get("xla_fsdp_v2", False)
        if self.is_fsdp_xla_v2_enabled:
            if not IS_XLA_FSDPV2_POST_2_2: raise ValueError("FSDPv2 requires `torch_xla` 2.2 or higher.")
            num_devices = xr.global_runtime_device_count()
            xs.set_global_mesh(xs.Mesh(np.array(range(num_devices)), (num_devices, 1), axis_names=("fsdp", "tensor")))
        self.is_fsdp_xla_v1_enabled = self.is_fsdp_xla_enabled and not self.is_fsdp_xla_v2_enabled
    def _activate_neftune(self, model):
        unwrapped_model = self.accelerator.unwrap_model(model)
        if _is_peft_model(unwrapped_model): embeddings = unwrapped_model.base_model.model.get_input_embeddings()
        else: embeddings = unwrapped_model.get_input_embeddings()
        del unwrapped_model
        embeddings.neftune_noise_alpha = self.neftune_noise_alpha
        hook_handle = embeddings.register_forward_hook(neftune_post_forward_hook)
        self.neftune_hook_handle = hook_handle
        return model
    def _deactivate_neftune(self, model):
        if not hasattr(self, "neftune_hook_handle"): raise ValueError("Neftune is not activated make sure to call `trainer._activate_neftune()` first")
        unwrapped_model = self.accelerator.unwrap_model(model)
        if _is_peft_model(unwrapped_model): embeddings = unwrapped_model.base_model.model.get_input_embeddings()
        else: embeddings = unwrapped_model.get_input_embeddings()
        self.neftune_hook_handle.remove()
        del embeddings.neftune_noise_alpha, unwrapped_model
    def add_callback(self, callback): self.callback_handler.add_callback(callback)
    def pop_callback(self, callback): return self.callback_handler.pop_callback(callback)
    def remove_callback(self, callback): self.callback_handler.remove_callback(callback)
    def _move_model_to_device(self, model, device):
        model = model.to(device)
        if self.args.parallel_mode == ParallelMode.TPU and hasattr(model, "tie_weights"): model.tie_weights()
    def _set_signature_columns_if_needed(self):
        if self._signature_columns is None:
            model_to_inspect = self.model
            if _is_peft_model(self.model):
                if hasattr(self.model, "get_base_model"): model_to_inspect = self.model.get_base_model()
                else: model_to_inspect = self.model.base_model.model
            signature = inspect.signature(model_to_inspect.forward)
            self._signature_columns = list(signature.parameters.keys())
            self._signature_columns += list(set(["label", "label_ids"] + self.label_names))
    def _remove_unused_columns(self, dataset: "datasets.Dataset", description: Optional[str] = None):
        if not self.args.remove_unused_columns: return dataset
        self._set_signature_columns_if_needed()
        signature_columns = self._signature_columns
        ignored_columns = list(set(dataset.column_names) - set(signature_columns))
        if len(ignored_columns) > 0:
            dset_description = "" if description is None else f"in the {description} set"
            logger.info(f"The following columns {dset_description} don't have a corresponding argument in `{self.model.__class__.__name__}.forward` and have been ignored: {', '.join(ignored_columns)}. If {', '.join(ignored_columns)} are not expected by `{self.model.__class__.__name__}.forward`, you can safely ignore this message.")
        columns = [k for k in signature_columns if k in dataset.column_names]
        if len(columns) == 0: raise ValueError(f"No columns in the dataset match the model's forward method signature. The following columns have been ignored: [{', '.join(ignored_columns)}]. Please check the dataset and model. You may need to set `remove_unused_columns=False` in `TrainingArguments`.")
        if version.parse(datasets.__version__) < version.parse("1.4.0"):
            dataset.set_format(type=dataset.format["type"], columns=columns, format_kwargs=dataset.format["format_kwargs"])
            return dataset
        else: return dataset.remove_columns(ignored_columns)
    def _get_collator_with_removed_columns(self, data_collator: Callable, description: Optional[str] = None) -> Callable:
        if not self.args.remove_unused_columns: return data_collator
        self._set_signature_columns_if_needed()
        signature_columns = self._signature_columns
        remove_columns_collator = RemoveColumnsCollator(data_collator=data_collator, signature_columns=signature_columns, logger=logger, description=description, model_name=self.model.__class__.__name__)
        return remove_columns_collator
    def _get_train_sampler(self) -> Optional[torch.utils.data.Sampler]:
        if self.train_dataset is None or not has_length(self.train_dataset): return None
        if self.args.group_by_length:
            if is_datasets_available() and isinstance(self.train_dataset, datasets.Dataset): lengths = (self.train_dataset[self.args.length_column_name] if self.args.length_column_name in self.train_dataset.column_names else None)
            else: lengths = None
            model_input_name = self.tokenizer.model_input_names[0] if self.tokenizer is not None else None
            return LengthGroupedSampler(self.args.train_batch_size * self.args.gradient_accumulation_steps, dataset=self.train_dataset, lengths=lengths, model_input_name=model_input_name)
        else: return RandomSampler(self.train_dataset)
    def get_train_dataloader(self) -> DataLoader:
        if self.train_dataset is None: raise ValueError("Trainer: training requires a train_dataset.")
        train_dataset = self.train_dataset
        data_collator = self.data_collator
        if is_datasets_available() and isinstance(train_dataset, datasets.Dataset): train_dataset = self._remove_unused_columns(train_dataset, description="training")
        else: data_collator = self._get_collator_with_removed_columns(data_collator, description="training")
        dataloader_params = {"batch_size": self._train_batch_size, "collate_fn": data_collator, "num_workers": self.args.dataloader_num_workers, "pin_memory": self.args.dataloader_pin_memory, "persistent_workers": self.args.dataloader_persistent_workers}
        if not isinstance(train_dataset, torch.utils.data.IterableDataset):
            dataloader_params["sampler"] = self._get_train_sampler()
            dataloader_params["drop_last"] = self.args.dataloader_drop_last
            dataloader_params["worker_init_fn"] = seed_worker
            dataloader_params["prefetch_factor"] = self.args.dataloader_prefetch_factor
        return self.accelerator.prepare(DataLoader(train_dataset, **dataloader_params))
    def _get_eval_sampler(self, eval_dataset: Dataset) -> Optional[torch.utils.data.Sampler]:
        if self.args.use_legacy_prediction_loop:
            if is_torch_xla_available(): return SequentialDistributedSampler(eval_dataset, num_replicas=xm.xrt_world_size(), rank=xm.get_ordinal())
            elif is_sagemaker_mp_enabled(): return SequentialDistributedSampler(eval_dataset, num_replicas=smp.dp_size(), rank=smp.dp_rank(), batch_size=self.args.per_device_eval_batch_size)
            else: return SequentialSampler(eval_dataset)
        if self.args.world_size <= 1: return SequentialSampler(eval_dataset)
        else: return None
    def get_eval_dataloader(self, eval_dataset: Optional[Union[str, Dataset]] = None) -> DataLoader:
        if eval_dataset is None and self.eval_dataset is None: raise ValueError("Trainer: evaluation requires an eval_dataset.")
        dataloader_key = eval_dataset if isinstance(eval_dataset, str) else "eval"
        if (hasattr(self, "_eval_dataloaders") and dataloader_key in self._eval_dataloaders and self.args.dataloader_persistent_workers): return self.accelerator.prepare(self._eval_dataloaders[dataloader_key])
        eval_dataset = (self.eval_dataset[eval_dataset] if isinstance(eval_dataset, str) else eval_dataset if eval_dataset is not None else self.eval_dataset)
        data_collator = self.data_collator
        if is_datasets_available() and isinstance(eval_dataset, datasets.Dataset): eval_dataset = self._remove_unused_columns(eval_dataset, description="evaluation")
        else: data_collator = self._get_collator_with_removed_columns(data_collator, description="evaluation")
        dataloader_params = {"batch_size": self.args.eval_batch_size, "collate_fn": data_collator, "num_workers": self.args.dataloader_num_workers, "pin_memory": self.args.dataloader_pin_memory, "persistent_workers": self.args.dataloader_persistent_workers}
        if not isinstance(eval_dataset, torch.utils.data.IterableDataset):
            dataloader_params["sampler"] = self._get_eval_sampler(eval_dataset)
            dataloader_params["drop_last"] = self.args.dataloader_drop_last
            dataloader_params["prefetch_factor"] = self.args.dataloader_prefetch_factor
        eval_dataloader = DataLoader(eval_dataset, **dataloader_params)
        if self.args.dataloader_persistent_workers:
            if hasattr(self, "_eval_dataloaders"): self._eval_dataloaders[dataloader_key] = eval_dataloader
            else: self._eval_dataloaders = {dataloader_key: eval_dataloader}
        return self.accelerator.prepare(eval_dataloader)
    def get_test_dataloader(self, test_dataset: Dataset) -> DataLoader:
        data_collator = self.data_collator
        if is_datasets_available() and isinstance(test_dataset, datasets.Dataset): test_dataset = self._remove_unused_columns(test_dataset, description="test")
        else: data_collator = self._get_collator_with_removed_columns(data_collator, description="test")
        dataloader_params = {"batch_size": self.args.eval_batch_size, "collate_fn": data_collator, "num_workers": self.args.dataloader_num_workers, "pin_memory": self.args.dataloader_pin_memory, "persistent_workers": self.args.dataloader_persistent_workers}
        if not isinstance(test_dataset, torch.utils.data.IterableDataset):
            dataloader_params["sampler"] = self._get_eval_sampler(test_dataset)
            dataloader_params["drop_last"] = self.args.dataloader_drop_last
            dataloader_params["prefetch_factor"] = self.args.dataloader_prefetch_factor
        return self.accelerator.prepare(DataLoader(test_dataset, **dataloader_params))
    def create_optimizer_and_scheduler(self, num_training_steps: int):
        self.create_optimizer()
        if IS_SAGEMAKER_MP_POST_1_10 and smp.state.cfg.fp16: optimizer = self.optimizer.optimizer
        else: optimizer = self.optimizer
        self.create_scheduler(num_training_steps=num_training_steps, optimizer=optimizer)
    def get_decay_parameter_names(self, model) -> List[str]:
        decay_parameters = get_parameter_names(model, ALL_LAYERNORM_LAYERS)
        decay_parameters = [name for name in decay_parameters if "bias" not in name]
        return decay_parameters
    def create_optimizer(self):
        opt_model = self.model_wrapped if is_sagemaker_mp_enabled() else self.model
        if self.optimizer is None:
            decay_parameters = self.get_decay_parameter_names(opt_model)
            optimizer_grouped_parameters = [{"params": [p for n, p in opt_model.named_parameters() if (n in decay_parameters and p.requires_grad)], "weight_decay": self.args.weight_decay}, {"params": [p for n, p in opt_model.named_parameters() if (n not in decay_parameters and p.requires_grad)], "weight_decay": 0.0}]
            optimizer_cls, optimizer_kwargs = self.get_optimizer_cls_and_kwargs(self.args, opt_model)
            if "params" in optimizer_kwargs: optimizer_grouped_parameters = optimizer_kwargs.pop("params")
            if "model" in optimizer_kwargs: optimizer_grouped_parameters = optimizer_kwargs.pop("model")
            if "optimizer_dict" in optimizer_kwargs: optimizer_grouped_parameters = optimizer_kwargs.pop("optimizer_dict")
            self.optimizer = optimizer_cls(optimizer_grouped_parameters, **optimizer_kwargs)
            if optimizer_cls.__name__ == "Adam8bit":
                import sapiens_machine
                manager = sapiens_machine.optim.GlobalOptimManager.get_instance()
                skipped = 0
                for module in opt_model.modules():
                    if isinstance(module, nn.Embedding):
                        skipped += sum({p.data_ptr(): p.numel() for p in module.parameters()}.values())
                        logger.info(f"skipped {module}: {skipped/2**20}M params")
                        manager.register_module_override(module, "weight", {"optim_bits": 32})
                        logger.debug(f"sapiens_machine: will optimize {module} in fp32")
                logger.info(f"skipped: {skipped/2**20}M params")
        if is_sagemaker_mp_enabled(): self.optimizer = smp.DistributedOptimizer(self.optimizer)
        return self.optimizer
    def get_num_trainable_parameters(self): return sum(p.numel() for p in self.model.parameters() if p.requires_grad)
    def get_learning_rates(self):
        if self.optimizer is None: raise ValueError("Trainer optimizer is None, please make sure you have setup the optimizer before.")
        return [group["lr"] for group in self.optimizer.param_groups]
    def get_optimizer_group(self, param: Optional[Union[str, torch.nn.parameter.Parameter]] = None):
        if self.optimizer is None: raise ValueError("Trainer optimizer is None, please make sure you have setup the optimizer before.")
        if param is not None:
            for group in self.optimizer.param_groups:
                if param in group["params"]: return group
        return [group["params"] for group in self.optimizer.param_groups]
    @staticmethod
    def get_optimizer_cls_and_kwargs(args: TrainingArguments, model: Optional[PreTrainedModel] = None) -> Tuple[Any, Any]:
        optim_args = {}
        if args.optim_args:
            for mapping in args.optim_args.replace(" ", "").split(","):
                key, value = mapping.split("=")
                optim_args[key] = value
        optimizer_kwargs = {"lr": args.learning_rate}
        adam_kwargs = {"betas": (args.adam_beta1, args.adam_beta2), "eps": args.adam_epsilon}
        if args.optim == OptimizerNames.ADAFACTOR:
            optimizer_cls = Adafactor
            optimizer_kwargs.update({"scale_parameter": False, "relative_step": False})
        elif args.optim == OptimizerNames.ADAMW_HF:
            from .optimization import AdamW
            optimizer_cls = AdamW
            optimizer_kwargs.update(adam_kwargs)
        elif args.optim in [OptimizerNames.ADAMW_TORCH, OptimizerNames.ADAMW_TORCH_FUSED]:
            from torch.optim import AdamW
            optimizer_cls = AdamW
            optimizer_kwargs.update(adam_kwargs)
            if args.optim == OptimizerNames.ADAMW_TORCH_FUSED: optimizer_kwargs.update({"fused": True})
        elif args.optim == OptimizerNames.ADAMW_TORCH_XLA:
            try:
                from torch_xla.amp.syncfree import AdamW
                optimizer_cls = AdamW
                optimizer_kwargs.update(adam_kwargs)
            except ImportError: raise ValueError("Trainer failed to import syncfree AdamW from torch_xla.")
        elif args.optim == OptimizerNames.ADAMW_TORCH_NPU_FUSED:
            try:
                from torch_npu.optim import NpuFusedAdamW
                optimizer_cls = NpuFusedAdamW
                optimizer_kwargs.update(adam_kwargs)
            except ImportError: raise ValueError("Trainer failed to import FusedAdamW from torch_npu.")
        elif args.optim == OptimizerNames.ADAMW_APEX_FUSED:
            try:
                from apex.optimizers import FusedAdam
                optimizer_cls = FusedAdam
                optimizer_kwargs.update(adam_kwargs)
            except ImportError: raise ValueError("Trainer tried to instantiate apex FusedAdam but apex is not installed!")
        elif args.optim in [OptimizerNames.ADAMW_SAPIENS, OptimizerNames.ADAMW_8BIT, OptimizerNames.PAGED_ADAMW, OptimizerNames.PAGED_ADAMW_8BIT, OptimizerNames.ADEMAMIX,
        OptimizerNames.ADEMAMIX_8BIT, OptimizerNames.PAGED_ADEMAMIX, OptimizerNames.PAGED_ADEMAMIX_8BIT, OptimizerNames.LION, OptimizerNames.LION_8BIT, OptimizerNames.PAGED_LION,
        OptimizerNames.PAGED_LION_8BIT, OptimizerNames.RMSPROP_SAPIENS, OptimizerNames.RMSPROP_8BIT, OptimizerNames.RMSPROP_32BIT]:
            try:
                from sapiens_machine.optim import AdamW, Lion, RMSprop
                is_paged = False
                optim_bits = 32
                optimizer_cls = None
                additional_optim_kwargs = adam_kwargs
                if "paged" in args.optim: is_paged = True
                if "8bit" in args.optim: optim_bits = 8
                if "adam" in args.optim: optimizer_cls = AdamW
                elif "lion" in args.optim:
                    optimizer_cls = Lion
                    additional_optim_kwargs = {"betas": (args.adam_beta1, args.adam_beta2)}
                elif "rmsprop" in args.optim:
                    optimizer_cls = RMSprop
                    additional_optim_kwargs = optim_args
                elif "ademamix" in args.optim:
                    if is_sapiens_machine_available() and version.parse(importlib.metadata.version("sapiens_machine")) < version.parse("1.0.0"): raise ValueError("The AdEMAMix optimizer is not supported by your current version of `sapiens_machine`. Please install `sapiens_machine` >= 1.0.0.")
                    from sapiens_machine.optim import AdEMAMix
                    optimizer_cls = AdEMAMix
                    additional_optim_kwargs = {"betas": (float(optim_args.get("beta1", args.adam_beta1)), float(optim_args.get("beta2", args.adam_beta2)), float(optim_args.get("beta3", 0.9999))), "alpha": float(optim_args.get("alpha", 5.0)), "eps": float(optim_args.get("eps", args.adam_epsilon))}
                    if "t_alpha" in optim_args: additional_optim_kwargs["t_alpha"] = int(optim_args["t_alpha"])
                    if "t_beta3" in optim_args: additional_optim_kwargs["t_beta3"] = int(optim_args["t_beta3"])
                sapiens_kwargs = {"optim_bits": optim_bits}
                if "rmsprop" not in args.optim: sapiens_kwargs["is_paged"] = is_paged
                optimizer_kwargs.update(additional_optim_kwargs)
                optimizer_kwargs.update(sapiens_kwargs)
            except ImportError: raise ValueError("Trainer tried to instantiate sapiens optimizer but `sapiens_machine` is not installed!")
        elif args.optim == OptimizerNames.ADAMW_ANYPRECISION:
            try:
                from torchdistx.optimizers import AnyPrecisionAdamW
                optimizer_cls = AnyPrecisionAdamW
                optimizer_kwargs.update(adam_kwargs)
                optimizer_kwargs.update({"use_kahan_summation": strtobool(optim_args.get("use_kahan_summation", "False")), "momentum_dtype": getattr(torch, optim_args.get("momentum_dtype", "float32")), "variance_dtype": getattr(torch, optim_args.get("variance_dtype", "float32")), "compensation_buffer_dtype": getattr(torch, optim_args.get("compensation_buffer_dtype", "bfloat16"))})
            except ImportError: raise ValueError("Please install https://github.com/pytorch/torchdistx")
        elif args.optim == OptimizerNames.SGD: optimizer_cls = torch.optim.SGD
        elif args.optim == OptimizerNames.ADAGRAD: optimizer_cls = torch.optim.Adagrad
        elif args.optim == OptimizerNames.RMSPROP: optimizer_cls = torch.optim.RMSprop
        elif args.optim in [OptimizerNames.GALORE_ADAMW, OptimizerNames.GALORE_ADAMW_8BIT, OptimizerNames.GALORE_ADAFACTOR, OptimizerNames.GALORE_ADAMW_LAYERWISE, OptimizerNames.GALORE_ADAMW_8BIT_LAYERWISE, OptimizerNames.GALORE_ADAFACTOR_LAYERWISE]:
            if not is_galore_torch_available(): raise ImportError("You need to install `galore_torch` in order to use GaLore optimizers install it with `pip install git+https://github.com/jiaweizzhao/GaLore`")
            from galore_torch import GaLoreAdafactor, GaLoreAdamW, GaLoreAdamW8bit
            is_layerwise = args.optim.lower().endswith("layerwise")
            if is_layerwise and args.parallel_mode == ParallelMode.DISTRIBUTED: raise NotImplementedError("Layer-wise GaLore does not support DDP at this time")
            optimizer_mapping = {OptimizerNames.GALORE_ADAMW: GaLoreAdamW, OptimizerNames.GALORE_ADAMW_8BIT: GaLoreAdamW8bit, OptimizerNames.GALORE_ADAFACTOR: GaLoreAdafactor, OptimizerNames.GALORE_ADAMW_LAYERWISE: GaLoreAdamW, OptimizerNames.GALORE_ADAMW_8BIT_LAYERWISE: GaLoreAdamW8bit, OptimizerNames.GALORE_ADAFACTOR_LAYERWISE: GaLoreAdafactor}
            optimizer_cls = optimizer_mapping[args.optim]
            if args.optim_target_modules is None: raise ValueError("You need to define a `optim_target_modules` in order to properly use GaLore optimizers")
            if not isinstance(args.optim_target_modules, (list, str)): raise ValueError(f"`optim_target_modules` has to be a list of strings, a string corresponding to a regex, or a specific module or 'all-linear', you passed {args.optim_target_modules}")
            if model is None: raise ValueError("You need to pass a model in order to correctly initialize a GaLore optimizer.")
            logger.warning("Activated GaLoRE fine-tuning, depending on your model size and hardware, the training might take a while before starting. Please be patient!")
            all_linear = (isinstance(args.optim_target_modules, str) and args.optim_target_modules.replace("_", "-") == "all-linear")
            galore_params = []
            galore_params_names = []
            for module_name, module in model.named_modules():
                target_module_exists, is_regex = check_target_module_exists(args.optim_target_modules, module_name, return_is_regex=True)
                if not isinstance(module, nn.Linear):
                    if target_module_exists and not is_regex: logger.warning(f"{module_name} has been matched but ignored as GaLore only supports linear layers. Please double check your `optim_target_modules`!")
                    continue
                if not target_module_exists and not all_linear: continue
                galore_params.append(module.weight)
                galore_params_names.append(module_name + ".weight")
            if len(galore_params) == 0: raise ValueError(f"None of the target modules were found! ({args.optim_target_modules}). Please make sure to pass a valid `target_modules`.")
            non_galore_params = [p for n, p in model.named_parameters() if n not in galore_params_names]
            galore_optim_kwargs = {"rank": int(optim_args.pop("rank", 128)), "update_proj_gap": int(optim_args.pop("update_proj_gap", 200)), "scale": float(optim_args.pop("scale", 0.25)), "proj_type": optim_args.pop("proj_type", "std")}
            param_groups = [{"params": non_galore_params}, {"params": galore_params, **galore_optim_kwargs}]
            if is_layerwise:
                if args.gradient_accumulation_steps != 1: raise ValueError("Layerwise GaLoRE optimizer do not support gradient accumulation !")
                optimizer_dict = {}
                for param in non_galore_params:
                    param_groups = [{"params": [param]}]
                    optimizer_dict[param] = optimizer_cls(param_groups, **optimizer_kwargs)
                for param in galore_params:
                    param_groups = [{"params": [param], **galore_optim_kwargs}]
                    optimizer_dict[param] = optimizer_cls(param_groups, **optimizer_kwargs)
                def optimizer_hook(param):
                    if param.grad is not None:
                        optimizer_dict[param].step()
                        optimizer_dict[param].zero_grad()
                for param in model.parameters():
                    if param.requires_grad: param.register_post_accumulate_grad_hook(optimizer_hook)
                optimizer_cls = LayerWiseDummyOptimizer
                optimizer_kwargs.update({"optimizer_dict": optimizer_dict})
            optimizer_kwargs.update({"params": param_groups})
            if args.optim == OptimizerNames.GALORE_ADAFACTOR: optimizer_kwargs.update({"scale_parameter": False, "relative_step": False})
        elif args.optim in [OptimizerNames.LOMO, OptimizerNames.ADALOMO]:
            if not is_lomo_available(): raise ImportError("You need to install `lomo_optim` in order to use LOMO optimizers install it with `pip install lomo-optim`")
            if not is_sapiens_accelerator_available("0.30.0"): raise ImportError("You need to have `sapiens_accelerator>=0.30.0` to be able to use LOMO optimizers")
            if model is None: raise ValueError("You need to pass a `model` in order to correctly initialize a LOMO optimizer.")
            from lomo_optim import AdaLomo, Lomo
            if "ada" in args.optim: optimizer_cls = AdaLomo
            else: optimizer_cls = Lomo
            optimizer_kwargs.update({"model": model})
        elif args.optim == OptimizerNames.GROKADAMW:
            if not is_grokadamw_available(): raise ValueError("Please install grokadamw with `pip install grokadamw`")
            from grokadamw import GrokAdamW
            optimizer_cls = GrokAdamW
            optimizer_kwargs.update({"alpha_init": float(optim_args.get("alpha_init", 0.98)), "lamb": float(optim_args.get("lamb", 2.0)), "gamma": float(optim_args.get("gamma", 0.1)), "grokking_signal_decay_rate": float(optim_args.get("grokking_signal_decay_rate", 0.1)), "gradient_clipping": float(optim_args.get("gradient_clipping", 1.0))})
        elif args.optim == OptimizerNames.ADAMW_TORCH_4BIT:
            if not is_torchao_available() or version.parse(importlib.metadata.version("torchao")) < version.parse("0.4.0"): raise ImportError("You need to have `torchao>=0.4.0` in order to use torch 4-bit optimizers. Install it with `pip install torchao` or follow the instructions here: https://github.com/pytorch/ao")
            if version.parse(importlib.metadata.version("torch")) <= version.parse("2.4"): raise ImportError("You need to have `torch>2.4` in order to use torch 4-bit optimizers. Install it with `pip install --upgrade torch` it is available on pipy. Otherwise, you need to install torch nightly.")
            from torchao.prototype.low_bit_optim import AdamW4bit
            optimizer_cls = AdamW4bit
            optimizer_kwargs.update(adam_kwargs)
        elif args.optim in [OptimizerNames.SCHEDULE_FREE_ADAMW, OptimizerNames.SCHEDULE_FREE_SGD]:
            if not is_schedulefree_available(): raise ImportError("You need to install `schedulefree` in order to use schedulefree optimizers install it with `pip install schedulefree`")
            if not is_sapiens_accelerator_available("0.30.0"): raise ImportError("You need to have `sapiens_accelerator>=0.30.0` to be able to use schedulefree optimizers")
            from schedulefree import AdamWScheduleFree, SGDScheduleFree
            additional_optim_kwargs = {}
            if args.optim == OptimizerNames.SCHEDULE_FREE_ADAMW:
                optimizer_cls = AdamWScheduleFree
                additional_optim_kwargs = adam_kwargs
            elif args.optim == OptimizerNames.SCHEDULE_FREE_SGD: optimizer_cls = SGDScheduleFree
            else: raise ValueError("Invalid schedulefree optimizer")
            additional_optim_kwargs["weight_decay"] = args.weight_decay
            additional_optim_kwargs["warmup_steps"] = args.warmup_steps
            additional_optim_kwargs.update({"weight_lr_power": float(optim_args.get("weight_lr_power", 2.0)), "r": float(optim_args.get("r", 0.0))})
            optimizer_kwargs.update(additional_optim_kwargs)
        else: raise ValueError(f"Trainer cannot instantiate unsupported optimizer: {args.optim}")
        return optimizer_cls, optimizer_kwargs
    def create_scheduler(self, num_training_steps: int, optimizer: torch.optim.Optimizer = None):
        if self.lr_scheduler is None:
            self.lr_scheduler = get_scheduler(self.args.lr_scheduler_type, optimizer=self.optimizer if optimizer is None else optimizer, num_warmup_steps=self.args.get_warmup_steps(num_training_steps), num_training_steps=num_training_steps, scheduler_specific_kwargs=self.args.lr_scheduler_kwargs)
            self._created_lr_scheduler = True
        return self.lr_scheduler
    def num_examples(self, dataloader: DataLoader) -> int:
        try:
            dataset = dataloader.dataset
            if isinstance(dataset, IterableDatasetShard): return len(dataloader.dataset.dataset)
            return len(dataloader.dataset)
        except (NameError, AttributeError, TypeError): return len(dataloader) * self.args.per_device_train_batch_size
    def num_tokens(self, train_dl: DataLoader, max_steps: Optional[int] = None) -> int:
        train_tokens = 0
        try:
            for step, batch in enumerate(train_dl):
                tokens = batch["input_ids"].numel()
                if max_steps is not None: return tokens * max_steps
                train_tokens += tokens
            return train_tokens
        except KeyError:
            logger.warning("Cannot get num_tokens from dataloader")
            return train_tokens
    def _hp_search_setup(self, trial: Union["optuna.Trial", Dict[str, Any]]):
        self._trial = trial
        if self.hp_search_backend is None or trial is None: return
        if self.hp_search_backend == HPSearchBackend.OPTUNA: params = self.hp_space(trial)
        elif self.hp_search_backend == HPSearchBackend.RAY:
            params = trial
            params.pop("wandb", None)
        elif self.hp_search_backend == HPSearchBackend.SIGOPT: params = {k: int(v) if isinstance(v, str) else v for k, v in trial.assignments.items()}
        elif self.hp_search_backend == HPSearchBackend.WANDB: params = trial
        for key, value in params.items():
            if not hasattr(self.args, key):
                logger.warning(f"Trying to set {key} in the hyperparameter search but there is no corresponding field in `TrainingArguments`.")
                continue
            old_attr = getattr(self.args, key, None)
            if old_attr is not None: value = type(old_attr)(value)
            setattr(self.args, key, value)
        if self.hp_search_backend == HPSearchBackend.OPTUNA: logger.info(f"Trial: {trial.params}")
        if self.hp_search_backend == HPSearchBackend.SIGOPT: logger.info(f"SigOpt Assignments: {trial.assignments}")
        if self.hp_search_backend == HPSearchBackend.WANDB: logger.info(f"W&B Sweep parameters: {trial}")
        if self.is_deepspeed_enabled:
            if self.args.deepspeed is None: raise ValueError("For sweeps with deepspeed, `args.deepspeed` must be set")
            from sapiens_accelerator.utils import DeepSpeedPlugin
            from sapiens_transformers.integrations.deepspeed import HfTrainerDeepSpeedConfig
            self.args.hf_deepspeed_config = HfTrainerDeepSpeedConfig(self.args.deepspeed)
            self.args.hf_deepspeed_config.trainer_config_process(self.args)
            self.args.deepspeed_plugin = DeepSpeedPlugin(hf_ds_config=self.args.hf_deepspeed_config)
        self.create_accelerator_and_postprocess()
    def _report_to_hp_search(self, trial: Union["optuna.Trial", Dict[str, Any]], step: int, metrics: Dict[str, float]):
        if self.hp_search_backend is None or trial is None: return
        metrics = metrics.copy()
        self.objective = self.compute_objective(metrics)
        if self.hp_search_backend == HPSearchBackend.OPTUNA:
            import optuna
            if not trial.study._is_multi_objective():
                trial.report(self.objective, step)
                if trial.should_prune():
                    self.callback_handler.on_train_end(self.args, self.state, self.control)
                    raise optuna.TrialPruned()
        elif self.hp_search_backend == HPSearchBackend.RAY:
            import ray.train
            with tempfile.TemporaryDirectory() as temp_checkpoint_dir:
                checkpoint = None
                if self.control.should_save:
                    self._tune_save_checkpoint(checkpoint_dir=temp_checkpoint_dir)
                    checkpoint = ray.train.Checkpoint.from_directory(temp_checkpoint_dir)
                metrics["objective"] = self.objective
                ray.train.report(metrics, checkpoint=checkpoint)
    def _tune_save_checkpoint(self, checkpoint_dir: str):
        output_dir = os.path.join(checkpoint_dir, f"{PREFIX_CHECKPOINT_DIR}-{self.state.global_step}")
        self.save_model(output_dir, _internal_call=True)
        if self.args.should_save:
            self.state.stateful_callbacks["TrainerControl"] = self.control.state()
            self.state.save_to_json(os.path.join(output_dir, TRAINER_STATE_NAME))
            torch.save(self.optimizer.state_dict(), os.path.join(output_dir, OPTIMIZER_NAME))
            torch.save(self.lr_scheduler.state_dict(), os.path.join(output_dir, SCHEDULER_NAME))
    def call_model_init(self, trial=None):
        model_init_argcount = number_of_arguments(self.model_init)
        if model_init_argcount == 0: model = self.model_init()
        elif model_init_argcount == 1: model = self.model_init(trial)
        else: raise RuntimeError("model_init should have 0 or 1 argument.")
        if model is None: raise RuntimeError("model_init should not return None.")
        return model
    def torch_jit_model_eval(self, model, dataloader, training=False):
        if not training:
            if dataloader is None:
                logger.warning("failed to use PyTorch jit mode due to current dataloader is none.")
                return model
            example_batch = next(iter(dataloader))
            example_batch = self._prepare_inputs(example_batch)
            try:
                jit_model = copy.copy(model)
                jit_model.eval()
                original_forward = jit_model.__dict__.pop("_original_forward", None)
                if original_forward: jit_model.forward = original_forward
                with self.accelerator.autocast(cache_enabled=False), torch.no_grad():
                    if version.parse(version.parse(torch.__version__).base_version) >= version.parse("2.0.0"):
                        if isinstance(example_batch, dict): jit_model = torch.jit.trace(jit_model, example_kwarg_inputs=example_batch, strict=False)
                        else: jit_model = torch.jit.trace(jit_model, example_kwarg_inputs={key: example_batch[key] for key in example_batch}, strict=False)
                    else:
                        jit_inputs = []
                        for key in example_batch:
                            example_tensor = torch.ones_like(example_batch[key])
                            jit_inputs.append(example_tensor)
                        jit_inputs = tuple(jit_inputs)
                        jit_model = torch.jit.trace(jit_model, jit_inputs, strict=False)
                jit_model = torch.jit.freeze(jit_model)
                with torch.no_grad():
                    jit_model(**example_batch)
                    jit_model(**example_batch)
                model = jit_model
                self.use_cpu_amp = False
            except (RuntimeError, TypeError, ValueError, NameError, IndexError) as e: logger.warning(f"failed to use PyTorch jit mode due to: {e}.")
        return model
    def ipex_optimize_model(self, model, training=False, dtype=torch.float32):
        if not is_ipex_available(): raise ImportError("Using IPEX but IPEX is not installed or IPEX's version does not match current PyTorch, please refer to https://github.com/intel/intel-extension-for-pytorch.")
        import intel_extension_for_pytorch as ipex
        if not training:
            model.eval()
            dtype = torch.bfloat16 if not self.is_in_train and self.args.bf16_full_eval else dtype
            model = ipex.optimize(model, dtype=dtype, level="O1", conv_bn_folding=False, inplace=not self.is_in_train)
        else:
            if not model.training: model.train()
            model, self.optimizer = ipex.optimize(model, dtype=dtype, optimizer=self.optimizer, inplace=True, level="O1")
        return model
    def compare_trainer_and_checkpoint_args(self, training_args, trainer_state):
        attributes_map = {'logging_steps': 'logging_steps', 'eval_steps': 'eval_steps', 'save_steps': 'save_steps'}
        has_warning = False
        warning_str = "Warning: The following arguments do not match the ones in the `trainer_state.json` within the checkpoint directory: "
        for arg_attr, state_attr in attributes_map.items():
            arg_value = getattr(training_args, arg_attr, None)
            state_value = getattr(trainer_state, state_attr, None)
            if arg_value is not None and state_value is not None and arg_value != state_value:
                warning_str += f"\n\t{arg_attr}: {arg_value} (from args) != {state_value} (from trainer_state.json)"
                has_warning = True
        train_bs_args = training_args.per_device_train_batch_size
        train_bs_state = trainer_state.train_batch_size // max(1, training_args.n_gpu)
        if train_bs_args != train_bs_state:
            warning_str += f"\n\tper_device_train_batch_size: {train_bs_args} (from args) != {train_bs_state} (from trainer_state.json)"
            has_warning = True
        if has_warning: logger.warning_once(warning_str)
    def _wrap_model(self, model, training=True, dataloader=None):
        if self.args.use_ipex:
            dtype = torch.bfloat16 if self.use_cpu_amp else torch.float32
            model = self.ipex_optimize_model(model, training, dtype=dtype)
        if is_sagemaker_mp_enabled():
            if isinstance(self.model_wrapped, smp.model.DistributedModel): return self.model_wrapped
            return smp.DistributedModel(model, backward_passes_per_step=self.args.gradient_accumulation_steps)
        if self.accelerator.unwrap_model(model) is not model: return model
        if self.use_apex and training: model, self.optimizer = amp.initialize(model, self.optimizer, opt_level=self.args.fp16_opt_level)
        if self.args.n_gpu > 1 and not getattr(model, "is_loaded_in_8bit", False): model = nn.DataParallel(model)
        if self.args.jit_mode_eval:
            start_time = time.time()
            model = self.torch_jit_model_eval(model, dataloader, training)
            self.jit_compilation_time = round(time.time() - start_time, 4)
        if not training: return model
        if self.is_fsdp_xla_enabled:
            try:
                from torch_xla.distributed.fsdp import XlaFullyShardedDataParallel as FSDP
                from torch_xla.distributed.fsdp import checkpoint_module
                from torch_xla.distributed.fsdp.wrap import (size_based_auto_wrap_policy, transformer_auto_wrap_policy)
                if self.is_fsdp_xla_v2_enabled: from torch_xla.experimental.spmd_fully_sharded_data_parallel import (SpmdFullyShardedDataParallel as FSDPv2)
            except ImportError: raise ImportError("Missing XLA FSDP related module; please make sure to use torch-xla >= 2.0.")
            auto_wrap_policy = None
            auto_wrapper_callable = None
            default_transformer_cls_names_to_wrap = getattr(model, "_no_split_modules", None)
            fsdp_transformer_layer_cls_to_wrap = self.args.fsdp_config.get("transformer_layer_cls_to_wrap", default_transformer_cls_names_to_wrap)
            if self.args.fsdp_config["min_num_params"] > 0: auto_wrap_policy = functools.partial(size_based_auto_wrap_policy, min_num_params=self.args.fsdp_config["min_num_params"])
            elif fsdp_transformer_layer_cls_to_wrap is not None:
                transformer_cls_to_wrap = set()
                for layer_class in fsdp_transformer_layer_cls_to_wrap:
                    transformer_cls = get_module_class_from_name(model, layer_class)
                    if transformer_cls is None: raise Exception("Could not find the transformer layer class to wrap in the model.")
                    else: transformer_cls_to_wrap.add(transformer_cls)
                auto_wrap_policy = functools.partial(transformer_auto_wrap_policy, transformer_layer_cls=transformer_cls_to_wrap)
            fsdp_kwargs = self.args.xla_fsdp_config
            if self.args.fsdp_config["xla_fsdp_grad_ckpt"]:
                if model.config.use_cache:
                    logger.warning_once("`use_cache=True` is incompatible with gradient checkpointing. Setting `use_cache=False`.")
                    model.config.use_cache = False
                def auto_wrapper_callable(m, *args, **kwargs):
                    target_cls = FSDP if not self.is_fsdp_xla_v2_enabled else FSDPv2
                    return target_cls(checkpoint_module(m), *args, **kwargs)
            if self.is_fsdp_xla_v2_enabled:
                def shard_output(output, mesh):
                    from .modeling_outputs import CausalLMOutputWithPast
                    real_output = None
                    if isinstance(output, torch.Tensor): real_output = output
                    elif isinstance(output, tuple): real_output = output[0]
                    elif isinstance(output, CausalLMOutputWithPast): real_output = output.logits
                    if real_output is None: raise ValueError("Something went wrong, the output of the model shouldn't be `None`")
                    xs.mark_sharding(real_output, mesh, ("fsdp", None, None))
                self.model = model = FSDPv2(model, shard_output=shard_output, auto_wrap_policy=auto_wrap_policy, auto_wrapper_callable=auto_wrapper_callable)
            else: self.model = model = FSDP(model, auto_wrap_policy=auto_wrap_policy, auto_wrapper_callable=auto_wrapper_callable, **fsdp_kwargs)
            def patched_optimizer_step(optimizer, barrier=False, optimizer_args={}):
                loss = optimizer.step(**optimizer_args)
                if barrier: xm.mark_step()
                return loss
            xm.optimizer_step = patched_optimizer_step
        elif is_sagemaker_dp_enabled(): model = nn.parallel.DistributedDataParallel(model, device_ids=[int(os.getenv("SMDATAPARALLEL_LOCAL_RANK"))])
        elif self.args.parallel_mode == ParallelMode.DISTRIBUTED:
            if is_torch_neuroncore_available(): return model
            kwargs = {}
            if self.args.ddp_find_unused_parameters is not None: kwargs["find_unused_parameters"] = self.args.ddp_find_unused_parameters
            elif isinstance(model, PreTrainedModel): kwargs["find_unused_parameters"] = not model.is_gradient_checkpointing
            else: kwargs["find_unused_parameters"] = True
            if self.args.ddp_bucket_cap_mb is not None: kwargs["bucket_cap_mb"] = self.args.ddp_bucket_cap_mb
            if self.args.ddp_broadcast_buffers is not None: kwargs["broadcast_buffers"] = self.args.ddp_broadcast_buffers
            self.accelerator.ddp_handler = DistributedDataParallelKwargs(**kwargs)
        return model
    def train(self, resume_from_checkpoint: Optional[Union[str, bool]] = None, trial: Union["optuna.Trial", Dict[str, Any]] = None, ignore_keys_for_eval: Optional[List[str]] = None, **kwargs):
        if resume_from_checkpoint is False: resume_from_checkpoint = None
        self._memory_tracker.start()
        args = self.args
        self.is_in_train = True
        if self.neftune_noise_alpha is not None: self.model = self._activate_neftune(self.model)
        if (args.fp16_full_eval or args.bf16_full_eval) and not args.do_train and not self.is_model_parallel: self._move_model_to_device(self.model, args.device)
        if "model_path" in kwargs:
            resume_from_checkpoint = kwargs.pop("model_path")
            warnings.warn("`model_path` is deprecated and will be removed in a future version. Use `resume_from_checkpoint` instead.", FutureWarning)
        if len(kwargs) > 0: raise TypeError(f"train() received got unexpected keyword arguments: {', '.join(list(kwargs.keys()))}.")
        self._hp_search_setup(trial)
        self._train_batch_size = self.args.train_batch_size
        model_reloaded = False
        if self.model_init is not None:
            enable_full_determinism(self.args.seed) if self.args.full_determinism else set_seed(self.args.seed)
            self.model = self.call_model_init(trial)
            model_reloaded = True
            self.optimizer, self.lr_scheduler = None, None
        if isinstance(resume_from_checkpoint, bool) and resume_from_checkpoint:
            resume_from_checkpoint = get_last_checkpoint(args.output_dir)
            if resume_from_checkpoint is None: raise ValueError(f"No valid checkpoint found in output directory ({args.output_dir})")
        if resume_from_checkpoint is not None:
            if not is_sagemaker_mp_enabled() and not self.is_deepspeed_enabled and not self.is_fsdp_enabled: self._load_from_checkpoint(resume_from_checkpoint)
            state = TrainerState.load_from_json(os.path.join(resume_from_checkpoint, TRAINER_STATE_NAME))
            if state.train_batch_size is not None: self._train_batch_size = state.train_batch_size
        if model_reloaded:
            if self.place_model_on_device: self._move_model_to_device(self.model, args.device)
            self.model_wrapped = self.model
        inner_training_loop = find_executable_batch_size(self._inner_training_loop, self._train_batch_size, args.auto_find_batch_size)
        if args.push_to_hub:
            try:
                hf_hub_utils.disable_progress_bars()
                return inner_training_loop(args=args, resume_from_checkpoint=resume_from_checkpoint, trial=trial, ignore_keys_for_eval=ignore_keys_for_eval)
            finally: hf_hub_utils.enable_progress_bars()
        else: return inner_training_loop(args=args, resume_from_checkpoint=resume_from_checkpoint, trial=trial, ignore_keys_for_eval=ignore_keys_for_eval)
    def _inner_training_loop(self, batch_size=None, args=None, resume_from_checkpoint=None, trial=None, ignore_keys_for_eval=None):
        self.accelerator.free_memory()
        self._train_batch_size = batch_size
        if self.args.auto_find_batch_size:
            if self.state.train_batch_size != self._train_batch_size:
                from sapiens_accelerator.utils import release_memory
                (self.model_wrapped,) = release_memory(self.model_wrapped)
                self.model_wrapped = self.model
                if self.is_deepspeed_enabled:
                    original_bs = self.args.per_device_train_batch_size
                    self.args.per_device_train_batch_size = self._train_batch_size // max(1, self.args.n_gpu)
                    self.propagate_args_to_deepspeed(True)
                    self.args.per_device_train_batch_size = original_bs
            self.state.train_batch_size = self._train_batch_size
        logger.debug(f"Currently training with a batch size of: {self._train_batch_size}")
        train_dataloader = self.get_train_dataloader()
        if self.is_fsdp_xla_v2_enabled: train_dataloader = tpu_spmd_dataloader(train_dataloader)
        total_train_batch_size = self._train_batch_size * args.gradient_accumulation_steps * args.world_size
        len_dataloader = None
        num_train_tokens = None
        if has_length(train_dataloader):
            len_dataloader = len(train_dataloader)
            num_update_steps_per_epoch = len_dataloader // args.gradient_accumulation_steps
            num_update_steps_per_epoch = max(num_update_steps_per_epoch, 1)
            num_examples = self.num_examples(train_dataloader)
            if args.max_steps > 0:
                max_steps = args.max_steps
                num_train_epochs = args.max_steps // num_update_steps_per_epoch + int(args.max_steps % num_update_steps_per_epoch > 0)
                num_train_samples = args.max_steps * total_train_batch_size
                if args.include_tokens_per_second: num_train_tokens = (self.num_tokens(train_dataloader, args.max_steps) * args.gradient_accumulation_steps)
            else:
                max_steps = math.ceil(args.num_train_epochs * num_update_steps_per_epoch)
                num_train_epochs = math.ceil(args.num_train_epochs)
                num_train_samples = self.num_examples(train_dataloader) * args.num_train_epochs
                if args.include_tokens_per_second: num_train_tokens = self.num_tokens(train_dataloader) * args.num_train_epochs
        elif args.max_steps > 0:
            max_steps = args.max_steps
            num_train_epochs = sys.maxsize
            num_update_steps_per_epoch = max_steps
            num_examples = total_train_batch_size * args.max_steps
            num_train_samples = args.max_steps * total_train_batch_size
            if args.include_tokens_per_second: num_train_tokens = self.num_tokens(train_dataloader, args.max_steps) * args.gradient_accumulation_steps
        else: raise ValueError(f"args.max_steps must be set to a positive value if dataloader does not have a length, was {args.max_steps}")
        if DebugOption.UNDERFLOW_OVERFLOW in self.args.debug:
            if self.args.n_gpu > 1: raise ValueError("Currently --debug underflow_overflow is not supported under DP. Please use DDP (torchrun or torch.distributed.launch (deprecated)).")
            else: debug_overflow = DebugUnderflowOverflow(self.model)
        delay_optimizer_creation = is_sagemaker_mp_enabled() or self.is_fsdp_xla_enabled or self.is_fsdp_enabled
        if self._created_lr_scheduler:
            self.lr_scheduler = None
            self._created_lr_scheduler = False
        if self.is_deepspeed_enabled: self.optimizer, self.lr_scheduler = deepspeed_init(self, num_training_steps=max_steps)
        if not delay_optimizer_creation: self.create_optimizer_and_scheduler(num_training_steps=max_steps)
        self.state = TrainerState(stateful_callbacks=[cb for cb in self.callback_handler.callbacks + [self.control] if isinstance(cb, ExportableState)])
        self.state.is_hyper_param_search = trial is not None
        self.state.train_batch_size = self._train_batch_size
        if args.logging_steps is not None:
            if args.logging_steps < 1: self.state.logging_steps = math.ceil(max_steps * args.logging_steps)
            else: self.state.logging_steps = args.logging_steps
        if args.eval_steps is not None:
            if args.eval_steps < 1: self.state.eval_steps = math.ceil(max_steps * args.eval_steps)
            else: self.state.eval_steps = args.eval_steps
        if args.save_steps is not None:
            if args.save_steps < 1: self.state.save_steps = math.ceil(max_steps * args.save_steps)
            else: self.state.save_steps = args.save_steps
        if args.gradient_checkpointing: self.model.gradient_checkpointing_enable(gradient_checkpointing_kwargs=args.gradient_checkpointing_kwargs)
        model = self._wrap_model(self.model_wrapped)
        use_accelerator_prepare = True if model is self.model else False
        if delay_optimizer_creation:
            if use_accelerator_prepare:
                self._fsdp_qlora_plugin_updates()
                self.model = self.accelerator.prepare(self.model)
            self.create_optimizer_and_scheduler(num_training_steps=max_steps)
        if use_accelerator_prepare:
            self.model.train()
            if hasattr(self.lr_scheduler, "step"):
                if self.use_apex: model = self.accelerator.prepare(self.model)
                else: model, self.optimizer = self.accelerator.prepare(self.model, self.optimizer)
            else: model, self.optimizer, self.lr_scheduler = self.accelerator.prepare(self.model, self.optimizer, self.lr_scheduler)
        elif self.args.optim in [OptimizerNames.LOMO, OptimizerNames.ADALOMO]: self.optimizer = self.accelerator.prepare(self.optimizer)
        if self.is_fsdp_enabled: self.model = self.model_wrapped = model
        if model is not self.model: self.model_wrapped = model
        if self.is_deepspeed_enabled: self.deepspeed = self.model_wrapped
        if resume_from_checkpoint is not None:
            if self.is_deepspeed_enabled: deepspeed_load_checkpoint(self.model_wrapped, resume_from_checkpoint, load_module_strict=not _is_peft_model(self.model))
            elif is_sagemaker_mp_enabled() or self.is_fsdp_enabled: self._load_from_checkpoint(resume_from_checkpoint, self.model_wrapped)
        self._load_optimizer_and_scheduler(resume_from_checkpoint)
        logger.info("***** Running training *****")
        logger.info(f"  Num examples = {num_examples:,}")
        logger.info(f"  Num Epochs = {num_train_epochs:,}")
        logger.info(f"  Instantaneous batch size per device = {self.args.per_device_train_batch_size:,}")
        if self.args.per_device_train_batch_size != self._train_batch_size: logger.info(f"  Training with DataParallel so batch size has been adjusted to: {self._train_batch_size:,}")
        logger.info(f"  Total train batch size (w. parallel, distributed & accumulation) = {total_train_batch_size:,}")
        logger.info(f"  Gradient Accumulation steps = {args.gradient_accumulation_steps}")
        logger.info(f"  Total optimization steps = {max_steps:,}")
        logger.info(f"  Number of trainable parameters = {get_model_param_count(model, trainable_only=True):,}")
        self.state.epoch = 0
        start_time = time.time()
        epochs_trained = 0
        steps_trained_in_current_epoch = 0
        steps_trained_progress_bar = None
        if resume_from_checkpoint is not None and os.path.isfile(os.path.join(resume_from_checkpoint, TRAINER_STATE_NAME)):
            self.state = TrainerState.load_from_json(os.path.join(resume_from_checkpoint, TRAINER_STATE_NAME))
            self.compare_trainer_and_checkpoint_args(self.args, self.state)
            self._load_callback_state()
            epochs_trained = int(self.state.global_step // num_update_steps_per_epoch)
            if not args.ignore_data_skip:
                steps_trained_in_current_epoch = self.state.global_step % (num_update_steps_per_epoch)
                steps_trained_in_current_epoch *= args.gradient_accumulation_steps
            else: steps_trained_in_current_epoch = 0
            logger.info("  Continuing training from checkpoint, will skip to saved global_step")
            logger.info(f"  Continuing training from epoch {epochs_trained}")
            logger.info(f"  Continuing training from global step {self.state.global_step}")
            if not args.ignore_data_skip: logger.info(f"  Will skip the first {epochs_trained} epochs then the first {steps_trained_in_current_epoch} batches in the first epoch.")
        self.callback_handler.model = self.model
        self.callback_handler.optimizer = self.optimizer
        self.callback_handler.lr_scheduler = self.lr_scheduler
        self.callback_handler.train_dataloader = train_dataloader
        if self.hp_name is not None and self._trial is not None: self.state.trial_name = self.hp_name(self._trial)
        if trial is not None:
            assignments = trial.assignments if self.hp_search_backend == HPSearchBackend.SIGOPT else trial
            self.state.trial_params = hp_params(assignments)
        else: self.state.trial_params = None
        self.state.max_steps = max_steps
        self.state.num_train_epochs = num_train_epochs
        self.state.is_local_process_zero = self.is_local_process_zero()
        self.state.is_world_process_zero = self.is_world_process_zero()
        tr_loss = torch.tensor(0.0).to(args.device)
        self._total_loss_scalar = 0.0
        self._globalstep_last_logged = self.state.global_step
        model.zero_grad()
        grad_norm: Optional[float] = None
        self.control = self.callback_handler.on_train_begin(args, self.state, self.control)
        if args.eval_on_start: self._evaluate(trial, ignore_keys_for_eval, skip_scheduler=True)
        total_batched_samples = 0
        for epoch in range(epochs_trained, num_train_epochs):
            epoch_iterator = train_dataloader
            if hasattr(epoch_iterator, "set_epoch"): epoch_iterator.set_epoch(epoch)
            if args.past_index >= 0: self._past = None
            steps_in_epoch = (len(epoch_iterator) if len_dataloader is not None else args.max_steps * args.gradient_accumulation_steps)
            self.control = self.callback_handler.on_epoch_begin(args, self.state, self.control)
            if epoch == epochs_trained and resume_from_checkpoint is not None and steps_trained_in_current_epoch == 0: self._load_rng_state(resume_from_checkpoint)
            rng_to_sync = False
            steps_skipped = 0
            if steps_trained_in_current_epoch > 0:
                epoch_iterator = skip_first_batches(epoch_iterator, steps_trained_in_current_epoch)
                steps_skipped = steps_trained_in_current_epoch
                steps_trained_in_current_epoch = 0
                rng_to_sync = True
            step = -1
            for step, inputs in enumerate(epoch_iterator):
                total_batched_samples += 1
                if self.args.include_num_input_tokens_seen:
                    main_input_name = getattr(self.model, "main_input_name", "input_ids")
                    if main_input_name not in inputs: logger.warning("Tried to track the number of tokens seen, however the current model is not configured properly to know what item is the input. To fix this, add a `main_input_name` attribute to the model class you are using.")
                    else: self.state.num_input_tokens_seen += (torch.sum(self.accelerator.gather(torch.tensor(inputs[main_input_name].numel(), device=self.args.device, dtype=torch.int64))).cpu().item())
                if rng_to_sync:
                    self._load_rng_state(resume_from_checkpoint)
                    rng_to_sync = False
                if steps_trained_in_current_epoch > 0:
                    steps_trained_in_current_epoch -= 1
                    if steps_trained_progress_bar is not None: steps_trained_progress_bar.update(1)
                    if steps_trained_in_current_epoch == 0: self._load_rng_state(resume_from_checkpoint)
                    continue
                elif steps_trained_progress_bar is not None:
                    steps_trained_progress_bar.close()
                    steps_trained_progress_bar = None
                if step % args.gradient_accumulation_steps == 0: self.control = self.callback_handler.on_step_begin(args, self.state, self.control)
                with self.accelerator.accumulate(model): tr_loss_step = self.training_step(model, inputs)
                if (args.logging_nan_inf_filter and not is_torch_xla_available() and (torch.isnan(tr_loss_step) or torch.isinf(tr_loss_step))): tr_loss += tr_loss / (1 + self.state.global_step - self._globalstep_last_logged)
                else:
                    if tr_loss.device != tr_loss_step.device: raise ValueError(f"Calculated loss must be on the original device: {tr_loss.device} but device in use is {tr_loss_step.device}")
                    tr_loss += tr_loss_step
                self.current_flos += float(self.floating_point_ops(inputs))
                is_last_step_and_steps_less_than_grad_acc = (steps_in_epoch <= args.gradient_accumulation_steps and (step + 1) == steps_in_epoch)
                if (total_batched_samples % args.gradient_accumulation_steps == 0 or is_last_step_and_steps_less_than_grad_acc):
                    if is_last_step_and_steps_less_than_grad_acc: self.accelerator.gradient_state._set_sync_gradients(True)
                    if args.max_grad_norm is not None and args.max_grad_norm > 0:
                        if is_sagemaker_mp_enabled() and args.fp16: _grad_norm = self.optimizer.clip_master_grads(args.max_grad_norm)
                        elif self.use_apex: _grad_norm = nn.utils.clip_grad_norm_(amp.master_params(self.optimizer), args.max_grad_norm)
                        else: _grad_norm = self.accelerator.clip_grad_norm_(model.parameters(), args.max_grad_norm)
                        if (is_sapiens_accelerator_available() and self.accelerator.distributed_type == DistributedType.DEEPSPEED):
                            grad_norm = model.get_global_grad_norm()
                            if hasattr(grad_norm, "item"): grad_norm = grad_norm.item()
                        else: grad_norm = _grad_norm
                    self.control = self.callback_handler.on_pre_optimizer_step(args, self.state, self.control)
                    self.optimizer.step()
                    self.control = self.callback_handler.on_optimizer_step(args, self.state, self.control)
                    optimizer_was_run = not self.accelerator.optimizer_step_was_skipped
                    if optimizer_was_run:
                        if not isinstance(self.lr_scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau): self.lr_scheduler.step()
                    model.zero_grad()
                    self.state.global_step += 1
                    self.state.epoch = epoch + (step + 1 + steps_skipped) / steps_in_epoch
                    self.control = self.callback_handler.on_step_end(args, self.state, self.control)
                    self._maybe_log_save_evaluate(tr_loss, grad_norm, model, trial, epoch, ignore_keys_for_eval)
                else: self.control = self.callback_handler.on_substep_end(args, self.state, self.control)
                if self.control.should_epoch_stop or self.control.should_training_stop:
                    if is_torch_xla_available(): xm.mark_step()
                    break
            if step < 0:
                logger.warning(f"There seems not to be a single sample in your epoch_iterator, stopping training at step {self.state.global_step}! This is expected if you're using an IterableDataset and set num_steps ({max_steps}) higher than the number of available samples.")
                self.control.should_training_stop = True
            self.control = self.callback_handler.on_epoch_end(args, self.state, self.control)
            self._maybe_log_save_evaluate(tr_loss, grad_norm, model, trial, epoch, ignore_keys_for_eval)
            if DebugOption.TPU_METRICS_DEBUG in self.args.debug:
                if is_torch_xla_available(): xm.master_print(met.metrics_report())
                else: logger.warning("You enabled PyTorch/XLA debug metrics but you don't have a TPU configured. Check your training configuration if this is unexpected.")
            if self.control.should_training_stop: break
        if args.past_index and hasattr(self, "_past"): delattr(self, "_past")
        logger.info("\n\nTraining completed.\n\n")
        if args.load_best_model_at_end and self.state.best_model_checkpoint is not None:
            if is_torch_xla_available(): xm.rendezvous("load_best_model_at_end")
            elif args.parallel_mode == ParallelMode.DISTRIBUTED: dist.barrier()
            elif is_sagemaker_mp_enabled(): smp.barrier()
            self._load_best_model()
        self._total_loss_scalar += tr_loss.item()
        effective_global_step = max(self.state.global_step, 0.001)
        train_loss = self._total_loss_scalar / effective_global_step
        metrics = speed_metrics("train", start_time, num_samples=num_train_samples, num_steps=self.state.max_steps, num_tokens=num_train_tokens)
        self.store_flos()
        metrics["total_flos"] = self.state.total_flos
        metrics["train_loss"] = train_loss
        self.is_in_train = False
        self._memory_tracker.stop_and_update_metrics(metrics)
        self.log(metrics)
        run_dir = self._get_output_dir(trial)
        checkpoints_sorted = self._sorted_checkpoints(use_mtime=False, output_dir=run_dir)
        if self.args.should_save and self.state.best_model_checkpoint is not None and self.args.save_total_limit == 1:
            for checkpoint in checkpoints_sorted:
                if not os.path.samefile(checkpoint, self.state.best_model_checkpoint):
                    logger.info(f"Deleting older checkpoint [{checkpoint}] due to args.save_total_limit")
                    shutil.rmtree(checkpoint, ignore_errors=True)
        self.control = self.callback_handler.on_train_end(args, self.state, self.control)
        self._finish_current_push()
        if self.neftune_noise_alpha is not None: self._deactivate_neftune(self.model)
        return TrainOutput(self.state.global_step, train_loss, metrics)
    def _get_output_dir(self, trial):
        if self.hp_search_backend is not None and trial is not None:
            if self.hp_search_backend == HPSearchBackend.OPTUNA: run_id = trial.number
            elif self.hp_search_backend == HPSearchBackend.RAY:
                import ray.train
                run_id = ray.train.get_context().get_trial_id()
            elif self.hp_search_backend == HPSearchBackend.SIGOPT: run_id = trial.id
            elif self.hp_search_backend == HPSearchBackend.WANDB:
                import wandb
                run_id = wandb.run.id
            run_name = self.hp_name(trial) if self.hp_name is not None else f"run-{run_id}"
            run_dir = os.path.join(self.args.output_dir, run_name)
        else: run_dir = self.args.output_dir
        return run_dir
    def _load_from_checkpoint(self, resume_from_checkpoint, model=None):
        if model is None: model = self.model
        config_file = os.path.join(resume_from_checkpoint, CONFIG_NAME)
        adapter_weights_file = os.path.join(resume_from_checkpoint, ADAPTER_WEIGHTS_NAME)
        adapter_safe_weights_file = os.path.join(resume_from_checkpoint, ADAPTER_SAFE_WEIGHTS_NAME)
        weights_file = os.path.join(resume_from_checkpoint, WEIGHTS_NAME)
        weights_index_file = os.path.join(resume_from_checkpoint, WEIGHTS_INDEX_NAME)
        safe_weights_file = os.path.join(resume_from_checkpoint, SAFE_WEIGHTS_NAME)
        safe_weights_index_file = os.path.join(resume_from_checkpoint, SAFE_WEIGHTS_INDEX_NAME)
        is_fsdp_ckpt = os.path.isdir(resume_from_checkpoint) and (any(FSDP_MODEL_NAME in folder_name for folder_name in os.listdir(resume_from_checkpoint) if os.path.isdir(os.path.join(resume_from_checkpoint, folder_name))) or os.path.isfile(os.path.join(resume_from_checkpoint, f"{FSDP_MODEL_NAME}.bin")))
        adapter_subdirs = ([folder_name for folder_name in os.listdir(resume_from_checkpoint) if os.path.isdir(os.path.join(resume_from_checkpoint, folder_name)) and (os.path.isfile(os.path.join(resume_from_checkpoint, folder_name, ADAPTER_WEIGHTS_NAME)) or os.path.isfile(os.path.join(resume_from_checkpoint, folder_name, ADAPTER_SAFE_WEIGHTS_NAME)))] if os.path.isdir(resume_from_checkpoint) else [])
        if is_fsdp_ckpt and not self.is_fsdp_enabled: raise ValueError(f"Checkpoint found at {resume_from_checkpoint} is only supported when using PyTorch FSDP")
        if not (any(os.path.isfile(f) for f in [weights_file, safe_weights_file, weights_index_file, safe_weights_index_file, adapter_weights_file, adapter_safe_weights_file]) or is_fsdp_ckpt or adapter_subdirs): raise ValueError(f"Can't find a valid checkpoint at {resume_from_checkpoint}")
        logger.info(f"Loading model from {resume_from_checkpoint}.")
        if os.path.isfile(config_file):
            config = PretrainedConfig.from_json_file(config_file)
            checkpoint_version = config.sapiens_transformers_version
            if checkpoint_version is not None and checkpoint_version != __version__: logger.warning(f"You are resuming training from a checkpoint trained with {checkpoint_version} of Transformers but your current version is {__version__}. This is not recommended and could yield to errors or unwanted behaviors.")
        if os.path.isfile(weights_file) or os.path.isfile(safe_weights_file) or is_fsdp_ckpt:
            weights_only_kwarg = {"weights_only": True} if is_torch_greater_or_equal_than_1_13 else {}
            if is_sagemaker_mp_enabled():
                if os.path.isfile(os.path.join(resume_from_checkpoint, "user_content.pt")): smp.resume_from_checkpoint(path=resume_from_checkpoint, tag=WEIGHTS_NAME, partial=False, load_optimizer=False)
                else:
                    if hasattr(self.args, "fp16") and self.args.fp16 is True: logger.warning("Enabling FP16 and loading from smp < 1.10 checkpoint together is not suppported.")
                    state_dict = torch.load(weights_file, map_location="cpu", **weights_only_kwarg)
                    state_dict["_smp_is_partial"] = False
                    load_result = model.load_state_dict(state_dict, strict=True)
                    del state_dict
            elif self.is_fsdp_enabled: load_fsdp_model(self.accelerator.state.fsdp_plugin, self.accelerator, model, resume_from_checkpoint, **_get_fsdp_ckpt_kwargs())
            else:
                if self.args.save_safetensors and os.path.isfile(safe_weights_file): state_dict = safetensors.torch.load_file(safe_weights_file, device="cpu")
                else: state_dict = torch.load(weights_file, map_location="cpu", **weights_only_kwarg)
                load_result = model.load_state_dict(state_dict, False)
                del state_dict
                self._issue_warnings_after_load(load_result)
        elif _is_peft_model(model):
            if (hasattr(model, "active_adapter") or hasattr(model, "active_adapters")) and hasattr(model, "load_adapter"):
                if os.path.exists(resume_from_checkpoint):
                    if hasattr(model, "active_adapters"):
                        active_adapters = model.active_adapters
                        if len(active_adapters) > 1: logger.warning("Multiple active adapters detected will only consider the first adapter")
                        active_adapter = active_adapters[0]
                    else: active_adapter = model.active_adapter
                    if adapter_subdirs:
                        for subdir_name in adapter_subdirs:
                            peft_id = os.path.join(resume_from_checkpoint, subdir_name)
                            model.load_adapter(peft_id, subdir_name, is_trainable=(subdir_name == active_adapter))
                        model.set_adapter(active_adapter)
                    else: model.load_adapter(resume_from_checkpoint, active_adapter, is_trainable=True)
                else: logger.warning(f"The intermediate checkpoints of PEFT may not be saved correctly, consider using a custom callback to save {ADAPTER_WEIGHTS_NAME} in corresponding saving folders.")
            else: logger.warning("Could not load adapter model, make sure to have `peft>=0.3.0` installed")
        else:
            load_result = load_sharded_checkpoint(model, resume_from_checkpoint, strict=is_sagemaker_mp_enabled(), prefer_safe=self.args.save_safetensors)
            if not is_sagemaker_mp_enabled(): self._issue_warnings_after_load(load_result)
    def _load_best_model(self):
        logger.info(f"Loading best model from {self.state.best_model_checkpoint} (score: {self.state.best_metric}).")
        best_model_path = os.path.join(self.state.best_model_checkpoint, WEIGHTS_NAME)
        best_safe_model_path = os.path.join(self.state.best_model_checkpoint, SAFE_WEIGHTS_NAME)
        best_adapter_model_path = os.path.join(self.state.best_model_checkpoint, ADAPTER_WEIGHTS_NAME)
        best_safe_adapter_model_path = os.path.join(self.state.best_model_checkpoint, ADAPTER_SAFE_WEIGHTS_NAME)
        model = self.model_wrapped if is_sagemaker_mp_enabled() else self.model
        if self.is_deepspeed_enabled: deepspeed_load_checkpoint(self.model_wrapped, self.state.best_model_checkpoint, load_module_strict=not _is_peft_model(self.model))
        elif self.is_fsdp_enabled: load_result = load_fsdp_model(self.accelerator.state.fsdp_plugin, self.accelerator, model, self.state.best_model_checkpoint, **_get_fsdp_ckpt_kwargs())
        elif (os.path.exists(best_model_path) or os.path.exists(best_safe_model_path) or os.path.exists(best_adapter_model_path) or os.path.exists(best_safe_adapter_model_path)):
            has_been_loaded = True
            weights_only_kwarg = {"weights_only": True} if is_torch_greater_or_equal_than_1_13 else {}
            if is_sagemaker_mp_enabled():
                if os.path.isfile(os.path.join(self.state.best_model_checkpoint, "user_content.pt")): smp.resume_from_checkpoint(path=self.state.best_model_checkpoint, tag=WEIGHTS_NAME, partial=False, load_optimizer=False)
                else:
                    if self.args.save_safetensors and os.path.isfile(best_safe_model_path): state_dict = safetensors.torch.load_file(best_safe_model_path, device="cpu")
                    else: state_dict = torch.load(best_model_path, map_location="cpu", **weights_only_kwarg)
                    state_dict["_smp_is_partial"] = False
                    load_result = model.load_state_dict(state_dict, strict=True)
            else:
                if _is_peft_model(model):
                    if (hasattr(model, "active_adapter") or hasattr(model, "active_adapters")) and hasattr(model, "load_adapter"):
                        if hasattr(model, "active_adapters"):
                            active_adapter = model.active_adapters[0]
                            if len(model.active_adapters) > 1: logger.warning("Detected multiple active adapters, will only consider the first one")
                        else: active_adapter = model.active_adapter
                        if os.path.exists(best_adapter_model_path) or os.path.exists(best_safe_adapter_model_path):
                            model.load_adapter(self.state.best_model_checkpoint, active_adapter)
                            from torch.nn.modules.module import _IncompatibleKeys
                            load_result = _IncompatibleKeys([], [])
                        else:
                            logger.warning(f"The intermediate checkpoints of PEFT may not be saved correctly, consider using a custom callback to save {ADAPTER_WEIGHTS_NAME} in corresponding saving folders.")
                            has_been_loaded = False
                    else:
                        logger.warning("Could not load adapter model, make sure to have `peft>=0.3.0` installed")
                        has_been_loaded = False
                else:
                    if self.args.save_safetensors and os.path.isfile(best_safe_model_path): state_dict = safetensors.torch.load_file(best_safe_model_path, device="cpu")
                    else: state_dict = torch.load(best_model_path, map_location="cpu", **weights_only_kwarg)
                    load_result = model.load_state_dict(state_dict, False)
                if not is_sagemaker_mp_enabled() and has_been_loaded: self._issue_warnings_after_load(load_result)
        elif os.path.exists(os.path.join(self.state.best_model_checkpoint, SAFE_WEIGHTS_INDEX_NAME)) or os.path.exists(os.path.join(self.state.best_model_checkpoint, WEIGHTS_INDEX_NAME)):
            load_result = load_sharded_checkpoint(model, self.state.best_model_checkpoint, strict=is_sagemaker_mp_enabled())
            if not is_sagemaker_mp_enabled(): self._issue_warnings_after_load(load_result)
        else: logger.warning(f"Could not locate the best model at {best_model_path}, if you are running a distributed training on multiple nodes, you should activate `--save_on_each_node`.")
    def _issue_warnings_after_load(self, load_result):
        if len(load_result.missing_keys) != 0:
            if self.model._keys_to_ignore_on_save is not None and set(load_result.missing_keys) == set(self.model._keys_to_ignore_on_save): self.model.tie_weights()
            else: logger.warning(f"There were missing keys in the checkpoint model loaded: {load_result.missing_keys}.")
        if len(load_result.unexpected_keys) != 0: logger.warning(f"There were unexpected keys in the checkpoint model loaded: {load_result.unexpected_keys}.")
    def _evaluate(self, trial, ignore_keys_for_eval, skip_scheduler=False):
        metrics = self.evaluate(ignore_keys=ignore_keys_for_eval)
        self._report_to_hp_search(trial, self.state.global_step, metrics)
        if isinstance(self.lr_scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau) and not skip_scheduler:
            metric_to_check = self.args.metric_for_best_model
            if not metric_to_check.startswith("eval_"): metric_to_check = f"eval_{metric_to_check}"
            try: self.lr_scheduler.step(metrics[metric_to_check])
            except KeyError as exc: raise KeyError(f"The `metric_for_best_model` training argument is set to '{metric_to_check}', which is not found in the evaluation metrics. The available evaluation metrics are: {list(metrics.keys())}. Consider changing the `metric_for_best_model` via the TrainingArguments.") from exc
        return metrics
    def _maybe_log_save_evaluate(self, tr_loss, grad_norm, model, trial, epoch, ignore_keys_for_eval):
        if self.control.should_log and self.state.global_step > self._globalstep_last_logged:
            if is_torch_xla_available(): xm.mark_step()
            logs: Dict[str, float] = {}
            tr_loss_scalar = self._nested_gather(tr_loss).mean().item()
            tr_loss -= tr_loss
            logs["loss"] = round(tr_loss_scalar / (self.state.global_step - self._globalstep_last_logged), 4)
            if grad_norm is not None: logs["grad_norm"] = grad_norm.detach().item() if isinstance(grad_norm, torch.Tensor) else grad_norm
            logs["learning_rate"] = self._get_learning_rate()
            self._total_loss_scalar += tr_loss_scalar
            self._globalstep_last_logged = self.state.global_step
            self.store_flos()
            self.log(logs)
        metrics = None
        if self.control.should_evaluate: metrics = self._evaluate(trial, ignore_keys_for_eval)
        if self.control.should_save:
            self._save_checkpoint(model, trial, metrics=metrics)
            self.control = self.callback_handler.on_save(self.args, self.state, self.control)
    def _load_rng_state(self, checkpoint):
        if checkpoint is None: return
        if self.args.world_size > 1:
            process_index = self.args.process_index
            rng_file = os.path.join(checkpoint, f"rng_state_{process_index}.pth")
            if not os.path.isfile(rng_file):
                logger.info(f"Didn't find an RNG file for process {process_index}, if you are resuming a training that wasn't launched in a distributed fashion, reproducibility is not guaranteed.")
                return
        else:
            rng_file = os.path.join(checkpoint, "rng_state.pth")
            if not os.path.isfile(rng_file):
                logger.info("Didn't find an RNG file, if you are resuming a training that was launched in a distributed fashion, reproducibility is not guaranteed.")
                return
        checkpoint_rng_state = torch.load(rng_file)
        random.setstate(checkpoint_rng_state["python"])
        np.random.set_state(checkpoint_rng_state["numpy"])
        torch.random.set_rng_state(checkpoint_rng_state["cpu"])
        if torch.cuda.is_available():
            if self.args.parallel_mode == ParallelMode.DISTRIBUTED: torch.cuda.random.set_rng_state_all(checkpoint_rng_state["cuda"])
            else:
                try: torch.cuda.random.set_rng_state(checkpoint_rng_state["cuda"])
                except Exception as e: logger.info(f"Didn't manage to set back the RNG states of the GPU because of the following error:\n {e}\nThis won't yield the same results as if the training had not been interrupted.")
        if is_torch_xla_available(): xm.set_rng_state(checkpoint_rng_state["xla"])
        if is_torch_npu_available():
            if self.args.parallel_mode == ParallelMode.DISTRIBUTED: torch.npu.random.set_rng_state_all(checkpoint_rng_state["npu"])
            else:
                try: torch.npu.random.set_rng_state(checkpoint_rng_state["npu"])
                except Exception as e: logger.info(f"Didn't manage to set back the RNG states of the NPU because of the following error:\n {e}\nThis won't yield the same results as if the training had not been interrupted.")
        if is_torch_mlu_available():
            if self.args.parallel_mode == ParallelMode.DISTRIBUTED: torch.mlu.random.set_rng_state_all(checkpoint_rng_state["mlu"])
            else:
                try: torch.mlu.random.set_rng_state(checkpoint_rng_state["mlu"])
                except Exception as e: logger.info(f"Didn't manage to set back the RNG states of the MLU because of the following error:\n {e}\nThis won't yield the same results as if the training had not been interrupted.")
        if is_torch_musa_available():
            if self.args.parallel_mode == ParallelMode.DISTRIBUTED: torch.musa.set_rng_state_all(checkpoint_rng_state["musa"])
            else:
                try: torch.musa.set_rng_state(checkpoint_rng_state["musa"])
                except Exception as e: logger.info(f"Didn't manage to set back the RNG states of the MUSA because of the following error:\n {e}\nThis won't yield the same results as if the training had not been interrupted.")
    def _save_checkpoint(self, model, trial, metrics=None):
        checkpoint_folder = f"{PREFIX_CHECKPOINT_DIR}-{self.state.global_step}"
        if self.hp_search_backend is None and trial is None: self.store_flos()
        run_dir = self._get_output_dir(trial=trial)
        output_dir = os.path.join(run_dir, checkpoint_folder)
        self.save_model(output_dir, _internal_call=True)
        if not self.args.save_only_model:
            self._save_optimizer_and_scheduler(output_dir)
            self._save_rng_state(output_dir)
        if metrics is not None and self.args.metric_for_best_model is not None:
            metric_to_check = self.args.metric_for_best_model
            if not metric_to_check.startswith("eval_"): metric_to_check = f"eval_{metric_to_check}"
            try: metric_value = metrics[metric_to_check]
            except KeyError as exc: raise KeyError(f"The `metric_for_best_model` training argument is set to '{metric_to_check}', which is not found in the evaluation metrics. The available evaluation metrics are: {list(metrics.keys())}. Consider changing the `metric_for_best_model` via the TrainingArguments.") from exc
            operator = np.greater if self.args.greater_is_better else np.less
            if (self.state.best_metric is None or self.state.best_model_checkpoint is None or operator(metric_value, self.state.best_metric)):
                self.state.best_metric = metric_value
                self.state.best_model_checkpoint = output_dir
        if self.args.should_save:
            for cb in [cb for cb in self.callback_handler.callbacks + [self.control] if isinstance(cb, ExportableState)]:
                cb_name = cb.__class__.__name__
                cb_state = cb.state()
                if isinstance(self.state.stateful_callbacks[cb_name], list): self.state.stateful_callbacks[cb_name].append(cb_state)
                else: self.state.stateful_callbacks[cb_name] = cb_state
            self.state.save_to_json(os.path.join(output_dir, TRAINER_STATE_NAME))
        if self.args.push_to_hub: self._push_from_checkpoint(output_dir)
        if self.args.should_save: self._rotate_checkpoints(use_mtime=False, output_dir=run_dir)
    def _save_rng_state(self, output_dir):
        rng_states = {"python": random.getstate(), "numpy": np.random.get_state(), "cpu": torch.random.get_rng_state()}
        if torch.cuda.is_available():
            if self.args.parallel_mode == ParallelMode.DISTRIBUTED: rng_states["cuda"] = torch.cuda.random.get_rng_state_all()
            else: rng_states["cuda"] = torch.cuda.random.get_rng_state()
        if is_torch_xla_available(): rng_states["xla"] = xm.get_rng_state()
        if is_torch_npu_available():
            if self.args.parallel_mode == ParallelMode.DISTRIBUTED: rng_states["npu"] = torch.npu.random.get_rng_state_all()
            else: rng_states["npu"] = torch.npu.random.get_rng_state()
        if is_torch_mlu_available():
            if self.args.parallel_mode == ParallelMode.DISTRIBUTED: rng_states["mlu"] = torch.mlu.random.get_rng_state_all()
            else: rng_states["mlu"] = torch.mlu.random.get_rng_state()
        if is_torch_musa_available():
            if self.args.parallel_mode == ParallelMode.DISTRIBUTED: rng_states["musa"] = torch.musa.get_rng_state_all()
            else: rng_states["musa"] = torch.musa.get_rng_state()
        os.makedirs(output_dir, exist_ok=True)
        if self.args.world_size <= 1: torch.save(rng_states, os.path.join(output_dir, "rng_state.pth"))
        else: torch.save(rng_states, os.path.join(output_dir, f"rng_state_{self.args.process_index}.pth"))
    def _save_optimizer_and_scheduler(self, output_dir):
        if is_torch_xla_available():
            xm.rendezvous("saving_optimizer_states")
            if self.is_fsdp_xla_v1_enabled:
                optm = {"optimizer": self.optimizer.state_dict(), "shard_metadata": self.model.get_shard_metadata()}
                xm.save(optm, os.path.join(output_dir, f"rank{self.args.process_index}-of-{self.args.world_size}-{OPTIMIZER_NAME}"), master_only=False)
            else: xm.save(self.optimizer.state_dict(), os.path.join(output_dir, OPTIMIZER_NAME))
            with warnings.catch_warnings(record=True) as caught_warnings:
                xm.save(self.lr_scheduler.state_dict(), os.path.join(output_dir, SCHEDULER_NAME))
                reissue_pt_warnings(caught_warnings)
        elif is_sagemaker_mp_enabled():
            opt_state_dict = self.optimizer.local_state_dict(gather_if_shard=False)
            smp.barrier()
            if smp.rdp_rank() == 0 or smp.state.cfg.shard_optimizer_state: smp.save(opt_state_dict, os.path.join(output_dir, OPTIMIZER_NAME), partial=True, v3=smp.state.cfg.shard_optimizer_state)
        elif self.is_deepspeed_enabled:
            accept_exclude_frozen_parameters = "exclude_frozen_parameters" in set(inspect.signature(self.model_wrapped.save_checkpoint).parameters.keys())
            if accept_exclude_frozen_parameters and _is_peft_model(self.model): self.model_wrapped.save_checkpoint(output_dir, exclude_frozen_parameters=True)
            else: self.model_wrapped.save_checkpoint(output_dir)
        elif self.is_fsdp_enabled:
            save_fsdp_model(self.accelerator.state.fsdp_plugin, self.accelerator, self.model, output_dir, **_get_fsdp_ckpt_kwargs())
            save_fsdp_optimizer(self.accelerator.state.fsdp_plugin, self.accelerator, self.optimizer, self.model, output_dir)
        elif self.args.should_save: torch.save(self.optimizer.state_dict(), os.path.join(output_dir, OPTIMIZER_NAME))
        is_deepspeed_custom_scheduler = self.is_deepspeed_enabled and not isinstance(self.lr_scheduler, DeepSpeedSchedulerWrapper)
        if (self.args.should_save and (not self.is_deepspeed_enabled or is_deepspeed_custom_scheduler) and not is_torch_xla_available()):
            with warnings.catch_warnings(record=True) as caught_warnings: torch.save(self.lr_scheduler.state_dict(), os.path.join(output_dir, SCHEDULER_NAME))
            reissue_pt_warnings(caught_warnings)
    def _load_optimizer_and_scheduler(self, checkpoint):
        if checkpoint is None: return
        if self.is_deepspeed_enabled:
            if not isinstance(self.lr_scheduler, DeepSpeedSchedulerWrapper):
                with warnings.catch_warnings(record=True) as caught_warnings: self.lr_scheduler.load_state_dict(torch.load(os.path.join(checkpoint, SCHEDULER_NAME)))
                reissue_pt_warnings(caught_warnings)
            return
        checkpoint_file_exists = (glob.glob(os.path.join(checkpoint, OPTIMIZER_NAME) + "_*") if is_sagemaker_mp_enabled() else (os.path.isfile(os.path.join(checkpoint, OPTIMIZER_NAME)) or os.path.isfile(os.path.join(checkpoint, OPTIMIZER_NAME_BIN)) or (os.path.isdir(checkpoint) and any(OPTIMIZER_NAME_BIN.split(".")[0] in folder_name for folder_name in os.listdir(checkpoint) if os.path.isdir(os.path.join(checkpoint, folder_name))))))
        checkpoint_file_exists = (glob.glob(os.path.join(checkpoint, f"rank*-of-{self.args.world_size}-{OPTIMIZER_NAME}")) if self.is_fsdp_xla_v1_enabled else checkpoint_file_exists)
        if checkpoint_file_exists and os.path.isfile(os.path.join(checkpoint, SCHEDULER_NAME)):
            if is_torch_xla_available():
                if self.is_fsdp_xla_v1_enabled:
                    optimizer_state = torch.load(os.path.join(checkpoint, f"rank{self.args.process_index}-of-{self.args.world_size}-{OPTIMIZER_NAME}"), map_location="cpu")
                    optimizer_state = optimizer_state["optimizer"]
                else: optimizer_state = torch.load(os.path.join(checkpoint, OPTIMIZER_NAME), map_location="cpu")
                with warnings.catch_warnings(record=True) as caught_warnings: lr_scheduler_state = torch.load(os.path.join(checkpoint, SCHEDULER_NAME), map_location="cpu")
                reissue_pt_warnings(caught_warnings)
                xm.send_cpu_data_to_device(optimizer_state, self.args.device)
                xm.send_cpu_data_to_device(lr_scheduler_state, self.args.device)
                self.optimizer.load_state_dict(optimizer_state)
                self.lr_scheduler.load_state_dict(lr_scheduler_state)
            else:
                if is_sagemaker_mp_enabled():
                    if os.path.isfile(os.path.join(checkpoint, "user_content.pt")):
                        def opt_load_hook(mod, opt): opt.load_state_dict(smp.load(os.path.join(checkpoint, OPTIMIZER_NAME), partial=True))
                    else:
                        def opt_load_hook(mod, opt):
                            if IS_SAGEMAKER_MP_POST_1_10: opt.load_state_dict(smp.load(os.path.join(checkpoint, OPTIMIZER_NAME), partial=True, back_compat=True))
                            else: opt.load_state_dict(smp.load(os.path.join(checkpoint, OPTIMIZER_NAME), partial=True))
                    self.model_wrapped.register_post_step_hook(opt_load_hook)
                else:
                    map_location = self.args.device if self.args.world_size > 1 else "cpu"
                    if self.is_fsdp_enabled: load_fsdp_optimizer(self.accelerator.state.fsdp_plugin, self.accelerator, self.optimizer, self.model, checkpoint, **_get_fsdp_ckpt_kwargs())
                    else: self.optimizer.load_state_dict(torch.load(os.path.join(checkpoint, OPTIMIZER_NAME), map_location=map_location))
                with warnings.catch_warnings(record=True) as caught_warnings: self.lr_scheduler.load_state_dict(torch.load(os.path.join(checkpoint, SCHEDULER_NAME)))
                reissue_pt_warnings(caught_warnings)
    def _load_callback_state(self):
        if not self.args.restore_callback_states_from_checkpoint: return
        not_found = []
        new_callbacks = []
        original_callbacks = self.callback_handler.callbacks + [self.control]
        for stored_callback, data in self.state.stateful_callbacks.items():
            if not isinstance(data, list): data = [data]
            if any(callback.__class__.__name__ == stored_callback for callback in original_callbacks):
                duplicates = [callback for callback in original_callbacks if callback.__class__.__name__ == stored_callback]
                for callback, callback_data in zip(duplicates, data):
                    args = callback_data.get("args", {})
                    attributes = callback_data.get("attributes", {})
                    new_callback = type(callback)(**args)
                    for attribute, value in attributes.items(): setattr(new_callback, attribute, value)
                    if isinstance(callback, TrainerControl): self.control = new_callback
                    else: new_callbacks.append(new_callback)
                    self.callback_handler.remove_callback(type(new_callback))
                logger.info("Continuing training from checkpoint, restoring any callbacks that were passed in")
            else: not_found.append(stored_callback)
        if len(not_found) > 0: logger.warning(f"Checkpoint included callbacks not included in current configuration. Ignoring. ({', '.join(not_found)})")
        for callback in new_callbacks: self.callback_handler.add_callback(callback)
    def hyperparameter_search(self, hp_space: Optional[Callable[["optuna.Trial"], Dict[str, float]]] = None, compute_objective: Optional[Callable[[Dict[str, float]], float]] = None,
    n_trials: int = 20, direction: Union[str, List[str]] = "minimize", backend: Optional[Union["str", HPSearchBackend]] = None, hp_name: Optional[Callable[["optuna.Trial"], str]] = None, **kwargs) -> Union[BestRun, List[BestRun]]:
        if backend is None: backend = default_hp_search_backend()
        backend = HPSearchBackend(backend)
        backend_obj = ALL_HYPERPARAMETER_SEARCH_BACKENDS[backend]()
        backend_obj.ensure_available()
        self.hp_search_backend = backend
        if self.model_init is None: raise RuntimeError("To use hyperparameter search, you need to pass your model through a model_init function.")
        self.hp_space = backend_obj.default_hp_space if hp_space is None else hp_space
        self.hp_name = hp_name
        self.compute_objective = default_compute_objective if compute_objective is None else compute_objective
        best_run = backend_obj.run(self, n_trials, direction, **kwargs)
        self.hp_search_backend = None
        return best_run
    def log(self, logs: Dict[str, float]) -> None:
        if self.state.epoch is not None: logs["epoch"] = self.state.epoch
        if self.args.include_num_input_tokens_seen: logs["num_input_tokens_seen"] = self.state.num_input_tokens_seen
        output = {**logs, **{"step": self.state.global_step}}
        self.state.log_history.append(output)
        self.control = self.callback_handler.on_log(self.args, self.state, self.control, logs)
    def _prepare_input(self, data: Union[torch.Tensor, Any]) -> Union[torch.Tensor, Any]:
        if isinstance(data, Mapping): return type(data)({k: self._prepare_input(v) for k, v in data.items()})
        elif isinstance(data, (tuple, list)): return type(data)(self._prepare_input(v) for v in data)
        elif isinstance(data, torch.Tensor):
            kwargs = {"device": self.args.device}
            if self.is_deepspeed_enabled and (torch.is_floating_point(data) or torch.is_complex(data)): kwargs.update({"dtype": self.accelerator.state.deepspeed_plugin.hf_ds_config.dtype()})
            return data.to(**kwargs)
        return data
    def _prepare_inputs(self, inputs: Dict[str, Union[torch.Tensor, Any]]) -> Dict[str, Union[torch.Tensor, Any]]:
        inputs = self._prepare_input(inputs)
        if len(inputs) == 0: raise ValueError(f"The batch received was empty, your model won't be able to train on it. Double-check that your training dataset contains keys expected by the model: {','.join(self._signature_columns)}.")
        if self.args.past_index >= 0 and self._past is not None: inputs["mems"] = self._past
        return inputs
    def compute_loss_context_manager(self): return self.autocast_smart_context_manager()
    def autocast_smart_context_manager(self, cache_enabled: Optional[bool] = True):
        if self.use_cpu_amp: ctx_manager = torch.cpu.amp.autocast(cache_enabled=cache_enabled, dtype=self.amp_dtype)
        else: ctx_manager = contextlib.nullcontext()
        return ctx_manager
    def training_step(self, model: nn.Module, inputs: Dict[str, Union[torch.Tensor, Any]]) -> torch.Tensor:
        model.train()
        if hasattr(self.optimizer, "train") and callable(self.optimizer.train): self.optimizer.train()
        inputs = self._prepare_inputs(inputs)
        if is_sagemaker_mp_enabled():
            loss_mb = smp_forward_backward(model, inputs, self.args.gradient_accumulation_steps)
            return loss_mb.reduce_mean().detach().to(self.args.device)
        with self.compute_loss_context_manager(): loss = self.compute_loss(model, inputs)
        del inputs
        if (self.args.torch_empty_cache_steps is not None and self.state.global_step % self.args.torch_empty_cache_steps == 0):
            if is_torch_xpu_available(): torch.xpu.empty_cache()
            elif is_torch_mlu_available(): torch.mlu.empty_cache()
            elif is_torch_musa_available(): torch.musa.empty_cache()
            elif is_torch_npu_available(): torch.npu.empty_cache()
            elif is_torch_mps_available(min_version="2.0"): torch.mps.empty_cache()
            else: torch.cuda.empty_cache()
        kwargs = {}
        if self.args.optim in [OptimizerNames.LOMO, OptimizerNames.ADALOMO]: kwargs["learning_rate"] = self._get_learning_rate()
        if self.args.n_gpu > 1: loss = loss.mean()
        if self.use_apex:
            with amp.scale_loss(loss, self.optimizer) as scaled_loss: scaled_loss.backward()
        else: self.accelerator.backward(loss, **kwargs)
        return loss.detach() / self.args.gradient_accumulation_steps
    def compute_loss(self, model, inputs, return_outputs=False):
        if self.label_smoother is not None and "labels" in inputs: labels = inputs.pop("labels")
        else: labels = None
        outputs = model(**inputs)
        if self.args.past_index >= 0: self._past = outputs[self.args.past_index]
        if labels is not None:
            unwrapped_model = self.accelerator.unwrap_model(model)
            if _is_peft_model(unwrapped_model): model_name = unwrapped_model.base_model.model._get_name()
            else: model_name = unwrapped_model._get_name()
            if model_name in MODEL_FOR_CAUSAL_LM_MAPPING_NAMES.values(): loss = self.label_smoother(outputs, labels, shift_labels=True)
            else: loss = self.label_smoother(outputs, labels)
        else:
            if isinstance(outputs, dict) and "loss" not in outputs: raise ValueError(f"The model did not return a loss from the inputs, only the following keys: {','.join(outputs.keys())}. For reference, the inputs it received are {','.join(inputs.keys())}.")
            loss = outputs["loss"] if isinstance(outputs, dict) else outputs[0]
        return (loss, outputs) if return_outputs else loss
    def is_local_process_zero(self) -> bool: return self.args.local_process_index == 0
    def is_world_process_zero(self) -> bool:
        if is_sagemaker_mp_enabled(): return smp.rank() == 0
        else: return self.args.process_index == 0
    def save_model(self, output_dir: Optional[str] = None, _internal_call: bool = False):
        if output_dir is None: output_dir = self.args.output_dir
        if is_torch_xla_available(): self._save_tpu(output_dir)
        elif is_sagemaker_mp_enabled():
            os.makedirs(output_dir, exist_ok=True)
            state_dict = self.model_wrapped.state_dict()
            if self.args.should_save: self._save(output_dir, state_dict=state_dict)
            if IS_SAGEMAKER_MP_POST_1_10: Path(os.path.join(output_dir, "user_content.pt")).touch()
        elif self.is_fsdp_enabled:
            if ("FULL_STATE_DICT" in str(self.accelerator.state.fsdp_plugin.state_dict_type)) and (version.parse(sapiens_accelerator_version) > version.parse("0.24.1")):
                state_dict = self.accelerator.get_state_dict(self.model)
                if self.args.should_save: self._save(output_dir, state_dict=state_dict)
        elif self.is_deepspeed_enabled:
            try:
                state_dict = self.accelerator.get_state_dict(self.deepspeed)
                if self.args.should_save: self._save(output_dir, state_dict=state_dict)
            except ValueError:
                logger.warning(" stage3_gather_16bit_weights_on_model_save=false. Saving the full checkpoint instead, use zero_to_fp32.py to recover weights")
                if self.args.should_save: self._save(output_dir, state_dict={})
                remove_dummy_checkpoint(self.args.should_save, output_dir, [WEIGHTS_NAME, SAFE_WEIGHTS_NAME])
                self.model_wrapped.save_checkpoint(output_dir)
        elif self.args.should_save: self._save(output_dir)
        if self.args.push_to_hub and not _internal_call: self.push_to_hub(commit_message="Model save")
    def _save_tpu(self, output_dir: Optional[str] = None):
        output_dir = output_dir if output_dir is not None else self.args.output_dir
        logger.info(f"Saving model checkpoint to {output_dir}")
        model = self.model
        xm.mark_step()
        if xm.is_master_ordinal(local=False):
            os.makedirs(output_dir, exist_ok=True)
            torch.save(self.args, os.path.join(output_dir, TRAINING_ARGS_NAME))
        supported_classes = (PushToHubMixin,)
        xm.rendezvous("saving_checkpoint")
        if self.is_fsdp_xla_v1_enabled:
            ckpt = {"model": model.state_dict(), "shard_metadata": model.get_shard_metadata()}
            ckpt_path = os.path.join(output_dir, f"rank{self.args.process_index}-of-{self.args.world_size}-{WEIGHTS_NAME}")
            xm.save(ckpt, ckpt_path, master_only=False)
            xm.rendezvous("save_full_checkpoints")
            if self.args.should_save:
                from torch_xla.distributed.fsdp import consolidate_sharded_model_checkpoints
                full_state_dict, _ = consolidate_sharded_model_checkpoints(ckpt_prefix=os.path.join(output_dir, ""), ckpt_suffix=f"rank*-of-*-{WEIGHTS_NAME}", save_model=False)
                model = model.module.module
                unwrapped_model = self.accelerator.unwrap_model(model)
                if isinstance(unwrapped_model, supported_classes): unwrapped_model.save_pretrained(output_dir, state_dict=full_state_dict, save_function=xm.save, safe_serialization=self.args.save_safetensors)
                else:
                    logger.info("Trainer.model is not a `PreTrainedModel`, only saving its state dict.")
                    xm.save(full_state_dict, os.path.join(output_dir, WEIGHTS_NAME))
        elif not isinstance(model, supported_classes):
            if isinstance(self.accelerator.unwrap_model(model), supported_classes): self.accelerator.unwrap_model(model).save_pretrained(output_dir, is_main_process=self.args.should_save, state_dict=xm._maybe_convert_to_cpu(model.state_dict()), save_function=xm.save, safe_serialization=self.args.save_safetensors)
            else:
                logger.info("Trainer.model is not a `PreTrainedModel`, only saving its state dict.")
                state_dict = xm._maybe_convert_to_cpu(model.state_dict())
                xm.save(state_dict, os.path.join(output_dir, WEIGHTS_NAME))
        else: model.save_pretrained(output_dir, is_main_process=self.args.should_save, save_function=xm.save, safe_serialization=self.args.save_safetensors, state_dict=xm._maybe_convert_to_cpu(model.state_dict()))
        if self.tokenizer is not None and self.args.should_save: self.tokenizer.save_pretrained(output_dir)
    def _save(self, output_dir: Optional[str] = None, state_dict=None):
        output_dir = output_dir if output_dir is not None else self.args.output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Saving model checkpoint to {output_dir}")
        supported_classes = (PreTrainedModel,) if not is_peft_available() else (PreTrainedModel, PeftModel)
        if not isinstance(self.model, supported_classes):
            if state_dict is None: state_dict = self.model.state_dict()
            if isinstance(self.accelerator.unwrap_model(self.model), supported_classes): self.accelerator.unwrap_model(self.model).save_pretrained(output_dir, state_dict=state_dict, safe_serialization=self.args.save_safetensors)
            else:
                logger.info("Trainer.model is not a `PreTrainedModel`, only saving its state dict.")
                if self.args.save_safetensors: safetensors.torch.save_file(state_dict, os.path.join(output_dir, SAFE_WEIGHTS_NAME), metadata={"format": "pt"})
                else: torch.save(state_dict, os.path.join(output_dir, WEIGHTS_NAME))
        else: self.model.save_pretrained(output_dir, state_dict=state_dict, safe_serialization=self.args.save_safetensors)
        if self.tokenizer is not None: self.tokenizer.save_pretrained(output_dir)
        torch.save(self.args, os.path.join(output_dir, TRAINING_ARGS_NAME))
    def store_flos(self):
        if self.args.parallel_mode == ParallelMode.DISTRIBUTED:
            self.state.total_flos += (distributed_broadcast_scalars([self.current_flos], device=self.args.device).sum().item())
            self.current_flos = 0
        else:
            self.state.total_flos += self.current_flos
            self.current_flos = 0
    def _sorted_checkpoints(self, output_dir=None, checkpoint_prefix=PREFIX_CHECKPOINT_DIR, use_mtime=False) -> List[str]:
        ordering_and_checkpoint_path = []
        glob_checkpoints = [str(x) for x in Path(output_dir).glob(f"{checkpoint_prefix}-*") if os.path.isdir(x)]
        for path in glob_checkpoints:
            if use_mtime: ordering_and_checkpoint_path.append((os.path.getmtime(path), path))
            else:
                regex_match = re.match(f".*{checkpoint_prefix}-([0-9]+)", path)
                if regex_match is not None and regex_match.groups() is not None: ordering_and_checkpoint_path.append((int(regex_match.groups()[0]), path))
        checkpoints_sorted = sorted(ordering_and_checkpoint_path)
        checkpoints_sorted = [checkpoint[1] for checkpoint in checkpoints_sorted]
        if (self.state.best_model_checkpoint is not None and str(Path(self.state.best_model_checkpoint)) in checkpoints_sorted):
            best_model_index = checkpoints_sorted.index(str(Path(self.state.best_model_checkpoint)))
            for i in range(best_model_index, len(checkpoints_sorted) - 2): checkpoints_sorted[i], checkpoints_sorted[i + 1] = checkpoints_sorted[i + 1], checkpoints_sorted[i]
        return checkpoints_sorted
    def _rotate_checkpoints(self, use_mtime=False, output_dir=None) -> None:
        if self.args.save_total_limit is None or self.args.save_total_limit <= 0: return
        checkpoints_sorted = self._sorted_checkpoints(use_mtime=use_mtime, output_dir=output_dir)
        if len(checkpoints_sorted) <= self.args.save_total_limit: return
        save_total_limit = self.args.save_total_limit
        if (self.state.best_model_checkpoint is not None and self.args.save_total_limit == 1 and checkpoints_sorted[-1] != self.state.best_model_checkpoint): save_total_limit = 2
        number_of_checkpoints_to_delete = max(0, len(checkpoints_sorted) - save_total_limit)
        checkpoints_to_be_deleted = checkpoints_sorted[:number_of_checkpoints_to_delete]
        for checkpoint in checkpoints_to_be_deleted:
            logger.info(f"Deleting older checkpoint [{checkpoint}] due to args.save_total_limit")
            shutil.rmtree(checkpoint, ignore_errors=True)
    def evaluate(self, eval_dataset: Optional[Union[Dataset, Dict[str, Dataset]]] = None, ignore_keys: Optional[List[str]] = None, metric_key_prefix: str = "eval") -> Dict[str, float]:
        override = eval_dataset is not None
        eval_dataset = eval_dataset if override else self.eval_dataset
        if isinstance(eval_dataset, dict):
            metrics = {}
            for eval_dataset_name, _eval_dataset in eval_dataset.items():
                dataset_metrics = self.evaluate(eval_dataset=_eval_dataset if override else eval_dataset_name, ignore_keys=ignore_keys, metric_key_prefix=f"{metric_key_prefix}_{eval_dataset_name}")
                metrics.update(dataset_metrics)
            return metrics
        self._memory_tracker.start()
        eval_dataloader = self.get_eval_dataloader(eval_dataset)
        if self.is_fsdp_xla_v2_enabled: eval_dataloader = tpu_spmd_dataloader(eval_dataloader)
        start_time = time.time()
        eval_loop = self.prediction_loop if self.args.use_legacy_prediction_loop else self.evaluation_loop
        output = eval_loop(eval_dataloader, description="Evaluation", prediction_loss_only=True if self.compute_metrics is None else None, ignore_keys=ignore_keys, metric_key_prefix=metric_key_prefix)
        total_batch_size = self.args.eval_batch_size * self.args.world_size
        if f"{metric_key_prefix}_jit_compilation_time" in output.metrics: start_time += output.metrics[f"{metric_key_prefix}_jit_compilation_time"]
        if f"{metric_key_prefix}_model_preparation_time" in output.metrics: start_time += output.metrics[f"{metric_key_prefix}_model_preparation_time"]
        output.metrics.update(speed_metrics(metric_key_prefix, start_time, num_samples=output.num_samples, num_steps=math.ceil(output.num_samples / total_batch_size)))
        self.log(output.metrics)
        if DebugOption.TPU_METRICS_DEBUG in self.args.debug: xm.master_print(met.metrics_report())
        self.control = self.callback_handler.on_evaluate(self.args, self.state, self.control, output.metrics)
        self._memory_tracker.stop_and_update_metrics(output.metrics)
        return output.metrics
    def predict(self, test_dataset: Dataset, ignore_keys: Optional[List[str]] = None, metric_key_prefix: str = "test") -> PredictionOutput:
        self._memory_tracker.start()
        test_dataloader = self.get_test_dataloader(test_dataset)
        start_time = time.time()
        eval_loop = self.prediction_loop if self.args.use_legacy_prediction_loop else self.evaluation_loop
        output = eval_loop(test_dataloader, description="Prediction", ignore_keys=ignore_keys, metric_key_prefix=metric_key_prefix)
        total_batch_size = self.args.eval_batch_size * self.args.world_size
        if f"{metric_key_prefix}_jit_compilation_time" in output.metrics: start_time += output.metrics[f"{metric_key_prefix}_jit_compilation_time"]
        if f"{metric_key_prefix}_model_preparation_time" in output.metrics: start_time += output.metrics[f"{metric_key_prefix}_model_preparation_time"]
        output.metrics.update(speed_metrics(metric_key_prefix, start_time, num_samples=output.num_samples, num_steps=math.ceil(output.num_samples / total_batch_size)))
        self.control = self.callback_handler.on_predict(self.args, self.state, self.control, output.metrics)
        self._memory_tracker.stop_and_update_metrics(output.metrics)
        return PredictionOutput(predictions=output.predictions, label_ids=output.label_ids, metrics=output.metrics)
    def evaluation_loop(self, dataloader: DataLoader, description: str, prediction_loss_only: Optional[bool] = None, ignore_keys: Optional[List[str]] = None, metric_key_prefix: str = "eval") -> EvalLoopOutput:
        args = self.args
        prediction_loss_only = prediction_loss_only if prediction_loss_only is not None else args.prediction_loss_only
        if self.is_deepspeed_enabled and self.deepspeed is None: _, _ = deepspeed_init(self, num_training_steps=0, inference=True)
        model = self._wrap_model(self.model, training=False, dataloader=dataloader)
        if len(self.accelerator._models) == 0 and model is self.model:
            start_time = time.time()
            model = (self.accelerator.prepare(model) if self.is_deepspeed_enabled else self.accelerator.prepare_model(model, evaluation_mode=True))
            self.model_preparation_time = round(time.time() - start_time, 4)
            if self.is_fsdp_enabled: self.model = model
            if model is not self.model: self.model_wrapped = model
            if self.is_deepspeed_enabled: self.deepspeed = self.model_wrapped
        if not self.is_in_train:
            if args.fp16_full_eval: model = model.to(dtype=torch.float16, device=args.device)
            elif args.bf16_full_eval: model = model.to(dtype=torch.bfloat16, device=args.device)
        batch_size = self.args.eval_batch_size
        logger.info(f"\n***** Running {description} *****")
        if has_length(dataloader): logger.info(f"  Num examples = {self.num_examples(dataloader)}")
        else: logger.info("  Num examples: Unknown")
        logger.info(f"  Batch size = {batch_size}")
        model.eval()
        if hasattr(self.optimizer, "eval") and callable(self.optimizer.eval): self.optimizer.eval()
        self.callback_handler.eval_dataloader = dataloader
        eval_dataset = getattr(dataloader, "dataset", None)
        if args.past_index >= 0: self._past = None
        all_losses = EvalLoopContainer(self.args.eval_do_concat_batches, padding_index=-100)
        all_preds = EvalLoopContainer(self.args.eval_do_concat_batches, padding_index=-100)
        all_labels = EvalLoopContainer(self.args.eval_do_concat_batches, padding_index=-100)
        all_inputs = EvalLoopContainer(self.args.eval_do_concat_batches, padding_index=-100)
        metrics = None
        observed_num_examples = 0
        for step, inputs in enumerate(dataloader):
            observed_batch_size = find_batch_size(inputs)
            if observed_batch_size is not None:
                observed_num_examples += observed_batch_size
                if batch_size is None: batch_size = observed_batch_size
            losses, logits, labels = self.prediction_step(model, inputs, prediction_loss_only, ignore_keys=ignore_keys)
            main_input_name = getattr(self.model, "main_input_name", "input_ids")
            inputs_decode = self._prepare_input(inputs[main_input_name]) if args.include_inputs_for_metrics else None
            if is_torch_xla_available(): xm.mark_step()
            if losses is not None:
                losses = self.gather_function((losses.repeat(batch_size)))
                all_losses.add(losses)
            if inputs_decode is not None:
                inputs_decode = self.accelerator.pad_across_processes(inputs_decode, dim=1, pad_index=-100)
                inputs_decode = self.gather_function((inputs_decode))
                if not self.args.batch_eval_metrics or description == "Prediction": all_inputs.add(inputs_decode)
            if labels is not None: labels = self.accelerator.pad_across_processes(labels, dim=1, pad_index=-100)
            if logits is not None:
                logits = self.accelerator.pad_across_processes(logits, dim=1, pad_index=-100)
                if self.preprocess_logits_for_metrics is not None: logits = self.preprocess_logits_for_metrics(logits, labels)
                logits = self.gather_function((logits))
                if not self.args.batch_eval_metrics or description == "Prediction": all_preds.add(logits)
            if labels is not None:
                labels = self.gather_function((labels))
                if not self.args.batch_eval_metrics or description == "Prediction": all_labels.add(labels)
            self.control = self.callback_handler.on_prediction_step(args, self.state, self.control)
            if self.args.batch_eval_metrics:
                if self.compute_metrics is not None and logits is not None and labels is not None:
                    is_last_step = self.accelerator.gradient_state.end_of_dataloader
                    if args.include_inputs_for_metrics: metrics = self.compute_metrics(EvalPrediction(predictions=logits, label_ids=labels, inputs=inputs), compute_result=is_last_step)
                    else: metrics = self.compute_metrics(EvalPrediction(predictions=logits, label_ids=labels), compute_result=is_last_step)
                del losses, logits, labels, inputs
                torch.cuda.empty_cache()
            elif args.eval_accumulation_steps is not None and (step + 1) % args.eval_accumulation_steps == 0:
                all_losses.to_cpu_and_numpy()
                all_preds.to_cpu_and_numpy()
                all_labels.to_cpu_and_numpy()
                all_inputs.to_cpu_and_numpy()
                del losses, logits, labels, inputs
                torch.cuda.empty_cache()
        self.gather_function = self.accelerator.gather_for_metrics
        if args.past_index and hasattr(self, "_past"): delattr(self, "_past")
        all_losses = all_losses.get_arrays()
        all_preds = all_preds.get_arrays()
        all_labels = all_labels.get_arrays()
        all_inputs = all_inputs.get_arrays()
        if has_length(eval_dataset): num_samples = len(eval_dataset)
        elif isinstance(eval_dataset, IterableDatasetShard) and getattr(eval_dataset, "num_examples", 0) > 0: num_samples = eval_dataset.num_examples
        else:
            if has_length(dataloader): num_samples = self.num_examples(dataloader)
            else: num_samples = observed_num_examples
        if num_samples == 0 and observed_num_examples > 0: num_samples = observed_num_examples
        if (self.compute_metrics is not None and all_preds is not None and all_labels is not None and not self.args.batch_eval_metrics):
            if args.include_inputs_for_metrics: metrics = self.compute_metrics(EvalPrediction(predictions=all_preds, label_ids=all_labels, inputs=all_inputs))
            else: metrics = self.compute_metrics(EvalPrediction(predictions=all_preds, label_ids=all_labels))
        elif metrics is None: metrics = {}
        metrics = denumpify_detensorize(metrics)
        if isinstance(all_losses, list) and all_losses: metrics[f"{metric_key_prefix}_loss"] = np.concatenate(all_losses).mean().item()
        elif isinstance(all_losses, np.ndarray): metrics[f"{metric_key_prefix}_loss"] = all_losses.mean().item()
        if hasattr(self, "jit_compilation_time"): metrics[f"{metric_key_prefix}_jit_compilation_time"] = self.jit_compilation_time
        if hasattr(self, "model_preparation_time"): metrics[f"{metric_key_prefix}_model_preparation_time"] = self.model_preparation_time
        for key in list(metrics.keys()):
            if not key.startswith(f"{metric_key_prefix}_"): metrics[f"{metric_key_prefix}_{key}"] = metrics.pop(key)
        return EvalLoopOutput(predictions=all_preds, label_ids=all_labels, metrics=metrics, num_samples=num_samples)
    def _nested_gather(self, tensors, name=None):
        if tensors is None: return
        if is_torch_xla_available():
            if name is None: name = "nested_gather"
            tensors = nested_xla_mesh_reduce(tensors, name)
        elif is_sagemaker_mp_enabled(): tensors = smp_gather(tensors)
        elif (self.args.distributed_state is not None and self.args.distributed_state.distributed_type != "NO") or (self.args.distributed_state is None and self.args.local_rank != -1): tensors = distributed_concat(tensors)
        return tensors
    def prediction_step(self, model: nn.Module, inputs: Dict[str, Union[torch.Tensor, Any]], prediction_loss_only: bool, ignore_keys: Optional[List[str]] = None) -> Tuple[Optional[torch.Tensor], Optional[torch.Tensor], Optional[torch.Tensor]]:
        has_labels = False if len(self.label_names) == 0 else all(inputs.get(k) is not None for k in self.label_names)
        return_loss = inputs.get("return_loss", None)
        if return_loss is None: return_loss = self.can_return_loss
        loss_without_labels = True if len(self.label_names) == 0 and return_loss else False
        inputs = self._prepare_inputs(inputs)
        if ignore_keys is None:
            if hasattr(self.model, "config"): ignore_keys = getattr(self.model.config, "keys_to_ignore_at_inference", [])
            else: ignore_keys = []
        if has_labels or loss_without_labels:
            labels = nested_detach(tuple(inputs.get(name) for name in self.label_names))
            if len(labels) == 1: labels = labels[0]
        else: labels = None
        with torch.no_grad():
            if is_sagemaker_mp_enabled():
                raw_outputs = smp_forward_only(model, inputs)
                if has_labels or loss_without_labels:
                    if isinstance(raw_outputs, dict):
                        loss_mb = raw_outputs["loss"]
                        logits_mb = tuple(v for k, v in raw_outputs.items() if k not in ignore_keys + ["loss"])
                    else:
                        loss_mb = raw_outputs[0]
                        logits_mb = raw_outputs[1:]
                    loss = loss_mb.reduce_mean().detach().cpu()
                    logits = smp_nested_concat(logits_mb)
                else:
                    loss = None
                    if isinstance(raw_outputs, dict): logits_mb = tuple(v for k, v in raw_outputs.items() if k not in ignore_keys)
                    else: logits_mb = raw_outputs
                    logits = smp_nested_concat(logits_mb)
            else:
                if has_labels or loss_without_labels:
                    with self.compute_loss_context_manager(): loss, outputs = self.compute_loss(model, inputs, return_outputs=True)
                    loss = loss.mean().detach()
                    if isinstance(outputs, dict): logits = tuple(v for k, v in outputs.items() if k not in ignore_keys + ["loss"])
                    else: logits = outputs[1:]
                else:
                    loss = None
                    with self.compute_loss_context_manager(): outputs = model(**inputs)
                    if isinstance(outputs, dict): logits = tuple(v for k, v in outputs.items() if k not in ignore_keys)
                    else: logits = outputs
                    if self.args.past_index >= 0: self._past = outputs[self.args.past_index - 1]
        if prediction_loss_only: return (loss, None, None)
        logits = nested_detach(logits)
        if len(logits) == 1: logits = logits[0]
        return (loss, logits, labels)
    def floating_point_ops(self, inputs: Dict[str, Union[torch.Tensor, Any]]):
        if hasattr(self.model, "floating_point_ops"): return self.model.floating_point_ops(inputs)
        else: return 0
    def init_hf_repo(self, token: Optional[str] = None):
        if not self.is_world_process_zero(): return
        if self.args.hub_model_id is None: repo_name = Path(self.args.output_dir).absolute().name
        else: repo_name = self.args.hub_model_id
        token = token if token is not None else self.args.hub_token
        repo_url = create_repo(repo_name, token=token, private=self.args.hub_private_repo, exist_ok=True)
        self.hub_model_id = repo_url.repo_id
        self.push_in_progress = None
    def create_model_card(self, language: Optional[str] = None, license: Optional[str] = None, tags: Union[str, List[str], None] = None, model_name: Optional[str] = None,
    finetuned_from: Optional[str] = None, tasks: Union[str, List[str], None] = None, dataset_tags: Union[str, List[str], None] = None, dataset: Union[str, List[str], None] = None, dataset_args: Union[str, List[str], None] = None):
        if not self.is_world_process_zero(): return
        model_card_filepath = os.path.join(self.args.output_dir, "README.md")
        is_peft_library = False
        if os.path.exists(model_card_filepath):
            library_name = ModelCard.load(model_card_filepath).data.get("library_name")
            is_peft_library = library_name == "peft"
            existing_tags = ModelCard.load(model_card_filepath).data.tags
            if tags is not None and existing_tags is not None:
                if isinstance(tags, str): tags = [tags]
                for tag in existing_tags:
                    if tag not in tags: tags.append(tag)
        training_summary = TrainingSummary.from_trainer(self, language=language, license=license, tags=tags, model_name=model_name, finetuned_from=finetuned_from, tasks=tasks, dataset_tags=dataset_tags, dataset=dataset, dataset_args=dataset_args)
        model_card = training_summary.to_model_card()
        with open(model_card_filepath, "w") as f: f.write(model_card)
        if is_peft_library: self.accelerator.unwrap_model(self.model).create_or_update_model_card(self.args.output_dir)
    def _push_from_checkpoint(self, checkpoint_folder):
        if not self.is_world_process_zero() or self.args.hub_strategy == HubStrategy.END: return
        if not self.args.hub_always_push and self.push_in_progress is not None and not self.push_in_progress.is_done(): return
        output_dir = self.args.output_dir
        modeling_files = [CONFIG_NAME, WEIGHTS_NAME, SAFE_WEIGHTS_NAME]
        for index_file in [WEIGHTS_INDEX_NAME, SAFE_WEIGHTS_INDEX_NAME]:
            index_path = os.path.join(checkpoint_folder, index_file)
            if os.path.isfile(index_path):
                modeling_files.append(index_file)
                with open(index_path) as f: index = json.loads(f.read())
                shard_files = list(set(index["weight_map"].values()))
                modeling_files.extend(shard_files)
        if is_peft_available(): modeling_files.extend([ADAPTER_CONFIG_NAME, ADAPTER_WEIGHTS_NAME, ADAPTER_SAFE_WEIGHTS_NAME])
        for modeling_file in modeling_files:
            if os.path.isfile(os.path.join(checkpoint_folder, modeling_file)): shutil.copy(os.path.join(checkpoint_folder, modeling_file), os.path.join(output_dir, modeling_file))
        if self.tokenizer is not None: self.tokenizer.save_pretrained(output_dir)
        torch.save(self.args, os.path.join(output_dir, TRAINING_ARGS_NAME))
        if self.args.save_strategy == IntervalStrategy.STEPS: commit_message = f"Training in progress, step {self.state.global_step}"
        else: commit_message = f"Training in progress, epoch {int(self.state.epoch)}"
        model_push_job = upload_folder(repo_id=self.hub_model_id, folder_path=output_dir, commit_message=commit_message, token=self.args.hub_token, run_as_future=True, ignore_patterns=["_*", f"{PREFIX_CHECKPOINT_DIR}-*"])
        push_jobs = [model_push_job]
        if self.args.hub_strategy in [HubStrategy.CHECKPOINT, HubStrategy.ALL_CHECKPOINTS]:
            path_in_repo = ("last-checkpoint" if self.args.hub_strategy == HubStrategy.CHECKPOINT else Path(checkpoint_folder).name)
            checkpoint_push = upload_folder(repo_id=self.hub_model_id, folder_path=checkpoint_folder, path_in_repo=path_in_repo, commit_message=commit_message + ", checkpoint", token=self.args.hub_token, run_as_future=True)
            push_jobs.append(checkpoint_push)
        if self.push_in_progress is None or self.push_in_progress.is_done(): self.push_in_progress = PushInProgress(push_jobs)
        else: self.push_in_progress.jobs.extend(push_jobs)
    def _finish_current_push(self):
        if not hasattr(self, "push_in_progress"): return
        if self.push_in_progress is not None and not self.push_in_progress.is_done():
            logger.info("Waiting for the current checkpoint push to be finished, this might take a couple of minutes.")
            self.push_in_progress.wait_until_done()
    def push_to_hub(self, commit_message: Optional[str] = "End of training", blocking: bool = True, token: Optional[str] = None, revision: Optional[str] = None, **kwargs) -> str:
        model_name = kwargs.pop("model_name", None)
        if model_name is None and self.args.should_save:
            if self.args.hub_model_id is None: model_name = Path(self.args.output_dir).name
            else: model_name = self.args.hub_model_id.split("/")[-1]
        token = token if token is not None else self.args.hub_token
        if self.hub_model_id is None: self.init_hf_repo(token=token)
        self.save_model(_internal_call=True)
        if not self.is_world_process_zero(): return
        if getattr(self.model, "model_tags", None) is not None:
            if "tags" not in kwargs: kwargs["tags"] = []
            if isinstance(kwargs["tags"], str): kwargs["tags"] = [kwargs["tags"]]
            for model_tag in self.model.model_tags:
                if model_tag not in kwargs["tags"]: kwargs["tags"].append(model_tag)
        self.create_model_card(model_name=model_name, **kwargs)
        self._finish_current_push()
        return upload_folder(repo_id=self.hub_model_id, folder_path=self.args.output_dir, commit_message=commit_message, token=token, run_as_future=not blocking, ignore_patterns=["_*", f"{PREFIX_CHECKPOINT_DIR}-*"], revision=revision)
    def prediction_loop(self, dataloader: DataLoader, description: str, prediction_loss_only: Optional[bool] = None, ignore_keys: Optional[List[str]] = None, metric_key_prefix: str = "eval") -> EvalLoopOutput:
        args = self.args
        if not has_length(dataloader): raise ValueError("dataloader must implement a working __len__")
        prediction_loss_only = prediction_loss_only if prediction_loss_only is not None else args.prediction_loss_only
        if self.is_deepspeed_enabled and self.deepspeed is None: _, _ = deepspeed_init(self, num_training_steps=0, inference=True)
        model = self._wrap_model(self.model, training=False, dataloader=dataloader)
        if len(self.accelerator._models) == 0 and model is self.model:
            model = (self.accelerator.prepare(model) if self.is_deepspeed_enabled else self.accelerator.prepare_model(model, evaluation_mode=True))
            if self.is_fsdp_enabled: self.model = model
            if model is not self.model: self.model_wrapped = model
            if self.is_deepspeed_enabled: self.deepspeed = self.model_wrapped
        if not self.is_in_train:
            if args.fp16_full_eval: model = model.to(dtype=torch.float16, device=args.device)
            elif args.bf16_full_eval: model = model.to(dtype=torch.bfloat16, device=args.device)
        batch_size = dataloader.batch_size
        num_examples = self.num_examples(dataloader)
        logger.info(f"\n***** Running {description} *****")
        logger.info(f"  Num examples = {num_examples}")
        logger.info(f"  Batch size = {batch_size}")
        losses_host: torch.Tensor = None
        preds_host: Union[torch.Tensor, List[torch.Tensor]] = None
        labels_host: Union[torch.Tensor, List[torch.Tensor]] = None
        inputs_host: Union[torch.Tensor, List[torch.Tensor]] = None
        metrics: Optional[dict] = None
        world_size = max(1, args.world_size)
        eval_losses_gatherer = DistributedTensorGatherer(world_size, num_examples, make_multiple_of=batch_size)
        if not prediction_loss_only:
            make_multiple_of = None
            if hasattr(dataloader, "sampler") and isinstance(dataloader.sampler, SequentialDistributedSampler): make_multiple_of = dataloader.sampler.batch_size
            preds_gatherer = DistributedTensorGatherer(world_size, num_examples, make_multiple_of=make_multiple_of)
            labels_gatherer = DistributedTensorGatherer(world_size, num_examples, make_multiple_of=make_multiple_of)
            inputs_gatherer = DistributedTensorGatherer(world_size, num_examples, make_multiple_of=make_multiple_of)
        model.eval()
        if hasattr(self.optimizer, "eval") and callable(self.optimizer.eval): self.optimizer.eval()
        if args.past_index >= 0: self._past = None
        self.callback_handler.eval_dataloader = dataloader
        for step, inputs in enumerate(dataloader):
            loss, logits, labels = self.prediction_step(model, inputs, prediction_loss_only, ignore_keys=ignore_keys)
            main_input_name = getattr(self.model, "main_input_name", "input_ids")
            inputs_decode = self._prepare_input(inputs[main_input_name]) if args.include_inputs_for_metrics else None
            if loss is not None:
                losses = loss.repeat(batch_size)
                losses_host = losses if losses_host is None else torch.cat((losses_host, losses), dim=0)
            if logits is not None: preds_host = logits if preds_host is None else nested_concat(preds_host, logits, padding_index=-100)
            if labels is not None: labels_host = labels if labels_host is None else nested_concat(labels_host, labels, padding_index=-100)
            if inputs_decode is not None: inputs_host = (inputs_decode if inputs_host is None else nested_concat(inputs_host, inputs_decode, padding_index=-100))
            self.control = self.callback_handler.on_prediction_step(args, self.state, self.control)
            if self.args.batch_eval_metrics:
                if self.compute_metrics is not None and preds_host is not None and labels_host is not None:
                    is_last_step = self.accelerator.gradient_state.end_of_dataloader
                    if args.include_inputs_for_metrics: metrics = self.compute_metrics(EvalPrediction(predictions=preds_host, label_ids=labels_host, inputs=inputs_host), compute_result=is_last_step)
                    else: metrics = self.compute_metrics(EvalPrediction(predictions=preds_host, label_ids=labels_host), compute_result=is_last_step)
            if self.args.batch_eval_metrics or (args.eval_accumulation_steps is not None and (step + 1) % args.eval_accumulation_steps == 0):
                eval_losses_gatherer.add_arrays(self._gather_and_numpify(losses_host, "eval_losses"))
                if not prediction_loss_only:
                    preds_gatherer.add_arrays(self._gather_and_numpify(preds_host, "eval_preds"))
                    labels_gatherer.add_arrays(self._gather_and_numpify(labels_host, "eval_label_ids"))
                    inputs_gatherer.add_arrays(self._gather_and_numpify(inputs_host, "eval_inputs_ids"))
                del losses_host, preds_host, labels_host, inputs_host
                torch.cuda.empty_cache()
                losses_host, preds_host, labels_host, inputs_host = None, None, None, None
        if args.past_index and hasattr(self, "_past"): delattr(self, "_past")
        eval_losses_gatherer.add_arrays(self._gather_and_numpify(losses_host, "eval_losses"))
        if not prediction_loss_only:
            preds_gatherer.add_arrays(self._gather_and_numpify(preds_host, "eval_preds"))
            labels_gatherer.add_arrays(self._gather_and_numpify(labels_host, "eval_label_ids"))
            inputs_gatherer.add_arrays(self._gather_and_numpify(inputs_host, "eval_inputs_ids"))
        eval_loss = eval_losses_gatherer.finalize()
        preds = preds_gatherer.finalize() if not prediction_loss_only else None
        label_ids = labels_gatherer.finalize() if not prediction_loss_only else None
        inputs_ids = inputs_gatherer.finalize() if not prediction_loss_only else None
        if (self.compute_metrics is not None and preds is not None and label_ids is not None and not self.args.batch_eval_metrics):
            if args.include_inputs_for_metrics: metrics = self.compute_metrics(EvalPrediction(predictions=preds, label_ids=label_ids, inputs=inputs_ids))
            else: metrics = self.compute_metrics(EvalPrediction(predictions=preds, label_ids=label_ids))
        elif metrics is None: metrics = {}
        metrics = denumpify_detensorize(metrics)
        if eval_loss is not None: metrics[f"{metric_key_prefix}_loss"] = eval_loss.mean().item()
        for key in list(metrics.keys()):
            if not key.startswith(f"{metric_key_prefix}_"): metrics[f"{metric_key_prefix}_{key}"] = metrics.pop(key)
        return EvalLoopOutput(predictions=preds, label_ids=label_ids, metrics=metrics, num_samples=num_examples)
    def _gather_and_numpify(self, tensors, name):
        if tensors is None: return
        if is_torch_xla_available(): tensors = nested_xla_mesh_reduce(tensors, name)
        elif is_sagemaker_mp_enabled(): tensors = smp_gather(tensors)
        elif self.args.parallel_mode == ParallelMode.DISTRIBUTED: tensors = distributed_concat(tensors)
        return nested_numpify(tensors)
    def _add_sm_patterns_to_gitignore(self) -> None:
        if not self.is_world_process_zero(): return
        patterns = ["*.sagemaker-uploading", "*.sagemaker-uploaded"]
        if os.path.exists(os.path.join(self.repo.local_dir, ".gitignore")):
            with open(os.path.join(self.repo.local_dir, ".gitignore"), "r") as f: current_content = f.read()
        else: current_content = ""
        content = current_content
        for pattern in patterns:
            if pattern not in content:
                if content.endswith("\n"): content += pattern
                else: content += f"\n{pattern}"
        if content != current_content:
            with open(os.path.join(self.repo.local_dir, ".gitignore"), "w") as f:
                logger.debug(f"Writing .gitignore file. Content: {content}")
                f.write(content)
        self.repo.git_add(".gitignore")
        time.sleep(0.5)
        if not self.repo.is_repo_clean():
            self.repo.git_commit("Add *.sagemaker patterns to .gitignore.")
            self.repo.git_push()
    def create_accelerator_and_postprocess(self):
        grad_acc_kwargs = {}
        if is_sapiens_accelerator_available("0.28.0") and self.args.accelerator_config.gradient_accumulation_kwargs is not None: grad_acc_kwargs = self.args.accelerator_config.gradient_accumulation_kwargs
        if "num_steps" in grad_acc_kwargs and self.args.gradient_accumulation_steps > 1: raise ValueError("The `AcceleratorConfig`'s `num_steps` is set but `gradient_accumulation_steps` is greater than 1 in the passed `TrainingArguments`. If using the passed `AcceleratorConfig` is desired, do not set the `TrainingArguments` `gradient_accumulation_steps`.")
        elif "num_steps" not in grad_acc_kwargs: grad_acc_kwargs["num_steps"] = self.args.gradient_accumulation_steps
        grad_acc_kwargs["sync_with_dataloader"] = False
        gradient_accumulation_plugin = GradientAccumulationPlugin(**grad_acc_kwargs)
        accelerator_config = self.args.accelerator_config.to_dict()
        if is_sapiens_accelerator_available("0.28.0"): dataloader_config = DataLoaderConfiguration(split_batches=accelerator_config.pop("split_batches"), dispatch_batches=accelerator_config.pop("dispatch_batches"), even_batches=accelerator_config.pop("even_batches"), use_seedable_sampler=accelerator_config.pop("use_seedable_sampler"))
        non_blocking = accelerator_config.pop("non_blocking")
        if not is_sapiens_accelerator_available("0.30.0"):
            if non_blocking: raise ImportError("`non_blocking` is only supported in sapiens_accelerator v0.30.0 and above. Please upgrade sapiens_accelerator to use this feature.")
        else:
            if non_blocking and not self.args.dataloader_pin_memory: logger.warning("`non_blocking` is enabled but `dataloader_pin_memory` is not. For the best performance, it's recommended to enable both.")
            dataloader_config.non_blocking = non_blocking
        accelerator_config.pop("gradient_accumulation_kwargs")
        args = {"deepspeed_plugin": self.args.deepspeed_plugin, "gradient_accumulation_plugin": gradient_accumulation_plugin}
        if is_sapiens_accelerator_available("0.28.0"): args["dataloader_config"] = dataloader_config
        else: args.update(accelerator_config)
        self.accelerator = Accelerator(**args)
        self.gather_function = self.accelerator.gather_for_metrics
        if "use_gather_object" in inspect.signature(self.gather_function).parameters.keys(): self.gather_function = functools.partial(self.gather_function, use_gather_object=self.args.eval_use_gather_object)
        self.is_deepspeed_enabled = getattr(self.accelerator.state, "deepspeed_plugin", None) is not None
        self.is_fsdp_enabled = getattr(self.accelerator.state, "fsdp_plugin", None) is not None
        if self.is_fsdp_enabled:
            fsdp_plugin = self.accelerator.state.fsdp_plugin
            fsdp_plugin.limit_all_gathers = self.args.fsdp_config.get("limit_all_gathers", fsdp_plugin.limit_all_gathers)
            fsdp_plugin.activation_checkpointing = self.args.fsdp_config.get("activation_checkpointing", fsdp_plugin.activation_checkpointing)
            if fsdp_plugin.activation_checkpointing and self.args.gradient_checkpointing: raise ValueError("The activation_checkpointing in FSDP config and the gradient_checkpointing in training arg can't be set to True simultaneously. Please use FSDP's activation_checkpointing logic when using FSDP.")
        if self.is_deepspeed_enabled and getattr(self.args, "hf_deepspeed_config", None) is None: self.propagate_args_to_deepspeed()
        if (self.args.save_only_model and (self.is_deepspeed_enabled or self.is_fsdp_enabled) and self.args.load_best_model_at_end):
            wrapper = "DeepSpeed" if self.is_deepspeed_enabled else "FSDP"
            raise ValueError(f"{wrapper} can't be used with `save_only_model` along with `load_best_model_at_end`.")
        if (self.is_deepspeed_enabled and self.accelerator.state.deepspeed_plugin.zero_stage == 3 and self.args.auto_find_batch_size): raise ValueError("`auto_find_batch_size` isn't supported yet with DeepSpeed Zero-3. Please consider using Zero-2, Zero-1, or FSDP")
    def propagate_args_to_deepspeed(self, auto_find_batch_size=False):
        from sapiens_transformers.integrations.deepspeed import HfTrainerDeepSpeedConfig
        ds_plugin = self.accelerator.state.deepspeed_plugin
        ds_plugin.hf_ds_config = HfTrainerDeepSpeedConfig(ds_plugin.hf_ds_config.config)
        ds_plugin.deepspeed_config = ds_plugin.hf_ds_config.config
        ds_plugin.hf_ds_config.trainer_config_process(self.args, auto_find_batch_size)
    def _fsdp_qlora_plugin_updates(self):
        if self.is_fsdp_enabled and _is_peft_model(self.model):
            from peft import LoraConfig
            from peft.utils.other import fsdp_auto_wrap_policy
            if isinstance(self.model.active_peft_config, LoraConfig):
                fsdp_plugin = self.accelerator.state.fsdp_plugin
                fsdp_plugin.auto_wrap_policy = fsdp_auto_wrap_policy(self.model)
            if (getattr(self.model, "quantization_method", None) == QuantizationMethod.SAPIENS_MACHINE and self.model.hf_quantizer.quantization_config.sapiens_4bit_quant_storage.is_floating_point and version.parse(sapiens_accelerator_version) > version.parse("0.27.0")): fsdp_plugin.set_mixed_precision(self.model.hf_quantizer.quantization_config.sapiens_4bit_quant_storage, override=True)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
