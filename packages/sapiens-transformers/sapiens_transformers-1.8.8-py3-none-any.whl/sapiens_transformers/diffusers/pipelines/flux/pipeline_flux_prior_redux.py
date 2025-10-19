'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import List, Optional, Union
import torch
from PIL import Image
from sapiens_transformers import CLIPTextModel, CLIPTokenizer, SiglipImageProcessor, SiglipVisionModel, T5EncoderModel, T5TokenizerFast
from ...image_processor import PipelineImageInput
from ...loaders import FluxLoraLoaderMixin, TextualInversionLoaderMixin
from ...utils import USE_PEFT_BACKEND, is_torch_xla_available, replace_example_docstring, scale_lora_layers, unscale_lora_layers
from ..pipeline_utils import DiffusionPipeline
from .modeling_flux import ReduxImageEncoder
from .pipeline_output import FluxPriorReduxPipelineOutput
if is_torch_xla_available(): XLA_AVAILABLE = True
else: XLA_AVAILABLE = False
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import FluxPriorReduxPipeline, FluxPipeline\n        >>> from sapiens_transformers.diffusers.utils import load_image\n\n        >>> device = "cuda"\n        >>> dtype = torch.bfloat16\n\n        >>> repo_redux = "black-forest-labs/FLUX.1-Redux-dev"\n        >>> repo_base = "black-forest-labs/FLUX.1-dev"\n        >>> pipe_prior_redux = FluxPriorReduxPipeline.from_pretrained(repo_redux, torch_dtype=dtype).to(device)\n        >>> pipe = FluxPipeline.from_pretrained(\n        ...     repo_base, text_encoder=None, text_encoder_2=None, torch_dtype=torch.bfloat16\n        ... ).to(device)\n\n        >>> image = load_image(\n        ...     "https://huggingface.co/datasets/YiYiXu/testing-images/resolve/main/style_ziggy/img5.png"\n        ... )\n        >>> pipe_prior_output = pipe_prior_redux(image)\n        >>> images = pipe(\n        ...     guidance_scale=2.5,\n        ...     num_inference_steps=50,\n        ...     generator=torch.Generator("cpu").manual_seed(0),\n        ...     **pipe_prior_output,\n        ... ).images\n        >>> images[0].save("flux-redux.png")\n        ```\n'
class FluxPriorReduxPipeline(DiffusionPipeline):
    """Args:"""
    model_cpu_offload_seq = 'image_encoder->image_embedder'
    _optional_components = ['text_encoder', 'tokenizer', 'text_encoder_2', 'tokenizer_2']
    _callback_tensor_inputs = []
    def __init__(self, image_encoder: SiglipVisionModel, feature_extractor: SiglipImageProcessor, image_embedder: ReduxImageEncoder, text_encoder: CLIPTextModel=None, tokenizer: CLIPTokenizer=None,
    text_encoder_2: T5EncoderModel=None, tokenizer_2: T5TokenizerFast=None):
        super().__init__()
        self.register_modules(image_encoder=image_encoder, feature_extractor=feature_extractor, image_embedder=image_embedder, text_encoder=text_encoder, tokenizer=tokenizer,
        text_encoder_2=text_encoder_2, tokenizer_2=tokenizer_2)
        self.tokenizer_max_length = self.tokenizer.model_max_length if hasattr(self, 'tokenizer') and self.tokenizer is not None else 77
    def check_inputs(self, image, prompt, prompt_2, prompt_embeds=None, pooled_prompt_embeds=None, prompt_embeds_scale=1.0, pooled_prompt_embeds_scale=1.0):
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt_2 is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt_2`: {prompt_2} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        elif prompt_2 is not None and (not isinstance(prompt_2, str) and (not isinstance(prompt_2, list))): raise ValueError(f'`prompt_2` has to be of type `str` or `list` but is {type(prompt_2)}')
        if prompt is not None and (isinstance(prompt, list) and isinstance(image, list) and (len(prompt) != len(image))): raise ValueError(f'number of prompts must be equal to number of images, but {len(prompt)} prompts were provided and {len(image)} images')
        if prompt_embeds is not None and pooled_prompt_embeds is None: raise ValueError('If `prompt_embeds` are provided, `pooled_prompt_embeds` also have to be passed. Make sure to generate `pooled_prompt_embeds` from the same text encoder that was used to generate `prompt_embeds`.')
        if isinstance(prompt_embeds_scale, list) and (isinstance(image, list) and len(prompt_embeds_scale) != len(image)): raise ValueError(f'number of weights must be equal to number of images, but {len(prompt_embeds_scale)} weights were provided and {len(image)} images')
    def encode_image(self, image, device, num_images_per_prompt):
        dtype = next(self.image_encoder.parameters()).dtype
        image = self.feature_extractor.preprocess(images=image, do_resize=True, return_tensors='pt', do_convert_rgb=True)
        image = image.to(device=device, dtype=dtype)
        image_enc_hidden_states = self.image_encoder(**image).last_hidden_state
        image_enc_hidden_states = image_enc_hidden_states.repeat_interleave(num_images_per_prompt, dim=0)
        return image_enc_hidden_states
    def _get_t5_prompt_embeds(self, prompt: Union[str, List[str]]=None, num_images_per_prompt: int=1, max_sequence_length: int=512, device: Optional[torch.device]=None, dtype: Optional[torch.dtype]=None):
        device = device or self._execution_device
        dtype = dtype or self.text_encoder.dtype
        prompt = [prompt] if isinstance(prompt, str) else prompt
        batch_size = len(prompt)
        if isinstance(self, TextualInversionLoaderMixin): prompt = self.maybe_convert_prompt(prompt, self.tokenizer_2)
        text_inputs = self.tokenizer_2(prompt, padding='max_length', max_length=max_sequence_length, truncation=True, return_length=False, return_overflowing_tokens=False, return_tensors='pt')
        text_input_ids = text_inputs.input_ids
        untruncated_ids = self.tokenizer_2(prompt, padding='longest', return_tensors='pt').input_ids
        if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer_2.batch_decode(untruncated_ids[:, self.tokenizer_max_length - 1:-1])
        prompt_embeds = self.text_encoder_2(text_input_ids.to(device), output_hidden_states=False)[0]
        dtype = self.text_encoder_2.dtype
        prompt_embeds = prompt_embeds.to(dtype=dtype, device=device)
        _, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_images_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
        return prompt_embeds
    def _get_clip_prompt_embeds(self, prompt: Union[str, List[str]], num_images_per_prompt: int=1, device: Optional[torch.device]=None):
        device = device or self._execution_device
        prompt = [prompt] if isinstance(prompt, str) else prompt
        batch_size = len(prompt)
        if isinstance(self, TextualInversionLoaderMixin): prompt = self.maybe_convert_prompt(prompt, self.tokenizer)
        text_inputs = self.tokenizer(prompt, padding='max_length', max_length=self.tokenizer_max_length, truncation=True, return_overflowing_tokens=False, return_length=False, return_tensors='pt')
        text_input_ids = text_inputs.input_ids
        untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
        if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer.batch_decode(untruncated_ids[:, self.tokenizer_max_length - 1:-1])
        prompt_embeds = self.text_encoder(text_input_ids.to(device), output_hidden_states=False)
        prompt_embeds = prompt_embeds.pooler_output
        prompt_embeds = prompt_embeds.to(dtype=self.text_encoder.dtype, device=device)
        prompt_embeds = prompt_embeds.repeat(1, num_images_per_prompt)
        prompt_embeds = prompt_embeds.view(batch_size * num_images_per_prompt, -1)
        return prompt_embeds
    def encode_prompt(self, prompt: Union[str, List[str]], prompt_2: Union[str, List[str]], device: Optional[torch.device]=None, num_images_per_prompt: int=1, prompt_embeds: Optional[torch.FloatTensor]=None,
    pooled_prompt_embeds: Optional[torch.FloatTensor]=None, max_sequence_length: int=512, lora_scale: Optional[float]=None):
        """Args:"""
        device = device or self._execution_device
        if lora_scale is not None and isinstance(self, FluxLoraLoaderMixin):
            self._lora_scale = lora_scale
            if self.text_encoder is not None and USE_PEFT_BACKEND: scale_lora_layers(self.text_encoder, lora_scale)
            if self.text_encoder_2 is not None and USE_PEFT_BACKEND: scale_lora_layers(self.text_encoder_2, lora_scale)
        prompt = [prompt] if isinstance(prompt, str) else prompt
        if prompt_embeds is None:
            prompt_2 = prompt_2 or prompt
            prompt_2 = [prompt_2] if isinstance(prompt_2, str) else prompt_2
            pooled_prompt_embeds = self._get_clip_prompt_embeds(prompt=prompt, device=device, num_images_per_prompt=num_images_per_prompt)
            prompt_embeds = self._get_t5_prompt_embeds(prompt=prompt_2, num_images_per_prompt=num_images_per_prompt, max_sequence_length=max_sequence_length, device=device)
        if self.text_encoder is not None:
            if isinstance(self, FluxLoraLoaderMixin) and USE_PEFT_BACKEND: unscale_lora_layers(self.text_encoder, lora_scale)
        if self.text_encoder_2 is not None:
            if isinstance(self, FluxLoraLoaderMixin) and USE_PEFT_BACKEND: unscale_lora_layers(self.text_encoder_2, lora_scale)
        dtype = self.text_encoder.dtype if self.text_encoder is not None else self.transformer.dtype
        text_ids = torch.zeros(prompt_embeds.shape[1], 3).to(device=device, dtype=dtype)
        return (prompt_embeds, pooled_prompt_embeds, text_ids)
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, image: PipelineImageInput, prompt: Union[str, List[str]]=None, prompt_2: Optional[Union[str, List[str]]]=None, prompt_embeds: Optional[torch.FloatTensor]=None,
    pooled_prompt_embeds: Optional[torch.FloatTensor]=None, prompt_embeds_scale: Optional[Union[float, List[float]]]=1.0, pooled_prompt_embeds_scale: Optional[Union[float, List[float]]]=1.0, return_dict: bool=True):
        """Examples:"""
        self.check_inputs(image, prompt, prompt_2, prompt_embeds=prompt_embeds, pooled_prompt_embeds=pooled_prompt_embeds, prompt_embeds_scale=prompt_embeds_scale, pooled_prompt_embeds_scale=pooled_prompt_embeds_scale)
        if image is not None and isinstance(image, Image.Image): batch_size = 1
        elif image is not None and isinstance(image, list): batch_size = len(image)
        else: batch_size = image.shape[0]
        if prompt is not None and isinstance(prompt, str): prompt = batch_size * [prompt]
        if isinstance(prompt_embeds_scale, float): prompt_embeds_scale = batch_size * [prompt_embeds_scale]
        if isinstance(pooled_prompt_embeds_scale, float): pooled_prompt_embeds_scale = batch_size * [pooled_prompt_embeds_scale]
        device = self._execution_device
        image_latents = self.encode_image(image, device, 1)
        image_embeds = self.image_embedder(image_latents).image_embeds
        image_embeds = image_embeds.to(device=device)
        if hasattr(self, 'text_encoder') and self.text_encoder is not None: prompt_embeds, pooled_prompt_embeds, _ = self.encode_prompt(prompt=prompt, prompt_2=prompt_2, prompt_embeds=prompt_embeds,
        pooled_prompt_embeds=pooled_prompt_embeds, device=device, num_images_per_prompt=1, max_sequence_length=512, lora_scale=None)
        else:
            prompt_embeds = torch.zeros((batch_size, 512, 4096), device=device, dtype=image_embeds.dtype)
            pooled_prompt_embeds = torch.zeros((batch_size, 768), device=device, dtype=image_embeds.dtype)
        prompt_embeds = torch.cat([prompt_embeds, image_embeds], dim=1)
        prompt_embeds *= torch.tensor(prompt_embeds_scale, device=device, dtype=image_embeds.dtype)[:, None, None]
        pooled_prompt_embeds *= torch.tensor(pooled_prompt_embeds_scale, device=device, dtype=image_embeds.dtype)[:, None]
        prompt_embeds = torch.sum(prompt_embeds, dim=0, keepdim=True)
        pooled_prompt_embeds = torch.sum(pooled_prompt_embeds, dim=0, keepdim=True)
        self.maybe_free_model_hooks()
        if not return_dict: return (prompt_embeds, pooled_prompt_embeds)
        return FluxPriorReduxPipelineOutput(prompt_embeds=prompt_embeds, pooled_prompt_embeds=pooled_prompt_embeds)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
