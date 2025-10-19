'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from sapiens_transformers import BaseImageProcessor, CLIPTextModelWithProjection, CLIPTokenizer, PreTrainedModel, T5EncoderModel, T5TokenizerFast
from ...utils import USE_PEFT_BACKEND, is_torch_xla_available, replace_example_docstring, scale_lora_layers, unscale_lora_layers
from ...loaders import FromSingleFileMixin, SAPIIPAdapterMixin, SAPILoraLoaderMixin
from ...image_processor import PipelineImageInput, VaeImageProcessor
from typing import Any, Callable, Dict, List, Optional, Union
from ...schedulers import FlowMatchEulerDiscreteScheduler
from ...models.sapiens_transformers import SAPITransformer2DModel
from .pipeline_output import SAPIImageGenPipelineOutput
from ...models.autoencoders import AutoencoderKL
from ..pipeline_utils import DiffusionPipeline
from ...utils.torch_utils import randn_tensor
import inspect
import torch
if is_torch_xla_available():
    import torch_xla.core.xla_model as xm
    XLA_AVAILABLE = True
else: XLA_AVAILABLE = False
EXAMPLE_DOC_STRING = ''
def calculate_shift(image_seq_len, base_seq_len: int=256, max_seq_len: int=4096, base_shift: float=0.5, max_shift: float=1.16):
    m = (max_shift - base_shift) / (max_seq_len - base_seq_len)
    b = base_shift - m * base_seq_len
    mu = image_seq_len * m + b
    return mu
def retrieve_timesteps(scheduler, num_inference_steps: Optional[int]=None, device: Optional[Union[str, torch.device]]=None,
timesteps: Optional[List[int]]=None, sigmas: Optional[List[float]]=None, **kwargs):
    """Returns:"""
    if timesteps is not None and sigmas is not None: raise ValueError('Only one of `timesteps` or `sigmas` can be passed. Please choose one to set custom values')
    if timesteps is not None:
        accepts_timesteps = 'timesteps' in set(inspect.signature(scheduler.set_timesteps).parameters.keys())
        if not accepts_timesteps: raise ValueError(f"The current scheduler class {scheduler.__class__}'s `set_timesteps` does not support custom timestep schedules. Please check whether you are using the correct scheduler.")
        scheduler.set_timesteps(timesteps=timesteps, device=device, **kwargs)
        timesteps = scheduler.timesteps
        num_inference_steps = len(timesteps)
    elif sigmas is not None:
        accept_sigmas = 'sigmas' in set(inspect.signature(scheduler.set_timesteps).parameters.keys())
        if not accept_sigmas: raise ValueError(f"The current scheduler class {scheduler.__class__}'s `set_timesteps` does not support custom sigmas schedules. Please check whether you are using the correct scheduler.")
        scheduler.set_timesteps(sigmas=sigmas, device=device, **kwargs)
        timesteps = scheduler.timesteps
        num_inference_steps = len(timesteps)
    else:
        scheduler.set_timesteps(num_inference_steps, device=device, **kwargs)
        timesteps = scheduler.timesteps
    return (timesteps, num_inference_steps)
class SAPIImageGenPipeline(DiffusionPipeline, SAPILoraLoaderMixin, FromSingleFileMixin, SAPIIPAdapterMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->text_encoder_2->text_encoder_3->image_encoder->transformer->vae'
    _optional_components = ['image_encoder', 'feature_extractor']
    _callback_tensor_inputs = ['latents', 'prompt_embeds', 'negative_prompt_embeds', 'negative_pooled_prompt_embeds']
    def __init__(self, transformer: SAPITransformer2DModel, scheduler: FlowMatchEulerDiscreteScheduler, vae: AutoencoderKL, text_encoder: CLIPTextModelWithProjection, tokenizer: CLIPTokenizer,
    text_encoder_2: CLIPTextModelWithProjection, tokenizer_2: CLIPTokenizer, text_encoder_3: T5EncoderModel, tokenizer_3: T5TokenizerFast,
    image_encoder: PreTrainedModel=None, feature_extractor: BaseImageProcessor=None):
        super().__init__()
        self.register_modules(vae=vae, text_encoder=text_encoder, text_encoder_2=text_encoder_2, text_encoder_3=text_encoder_3, tokenizer=tokenizer, tokenizer_2=tokenizer_2,
        tokenizer_3=tokenizer_3, transformer=transformer, scheduler=scheduler, image_encoder=image_encoder, feature_extractor=feature_extractor)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1) if hasattr(self, 'vae') and self.vae is not None else 8
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor)
        self.tokenizer_max_length = self.tokenizer.model_max_length if hasattr(self, 'tokenizer') and self.tokenizer is not None else 77
        self.default_sample_size = self.transformer.config.sample_size if hasattr(self, 'transformer') and self.transformer is not None else 128
        self.patch_size = self.transformer.config.patch_size if hasattr(self, 'transformer') and self.transformer is not None else 2
    def _get_t5_prompt_embeds(self, prompt: Union[str, List[str]]=None, num_images_per_prompt: int=1, max_sequence_length: int=256, device: Optional[torch.device]=None, dtype: Optional[torch.dtype]=None):
        device = device or self._execution_device
        dtype = dtype or self.text_encoder.dtype
        prompt = [prompt] if isinstance(prompt, str) else prompt
        batch_size = len(prompt)
        if self.text_encoder_3 is None: return torch.zeros((batch_size * num_images_per_prompt, self.tokenizer_max_length, self.transformer.config.joint_attention_dim), device=device, dtype=dtype)
        text_inputs = self.tokenizer_3(prompt, padding='max_length', max_length=max_sequence_length, truncation=True, add_special_tokens=True, return_tensors='pt')
        text_input_ids = text_inputs.input_ids
        untruncated_ids = self.tokenizer_3(prompt, padding='longest', return_tensors='pt').input_ids
        if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer_3.batch_decode(untruncated_ids[:, self.tokenizer_max_length - 1:-1])
        prompt_embeds = self.text_encoder_3(text_input_ids.to(device))[0]
        dtype = self.text_encoder_3.dtype
        prompt_embeds = prompt_embeds.to(dtype=dtype, device=device)
        _, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_images_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
        return prompt_embeds
    def _get_clip_prompt_embeds(self, prompt: Union[str, List[str]], num_images_per_prompt: int=1, device: Optional[torch.device]=None, clip_skip: Optional[int]=None, clip_model_index: int=0):
        device = device or self._execution_device
        clip_tokenizers = [self.tokenizer, self.tokenizer_2]
        clip_text_encoders = [self.text_encoder, self.text_encoder_2]
        tokenizer = clip_tokenizers[clip_model_index]
        text_encoder = clip_text_encoders[clip_model_index]
        prompt = [prompt] if isinstance(prompt, str) else prompt
        batch_size = len(prompt)
        text_inputs = tokenizer(prompt, padding='max_length', max_length=self.tokenizer_max_length, truncation=True, return_tensors='pt')
        text_input_ids = text_inputs.input_ids
        untruncated_ids = tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
        if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = tokenizer.batch_decode(untruncated_ids[:, self.tokenizer_max_length - 1:-1])
        prompt_embeds = text_encoder(text_input_ids.to(device), output_hidden_states=True)
        pooled_prompt_embeds = prompt_embeds[0]
        if clip_skip is None: prompt_embeds = prompt_embeds.hidden_states[-2]
        else: prompt_embeds = prompt_embeds.hidden_states[-(clip_skip + 2)]
        prompt_embeds = prompt_embeds.to(dtype=self.text_encoder.dtype, device=device)
        _, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_images_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
        pooled_prompt_embeds = pooled_prompt_embeds.repeat(1, num_images_per_prompt, 1)
        pooled_prompt_embeds = pooled_prompt_embeds.view(batch_size * num_images_per_prompt, -1)
        return (prompt_embeds, pooled_prompt_embeds)
    def encode_prompt(self, prompt: Union[str, List[str]], prompt_2: Union[str, List[str]], prompt_3: Union[str, List[str]], device: Optional[torch.device]=None,
    num_images_per_prompt: int=1, do_classifier_free_guidance: bool=True, negative_prompt: Optional[Union[str, List[str]]]=None, negative_prompt_2: Optional[Union[str,
    List[str]]]=None, negative_prompt_3: Optional[Union[str, List[str]]]=None, prompt_embeds: Optional[torch.FloatTensor]=None, negative_prompt_embeds: Optional[torch.FloatTensor]=None,
    pooled_prompt_embeds: Optional[torch.FloatTensor]=None, negative_pooled_prompt_embeds: Optional[torch.FloatTensor]=None,
    clip_skip: Optional[int]=None, max_sequence_length: int=256, lora_scale: Optional[float]=None):
        """Args:"""
        device = device or self._execution_device
        if lora_scale is not None and isinstance(self, SAPILoraLoaderMixin):
            self._lora_scale = lora_scale
            if self.text_encoder is not None and USE_PEFT_BACKEND: scale_lora_layers(self.text_encoder, lora_scale)
            if self.text_encoder_2 is not None and USE_PEFT_BACKEND: scale_lora_layers(self.text_encoder_2, lora_scale)
        prompt = [prompt] if isinstance(prompt, str) else prompt
        if prompt is not None: batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if prompt_embeds is None:
            prompt_2 = prompt_2 or prompt
            prompt_2 = [prompt_2] if isinstance(prompt_2, str) else prompt_2
            prompt_3 = prompt_3 or prompt
            prompt_3 = [prompt_3] if isinstance(prompt_3, str) else prompt_3
            prompt_embed, pooled_prompt_embed = self._get_clip_prompt_embeds(prompt=prompt, device=device, num_images_per_prompt=num_images_per_prompt, clip_skip=clip_skip, clip_model_index=0)
            prompt_2_embed, pooled_prompt_2_embed = self._get_clip_prompt_embeds(prompt=prompt_2, device=device, num_images_per_prompt=num_images_per_prompt, clip_skip=clip_skip, clip_model_index=1)
            clip_prompt_embeds = torch.cat([prompt_embed, prompt_2_embed], dim=-1)
            t5_prompt_embed = self._get_t5_prompt_embeds(prompt=prompt_3, num_images_per_prompt=num_images_per_prompt, max_sequence_length=max_sequence_length, device=device)
            clip_prompt_embeds = torch.nn.functional.pad(clip_prompt_embeds, (0, t5_prompt_embed.shape[-1] - clip_prompt_embeds.shape[-1]))
            prompt_embeds = torch.cat([clip_prompt_embeds, t5_prompt_embed], dim=-2)
            pooled_prompt_embeds = torch.cat([pooled_prompt_embed, pooled_prompt_2_embed], dim=-1)
        if do_classifier_free_guidance and negative_prompt_embeds is None:
            negative_prompt = negative_prompt or ''
            negative_prompt_2 = negative_prompt_2 or negative_prompt
            negative_prompt_3 = negative_prompt_3 or negative_prompt
            negative_prompt = batch_size * [negative_prompt] if isinstance(negative_prompt, str) else negative_prompt
            negative_prompt_2 = batch_size * [negative_prompt_2] if isinstance(negative_prompt_2, str) else negative_prompt_2
            negative_prompt_3 = batch_size * [negative_prompt_3] if isinstance(negative_prompt_3, str) else negative_prompt_3
            if prompt is not None and type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            negative_prompt_embed, negative_pooled_prompt_embed = self._get_clip_prompt_embeds(negative_prompt, device=device, num_images_per_prompt=num_images_per_prompt, clip_skip=None, clip_model_index=0)
            negative_prompt_2_embed, negative_pooled_prompt_2_embed = self._get_clip_prompt_embeds(negative_prompt_2, device=device, num_images_per_prompt=num_images_per_prompt, clip_skip=None, clip_model_index=1)
            negative_clip_prompt_embeds = torch.cat([negative_prompt_embed, negative_prompt_2_embed], dim=-1)
            t5_negative_prompt_embed = self._get_t5_prompt_embeds(prompt=negative_prompt_3, num_images_per_prompt=num_images_per_prompt, max_sequence_length=max_sequence_length, device=device)
            negative_clip_prompt_embeds = torch.nn.functional.pad(negative_clip_prompt_embeds, (0, t5_negative_prompt_embed.shape[-1] - negative_clip_prompt_embeds.shape[-1]))
            negative_prompt_embeds = torch.cat([negative_clip_prompt_embeds, t5_negative_prompt_embed], dim=-2)
            negative_pooled_prompt_embeds = torch.cat([negative_pooled_prompt_embed, negative_pooled_prompt_2_embed], dim=-1)
        if self.text_encoder is not None:
            if isinstance(self, SAPILoraLoaderMixin) and USE_PEFT_BACKEND: unscale_lora_layers(self.text_encoder, lora_scale)
        if self.text_encoder_2 is not None:
            if isinstance(self, SAPILoraLoaderMixin) and USE_PEFT_BACKEND: unscale_lora_layers(self.text_encoder_2, lora_scale)
        return (prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds)
    def check_inputs(self, prompt, prompt_2, prompt_3, height, width, negative_prompt=None, negative_prompt_2=None, negative_prompt_3=None, prompt_embeds=None, negative_prompt_embeds=None, pooled_prompt_embeds=None, negative_pooled_prompt_embeds=None, callback_on_step_end_tensor_inputs=None, max_sequence_length=None):
        if height % (self.vae_scale_factor * self.patch_size) != 0 or width % (self.vae_scale_factor * self.patch_size) != 0: raise ValueError(f'`height` and `width` have to be divisible by {self.vae_scale_factor * self.patch_size} but are {height} and {width}.You can use height {height - height % (self.vae_scale_factor * self.patch_size)} and width {width - width % (self.vae_scale_factor * self.patch_size)}.')
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt_2 is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt_2`: {prompt_2} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt_3 is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt_3`: {prompt_2} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        elif prompt_2 is not None and (not isinstance(prompt_2, str) and (not isinstance(prompt_2, list))): raise ValueError(f'`prompt_2` has to be of type `str` or `list` but is {type(prompt_2)}')
        elif prompt_3 is not None and (not isinstance(prompt_3, str) and (not isinstance(prompt_3, list))): raise ValueError(f'`prompt_3` has to be of type `str` or `list` but is {type(prompt_3)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        elif negative_prompt_2 is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt_2`: {negative_prompt_2} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        elif negative_prompt_3 is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt_3`: {negative_prompt_3} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
        if prompt_embeds is not None and pooled_prompt_embeds is None: raise ValueError('If `prompt_embeds` are provided, `pooled_prompt_embeds` also have to be passed. Make sure to generate `pooled_prompt_embeds` from the same text encoder that was used to generate `prompt_embeds`.')
        if negative_prompt_embeds is not None and negative_pooled_prompt_embeds is None: raise ValueError('If `negative_prompt_embeds` are provided, `negative_pooled_prompt_embeds` also have to be passed. Make sure to generate `negative_pooled_prompt_embeds` from the same text encoder that was used to generate `negative_prompt_embeds`.')
        if max_sequence_length is not None and max_sequence_length > 512: raise ValueError(f'`max_sequence_length` cannot be greater than 512 but is {max_sequence_length}')
    def prepare_latents(self, batch_size, num_channels_latents, height, width, dtype, device, generator, latents=None):
        if latents is not None: return latents.to(device=device, dtype=dtype)
        shape = (batch_size, num_channels_latents, int(height) // self.vae_scale_factor, int(width) // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        return latents
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def skip_guidance_layers(self): return self._skip_guidance_layers
    @property
    def clip_skip(self): return self._clip_skip
    @property
    def do_classifier_free_guidance(self): return self._guidance_scale > 1
    @property
    def joint_attention_kwargs(self): return self._joint_attention_kwargs
    @property
    def num_timesteps(self): return self._num_timesteps
    @property
    def interrupt(self): return self._interrupt
    def encode_image(self, image: PipelineImageInput, device: torch.device) -> torch.Tensor:
        """Returns:"""
        if not isinstance(image, torch.Tensor): image = self.feature_extractor(image, return_tensors='pt').pixel_values
        image = image.to(device=device, dtype=self.dtype)
        return self.image_encoder(image, output_hidden_states=True).hidden_states[-2]
    def prepare_ip_adapter_image_embeds(self, ip_adapter_image: Optional[PipelineImageInput]=None, ip_adapter_image_embeds: Optional[torch.Tensor]=None, device: Optional[torch.device]=None,
    num_images_per_prompt: int=1, do_classifier_free_guidance: bool=True) -> torch.Tensor:
        """Args:"""
        device = device or self._execution_device
        if ip_adapter_image_embeds is not None:
            if do_classifier_free_guidance: single_negative_image_embeds, single_image_embeds = ip_adapter_image_embeds.chunk(2)
            else: single_image_embeds = ip_adapter_image_embeds
        elif ip_adapter_image is not None:
            single_image_embeds = self.encode_image(ip_adapter_image, device)
            if do_classifier_free_guidance: single_negative_image_embeds = torch.zeros_like(single_image_embeds)
        else: raise ValueError('Neither `ip_adapter_image_embeds` or `ip_adapter_image_embeds` were provided.')
        image_embeds = torch.cat([single_image_embeds] * num_images_per_prompt, dim=0)
        if do_classifier_free_guidance:
            negative_image_embeds = torch.cat([single_negative_image_embeds] * num_images_per_prompt, dim=0)
            image_embeds = torch.cat([negative_image_embeds, image_embeds], dim=0)
        return image_embeds.to(device=device)
    def enable_sequential_cpu_offload(self, *args, **kwargs): super().enable_sequential_cpu_offload(*args, **kwargs)
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]]=None, prompt_2: Optional[Union[str, List[str]]]=None, prompt_3: Optional[Union[str, List[str]]]=None, height: Optional[int]=None,
    width: Optional[int]=None, num_inference_steps: int=28, sigmas: Optional[List[float]]=None, guidance_scale: float=7.0, negative_prompt: Optional[Union[str, List[str]]]=None,
    negative_prompt_2: Optional[Union[str, List[str]]]=None, negative_prompt_3: Optional[Union[str, List[str]]]=None, num_images_per_prompt: Optional[int]=1,
    generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.FloatTensor]=None, prompt_embeds: Optional[torch.FloatTensor]=None,
    negative_prompt_embeds: Optional[torch.FloatTensor]=None, pooled_prompt_embeds: Optional[torch.FloatTensor]=None, negative_pooled_prompt_embeds: Optional[torch.FloatTensor]=None,
    ip_adapter_image: Optional[PipelineImageInput]=None, ip_adapter_image_embeds: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', return_dict: bool=True,
    joint_attention_kwargs: Optional[Dict[str, Any]]=None, clip_skip: Optional[int]=None, callback_on_step_end: Optional[Callable[[int, int, Dict], None]]=None,
    callback_on_step_end_tensor_inputs: List[str]=['latents'], max_sequence_length: int=256, skip_guidance_layers: List[int]=None, skip_layer_guidance_scale: float=2.8,
    skip_layer_guidance_stop: float=0.2, skip_layer_guidance_start: float=0.01, mu: Optional[float]=None):
        """Examples:"""
        height = height or self.default_sample_size * self.vae_scale_factor
        width = width or self.default_sample_size * self.vae_scale_factor
        self.check_inputs(prompt, prompt_2, prompt_3, height, width, negative_prompt=negative_prompt, negative_prompt_2=negative_prompt_2, negative_prompt_3=negative_prompt_3,
        prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, pooled_prompt_embeds=pooled_prompt_embeds, negative_pooled_prompt_embeds=negative_pooled_prompt_embeds,
        callback_on_step_end_tensor_inputs=callback_on_step_end_tensor_inputs, max_sequence_length=max_sequence_length)
        self._guidance_scale = guidance_scale
        self._skip_layer_guidance_scale = skip_layer_guidance_scale
        self._clip_skip = clip_skip
        self._joint_attention_kwargs = joint_attention_kwargs
        self._interrupt = False
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        lora_scale = self.joint_attention_kwargs.get('scale', None) if self.joint_attention_kwargs is not None else None
        prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds = self.encode_prompt(prompt=prompt, prompt_2=prompt_2, prompt_3=prompt_3,
        negative_prompt=negative_prompt, negative_prompt_2=negative_prompt_2, negative_prompt_3=negative_prompt_3, do_classifier_free_guidance=self.do_classifier_free_guidance,
        prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, pooled_prompt_embeds=pooled_prompt_embeds, negative_pooled_prompt_embeds=negative_pooled_prompt_embeds,
        device=device, clip_skip=self.clip_skip, num_images_per_prompt=num_images_per_prompt, max_sequence_length=max_sequence_length, lora_scale=lora_scale)
        if self.do_classifier_free_guidance:
            if skip_guidance_layers is not None:
                original_prompt_embeds = prompt_embeds
                original_pooled_prompt_embeds = pooled_prompt_embeds
            prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds], dim=0)
            pooled_prompt_embeds = torch.cat([negative_pooled_prompt_embeds, pooled_prompt_embeds], dim=0)
        num_channels_latents = self.transformer.config.in_channels
        latents = self.prepare_latents(batch_size * num_images_per_prompt, num_channels_latents, height, width, prompt_embeds.dtype, device, generator, latents)
        scheduler_kwargs = {}
        if self.scheduler.config.get('use_dynamic_shifting', None) and mu is None:
            _, _, height, width = latents.shape
            image_seq_len = height // self.transformer.config.patch_size * (width // self.transformer.config.patch_size)
            mu = calculate_shift(image_seq_len, self.scheduler.config.base_image_seq_len, self.scheduler.config.max_image_seq_len, self.scheduler.config.base_shift, self.scheduler.config.max_shift)
            scheduler_kwargs['mu'] = mu
        elif mu is not None: scheduler_kwargs['mu'] = mu
        timesteps, num_inference_steps = retrieve_timesteps(self.scheduler, num_inference_steps, device, sigmas=sigmas, **scheduler_kwargs)
        num_warmup_steps = max(len(timesteps) - num_inference_steps * self.scheduler.order, 0)
        self._num_timesteps = len(timesteps)
        if ip_adapter_image is not None and self.is_ip_adapter_active or ip_adapter_image_embeds is not None:
            ip_adapter_image_embeds = self.prepare_ip_adapter_image_embeds(ip_adapter_image, ip_adapter_image_embeds, device, batch_size * num_images_per_prompt, self.do_classifier_free_guidance)
            if self.joint_attention_kwargs is None: self._joint_attention_kwargs = {'ip_adapter_image_embeds': ip_adapter_image_embeds}
            else: self._joint_attention_kwargs.update(ip_adapter_image_embeds=ip_adapter_image_embeds)
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                if self.interrupt: continue
                latent_model_input = torch.cat([latents] * 2) if self.do_classifier_free_guidance else latents
                timestep = t.expand(latent_model_input.shape[0])
                noise_pred = self.transformer(hidden_states=latent_model_input, timestep=timestep, encoder_hidden_states=prompt_embeds, pooled_projections=pooled_prompt_embeds,
                joint_attention_kwargs=self.joint_attention_kwargs, return_dict=False)[0]
                if self.do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + self.guidance_scale * (noise_pred_text - noise_pred_uncond)
                    should_skip_layers = True if i > num_inference_steps * skip_layer_guidance_start and i < num_inference_steps * skip_layer_guidance_stop else False
                    if skip_guidance_layers is not None and should_skip_layers:
                        timestep = t.expand(latents.shape[0])
                        latent_model_input = latents
                        noise_pred_skip_layers = self.transformer(hidden_states=latent_model_input, timestep=timestep, encoder_hidden_states=original_prompt_embeds,
                        pooled_projections=original_pooled_prompt_embeds, joint_attention_kwargs=self.joint_attention_kwargs, return_dict=False, skip_layers=skip_guidance_layers)[0]
                        noise_pred = noise_pred + (noise_pred_text - noise_pred_skip_layers) * self._skip_layer_guidance_scale
                latents_dtype = latents.dtype
                latents = self.scheduler.step(noise_pred, t, latents, return_dict=False)[0]
                if latents.dtype != latents_dtype:
                    if torch.backends.mps.is_available(): latents = latents.to(latents_dtype)
                if callback_on_step_end is not None:
                    callback_kwargs = {}
                    for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                    callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                    latents = callback_outputs.pop('latents', latents)
                    prompt_embeds = callback_outputs.pop('prompt_embeds', prompt_embeds)
                    negative_prompt_embeds = callback_outputs.pop('negative_prompt_embeds', negative_prompt_embeds)
                    negative_pooled_prompt_embeds = callback_outputs.pop('negative_pooled_prompt_embeds', negative_pooled_prompt_embeds)
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0): progress_bar.update()
                if XLA_AVAILABLE: xm.mark_step()
        if output_type == 'latent': image = latents
        else:
            latents = latents / self.vae.config.scaling_factor + self.vae.config.shift_factor
            image = self.vae.decode(latents, return_dict=False)[0]
            image = self.image_processor.postprocess(image, output_type=output_type)
        self.maybe_free_model_hooks()
        if not return_dict: return (image,)
        return SAPIImageGenPipelineOutput(images=image)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
