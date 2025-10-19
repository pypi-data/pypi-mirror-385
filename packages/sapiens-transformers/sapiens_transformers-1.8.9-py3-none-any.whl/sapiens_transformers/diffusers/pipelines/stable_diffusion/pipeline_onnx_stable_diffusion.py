'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from typing import Callable, List, Optional, Union
import numpy as np
import torch
from sapiens_transformers import CLIPImageProcessor, CLIPTokenizer
from ...configuration_utils import FrozenDict
from ...schedulers import DDIMScheduler, LMSDiscreteScheduler, PNDMScheduler
from ...utils import deprecate
from ..onnx_utils import ORT_TO_NP_TYPE, OnnxRuntimeModel
from ..pipeline_utils import DiffusionPipeline
from . import StableDiffusionPipelineOutput
class OnnxStableDiffusionPipeline(DiffusionPipeline):
    vae_encoder: OnnxRuntimeModel
    vae_decoder: OnnxRuntimeModel
    text_encoder: OnnxRuntimeModel
    tokenizer: CLIPTokenizer
    unet: OnnxRuntimeModel
    scheduler: Union[DDIMScheduler, PNDMScheduler, LMSDiscreteScheduler]
    safety_checker: OnnxRuntimeModel
    feature_extractor: CLIPImageProcessor
    _optional_components = ['safety_checker', 'feature_extractor']
    _is_onnx = True
    def __init__(self, vae_encoder: OnnxRuntimeModel, vae_decoder: OnnxRuntimeModel, text_encoder: OnnxRuntimeModel, tokenizer: CLIPTokenizer, unet: OnnxRuntimeModel, scheduler: Union[DDIMScheduler,
    PNDMScheduler, LMSDiscreteScheduler], safety_checker: OnnxRuntimeModel, feature_extractor: CLIPImageProcessor, requires_safety_checker: bool=True):
        super().__init__()
        if hasattr(scheduler.config, 'steps_offset') and scheduler.config.steps_offset != 1:
            deprecation_message = f'The configuration file of this scheduler: {scheduler} is outdated. `steps_offset` should be set to 1 instead of {scheduler.config.steps_offset}. Please make sure to update the config accordingly as leaving `steps_offset` might led to incorrect results in future versions. If you have downloaded this checkpoint from the Sapiens Hub, it would be very nice if you could open a Pull request for the `scheduler/scheduler_config.json` file'
            deprecate('steps_offset!=1', '1.0.0', deprecation_message, standard_warn=False)
            new_config = dict(scheduler.config)
            new_config['steps_offset'] = 1
            scheduler._internal_dict = FrozenDict(new_config)
        if hasattr(scheduler.config, 'clip_sample') and scheduler.config.clip_sample is True:
            deprecation_message = f'The configuration file of this scheduler: {scheduler} has not set the configuration `clip_sample`. `clip_sample` should be set to False in the configuration file. Please make sure to update the config accordingly as not setting `clip_sample` in the config might lead to incorrect results in future versions. If you have downloaded this checkpoint from the Sapiens Hub, it would be very nice if you could open a Pull request for the `scheduler/scheduler_config.json` file'
            deprecate('clip_sample not set', '1.0.0', deprecation_message, standard_warn=False)
            new_config = dict(scheduler.config)
            new_config['clip_sample'] = False
            scheduler._internal_dict = FrozenDict(new_config)
        if safety_checker is not None and feature_extractor is None: raise ValueError("Make sure to define a feature extractor when loading {self.__class__} if you want to use the safety checker. If you do not want to use the safety checker, you can pass `'safety_checker=None'` instead.")
        self.register_modules(vae_encoder=vae_encoder, vae_decoder=vae_decoder, text_encoder=text_encoder, tokenizer=tokenizer, unet=unet,
        scheduler=scheduler, safety_checker=safety_checker, feature_extractor=feature_extractor)
        self.register_to_config(requires_safety_checker=requires_safety_checker)
    def _encode_prompt(self, prompt: Union[str, List[str]], num_images_per_prompt: Optional[int], do_classifier_free_guidance: bool, negative_prompt: Optional[str],
    prompt_embeds: Optional[np.ndarray]=None, negative_prompt_embeds: Optional[np.ndarray]=None):
        """Args:"""
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if prompt_embeds is None:
            text_inputs = self.tokenizer(prompt, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='np')
            text_input_ids = text_inputs.input_ids
            untruncated_ids = self.tokenizer(prompt, padding='max_length', return_tensors='np').input_ids
            if not np.array_equal(text_input_ids, untruncated_ids): removed_text = self.tokenizer.batch_decode(untruncated_ids[:, self.tokenizer.model_max_length - 1:-1])
            prompt_embeds = self.text_encoder(input_ids=text_input_ids.astype(np.int32))[0]
        prompt_embeds = np.repeat(prompt_embeds, num_images_per_prompt, axis=0)
        if do_classifier_free_guidance and negative_prompt_embeds is None:
            uncond_tokens: List[str]
            if negative_prompt is None: uncond_tokens = [''] * batch_size
            elif type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif isinstance(negative_prompt, str): uncond_tokens = [negative_prompt] * batch_size
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            else: uncond_tokens = negative_prompt
            max_length = prompt_embeds.shape[1]
            uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=max_length, truncation=True, return_tensors='np')
            negative_prompt_embeds = self.text_encoder(input_ids=uncond_input.input_ids.astype(np.int32))[0]
        if do_classifier_free_guidance:
            negative_prompt_embeds = np.repeat(negative_prompt_embeds, num_images_per_prompt, axis=0)
            prompt_embeds = np.concatenate([negative_prompt_embeds, prompt_embeds])
        return prompt_embeds
    def check_inputs(self, prompt: Union[str, List[str]], height: Optional[int], width: Optional[int], callback_steps: int, negative_prompt: Optional[str]=None,
    prompt_embeds: Optional[np.ndarray]=None, negative_prompt_embeds: Optional[np.ndarray]=None):
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
        if callback_steps is None or (callback_steps is not None and (not isinstance(callback_steps, int) or callback_steps <= 0)): raise ValueError(f'`callback_steps` has to be a positive integer but is {callback_steps} of type {type(callback_steps)}.')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
    def __call__(self, prompt: Union[str, List[str]]=None, height: Optional[int]=512, width: Optional[int]=512, num_inference_steps: Optional[int]=50, guidance_scale: Optional[float]=7.5,
    negative_prompt: Optional[Union[str, List[str]]]=None, num_images_per_prompt: Optional[int]=1, eta: Optional[float]=0.0, generator: Optional[np.random.RandomState]=None,
    latents: Optional[np.ndarray]=None, prompt_embeds: Optional[np.ndarray]=None, negative_prompt_embeds: Optional[np.ndarray]=None, output_type: Optional[str]='pil',
    return_dict: bool=True, callback: Optional[Callable[[int, int, np.ndarray], None]]=None, callback_steps: int=1):
        """Returns:"""
        self.check_inputs(prompt, height, width, callback_steps, negative_prompt, prompt_embeds, negative_prompt_embeds)
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if generator is None: generator = np.random
        do_classifier_free_guidance = guidance_scale > 1.0
        prompt_embeds = self._encode_prompt(prompt, num_images_per_prompt, do_classifier_free_guidance, negative_prompt,
        prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds)
        latents_dtype = prompt_embeds.dtype
        latents_shape = (batch_size * num_images_per_prompt, 4, height // 8, width // 8)
        if latents is None: latents = generator.randn(*latents_shape).astype(latents_dtype)
        elif latents.shape != latents_shape: raise ValueError(f'Unexpected latents shape, got {latents.shape}, expected {latents_shape}')
        self.scheduler.set_timesteps(num_inference_steps)
        latents = latents * np.float64(self.scheduler.init_noise_sigma)
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        timestep_dtype = next((input.type for input in self.unet.model.get_inputs() if input.name == 'timestep'), 'tensor(float)')
        timestep_dtype = ORT_TO_NP_TYPE[timestep_dtype]
        for i, t in enumerate(self.progress_bar(self.scheduler.timesteps)):
            latent_model_input = np.concatenate([latents] * 2) if do_classifier_free_guidance else latents
            latent_model_input = self.scheduler.scale_model_input(torch.from_numpy(latent_model_input), t)
            latent_model_input = latent_model_input.cpu().numpy()
            timestep = np.array([t], dtype=timestep_dtype)
            noise_pred = self.unet(sample=latent_model_input, timestep=timestep, encoder_hidden_states=prompt_embeds)
            noise_pred = noise_pred[0]
            if do_classifier_free_guidance:
                noise_pred_uncond, noise_pred_text = np.split(noise_pred, 2)
                noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
            scheduler_output = self.scheduler.step(torch.from_numpy(noise_pred), t, torch.from_numpy(latents), **extra_step_kwargs)
            latents = scheduler_output.prev_sample.numpy()
            if callback is not None and i % callback_steps == 0:
                step_idx = i // getattr(self.scheduler, 'order', 1)
                callback(step_idx, t, latents)
        latents = 1 / 0.18215 * latents
        image = np.concatenate([self.vae_decoder(latent_sample=latents[i:i + 1])[0] for i in range(latents.shape[0])])
        image = np.clip(image / 2 + 0.5, 0, 1)
        image = image.transpose((0, 2, 3, 1))
        if self.safety_checker is not None:
            safety_checker_input = self.feature_extractor(self.numpy_to_pil(image), return_tensors='np').pixel_values.astype(image.dtype)
            images, has_nsfw_concept = ([], [])
            for i in range(image.shape[0]):
                image_i, has_nsfw_concept_i = self.safety_checker(clip_input=safety_checker_input[i:i + 1], images=image[i:i + 1])
                images.append(image_i)
                has_nsfw_concept.append(has_nsfw_concept_i[0])
            image = np.concatenate(images)
        else: has_nsfw_concept = None
        if output_type == 'pil': image = self.numpy_to_pil(image)
        if not return_dict: return (image, has_nsfw_concept)
        return StableDiffusionPipelineOutput(images=image, nsfw_content_detected=has_nsfw_concept)
class StableDiffusionOnnxPipeline(OnnxStableDiffusionPipeline):
    def __init__(self, vae_encoder: OnnxRuntimeModel, vae_decoder: OnnxRuntimeModel, text_encoder: OnnxRuntimeModel, tokenizer: CLIPTokenizer, unet: OnnxRuntimeModel,
    scheduler: Union[DDIMScheduler, PNDMScheduler, LMSDiscreteScheduler], safety_checker: OnnxRuntimeModel, feature_extractor: CLIPImageProcessor):
        deprecation_message = 'Please use `OnnxStableDiffusionPipeline` instead of `StableDiffusionOnnxPipeline`.'
        deprecate('StableDiffusionOnnxPipeline', '1.0.0', deprecation_message)
        super().__init__(vae_encoder=vae_encoder, vae_decoder=vae_decoder, text_encoder=text_encoder, tokenizer=tokenizer, unet=unet,
        scheduler=scheduler, safety_checker=safety_checker, feature_extractor=feature_extractor)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
