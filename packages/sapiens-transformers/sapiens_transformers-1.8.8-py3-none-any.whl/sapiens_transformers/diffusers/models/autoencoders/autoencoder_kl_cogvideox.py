'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...configuration_utils import ConfigMixin, register_to_config
from ...loaders.single_file_model import FromOriginalModelMixin
from .vae import DecoderOutput, DiagonalGaussianDistribution
from ...utils.sapiens_accelerator_utils import apply_forward_hook
from ..modeling_outputs import AutoencoderKLOutput
from ..downsampling import CogVideoXDownsample3D
from typing import Dict, Optional, Tuple, Union
from ..upsampling import CogVideoXUpsample3D
from ..activations import get_activation
from ..modeling_utils import ModelMixin
import torch.nn.functional as F
import torch.nn as nn
import numpy as np
import torch
class CogVideoXSafeConv3d(nn.Conv3d):
    def forward(self, input: torch.Tensor) -> torch.Tensor:
        memory_count = input.shape[0] * input.shape[1] * input.shape[2] * input.shape[3] * input.shape[4] * 2 / 1024 ** 3
        if memory_count > 2:
            kernel_size = self.kernel_size[0]
            part_num = int(memory_count / 2) + 1
            input_chunks = torch.chunk(input, part_num, dim=2)
            if kernel_size > 1: input_chunks = [input_chunks[0]] + [torch.cat((input_chunks[i - 1][:, :, -kernel_size + 1:], input_chunks[i]), dim=2) for i in range(1, len(input_chunks))]
            output_chunks = []
            for input_chunk in input_chunks: output_chunks.append(super().forward(input_chunk))
            output = torch.cat(output_chunks, dim=2)
            return output
        else: return super().forward(input)
class CogVideoXCausalConv3d(nn.Module):
    """Args:"""
    def __init__(self, in_channels: int, out_channels: int, kernel_size: Union[int, Tuple[int, int, int]], stride: int=1, dilation: int=1, pad_mode: str='constant'):
        super().__init__()
        if isinstance(kernel_size, int): kernel_size = (kernel_size,) * 3
        time_kernel_size, height_kernel_size, width_kernel_size = kernel_size
        time_pad = time_kernel_size - 1
        height_pad = (height_kernel_size - 1) // 2
        width_pad = (width_kernel_size - 1) // 2
        self.pad_mode = pad_mode
        self.height_pad = height_pad
        self.width_pad = width_pad
        self.time_pad = time_pad
        self.time_causal_padding = (width_pad, width_pad, height_pad, height_pad, time_pad, 0)
        self.temporal_dim = 2
        self.time_kernel_size = time_kernel_size
        stride = stride if isinstance(stride, tuple) else (stride, 1, 1)
        dilation = (dilation, 1, 1)
        self.conv = CogVideoXSafeConv3d(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size, stride=stride, dilation=dilation)
    def fake_context_parallel_forward(self, inputs: torch.Tensor, conv_cache: Optional[torch.Tensor]=None) -> torch.Tensor:
        if self.pad_mode == 'replicate': inputs = F.pad(inputs, self.time_causal_padding, mode='replicate')
        else:
            kernel_size = self.time_kernel_size
            if kernel_size > 1:
                cached_inputs = [conv_cache] if conv_cache is not None else [inputs[:, :, :1]] * (kernel_size - 1)
                inputs = torch.cat(cached_inputs + [inputs], dim=2)
        return inputs
    def forward(self, inputs: torch.Tensor, conv_cache: Optional[torch.Tensor]=None) -> torch.Tensor:
        inputs = self.fake_context_parallel_forward(inputs, conv_cache)
        if self.pad_mode == 'replicate': conv_cache = None
        else:
            padding_2d = (self.width_pad, self.width_pad, self.height_pad, self.height_pad)
            conv_cache = inputs[:, :, -self.time_kernel_size + 1:].clone()
            inputs = F.pad(inputs, padding_2d, mode='constant', value=0)
        output = self.conv(inputs)
        return (output, conv_cache)
class CogVideoXSpatialNorm3D(nn.Module):
    """Args:"""
    def __init__(self, f_channels: int, zq_channels: int, groups: int=32):
        super().__init__()
        self.norm_layer = nn.GroupNorm(num_channels=f_channels, num_groups=groups, eps=1e-06, affine=True)
        self.conv_y = CogVideoXCausalConv3d(zq_channels, f_channels, kernel_size=1, stride=1)
        self.conv_b = CogVideoXCausalConv3d(zq_channels, f_channels, kernel_size=1, stride=1)
    def forward(self, f: torch.Tensor, zq: torch.Tensor, conv_cache: Optional[Dict[str, torch.Tensor]]=None) -> torch.Tensor:
        new_conv_cache = {}
        conv_cache = conv_cache or {}
        if f.shape[2] > 1 and f.shape[2] % 2 == 1:
            f_first, f_rest = (f[:, :, :1], f[:, :, 1:])
            f_first_size, f_rest_size = (f_first.shape[-3:], f_rest.shape[-3:])
            z_first, z_rest = (zq[:, :, :1], zq[:, :, 1:])
            z_first = F.interpolate(z_first, size=f_first_size)
            z_rest = F.interpolate(z_rest, size=f_rest_size)
            zq = torch.cat([z_first, z_rest], dim=2)
        else: zq = F.interpolate(zq, size=f.shape[-3:])
        conv_y, new_conv_cache['conv_y'] = self.conv_y(zq, conv_cache=conv_cache.get('conv_y'))
        conv_b, new_conv_cache['conv_b'] = self.conv_b(zq, conv_cache=conv_cache.get('conv_b'))
        norm_f = self.norm_layer(f)
        new_f = norm_f * conv_y + conv_b
        return (new_f, new_conv_cache)
class CogVideoXResnetBlock3D(nn.Module):
    """Args:"""
    def __init__(self, in_channels: int, out_channels: Optional[int]=None, dropout: float=0.0, temb_channels: int=512, groups: int=32, eps: float=1e-06, non_linearity: str='swish',
    conv_shortcut: bool=False, spatial_norm_dim: Optional[int]=None, pad_mode: str='first'):
        super().__init__()
        out_channels = out_channels or in_channels
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.nonlinearity = get_activation(non_linearity)
        self.use_conv_shortcut = conv_shortcut
        self.spatial_norm_dim = spatial_norm_dim
        if spatial_norm_dim is None:
            self.norm1 = nn.GroupNorm(num_channels=in_channels, num_groups=groups, eps=eps)
            self.norm2 = nn.GroupNorm(num_channels=out_channels, num_groups=groups, eps=eps)
        else:
            self.norm1 = CogVideoXSpatialNorm3D(f_channels=in_channels, zq_channels=spatial_norm_dim, groups=groups)
            self.norm2 = CogVideoXSpatialNorm3D(f_channels=out_channels, zq_channels=spatial_norm_dim, groups=groups)
        self.conv1 = CogVideoXCausalConv3d(in_channels=in_channels, out_channels=out_channels, kernel_size=3, pad_mode=pad_mode)
        if temb_channels > 0: self.temb_proj = nn.Linear(in_features=temb_channels, out_features=out_channels)
        self.dropout = nn.Dropout(dropout)
        self.conv2 = CogVideoXCausalConv3d(in_channels=out_channels, out_channels=out_channels, kernel_size=3, pad_mode=pad_mode)
        if self.in_channels != self.out_channels:
            if self.use_conv_shortcut: self.conv_shortcut = CogVideoXCausalConv3d(in_channels=in_channels, out_channels=out_channels, kernel_size=3, pad_mode=pad_mode)
            else: self.conv_shortcut = CogVideoXSafeConv3d(in_channels=in_channels, out_channels=out_channels, kernel_size=1, stride=1, padding=0)
    def forward(self, inputs: torch.Tensor, temb: Optional[torch.Tensor]=None, zq: Optional[torch.Tensor]=None, conv_cache: Optional[Dict[str, torch.Tensor]]=None) -> torch.Tensor:
        new_conv_cache = {}
        conv_cache = conv_cache or {}
        hidden_states = inputs
        if zq is not None: hidden_states, new_conv_cache['norm1'] = self.norm1(hidden_states, zq, conv_cache=conv_cache.get('norm1'))
        else: hidden_states = self.norm1(hidden_states)
        hidden_states = self.nonlinearity(hidden_states)
        hidden_states, new_conv_cache['conv1'] = self.conv1(hidden_states, conv_cache=conv_cache.get('conv1'))
        if temb is not None: hidden_states = hidden_states + self.temb_proj(self.nonlinearity(temb))[:, :, None, None, None]
        if zq is not None: hidden_states, new_conv_cache['norm2'] = self.norm2(hidden_states, zq, conv_cache=conv_cache.get('norm2'))
        else: hidden_states = self.norm2(hidden_states)
        hidden_states = self.nonlinearity(hidden_states)
        hidden_states = self.dropout(hidden_states)
        hidden_states, new_conv_cache['conv2'] = self.conv2(hidden_states, conv_cache=conv_cache.get('conv2'))
        if self.in_channels != self.out_channels:
            if self.use_conv_shortcut: inputs, new_conv_cache['conv_shortcut'] = self.conv_shortcut(inputs, conv_cache=conv_cache.get('conv_shortcut'))
            else: inputs = self.conv_shortcut(inputs)
        hidden_states = hidden_states + inputs
        return (hidden_states, new_conv_cache)
class CogVideoXDownBlock3D(nn.Module):
    """Args:"""
    _supports_gradient_checkpointing = True
    def __init__(self, in_channels: int, out_channels: int, temb_channels: int, dropout: float=0.0, num_layers: int=1, resnet_eps: float=1e-06, resnet_act_fn: str='swish', resnet_groups: int=32,
    add_downsample: bool=True, downsample_padding: int=0, compress_time: bool=False, pad_mode: str='first'):
        super().__init__()
        resnets = []
        for i in range(num_layers):
            in_channel = in_channels if i == 0 else out_channels
            resnets.append(CogVideoXResnetBlock3D(in_channels=in_channel, out_channels=out_channels, dropout=dropout, temb_channels=temb_channels, groups=resnet_groups, eps=resnet_eps, non_linearity=resnet_act_fn, pad_mode=pad_mode))
        self.resnets = nn.ModuleList(resnets)
        self.downsamplers = None
        if add_downsample: self.downsamplers = nn.ModuleList([CogVideoXDownsample3D(out_channels, out_channels, padding=downsample_padding, compress_time=compress_time)])
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor, temb: Optional[torch.Tensor]=None, zq: Optional[torch.Tensor]=None, conv_cache: Optional[Dict[str, torch.Tensor]]=None) -> torch.Tensor:
        new_conv_cache = {}
        conv_cache = conv_cache or {}
        for i, resnet in enumerate(self.resnets):
            conv_cache_key = f'resnet_{i}'
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module):
                    def create_forward(*inputs): return module(*inputs)
                    return create_forward
                hidden_states, new_conv_cache[conv_cache_key] = torch.utils.checkpoint.checkpoint(create_custom_forward(resnet), hidden_states, temb, zq, conv_cache.get(conv_cache_key))
            else: hidden_states, new_conv_cache[conv_cache_key] = resnet(hidden_states, temb, zq, conv_cache=conv_cache.get(conv_cache_key))
        if self.downsamplers is not None:
            for downsampler in self.downsamplers: hidden_states = downsampler(hidden_states)
        return (hidden_states, new_conv_cache)
class CogVideoXMidBlock3D(nn.Module):
    """Args:"""
    _supports_gradient_checkpointing = True
    def __init__(self, in_channels: int, temb_channels: int, dropout: float=0.0, num_layers: int=1, resnet_eps: float=1e-06, resnet_act_fn: str='swish', resnet_groups: int=32, spatial_norm_dim: Optional[int]=None, pad_mode: str='first'):
        super().__init__()
        resnets = []
        for _ in range(num_layers): resnets.append(CogVideoXResnetBlock3D(in_channels=in_channels, out_channels=in_channels, dropout=dropout, temb_channels=temb_channels, groups=resnet_groups,
        eps=resnet_eps, spatial_norm_dim=spatial_norm_dim, non_linearity=resnet_act_fn, pad_mode=pad_mode))
        self.resnets = nn.ModuleList(resnets)
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor, temb: Optional[torch.Tensor]=None, zq: Optional[torch.Tensor]=None, conv_cache: Optional[Dict[str, torch.Tensor]]=None) -> torch.Tensor:
        new_conv_cache = {}
        conv_cache = conv_cache or {}
        for i, resnet in enumerate(self.resnets):
            conv_cache_key = f'resnet_{i}'
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module):
                    def create_forward(*inputs): return module(*inputs)
                    return create_forward
                hidden_states, new_conv_cache[conv_cache_key] = torch.utils.checkpoint.checkpoint(create_custom_forward(resnet), hidden_states, temb, zq, conv_cache.get(conv_cache_key))
            else: hidden_states, new_conv_cache[conv_cache_key] = resnet(hidden_states, temb, zq, conv_cache=conv_cache.get(conv_cache_key))
        return (hidden_states, new_conv_cache)
class CogVideoXUpBlock3D(nn.Module):
    """Args:"""
    def __init__(self, in_channels: int, out_channels: int, temb_channels: int, dropout: float=0.0, num_layers: int=1, resnet_eps: float=1e-06, resnet_act_fn: str='swish', resnet_groups: int=32, spatial_norm_dim: int=16, add_upsample: bool=True,
    upsample_padding: int=1, compress_time: bool=False, pad_mode: str='first'):
        super().__init__()
        resnets = []
        for i in range(num_layers):
            in_channel = in_channels if i == 0 else out_channels
            resnets.append(CogVideoXResnetBlock3D(in_channels=in_channel, out_channels=out_channels, dropout=dropout, temb_channels=temb_channels, groups=resnet_groups, eps=resnet_eps, non_linearity=resnet_act_fn, spatial_norm_dim=spatial_norm_dim, pad_mode=pad_mode))
        self.resnets = nn.ModuleList(resnets)
        self.upsamplers = None
        if add_upsample: self.upsamplers = nn.ModuleList([CogVideoXUpsample3D(out_channels, out_channels, padding=upsample_padding, compress_time=compress_time)])
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor, temb: Optional[torch.Tensor]=None, zq: Optional[torch.Tensor]=None, conv_cache: Optional[Dict[str, torch.Tensor]]=None) -> torch.Tensor:
        new_conv_cache = {}
        conv_cache = conv_cache or {}
        for i, resnet in enumerate(self.resnets):
            conv_cache_key = f'resnet_{i}'
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module):
                    def create_forward(*inputs): return module(*inputs)
                    return create_forward
                hidden_states, new_conv_cache[conv_cache_key] = torch.utils.checkpoint.checkpoint(create_custom_forward(resnet), hidden_states, temb, zq, conv_cache.get(conv_cache_key))
            else: hidden_states, new_conv_cache[conv_cache_key] = resnet(hidden_states, temb, zq, conv_cache=conv_cache.get(conv_cache_key))
        if self.upsamplers is not None:
            for upsampler in self.upsamplers: hidden_states = upsampler(hidden_states)
        return (hidden_states, new_conv_cache)
class CogVideoXEncoder3D(nn.Module):
    """Args:"""
    _supports_gradient_checkpointing = True
    def __init__(self, in_channels: int=3, out_channels: int=16, down_block_types: Tuple[str, ...]=('CogVideoXDownBlock3D', 'CogVideoXDownBlock3D', 'CogVideoXDownBlock3D', 'CogVideoXDownBlock3D'), block_out_channels: Tuple[int, ...]=(128, 256, 256, 512),
    layers_per_block: int=3, act_fn: str='silu', norm_eps: float=1e-06, norm_num_groups: int=32, dropout: float=0.0, pad_mode: str='first', temporal_compression_ratio: float=4):
        super().__init__()
        temporal_compress_level = int(np.log2(temporal_compression_ratio))
        self.conv_in = CogVideoXCausalConv3d(in_channels, block_out_channels[0], kernel_size=3, pad_mode=pad_mode)
        self.down_blocks = nn.ModuleList([])
        output_channel = block_out_channels[0]
        for i, down_block_type in enumerate(down_block_types):
            input_channel = output_channel
            output_channel = block_out_channels[i]
            is_final_block = i == len(block_out_channels) - 1
            compress_time = i < temporal_compress_level
            if down_block_type == 'CogVideoXDownBlock3D': down_block = CogVideoXDownBlock3D(in_channels=input_channel, out_channels=output_channel, temb_channels=0, dropout=dropout, num_layers=layers_per_block, resnet_eps=norm_eps,
            resnet_act_fn=act_fn, resnet_groups=norm_num_groups, add_downsample=not is_final_block, compress_time=compress_time)
            else: raise ValueError('Invalid `down_block_type` encountered. Must be `CogVideoXDownBlock3D`')
            self.down_blocks.append(down_block)
        self.mid_block = CogVideoXMidBlock3D(in_channels=block_out_channels[-1], temb_channels=0, dropout=dropout, num_layers=2, resnet_eps=norm_eps, resnet_act_fn=act_fn, resnet_groups=norm_num_groups, pad_mode=pad_mode)
        self.norm_out = nn.GroupNorm(norm_num_groups, block_out_channels[-1], eps=1e-06)
        self.conv_act = nn.SiLU()
        self.conv_out = CogVideoXCausalConv3d(block_out_channels[-1], 2 * out_channels, kernel_size=3, pad_mode=pad_mode)
        self.gradient_checkpointing = False
    def forward(self, sample: torch.Tensor, temb: Optional[torch.Tensor]=None, conv_cache: Optional[Dict[str, torch.Tensor]]=None) -> torch.Tensor:
        new_conv_cache = {}
        conv_cache = conv_cache or {}
        hidden_states, new_conv_cache['conv_in'] = self.conv_in(sample, conv_cache=conv_cache.get('conv_in'))
        if torch.is_grad_enabled() and self.gradient_checkpointing:
            def create_custom_forward(module):
                def custom_forward(*inputs): return module(*inputs)
                return custom_forward
            for i, down_block in enumerate(self.down_blocks):
                conv_cache_key = f'down_block_{i}'
                hidden_states, new_conv_cache[conv_cache_key] = torch.utils.checkpoint.checkpoint(create_custom_forward(down_block), hidden_states, temb, None, conv_cache.get(conv_cache_key))
            hidden_states, new_conv_cache['mid_block'] = torch.utils.checkpoint.checkpoint(create_custom_forward(self.mid_block), hidden_states, temb, None, conv_cache.get('mid_block'))
        else:
            for i, down_block in enumerate(self.down_blocks):
                conv_cache_key = f'down_block_{i}'
                hidden_states, new_conv_cache[conv_cache_key] = down_block(hidden_states, temb, None, conv_cache.get(conv_cache_key))
            hidden_states, new_conv_cache['mid_block'] = self.mid_block(hidden_states, temb, None, conv_cache=conv_cache.get('mid_block'))
        hidden_states = self.norm_out(hidden_states)
        hidden_states = self.conv_act(hidden_states)
        hidden_states, new_conv_cache['conv_out'] = self.conv_out(hidden_states, conv_cache=conv_cache.get('conv_out'))
        return (hidden_states, new_conv_cache)
class CogVideoXDecoder3D(nn.Module):
    """Args:"""
    _supports_gradient_checkpointing = True
    def __init__(self, in_channels: int=16, out_channels: int=3, up_block_types: Tuple[str, ...]=('CogVideoXUpBlock3D', 'CogVideoXUpBlock3D', 'CogVideoXUpBlock3D', 'CogVideoXUpBlock3D'), block_out_channels: Tuple[int, ...]=(128, 256, 256, 512),
    layers_per_block: int=3, act_fn: str='silu', norm_eps: float=1e-06, norm_num_groups: int=32, dropout: float=0.0, pad_mode: str='first', temporal_compression_ratio: float=4):
        super().__init__()
        reversed_block_out_channels = list(reversed(block_out_channels))
        self.conv_in = CogVideoXCausalConv3d(in_channels, reversed_block_out_channels[0], kernel_size=3, pad_mode=pad_mode)
        self.mid_block = CogVideoXMidBlock3D(in_channels=reversed_block_out_channels[0], temb_channels=0, num_layers=2, resnet_eps=norm_eps, resnet_act_fn=act_fn, resnet_groups=norm_num_groups, spatial_norm_dim=in_channels, pad_mode=pad_mode)
        self.up_blocks = nn.ModuleList([])
        output_channel = reversed_block_out_channels[0]
        temporal_compress_level = int(np.log2(temporal_compression_ratio))
        for i, up_block_type in enumerate(up_block_types):
            prev_output_channel = output_channel
            output_channel = reversed_block_out_channels[i]
            is_final_block = i == len(block_out_channels) - 1
            compress_time = i < temporal_compress_level
            if up_block_type == 'CogVideoXUpBlock3D':
                up_block = CogVideoXUpBlock3D(in_channels=prev_output_channel, out_channels=output_channel, temb_channels=0, dropout=dropout, num_layers=layers_per_block + 1, resnet_eps=norm_eps, resnet_act_fn=act_fn, resnet_groups=norm_num_groups,
                spatial_norm_dim=in_channels, add_upsample=not is_final_block, compress_time=compress_time, pad_mode=pad_mode)
                prev_output_channel = output_channel
            else: raise ValueError('Invalid `up_block_type` encountered. Must be `CogVideoXUpBlock3D`')
            self.up_blocks.append(up_block)
        self.norm_out = CogVideoXSpatialNorm3D(reversed_block_out_channels[-1], in_channels, groups=norm_num_groups)
        self.conv_act = nn.SiLU()
        self.conv_out = CogVideoXCausalConv3d(reversed_block_out_channels[-1], out_channels, kernel_size=3, pad_mode=pad_mode)
        self.gradient_checkpointing = False
    def forward(self, sample: torch.Tensor, temb: Optional[torch.Tensor]=None, conv_cache: Optional[Dict[str, torch.Tensor]]=None) -> torch.Tensor:
        new_conv_cache = {}
        conv_cache = conv_cache or {}
        hidden_states, new_conv_cache['conv_in'] = self.conv_in(sample, conv_cache=conv_cache.get('conv_in'))
        if torch.is_grad_enabled() and self.gradient_checkpointing:
            def create_custom_forward(module):
                def custom_forward(*inputs): return module(*inputs)
                return custom_forward
            hidden_states, new_conv_cache['mid_block'] = torch.utils.checkpoint.checkpoint(create_custom_forward(self.mid_block), hidden_states, temb, sample, conv_cache.get('mid_block'))
            for i, up_block in enumerate(self.up_blocks):
                conv_cache_key = f'up_block_{i}'
                hidden_states, new_conv_cache[conv_cache_key] = torch.utils.checkpoint.checkpoint(create_custom_forward(up_block), hidden_states, temb, sample, conv_cache.get(conv_cache_key))
        else:
            hidden_states, new_conv_cache['mid_block'] = self.mid_block(hidden_states, temb, sample, conv_cache=conv_cache.get('mid_block'))
            for i, up_block in enumerate(self.up_blocks):
                conv_cache_key = f'up_block_{i}'
                hidden_states, new_conv_cache[conv_cache_key] = up_block(hidden_states, temb, sample, conv_cache=conv_cache.get(conv_cache_key))
        hidden_states, new_conv_cache['norm_out'] = self.norm_out(hidden_states, sample, conv_cache=conv_cache.get('norm_out'))
        hidden_states = self.conv_act(hidden_states)
        hidden_states, new_conv_cache['conv_out'] = self.conv_out(hidden_states, conv_cache=conv_cache.get('conv_out'))
        return (hidden_states, new_conv_cache)
class AutoencoderKLCogVideoX(ModelMixin, ConfigMixin, FromOriginalModelMixin):
    _supports_gradient_checkpointing = True
    _no_split_modules = ['CogVideoXResnetBlock3D']
    @register_to_config
    def __init__(self, in_channels: int=3, out_channels: int=3, down_block_types: Tuple[str]=('CogVideoXDownBlock3D', 'CogVideoXDownBlock3D', 'CogVideoXDownBlock3D', 'CogVideoXDownBlock3D'),
    up_block_types: Tuple[str]=('CogVideoXUpBlock3D', 'CogVideoXUpBlock3D', 'CogVideoXUpBlock3D', 'CogVideoXUpBlock3D'), block_out_channels: Tuple[int]=(128, 256, 256, 512), latent_channels: int=16,
    layers_per_block: int=3, act_fn: str='silu', norm_eps: float=1e-06, norm_num_groups: int=32, temporal_compression_ratio: float=4, sample_height: int=480, sample_width: int=720, scaling_factor: float=1.15258426,
    shift_factor: Optional[float]=None, latents_mean: Optional[Tuple[float]]=None, latents_std: Optional[Tuple[float]]=None, force_upcast: float=True, use_quant_conv: bool=False, use_post_quant_conv: bool=False, invert_scale_latents: bool=False):
        super().__init__()
        self.encoder = CogVideoXEncoder3D(in_channels=in_channels, out_channels=latent_channels, down_block_types=down_block_types, block_out_channels=block_out_channels, layers_per_block=layers_per_block, act_fn=act_fn,
        norm_eps=norm_eps, norm_num_groups=norm_num_groups, temporal_compression_ratio=temporal_compression_ratio)
        self.decoder = CogVideoXDecoder3D(in_channels=latent_channels, out_channels=out_channels, up_block_types=up_block_types, block_out_channels=block_out_channels, layers_per_block=layers_per_block, act_fn=act_fn,
        norm_eps=norm_eps, norm_num_groups=norm_num_groups, temporal_compression_ratio=temporal_compression_ratio)
        self.quant_conv = CogVideoXSafeConv3d(2 * out_channels, 2 * out_channels, 1) if use_quant_conv else None
        self.post_quant_conv = CogVideoXSafeConv3d(out_channels, out_channels, 1) if use_post_quant_conv else None
        self.use_slicing = False
        self.use_tiling = False
        self.num_latent_frames_batch_size = 2
        self.num_sample_frames_batch_size = 8
        self.tile_sample_min_height = sample_height // 2
        self.tile_sample_min_width = sample_width // 2
        self.tile_latent_min_height = int(self.tile_sample_min_height / 2 ** (len(self.config.block_out_channels) - 1))
        self.tile_latent_min_width = int(self.tile_sample_min_width / 2 ** (len(self.config.block_out_channels) - 1))
        self.tile_overlap_factor_height = 1 / 6
        self.tile_overlap_factor_width = 1 / 5
    def _set_gradient_checkpointing(self, module, value=False):
        if isinstance(module, (CogVideoXEncoder3D, CogVideoXDecoder3D)): module.gradient_checkpointing = value
    def enable_tiling(self, tile_sample_min_height: Optional[int]=None, tile_sample_min_width: Optional[int]=None, tile_overlap_factor_height: Optional[float]=None, tile_overlap_factor_width: Optional[float]=None) -> None:
        """Args:"""
        self.use_tiling = True
        self.tile_sample_min_height = tile_sample_min_height or self.tile_sample_min_height
        self.tile_sample_min_width = tile_sample_min_width or self.tile_sample_min_width
        self.tile_latent_min_height = int(self.tile_sample_min_height / 2 ** (len(self.config.block_out_channels) - 1))
        self.tile_latent_min_width = int(self.tile_sample_min_width / 2 ** (len(self.config.block_out_channels) - 1))
        self.tile_overlap_factor_height = tile_overlap_factor_height or self.tile_overlap_factor_height
        self.tile_overlap_factor_width = tile_overlap_factor_width or self.tile_overlap_factor_width
    def disable_tiling(self) -> None: self.use_tiling = False
    def enable_slicing(self) -> None: self.use_slicing = True
    def disable_slicing(self) -> None: self.use_slicing = False
    def _encode(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, num_channels, num_frames, height, width = x.shape
        if self.use_tiling and (width > self.tile_sample_min_width or height > self.tile_sample_min_height): return self.tiled_encode(x)
        frame_batch_size = self.num_sample_frames_batch_size
        num_batches = max(num_frames // frame_batch_size, 1)
        conv_cache = None
        enc = []
        for i in range(num_batches):
            remaining_frames = num_frames % frame_batch_size
            start_frame = frame_batch_size * i + (0 if i == 0 else remaining_frames)
            end_frame = frame_batch_size * (i + 1) + remaining_frames
            x_intermediate = x[:, :, start_frame:end_frame]
            x_intermediate, conv_cache = self.encoder(x_intermediate, conv_cache=conv_cache)
            if self.quant_conv is not None: x_intermediate = self.quant_conv(x_intermediate)
            enc.append(x_intermediate)
        enc = torch.cat(enc, dim=2)
        return enc
    @apply_forward_hook
    def encode(self, x: torch.Tensor, return_dict: bool=True) -> Union[AutoencoderKLOutput, Tuple[DiagonalGaussianDistribution]]:
        """Returns:"""
        if self.use_slicing and x.shape[0] > 1:
            encoded_slices = [self._encode(x_slice) for x_slice in x.split(1)]
            h = torch.cat(encoded_slices)
        else: h = self._encode(x)
        posterior = DiagonalGaussianDistribution(h)
        if not return_dict: return (posterior,)
        return AutoencoderKLOutput(latent_dist=posterior)
    def _decode(self, z: torch.Tensor, return_dict: bool=True) -> Union[DecoderOutput, torch.Tensor]:
        batch_size, num_channels, num_frames, height, width = z.shape
        if self.use_tiling and (width > self.tile_latent_min_width or height > self.tile_latent_min_height): return self.tiled_decode(z, return_dict=return_dict)
        frame_batch_size = self.num_latent_frames_batch_size
        num_batches = max(num_frames // frame_batch_size, 1)
        conv_cache = None
        dec = []
        for i in range(num_batches):
            remaining_frames = num_frames % frame_batch_size
            start_frame = frame_batch_size * i + (0 if i == 0 else remaining_frames)
            end_frame = frame_batch_size * (i + 1) + remaining_frames
            z_intermediate = z[:, :, start_frame:end_frame]
            if self.post_quant_conv is not None: z_intermediate = self.post_quant_conv(z_intermediate)
            z_intermediate, conv_cache = self.decoder(z_intermediate, conv_cache=conv_cache)
            dec.append(z_intermediate)
        dec = torch.cat(dec, dim=2)
        if not return_dict: return (dec,)
        return DecoderOutput(sample=dec)
    @apply_forward_hook
    def decode(self, z: torch.Tensor, return_dict: bool=True) -> Union[DecoderOutput, torch.Tensor]:
        """Returns:"""
        if self.use_slicing and z.shape[0] > 1:
            decoded_slices = [self._decode(z_slice).sample for z_slice in z.split(1)]
            decoded = torch.cat(decoded_slices)
        else: decoded = self._decode(z).sample
        if not return_dict: return (decoded,)
        return DecoderOutput(sample=decoded)
    def blend_v(self, a: torch.Tensor, b: torch.Tensor, blend_extent: int) -> torch.Tensor:
        blend_extent = min(a.shape[3], b.shape[3], blend_extent)
        for y in range(blend_extent): b[:, :, :, y, :] = a[:, :, :, -blend_extent + y, :] * (1 - y / blend_extent) + b[:, :, :, y, :] * (y / blend_extent)
        return b
    def blend_h(self, a: torch.Tensor, b: torch.Tensor, blend_extent: int) -> torch.Tensor:
        blend_extent = min(a.shape[4], b.shape[4], blend_extent)
        for x in range(blend_extent): b[:, :, :, :, x] = a[:, :, :, :, -blend_extent + x] * (1 - x / blend_extent) + b[:, :, :, :, x] * (x / blend_extent)
        return b
    def tiled_encode(self, x: torch.Tensor) -> torch.Tensor:
        """Returns:"""
        batch_size, num_channels, num_frames, height, width = x.shape
        overlap_height = int(self.tile_sample_min_height * (1 - self.tile_overlap_factor_height))
        overlap_width = int(self.tile_sample_min_width * (1 - self.tile_overlap_factor_width))
        blend_extent_height = int(self.tile_latent_min_height * self.tile_overlap_factor_height)
        blend_extent_width = int(self.tile_latent_min_width * self.tile_overlap_factor_width)
        row_limit_height = self.tile_latent_min_height - blend_extent_height
        row_limit_width = self.tile_latent_min_width - blend_extent_width
        frame_batch_size = self.num_sample_frames_batch_size
        rows = []
        for i in range(0, height, overlap_height):
            row = []
            for j in range(0, width, overlap_width):
                num_batches = max(num_frames // frame_batch_size, 1)
                conv_cache = None
                time = []
                for k in range(num_batches):
                    remaining_frames = num_frames % frame_batch_size
                    start_frame = frame_batch_size * k + (0 if k == 0 else remaining_frames)
                    end_frame = frame_batch_size * (k + 1) + remaining_frames
                    tile = x[:, :, start_frame:end_frame, i:i + self.tile_sample_min_height, j:j + self.tile_sample_min_width]
                    tile, conv_cache = self.encoder(tile, conv_cache=conv_cache)
                    if self.quant_conv is not None: tile = self.quant_conv(tile)
                    time.append(tile)
                row.append(torch.cat(time, dim=2))
            rows.append(row)
        result_rows = []
        for i, row in enumerate(rows):
            result_row = []
            for j, tile in enumerate(row):
                if i > 0: tile = self.blend_v(rows[i - 1][j], tile, blend_extent_height)
                if j > 0: tile = self.blend_h(row[j - 1], tile, blend_extent_width)
                result_row.append(tile[:, :, :, :row_limit_height, :row_limit_width])
            result_rows.append(torch.cat(result_row, dim=4))
        enc = torch.cat(result_rows, dim=3)
        return enc
    def tiled_decode(self, z: torch.Tensor, return_dict: bool=True) -> Union[DecoderOutput, torch.Tensor]:
        """Returns:"""
        batch_size, num_channels, num_frames, height, width = z.shape
        overlap_height = int(self.tile_latent_min_height * (1 - self.tile_overlap_factor_height))
        overlap_width = int(self.tile_latent_min_width * (1 - self.tile_overlap_factor_width))
        blend_extent_height = int(self.tile_sample_min_height * self.tile_overlap_factor_height)
        blend_extent_width = int(self.tile_sample_min_width * self.tile_overlap_factor_width)
        row_limit_height = self.tile_sample_min_height - blend_extent_height
        row_limit_width = self.tile_sample_min_width - blend_extent_width
        frame_batch_size = self.num_latent_frames_batch_size
        rows = []
        for i in range(0, height, overlap_height):
            row = []
            for j in range(0, width, overlap_width):
                num_batches = max(num_frames // frame_batch_size, 1)
                conv_cache = None
                time = []
                for k in range(num_batches):
                    remaining_frames = num_frames % frame_batch_size
                    start_frame = frame_batch_size * k + (0 if k == 0 else remaining_frames)
                    end_frame = frame_batch_size * (k + 1) + remaining_frames
                    tile = z[:, :, start_frame:end_frame, i:i + self.tile_latent_min_height, j:j + self.tile_latent_min_width]
                    if self.post_quant_conv is not None: tile = self.post_quant_conv(tile)
                    tile, conv_cache = self.decoder(tile, conv_cache=conv_cache)
                    time.append(tile)
                row.append(torch.cat(time, dim=2))
            rows.append(row)
        result_rows = []
        for i, row in enumerate(rows):
            result_row = []
            for j, tile in enumerate(row):
                if i > 0: tile = self.blend_v(rows[i - 1][j], tile, blend_extent_height)
                if j > 0: tile = self.blend_h(row[j - 1], tile, blend_extent_width)
                result_row.append(tile[:, :, :, :row_limit_height, :row_limit_width])
            result_rows.append(torch.cat(result_row, dim=4))
        dec = torch.cat(result_rows, dim=3)
        if not return_dict: return (dec,)
        return DecoderOutput(sample=dec)
    def forward(self, sample: torch.Tensor, sample_posterior: bool=False, return_dict: bool=True, generator: Optional[torch.Generator]=None) -> Union[torch.Tensor, torch.Tensor]:
        x = sample
        posterior = self.encode(x).latent_dist
        if sample_posterior: z = posterior.sample(generator=generator)
        else: z = posterior.mode()
        dec = self.decode(z).sample
        if not return_dict: return (dec,)
        return DecoderOutput(sample=dec)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
