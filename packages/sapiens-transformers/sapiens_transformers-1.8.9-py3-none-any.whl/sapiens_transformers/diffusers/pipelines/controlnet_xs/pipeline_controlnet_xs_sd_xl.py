'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np
import PIL.Image
import torch
import torch.nn.functional as F
from sapiens_transformers import CLIPImageProcessor, CLIPTextModel, CLIPTextModelWithProjection, CLIPTokenizer
from ...utils.import_utils import is_invisible_watermark_available
from ...callbacks import MultiPipelineCallbacks, PipelineCallback
from ...image_processor import PipelineImageInput, VaeImageProcessor
from ...loaders import FromSingleFileMixin, StableDiffusionXLLoraLoaderMixin, TextualInversionLoaderMixin
from ...models import AutoencoderKL, ControlNetXSAdapter, UNet2DConditionModel, UNetControlNetXSModel
from ...models.attention_processor import AttnProcessor2_0, XFormersAttnProcessor
from ...models.lora import adjust_lora_scale_text_encoder
from ...schedulers import KarrasDiffusionSchedulers
from ...utils import USE_PEFT_BACKEND, replace_example_docstring, scale_lora_layers, unscale_lora_layers
from ...utils.torch_utils import is_compiled_module, is_torch_version, randn_tensor
from ..pipeline_utils import DiffusionPipeline
from ..stable_diffusion_xl.pipeline_output import StableDiffusionXLPipelineOutput
if is_invisible_watermark_available(): from ..stable_diffusion_xl.watermark import StableDiffusionXLWatermarker
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> # !pip install opencv-python transformers sapiens_accelerator\n        >>> from sapiens_transformers.diffusers import StableDiffusionXLControlNetXSPipeline, ControlNetXSAdapter, AutoencoderKL\n        >>> from sapiens_transformers.diffusers.utils import load_image\n        >>> import numpy as np\n        >>> import torch\n\n        >>> import cv2\n        >>> from PIL import Image\n\n        >>> prompt = "aerial view, a futuristic research complex in a bright foggy jungle, hard lighting"\n        >>> negative_prompt = "low quality, bad quality, sketches"\n\n        >>> # download an image\n        >>> image = load_image(\n        ...     "https://hf.co/datasets/hf-internal-testing/diffusers-images/resolve/main/sd_controlnet/hf-logo.png"\n        ... )\n\n        >>> # initialize the models and pipeline\n        >>> controlnet_conditioning_scale = 0.5\n        >>> vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)\n        >>> controlnet = ControlNetXSAdapter.from_pretrained(\n        ...     "UmerHA/Testing-ConrolNetXS-SDXL-canny", torch_dtype=torch.float16\n        ... )\n        >>> pipe = StableDiffusionXLControlNetXSPipeline.from_pretrained(\n        ...     "stabilityai/stable-diffusion-xl-base-1.0", controlnet=controlnet, torch_dtype=torch.float16\n        ... )\n        >>> pipe.enable_model_cpu_offload()\n\n        >>> # get canny image\n        >>> image = np.array(image)\n        >>> image = cv2.Canny(image, 100, 200)\n        >>> image = image[:, :, None]\n        >>> image = np.concatenate([image, image, image], axis=2)\n        >>> canny_image = Image.fromarray(image)\n\n        >>> # generate image\n        >>> image = pipe(\n        ...     prompt, controlnet_conditioning_scale=controlnet_conditioning_scale, image=canny_image\n        ... ).images[0]\n        ```\n'
class StableDiffusionXLControlNetXSPipeline(DiffusionPipeline, TextualInversionLoaderMixin, StableDiffusionXLLoraLoaderMixin, FromSingleFileMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->text_encoder_2->unet->vae'
    _optional_components = ['tokenizer', 'tokenizer_2', 'text_encoder', 'text_encoder_2', 'feature_extractor']
    _callback_tensor_inputs = ['latents', 'prompt_embeds', 'negative_prompt_embeds', 'add_text_embeds', 'add_time_ids', 'negative_pooled_prompt_embeds', 'negative_add_time_ids']
    def __init__(self, vae: AutoencoderKL, text_encoder: CLIPTextModel, text_encoder_2: CLIPTextModelWithProjection, tokenizer: CLIPTokenizer, tokenizer_2: CLIPTokenizer,
    unet: Union[UNet2DConditionModel, UNetControlNetXSModel], controlnet: ControlNetXSAdapter, scheduler: KarrasDiffusionSchedulers, force_zeros_for_empty_prompt: bool=True,
    add_watermarker: Optional[bool]=None, feature_extractor: CLIPImageProcessor=None):
        super().__init__()
        if isinstance(unet, UNet2DConditionModel): unet = UNetControlNetXSModel.from_unet(unet, controlnet)
        self.register_modules(vae=vae, text_encoder=text_encoder, text_encoder_2=text_encoder_2, tokenizer=tokenizer, tokenizer_2=tokenizer_2, unet=unet,
        controlnet=controlnet, scheduler=scheduler, feature_extractor=feature_extractor)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor, do_convert_rgb=True)
        self.control_image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor, do_convert_rgb=True, do_normalize=False)
        add_watermarker = add_watermarker if add_watermarker is not None else is_invisible_watermark_available()
        if add_watermarker: self.watermark = StableDiffusionXLWatermarker()
        else: self.watermark = None
        self.register_to_config(force_zeros_for_empty_prompt=force_zeros_for_empty_prompt)
    def encode_prompt(self, prompt: str, prompt_2: Optional[str]=None, device: Optional[torch.device]=None, num_images_per_prompt: int=1, do_classifier_free_guidance: bool=True,
    negative_prompt: Optional[str]=None, negative_prompt_2: Optional[str]=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None,
    pooled_prompt_embeds: Optional[torch.Tensor]=None, negative_pooled_prompt_embeds: Optional[torch.Tensor]=None, lora_scale: Optional[float]=None, clip_skip: Optional[int]=None):
        """Args:"""
        device = device or self._execution_device
        if lora_scale is not None and isinstance(self, StableDiffusionXLLoraLoaderMixin):
            self._lora_scale = lora_scale
            if self.text_encoder is not None:
                if not USE_PEFT_BACKEND: adjust_lora_scale_text_encoder(self.text_encoder, lora_scale)
                else: scale_lora_layers(self.text_encoder, lora_scale)
            if self.text_encoder_2 is not None:
                if not USE_PEFT_BACKEND: adjust_lora_scale_text_encoder(self.text_encoder_2, lora_scale)
                else: scale_lora_layers(self.text_encoder_2, lora_scale)
        prompt = [prompt] if isinstance(prompt, str) else prompt
        if prompt is not None: batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        tokenizers = [self.tokenizer, self.tokenizer_2] if self.tokenizer is not None else [self.tokenizer_2]
        text_encoders = [self.text_encoder, self.text_encoder_2] if self.text_encoder is not None else [self.text_encoder_2]
        if prompt_embeds is None:
            prompt_2 = prompt_2 or prompt
            prompt_2 = [prompt_2] if isinstance(prompt_2, str) else prompt_2
            prompt_embeds_list = []
            prompts = [prompt, prompt_2]
            for prompt, tokenizer, text_encoder in zip(prompts, tokenizers, text_encoders):
                if isinstance(self, TextualInversionLoaderMixin): prompt = self.maybe_convert_prompt(prompt, tokenizer)
                text_inputs = tokenizer(prompt, padding='max_length', max_length=tokenizer.model_max_length, truncation=True, return_tensors='pt')
                text_input_ids = text_inputs.input_ids
                untruncated_ids = tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
                if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = tokenizer.batch_decode(untruncated_ids[:, tokenizer.model_max_length - 1:-1])
                prompt_embeds = text_encoder(text_input_ids.to(device), output_hidden_states=True)
                pooled_prompt_embeds = prompt_embeds[0]
                if clip_skip is None: prompt_embeds = prompt_embeds.hidden_states[-2]
                else: prompt_embeds = prompt_embeds.hidden_states[-(clip_skip + 2)]
                prompt_embeds_list.append(prompt_embeds)
            prompt_embeds = torch.concat(prompt_embeds_list, dim=-1)
        zero_out_negative_prompt = negative_prompt is None and self.config.force_zeros_for_empty_prompt
        if do_classifier_free_guidance and negative_prompt_embeds is None and zero_out_negative_prompt:
            negative_prompt_embeds = torch.zeros_like(prompt_embeds)
            negative_pooled_prompt_embeds = torch.zeros_like(pooled_prompt_embeds)
        elif do_classifier_free_guidance and negative_prompt_embeds is None:
            negative_prompt = negative_prompt or ''
            negative_prompt_2 = negative_prompt_2 or negative_prompt
            negative_prompt = batch_size * [negative_prompt] if isinstance(negative_prompt, str) else negative_prompt
            negative_prompt_2 = batch_size * [negative_prompt_2] if isinstance(negative_prompt_2, str) else negative_prompt_2
            uncond_tokens: List[str]
            if prompt is not None and type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            else: uncond_tokens = [negative_prompt, negative_prompt_2]
            negative_prompt_embeds_list = []
            for negative_prompt, tokenizer, text_encoder in zip(uncond_tokens, tokenizers, text_encoders):
                if isinstance(self, TextualInversionLoaderMixin): negative_prompt = self.maybe_convert_prompt(negative_prompt, tokenizer)
                max_length = prompt_embeds.shape[1]
                uncond_input = tokenizer(negative_prompt, padding='max_length', max_length=max_length, truncation=True, return_tensors='pt')
                negative_prompt_embeds = text_encoder(uncond_input.input_ids.to(device), output_hidden_states=True)
                negative_pooled_prompt_embeds = negative_prompt_embeds[0]
                negative_prompt_embeds = negative_prompt_embeds.hidden_states[-2]
                negative_prompt_embeds_list.append(negative_prompt_embeds)
            negative_prompt_embeds = torch.concat(negative_prompt_embeds_list, dim=-1)
        if self.text_encoder_2 is not None: prompt_embeds = prompt_embeds.to(dtype=self.text_encoder_2.dtype, device=device)
        else: prompt_embeds = prompt_embeds.to(dtype=self.unet.dtype, device=device)
        bs_embed, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_images_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(bs_embed * num_images_per_prompt, seq_len, -1)
        if do_classifier_free_guidance:
            seq_len = negative_prompt_embeds.shape[1]
            if self.text_encoder_2 is not None: negative_prompt_embeds = negative_prompt_embeds.to(dtype=self.text_encoder_2.dtype, device=device)
            else: negative_prompt_embeds = negative_prompt_embeds.to(dtype=self.unet.dtype, device=device)
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt, 1)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
        pooled_prompt_embeds = pooled_prompt_embeds.repeat(1, num_images_per_prompt).view(bs_embed * num_images_per_prompt, -1)
        if do_classifier_free_guidance: negative_pooled_prompt_embeds = negative_pooled_prompt_embeds.repeat(1, num_images_per_prompt).view(bs_embed * num_images_per_prompt, -1)
        if self.text_encoder is not None:
            if isinstance(self, StableDiffusionXLLoraLoaderMixin) and USE_PEFT_BACKEND: unscale_lora_layers(self.text_encoder, lora_scale)
        if self.text_encoder_2 is not None:
            if isinstance(self, StableDiffusionXLLoraLoaderMixin) and USE_PEFT_BACKEND: unscale_lora_layers(self.text_encoder_2, lora_scale)
        return (prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds)
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, prompt, prompt_2, image, negative_prompt=None, negative_prompt_2=None, prompt_embeds=None, negative_prompt_embeds=None, pooled_prompt_embeds=None,
    negative_pooled_prompt_embeds=None, controlnet_conditioning_scale=1.0, control_guidance_start=0.0, control_guidance_end=1.0, callback_on_step_end_tensor_inputs=None):
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt_2 is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt_2`: {prompt_2} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        elif prompt_2 is not None and (not isinstance(prompt_2, str) and (not isinstance(prompt_2, list))): raise ValueError(f'`prompt_2` has to be of type `str` or `list` but is {type(prompt_2)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        elif negative_prompt_2 is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt_2`: {negative_prompt_2} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
        if prompt_embeds is not None and pooled_prompt_embeds is None: raise ValueError('If `prompt_embeds` are provided, `pooled_prompt_embeds` also have to be passed. Make sure to generate `pooled_prompt_embeds` from the same text encoder that was used to generate `prompt_embeds`.')
        if negative_prompt_embeds is not None and negative_pooled_prompt_embeds is None: raise ValueError('If `negative_prompt_embeds` are provided, `negative_pooled_prompt_embeds` also have to be passed. Make sure to generate `negative_pooled_prompt_embeds` from the same text encoder that was used to generate `negative_prompt_embeds`.')
        is_compiled = hasattr(F, 'scaled_dot_product_attention') and isinstance(self.unet, torch._dynamo.eval_frame.OptimizedModule)
        if isinstance(self.unet, UNetControlNetXSModel) or (is_compiled and isinstance(self.unet._orig_mod, UNetControlNetXSModel)):
            self.check_image(image, prompt, prompt_embeds)
            if not isinstance(controlnet_conditioning_scale, float): raise TypeError('For single controlnet: `controlnet_conditioning_scale` must be type `float`.')
        else: assert False
        start, end = (control_guidance_start, control_guidance_end)
        if start >= end: raise ValueError(f'control guidance start: {start} cannot be larger or equal to control guidance end: {end}.')
        if start < 0.0: raise ValueError(f"control guidance start: {start} can't be smaller than 0.")
        if end > 1.0: raise ValueError(f"control guidance end: {end} can't be larger than 1.0.")
    def check_image(self, image, prompt, prompt_embeds):
        image_is_pil = isinstance(image, PIL.Image.Image)
        image_is_tensor = isinstance(image, torch.Tensor)
        image_is_np = isinstance(image, np.ndarray)
        image_is_pil_list = isinstance(image, list) and isinstance(image[0], PIL.Image.Image)
        image_is_tensor_list = isinstance(image, list) and isinstance(image[0], torch.Tensor)
        image_is_np_list = isinstance(image, list) and isinstance(image[0], np.ndarray)
        if not image_is_pil and (not image_is_tensor) and (not image_is_np) and (not image_is_pil_list) and (not image_is_tensor_list) and (not image_is_np_list): raise TypeError(f'image must be passed and be one of PIL image, numpy array, torch tensor, list of PIL images, list of numpy arrays or list of torch tensors, but is {type(image)}')
        if image_is_pil: image_batch_size = 1
        else: image_batch_size = len(image)
        if prompt is not None and isinstance(prompt, str): prompt_batch_size = 1
        elif prompt is not None and isinstance(prompt, list): prompt_batch_size = len(prompt)
        elif prompt_embeds is not None: prompt_batch_size = prompt_embeds.shape[0]
        if image_batch_size != 1 and image_batch_size != prompt_batch_size: raise ValueError(f'If image batch size is not 1, image batch size must be same as prompt batch size. image batch size: {image_batch_size}, prompt batch size: {prompt_batch_size}')
    def prepare_image(self, image, width, height, batch_size, num_images_per_prompt, device, dtype, do_classifier_free_guidance=False):
        image = self.control_image_processor.preprocess(image, height=height, width=width).to(dtype=torch.float32)
        image_batch_size = image.shape[0]
        if image_batch_size == 1: repeat_by = batch_size
        else: repeat_by = num_images_per_prompt
        image = image.repeat_interleave(repeat_by, dim=0)
        image = image.to(device=device, dtype=dtype)
        if do_classifier_free_guidance: image = torch.cat([image] * 2)
        return image
    def prepare_latents(self, batch_size, num_channels_latents, height, width, dtype, device, generator, latents=None):
        shape = (batch_size, num_channels_latents, int(height) // self.vae_scale_factor, int(width) // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else: latents = latents.to(device)
        latents = latents * self.scheduler.init_noise_sigma
        return latents
    def _get_add_time_ids(self, original_size, crops_coords_top_left, target_size, dtype, text_encoder_projection_dim=None):
        add_time_ids = list(original_size + crops_coords_top_left + target_size)
        passed_add_embed_dim = self.unet.config.addition_time_embed_dim * len(add_time_ids) + text_encoder_projection_dim
        expected_add_embed_dim = self.unet.base_add_embedding.linear_1.in_features
        if expected_add_embed_dim != passed_add_embed_dim: raise ValueError(f'Model expects an added time embedding vector of length {expected_add_embed_dim}, but a vector of {passed_add_embed_dim} was created. The model has an incorrect config. Please check `unet.config.time_embedding_type` and `text_encoder_2.config.projection_dim`.')
        add_time_ids = torch.tensor([add_time_ids], dtype=dtype)
        return add_time_ids
    def upcast_vae(self):
        dtype = self.vae.dtype
        self.vae.to(dtype=torch.float32)
        use_torch_2_0_or_xformers = isinstance(self.vae.decoder.mid_block.attentions[0].processor, (AttnProcessor2_0, XFormersAttnProcessor))
        if use_torch_2_0_or_xformers:
            self.vae.post_quant_conv.to(dtype)
            self.vae.decoder.conv_in.to(dtype)
            self.vae.decoder.mid_block.to(dtype)
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def clip_skip(self): return self._clip_skip
    @property
    def do_classifier_free_guidance(self): return self._guidance_scale > 1 and self.unet.config.time_cond_proj_dim is None
    @property
    def cross_attention_kwargs(self): return self._cross_attention_kwargs
    @property
    def num_timesteps(self): return self._num_timesteps
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]]=None, prompt_2: Optional[Union[str, List[str]]]=None, image: PipelineImageInput=None, height: Optional[int]=None, width: Optional[int]=None,
    num_inference_steps: int=50, guidance_scale: float=5.0, negative_prompt: Optional[Union[str, List[str]]]=None, negative_prompt_2: Optional[Union[str, List[str]]]=None,
    num_images_per_prompt: Optional[int]=1, eta: float=0.0, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None,
    prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, pooled_prompt_embeds: Optional[torch.Tensor]=None,
    negative_pooled_prompt_embeds: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', return_dict: bool=True, cross_attention_kwargs: Optional[Dict[str, Any]]=None,
    controlnet_conditioning_scale: Union[float, List[float]]=1.0, control_guidance_start: float=0.0, control_guidance_end: float=1.0, original_size: Tuple[int, int]=None,
    crops_coords_top_left: Tuple[int, int]=(0, 0), target_size: Tuple[int, int]=None, negative_original_size: Optional[Tuple[int, int]]=None, negative_crops_coords_top_left: Tuple[int, int]=(0, 0),
    negative_target_size: Optional[Tuple[int, int]]=None, clip_skip: Optional[int]=None, callback_on_step_end: Optional[Union[Callable[[int, int, Dict], None],
    PipelineCallback, MultiPipelineCallbacks]]=None, callback_on_step_end_tensor_inputs: List[str]=['latents']):
        """Examples:"""
        if isinstance(callback_on_step_end, (PipelineCallback, MultiPipelineCallbacks)): callback_on_step_end_tensor_inputs = callback_on_step_end.tensor_inputs
        unet = self.unet._orig_mod if is_compiled_module(self.unet) else self.unet
        self.check_inputs(prompt, prompt_2, image, negative_prompt, negative_prompt_2, prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds,
        controlnet_conditioning_scale, control_guidance_start, control_guidance_end, callback_on_step_end_tensor_inputs)
        self._guidance_scale = guidance_scale
        self._clip_skip = clip_skip
        self._cross_attention_kwargs = cross_attention_kwargs
        self._interrupt = False
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        text_encoder_lora_scale = cross_attention_kwargs.get('scale', None) if cross_attention_kwargs is not None else None
        prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds = self.encode_prompt(prompt, prompt_2, device, num_images_per_prompt, do_classifier_free_guidance,
        negative_prompt, negative_prompt_2, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, pooled_prompt_embeds=pooled_prompt_embeds,
        negative_pooled_prompt_embeds=negative_pooled_prompt_embeds, lora_scale=text_encoder_lora_scale, clip_skip=clip_skip)
        if isinstance(unet, UNetControlNetXSModel):
            image = self.prepare_image(image=image, width=width, height=height, batch_size=batch_size * num_images_per_prompt, num_images_per_prompt=num_images_per_prompt,
            device=device, dtype=unet.dtype, do_classifier_free_guidance=do_classifier_free_guidance)
            height, width = image.shape[-2:]
        else: assert False
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps
        num_channels_latents = self.unet.in_channels
        latents = self.prepare_latents(batch_size * num_images_per_prompt, num_channels_latents, height, width, prompt_embeds.dtype, device, generator, latents)
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        if isinstance(image, list): original_size = original_size or image[0].shape[-2:]
        else: original_size = original_size or image.shape[-2:]
        target_size = target_size or (height, width)
        add_text_embeds = pooled_prompt_embeds
        if self.text_encoder_2 is None: text_encoder_projection_dim = int(pooled_prompt_embeds.shape[-1])
        else: text_encoder_projection_dim = self.text_encoder_2.config.projection_dim
        add_time_ids = self._get_add_time_ids(original_size, crops_coords_top_left, target_size, dtype=prompt_embeds.dtype, text_encoder_projection_dim=text_encoder_projection_dim)
        if negative_original_size is not None and negative_target_size is not None: negative_add_time_ids = self._get_add_time_ids(negative_original_size, negative_crops_coords_top_left,
        negative_target_size, dtype=prompt_embeds.dtype, text_encoder_projection_dim=text_encoder_projection_dim)
        else: negative_add_time_ids = add_time_ids
        if do_classifier_free_guidance:
            prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds], dim=0)
            add_text_embeds = torch.cat([negative_pooled_prompt_embeds, add_text_embeds], dim=0)
            add_time_ids = torch.cat([negative_add_time_ids, add_time_ids], dim=0)
        prompt_embeds = prompt_embeds.to(device)
        add_text_embeds = add_text_embeds.to(device)
        add_time_ids = add_time_ids.to(device).repeat(batch_size * num_images_per_prompt, 1)
        num_warmup_steps = len(timesteps) - num_inference_steps * self.scheduler.order
        self._num_timesteps = len(timesteps)
        is_controlnet_compiled = is_compiled_module(self.unet)
        is_torch_higher_equal_2_1 = is_torch_version('>=', '2.1')
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                if is_controlnet_compiled and is_torch_higher_equal_2_1: torch._inductor.cudagraph_mark_step_begin()
                latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                added_cond_kwargs = {'text_embeds': add_text_embeds, 'time_ids': add_time_ids}
                apply_control = i / len(timesteps) >= control_guidance_start and (i + 1) / len(timesteps) <= control_guidance_end
                noise_pred = self.unet(sample=latent_model_input, timestep=t, encoder_hidden_states=prompt_embeds, controlnet_cond=image, conditioning_scale=controlnet_conditioning_scale,
                cross_attention_kwargs=cross_attention_kwargs, added_cond_kwargs=added_cond_kwargs, return_dict=True, apply_control=apply_control).sample
                if do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs, return_dict=False)[0]
                if callback_on_step_end is not None:
                    callback_kwargs = {}
                    for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                    callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                    latents = callback_outputs.pop('latents', latents)
                    prompt_embeds = callback_outputs.pop('prompt_embeds', prompt_embeds)
                    negative_prompt_embeds = callback_outputs.pop('negative_prompt_embeds', negative_prompt_embeds)
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0): progress_bar.update()
        if self.vae.dtype == torch.float16 and self.vae.config.force_upcast:
            self.upcast_vae()
            latents = latents.to(next(iter(self.vae.post_quant_conv.parameters())).dtype)
        if not output_type == 'latent':
            needs_upcasting = self.vae.dtype == torch.float16 and self.vae.config.force_upcast
            if needs_upcasting:
                self.upcast_vae()
                latents = latents.to(next(iter(self.vae.post_quant_conv.parameters())).dtype)
            image = self.vae.decode(latents / self.vae.config.scaling_factor, return_dict=False)[0]
            if needs_upcasting: self.vae.to(dtype=torch.float16)
        else: image = latents
        if not output_type == 'latent':
            if self.watermark is not None: image = self.watermark.apply_watermark(image)
            image = self.image_processor.postprocess(image, output_type=output_type)
        self.maybe_free_model_hooks()
        if not return_dict: return (image,)
        return StableDiffusionXLPipelineOutput(images=image)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
