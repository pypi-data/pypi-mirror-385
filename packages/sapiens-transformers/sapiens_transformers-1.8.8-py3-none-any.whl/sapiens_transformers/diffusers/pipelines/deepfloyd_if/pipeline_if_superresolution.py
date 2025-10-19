'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import html
import inspect
import re
import urllib.parse as ul
from typing import Any, Callable, Dict, List, Optional, Union
import numpy as np
import PIL.Image
import torch
import torch.nn.functional as F
from sapiens_transformers import CLIPImageProcessor, T5EncoderModel, T5Tokenizer
from ...loaders import StableDiffusionLoraLoaderMixin
from ...models import UNet2DConditionModel
from ...schedulers import DDPMScheduler
from ...utils import BACKENDS_MAPPING, is_bs4_available, is_ftfy_available, replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline
from .pipeline_output import IFPipelineOutput
from .safety_checker import IFSafetyChecker
from .watermark import IFWatermarker
if is_bs4_available(): from bs4 import BeautifulSoup
if is_ftfy_available(): import ftfy
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> from sapiens_transformers.diffusers import IFPipeline, IFSuperResolutionPipeline, DiffusionPipeline\n        >>> from sapiens_transformers.diffusers.utils import pt_to_pil\n        >>> import torch\n\n        >>> pipe = IFPipeline.from_pretrained("DeepFloyd/IF-I-XL-v1.0", variant="fp16", torch_dtype=torch.float16)\n        >>> pipe.enable_model_cpu_offload()\n\n        >>> prompt = \'a photo of a kangaroo wearing an orange hoodie and blue sunglasses standing in front of the eiffel tower holding a sign that says "very deep learning"\'\n        >>> prompt_embeds, negative_embeds = pipe.encode_prompt(prompt)\n\n        >>> image = pipe(prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_embeds, output_type="pt").images\n\n        >>> # save intermediate image\n        >>> pil_image = pt_to_pil(image)\n        >>> pil_image[0].save("./if_stage_I.png")\n\n        >>> super_res_1_pipe = IFSuperResolutionPipeline.from_pretrained(\n        ...     "DeepFloyd/IF-II-L-v1.0", text_encoder=None, variant="fp16", torch_dtype=torch.float16\n        ... )\n        >>> super_res_1_pipe.enable_model_cpu_offload()\n\n        >>> image = super_res_1_pipe(\n        ...     image=image, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_embeds\n        ... ).images\n        >>> image[0].save("./if_stage_II.png")\n        ```\n'
class IFSuperResolutionPipeline(DiffusionPipeline, StableDiffusionLoraLoaderMixin):
    tokenizer: T5Tokenizer
    text_encoder: T5EncoderModel
    unet: UNet2DConditionModel
    scheduler: DDPMScheduler
    image_noising_scheduler: DDPMScheduler
    feature_extractor: Optional[CLIPImageProcessor]
    safety_checker: Optional[IFSafetyChecker]
    watermarker: Optional[IFWatermarker]
    bad_punct_regex = re.compile('[' + '#®•©™&@·º½¾¿¡§~' + '\\)' + '\\(' + '\\]' + '\\[' + '\\}' + '\\{' + '\\|' + '\\' + '\\/' + '\\*' + ']{1,}')
    _optional_components = ['tokenizer', 'text_encoder', 'safety_checker', 'feature_extractor', 'watermarker']
    model_cpu_offload_seq = 'text_encoder->unet'
    _exclude_from_cpu_offload = ['watermarker']
    def __init__(self, tokenizer: T5Tokenizer, text_encoder: T5EncoderModel, unet: UNet2DConditionModel, scheduler: DDPMScheduler, image_noising_scheduler: DDPMScheduler,
    safety_checker: Optional[IFSafetyChecker], feature_extractor: Optional[CLIPImageProcessor], watermarker: Optional[IFWatermarker], requires_safety_checker: bool=True):
        super().__init__()
        if safety_checker is not None and feature_extractor is None: raise ValueError("Make sure to define a feature extractor when loading {self.__class__} if you want to use the safety checker. If you do not want to use the safety checker, you can pass `'safety_checker=None'` instead.")
        self.register_modules(tokenizer=tokenizer, text_encoder=text_encoder, unet=unet, scheduler=scheduler, image_noising_scheduler=image_noising_scheduler, safety_checker=safety_checker,
        feature_extractor=feature_extractor, watermarker=watermarker)
        self.register_to_config(requires_safety_checker=requires_safety_checker)
    def _text_preprocessing(self, text, clean_caption=False):
        if clean_caption and (not is_bs4_available()): clean_caption = False
        if clean_caption and (not is_ftfy_available()): clean_caption = False
        if not isinstance(text, (tuple, list)): text = [text]
        def process(text: str):
            if clean_caption:
                text = self._clean_caption(text)
                text = self._clean_caption(text)
            else: text = text.lower().strip()
            return text
        return [process(t) for t in text]
    def _clean_caption(self, caption):
        caption = str(caption)
        caption = ul.unquote_plus(caption)
        caption = caption.strip().lower()
        caption = re.sub('<person>', 'person', caption)
        caption = re.sub('\\b((?:https?:(?:\\/{1,3}|[a-zA-Z0-9%])|[a-zA-Z0-9.\\-]+[.](?:com|co|ru|net|org|edu|gov|it)[\\w/-]*\\b\\/?(?!@)))', '', caption)
        caption = re.sub('\\b((?:www:(?:\\/{1,3}|[a-zA-Z0-9%])|[a-zA-Z0-9.\\-]+[.](?:com|co|ru|net|org|edu|gov|it)[\\w/-]*\\b\\/?(?!@)))', '', caption)
        caption = BeautifulSoup(caption, features='html.parser').text
        caption = re.sub('@[\\w\\d]+\\b', '', caption)
        caption = re.sub('[\\u31c0-\\u31ef]+', '', caption)
        caption = re.sub('[\\u31f0-\\u31ff]+', '', caption)
        caption = re.sub('[\\u3200-\\u32ff]+', '', caption)
        caption = re.sub('[\\u3300-\\u33ff]+', '', caption)
        caption = re.sub('[\\u3400-\\u4dbf]+', '', caption)
        caption = re.sub('[\\u4dc0-\\u4dff]+', '', caption)
        caption = re.sub('[\\u4e00-\\u9fff]+', '', caption)
        caption = re.sub('[\\u002D\\u058A\\u05BE\\u1400\\u1806\\u2010-\\u2015\\u2E17\\u2E1A\\u2E3A\\u2E3B\\u2E40\\u301C\\u3030\\u30A0\\uFE31\\uFE32\\uFE58\\uFE63\\uFF0D]+', '-', caption)
        caption = re.sub('[`´«»“”¨]', '"', caption)
        caption = re.sub('[‘’]', "'", caption)
        caption = re.sub('&quot;?', '', caption)
        caption = re.sub('&amp', '', caption)
        caption = re.sub('\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}', ' ', caption)
        caption = re.sub('\\d:\\d\\d\\s+$', '', caption)
        caption = re.sub('\\\\n', ' ', caption)
        caption = re.sub('#\\d{1,3}\\b', '', caption)
        caption = re.sub('#\\d{5,}\\b', '', caption)
        caption = re.sub('\\b\\d{6,}\\b', '', caption)
        caption = re.sub('[\\S]+\\.(?:png|jpg|jpeg|bmp|webp|eps|pdf|apk|mp4)', '', caption)
        caption = re.sub('[\\"\\\']{2,}', '"', caption)
        caption = re.sub('[\\.]{2,}', ' ', caption)
        caption = re.sub(self.bad_punct_regex, ' ', caption)
        caption = re.sub('\\s+\\.\\s+', ' ', caption)
        regex2 = re.compile('(?:\\-|\\_)')
        if len(re.findall(regex2, caption)) > 3: caption = re.sub(regex2, ' ', caption)
        caption = ftfy.fix_text(caption)
        caption = html.unescape(html.unescape(caption))
        caption = re.sub('\\b[a-zA-Z]{1,3}\\d{3,15}\\b', '', caption)
        caption = re.sub('\\b[a-zA-Z]+\\d+[a-zA-Z]+\\b', '', caption)
        caption = re.sub('\\b\\d+[a-zA-Z]+\\d+\\b', '', caption)
        caption = re.sub('(worldwide\\s+)?(free\\s+)?shipping', '', caption)
        caption = re.sub('(free\\s)?download(\\sfree)?', '', caption)
        caption = re.sub('\\bclick\\b\\s(?:for|on)\\s\\w+', '', caption)
        caption = re.sub('\\b(?:png|jpg|jpeg|bmp|webp|eps|pdf|apk|mp4)(\\simage[s]?)?', '', caption)
        caption = re.sub('\\bpage\\s+\\d+\\b', '', caption)
        caption = re.sub('\\b\\d*[a-zA-Z]+\\d+[a-zA-Z]+\\d+[a-zA-Z\\d]*\\b', ' ', caption)
        caption = re.sub('\\b\\d+\\.?\\d*[xх×]\\d+\\.?\\d*\\b', '', caption)
        caption = re.sub('\\b\\s+\\:\\s+', ': ', caption)
        caption = re.sub('(\\D[,\\./])\\b', '\\1 ', caption)
        caption = re.sub('\\s+', ' ', caption)
        caption.strip()
        caption = re.sub('^[\\"\\\']([\\w\\W]+)[\\"\\\']$', '\\1', caption)
        caption = re.sub("^[\\'\\_,\\-\\:;]", '', caption)
        caption = re.sub("[\\'\\_,\\-\\:\\-\\+]$", '', caption)
        caption = re.sub('^\\.\\S+$', '', caption)
        return caption.strip()
    @torch.no_grad()
    def encode_prompt(self, prompt: Union[str, List[str]], do_classifier_free_guidance: bool=True, num_images_per_prompt: int=1, device: Optional[torch.device]=None,
    negative_prompt: Optional[Union[str, List[str]]]=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, clean_caption: bool=False):
        """Args:"""
        if prompt is not None and negative_prompt is not None:
            if type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
        if device is None: device = self._execution_device
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        max_length = 77
        if prompt_embeds is None:
            prompt = self._text_preprocessing(prompt, clean_caption=clean_caption)
            text_inputs = self.tokenizer(prompt, padding='max_length', max_length=max_length, truncation=True, add_special_tokens=True, return_tensors='pt')
            text_input_ids = text_inputs.input_ids
            untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
            if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer.batch_decode(untruncated_ids[:, max_length - 1:-1])
            attention_mask = text_inputs.attention_mask.to(device)
            prompt_embeds = self.text_encoder(text_input_ids.to(device), attention_mask=attention_mask)
            prompt_embeds = prompt_embeds[0]
        if self.text_encoder is not None: dtype = self.text_encoder.dtype
        elif self.unet is not None: dtype = self.unet.dtype
        else: dtype = None
        prompt_embeds = prompt_embeds.to(dtype=dtype, device=device)
        bs_embed, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_images_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(bs_embed * num_images_per_prompt, seq_len, -1)
        if do_classifier_free_guidance and negative_prompt_embeds is None:
            uncond_tokens: List[str]
            if negative_prompt is None: uncond_tokens = [''] * batch_size
            elif isinstance(negative_prompt, str): uncond_tokens = [negative_prompt]
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            else: uncond_tokens = negative_prompt
            uncond_tokens = self._text_preprocessing(uncond_tokens, clean_caption=clean_caption)
            max_length = prompt_embeds.shape[1]
            uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=max_length, truncation=True, return_attention_mask=True, add_special_tokens=True, return_tensors='pt')
            attention_mask = uncond_input.attention_mask.to(device)
            negative_prompt_embeds = self.text_encoder(uncond_input.input_ids.to(device), attention_mask=attention_mask)
            negative_prompt_embeds = negative_prompt_embeds[0]
        if do_classifier_free_guidance:
            seq_len = negative_prompt_embeds.shape[1]
            negative_prompt_embeds = negative_prompt_embeds.to(dtype=dtype, device=device)
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt, 1)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
        else: negative_prompt_embeds = None
        return (prompt_embeds, negative_prompt_embeds)
    def run_safety_checker(self, image, device, dtype):
        if self.safety_checker is not None:
            safety_checker_input = self.feature_extractor(self.numpy_to_pil(image), return_tensors='pt').to(device)
            image, nsfw_detected, watermark_detected = self.safety_checker(images=image, clip_input=safety_checker_input.pixel_values.to(dtype=dtype))
        else:
            nsfw_detected = None
            watermark_detected = None
        return (image, nsfw_detected, watermark_detected)
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, prompt, image, batch_size, noise_level, callback_steps, negative_prompt=None, prompt_embeds=None, negative_prompt_embeds=None):
        if callback_steps is None or (callback_steps is not None and (not isinstance(callback_steps, int) or callback_steps <= 0)): raise ValueError(f'`callback_steps` has to be a positive integer but is {callback_steps} of type {type(callback_steps)}.')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
        if noise_level < 0 or noise_level >= self.image_noising_scheduler.config.num_train_timesteps: raise ValueError(f'`noise_level`: {noise_level} must be a valid timestep in `self.noising_scheduler`, [0, {self.image_noising_scheduler.config.num_train_timesteps})')
        if isinstance(image, list): check_image_type = image[0]
        else: check_image_type = image
        if not isinstance(check_image_type, torch.Tensor) and (not isinstance(check_image_type, PIL.Image.Image)) and (not isinstance(check_image_type, np.ndarray)): raise ValueError(f'`image` has to be of type `torch.Tensor`, `PIL.Image.Image`, `np.ndarray`, or List[...] but is {type(check_image_type)}')
        if isinstance(image, list): image_batch_size = len(image)
        elif isinstance(image, torch.Tensor): image_batch_size = image.shape[0]
        elif isinstance(image, PIL.Image.Image): image_batch_size = 1
        elif isinstance(image, np.ndarray): image_batch_size = image.shape[0]
        else: assert False
        if batch_size != image_batch_size: raise ValueError(f'image batch size: {image_batch_size} must be same as prompt batch size {batch_size}')
    def prepare_intermediate_images(self, batch_size, num_channels, height, width, dtype, device, generator):
        shape = (batch_size, num_channels, height, width)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        intermediate_images = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        intermediate_images = intermediate_images * self.scheduler.init_noise_sigma
        return intermediate_images
    def preprocess_image(self, image, num_images_per_prompt, device):
        if not isinstance(image, torch.Tensor) and (not isinstance(image, list)): image = [image]
        if isinstance(image[0], PIL.Image.Image):
            image = [np.array(i).astype(np.float32) / 127.5 - 1.0 for i in image]
            image = np.stack(image, axis=0)
            image = torch.from_numpy(image.transpose(0, 3, 1, 2))
        elif isinstance(image[0], np.ndarray):
            image = np.stack(image, axis=0)
            if image.ndim == 5: image = image[0]
            image = torch.from_numpy(image.transpose(0, 3, 1, 2))
        elif isinstance(image, list) and isinstance(image[0], torch.Tensor):
            dims = image[0].ndim
            if dims == 3: image = torch.stack(image, dim=0)
            elif dims == 4: image = torch.concat(image, dim=0)
            else: raise ValueError(f'Image must have 3 or 4 dimensions, instead got {dims}')
        image = image.to(device=device, dtype=self.unet.dtype)
        image = image.repeat_interleave(num_images_per_prompt, dim=0)
        return image
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]]=None, height: int=None, width: int=None, image: Union[PIL.Image.Image, np.ndarray, torch.Tensor]=None, num_inference_steps: int=50,
    timesteps: List[int]=None, guidance_scale: float=4.0, negative_prompt: Optional[Union[str, List[str]]]=None, num_images_per_prompt: Optional[int]=1, eta: float=0.0,
    generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None,
    output_type: Optional[str]='pil', return_dict: bool=True, callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: int=1,
    cross_attention_kwargs: Optional[Dict[str, Any]]=None, noise_level: int=250, clean_caption: bool=True):
        """Examples:"""
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        self.check_inputs(prompt, image, batch_size, noise_level, callback_steps, negative_prompt, prompt_embeds, negative_prompt_embeds)
        height = height or self.unet.config.sample_size
        width = width or self.unet.config.sample_size
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        prompt_embeds, negative_prompt_embeds = self.encode_prompt(prompt, do_classifier_free_guidance, num_images_per_prompt=num_images_per_prompt, device=device, negative_prompt=negative_prompt,
        prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, clean_caption=clean_caption)
        if do_classifier_free_guidance: prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
        if timesteps is not None:
            self.scheduler.set_timesteps(timesteps=timesteps, device=device)
            timesteps = self.scheduler.timesteps
            num_inference_steps = len(timesteps)
        else:
            self.scheduler.set_timesteps(num_inference_steps, device=device)
            timesteps = self.scheduler.timesteps
        if hasattr(self.scheduler, 'set_begin_index'): self.scheduler.set_begin_index(0)
        num_channels = self.unet.config.in_channels // 2
        intermediate_images = self.prepare_intermediate_images(batch_size * num_images_per_prompt, num_channels, height, width, prompt_embeds.dtype, device, generator)
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        image = self.preprocess_image(image, num_images_per_prompt, device)
        upscaled = F.interpolate(image, (height, width), mode='bilinear', align_corners=True)
        noise_level = torch.tensor([noise_level] * upscaled.shape[0], device=upscaled.device)
        noise = randn_tensor(upscaled.shape, generator=generator, device=upscaled.device, dtype=upscaled.dtype)
        upscaled = self.image_noising_scheduler.add_noise(upscaled, noise, timesteps=noise_level)
        if do_classifier_free_guidance: noise_level = torch.cat([noise_level] * 2)
        if hasattr(self, 'text_encoder_offload_hook') and self.text_encoder_offload_hook is not None: self.text_encoder_offload_hook.offload()
        num_warmup_steps = len(timesteps) - num_inference_steps * self.scheduler.order
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                model_input = torch.cat([intermediate_images, upscaled], dim=1)
                model_input = torch.cat([model_input] * 2) if do_classifier_free_guidance else model_input
                model_input = self.scheduler.scale_model_input(model_input, t)
                noise_pred = self.unet(model_input, t, encoder_hidden_states=prompt_embeds, class_labels=noise_level, cross_attention_kwargs=cross_attention_kwargs, return_dict=False)[0]
                if do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred_uncond, _ = noise_pred_uncond.split(model_input.shape[1] // 2, dim=1)
                    noise_pred_text, predicted_variance = noise_pred_text.split(model_input.shape[1] // 2, dim=1)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                    noise_pred = torch.cat([noise_pred, predicted_variance], dim=1)
                if self.scheduler.config.variance_type not in ['learned', 'learned_range']: noise_pred, _ = noise_pred.split(intermediate_images.shape[1], dim=1)
                intermediate_images = self.scheduler.step(noise_pred, t, intermediate_images, **extra_step_kwargs, return_dict=False)[0]
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0):
                    progress_bar.update()
                    if callback is not None and i % callback_steps == 0: callback(i, t, intermediate_images)
        image = intermediate_images
        if output_type == 'pil':
            image = (image / 2 + 0.5).clamp(0, 1)
            image = image.cpu().permute(0, 2, 3, 1).float().numpy()
            image, nsfw_detected, watermark_detected = self.run_safety_checker(image, device, prompt_embeds.dtype)
            image = self.numpy_to_pil(image)
            if self.watermarker is not None: self.watermarker.apply_watermark(image, self.unet.config.sample_size)
        elif output_type == 'pt':
            nsfw_detected = None
            watermark_detected = None
            if hasattr(self, 'unet_offload_hook') and self.unet_offload_hook is not None: self.unet_offload_hook.offload()
        else:
            image = (image / 2 + 0.5).clamp(0, 1)
            image = image.cpu().permute(0, 2, 3, 1).float().numpy()
            image, nsfw_detected, watermark_detected = self.run_safety_checker(image, device, prompt_embeds.dtype)
        self.maybe_free_model_hooks()
        if not return_dict: return (image, nsfw_detected, watermark_detected)
        return IFPipelineOutput(images=image, nsfw_detected=nsfw_detected, watermark_detected=watermark_detected)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
