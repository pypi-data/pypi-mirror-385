'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import PIL.Image
import torch
from sapiens_transformers import CLIPImageProcessor, CLIPVisionModelWithProjection
from ...callbacks import MultiPipelineCallbacks, PipelineCallback
from ...image_processor import PipelineImageInput, VaeImageProcessor
from ...loaders import IPAdapterMixin, StableDiffusionXLLoraLoaderMixin
from ...models import AutoencoderKL, ImageProjection, UNet2DConditionModel
from ...models.attention_processor import AttnProcessor2_0, FusedAttnProcessor2_0, XFormersAttnProcessor
from ...schedulers import KarrasDiffusionSchedulers
from ...utils import is_torch_xla_available, replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, StableDiffusionMixin
from .pipeline_output import KolorsPipelineOutput
from .text_encoder import ChatGLMModel
from .tokenizer import ChatGLMTokenizer
if is_torch_xla_available():
    import torch_xla.core.xla_model as xm
    XLA_AVAILABLE = True
else: XLA_AVAILABLE = False
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import KolorsImg2ImgPipeline\n        >>> from sapiens_transformers.diffusers.utils import load_image\n\n        >>> pipe = KolorsImg2ImgPipeline.from_pretrained(\n        ...     "Kwai-Kolors/Kolors-diffusers", variant="fp16", torch_dtype=torch.float16\n        ... )\n        >>> pipe = pipe.to("cuda")\n        >>> url = (\n        ...     "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/kolors/bunny_source.png"\n        ... )\n\n\n        >>> init_image = load_image(url)\n        >>> prompt = "high quality image of a capybara wearing sunglasses. In the background of the image there are trees, poles, grass and other objects. At the bottom of the object there is the road., 8k, highly detailed."\n        >>> image = pipe(prompt, image=init_image).images[0]\n        ```\n'
def retrieve_latents(encoder_output: torch.Tensor, generator: Optional[torch.Generator]=None, sample_mode: str='sample'):
    if hasattr(encoder_output, 'latent_dist') and sample_mode == 'sample': return encoder_output.latent_dist.sample(generator)
    elif hasattr(encoder_output, 'latent_dist') and sample_mode == 'argmax': return encoder_output.latent_dist.mode()
    elif hasattr(encoder_output, 'latents'): return encoder_output.latents
    else: raise AttributeError('Could not access latents of provided encoder_output')
def retrieve_timesteps(scheduler, num_inference_steps: Optional[int]=None, device: Optional[Union[str, torch.device]]=None, timesteps: Optional[List[int]]=None, sigmas: Optional[List[float]]=None, **kwargs):
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
class KolorsImg2ImgPipeline(DiffusionPipeline, StableDiffusionMixin, StableDiffusionXLLoraLoaderMixin, IPAdapterMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->image_encoder-unet->vae'
    _optional_components = ['image_encoder', 'feature_extractor']
    _callback_tensor_inputs = ['latents', 'prompt_embeds', 'negative_prompt_embeds', 'add_text_embeds', 'add_time_ids', 'negative_pooled_prompt_embeds', 'negative_add_time_ids']
    def __init__(self, vae: AutoencoderKL, text_encoder: ChatGLMModel, tokenizer: ChatGLMTokenizer, unet: UNet2DConditionModel, scheduler: KarrasDiffusionSchedulers,
    image_encoder: CLIPVisionModelWithProjection=None, feature_extractor: CLIPImageProcessor=None, force_zeros_for_empty_prompt: bool=False):
        super().__init__()
        self.register_modules(vae=vae, text_encoder=text_encoder, tokenizer=tokenizer, unet=unet, scheduler=scheduler, image_encoder=image_encoder, feature_extractor=feature_extractor)
        self.register_to_config(force_zeros_for_empty_prompt=force_zeros_for_empty_prompt)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1) if hasattr(self, 'vae') and self.vae is not None else 8
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor)
        self.default_sample_size = self.unet.config.sample_size
    def encode_prompt(self, prompt, device: Optional[torch.device]=None, num_images_per_prompt: int=1, do_classifier_free_guidance: bool=True, negative_prompt=None,
    prompt_embeds: Optional[torch.FloatTensor]=None, pooled_prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.FloatTensor]=None,
    negative_pooled_prompt_embeds: Optional[torch.Tensor]=None, max_sequence_length: int=256):
        """Args:"""
        device = device or self._execution_device
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        tokenizers = [self.tokenizer]
        text_encoders = [self.text_encoder]
        if prompt_embeds is None:
            prompt_embeds_list = []
            for tokenizer, text_encoder in zip(tokenizers, text_encoders):
                text_inputs = tokenizer(prompt, padding='max_length', max_length=max_sequence_length, truncation=True, return_tensors='pt').to(device)
                output = text_encoder(input_ids=text_inputs['input_ids'], attention_mask=text_inputs['attention_mask'], position_ids=text_inputs['position_ids'], output_hidden_states=True)
                prompt_embeds = output.hidden_states[-2].permute(1, 0, 2).clone()
                pooled_prompt_embeds = output.hidden_states[-1][-1, :, :].clone()
                bs_embed, seq_len, _ = prompt_embeds.shape
                prompt_embeds = prompt_embeds.repeat(1, num_images_per_prompt, 1)
                prompt_embeds = prompt_embeds.view(bs_embed * num_images_per_prompt, seq_len, -1)
                prompt_embeds_list.append(prompt_embeds)
            prompt_embeds = prompt_embeds_list[0]
        zero_out_negative_prompt = negative_prompt is None and self.config.force_zeros_for_empty_prompt
        if do_classifier_free_guidance and negative_prompt_embeds is None and zero_out_negative_prompt: negative_prompt_embeds = torch.zeros_like(prompt_embeds)
        elif do_classifier_free_guidance and negative_prompt_embeds is None:
            uncond_tokens: List[str]
            if negative_prompt is None: uncond_tokens = [''] * batch_size
            elif prompt is not None and type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif isinstance(negative_prompt, str): uncond_tokens = [negative_prompt]
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            else: uncond_tokens = negative_prompt
            negative_prompt_embeds_list = []
            for tokenizer, text_encoder in zip(tokenizers, text_encoders):
                uncond_input = tokenizer(uncond_tokens, padding='max_length', max_length=max_sequence_length, truncation=True, return_tensors='pt').to(device)
                output = text_encoder(input_ids=uncond_input['input_ids'], attention_mask=uncond_input['attention_mask'], position_ids=uncond_input['position_ids'], output_hidden_states=True)
                negative_prompt_embeds = output.hidden_states[-2].permute(1, 0, 2).clone()
                negative_pooled_prompt_embeds = output.hidden_states[-1][-1, :, :].clone()
                if do_classifier_free_guidance:
                    seq_len = negative_prompt_embeds.shape[1]
                    negative_prompt_embeds = negative_prompt_embeds.to(dtype=text_encoder.dtype, device=device)
                    negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt, 1)
                    negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
                negative_prompt_embeds_list.append(negative_prompt_embeds)
            negative_prompt_embeds = negative_prompt_embeds_list[0]
        bs_embed = pooled_prompt_embeds.shape[0]
        pooled_prompt_embeds = pooled_prompt_embeds.repeat(1, num_images_per_prompt).view(bs_embed * num_images_per_prompt, -1)
        if do_classifier_free_guidance: negative_pooled_prompt_embeds = negative_pooled_prompt_embeds.repeat(1, num_images_per_prompt).view(bs_embed * num_images_per_prompt, -1)
        return (prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds)
    def encode_image(self, image, device, num_images_per_prompt, output_hidden_states=None):
        dtype = next(self.image_encoder.parameters()).dtype
        if not isinstance(image, torch.Tensor): image = self.feature_extractor(image, return_tensors='pt').pixel_values
        image = image.to(device=device, dtype=dtype)
        if output_hidden_states:
            image_enc_hidden_states = self.image_encoder(image, output_hidden_states=True).hidden_states[-2]
            image_enc_hidden_states = image_enc_hidden_states.repeat_interleave(num_images_per_prompt, dim=0)
            uncond_image_enc_hidden_states = self.image_encoder(torch.zeros_like(image), output_hidden_states=True).hidden_states[-2]
            uncond_image_enc_hidden_states = uncond_image_enc_hidden_states.repeat_interleave(num_images_per_prompt, dim=0)
            return (image_enc_hidden_states, uncond_image_enc_hidden_states)
        else:
            image_embeds = self.image_encoder(image).image_embeds
            image_embeds = image_embeds.repeat_interleave(num_images_per_prompt, dim=0)
            uncond_image_embeds = torch.zeros_like(image_embeds)
            return (image_embeds, uncond_image_embeds)
    def prepare_ip_adapter_image_embeds(self, ip_adapter_image, ip_adapter_image_embeds, device, num_images_per_prompt, do_classifier_free_guidance):
        image_embeds = []
        if do_classifier_free_guidance: negative_image_embeds = []
        if ip_adapter_image_embeds is None:
            if not isinstance(ip_adapter_image, list): ip_adapter_image = [ip_adapter_image]
            if len(ip_adapter_image) != len(self.unet.encoder_hid_proj.image_projection_layers): raise ValueError(f'`ip_adapter_image` must have same length as the number of IP Adapters. Got {len(ip_adapter_image)} images and {len(self.unet.encoder_hid_proj.image_projection_layers)} IP Adapters.')
            for single_ip_adapter_image, image_proj_layer in zip(ip_adapter_image, self.unet.encoder_hid_proj.image_projection_layers):
                output_hidden_state = not isinstance(image_proj_layer, ImageProjection)
                single_image_embeds, single_negative_image_embeds = self.encode_image(single_ip_adapter_image, device, 1, output_hidden_state)
                image_embeds.append(single_image_embeds[None, :])
                if do_classifier_free_guidance: negative_image_embeds.append(single_negative_image_embeds[None, :])
        else:
            for single_image_embeds in ip_adapter_image_embeds:
                if do_classifier_free_guidance:
                    single_negative_image_embeds, single_image_embeds = single_image_embeds.chunk(2)
                    negative_image_embeds.append(single_negative_image_embeds)
                image_embeds.append(single_image_embeds)
        ip_adapter_image_embeds = []
        for i, single_image_embeds in enumerate(image_embeds):
            single_image_embeds = torch.cat([single_image_embeds] * num_images_per_prompt, dim=0)
            if do_classifier_free_guidance:
                single_negative_image_embeds = torch.cat([negative_image_embeds[i]] * num_images_per_prompt, dim=0)
                single_image_embeds = torch.cat([single_negative_image_embeds, single_image_embeds], dim=0)
            single_image_embeds = single_image_embeds.to(device=device)
            ip_adapter_image_embeds.append(single_image_embeds)
        return ip_adapter_image_embeds
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, prompt, strength, num_inference_steps, height, width, negative_prompt=None, prompt_embeds=None, pooled_prompt_embeds=None,
    negative_prompt_embeds=None, negative_pooled_prompt_embeds=None, ip_adapter_image=None, ip_adapter_image_embeds=None,
    callback_on_step_end_tensor_inputs=None, max_sequence_length=None):
        if strength < 0 or strength > 1: raise ValueError(f'The value of strength should in [0.0, 1.0] but is {strength}')
        if not isinstance(num_inference_steps, int) or num_inference_steps <= 0: raise ValueError(f'`num_inference_steps` has to be a positive integer but is {num_inference_steps} of type {type(num_inference_steps)}.')
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
        if prompt_embeds is not None and pooled_prompt_embeds is None: raise ValueError('If `prompt_embeds` are provided, `pooled_prompt_embeds` also have to be passed. Make sure to generate `pooled_prompt_embeds` from the same text encoder that was used to generate `prompt_embeds`.')
        if negative_prompt_embeds is not None and negative_pooled_prompt_embeds is None: raise ValueError('If `negative_prompt_embeds` are provided, `negative_pooled_prompt_embeds` also have to be passed. Make sure to generate `negative_pooled_prompt_embeds` from the same text encoder that was used to generate `negative_prompt_embeds`.')
        if ip_adapter_image is not None and ip_adapter_image_embeds is not None: raise ValueError('Provide either `ip_adapter_image` or `ip_adapter_image_embeds`. Cannot leave both `ip_adapter_image` and `ip_adapter_image_embeds` defined.')
        if ip_adapter_image_embeds is not None:
            if not isinstance(ip_adapter_image_embeds, list): raise ValueError(f'`ip_adapter_image_embeds` has to be of type `list` but is {type(ip_adapter_image_embeds)}')
            elif ip_adapter_image_embeds[0].ndim not in [3, 4]: raise ValueError(f'`ip_adapter_image_embeds` has to be a list of 3D or 4D tensors but is {ip_adapter_image_embeds[0].ndim}D')
        if max_sequence_length is not None and max_sequence_length > 256: raise ValueError(f'`max_sequence_length` cannot be greater than 256 but is {max_sequence_length}')
    def get_timesteps(self, num_inference_steps, strength, device, denoising_start=None):
        if denoising_start is None:
            init_timestep = min(int(num_inference_steps * strength), num_inference_steps)
            t_start = max(num_inference_steps - init_timestep, 0)
            timesteps = self.scheduler.timesteps[t_start * self.scheduler.order:]
            if hasattr(self.scheduler, 'set_begin_index'): self.scheduler.set_begin_index(t_start * self.scheduler.order)
            return (timesteps, num_inference_steps - t_start)
        else:
            discrete_timestep_cutoff = int(round(self.scheduler.config.num_train_timesteps - denoising_start * self.scheduler.config.num_train_timesteps))
            num_inference_steps = (self.scheduler.timesteps < discrete_timestep_cutoff).sum().item()
            if self.scheduler.order == 2 and num_inference_steps % 2 == 0: num_inference_steps = num_inference_steps + 1
            t_start = len(self.scheduler.timesteps) - num_inference_steps
            timesteps = self.scheduler.timesteps[t_start:]
            if hasattr(self.scheduler, 'set_begin_index'): self.scheduler.set_begin_index(t_start)
            return (timesteps, num_inference_steps)
    def prepare_latents(self, image, timestep, batch_size, num_images_per_prompt, dtype, device, generator=None, add_noise=True):
        if not isinstance(image, (torch.Tensor, PIL.Image.Image, list)): raise ValueError(f'`image` has to be of type `torch.Tensor`, `PIL.Image.Image` or list but is {type(image)}')
        latents_mean = latents_std = None
        if hasattr(self.vae.config, 'latents_mean') and self.vae.config.latents_mean is not None: latents_mean = torch.tensor(self.vae.config.latents_mean).view(1, 4, 1, 1)
        if hasattr(self.vae.config, 'latents_std') and self.vae.config.latents_std is not None: latents_std = torch.tensor(self.vae.config.latents_std).view(1, 4, 1, 1)
        if hasattr(self, 'final_offload_hook') and self.final_offload_hook is not None:
            self.text_encoder_2.to('cpu')
            torch.cuda.empty_cache()
        image = image.to(device=device, dtype=dtype)
        batch_size = batch_size * num_images_per_prompt
        if image.shape[1] == 4: init_latents = image
        else:
            if self.vae.config.force_upcast:
                image = image.float()
                self.vae.to(dtype=torch.float32)
            if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
            elif isinstance(generator, list):
                if image.shape[0] < batch_size and batch_size % image.shape[0] == 0: image = torch.cat([image] * (batch_size // image.shape[0]), dim=0)
                elif image.shape[0] < batch_size and batch_size % image.shape[0] != 0: raise ValueError(f'Cannot duplicate `image` of batch size {image.shape[0]} to effective batch_size {batch_size} ')
                init_latents = [retrieve_latents(self.vae.encode(image[i:i + 1]), generator=generator[i]) for i in range(batch_size)]
                init_latents = torch.cat(init_latents, dim=0)
            else: init_latents = retrieve_latents(self.vae.encode(image), generator=generator)
            if self.vae.config.force_upcast: self.vae.to(dtype)
            init_latents = init_latents.to(dtype)
            if latents_mean is not None and latents_std is not None:
                latents_mean = latents_mean.to(device=device, dtype=dtype)
                latents_std = latents_std.to(device=device, dtype=dtype)
                init_latents = (init_latents - latents_mean) * self.vae.config.scaling_factor / latents_std
            else: init_latents = self.vae.config.scaling_factor * init_latents
        if batch_size > init_latents.shape[0] and batch_size % init_latents.shape[0] == 0:
            additional_image_per_prompt = batch_size // init_latents.shape[0]
            init_latents = torch.cat([init_latents] * additional_image_per_prompt, dim=0)
        elif batch_size > init_latents.shape[0] and batch_size % init_latents.shape[0] != 0: raise ValueError(f'Cannot duplicate `image` of batch size {init_latents.shape[0]} to {batch_size} text prompts.')
        else: init_latents = torch.cat([init_latents], dim=0)
        if add_noise:
            shape = init_latents.shape
            noise = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
            init_latents = self.scheduler.add_noise(init_latents, noise, timestep)
        latents = init_latents
        return latents
    def _get_add_time_ids(self, original_size, crops_coords_top_left, target_size, dtype, text_encoder_projection_dim=None):
        add_time_ids = list(original_size + crops_coords_top_left + target_size)
        passed_add_embed_dim = self.unet.config.addition_time_embed_dim * len(add_time_ids) + text_encoder_projection_dim
        expected_add_embed_dim = self.unet.add_embedding.linear_1.in_features
        if expected_add_embed_dim != passed_add_embed_dim: raise ValueError(f'Model expects an added time embedding vector of length {expected_add_embed_dim}, but a vector of {passed_add_embed_dim} was created. The model has an incorrect config. Please check `unet.config.time_embedding_type` and `text_encoder_2.config.projection_dim`.')
        add_time_ids = torch.tensor([add_time_ids], dtype=dtype)
        return add_time_ids
    def upcast_vae(self):
        dtype = self.vae.dtype
        self.vae.to(dtype=torch.float32)
        use_torch_2_0_or_xformers = isinstance(self.vae.decoder.mid_block.attentions[0].processor, (AttnProcessor2_0, XFormersAttnProcessor, FusedAttnProcessor2_0))
        if use_torch_2_0_or_xformers:
            self.vae.post_quant_conv.to(dtype)
            self.vae.decoder.conv_in.to(dtype)
            self.vae.decoder.mid_block.to(dtype)
    def get_guidance_scale_embedding(self, w: torch.Tensor, embedding_dim: int=512, dtype: torch.dtype=torch.float32) -> torch.Tensor:
        """Returns:"""
        assert len(w.shape) == 1
        w = w * 1000.0
        half_dim = embedding_dim // 2
        emb = torch.log(torch.tensor(10000.0)) / (half_dim - 1)
        emb = torch.exp(torch.arange(half_dim, dtype=dtype) * -emb)
        emb = w.to(dtype)[:, None] * emb[None, :]
        emb = torch.cat([torch.sin(emb), torch.cos(emb)], dim=1)
        if embedding_dim % 2 == 1: emb = torch.nn.functional.pad(emb, (0, 1))
        assert emb.shape == (w.shape[0], embedding_dim)
        return emb
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def do_classifier_free_guidance(self): return self._guidance_scale > 1 and self.unet.config.time_cond_proj_dim is None
    @property
    def cross_attention_kwargs(self): return self._cross_attention_kwargs
    @property
    def denoising_start(self): return self._denoising_start
    @property
    def denoising_end(self): return self._denoising_end
    @property
    def num_timesteps(self): return self._num_timesteps
    @property
    def interrupt(self): return self._interrupt
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]]=None, image: PipelineImageInput=None, strength: float=0.3, height: Optional[int]=None, width: Optional[int]=None,
    num_inference_steps: int=50, timesteps: List[int]=None, sigmas: List[float]=None, denoising_start: Optional[float]=None, denoising_end: Optional[float]=None,
    guidance_scale: float=5.0, negative_prompt: Optional[Union[str, List[str]]]=None, num_images_per_prompt: Optional[int]=1, eta: float=0.0,
    generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None,
    pooled_prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, negative_pooled_prompt_embeds: Optional[torch.Tensor]=None,
    ip_adapter_image: Optional[PipelineImageInput]=None, ip_adapter_image_embeds: Optional[List[torch.Tensor]]=None, output_type: Optional[str]='pil',
    return_dict: bool=True, cross_attention_kwargs: Optional[Dict[str, Any]]=None, original_size: Optional[Tuple[int, int]]=None,
    crops_coords_top_left: Tuple[int, int]=(0, 0), target_size: Optional[Tuple[int, int]]=None, negative_original_size: Optional[Tuple[int, int]]=None,
    negative_crops_coords_top_left: Tuple[int, int]=(0, 0), negative_target_size: Optional[Tuple[int, int]]=None, callback_on_step_end: Optional[Union[Callable[[int,
    int, Dict], None], PipelineCallback, MultiPipelineCallbacks]]=None, callback_on_step_end_tensor_inputs: List[str]=['latents'], max_sequence_length: int=256):
        """Examples:"""
        if isinstance(callback_on_step_end, (PipelineCallback, MultiPipelineCallbacks)): callback_on_step_end_tensor_inputs = callback_on_step_end.tensor_inputs
        height = height or self.default_sample_size * self.vae_scale_factor
        width = width or self.default_sample_size * self.vae_scale_factor
        original_size = original_size or (height, width)
        target_size = target_size or (height, width)
        self.check_inputs(prompt, strength, num_inference_steps, height, width, negative_prompt, prompt_embeds, pooled_prompt_embeds, negative_prompt_embeds,
        negative_pooled_prompt_embeds, ip_adapter_image, ip_adapter_image_embeds, callback_on_step_end_tensor_inputs, max_sequence_length=max_sequence_length)
        self._guidance_scale = guidance_scale
        self._cross_attention_kwargs = cross_attention_kwargs
        self._denoising_end = denoising_end
        self._denoising_start = denoising_start
        self._interrupt = False
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds = self.encode_prompt(prompt=prompt, device=device,
        num_images_per_prompt=num_images_per_prompt, do_classifier_free_guidance=self.do_classifier_free_guidance, negative_prompt=negative_prompt,
        prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds)
        image = self.image_processor.preprocess(image)
        def denoising_value_valid(dnv): return isinstance(dnv, float) and 0 < dnv < 1
        timesteps, num_inference_steps = retrieve_timesteps(self.scheduler, num_inference_steps, device, timesteps, sigmas)
        timesteps, num_inference_steps = self.get_timesteps(num_inference_steps, strength, device,
        denoising_start=self.denoising_start if denoising_value_valid(self.denoising_start) else None)
        latent_timestep = timesteps[:1].repeat(batch_size * num_images_per_prompt)
        add_noise = True if self.denoising_start is None else False
        if latents is None: latents = self.prepare_latents(image, latent_timestep, batch_size, num_images_per_prompt, prompt_embeds.dtype, device, generator, add_noise)
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        height, width = latents.shape[-2:]
        height = height * self.vae_scale_factor
        width = width * self.vae_scale_factor
        original_size = original_size or (height, width)
        target_size = target_size or (height, width)
        add_text_embeds = pooled_prompt_embeds
        text_encoder_projection_dim = int(pooled_prompt_embeds.shape[-1])
        add_time_ids = self._get_add_time_ids(original_size, crops_coords_top_left, target_size, dtype=prompt_embeds.dtype, text_encoder_projection_dim=text_encoder_projection_dim)
        if negative_original_size is not None and negative_target_size is not None: negative_add_time_ids = self._get_add_time_ids(negative_original_size,
        negative_crops_coords_top_left, negative_target_size, dtype=prompt_embeds.dtype, text_encoder_projection_dim=text_encoder_projection_dim)
        else: negative_add_time_ids = add_time_ids
        if self.do_classifier_free_guidance:
            prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds], dim=0)
            add_text_embeds = torch.cat([negative_pooled_prompt_embeds, add_text_embeds], dim=0)
            add_time_ids = torch.cat([negative_add_time_ids, add_time_ids], dim=0)
        prompt_embeds = prompt_embeds.to(device)
        add_text_embeds = add_text_embeds.to(device)
        add_time_ids = add_time_ids.to(device).repeat(batch_size * num_images_per_prompt, 1)
        if ip_adapter_image is not None or ip_adapter_image_embeds is not None: image_embeds = self.prepare_ip_adapter_image_embeds(ip_adapter_image,
        ip_adapter_image_embeds, device, batch_size * num_images_per_prompt, self.do_classifier_free_guidance)
        num_warmup_steps = max(len(timesteps) - num_inference_steps * self.scheduler.order, 0)
        if self.denoising_end is not None and self.denoising_start is not None and denoising_value_valid(self.denoising_end) and denoising_value_valid(self.denoising_start) and (self.denoising_start >= self.denoising_end): raise ValueError(f'`denoising_start`: {self.denoising_start} cannot be larger than or equal to `denoising_end`: ' + f' {self.denoising_end} when using type float.')
        elif self.denoising_end is not None and denoising_value_valid(self.denoising_end):
            discrete_timestep_cutoff = int(round(self.scheduler.config.num_train_timesteps - self.denoising_end * self.scheduler.config.num_train_timesteps))
            num_inference_steps = len(list(filter(lambda ts: ts >= discrete_timestep_cutoff, timesteps)))
            timesteps = timesteps[:num_inference_steps]
        timestep_cond = None
        if self.unet.config.time_cond_proj_dim is not None:
            guidance_scale_tensor = torch.tensor(self.guidance_scale - 1).repeat(batch_size * num_images_per_prompt)
            timestep_cond = self.get_guidance_scale_embedding(guidance_scale_tensor, embedding_dim=self.unet.config.time_cond_proj_dim).to(device=device, dtype=latents.dtype)
        self._num_timesteps = len(timesteps)
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                if self.interrupt: continue
                latent_model_input = torch.cat([latents] * 2) if self.do_classifier_free_guidance else latents
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                added_cond_kwargs = {'text_embeds': add_text_embeds, 'time_ids': add_time_ids}
                if ip_adapter_image is not None or ip_adapter_image_embeds is not None: added_cond_kwargs['image_embeds'] = image_embeds
                noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=prompt_embeds, timestep_cond=timestep_cond, cross_attention_kwargs=self.cross_attention_kwargs,
                added_cond_kwargs=added_cond_kwargs, return_dict=False)[0]
                if self.do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + self.guidance_scale * (noise_pred_text - noise_pred_uncond)
                latents_dtype = latents.dtype
                latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs, return_dict=False)[0]
                if latents.dtype != latents_dtype:
                    if torch.backends.mps.is_available(): latents = latents.to(latents_dtype)
                if callback_on_step_end is not None:
                    callback_kwargs = {}
                    for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                    callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                    latents = callback_outputs.pop('latents', latents)
                    prompt_embeds = callback_outputs.pop('prompt_embeds', prompt_embeds)
                    negative_prompt_embeds = callback_outputs.pop('negative_prompt_embeds', negative_prompt_embeds)
                    add_text_embeds = callback_outputs.pop('add_text_embeds', add_text_embeds)
                    negative_pooled_prompt_embeds = callback_outputs.pop('negative_pooled_prompt_embeds', negative_pooled_prompt_embeds)
                    add_time_ids = callback_outputs.pop('add_time_ids', add_time_ids)
                    negative_add_time_ids = callback_outputs.pop('negative_add_time_ids', negative_add_time_ids)
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0): progress_bar.update()
                if XLA_AVAILABLE: xm.mark_step()
        if not output_type == 'latent':
            needs_upcasting = self.vae.dtype == torch.float16 and self.vae.config.force_upcast
            if needs_upcasting:
                self.upcast_vae()
                latents = latents.to(next(iter(self.vae.post_quant_conv.parameters())).dtype)
            elif latents.dtype != self.vae.dtype:
                if torch.backends.mps.is_available(): self.vae = self.vae.to(latents.dtype)
            latents = latents / self.vae.config.scaling_factor
            image = self.vae.decode(latents, return_dict=False)[0]
            if needs_upcasting: self.vae.to(dtype=torch.float16)
        else: image = latents
        if not output_type == 'latent': image = self.image_processor.postprocess(image, output_type=output_type)
        self.maybe_free_model_hooks()
        if not return_dict: return (image,)
        return KolorsPipelineOutput(images=image)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
