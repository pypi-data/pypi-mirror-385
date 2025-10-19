'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
import math
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np
import torch
from torch.nn import functional as F
from sapiens_transformers import CLIPImageProcessor, CLIPTextModel, CLIPTokenizer
from ...image_processor import VaeImageProcessor
from ...loaders import StableDiffusionLoraLoaderMixin, TextualInversionLoaderMixin
from ...models import AutoencoderKL, UNet2DConditionModel
from ...models.attention_processor import Attention
from ...models.lora import adjust_lora_scale_text_encoder
from ...schedulers import KarrasDiffusionSchedulers
from ...utils import USE_PEFT_BACKEND, deprecate, replace_example_docstring, scale_lora_layers, unscale_lora_layers
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, StableDiffusionMixin
from ..stable_diffusion import StableDiffusionPipelineOutput
from ..stable_diffusion.safety_checker import StableDiffusionSafetyChecker
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import StableDiffusionAttendAndExcitePipeline\n\n        >>> pipe = StableDiffusionAttendAndExcitePipeline.from_pretrained(\n        ...     "CompVis/stable-diffusion-v1-4", torch_dtype=torch.float16\n        ... ).to("cuda")\n\n\n        >>> prompt = "a cat and a frog"\n\n        >>> # use get_indices function to find out indices of the tokens you want to alter\n        >>> pipe.get_indices(prompt)\n        {0: \'<|startoftext|>\', 1: \'a</w>\', 2: \'cat</w>\', 3: \'and</w>\', 4: \'a</w>\', 5: \'frog</w>\', 6: \'<|endoftext|>\'}\n\n        >>> token_indices = [2, 5]\n        >>> seed = 6141\n        >>> generator = torch.Generator("cuda").manual_seed(seed)\n\n        >>> images = pipe(\n        ...     prompt=prompt,\n        ...     token_indices=token_indices,\n        ...     guidance_scale=7.5,\n        ...     generator=generator,\n        ...     num_inference_steps=50,\n        ...     max_iter_to_alter=25,\n        ... ).images\n\n        >>> image = images[0]\n        >>> image.save(f"../images/{prompt}_{seed}.png")\n        ```\n'
class AttentionStore:
    @staticmethod
    def get_empty_store(): return {'down': [], 'mid': [], 'up': []}
    def __call__(self, attn, is_cross: bool, place_in_unet: str):
        if self.cur_att_layer >= 0 and is_cross:
            if attn.shape[1] == np.prod(self.attn_res): self.step_store[place_in_unet].append(attn)
        self.cur_att_layer += 1
        if self.cur_att_layer == self.num_att_layers:
            self.cur_att_layer = 0
            self.between_steps()
    def between_steps(self):
        self.attention_store = self.step_store
        self.step_store = self.get_empty_store()
    def get_average_attention(self):
        average_attention = self.attention_store
        return average_attention
    def aggregate_attention(self, from_where: List[str]) -> torch.Tensor:
        out = []
        attention_maps = self.get_average_attention()
        for location in from_where:
            for item in attention_maps[location]:
                cross_maps = item.reshape(-1, self.attn_res[0], self.attn_res[1], item.shape[-1])
                out.append(cross_maps)
        out = torch.cat(out, dim=0)
        out = out.sum(0) / out.shape[0]
        return out
    def reset(self):
        self.cur_att_layer = 0
        self.step_store = self.get_empty_store()
        self.attention_store = {}
    def __init__(self, attn_res):
        self.num_att_layers = -1
        self.cur_att_layer = 0
        self.step_store = self.get_empty_store()
        self.attention_store = {}
        self.curr_step_index = 0
        self.attn_res = attn_res
class AttendExciteAttnProcessor:
    def __init__(self, attnstore, place_in_unet):
        super().__init__()
        self.attnstore = attnstore
        self.place_in_unet = place_in_unet
    def __call__(self, attn: Attention, hidden_states, encoder_hidden_states=None, attention_mask=None):
        batch_size, sequence_length, _ = hidden_states.shape
        attention_mask = attn.prepare_attention_mask(attention_mask, sequence_length, batch_size)
        query = attn.to_q(hidden_states)
        is_cross = encoder_hidden_states is not None
        encoder_hidden_states = encoder_hidden_states if encoder_hidden_states is not None else hidden_states
        key = attn.to_k(encoder_hidden_states)
        value = attn.to_v(encoder_hidden_states)
        query = attn.head_to_batch_dim(query)
        key = attn.head_to_batch_dim(key)
        value = attn.head_to_batch_dim(value)
        attention_probs = attn.get_attention_scores(query, key, attention_mask)
        if attention_probs.requires_grad: self.attnstore(attention_probs, is_cross, self.place_in_unet)
        hidden_states = torch.bmm(attention_probs, value)
        hidden_states = attn.batch_to_head_dim(hidden_states)
        hidden_states = attn.to_out[0](hidden_states)
        hidden_states = attn.to_out[1](hidden_states)
        return hidden_states
class StableDiffusionAttendAndExcitePipeline(DiffusionPipeline, StableDiffusionMixin, TextualInversionLoaderMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->unet->vae'
    _optional_components = ['safety_checker', 'feature_extractor']
    _exclude_from_cpu_offload = ['safety_checker']
    def __init__(self, vae: AutoencoderKL, text_encoder: CLIPTextModel, tokenizer: CLIPTokenizer, unet: UNet2DConditionModel, scheduler: KarrasDiffusionSchedulers, safety_checker: StableDiffusionSafetyChecker, feature_extractor: CLIPImageProcessor, requires_safety_checker: bool=True):
        super().__init__()
        if safety_checker is not None and feature_extractor is None: raise ValueError("Make sure to define a feature extractor when loading {self.__class__} if you want to use the safety checker. If you do not want to use the safety checker, you can pass `'safety_checker=None'` instead.")
        self.register_modules(vae=vae, text_encoder=text_encoder, tokenizer=tokenizer, unet=unet, scheduler=scheduler, safety_checker=safety_checker, feature_extractor=feature_extractor)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor)
        self.register_to_config(requires_safety_checker=requires_safety_checker)
    def _encode_prompt(self, prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, lora_scale: Optional[float]=None, **kwargs):
        deprecation_message = '`_encode_prompt()` is deprecated and it will be removed in a future version. Use `encode_prompt()` instead. Also, be aware that the output format changed from a concatenated tensor to a tuple.'
        deprecate('_encode_prompt()', '1.0.0', deprecation_message, standard_warn=False)
        prompt_embeds_tuple = self.encode_prompt(prompt=prompt, device=device, num_images_per_prompt=num_images_per_prompt, do_classifier_free_guidance=do_classifier_free_guidance, negative_prompt=negative_prompt, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, lora_scale=lora_scale, **kwargs)
        prompt_embeds = torch.cat([prompt_embeds_tuple[1], prompt_embeds_tuple[0]])
        return prompt_embeds
    def encode_prompt(self, prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, lora_scale: Optional[float]=None, clip_skip: Optional[int]=None):
        """Args:"""
        if lora_scale is not None and isinstance(self, StableDiffusionLoraLoaderMixin):
            self._lora_scale = lora_scale
            if not USE_PEFT_BACKEND: adjust_lora_scale_text_encoder(self.text_encoder, lora_scale)
            else: scale_lora_layers(self.text_encoder, lora_scale)
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if prompt_embeds is None:
            if isinstance(self, TextualInversionLoaderMixin): prompt = self.maybe_convert_prompt(prompt, self.tokenizer)
            text_inputs = self.tokenizer(prompt, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
            text_input_ids = text_inputs.input_ids
            untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
            if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer.batch_decode(untruncated_ids[:, self.tokenizer.model_max_length - 1:-1])
            if hasattr(self.text_encoder.config, 'use_attention_mask') and self.text_encoder.config.use_attention_mask: attention_mask = text_inputs.attention_mask.to(device)
            else: attention_mask = None
            if clip_skip is None:
                prompt_embeds = self.text_encoder(text_input_ids.to(device), attention_mask=attention_mask)
                prompt_embeds = prompt_embeds[0]
            else:
                prompt_embeds = self.text_encoder(text_input_ids.to(device), attention_mask=attention_mask, output_hidden_states=True)
                prompt_embeds = prompt_embeds[-1][-(clip_skip + 1)]
                prompt_embeds = self.text_encoder.text_model.final_layer_norm(prompt_embeds)
        if self.text_encoder is not None: prompt_embeds_dtype = self.text_encoder.dtype
        elif self.unet is not None: prompt_embeds_dtype = self.unet.dtype
        else: prompt_embeds_dtype = prompt_embeds.dtype
        prompt_embeds = prompt_embeds.to(dtype=prompt_embeds_dtype, device=device)
        bs_embed, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_images_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(bs_embed * num_images_per_prompt, seq_len, -1)
        if do_classifier_free_guidance and negative_prompt_embeds is None:
            uncond_tokens: List[str]
            if negative_prompt is None: uncond_tokens = [''] * batch_size
            elif prompt is not None and type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif isinstance(negative_prompt, str): uncond_tokens = [negative_prompt]
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            else: uncond_tokens = negative_prompt
            if isinstance(self, TextualInversionLoaderMixin): uncond_tokens = self.maybe_convert_prompt(uncond_tokens, self.tokenizer)
            max_length = prompt_embeds.shape[1]
            uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=max_length, truncation=True, return_tensors='pt')
            if hasattr(self.text_encoder.config, 'use_attention_mask') and self.text_encoder.config.use_attention_mask: attention_mask = uncond_input.attention_mask.to(device)
            else: attention_mask = None
            negative_prompt_embeds = self.text_encoder(uncond_input.input_ids.to(device), attention_mask=attention_mask)
            negative_prompt_embeds = negative_prompt_embeds[0]
        if do_classifier_free_guidance:
            seq_len = negative_prompt_embeds.shape[1]
            negative_prompt_embeds = negative_prompt_embeds.to(dtype=prompt_embeds_dtype, device=device)
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt, 1)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
        if self.text_encoder is not None:
            if isinstance(self, StableDiffusionLoraLoaderMixin) and USE_PEFT_BACKEND: unscale_lora_layers(self.text_encoder, lora_scale)
        return (prompt_embeds, negative_prompt_embeds)
    def run_safety_checker(self, image, device, dtype):
        if self.safety_checker is None: has_nsfw_concept = None
        else:
            if torch.is_tensor(image): feature_extractor_input = self.image_processor.postprocess(image, output_type='pil')
            else: feature_extractor_input = self.image_processor.numpy_to_pil(image)
            safety_checker_input = self.feature_extractor(feature_extractor_input, return_tensors='pt').to(device)
            image, has_nsfw_concept = self.safety_checker(images=image, clip_input=safety_checker_input.pixel_values.to(dtype))
        return (image, has_nsfw_concept)
    def decode_latents(self, latents):
        deprecation_message = 'The decode_latents method is deprecated and will be removed in 1.0.0. Please use VaeImageProcessor.postprocess(...) instead'
        deprecate('decode_latents', '1.0.0', deprecation_message, standard_warn=False)
        latents = 1 / self.vae.config.scaling_factor * latents
        image = self.vae.decode(latents, return_dict=False)[0]
        image = (image / 2 + 0.5).clamp(0, 1)
        image = image.cpu().permute(0, 2, 3, 1).float().numpy()
        return image
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, prompt, indices, height, width, callback_steps, negative_prompt=None, prompt_embeds=None, negative_prompt_embeds=None):
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
        if callback_steps is None or (callback_steps is not None and (not isinstance(callback_steps, int) or callback_steps <= 0)): raise ValueError(f'`callback_steps` has to be a positive integer but is {callback_steps} of type {type(callback_steps)}.')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
        indices_is_list_ints = isinstance(indices, list) and isinstance(indices[0], int)
        indices_is_list_list_ints = isinstance(indices, list) and isinstance(indices[0], list) and isinstance(indices[0][0], int)
        if not indices_is_list_ints and (not indices_is_list_list_ints): raise TypeError('`indices` must be a list of ints or a list of a list of ints')
        if indices_is_list_ints: indices_batch_size = 1
        elif indices_is_list_list_ints: indices_batch_size = len(indices)
        if prompt is not None and isinstance(prompt, str): prompt_batch_size = 1
        elif prompt is not None and isinstance(prompt, list): prompt_batch_size = len(prompt)
        elif prompt_embeds is not None: prompt_batch_size = prompt_embeds.shape[0]
        if indices_batch_size != prompt_batch_size: raise ValueError(f'indices batch size must be same as prompt batch size. indices batch size: {indices_batch_size}, prompt batch size: {prompt_batch_size}')
    def prepare_latents(self, batch_size, num_channels_latents, height, width, dtype, device, generator, latents=None):
        shape = (batch_size, num_channels_latents, int(height) // self.vae_scale_factor, int(width) // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else: latents = latents.to(device)
        latents = latents * self.scheduler.init_noise_sigma
        return latents
    @staticmethod
    def _compute_max_attention_per_index(attention_maps: torch.Tensor, indices: List[int]) -> List[torch.Tensor]:
        attention_for_text = attention_maps[:, :, 1:-1]
        attention_for_text *= 100
        attention_for_text = torch.nn.functional.softmax(attention_for_text, dim=-1)
        indices = [index - 1 for index in indices]
        max_indices_list = []
        for i in indices:
            image = attention_for_text[:, :, i]
            smoothing = GaussianSmoothing().to(attention_maps.device)
            input = F.pad(image.unsqueeze(0).unsqueeze(0), (1, 1, 1, 1), mode='reflect')
            image = smoothing(input).squeeze(0).squeeze(0)
            max_indices_list.append(image.max())
        return max_indices_list
    def _aggregate_and_get_max_attention_per_token(self, indices: List[int]):
        attention_maps = self.attention_store.aggregate_attention(from_where=('up', 'down', 'mid'))
        max_attention_per_index = self._compute_max_attention_per_index(attention_maps=attention_maps, indices=indices)
        return max_attention_per_index
    @staticmethod
    def _compute_loss(max_attention_per_index: List[torch.Tensor]) -> torch.Tensor:
        losses = [max(0, 1.0 - curr_max) for curr_max in max_attention_per_index]
        loss = max(losses)
        return loss
    @staticmethod
    def _update_latent(latents: torch.Tensor, loss: torch.Tensor, step_size: float) -> torch.Tensor:
        grad_cond = torch.autograd.grad(loss.requires_grad_(True), [latents], retain_graph=True)[0]
        latents = latents - step_size * grad_cond
        return latents
    def _perform_iterative_refinement_step(self, latents: torch.Tensor, indices: List[int], loss: torch.Tensor, threshold: float, text_embeddings: torch.Tensor, step_size: float, t: int, max_refinement_steps: int=20):
        iteration = 0
        target_loss = max(0, 1.0 - threshold)
        while loss > target_loss:
            iteration += 1
            latents = latents.clone().detach().requires_grad_(True)
            self.unet(latents, t, encoder_hidden_states=text_embeddings).sample
            self.unet.zero_grad()
            max_attention_per_index = self._aggregate_and_get_max_attention_per_token(indices=indices)
            loss = self._compute_loss(max_attention_per_index)
            if loss != 0: latents = self._update_latent(latents, loss, step_size)
            if iteration >= max_refinement_steps: break
        latents = latents.clone().detach().requires_grad_(True)
        _ = self.unet(latents, t, encoder_hidden_states=text_embeddings).sample
        self.unet.zero_grad()
        max_attention_per_index = self._aggregate_and_get_max_attention_per_token(indices=indices)
        loss = self._compute_loss(max_attention_per_index)
        return (loss, latents, max_attention_per_index)
    def register_attention_control(self):
        attn_procs = {}
        cross_att_count = 0
        for name in self.unet.attn_processors.keys():
            if name.startswith('mid_block'): place_in_unet = 'mid'
            elif name.startswith('up_blocks'): place_in_unet = 'up'
            elif name.startswith('down_blocks'): place_in_unet = 'down'
            else: continue
            cross_att_count += 1
            attn_procs[name] = AttendExciteAttnProcessor(attnstore=self.attention_store, place_in_unet=place_in_unet)
        self.unet.set_attn_processor(attn_procs)
        self.attention_store.num_att_layers = cross_att_count
    def get_indices(self, prompt: str) -> Dict[str, int]:
        ids = self.tokenizer(prompt).input_ids
        indices = {i: tok for tok, i in zip(self.tokenizer.convert_ids_to_tokens(ids), range(len(ids)))}
        return indices
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]], token_indices: Union[List[int], List[List[int]]], height: Optional[int]=None, width: Optional[int]=None, num_inference_steps: int=50, guidance_scale: float=7.5, negative_prompt: Optional[Union[str, List[str]]]=None, num_images_per_prompt: int=1, eta: float=0.0, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', return_dict: bool=True, callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: int=1, cross_attention_kwargs: Optional[Dict[str, Any]]=None, max_iter_to_alter: int=25, thresholds: dict={0: 0.05, 10: 0.5, 20: 0.8}, scale_factor: int=20, attn_res: Optional[Tuple[int]]=(16, 16), clip_skip: Optional[int]=None):
        """Examples:"""
        height = height or self.unet.config.sample_size * self.vae_scale_factor
        width = width or self.unet.config.sample_size * self.vae_scale_factor
        self.check_inputs(prompt, token_indices, height, width, callback_steps, negative_prompt, prompt_embeds, negative_prompt_embeds)
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        prompt_embeds, negative_prompt_embeds = self.encode_prompt(prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, clip_skip=clip_skip)
        if do_classifier_free_guidance: prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps
        num_channels_latents = self.unet.config.in_channels
        latents = self.prepare_latents(batch_size * num_images_per_prompt, num_channels_latents, height, width, prompt_embeds.dtype, device, generator, latents)
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        if attn_res is None: attn_res = (int(np.ceil(width / 32)), int(np.ceil(height / 32)))
        self.attention_store = AttentionStore(attn_res)
        original_attn_proc = self.unet.attn_processors
        self.register_attention_control()
        scale_range = np.linspace(1.0, 0.5, len(self.scheduler.timesteps))
        step_size = scale_factor * np.sqrt(scale_range)
        text_embeddings = prompt_embeds[batch_size * num_images_per_prompt:] if do_classifier_free_guidance else prompt_embeds
        if isinstance(token_indices[0], int): token_indices = [token_indices]
        indices = []
        for ind in token_indices: indices = indices + [ind] * num_images_per_prompt
        num_warmup_steps = len(timesteps) - num_inference_steps * self.scheduler.order
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                with torch.enable_grad():
                    latents = latents.clone().detach().requires_grad_(True)
                    updated_latents = []
                    for latent, index, text_embedding in zip(latents, indices, text_embeddings):
                        latent = latent.unsqueeze(0)
                        text_embedding = text_embedding.unsqueeze(0)
                        self.unet(latent, t, encoder_hidden_states=text_embedding, cross_attention_kwargs=cross_attention_kwargs).sample
                        self.unet.zero_grad()
                        max_attention_per_index = self._aggregate_and_get_max_attention_per_token(indices=index)
                        loss = self._compute_loss(max_attention_per_index=max_attention_per_index)
                        if i in thresholds.keys() and loss > 1.0 - thresholds[i]: loss, latent, max_attention_per_index = self._perform_iterative_refinement_step(latents=latent, indices=index, loss=loss, threshold=thresholds[i], text_embeddings=text_embedding, step_size=step_size[i], t=t)
                        if i < max_iter_to_alter:
                            if loss != 0: latent = self._update_latent(latents=latent, loss=loss, step_size=step_size[i])
                        updated_latents.append(latent)
                    latents = torch.cat(updated_latents, dim=0)
                latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=prompt_embeds, cross_attention_kwargs=cross_attention_kwargs).sample
                if do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs).prev_sample
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0):
                    progress_bar.update()
                    if callback is not None and i % callback_steps == 0:
                        step_idx = i // getattr(self.scheduler, 'order', 1)
                        callback(step_idx, t, latents)
        if not output_type == 'latent':
            image = self.vae.decode(latents / self.vae.config.scaling_factor, return_dict=False)[0]
            image, has_nsfw_concept = self.run_safety_checker(image, device, prompt_embeds.dtype)
        else:
            image = latents
            has_nsfw_concept = None
        if has_nsfw_concept is None: do_denormalize = [True] * image.shape[0]
        else: do_denormalize = [not has_nsfw for has_nsfw in has_nsfw_concept]
        image = self.image_processor.postprocess(image, output_type=output_type, do_denormalize=do_denormalize)
        self.maybe_free_model_hooks()
        self.unet.set_attn_processor(original_attn_proc)
        if not return_dict: return (image, has_nsfw_concept)
        return StableDiffusionPipelineOutput(images=image, nsfw_content_detected=has_nsfw_concept)
class GaussianSmoothing(torch.nn.Module):
    def __init__(self, channels: int=1, kernel_size: int=3, sigma: float=0.5, dim: int=2):
        super().__init__()
        if isinstance(kernel_size, int): kernel_size = [kernel_size] * dim
        if isinstance(sigma, float): sigma = [sigma] * dim
        kernel = 1
        meshgrids = torch.meshgrid([torch.arange(size, dtype=torch.float32) for size in kernel_size])
        for size, std, mgrid in zip(kernel_size, sigma, meshgrids):
            mean = (size - 1) / 2
            kernel *= 1 / (std * math.sqrt(2 * math.pi)) * torch.exp(-((mgrid - mean) / (2 * std)) ** 2)
        kernel = kernel / torch.sum(kernel)
        kernel = kernel.view(1, 1, *kernel.size())
        kernel = kernel.repeat(channels, *[1] * (kernel.dim() - 1))
        self.register_buffer('weight', kernel)
        self.groups = channels
        if dim == 1: self.conv = F.conv1d
        elif dim == 2: self.conv = F.conv2d
        elif dim == 3: self.conv = F.conv3d
        else: raise RuntimeError('Only 1, 2 and 3 dimensions are supported. Received {}.'.format(dim))
    def forward(self, input):
        """Returns:"""
        return self.conv(input, weight=self.weight.to(input.dtype), groups=self.groups)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
