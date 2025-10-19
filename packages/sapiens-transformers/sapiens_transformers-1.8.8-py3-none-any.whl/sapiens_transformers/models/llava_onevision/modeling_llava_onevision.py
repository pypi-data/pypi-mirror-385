"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union
import numpy as np
import torch
import torch.utils.checkpoint
from torch import nn
from ...activations import ACT2FN
from ...generation import GenerationMixin
from ...image_processing_utils import select_best_resolution
from ...modeling_outputs import ModelOutput
from ...modeling_utils import PreTrainedModel
from ...utils import (add_start_docstrings, logging)
from ..auto import AutoModel, AutoModelForCausalLM
from .configuration_llava_onevision import LlavaOnevisionConfig
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "LlavaNextConfig"
def get_anyres_image_grid_shape(image_size, grid_pinpoints, patch_size):
    if not isinstance(grid_pinpoints, list): raise TypeError("grid_pinpoints should be a list of tuples or lists")
    if not isinstance(image_size, (list, tuple)):
        if not isinstance(image_size, (torch.Tensor, np.ndarray)): raise TypeError(f"image_size invalid type: {type(image_size)} not valid, should be either list, tuple, np.ndarray or tensor")
        image_size = image_size.tolist()
    height, width = select_best_resolution(image_size, grid_pinpoints)
    return height // patch_size, width // patch_size
def image_size_to_num_patches(image_size, grid_pinpoints, patch_size: int):
    if not isinstance(grid_pinpoints, list): raise TypeError("grid_pinpoints should be a list of tuples or lists")
    if not isinstance(image_size, (list, tuple)):
        if not isinstance(image_size, (torch.Tensor, np.ndarray)): raise TypeError(f"image_size invalid type {type(image_size)} with value {image_size}")
        image_size = image_size.tolist()
    best_resolution = select_best_resolution(image_size, grid_pinpoints)
    height, width = best_resolution
    num_patches = 0
    for i in range(0, height, patch_size):
        for j in range(0, width, patch_size): num_patches += 1
    num_patches += 1
    return num_patches
def unpad_image(tensor, original_size):
    if not isinstance(original_size, (list, tuple)):
        if not isinstance(original_size, (torch.Tensor, np.ndarray)): raise TypeError(f"image_size invalid type: {type(original_size)} not valid, should be either list, tuple, np.ndarray or tensor")
        original_size = original_size.tolist()
    original_height, original_width = original_size
    current_height, current_width = tensor.shape[1:]
    original_aspect_ratio = original_width / original_height
    current_aspect_ratio = current_width / current_height
    if original_aspect_ratio > current_aspect_ratio:
        scale_factor = current_width / original_width
        new_height = int(original_height * scale_factor)
        padding = (current_height - new_height) // 2
        unpadded_tensor = tensor[:, padding : current_height - padding, :]
    else:
        scale_factor = current_height / original_height
        new_width = int(original_width * scale_factor)
        padding = (current_width - new_width) // 2
        unpadded_tensor = tensor[:, :, padding : current_width - padding]
    return unpadded_tensor
@dataclass
class LlavaOnevisionCausalLMOutputWithPast(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    logits: torch.FloatTensor = None
    past_key_values: Optional[List[torch.FloatTensor]] = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None
    image_hidden_states: Optional[torch.FloatTensor] = None
    video_hidden_states: Optional[torch.FloatTensor] = None
class LlavaOnevisionMultiModalProjector(nn.Module):
    def __init__(self, config: LlavaOnevisionConfig):
        super().__init__()
        self.linear_1 = nn.Linear(config.vision_config.hidden_size, config.text_config.hidden_size, bias=True)
        self.act = ACT2FN[config.projector_hidden_act]
        self.linear_2 = nn.Linear(config.text_config.hidden_size, config.text_config.hidden_size, bias=True)
    def forward(self, image_features):
        hidden_states = self.linear_1(image_features)
        hidden_states = self.act(hidden_states)
        hidden_states = self.linear_2(hidden_states)
        return hidden_states
LLAVA_ONEVISION_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`LlavaNextConfig`] or [`LlavaNextVisionConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
@add_start_docstrings("The bare LLaVA-Onevision Model outputting raw hidden-states without any specific head on top.", LLAVA_ONEVISION_START_DOCSTRING)
class LlavaOnevisionPreTrainedModel(PreTrainedModel):
    config_class = LlavaOnevisionConfig
    base_model_prefix = "model"
    supports_gradient_checkpointing = True
    _no_split_modules = ["LlavaOnevisionVisionAttention"]
    _skip_keys_device_placement = "past_key_values"
    _supports_flash_attn_2 = True
    _supports_cache_class = True
    _supports_static_cache = False
    _supports_quantized_cache = True
    _supports_sdpa = True
    def _init_weights(self, module):
        std = (self.config.initializer_range if hasattr(self.config, "initializer_range") else self.config.text_config.initializer_range)
        if hasattr(module, "class_embedding"): module.class_embedding.data.normal_(mean=0.0, std=std)
        if isinstance(module, (nn.Linear, nn.Conv2d)):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
LLAVA_ONEVISION_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary. Padding will be ignored by default should you provide
            it.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, image_size, image_size)):
            The tensors corresponding to the input images. Pixel values can be obtained using
            [`AutoImageProcessor`]. See [`LlavaNextImageProcessor.__call__`] for details. [`LlavaProcessor`] uses
            [`LlavaNextImageProcessor`] for processing images.
        image_sizes (`torch.LongTensor` of shape `(batch_size, 2)`, *optional*):
            The sizes of the images in the batch, being (height, width) for each image.
        pixel_values_videos (`torch.FloatTensor` of shape `(batch_size, frames, num_channels, image_size, image_size)):
            The tensors corresponding to the input videos. Pixel values can be obtained using
            [`LlavaNextVideoProcessor`]. See [`LlavaNextVideoProcessor.__call__`] for details. [`LlavaProcessor`] uses
            [`LlavaNextVideoProcessor`] for processing videos.
        image_sizes_videos (`torch.LongTensor` of shape `(batch_size, frames, 2)`, *optional*):
            The sizes of the videos in the batch, being (height, width) for each frame in the video.
        attention_mask (`torch.Tensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            If `past_key_values` is used, optionally only the last `decoder_input_ids` have to be input (see
            `past_key_values`).
            If you want to change padding behavior, you should read [`modeling_opt._prepare_decoder_attention_mask`]
            and modify to your needs. See diagram 1 in [the paper](https://arxiv.org/abs/1910.13461) for more
            information on the default strategy.
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        position_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Indices of positions of each input sequence tokens in the position embeddings. Selected in the range `[0,
            config.n_positions - 1]`. [What are position IDs?](../glossary#position-ids)
        past_key_values (`tuple(tuple(torch.FloatTensor))`, *optional*, returned when `use_cache=True` is passed or when `config.use_cache=True`):
            Tuple of `tuple(torch.FloatTensor)` of length `config.n_layers`, with each tuple having 2 tensors of shape
            `(batch_size, num_heads, sequence_length, embed_size_per_head)` and 2 additional tensors of shape
            `(batch_size, num_heads, encoder_sequence_length, embed_size_per_head)`.
            Contains pre-computed hidden-states (key and values in the self-attention blocks and in the cross-attention
            blocks) that can be used (see `past_key_values` input) to speed up sequential decoding.
            If `past_key_values` are used, the user can optionally input only the last `decoder_input_ids` (those that
            don't have their past key value states given to this model) of shape `(batch_size, 1)` instead of all
            `decoder_input_ids` of shape `(batch_size, sequence_length)`.
        inputs_embeds (`torch.FloatTensor` of shape `(batch_size, sequence_length, hidden_size)`, *optional*):
            Optionally, instead of passing `input_ids` you can choose to directly pass an embedded representation. This
            is useful if you want more control over how to convert `input_ids` indices into associated vectors than the
            model's internal embedding lookup matrix.
        vision_feature_layer (`int`, *optional*, defaults to -2):
            The index of the layer to select the vision feature.
        vision_feature_select_strategy (`str`, *optional*, defaults to `"default"`):
            The feature selection strategy used to select the vision feature from the vision backbone.
            Can be one of `"default"` or `"full"`. If `"default"`, the CLS token is removed from the vision features.
            If `"full"`, the full vision features are used.
        vision_aspect_ratio (`str`, *optional*, defaults to `"anyres_max_9"`):
            Aspect ratio used when processong image features. The default value is "anyres_max_9".
        use_cache (`bool`, *optional*):
            If set to `True`, `past_key_values` key value states are returned and can be used to speed up decoding (see
            `past_key_values`).
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
        cache_position (`torch.LongTensor` of shape `(sequence_length)`, *optional*):
            Indices depicting the position of the input sequence tokens in the sequence. Contrarily to `position_ids`,
            this tensor is not affected by padding. It is used to update the cache in the correct position and to infer
            the complete sequence length.
"""
@add_start_docstrings("The LLaVA-Onevision model which consists of a vision backbone and a language model.", LLAVA_ONEVISION_START_DOCSTRING)
class LlavaOnevisionForConditionalGeneration(LlavaOnevisionPreTrainedModel, GenerationMixin):
    def __init__(self, config: LlavaOnevisionConfig):
        super().__init__(config)
        self.vision_tower = AutoModel.from_config(config.vision_config, attn_implementation=config._attn_implementation)
        self.multi_modal_projector = LlavaOnevisionMultiModalProjector(config)
        embed_std = 1 / math.sqrt(config.text_config.hidden_size)
        self.image_newline = nn.Parameter(torch.randn(config.text_config.hidden_size, dtype=self.dtype) * embed_std)
        self.vocab_size = config.text_config.vocab_size
        self.language_model = AutoModelForCausalLM.from_config(config.text_config, attn_implementation=config._attn_implementation)
        self.post_init()
    def get_input_embeddings(self): return self.language_model.get_input_embeddings()
    def set_input_embeddings(self, value): self.language_model.set_input_embeddings(value)
    def get_output_embeddings(self): return self.language_model.get_output_embeddings()
    def set_output_embeddings(self, new_embeddings): self.language_model.set_output_embeddings(new_embeddings)
    def set_decoder(self, decoder): self.language_model.set_decoder(decoder)
    def get_decoder(self): return self.language_model.get_decoder()
    def tie_weights(self): return self.language_model.tie_weights()
    def pack_image_features(self, image_features, image_sizes, image_newline=None, vision_aspect_ratio="anyres_max_9"):
        new_image_features = []
        feature_lens = []
        for image_idx, image_feature in enumerate(image_features):
            if image_feature.shape[0] > 1:
                base_image_feature = image_feature[0]
                image_feature = image_feature[1:]
                height = width = self.config.vision_config.image_size // self.config.vision_config.patch_size
                if height * width != base_image_feature.shape[0]: raise ValueError("The number of patches is not consistent with the image size.")
                num_patch_height, num_patch_width = get_anyres_image_grid_shape(image_sizes[image_idx], self.config.image_grid_pinpoints, self.config.vision_config.image_size)
                image_feature = image_feature.view(num_patch_height, num_patch_width, height, width, -1)
                image_feature = image_feature.permute(4, 0, 2, 1, 3).contiguous()
                image_feature = image_feature.flatten(1, 2).flatten(2, 3)
                image_feature = unpad_image(image_feature, image_sizes[image_idx])
                max_num_patches = int(vision_aspect_ratio.strip("anyres_max_"))
                channels, curr_height, curr_width = image_feature.shape
                ratio = math.sqrt(curr_height * curr_width / (max_num_patches * height**2))
                if ratio > 1.1:
                    image_feature = image_feature[None]
                    image_feature = nn.functional.interpolate(image_feature, [int(curr_height // ratio), int(curr_width // ratio)], mode="bilinear")[0]
                if image_newline is not None: image_feature = torch.cat((image_feature, image_newline[:, None, None].expand(*image_feature.shape[:-1], 1).to(image_feature.device, image_feature.dtype),), dim=-1)
                image_feature = image_feature.flatten(1, 2).transpose(0, 1)
                image_feature = torch.cat((base_image_feature, image_feature), dim=0)
            else:
                image_feature = image_feature[0]
                if image_newline is not None: image_feature = torch.cat((image_feature, image_newline[None].to(image_feature)), dim=0)
            new_image_features.append(image_feature)
            feature_lens.append(image_feature.size(0))
        image_features = torch.cat(new_image_features, dim=0)
        feature_lens = torch.tensor(feature_lens, dtype=torch.long, device=image_features.device)
        return image_features, feature_lens
    def apply_pooling(self, image_features):
        height = width = self.config.vision_config.image_size // self.config.vision_config.patch_size
        batch_frames, seq_len, dim = image_features.shape
        image_features = image_features.view(batch_frames, height, width, -1)
        image_features = image_features.permute(0, 3, 1, 2).contiguous()
        height, width = image_features.shape[2:]
        scaled_shape = [math.ceil(height / 2), math.ceil(width / 2)]
        image_features = nn.functional.interpolate(image_features, size=scaled_shape, mode="bilinear")
        image_features = image_features.permute(0, 2, 3, 1)
        image_features = image_features.view(batch_frames, -1, dim)
        return image_features
    @add_start_docstrings(LLAVA_ONEVISION_INPUTS_DOCSTRING)
    def forward(self, input_ids: torch.LongTensor = None, pixel_values: torch.FloatTensor = None, image_sizes: Optional[torch.LongTensor] = None, pixel_values_videos: torch.FloatTensor = None,
    image_sizes_videos: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_values: Optional[List[torch.FloatTensor]] = None,
    inputs_embeds: Optional[torch.FloatTensor] = None, vision_feature_layer: Optional[int] = None, vision_feature_select_strategy: Optional[str] = None, vision_aspect_ratio: Optional[str] = None,
    labels: Optional[torch.LongTensor] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None, cache_position: Optional[torch.LongTensor] = None, num_logits_to_keep: int = 0) -> Union[Tuple, LlavaOnevisionCausalLMOutputWithPast]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        vision_feature_layer = (vision_feature_layer if vision_feature_layer is not None else self.config.vision_feature_layer)
        vision_feature_select_strategy = (vision_feature_select_strategy if vision_feature_select_strategy is not None else self.config.vision_feature_select_strategy)
        vision_aspect_ratio = (vision_aspect_ratio if vision_aspect_ratio is not None else self.config.vision_aspect_ratio)
        if (input_ids is None) ^ (inputs_embeds is not None): raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time, and must specify either one")
        if (pixel_values is not None or pixel_values_videos is not None) and inputs_embeds is not None: raise ValueError("You cannot specify both pixel_values/pixel_values_videos and inputs_embeds at the same time, and must specify either one")
        if inputs_embeds is None: inputs_embeds = self.get_input_embeddings()(input_ids)
        if pixel_values is not None:
            image_num_patches = [image_size_to_num_patches(image_size=imsize, grid_pinpoints=self.config.image_grid_pinpoints, patch_size=self.config.vision_config.image_size) for imsize in image_sizes]
            if pixel_values.dim() == 5:
                _pixel_values_list = [pix_val[:num_patch] for pix_val, num_patch in zip(pixel_values, image_num_patches)]
                pixel_values = torch.cat(_pixel_values_list, dim=0)
            elif pixel_values.dim() != 4: raise ValueError(f"pixel_values of shape {pixel_values.shape}, expect to be of 4 or 5 dimensions")
            image_features = self.vision_tower(pixel_values, output_hidden_states=True)
            selected_image_feature = image_features.hidden_states[vision_feature_layer]
            if vision_feature_select_strategy == "default": selected_image_feature = selected_image_feature[:, 1:]
            elif vision_feature_select_strategy == "full": selected_image_feature = selected_image_feature
            image_features = self.multi_modal_projector(selected_image_feature)
            image_features = torch.split(image_features, image_num_patches, dim=0)
            image_features, feature_lens = self.pack_image_features(image_features, image_sizes, image_newline=self.image_newline, vision_aspect_ratio=vision_aspect_ratio)
            special_image_mask = ((input_ids == self.config.image_token_index).unsqueeze(-1).expand_as(inputs_embeds).to(inputs_embeds.device))
            image_features = image_features.to(inputs_embeds.device, inputs_embeds.dtype)
            inputs_embeds = inputs_embeds.masked_scatter(special_image_mask, image_features)
        if pixel_values_videos is not None:
            batch_size, frames, channels, height, width = pixel_values_videos.shape
            pixel_values_videos = pixel_values_videos.view(batch_size * frames, channels, height, width)
            video_features = self.vision_tower(pixel_values_videos, output_hidden_states=True)
            selected_video_feature = video_features.hidden_states[vision_feature_layer]
            if vision_feature_select_strategy == "default": selected_video_feature = selected_video_feature[:, 1:]
            elif vision_feature_select_strategy == "full": selected_video_feature = selected_video_feature
            video_features = self.multi_modal_projector(selected_video_feature)
            video_features = self.apply_pooling(video_features)
            video_features = video_features.reshape(batch_size, frames * video_features.shape[1], -1)
            image_newline = self.image_newline[None, None, :].repeat(batch_size, 1, 1).to(video_features.device)
            video_features = torch.cat((video_features, image_newline), dim=1)
            video_features = video_features.flatten(0, 1)
            special_video_mask = ((input_ids == self.config.video_token_index).unsqueeze(-1).expand_as(inputs_embeds).to(inputs_embeds.device))
            video_features = video_features.to(inputs_embeds.device, inputs_embeds.dtype)
            inputs_embeds = inputs_embeds.masked_scatter(special_video_mask, video_features)
        outputs = self.language_model(attention_mask=attention_mask, position_ids=position_ids, past_key_values=past_key_values, inputs_embeds=inputs_embeds, use_cache=use_cache,
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, cache_position=cache_position, num_logits_to_keep=num_logits_to_keep)
        logits = outputs[0]
        loss = None
        if labels is not None:
            if attention_mask is not None:
                shift_attention_mask = attention_mask[..., 1:]
                shift_logits = logits[..., :-1, :][shift_attention_mask.to(logits.device) != 0].contiguous()
                shift_labels = labels[..., 1:][shift_attention_mask.to(labels.device) != 0].contiguous()
            else:
                shift_logits = logits[..., :-1, :].contiguous()
                shift_labels = labels[..., 1:].contiguous()
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1).to(shift_logits.device))
        if not return_dict:
            output = (logits,) + outputs[1:]
            return (loss,) + output if loss is not None else output
        return LlavaOnevisionCausalLMOutputWithPast(loss=loss, logits=logits, past_key_values=outputs.past_key_values, hidden_states=outputs.hidden_states,
        attentions=outputs.attentions, image_hidden_states=image_features if pixel_values is not None else None, video_hidden_states=video_features if pixel_values_videos is not None else None)
    def prepare_inputs_for_generation(self, input_ids, past_key_values=None, inputs_embeds=None, pixel_values=None, image_sizes=None, pixel_values_videos=None,
    image_sizes_videos=None, attention_mask=None, cache_position=None, num_logits_to_keep=None, **kwargs):
        model_inputs = self.language_model.prepare_inputs_for_generation(input_ids, past_key_values=past_key_values, inputs_embeds=inputs_embeds, attention_mask=attention_mask,
        cache_position=cache_position, num_logits_to_keep=num_logits_to_keep, **kwargs)
        if cache_position[0] == 0:
            model_inputs["pixel_values"] = pixel_values
            model_inputs["image_sizes"] = image_sizes
            model_inputs["pixel_values_videos"] = pixel_values_videos
            model_inputs["image_sizes_videos"] = image_sizes_videos
        return model_inputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
