'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import Callable, Dict, List, Optional, Tuple, Union
import torch
import torch.nn as nn
from ..models.attention import BasicTransformerBlock, FreeNoiseTransformerBlock
from ..models.resnet import Downsample2D, ResnetBlock2D, Upsample2D
from ..models.sapiens_transformers.transformer_2d import Transformer2DModel
from ..models.unets.unet_motion_model import AnimateDiffTransformer3D, CrossAttnDownBlockMotion, DownBlockMotion, SAPIVideoGenTransformer3D, UpBlockMotion
from ..pipelines.pipeline_utils import DiffusionPipeline
from ..utils.torch_utils import randn_tensor
class SplitInferenceModule(nn.Module):
    """Args:"""
    def __init__(self, module: nn.Module, split_size: int=1, split_dim: int=0, input_kwargs_to_split: List[str]=['hidden_states']) -> None:
        super().__init__()
        self.module = module
        self.split_size = split_size
        self.split_dim = split_dim
        self.input_kwargs_to_split = set(input_kwargs_to_split)
    def forward(self, *args, **kwargs) -> Union[torch.Tensor, Tuple[torch.Tensor]]:
        """Returns:"""
        split_inputs = {}
        for key in list(kwargs.keys()):
            if key not in self.input_kwargs_to_split or not torch.is_tensor(kwargs[key]): continue
            split_inputs[key] = torch.split(kwargs[key], self.split_size, self.split_dim)
            kwargs.pop(key)
        results = []
        for split_input in zip(*split_inputs.values()):
            inputs = dict(zip(split_inputs.keys(), split_input))
            inputs.update(kwargs)
            intermediate_tensor_or_tensor_tuple = self.module(*args, **inputs)
            results.append(intermediate_tensor_or_tensor_tuple)
        if isinstance(results[0], torch.Tensor): return torch.cat(results, dim=self.split_dim)
        elif isinstance(results[0], tuple): return tuple([torch.cat(x, dim=self.split_dim) for x in zip(*results)])
        else: raise ValueError("In order to use the SplitInferenceModule, it is necessary for the underlying `module` to either return a torch.Tensor or a tuple of torch.Tensor's.")
class AnimateDiffFreeNoiseMixin:
    def _enable_free_noise_in_block(self, block: Union[CrossAttnDownBlockMotion, DownBlockMotion, UpBlockMotion]):
        for motion_module in block.motion_modules:
            num_transformer_blocks = len(motion_module.transformer_blocks)
            for i in range(num_transformer_blocks):
                if isinstance(motion_module.transformer_blocks[i], FreeNoiseTransformerBlock): motion_module.transformer_blocks[i].set_free_noise_properties(self._free_noise_context_length,
                self._free_noise_context_stride, self._free_noise_weighting_scheme)
                else:
                    assert isinstance(motion_module.transformer_blocks[i], BasicTransformerBlock)
                    basic_transfomer_block = motion_module.transformer_blocks[i]
                    motion_module.transformer_blocks[i] = FreeNoiseTransformerBlock(dim=basic_transfomer_block.dim, num_attention_heads=basic_transfomer_block.num_attention_heads,
                    attention_head_dim=basic_transfomer_block.attention_head_dim, dropout=basic_transfomer_block.dropout, cross_attention_dim=basic_transfomer_block.cross_attention_dim,
                    activation_fn=basic_transfomer_block.activation_fn, attention_bias=basic_transfomer_block.attention_bias, only_cross_attention=basic_transfomer_block.only_cross_attention,
                    double_self_attention=basic_transfomer_block.double_self_attention, positional_embeddings=basic_transfomer_block.positional_embeddings,
                    num_positional_embeddings=basic_transfomer_block.num_positional_embeddings, context_length=self._free_noise_context_length, context_stride=self._free_noise_context_stride,
                    weighting_scheme=self._free_noise_weighting_scheme).to(device=self.device, dtype=self.dtype)
                    motion_module.transformer_blocks[i].load_state_dict(basic_transfomer_block.state_dict(), strict=True)
                    motion_module.transformer_blocks[i].set_chunk_feed_forward(basic_transfomer_block._chunk_size, basic_transfomer_block._chunk_dim)
    def _disable_free_noise_in_block(self, block: Union[CrossAttnDownBlockMotion, DownBlockMotion, UpBlockMotion]):
        for motion_module in block.motion_modules:
            num_transformer_blocks = len(motion_module.transformer_blocks)
            for i in range(num_transformer_blocks):
                if isinstance(motion_module.transformer_blocks[i], FreeNoiseTransformerBlock):
                    free_noise_transfomer_block = motion_module.transformer_blocks[i]
                    motion_module.transformer_blocks[i] = BasicTransformerBlock(dim=free_noise_transfomer_block.dim, num_attention_heads=free_noise_transfomer_block.num_attention_heads,
                    attention_head_dim=free_noise_transfomer_block.attention_head_dim, dropout=free_noise_transfomer_block.dropout, cross_attention_dim=free_noise_transfomer_block.cross_attention_dim,
                    activation_fn=free_noise_transfomer_block.activation_fn, attention_bias=free_noise_transfomer_block.attention_bias,
                    only_cross_attention=free_noise_transfomer_block.only_cross_attention, double_self_attention=free_noise_transfomer_block.double_self_attention,
                    positional_embeddings=free_noise_transfomer_block.positional_embeddings,
                    num_positional_embeddings=free_noise_transfomer_block.num_positional_embeddings).to(device=self.device, dtype=self.dtype)
                    motion_module.transformer_blocks[i].load_state_dict(free_noise_transfomer_block.state_dict(), strict=True)
                    motion_module.transformer_blocks[i].set_chunk_feed_forward(free_noise_transfomer_block._chunk_size, free_noise_transfomer_block._chunk_dim)
    def _check_inputs_free_noise(self, prompt, negative_prompt, prompt_embeds, negative_prompt_embeds, num_frames) -> None:
        if not isinstance(prompt, (str, dict)): raise ValueError(f'Expected `prompt` to have type `str` or `dict` but found type(prompt)={type(prompt)!r}')
        if negative_prompt is not None:
            if not isinstance(negative_prompt, (str, dict)): raise ValueError(f'Expected `negative_prompt` to have type `str` or `dict` but found type(negative_prompt)={type(negative_prompt)!r}')
        if prompt_embeds is not None or negative_prompt_embeds is not None: raise ValueError('`prompt_embeds` and `negative_prompt_embeds` is not supported in FreeNoise yet.')
        frame_indices = [isinstance(x, int) for x in prompt.keys()]
        frame_prompts = [isinstance(x, str) for x in prompt.values()]
        min_frame = min(list(prompt.keys()))
        max_frame = max(list(prompt.keys()))
        if not all(frame_indices): raise ValueError('Expected integer keys in `prompt` dict for FreeNoise.')
        if not all(frame_prompts): raise ValueError('Expected str values in `prompt` dict for FreeNoise.')
        if min_frame != 0: raise ValueError('The minimum frame index in `prompt` dict must be 0 as a starting prompt is necessary.')
        if max_frame >= num_frames: raise ValueError(f'The maximum frame index in `prompt` dict must be lesser than num_frames={num_frames!r} and follow 0-based indexing.')
    def _encode_prompt_free_noise(self, prompt: Union[str, Dict[int, str]], num_frames: int, device: torch.device, num_videos_per_prompt: int, do_classifier_free_guidance: bool,
    negative_prompt: Optional[Union[str, Dict[int, str]]]=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None,
    lora_scale: Optional[float]=None, clip_skip: Optional[int]=None) -> torch.Tensor:
        if negative_prompt is None: negative_prompt = ''
        if isinstance(prompt, str): prompt = {0: prompt}
        if isinstance(negative_prompt, str): negative_prompt = {0: negative_prompt}
        self._check_inputs_free_noise(prompt, negative_prompt, prompt_embeds, negative_prompt_embeds, num_frames)
        prompt = dict(sorted(prompt.items()))
        negative_prompt = dict(sorted(negative_prompt.items()))
        prompt[num_frames - 1] = prompt[list(prompt.keys())[-1]]
        negative_prompt[num_frames - 1] = negative_prompt[list(negative_prompt.keys())[-1]]
        frame_indices = list(prompt.keys())
        frame_prompts = list(prompt.values())
        frame_negative_indices = list(negative_prompt.keys())
        frame_negative_prompts = list(negative_prompt.values())
        prompt_embeds, _ = self.encode_prompt(prompt=frame_prompts, device=device, num_images_per_prompt=num_videos_per_prompt, do_classifier_free_guidance=False,
        negative_prompt=None, prompt_embeds=None, negative_prompt_embeds=None, lora_scale=lora_scale, clip_skip=clip_skip)
        shape = (num_frames, *prompt_embeds.shape[1:])
        prompt_interpolation_embeds = prompt_embeds.new_zeros(shape)
        for i in range(len(frame_indices) - 1):
            start_frame = frame_indices[i]
            end_frame = frame_indices[i + 1]
            start_tensor = prompt_embeds[i].unsqueeze(0)
            end_tensor = prompt_embeds[i + 1].unsqueeze(0)
            prompt_interpolation_embeds[start_frame:end_frame + 1] = self._free_noise_prompt_interpolation_callback(start_frame, end_frame, start_tensor, end_tensor)
        negative_prompt_embeds = None
        negative_prompt_interpolation_embeds = None
        if do_classifier_free_guidance:
            _, negative_prompt_embeds = self.encode_prompt(prompt=[''] * len(frame_negative_prompts), device=device, num_images_per_prompt=num_videos_per_prompt, do_classifier_free_guidance=True,
            negative_prompt=frame_negative_prompts, prompt_embeds=None, negative_prompt_embeds=None, lora_scale=lora_scale, clip_skip=clip_skip)
            negative_prompt_interpolation_embeds = negative_prompt_embeds.new_zeros(shape)
            for i in range(len(frame_negative_indices) - 1):
                start_frame = frame_negative_indices[i]
                end_frame = frame_negative_indices[i + 1]
                start_tensor = negative_prompt_embeds[i].unsqueeze(0)
                end_tensor = negative_prompt_embeds[i + 1].unsqueeze(0)
                negative_prompt_interpolation_embeds[start_frame:end_frame + 1] = self._free_noise_prompt_interpolation_callback(start_frame, end_frame, start_tensor, end_tensor)
        prompt_embeds = prompt_interpolation_embeds
        negative_prompt_embeds = negative_prompt_interpolation_embeds
        if do_classifier_free_guidance: prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
        return (prompt_embeds, negative_prompt_embeds)
    def _prepare_latents_free_noise(self, batch_size: int, num_channels_latents: int, num_frames: int, height: int, width: int, dtype: torch.dtype, device: torch.device,
    generator: Optional[torch.Generator]=None, latents: Optional[torch.Tensor]=None):
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        context_num_frames = self._free_noise_context_length if self._free_noise_context_length == 'repeat_context' else num_frames
        shape = (batch_size, num_channels_latents, context_num_frames, height // self.vae_scale_factor, width // self.vae_scale_factor)
        if latents is None:
            latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
            if self._free_noise_noise_type == 'random': return latents
        else:
            if latents.size(2) == num_frames: return latents
            elif latents.size(2) != self._free_noise_context_length: raise ValueError(f'You have passed `latents` as a parameter to FreeNoise. The expected number of frames is either {num_frames} or {self._free_noise_context_length}, but found {latents.size(2)}')
            latents = latents.to(device)
        if self._free_noise_noise_type == 'shuffle_context':
            for i in range(self._free_noise_context_length, num_frames, self._free_noise_context_stride):
                window_start = max(0, i - self._free_noise_context_length)
                window_end = min(num_frames, window_start + self._free_noise_context_stride)
                window_length = window_end - window_start
                if window_length == 0: break
                indices = torch.LongTensor(list(range(window_start, window_end)))
                shuffled_indices = indices[torch.randperm(window_length, generator=generator)]
                current_start = i
                current_end = min(num_frames, current_start + window_length)
                if current_end == current_start + window_length: latents[:, :, current_start:current_end] = latents[:, :, shuffled_indices]
                else:
                    prefix_length = current_end - current_start
                    shuffled_indices = shuffled_indices[:prefix_length]
                    latents[:, :, current_start:current_end] = latents[:, :, shuffled_indices]
        elif self._free_noise_noise_type == 'repeat_context':
            num_repeats = (num_frames + self._free_noise_context_length - 1) // self._free_noise_context_length
            latents = torch.cat([latents] * num_repeats, dim=2)
        latents = latents[:, :, :num_frames]
        return latents
    def _lerp(self, start_index: int, end_index: int, start_tensor: torch.Tensor, end_tensor: torch.Tensor) -> torch.Tensor:
        num_indices = end_index - start_index + 1
        interpolated_tensors = []
        for i in range(num_indices):
            alpha = i / (num_indices - 1)
            interpolated_tensor = (1 - alpha) * start_tensor + alpha * end_tensor
            interpolated_tensors.append(interpolated_tensor)
        interpolated_tensors = torch.cat(interpolated_tensors)
        return interpolated_tensors
    def enable_free_noise(self, context_length: Optional[int]=16, context_stride: int=4, weighting_scheme: str='pyramid', noise_type: str='shuffle_context',
    prompt_interpolation_callback: Optional[Callable[[DiffusionPipeline, int, int, torch.Tensor, torch.Tensor], torch.Tensor]]=None) -> None:
        """Args:"""
        allowed_weighting_scheme = ['flat', 'pyramid', 'delayed_reverse_sawtooth']
        allowed_noise_type = ['shuffle_context', 'repeat_context', 'random']
        if weighting_scheme not in allowed_weighting_scheme: raise ValueError(f'The parameter `weighting_scheme` must be one of {allowed_weighting_scheme}, but got weighting_scheme={weighting_scheme!r}')
        if noise_type not in allowed_noise_type: raise ValueError(f'The parameter `noise_type` must be one of {allowed_noise_type}, but got noise_type={noise_type!r}')
        self._free_noise_context_length = context_length or self.motion_adapter.config.motion_max_seq_length
        self._free_noise_context_stride = context_stride
        self._free_noise_weighting_scheme = weighting_scheme
        self._free_noise_noise_type = noise_type
        self._free_noise_prompt_interpolation_callback = prompt_interpolation_callback or self._lerp
        if hasattr(self.unet.mid_block, 'motion_modules'): blocks = [*self.unet.down_blocks, self.unet.mid_block, *self.unet.up_blocks]
        else: blocks = [*self.unet.down_blocks, *self.unet.up_blocks]
        for block in blocks: self._enable_free_noise_in_block(block)
    def disable_free_noise(self) -> None:
        self._free_noise_context_length = None
        if hasattr(self.unet.mid_block, 'motion_modules'): blocks = [*self.unet.down_blocks, self.unet.mid_block, *self.unet.up_blocks]
        else: blocks = [*self.unet.down_blocks, *self.unet.up_blocks]
        blocks = [*self.unet.down_blocks, self.unet.mid_block, *self.unet.up_blocks]
        for block in blocks: self._disable_free_noise_in_block(block)
    def _enable_split_inference_motion_modules_(self, motion_modules: List[AnimateDiffTransformer3D], spatial_split_size: int) -> None:
        for motion_module in motion_modules:
            motion_module.proj_in = SplitInferenceModule(motion_module.proj_in, spatial_split_size, 0, ['input'])
            for i in range(len(motion_module.transformer_blocks)): motion_module.transformer_blocks[i] = SplitInferenceModule(motion_module.transformer_blocks[i], spatial_split_size, 0, ['hidden_states', 'encoder_hidden_states'])
            motion_module.proj_out = SplitInferenceModule(motion_module.proj_out, spatial_split_size, 0, ['input'])
    def _enable_split_inference_attentions_(self, attentions: List[Transformer2DModel], temporal_split_size: int) -> None:
        for i in range(len(attentions)): attentions[i] = SplitInferenceModule(attentions[i], temporal_split_size, 0, ['hidden_states', 'encoder_hidden_states'])
    def _enable_split_inference_resnets_(self, resnets: List[ResnetBlock2D], temporal_split_size: int) -> None:
        for i in range(len(resnets)): resnets[i] = SplitInferenceModule(resnets[i], temporal_split_size, 0, ['input_tensor', 'temb'])
    def _enable_split_inference_samplers_(self, samplers: Union[List[Downsample2D], List[Upsample2D]], temporal_split_size: int) -> None:
        for i in range(len(samplers)): samplers[i] = SplitInferenceModule(samplers[i], temporal_split_size, 0, ['hidden_states'])
    def enable_free_noise_split_inference(self, spatial_split_size: int=256, temporal_split_size: int=16) -> None:
        """Args:"""
        blocks = [*self.unet.down_blocks, self.unet.mid_block, *self.unet.up_blocks]
        for block in blocks:
            if getattr(block, 'motion_modules', None) is not None: self._enable_split_inference_motion_modules_(block.motion_modules, spatial_split_size)
            if getattr(block, 'attentions', None) is not None: self._enable_split_inference_attentions_(block.attentions, temporal_split_size)
            if getattr(block, 'resnets', None) is not None: self._enable_split_inference_resnets_(block.resnets, temporal_split_size)
            if getattr(block, 'downsamplers', None) is not None: self._enable_split_inference_samplers_(block.downsamplers, temporal_split_size)
            if getattr(block, 'upsamplers', None) is not None: self._enable_split_inference_samplers_(block.upsamplers, temporal_split_size)
    @property
    def free_noise_enabled(self): return hasattr(self, '_free_noise_context_length') and self._free_noise_context_length is not None
class SAPIVideoGenFreeNoiseMixin:
    def _enable_free_noise_in_block(self, block: Union[CrossAttnDownBlockMotion, DownBlockMotion, UpBlockMotion]):
        for motion_module in block.motion_modules:
            num_transformer_blocks = len(motion_module.transformer_blocks)
            for i in range(num_transformer_blocks):
                if isinstance(motion_module.transformer_blocks[i], FreeNoiseTransformerBlock): motion_module.transformer_blocks[i].set_free_noise_properties(self._free_noise_context_length,
                self._free_noise_context_stride, self._free_noise_weighting_scheme)
                else:
                    assert isinstance(motion_module.transformer_blocks[i], BasicTransformerBlock)
                    basic_transfomer_block = motion_module.transformer_blocks[i]
                    motion_module.transformer_blocks[i] = FreeNoiseTransformerBlock(dim=basic_transfomer_block.dim, num_attention_heads=basic_transfomer_block.num_attention_heads,
                    attention_head_dim=basic_transfomer_block.attention_head_dim, dropout=basic_transfomer_block.dropout, cross_attention_dim=basic_transfomer_block.cross_attention_dim,
                    activation_fn=basic_transfomer_block.activation_fn, attention_bias=basic_transfomer_block.attention_bias, only_cross_attention=basic_transfomer_block.only_cross_attention,
                    double_self_attention=basic_transfomer_block.double_self_attention, positional_embeddings=basic_transfomer_block.positional_embeddings,
                    num_positional_embeddings=basic_transfomer_block.num_positional_embeddings, context_length=self._free_noise_context_length, context_stride=self._free_noise_context_stride,
                    weighting_scheme=self._free_noise_weighting_scheme).to(device=self.device, dtype=self.dtype)
                    motion_module.transformer_blocks[i].load_state_dict(basic_transfomer_block.state_dict(), strict=True)
                    motion_module.transformer_blocks[i].set_chunk_feed_forward(basic_transfomer_block._chunk_size, basic_transfomer_block._chunk_dim)
    def _disable_free_noise_in_block(self, block: Union[CrossAttnDownBlockMotion, DownBlockMotion, UpBlockMotion]):
        for motion_module in block.motion_modules:
            num_transformer_blocks = len(motion_module.transformer_blocks)
            for i in range(num_transformer_blocks):
                if isinstance(motion_module.transformer_blocks[i], FreeNoiseTransformerBlock):
                    free_noise_transfomer_block = motion_module.transformer_blocks[i]
                    motion_module.transformer_blocks[i] = BasicTransformerBlock(dim=free_noise_transfomer_block.dim, num_attention_heads=free_noise_transfomer_block.num_attention_heads,
                    attention_head_dim=free_noise_transfomer_block.attention_head_dim, dropout=free_noise_transfomer_block.dropout, cross_attention_dim=free_noise_transfomer_block.cross_attention_dim,
                    activation_fn=free_noise_transfomer_block.activation_fn, attention_bias=free_noise_transfomer_block.attention_bias,
                    only_cross_attention=free_noise_transfomer_block.only_cross_attention, double_self_attention=free_noise_transfomer_block.double_self_attention,
                    positional_embeddings=free_noise_transfomer_block.positional_embeddings,
                    num_positional_embeddings=free_noise_transfomer_block.num_positional_embeddings).to(device=self.device, dtype=self.dtype)
                    motion_module.transformer_blocks[i].load_state_dict(free_noise_transfomer_block.state_dict(), strict=True)
                    motion_module.transformer_blocks[i].set_chunk_feed_forward(free_noise_transfomer_block._chunk_size, free_noise_transfomer_block._chunk_dim)
    def _check_inputs_free_noise(self, prompt, negative_prompt, prompt_embeds, negative_prompt_embeds, num_frames) -> None:
        if not isinstance(prompt, (str, dict)): raise ValueError(f'Expected `prompt` to have type `str` or `dict` but found type(prompt)={type(prompt)!r}')
        if negative_prompt is not None:
            if not isinstance(negative_prompt, (str, dict)): raise ValueError(f'Expected `negative_prompt` to have type `str` or `dict` but found type(negative_prompt)={type(negative_prompt)!r}')
        if prompt_embeds is not None or negative_prompt_embeds is not None: raise ValueError('`prompt_embeds` and `negative_prompt_embeds` is not supported in FreeNoise yet.')
        frame_indices = [isinstance(x, int) for x in prompt.keys()]
        frame_prompts = [isinstance(x, str) for x in prompt.values()]
        min_frame = min(list(prompt.keys()))
        max_frame = max(list(prompt.keys()))
        if not all(frame_indices): raise ValueError('Expected integer keys in `prompt` dict for FreeNoise.')
        if not all(frame_prompts): raise ValueError('Expected str values in `prompt` dict for FreeNoise.')
        if min_frame != 0: raise ValueError('The minimum frame index in `prompt` dict must be 0 as a starting prompt is necessary.')
        if max_frame >= num_frames: raise ValueError(f'The maximum frame index in `prompt` dict must be lesser than num_frames={num_frames!r} and follow 0-based indexing.')
    def _encode_prompt_free_noise(self, prompt: Union[str, Dict[int, str]], num_frames: int, device: torch.device, num_videos_per_prompt: int, do_classifier_free_guidance: bool,
    negative_prompt: Optional[Union[str, Dict[int, str]]]=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None,
    lora_scale: Optional[float]=None, clip_skip: Optional[int]=None) -> torch.Tensor:
        if negative_prompt is None: negative_prompt = ''
        if isinstance(prompt, str): prompt = {0: prompt}
        if isinstance(negative_prompt, str): negative_prompt = {0: negative_prompt}
        self._check_inputs_free_noise(prompt, negative_prompt, prompt_embeds, negative_prompt_embeds, num_frames)
        prompt = dict(sorted(prompt.items()))
        negative_prompt = dict(sorted(negative_prompt.items()))
        prompt[num_frames - 1] = prompt[list(prompt.keys())[-1]]
        negative_prompt[num_frames - 1] = negative_prompt[list(negative_prompt.keys())[-1]]
        frame_indices = list(prompt.keys())
        frame_prompts = list(prompt.values())
        frame_negative_indices = list(negative_prompt.keys())
        frame_negative_prompts = list(negative_prompt.values())
        prompt_embeds, _ = self.encode_prompt(prompt=frame_prompts, device=device, num_images_per_prompt=num_videos_per_prompt, do_classifier_free_guidance=False,
        negative_prompt=None, prompt_embeds=None, negative_prompt_embeds=None, lora_scale=lora_scale, clip_skip=clip_skip)
        shape = (num_frames, *prompt_embeds.shape[1:])
        prompt_interpolation_embeds = prompt_embeds.new_zeros(shape)
        for i in range(len(frame_indices) - 1):
            start_frame = frame_indices[i]
            end_frame = frame_indices[i + 1]
            start_tensor = prompt_embeds[i].unsqueeze(0)
            end_tensor = prompt_embeds[i + 1].unsqueeze(0)
            prompt_interpolation_embeds[start_frame:end_frame + 1] = self._free_noise_prompt_interpolation_callback(start_frame, end_frame, start_tensor, end_tensor)
        negative_prompt_embeds = None
        negative_prompt_interpolation_embeds = None
        if do_classifier_free_guidance:
            _, negative_prompt_embeds = self.encode_prompt(prompt=[''] * len(frame_negative_prompts), device=device, num_images_per_prompt=num_videos_per_prompt, do_classifier_free_guidance=True,
            negative_prompt=frame_negative_prompts, prompt_embeds=None, negative_prompt_embeds=None, lora_scale=lora_scale, clip_skip=clip_skip)
            negative_prompt_interpolation_embeds = negative_prompt_embeds.new_zeros(shape)
            for i in range(len(frame_negative_indices) - 1):
                start_frame = frame_negative_indices[i]
                end_frame = frame_negative_indices[i + 1]
                start_tensor = negative_prompt_embeds[i].unsqueeze(0)
                end_tensor = negative_prompt_embeds[i + 1].unsqueeze(0)
                negative_prompt_interpolation_embeds[start_frame:end_frame + 1] = self._free_noise_prompt_interpolation_callback(start_frame, end_frame, start_tensor, end_tensor)
        prompt_embeds = prompt_interpolation_embeds
        negative_prompt_embeds = negative_prompt_interpolation_embeds
        if do_classifier_free_guidance: prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
        return (prompt_embeds, negative_prompt_embeds)
    def _prepare_latents_free_noise(self, batch_size: int, num_channels_latents: int, num_frames: int, height: int, width: int, dtype: torch.dtype, device: torch.device,
    generator: Optional[torch.Generator]=None, latents: Optional[torch.Tensor]=None):
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        context_num_frames = self._free_noise_context_length if self._free_noise_context_length == 'repeat_context' else num_frames
        shape = (batch_size, num_channels_latents, context_num_frames, height // self.vae_scale_factor, width // self.vae_scale_factor)
        if latents is None:
            latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
            if self._free_noise_noise_type == 'random': return latents
        else:
            if latents.size(2) == num_frames: return latents
            elif latents.size(2) != self._free_noise_context_length: raise ValueError(f'You have passed `latents` as a parameter to FreeNoise. The expected number of frames is either {num_frames} or {self._free_noise_context_length}, but found {latents.size(2)}')
            latents = latents.to(device)
        if self._free_noise_noise_type == 'shuffle_context':
            for i in range(self._free_noise_context_length, num_frames, self._free_noise_context_stride):
                window_start = max(0, i - self._free_noise_context_length)
                window_end = min(num_frames, window_start + self._free_noise_context_stride)
                window_length = window_end - window_start
                if window_length == 0: break
                indices = torch.LongTensor(list(range(window_start, window_end)))
                shuffled_indices = indices[torch.randperm(window_length, generator=generator)]
                current_start = i
                current_end = min(num_frames, current_start + window_length)
                if current_end == current_start + window_length: latents[:, :, current_start:current_end] = latents[:, :, shuffled_indices]
                else:
                    prefix_length = current_end - current_start
                    shuffled_indices = shuffled_indices[:prefix_length]
                    latents[:, :, current_start:current_end] = latents[:, :, shuffled_indices]
        elif self._free_noise_noise_type == 'repeat_context':
            num_repeats = (num_frames + self._free_noise_context_length - 1) // self._free_noise_context_length
            latents = torch.cat([latents] * num_repeats, dim=2)
        latents = latents[:, :, :num_frames]
        return latents
    def _lerp(self, start_index: int, end_index: int, start_tensor: torch.Tensor, end_tensor: torch.Tensor) -> torch.Tensor:
        num_indices = end_index - start_index + 1
        interpolated_tensors = []
        for i in range(num_indices):
            alpha = i / (num_indices - 1)
            interpolated_tensor = (1 - alpha) * start_tensor + alpha * end_tensor
            interpolated_tensors.append(interpolated_tensor)
        interpolated_tensors = torch.cat(interpolated_tensors)
        return interpolated_tensors
    def enable_free_noise(self, context_length: Optional[int]=16, context_stride: int=4, weighting_scheme: str='pyramid', noise_type: str='shuffle_context',
    prompt_interpolation_callback: Optional[Callable[[DiffusionPipeline, int, int, torch.Tensor, torch.Tensor], torch.Tensor]]=None) -> None:
        """Args:"""
        allowed_weighting_scheme = ['flat', 'pyramid', 'delayed_reverse_sawtooth']
        allowed_noise_type = ['shuffle_context', 'repeat_context', 'random']
        if weighting_scheme not in allowed_weighting_scheme: raise ValueError(f'The parameter `weighting_scheme` must be one of {allowed_weighting_scheme}, but got weighting_scheme={weighting_scheme!r}')
        if noise_type not in allowed_noise_type: raise ValueError(f'The parameter `noise_type` must be one of {allowed_noise_type}, but got noise_type={noise_type!r}')
        self._free_noise_context_length = context_length or self.motion_adapter.config.motion_max_seq_length
        self._free_noise_context_stride = context_stride
        self._free_noise_weighting_scheme = weighting_scheme
        self._free_noise_noise_type = noise_type
        self._free_noise_prompt_interpolation_callback = prompt_interpolation_callback or self._lerp
        if hasattr(self.unet.mid_block, 'motion_modules'): blocks = [*self.unet.down_blocks, self.unet.mid_block, *self.unet.up_blocks]
        else: blocks = [*self.unet.down_blocks, *self.unet.up_blocks]
        for block in blocks: self._enable_free_noise_in_block(block)
    def disable_free_noise(self) -> None:
        self._free_noise_context_length = None
        if hasattr(self.unet.mid_block, 'motion_modules'): blocks = [*self.unet.down_blocks, self.unet.mid_block, *self.unet.up_blocks]
        else: blocks = [*self.unet.down_blocks, *self.unet.up_blocks]
        blocks = [*self.unet.down_blocks, self.unet.mid_block, *self.unet.up_blocks]
        for block in blocks: self._disable_free_noise_in_block(block)
    def _enable_split_inference_motion_modules_(self, motion_modules: List[SAPIVideoGenTransformer3D], spatial_split_size: int) -> None:
        for motion_module in motion_modules:
            motion_module.proj_in = SplitInferenceModule(motion_module.proj_in, spatial_split_size, 0, ['input'])
            for i in range(len(motion_module.transformer_blocks)): motion_module.transformer_blocks[i] = SplitInferenceModule(motion_module.transformer_blocks[i], spatial_split_size, 0, ['hidden_states', 'encoder_hidden_states'])
            motion_module.proj_out = SplitInferenceModule(motion_module.proj_out, spatial_split_size, 0, ['input'])
    def _enable_split_inference_attentions_(self, attentions: List[Transformer2DModel], temporal_split_size: int) -> None:
        for i in range(len(attentions)): attentions[i] = SplitInferenceModule(attentions[i], temporal_split_size, 0, ['hidden_states', 'encoder_hidden_states'])
    def _enable_split_inference_resnets_(self, resnets: List[ResnetBlock2D], temporal_split_size: int) -> None:
        for i in range(len(resnets)): resnets[i] = SplitInferenceModule(resnets[i], temporal_split_size, 0, ['input_tensor', 'temb'])
    def _enable_split_inference_samplers_(self, samplers: Union[List[Downsample2D], List[Upsample2D]], temporal_split_size: int) -> None:
        for i in range(len(samplers)): samplers[i] = SplitInferenceModule(samplers[i], temporal_split_size, 0, ['hidden_states'])
    def enable_free_noise_split_inference(self, spatial_split_size: int=256, temporal_split_size: int=16) -> None:
        """Args:"""
        blocks = [*self.unet.down_blocks, self.unet.mid_block, *self.unet.up_blocks]
        for block in blocks:
            if getattr(block, 'motion_modules', None) is not None: self._enable_split_inference_motion_modules_(block.motion_modules, spatial_split_size)
            if getattr(block, 'attentions', None) is not None: self._enable_split_inference_attentions_(block.attentions, temporal_split_size)
            if getattr(block, 'resnets', None) is not None: self._enable_split_inference_resnets_(block.resnets, temporal_split_size)
            if getattr(block, 'downsamplers', None) is not None: self._enable_split_inference_samplers_(block.downsamplers, temporal_split_size)
            if getattr(block, 'upsamplers', None) is not None: self._enable_split_inference_samplers_(block.upsamplers, temporal_split_size)
    @property
    def free_noise_enabled(self): return hasattr(self, '_free_noise_context_length') and self._free_noise_context_length is not None
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
