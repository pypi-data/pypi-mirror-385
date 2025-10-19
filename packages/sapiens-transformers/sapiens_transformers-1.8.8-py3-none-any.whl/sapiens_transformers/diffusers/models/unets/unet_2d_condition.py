'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..embeddings import (GaussianFourierProjection, GLIGENTextBoundingboxProjection, ImageHintTimeEmbedding, ImageProjection, ImageTimeEmbedding, TextImageProjection,
TextImageTimeEmbedding, TextTimeEmbedding, TimestepEmbedding, Timesteps)
from ..attention_processor import ADDED_KV_ATTENTION_PROCESSORS, CROSS_ATTENTION_PROCESSORS, Attention, AttentionProcessor, AttnAddedKVProcessor, AttnProcessor, FusedAttnProcessor2_0
from ...utils import USE_PEFT_BACKEND, BaseOutput, deprecate, scale_lora_layers, unscale_lora_layers
from .unet_2d_blocks import get_down_block, get_mid_block, get_up_block
from ...loaders import PeftAdapterMixin, UNet2DConditionLoadersMixin
from ...configuration_utils import ConfigMixin, register_to_config
from ...loaders.single_file_model import FromOriginalModelMixin
from typing import Any, Dict, List, Optional, Tuple, Union
from ..activations import get_activation
from ..modeling_utils import ModelMixin
from dataclasses import dataclass
import torch.utils.checkpoint
import torch.nn as nn
import torch
@dataclass
class UNet2DConditionOutput(BaseOutput):
    """Args:"""
    sample: torch.Tensor = None
class UNet2DConditionModel(ModelMixin, ConfigMixin, FromOriginalModelMixin, UNet2DConditionLoadersMixin, PeftAdapterMixin):
    _supports_gradient_checkpointing = True
    _no_split_modules = ['BasicTransformerBlock', 'ResnetBlock2D', 'CrossAttnUpBlock2D']
    @register_to_config
    def __init__(self, sample_size: Optional[Union[int, Tuple[int, int]]]=None, in_channels: int=4, out_channels: int=4, center_input_sample: bool=False, flip_sin_to_cos: bool=True, freq_shift: int=0,
    down_block_types: Tuple[str]=('CrossAttnDownBlock2D', 'CrossAttnDownBlock2D', 'CrossAttnDownBlock2D', 'DownBlock2D'), mid_block_type: Optional[str]='UNetMidBlock2DCrossAttn',
    up_block_types: Tuple[str]=('UpBlock2D', 'CrossAttnUpBlock2D', 'CrossAttnUpBlock2D', 'CrossAttnUpBlock2D'), only_cross_attention: Union[bool, Tuple[bool]]=False,
    block_out_channels: Tuple[int]=(320, 640, 1280, 1280), layers_per_block: Union[int, Tuple[int]]=2, downsample_padding: int=1, mid_block_scale_factor: float=1,
    dropout: float=0.0, act_fn: str='silu', norm_num_groups: Optional[int]=32, norm_eps: float=1e-05, cross_attention_dim: Union[int, Tuple[int]]=1280,
    transformer_layers_per_block: Union[int, Tuple[int], Tuple[Tuple]]=1, reverse_transformer_layers_per_block: Optional[Tuple[Tuple[int]]]=None,
    encoder_hid_dim: Optional[int]=None, encoder_hid_dim_type: Optional[str]=None, attention_head_dim: Union[int, Tuple[int]]=8, num_attention_heads: Optional[Union[int, Tuple[int]]]=None,
    dual_cross_attention: bool=False, use_linear_projection: bool=False, class_embed_type: Optional[str]=None, addition_embed_type: Optional[str]=None, addition_time_embed_dim: Optional[int]=None,
    num_class_embeds: Optional[int]=None, upcast_attention: bool=False, resnet_time_scale_shift: str='default', resnet_skip_time_act: bool=False, resnet_out_scale_factor: float=1.0,
    time_embedding_type: str='positional', time_embedding_dim: Optional[int]=None, time_embedding_act_fn: Optional[str]=None, timestep_post_act: Optional[str]=None, time_cond_proj_dim: Optional[int]=None,
    conv_in_kernel: int=3, conv_out_kernel: int=3, projection_class_embeddings_input_dim: Optional[int]=None, attention_type: str='default', class_embeddings_concat: bool=False,
    mid_block_only_cross_attention: Optional[bool]=None, cross_attention_norm: Optional[str]=None, addition_embed_type_num_heads: int=64):
        super().__init__()
        self.sample_size = sample_size
        if num_attention_heads is not None: raise ValueError('At the moment it is not possible to define the number of attention heads via `num_attention_heads` because of a naming issue as described in https://github.com/huggingface/diffusers/issues/2011#issuecomment-1547958131. Passing `num_attention_heads` will only be supported in diffusers v0.19.')
        num_attention_heads = num_attention_heads or attention_head_dim
        self._check_config(down_block_types=down_block_types, up_block_types=up_block_types, only_cross_attention=only_cross_attention, block_out_channels=block_out_channels, layers_per_block=layers_per_block,
        cross_attention_dim=cross_attention_dim, transformer_layers_per_block=transformer_layers_per_block, reverse_transformer_layers_per_block=reverse_transformer_layers_per_block,
        attention_head_dim=attention_head_dim, num_attention_heads=num_attention_heads)
        conv_in_padding = (conv_in_kernel - 1) // 2
        self.conv_in = nn.Conv2d(in_channels, block_out_channels[0], kernel_size=conv_in_kernel, padding=conv_in_padding)
        time_embed_dim, timestep_input_dim = self._set_time_proj(time_embedding_type, block_out_channels=block_out_channels, flip_sin_to_cos=flip_sin_to_cos, freq_shift=freq_shift, time_embedding_dim=time_embedding_dim)
        self.time_embedding = TimestepEmbedding(timestep_input_dim, time_embed_dim, act_fn=act_fn, post_act_fn=timestep_post_act, cond_proj_dim=time_cond_proj_dim)
        self._set_encoder_hid_proj(encoder_hid_dim_type, cross_attention_dim=cross_attention_dim, encoder_hid_dim=encoder_hid_dim)
        self._set_class_embedding(class_embed_type, act_fn=act_fn, num_class_embeds=num_class_embeds, projection_class_embeddings_input_dim=projection_class_embeddings_input_dim,
        time_embed_dim=time_embed_dim, timestep_input_dim=timestep_input_dim)
        self._set_add_embedding(addition_embed_type, addition_embed_type_num_heads=addition_embed_type_num_heads, addition_time_embed_dim=addition_time_embed_dim,
        cross_attention_dim=cross_attention_dim, encoder_hid_dim=encoder_hid_dim, flip_sin_to_cos=flip_sin_to_cos, freq_shift=freq_shift,
        projection_class_embeddings_input_dim=projection_class_embeddings_input_dim, time_embed_dim=time_embed_dim)
        if time_embedding_act_fn is None: self.time_embed_act = None
        else: self.time_embed_act = get_activation(time_embedding_act_fn)
        self.down_blocks = nn.ModuleList([])
        self.up_blocks = nn.ModuleList([])
        if isinstance(only_cross_attention, bool):
            if mid_block_only_cross_attention is None: mid_block_only_cross_attention = only_cross_attention
            only_cross_attention = [only_cross_attention] * len(down_block_types)
        if mid_block_only_cross_attention is None: mid_block_only_cross_attention = False
        if isinstance(num_attention_heads, int): num_attention_heads = (num_attention_heads,) * len(down_block_types)
        if isinstance(attention_head_dim, int): attention_head_dim = (attention_head_dim,) * len(down_block_types)
        if isinstance(cross_attention_dim, int): cross_attention_dim = (cross_attention_dim,) * len(down_block_types)
        if isinstance(layers_per_block, int): layers_per_block = [layers_per_block] * len(down_block_types)
        if isinstance(transformer_layers_per_block, int): transformer_layers_per_block = [transformer_layers_per_block] * len(down_block_types)
        if class_embeddings_concat: blocks_time_embed_dim = time_embed_dim * 2
        else: blocks_time_embed_dim = time_embed_dim
        output_channel = block_out_channels[0]
        for i, down_block_type in enumerate(down_block_types):
            input_channel = output_channel
            output_channel = block_out_channels[i]
            is_final_block = i == len(block_out_channels) - 1
            down_block = get_down_block(down_block_type, num_layers=layers_per_block[i], transformer_layers_per_block=transformer_layers_per_block[i], in_channels=input_channel,
            out_channels=output_channel, temb_channels=blocks_time_embed_dim, add_downsample=not is_final_block, resnet_eps=norm_eps, resnet_act_fn=act_fn, resnet_groups=norm_num_groups,
            cross_attention_dim=cross_attention_dim[i], num_attention_heads=num_attention_heads[i], downsample_padding=downsample_padding, dual_cross_attention=dual_cross_attention,
            use_linear_projection=use_linear_projection, only_cross_attention=only_cross_attention[i], upcast_attention=upcast_attention, resnet_time_scale_shift=resnet_time_scale_shift,
            attention_type=attention_type, resnet_skip_time_act=resnet_skip_time_act, resnet_out_scale_factor=resnet_out_scale_factor, cross_attention_norm=cross_attention_norm,
            attention_head_dim=attention_head_dim[i] if attention_head_dim[i] is not None else output_channel, dropout=dropout)
            self.down_blocks.append(down_block)
        self.mid_block = get_mid_block(mid_block_type, temb_channels=blocks_time_embed_dim, in_channels=block_out_channels[-1], resnet_eps=norm_eps, resnet_act_fn=act_fn,
        resnet_groups=norm_num_groups, output_scale_factor=mid_block_scale_factor, transformer_layers_per_block=transformer_layers_per_block[-1], num_attention_heads=num_attention_heads[-1],
        cross_attention_dim=cross_attention_dim[-1], dual_cross_attention=dual_cross_attention, use_linear_projection=use_linear_projection, mid_block_only_cross_attention=mid_block_only_cross_attention,
        upcast_attention=upcast_attention, resnet_time_scale_shift=resnet_time_scale_shift, attention_type=attention_type, resnet_skip_time_act=resnet_skip_time_act, cross_attention_norm=cross_attention_norm,
        attention_head_dim=attention_head_dim[-1], dropout=dropout)
        self.num_upsamplers = 0
        reversed_block_out_channels = list(reversed(block_out_channels))
        reversed_num_attention_heads = list(reversed(num_attention_heads))
        reversed_layers_per_block = list(reversed(layers_per_block))
        reversed_cross_attention_dim = list(reversed(cross_attention_dim))
        reversed_transformer_layers_per_block = list(reversed(transformer_layers_per_block)) if reverse_transformer_layers_per_block is None else reverse_transformer_layers_per_block
        only_cross_attention = list(reversed(only_cross_attention))
        output_channel = reversed_block_out_channels[0]
        for i, up_block_type in enumerate(up_block_types):
            is_final_block = i == len(block_out_channels) - 1
            prev_output_channel = output_channel
            output_channel = reversed_block_out_channels[i]
            input_channel = reversed_block_out_channels[min(i + 1, len(block_out_channels) - 1)]
            if not is_final_block:
                add_upsample = True
                self.num_upsamplers += 1
            else: add_upsample = False
            up_block = get_up_block(up_block_type, num_layers=reversed_layers_per_block[i] + 1, transformer_layers_per_block=reversed_transformer_layers_per_block[i], in_channels=input_channel,
            out_channels=output_channel, prev_output_channel=prev_output_channel, temb_channels=blocks_time_embed_dim, add_upsample=add_upsample, resnet_eps=norm_eps, resnet_act_fn=act_fn,
            resolution_idx=i, resnet_groups=norm_num_groups, cross_attention_dim=reversed_cross_attention_dim[i], num_attention_heads=reversed_num_attention_heads[i], dual_cross_attention=dual_cross_attention,
            use_linear_projection=use_linear_projection, only_cross_attention=only_cross_attention[i], upcast_attention=upcast_attention, resnet_time_scale_shift=resnet_time_scale_shift,
            attention_type=attention_type, resnet_skip_time_act=resnet_skip_time_act, resnet_out_scale_factor=resnet_out_scale_factor, cross_attention_norm=cross_attention_norm,
            attention_head_dim=attention_head_dim[i] if attention_head_dim[i] is not None else output_channel, dropout=dropout)
            self.up_blocks.append(up_block)
        if norm_num_groups is not None:
            self.conv_norm_out = nn.GroupNorm(num_channels=block_out_channels[0], num_groups=norm_num_groups, eps=norm_eps)
            self.conv_act = get_activation(act_fn)
        else:
            self.conv_norm_out = None
            self.conv_act = None
        conv_out_padding = (conv_out_kernel - 1) // 2
        self.conv_out = nn.Conv2d(block_out_channels[0], out_channels, kernel_size=conv_out_kernel, padding=conv_out_padding)
        self._set_pos_net_if_use_gligen(attention_type=attention_type, cross_attention_dim=cross_attention_dim)
    def _check_config(self, down_block_types: Tuple[str], up_block_types: Tuple[str], only_cross_attention: Union[bool, Tuple[bool]], block_out_channels: Tuple[int], layers_per_block: Union[int, Tuple[int]],
    cross_attention_dim: Union[int, Tuple[int]], transformer_layers_per_block: Union[int, Tuple[int], Tuple[Tuple[int]]], reverse_transformer_layers_per_block: bool, attention_head_dim: int, num_attention_heads: Optional[Union[int, Tuple[int]]]):
        if len(down_block_types) != len(up_block_types): raise ValueError(f'Must provide the same number of `down_block_types` as `up_block_types`. `down_block_types`: {down_block_types}. `up_block_types`: {up_block_types}.')
        if len(block_out_channels) != len(down_block_types): raise ValueError(f'Must provide the same number of `block_out_channels` as `down_block_types`. `block_out_channels`: {block_out_channels}. `down_block_types`: {down_block_types}.')
        if not isinstance(only_cross_attention, bool) and len(only_cross_attention) != len(down_block_types): raise ValueError(f'Must provide the same number of `only_cross_attention` as `down_block_types`. `only_cross_attention`: {only_cross_attention}. `down_block_types`: {down_block_types}.')
        if not isinstance(num_attention_heads, int) and len(num_attention_heads) != len(down_block_types): raise ValueError(f'Must provide the same number of `num_attention_heads` as `down_block_types`. `num_attention_heads`: {num_attention_heads}. `down_block_types`: {down_block_types}.')
        if not isinstance(attention_head_dim, int) and len(attention_head_dim) != len(down_block_types): raise ValueError(f'Must provide the same number of `attention_head_dim` as `down_block_types`. `attention_head_dim`: {attention_head_dim}. `down_block_types`: {down_block_types}.')
        if isinstance(cross_attention_dim, list) and len(cross_attention_dim) != len(down_block_types): raise ValueError(f'Must provide the same number of `cross_attention_dim` as `down_block_types`. `cross_attention_dim`: {cross_attention_dim}. `down_block_types`: {down_block_types}.')
        if not isinstance(layers_per_block, int) and len(layers_per_block) != len(down_block_types): raise ValueError(f'Must provide the same number of `layers_per_block` as `down_block_types`. `layers_per_block`: {layers_per_block}. `down_block_types`: {down_block_types}.')
        if isinstance(transformer_layers_per_block, list) and reverse_transformer_layers_per_block is None:
            for layer_number_per_block in transformer_layers_per_block:
                if isinstance(layer_number_per_block, list): raise ValueError("Must provide 'reverse_transformer_layers_per_block` if using asymmetrical UNet.")
    def _set_time_proj(self, time_embedding_type: str, block_out_channels: int, flip_sin_to_cos: bool, freq_shift: float, time_embedding_dim: int) -> Tuple[int, int]:
        if time_embedding_type == 'fourier':
            time_embed_dim = time_embedding_dim or block_out_channels[0] * 2
            if time_embed_dim % 2 != 0: raise ValueError(f'`time_embed_dim` should be divisible by 2, but is {time_embed_dim}.')
            self.time_proj = GaussianFourierProjection(time_embed_dim // 2, set_W_to_weight=False, log=False, flip_sin_to_cos=flip_sin_to_cos)
            timestep_input_dim = time_embed_dim
        elif time_embedding_type == 'positional':
            time_embed_dim = time_embedding_dim or block_out_channels[0] * 4
            self.time_proj = Timesteps(block_out_channels[0], flip_sin_to_cos, freq_shift)
            timestep_input_dim = block_out_channels[0]
        else: raise ValueError(f'{time_embedding_type} does not exist. Please make sure to use one of `fourier` or `positional`.')
        return (time_embed_dim, timestep_input_dim)
    def _set_encoder_hid_proj(self, encoder_hid_dim_type: Optional[str], cross_attention_dim: Union[int, Tuple[int]], encoder_hid_dim: Optional[int]):
        if encoder_hid_dim_type is None and encoder_hid_dim is not None:
            encoder_hid_dim_type = 'text_proj'
            self.register_to_config(encoder_hid_dim_type=encoder_hid_dim_type)
        if encoder_hid_dim is None and encoder_hid_dim_type is not None: raise ValueError(f'`encoder_hid_dim` has to be defined when `encoder_hid_dim_type` is set to {encoder_hid_dim_type}.')
        if encoder_hid_dim_type == 'text_proj': self.encoder_hid_proj = nn.Linear(encoder_hid_dim, cross_attention_dim)
        elif encoder_hid_dim_type == 'text_image_proj': self.encoder_hid_proj = TextImageProjection(text_embed_dim=encoder_hid_dim, image_embed_dim=cross_attention_dim, cross_attention_dim=cross_attention_dim)
        elif encoder_hid_dim_type == 'image_proj': self.encoder_hid_proj = ImageProjection(image_embed_dim=encoder_hid_dim, cross_attention_dim=cross_attention_dim)
        elif encoder_hid_dim_type is not None: raise ValueError(f"`encoder_hid_dim_type`: {encoder_hid_dim_type} must be None, 'text_proj', 'text_image_proj', or 'image_proj'.")
        else: self.encoder_hid_proj = None
    def _set_class_embedding(self, class_embed_type: Optional[str], act_fn: str, num_class_embeds: Optional[int], projection_class_embeddings_input_dim: Optional[int], time_embed_dim: int, timestep_input_dim: int):
        if class_embed_type is None and num_class_embeds is not None: self.class_embedding = nn.Embedding(num_class_embeds, time_embed_dim)
        elif class_embed_type == 'timestep': self.class_embedding = TimestepEmbedding(timestep_input_dim, time_embed_dim, act_fn=act_fn)
        elif class_embed_type == 'identity': self.class_embedding = nn.Identity(time_embed_dim, time_embed_dim)
        elif class_embed_type == 'projection':
            if projection_class_embeddings_input_dim is None: raise ValueError("`class_embed_type`: 'projection' requires `projection_class_embeddings_input_dim` be set")
            self.class_embedding = TimestepEmbedding(projection_class_embeddings_input_dim, time_embed_dim)
        elif class_embed_type == 'simple_projection':
            if projection_class_embeddings_input_dim is None: raise ValueError("`class_embed_type`: 'simple_projection' requires `projection_class_embeddings_input_dim` be set")
            self.class_embedding = nn.Linear(projection_class_embeddings_input_dim, time_embed_dim)
        else: self.class_embedding = None
    def _set_add_embedding(self, addition_embed_type: str, addition_embed_type_num_heads: int, addition_time_embed_dim: Optional[int], flip_sin_to_cos: bool, freq_shift: float, cross_attention_dim: Optional[int], encoder_hid_dim: Optional[int],
    projection_class_embeddings_input_dim: Optional[int], time_embed_dim: int):
        if addition_embed_type == 'text':
            if encoder_hid_dim is not None: text_time_embedding_from_dim = encoder_hid_dim
            else: text_time_embedding_from_dim = cross_attention_dim
            self.add_embedding = TextTimeEmbedding(text_time_embedding_from_dim, time_embed_dim, num_heads=addition_embed_type_num_heads)
        elif addition_embed_type == 'text_image': self.add_embedding = TextImageTimeEmbedding(text_embed_dim=cross_attention_dim, image_embed_dim=cross_attention_dim, time_embed_dim=time_embed_dim)
        elif addition_embed_type == 'text_time':
            self.add_time_proj = Timesteps(addition_time_embed_dim, flip_sin_to_cos, freq_shift)
            self.add_embedding = TimestepEmbedding(projection_class_embeddings_input_dim, time_embed_dim)
        elif addition_embed_type == 'image': self.add_embedding = ImageTimeEmbedding(image_embed_dim=encoder_hid_dim, time_embed_dim=time_embed_dim)
        elif addition_embed_type == 'image_hint': self.add_embedding = ImageHintTimeEmbedding(image_embed_dim=encoder_hid_dim, time_embed_dim=time_embed_dim)
        elif addition_embed_type is not None: raise ValueError(f"`addition_embed_type`: {addition_embed_type} must be None, 'text', 'text_image', 'text_time', 'image', or 'image_hint'.")
    def _set_pos_net_if_use_gligen(self, attention_type: str, cross_attention_dim: int):
        if attention_type in ['gated', 'gated-text-image']:
            positive_len = 768
            if isinstance(cross_attention_dim, int): positive_len = cross_attention_dim
            elif isinstance(cross_attention_dim, (list, tuple)): positive_len = cross_attention_dim[0]
            feature_type = 'text-only' if attention_type == 'gated' else 'text-image'
            self.position_net = GLIGENTextBoundingboxProjection(positive_len=positive_len, out_dim=cross_attention_dim, feature_type=feature_type)
    @property
    def attn_processors(self) -> Dict[str, AttentionProcessor]:
        """Returns:"""
        processors = {}
        def fn_recursive_add_processors(name: str, module: torch.nn.Module, processors: Dict[str, AttentionProcessor]):
            if hasattr(module, 'get_processor'): processors[f'{name}.processor'] = module.get_processor()
            for sub_name, child in module.named_children(): fn_recursive_add_processors(f'{name}.{sub_name}', child, processors)
            return processors
        for name, module in self.named_children(): fn_recursive_add_processors(name, module, processors)
        return processors
    def set_attn_processor(self, processor: Union[AttentionProcessor, Dict[str, AttentionProcessor]]):
        count = len(self.attn_processors.keys())
        if isinstance(processor, dict) and len(processor) != count: raise ValueError(f'A dict of processors was passed, but the number of processors {len(processor)} does not match the number of attention layers: {count}. Please make sure to pass {count} processor classes.')
        def fn_recursive_attn_processor(name: str, module: torch.nn.Module, processor):
            if hasattr(module, 'set_processor'):
                if not isinstance(processor, dict): module.set_processor(processor)
                else: module.set_processor(processor.pop(f'{name}.processor'))
            for sub_name, child in module.named_children(): fn_recursive_attn_processor(f'{name}.{sub_name}', child, processor)
        for name, module in self.named_children(): fn_recursive_attn_processor(name, module, processor)
    def set_default_attn_processor(self):
        if all((proc.__class__ in ADDED_KV_ATTENTION_PROCESSORS for proc in self.attn_processors.values())): processor = AttnAddedKVProcessor()
        elif all((proc.__class__ in CROSS_ATTENTION_PROCESSORS for proc in self.attn_processors.values())): processor = AttnProcessor()
        else: raise ValueError(f'Cannot call `set_default_attn_processor` when attention processors are of type {next(iter(self.attn_processors.values()))}')
        self.set_attn_processor(processor)
    def set_attention_slice(self, slice_size: Union[str, int, List[int]]='auto'):
        """Args:"""
        sliceable_head_dims = []
        def fn_recursive_retrieve_sliceable_dims(module: torch.nn.Module):
            if hasattr(module, 'set_attention_slice'): sliceable_head_dims.append(module.sliceable_head_dim)
            for child in module.children(): fn_recursive_retrieve_sliceable_dims(child)
        for module in self.children(): fn_recursive_retrieve_sliceable_dims(module)
        num_sliceable_layers = len(sliceable_head_dims)
        if slice_size == 'auto': slice_size = [dim // 2 for dim in sliceable_head_dims]
        elif slice_size == 'max': slice_size = num_sliceable_layers * [1]
        slice_size = num_sliceable_layers * [slice_size] if not isinstance(slice_size, list) else slice_size
        if len(slice_size) != len(sliceable_head_dims): raise ValueError(f'You have provided {len(slice_size)}, but {self.config} has {len(sliceable_head_dims)} different attention layers. Make sure to match `len(slice_size)` to be {len(sliceable_head_dims)}.')
        for i in range(len(slice_size)):
            size = slice_size[i]
            dim = sliceable_head_dims[i]
            if size is not None and size > dim: raise ValueError(f'size {size} has to be smaller or equal to {dim}.')
        def fn_recursive_set_attention_slice(module: torch.nn.Module, slice_size: List[int]):
            if hasattr(module, 'set_attention_slice'): module.set_attention_slice(slice_size.pop())
            for child in module.children(): fn_recursive_set_attention_slice(child, slice_size)
        reversed_slice_size = list(reversed(slice_size))
        for module in self.children(): fn_recursive_set_attention_slice(module, reversed_slice_size)
    def _set_gradient_checkpointing(self, module, value=False):
        if hasattr(module, 'gradient_checkpointing'): module.gradient_checkpointing = value
    def enable_freeu(self, s1: float, s2: float, b1: float, b2: float):
        """Args:"""
        for i, upsample_block in enumerate(self.up_blocks):
            setattr(upsample_block, 's1', s1)
            setattr(upsample_block, 's2', s2)
            setattr(upsample_block, 'b1', b1)
            setattr(upsample_block, 'b2', b2)
    def disable_freeu(self):
        freeu_keys = {'s1', 's2', 'b1', 'b2'}
        for i, upsample_block in enumerate(self.up_blocks):
            for k in freeu_keys:
                if hasattr(upsample_block, k) or getattr(upsample_block, k, None) is not None: setattr(upsample_block, k, None)
    def fuse_qkv_projections(self):
        self.original_attn_processors = None
        for _, attn_processor in self.attn_processors.items():
            if 'Added' in str(attn_processor.__class__.__name__): raise ValueError('`fuse_qkv_projections()` is not supported for models having added KV projections.')
        self.original_attn_processors = self.attn_processors
        for module in self.modules():
            if isinstance(module, Attention): module.fuse_projections(fuse=True)
        self.set_attn_processor(FusedAttnProcessor2_0())
    def unfuse_qkv_projections(self):
        if self.original_attn_processors is not None: self.set_attn_processor(self.original_attn_processors)
    def get_time_embed(self, sample: torch.Tensor, timestep: Union[torch.Tensor, float, int]) -> Optional[torch.Tensor]:
        timesteps = timestep
        if not torch.is_tensor(timesteps):
            is_mps = sample.device.type == 'mps'
            if isinstance(timestep, float): dtype = torch.float32 if is_mps else torch.float64
            else: dtype = torch.int32 if is_mps else torch.int64
            timesteps = torch.tensor([timesteps], dtype=dtype, device=sample.device)
        elif len(timesteps.shape) == 0: timesteps = timesteps[None].to(sample.device)
        timesteps = timesteps.expand(sample.shape[0])
        t_emb = self.time_proj(timesteps)
        t_emb = t_emb.to(dtype=sample.dtype)
        return t_emb
    def get_class_embed(self, sample: torch.Tensor, class_labels: Optional[torch.Tensor]) -> Optional[torch.Tensor]:
        class_emb = None
        if self.class_embedding is not None:
            if class_labels is None: raise ValueError('class_labels should be provided when num_class_embeds > 0')
            if self.config.class_embed_type == 'timestep':
                class_labels = self.time_proj(class_labels)
                class_labels = class_labels.to(dtype=sample.dtype)
            class_emb = self.class_embedding(class_labels).to(dtype=sample.dtype)
        return class_emb
    def get_aug_embed(self, emb: torch.Tensor, encoder_hidden_states: torch.Tensor, added_cond_kwargs: Dict[str, Any]) -> Optional[torch.Tensor]:
        aug_emb = None
        if self.config.addition_embed_type == 'text': aug_emb = self.add_embedding(encoder_hidden_states)
        elif self.config.addition_embed_type == 'text_image':
            if 'image_embeds' not in added_cond_kwargs: raise ValueError(f"{self.__class__} has the config param `addition_embed_type` set to 'text_image' which requires the keyword argument `image_embeds` to be passed in `added_cond_kwargs`")
            image_embs = added_cond_kwargs.get('image_embeds')
            text_embs = added_cond_kwargs.get('text_embeds', encoder_hidden_states)
            aug_emb = self.add_embedding(text_embs, image_embs)
        elif self.config.addition_embed_type == 'text_time':
            if 'text_embeds' not in added_cond_kwargs: raise ValueError(f"{self.__class__} has the config param `addition_embed_type` set to 'text_time' which requires the keyword argument `text_embeds` to be passed in `added_cond_kwargs`")
            text_embeds = added_cond_kwargs.get('text_embeds')
            if 'time_ids' not in added_cond_kwargs: raise ValueError(f"{self.__class__} has the config param `addition_embed_type` set to 'text_time' which requires the keyword argument `time_ids` to be passed in `added_cond_kwargs`")
            time_ids = added_cond_kwargs.get('time_ids')
            time_embeds = self.add_time_proj(time_ids.flatten())
            time_embeds = time_embeds.reshape((text_embeds.shape[0], -1))
            add_embeds = torch.concat([text_embeds, time_embeds], dim=-1)
            add_embeds = add_embeds.to(emb.dtype)
            aug_emb = self.add_embedding(add_embeds)
        elif self.config.addition_embed_type == 'image':
            if 'image_embeds' not in added_cond_kwargs: raise ValueError(f"{self.__class__} has the config param `addition_embed_type` set to 'image' which requires the keyword argument `image_embeds` to be passed in `added_cond_kwargs`")
            image_embs = added_cond_kwargs.get('image_embeds')
            aug_emb = self.add_embedding(image_embs)
        elif self.config.addition_embed_type == 'image_hint':
            if 'image_embeds' not in added_cond_kwargs or 'hint' not in added_cond_kwargs: raise ValueError(f"{self.__class__} has the config param `addition_embed_type` set to 'image_hint' which requires the keyword arguments `image_embeds` and `hint` to be passed in `added_cond_kwargs`")
            image_embs = added_cond_kwargs.get('image_embeds')
            hint = added_cond_kwargs.get('hint')
            aug_emb = self.add_embedding(image_embs, hint)
        return aug_emb
    def process_encoder_hidden_states(self, encoder_hidden_states: torch.Tensor, added_cond_kwargs: Dict[str, Any]) -> torch.Tensor:
        if self.encoder_hid_proj is not None and self.config.encoder_hid_dim_type == 'text_proj': encoder_hidden_states = self.encoder_hid_proj(encoder_hidden_states)
        elif self.encoder_hid_proj is not None and self.config.encoder_hid_dim_type == 'text_image_proj':
            if 'image_embeds' not in added_cond_kwargs: raise ValueError(f"{self.__class__} has the config param `encoder_hid_dim_type` set to 'text_image_proj' which requires the keyword argument `image_embeds` to be passed in `added_cond_kwargs`")
            image_embeds = added_cond_kwargs.get('image_embeds')
            encoder_hidden_states = self.encoder_hid_proj(encoder_hidden_states, image_embeds)
        elif self.encoder_hid_proj is not None and self.config.encoder_hid_dim_type == 'image_proj':
            if 'image_embeds' not in added_cond_kwargs: raise ValueError(f"{self.__class__} has the config param `encoder_hid_dim_type` set to 'image_proj' which requires the keyword argument `image_embeds` to be passed in `added_cond_kwargs`")
            image_embeds = added_cond_kwargs.get('image_embeds')
            encoder_hidden_states = self.encoder_hid_proj(image_embeds)
        elif self.encoder_hid_proj is not None and self.config.encoder_hid_dim_type == 'ip_image_proj':
            if 'image_embeds' not in added_cond_kwargs: raise ValueError(f"{self.__class__} has the config param `encoder_hid_dim_type` set to 'ip_image_proj' which requires the keyword argument `image_embeds` to be passed in `added_cond_kwargs`")
            if hasattr(self, 'text_encoder_hid_proj') and self.text_encoder_hid_proj is not None: encoder_hidden_states = self.text_encoder_hid_proj(encoder_hidden_states)
            image_embeds = added_cond_kwargs.get('image_embeds')
            image_embeds = self.encoder_hid_proj(image_embeds)
            encoder_hidden_states = (encoder_hidden_states, image_embeds)
        return encoder_hidden_states
    def forward(self, sample: torch.Tensor, timestep: Union[torch.Tensor, float, int], encoder_hidden_states: torch.Tensor, class_labels: Optional[torch.Tensor]=None, timestep_cond: Optional[torch.Tensor]=None,
    attention_mask: Optional[torch.Tensor]=None, cross_attention_kwargs: Optional[Dict[str, Any]]=None, added_cond_kwargs: Optional[Dict[str, torch.Tensor]]=None, down_block_additional_residuals: Optional[Tuple[torch.Tensor]]=None,
    mid_block_additional_residual: Optional[torch.Tensor]=None, down_intrablock_additional_residuals: Optional[Tuple[torch.Tensor]]=None, encoder_attention_mask: Optional[torch.Tensor]=None, return_dict: bool=True) -> Union[UNet2DConditionOutput, Tuple]:
        """Returns:"""
        default_overall_up_factor = 2 ** self.num_upsamplers
        forward_upsample_size = False
        upsample_size = None
        for dim in sample.shape[-2:]:
            if dim % default_overall_up_factor != 0:
                forward_upsample_size = True
                break
        if attention_mask is not None:
            attention_mask = (1 - attention_mask.to(sample.dtype)) * -10000.0
            attention_mask = attention_mask.unsqueeze(1)
        if encoder_attention_mask is not None:
            encoder_attention_mask = (1 - encoder_attention_mask.to(sample.dtype)) * -10000.0
            encoder_attention_mask = encoder_attention_mask.unsqueeze(1)
        if self.config.center_input_sample: sample = 2 * sample - 1.0
        t_emb = self.get_time_embed(sample=sample, timestep=timestep)
        emb = self.time_embedding(t_emb, timestep_cond)
        class_emb = self.get_class_embed(sample=sample, class_labels=class_labels)
        if class_emb is not None:
            if self.config.class_embeddings_concat: emb = torch.cat([emb, class_emb], dim=-1)
            else: emb = emb + class_emb
        aug_emb = self.get_aug_embed(emb=emb, encoder_hidden_states=encoder_hidden_states, added_cond_kwargs=added_cond_kwargs)
        if self.config.addition_embed_type == 'image_hint':
            aug_emb, hint = aug_emb
            sample = torch.cat([sample, hint], dim=1)
        emb = emb + aug_emb if aug_emb is not None else emb
        if self.time_embed_act is not None: emb = self.time_embed_act(emb)
        encoder_hidden_states = self.process_encoder_hidden_states(encoder_hidden_states=encoder_hidden_states, added_cond_kwargs=added_cond_kwargs)
        sample = self.conv_in(sample)
        if cross_attention_kwargs is not None and cross_attention_kwargs.get('gligen', None) is not None:
            cross_attention_kwargs = cross_attention_kwargs.copy()
            gligen_args = cross_attention_kwargs.pop('gligen')
            cross_attention_kwargs['gligen'] = {'objs': self.position_net(**gligen_args)}
        if cross_attention_kwargs is not None:
            cross_attention_kwargs = cross_attention_kwargs.copy()
            lora_scale = cross_attention_kwargs.pop('scale', 1.0)
        else: lora_scale = 1.0
        if USE_PEFT_BACKEND: scale_lora_layers(self, lora_scale)
        is_controlnet = mid_block_additional_residual is not None and down_block_additional_residuals is not None
        is_adapter = down_intrablock_additional_residuals is not None
        if not is_adapter and mid_block_additional_residual is None and (down_block_additional_residuals is not None):
            deprecate('T2I should not use down_block_additional_residuals', '1.3.0', 'Passing intrablock residual connections with `down_block_additional_residuals` is deprecated and will be removed in diffusers 1.3.0. `down_block_additional_residuals` should only be used for ControlNet. Please make sure use `down_intrablock_additional_residuals` instead. ', standard_warn=False)
            down_intrablock_additional_residuals = down_block_additional_residuals
            is_adapter = True
        down_block_res_samples = (sample,)
        for downsample_block in self.down_blocks:
            if hasattr(downsample_block, 'has_cross_attention') and downsample_block.has_cross_attention:
                additional_residuals = {}
                if is_adapter and len(down_intrablock_additional_residuals) > 0: additional_residuals['additional_residuals'] = down_intrablock_additional_residuals.pop(0)
                sample, res_samples = downsample_block(hidden_states=sample, temb=emb, encoder_hidden_states=encoder_hidden_states, attention_mask=attention_mask, cross_attention_kwargs=cross_attention_kwargs,
                encoder_attention_mask=encoder_attention_mask, **additional_residuals)
            else:
                sample, res_samples = downsample_block(hidden_states=sample, temb=emb)
                if is_adapter and len(down_intrablock_additional_residuals) > 0: sample += down_intrablock_additional_residuals.pop(0)
            down_block_res_samples += res_samples
        if is_controlnet:
            new_down_block_res_samples = ()
            for down_block_res_sample, down_block_additional_residual in zip(down_block_res_samples, down_block_additional_residuals):
                down_block_res_sample = down_block_res_sample + down_block_additional_residual
                new_down_block_res_samples = new_down_block_res_samples + (down_block_res_sample,)
            down_block_res_samples = new_down_block_res_samples
        if self.mid_block is not None:
            if hasattr(self.mid_block, 'has_cross_attention') and self.mid_block.has_cross_attention: sample = self.mid_block(sample, emb, encoder_hidden_states=encoder_hidden_states, attention_mask=attention_mask,
            cross_attention_kwargs=cross_attention_kwargs, encoder_attention_mask=encoder_attention_mask)
            else: sample = self.mid_block(sample, emb)
            if is_adapter and len(down_intrablock_additional_residuals) > 0 and (sample.shape == down_intrablock_additional_residuals[0].shape): sample += down_intrablock_additional_residuals.pop(0)
        if is_controlnet: sample = sample + mid_block_additional_residual
        for i, upsample_block in enumerate(self.up_blocks):
            is_final_block = i == len(self.up_blocks) - 1
            res_samples = down_block_res_samples[-len(upsample_block.resnets):]
            down_block_res_samples = down_block_res_samples[:-len(upsample_block.resnets)]
            if not is_final_block and forward_upsample_size: upsample_size = down_block_res_samples[-1].shape[2:]
            if hasattr(upsample_block, 'has_cross_attention') and upsample_block.has_cross_attention: sample = upsample_block(hidden_states=sample, temb=emb, res_hidden_states_tuple=res_samples,
            encoder_hidden_states=encoder_hidden_states, cross_attention_kwargs=cross_attention_kwargs, upsample_size=upsample_size, attention_mask=attention_mask, encoder_attention_mask=encoder_attention_mask)
            else: sample = upsample_block(hidden_states=sample, temb=emb, res_hidden_states_tuple=res_samples, upsample_size=upsample_size)
        if self.conv_norm_out:
            sample = self.conv_norm_out(sample)
            sample = self.conv_act(sample)
        sample = self.conv_out(sample)
        if USE_PEFT_BACKEND: unscale_lora_layers(self, lora_scale)
        if not return_dict: return (sample,)
        return UNet2DConditionOutput(sample=sample)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
