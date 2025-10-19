'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...configuration_utils import ConfigMixin, register_to_config
from .vae import DecoderOutput, DiagonalGaussianDistribution
from ...utils.sapiens_accelerator_utils import apply_forward_hook
from typing import Any, Dict, Optional, Tuple, Union
from ..modeling_outputs import AutoencoderKLOutput
from ...utils import is_torch_version
from ..attention_processor import Attention
from ..activations import get_activation
from ..modeling_utils import ModelMixin
import torch.nn.functional as F
import torch.utils.checkpoint
import torch.nn as nn
import numpy as np
import torch
def prepare_causal_attention_mask(num_frames: int, height_width: int, dtype: torch.dtype, device: torch.device, batch_size: int=None) -> torch.Tensor:
    seq_len = num_frames * height_width
    mask = torch.full((seq_len, seq_len), float('-inf'), dtype=dtype, device=device)
    for i in range(seq_len):
        i_frame = i // height_width
        mask[i, :(i_frame + 1) * height_width] = 0
    if batch_size is not None: mask = mask.unsqueeze(0).expand(batch_size, -1, -1)
    return mask
class HunyuanVideoCausalConv3d(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: Union[int, Tuple[int, int, int]]=3, stride: Union[int, Tuple[int, int, int]]=1, padding: Union[int, Tuple[int, int, int]]=0,
    dilation: Union[int, Tuple[int, int, int]]=1, bias: bool=True, pad_mode: str='replicate') -> None:
        super().__init__()
        kernel_size = (kernel_size, kernel_size, kernel_size) if isinstance(kernel_size, int) else kernel_size
        self.pad_mode = pad_mode
        self.time_causal_padding = (kernel_size[0] // 2, kernel_size[0] // 2, kernel_size[1] // 2, kernel_size[1] // 2, kernel_size[2] - 1, 0)
        self.conv = nn.Conv3d(in_channels, out_channels, kernel_size, stride, padding, dilation, bias=bias)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = F.pad(hidden_states, self.time_causal_padding, mode=self.pad_mode)
        return self.conv(hidden_states)
class HunyuanVideoUpsampleCausal3D(nn.Module):
    def __init__(self, in_channels: int, out_channels: Optional[int]=None, kernel_size: int=3, stride: int=1, bias: bool=True, upsample_factor: Tuple[float, float, float]=(2, 2, 2)) -> None:
        super().__init__()
        out_channels = out_channels or in_channels
        self.upsample_factor = upsample_factor
        self.conv = HunyuanVideoCausalConv3d(in_channels, out_channels, kernel_size, stride, bias=bias)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        num_frames = hidden_states.size(2)
        first_frame, other_frames = hidden_states.split((1, num_frames - 1), dim=2)
        first_frame = F.interpolate(first_frame.squeeze(2), scale_factor=self.upsample_factor[1:], mode='nearest').unsqueeze(2)
        if num_frames > 1:
            other_frames = other_frames.contiguous()
            other_frames = F.interpolate(other_frames, scale_factor=self.upsample_factor, mode='nearest')
            hidden_states = torch.cat((first_frame, other_frames), dim=2)
        else: hidden_states = first_frame
        hidden_states = self.conv(hidden_states)
        return hidden_states
class HunyuanVideoDownsampleCausal3D(nn.Module):
    def __init__(self, channels: int, out_channels: Optional[int]=None, padding: int=1, kernel_size: int=3, bias: bool=True, stride=2) -> None:
        super().__init__()
        out_channels = out_channels or channels
        self.conv = HunyuanVideoCausalConv3d(channels, out_channels, kernel_size, stride, padding, bias=bias)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.conv(hidden_states)
        return hidden_states
class HunyuanVideoResnetBlockCausal3D(nn.Module):
    def __init__(self, in_channels: int, out_channels: Optional[int]=None, dropout: float=0.0, groups: int=32, eps: float=1e-06, non_linearity: str='swish') -> None:
        super().__init__()
        out_channels = out_channels or in_channels
        self.nonlinearity = get_activation(non_linearity)
        self.norm1 = nn.GroupNorm(groups, in_channels, eps=eps, affine=True)
        self.conv1 = HunyuanVideoCausalConv3d(in_channels, out_channels, 3, 1, 0)
        self.norm2 = nn.GroupNorm(groups, out_channels, eps=eps, affine=True)
        self.dropout = nn.Dropout(dropout)
        self.conv2 = HunyuanVideoCausalConv3d(out_channels, out_channels, 3, 1, 0)
        self.conv_shortcut = None
        if in_channels != out_channels: self.conv_shortcut = HunyuanVideoCausalConv3d(in_channels, out_channels, 1, 1, 0)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = hidden_states.contiguous()
        residual = hidden_states
        hidden_states = self.norm1(hidden_states)
        hidden_states = self.nonlinearity(hidden_states)
        hidden_states = self.conv1(hidden_states)
        hidden_states = self.norm2(hidden_states)
        hidden_states = self.nonlinearity(hidden_states)
        hidden_states = self.dropout(hidden_states)
        hidden_states = self.conv2(hidden_states)
        if self.conv_shortcut is not None: residual = self.conv_shortcut(residual)
        hidden_states = hidden_states + residual
        return hidden_states
class HunyuanVideoMidBlock3D(nn.Module):
    def __init__(self, in_channels: int, dropout: float=0.0, num_layers: int=1, resnet_eps: float=1e-06, resnet_act_fn: str='swish', resnet_groups: int=32, add_attention: bool=True, attention_head_dim: int=1) -> None:
        super().__init__()
        resnet_groups = resnet_groups if resnet_groups is not None else min(in_channels // 4, 32)
        self.add_attention = add_attention
        resnets = [HunyuanVideoResnetBlockCausal3D(in_channels=in_channels, out_channels=in_channels, eps=resnet_eps, groups=resnet_groups, dropout=dropout, non_linearity=resnet_act_fn)]
        attentions = []
        for _ in range(num_layers):
            if self.add_attention: attentions.append(Attention(in_channels, heads=in_channels // attention_head_dim, dim_head=attention_head_dim, eps=resnet_eps, norm_num_groups=resnet_groups,
            residual_connection=True, bias=True, upcast_softmax=True, _from_deprecated_attn_block=True))
            else: attentions.append(None)
            resnets.append(HunyuanVideoResnetBlockCausal3D(in_channels=in_channels, out_channels=in_channels, eps=resnet_eps, groups=resnet_groups, dropout=dropout, non_linearity=resnet_act_fn))
        self.attentions = nn.ModuleList(attentions)
        self.resnets = nn.ModuleList(resnets)
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        if torch.is_grad_enabled() and self.gradient_checkpointing:
            def create_custom_forward(module, return_dict=None):
                def custom_forward(*inputs):
                    if return_dict is not None: return module(*inputs, return_dict=return_dict)
                    else: return module(*inputs)
                return custom_forward
            ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
            hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(self.resnets[0]), hidden_states, **ckpt_kwargs)
            for attn, resnet in zip(self.attentions, self.resnets[1:]):
                if attn is not None:
                    batch_size, num_channels, num_frames, height, width = hidden_states.shape
                    hidden_states = hidden_states.permute(0, 2, 3, 4, 1).flatten(1, 3)
                    attention_mask = prepare_causal_attention_mask(num_frames, height * width, hidden_states.dtype, hidden_states.device, batch_size=batch_size)
                    hidden_states = attn(hidden_states, attention_mask=attention_mask)
                    hidden_states = hidden_states.unflatten(1, (num_frames, height, width)).permute(0, 4, 1, 2, 3)
                hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(resnet), hidden_states, **ckpt_kwargs)
        else:
            hidden_states = self.resnets[0](hidden_states)
            for attn, resnet in zip(self.attentions, self.resnets[1:]):
                if attn is not None:
                    batch_size, num_channels, num_frames, height, width = hidden_states.shape
                    hidden_states = hidden_states.permute(0, 2, 3, 4, 1).flatten(1, 3)
                    attention_mask = prepare_causal_attention_mask(num_frames, height * width, hidden_states.dtype, hidden_states.device, batch_size=batch_size)
                    hidden_states = attn(hidden_states, attention_mask=attention_mask)
                    hidden_states = hidden_states.unflatten(1, (num_frames, height, width)).permute(0, 4, 1, 2, 3)
                hidden_states = resnet(hidden_states)
        return hidden_states
class HunyuanVideoDownBlock3D(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, dropout: float=0.0, num_layers: int=1, resnet_eps: float=1e-06, resnet_act_fn: str='swish', resnet_groups: int=32, add_downsample: bool=True, downsample_stride: int=2, downsample_padding: int=1) -> None:
        super().__init__()
        resnets = []
        for i in range(num_layers):
            in_channels = in_channels if i == 0 else out_channels
            resnets.append(HunyuanVideoResnetBlockCausal3D(in_channels=in_channels, out_channels=out_channels, eps=resnet_eps, groups=resnet_groups, dropout=dropout, non_linearity=resnet_act_fn))
        self.resnets = nn.ModuleList(resnets)
        if add_downsample: self.downsamplers = nn.ModuleList([HunyuanVideoDownsampleCausal3D(out_channels, out_channels=out_channels, padding=downsample_padding, stride=downsample_stride)])
        else: self.downsamplers = None
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        if torch.is_grad_enabled() and self.gradient_checkpointing:
            def create_custom_forward(module, return_dict=None):
                def custom_forward(*inputs):
                    if return_dict is not None: return module(*inputs, return_dict=return_dict)
                    else: return module(*inputs)
                return custom_forward
            ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
            for resnet in self.resnets: hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(resnet), hidden_states, **ckpt_kwargs)
        else:
            for resnet in self.resnets: hidden_states = resnet(hidden_states)
        if self.downsamplers is not None:
            for downsampler in self.downsamplers: hidden_states = downsampler(hidden_states)
        return hidden_states
class HunyuanVideoUpBlock3D(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, dropout: float=0.0, num_layers: int=1, resnet_eps: float=1e-06, resnet_act_fn: str='swish', resnet_groups: int=32, add_upsample: bool=True, upsample_scale_factor: Tuple[int, int, int]=(2, 2, 2)) -> None:
        super().__init__()
        resnets = []
        for i in range(num_layers):
            input_channels = in_channels if i == 0 else out_channels
            resnets.append(HunyuanVideoResnetBlockCausal3D(in_channels=input_channels, out_channels=out_channels, eps=resnet_eps, groups=resnet_groups, dropout=dropout, non_linearity=resnet_act_fn))
        self.resnets = nn.ModuleList(resnets)
        if add_upsample: self.upsamplers = nn.ModuleList([HunyuanVideoUpsampleCausal3D(out_channels, out_channels=out_channels, upsample_factor=upsample_scale_factor)])
        else: self.upsamplers = None
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        if torch.is_grad_enabled() and self.gradient_checkpointing:
            def create_custom_forward(module, return_dict=None):
                def custom_forward(*inputs):
                    if return_dict is not None: return module(*inputs, return_dict=return_dict)
                    else: return module(*inputs)
                return custom_forward
            ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
            for resnet in self.resnets: hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(resnet), hidden_states, **ckpt_kwargs)
        else:
            for resnet in self.resnets: hidden_states = resnet(hidden_states)
        if self.upsamplers is not None:
            for upsampler in self.upsamplers: hidden_states = upsampler(hidden_states)
        return hidden_states
class HunyuanVideoEncoder3D(nn.Module):
    def __init__(self, in_channels: int=3, out_channels: int=3, down_block_types: Tuple[str, ...]=('HunyuanVideoDownBlock3D', 'HunyuanVideoDownBlock3D', 'HunyuanVideoDownBlock3D', 'HunyuanVideoDownBlock3D'),
    block_out_channels: Tuple[int, ...]=(128, 256, 512, 512), layers_per_block: int=2, norm_num_groups: int=32, act_fn: str='silu', double_z: bool=True, mid_block_add_attention=True, temporal_compression_ratio: int=4, spatial_compression_ratio: int=8) -> None:
        super().__init__()
        self.conv_in = HunyuanVideoCausalConv3d(in_channels, block_out_channels[0], kernel_size=3, stride=1)
        self.mid_block = None
        self.down_blocks = nn.ModuleList([])
        output_channel = block_out_channels[0]
        for i, down_block_type in enumerate(down_block_types):
            if down_block_type != 'HunyuanVideoDownBlock3D': raise ValueError(f'Unsupported down_block_type: {down_block_type}')
            input_channel = output_channel
            output_channel = block_out_channels[i]
            is_final_block = i == len(block_out_channels) - 1
            num_spatial_downsample_layers = int(np.log2(spatial_compression_ratio))
            num_time_downsample_layers = int(np.log2(temporal_compression_ratio))
            if temporal_compression_ratio == 4:
                add_spatial_downsample = bool(i < num_spatial_downsample_layers)
                add_time_downsample = bool(i >= len(block_out_channels) - 1 - num_time_downsample_layers and (not is_final_block))
            elif temporal_compression_ratio == 8:
                add_spatial_downsample = bool(i < num_spatial_downsample_layers)
                add_time_downsample = bool(i < num_time_downsample_layers)
            else: raise ValueError(f'Unsupported time_compression_ratio: {temporal_compression_ratio}')
            downsample_stride_HW = (2, 2) if add_spatial_downsample else (1, 1)
            downsample_stride_T = (2,) if add_time_downsample else (1,)
            downsample_stride = tuple(downsample_stride_T + downsample_stride_HW)
            down_block = HunyuanVideoDownBlock3D(num_layers=layers_per_block, in_channels=input_channel, out_channels=output_channel, add_downsample=bool(add_spatial_downsample or add_time_downsample), resnet_eps=1e-06, resnet_act_fn=act_fn,
            resnet_groups=norm_num_groups, downsample_stride=downsample_stride, downsample_padding=0)
            self.down_blocks.append(down_block)
        self.mid_block = HunyuanVideoMidBlock3D(in_channels=block_out_channels[-1], resnet_eps=1e-06, resnet_act_fn=act_fn, attention_head_dim=block_out_channels[-1], resnet_groups=norm_num_groups, add_attention=mid_block_add_attention)
        self.conv_norm_out = nn.GroupNorm(num_channels=block_out_channels[-1], num_groups=norm_num_groups, eps=1e-06)
        self.conv_act = nn.SiLU()
        conv_out_channels = 2 * out_channels if double_z else out_channels
        self.conv_out = HunyuanVideoCausalConv3d(block_out_channels[-1], conv_out_channels, kernel_size=3)
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.conv_in(hidden_states)
        if torch.is_grad_enabled() and self.gradient_checkpointing:
            def create_custom_forward(module, return_dict=None):
                def custom_forward(*inputs):
                    if return_dict is not None: return module(*inputs, return_dict=return_dict)
                    else: return module(*inputs)
                return custom_forward
            ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
            for down_block in self.down_blocks: hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(down_block), hidden_states, **ckpt_kwargs)
            hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(self.mid_block), hidden_states, **ckpt_kwargs)
        else:
            for down_block in self.down_blocks: hidden_states = down_block(hidden_states)
            hidden_states = self.mid_block(hidden_states)
        hidden_states = self.conv_norm_out(hidden_states)
        hidden_states = self.conv_act(hidden_states)
        hidden_states = self.conv_out(hidden_states)
        return hidden_states
class HunyuanVideoDecoder3D(nn.Module):
    def __init__(self, in_channels: int=3, out_channels: int=3, up_block_types: Tuple[str, ...]=('HunyuanVideoUpBlock3D', 'HunyuanVideoUpBlock3D', 'HunyuanVideoUpBlock3D', 'HunyuanVideoUpBlock3D'), block_out_channels: Tuple[int, ...]=(128, 256, 512, 512),
    layers_per_block: int=2, norm_num_groups: int=32, act_fn: str='silu', mid_block_add_attention=True, time_compression_ratio: int=4, spatial_compression_ratio: int=8):
        super().__init__()
        self.layers_per_block = layers_per_block
        self.conv_in = HunyuanVideoCausalConv3d(in_channels, block_out_channels[-1], kernel_size=3, stride=1)
        self.up_blocks = nn.ModuleList([])
        self.mid_block = HunyuanVideoMidBlock3D(in_channels=block_out_channels[-1], resnet_eps=1e-06, resnet_act_fn=act_fn, attention_head_dim=block_out_channels[-1], resnet_groups=norm_num_groups, add_attention=mid_block_add_attention)
        reversed_block_out_channels = list(reversed(block_out_channels))
        output_channel = reversed_block_out_channels[0]
        for i, up_block_type in enumerate(up_block_types):
            if up_block_type != 'HunyuanVideoUpBlock3D': raise ValueError(f'Unsupported up_block_type: {up_block_type}')
            prev_output_channel = output_channel
            output_channel = reversed_block_out_channels[i]
            is_final_block = i == len(block_out_channels) - 1
            num_spatial_upsample_layers = int(np.log2(spatial_compression_ratio))
            num_time_upsample_layers = int(np.log2(time_compression_ratio))
            if time_compression_ratio == 4:
                add_spatial_upsample = bool(i < num_spatial_upsample_layers)
                add_time_upsample = bool(i >= len(block_out_channels) - 1 - num_time_upsample_layers and (not is_final_block))
            else: raise ValueError(f'Unsupported time_compression_ratio: {time_compression_ratio}')
            upsample_scale_factor_HW = (2, 2) if add_spatial_upsample else (1, 1)
            upsample_scale_factor_T = (2,) if add_time_upsample else (1,)
            upsample_scale_factor = tuple(upsample_scale_factor_T + upsample_scale_factor_HW)
            up_block = HunyuanVideoUpBlock3D(num_layers=self.layers_per_block + 1, in_channels=prev_output_channel, out_channels=output_channel, add_upsample=bool(add_spatial_upsample or add_time_upsample), upsample_scale_factor=upsample_scale_factor,
            resnet_eps=1e-06, resnet_act_fn=act_fn, resnet_groups=norm_num_groups)
            self.up_blocks.append(up_block)
            prev_output_channel = output_channel
        self.conv_norm_out = nn.GroupNorm(num_channels=block_out_channels[0], num_groups=norm_num_groups, eps=1e-06)
        self.conv_act = nn.SiLU()
        self.conv_out = HunyuanVideoCausalConv3d(block_out_channels[0], out_channels, kernel_size=3)
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.conv_in(hidden_states)
        if torch.is_grad_enabled() and self.gradient_checkpointing:
            def create_custom_forward(module, return_dict=None):
                def custom_forward(*inputs):
                    if return_dict is not None: return module(*inputs, return_dict=return_dict)
                    else: return module(*inputs)
                return custom_forward
            ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
            hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(self.mid_block), hidden_states, **ckpt_kwargs)
            for up_block in self.up_blocks: hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(up_block), hidden_states, **ckpt_kwargs)
        else:
            hidden_states = self.mid_block(hidden_states)
            for up_block in self.up_blocks: hidden_states = up_block(hidden_states)
        hidden_states = self.conv_norm_out(hidden_states)
        hidden_states = self.conv_act(hidden_states)
        hidden_states = self.conv_out(hidden_states)
        return hidden_states
class AutoencoderKLHunyuanVideo(ModelMixin, ConfigMixin):
    _supports_gradient_checkpointing = True
    @register_to_config
    def __init__(self, in_channels: int=3, out_channels: int=3, latent_channels: int=16, down_block_types: Tuple[str, ...]=('HunyuanVideoDownBlock3D', 'HunyuanVideoDownBlock3D', 'HunyuanVideoDownBlock3D', 'HunyuanVideoDownBlock3D'),
    up_block_types: Tuple[str, ...]=('HunyuanVideoUpBlock3D', 'HunyuanVideoUpBlock3D', 'HunyuanVideoUpBlock3D', 'HunyuanVideoUpBlock3D'), block_out_channels: Tuple[int]=(128, 256, 512, 512), layers_per_block: int=2, act_fn: str='silu',
    norm_num_groups: int=32, scaling_factor: float=0.476986, spatial_compression_ratio: int=8, temporal_compression_ratio: int=4, mid_block_add_attention: bool=True) -> None:
        super().__init__()
        self.time_compression_ratio = temporal_compression_ratio
        self.encoder = HunyuanVideoEncoder3D(in_channels=in_channels, out_channels=latent_channels, down_block_types=down_block_types, block_out_channels=block_out_channels, layers_per_block=layers_per_block, norm_num_groups=norm_num_groups, act_fn=act_fn,
        double_z=True, mid_block_add_attention=mid_block_add_attention, temporal_compression_ratio=temporal_compression_ratio, spatial_compression_ratio=spatial_compression_ratio)
        self.decoder = HunyuanVideoDecoder3D(in_channels=latent_channels, out_channels=out_channels, up_block_types=up_block_types, block_out_channels=block_out_channels, layers_per_block=layers_per_block, norm_num_groups=norm_num_groups, act_fn=act_fn,
        time_compression_ratio=temporal_compression_ratio, spatial_compression_ratio=spatial_compression_ratio, mid_block_add_attention=mid_block_add_attention)
        self.quant_conv = nn.Conv3d(2 * latent_channels, 2 * latent_channels, kernel_size=1)
        self.post_quant_conv = nn.Conv3d(latent_channels, latent_channels, kernel_size=1)
        self.spatial_compression_ratio = spatial_compression_ratio
        self.temporal_compression_ratio = temporal_compression_ratio
        self.use_slicing = False
        self.use_tiling = False
        self.use_framewise_encoding = True
        self.use_framewise_decoding = True
        self.tile_sample_min_height = 256
        self.tile_sample_min_width = 256
        self.tile_sample_min_num_frames = 16
        self.tile_sample_stride_height = 192
        self.tile_sample_stride_width = 192
        self.tile_sample_stride_num_frames = 12
    def _set_gradient_checkpointing(self, module, value=False):
        if isinstance(module, (HunyuanVideoEncoder3D, HunyuanVideoDecoder3D)): module.gradient_checkpointing = value
    def enable_tiling(self, tile_sample_min_height: Optional[int]=None, tile_sample_min_width: Optional[int]=None, tile_sample_min_num_frames: Optional[int]=None, tile_sample_stride_height: Optional[float]=None, tile_sample_stride_width: Optional[float]=None,
    tile_sample_stride_num_frames: Optional[float]=None) -> None:
        """Args:"""
        self.use_tiling = True
        self.tile_sample_min_height = tile_sample_min_height or self.tile_sample_min_height
        self.tile_sample_min_width = tile_sample_min_width or self.tile_sample_min_width
        self.tile_sample_min_num_frames = tile_sample_min_num_frames or self.tile_sample_min_num_frames
        self.tile_sample_stride_height = tile_sample_stride_height or self.tile_sample_stride_height
        self.tile_sample_stride_width = tile_sample_stride_width or self.tile_sample_stride_width
        self.tile_sample_stride_num_frames = tile_sample_stride_num_frames or self.tile_sample_stride_num_frames
    def disable_tiling(self) -> None: self.use_tiling = False
    def enable_slicing(self) -> None: self.use_slicing = True
    def disable_slicing(self) -> None: self.use_slicing = False
    def _encode(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, num_channels, num_frames, height, width = x.shape
        if self.use_framewise_decoding and num_frames > self.tile_sample_min_num_frames: return self._temporal_tiled_encode(x)
        if self.use_tiling and (width > self.tile_sample_min_width or height > self.tile_sample_min_height): return self.tiled_encode(x)
        x = self.encoder(x)
        enc = self.quant_conv(x)
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
        tile_latent_min_height = self.tile_sample_min_height // self.spatial_compression_ratio
        tile_latent_min_width = self.tile_sample_stride_width // self.spatial_compression_ratio
        tile_latent_min_num_frames = self.tile_sample_min_num_frames // self.temporal_compression_ratio
        if self.use_framewise_decoding and num_frames > tile_latent_min_num_frames: return self._temporal_tiled_decode(z, return_dict=return_dict)
        if self.use_tiling and (width > tile_latent_min_width or height > tile_latent_min_height): return self.tiled_decode(z, return_dict=return_dict)
        z = self.post_quant_conv(z)
        dec = self.decoder(z)
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
        blend_extent = min(a.shape[-2], b.shape[-2], blend_extent)
        for y in range(blend_extent): b[:, :, :, y, :] = a[:, :, :, -blend_extent + y, :] * (1 - y / blend_extent) + b[:, :, :, y, :] * (y / blend_extent)
        return b
    def blend_h(self, a: torch.Tensor, b: torch.Tensor, blend_extent: int) -> torch.Tensor:
        blend_extent = min(a.shape[-1], b.shape[-1], blend_extent)
        for x in range(blend_extent): b[:, :, :, :, x] = a[:, :, :, :, -blend_extent + x] * (1 - x / blend_extent) + b[:, :, :, :, x] * (x / blend_extent)
        return b
    def blend_t(self, a: torch.Tensor, b: torch.Tensor, blend_extent: int) -> torch.Tensor:
        blend_extent = min(a.shape[-3], b.shape[-3], blend_extent)
        for x in range(blend_extent): b[:, :, x, :, :] = a[:, :, -blend_extent + x, :, :] * (1 - x / blend_extent) + b[:, :, x, :, :] * (x / blend_extent)
        return b
    def tiled_encode(self, x: torch.Tensor) -> AutoencoderKLOutput:
        """Returns:"""
        batch_size, num_channels, num_frames, height, width = x.shape
        latent_height = height // self.spatial_compression_ratio
        latent_width = width // self.spatial_compression_ratio
        tile_latent_min_height = self.tile_sample_min_height // self.spatial_compression_ratio
        tile_latent_min_width = self.tile_sample_min_width // self.spatial_compression_ratio
        tile_latent_stride_height = self.tile_sample_stride_height // self.spatial_compression_ratio
        tile_latent_stride_width = self.tile_sample_stride_width // self.spatial_compression_ratio
        blend_height = tile_latent_min_height - tile_latent_stride_height
        blend_width = tile_latent_min_width - tile_latent_stride_width
        rows = []
        for i in range(0, height, self.tile_sample_stride_height):
            row = []
            for j in range(0, width, self.tile_sample_stride_width):
                tile = x[:, :, :, i:i + self.tile_sample_min_height, j:j + self.tile_sample_min_width]
                tile = self.encoder(tile)
                tile = self.quant_conv(tile)
                row.append(tile)
            rows.append(row)
        result_rows = []
        for i, row in enumerate(rows):
            result_row = []
            for j, tile in enumerate(row):
                if i > 0: tile = self.blend_v(rows[i - 1][j], tile, blend_height)
                if j > 0: tile = self.blend_h(row[j - 1], tile, blend_width)
                result_row.append(tile[:, :, :, :tile_latent_stride_height, :tile_latent_stride_width])
            result_rows.append(torch.cat(result_row, dim=4))
        enc = torch.cat(result_rows, dim=3)[:, :, :, :latent_height, :latent_width]
        return enc
    def tiled_decode(self, z: torch.Tensor, return_dict: bool=True) -> Union[DecoderOutput, torch.Tensor]:
        """Returns:"""
        batch_size, num_channels, num_frames, height, width = z.shape
        sample_height = height * self.spatial_compression_ratio
        sample_width = width * self.spatial_compression_ratio
        tile_latent_min_height = self.tile_sample_min_height // self.spatial_compression_ratio
        tile_latent_min_width = self.tile_sample_min_width // self.spatial_compression_ratio
        tile_latent_stride_height = self.tile_sample_stride_height // self.spatial_compression_ratio
        tile_latent_stride_width = self.tile_sample_stride_width // self.spatial_compression_ratio
        blend_height = self.tile_sample_min_height - self.tile_sample_stride_height
        blend_width = self.tile_sample_min_width - self.tile_sample_stride_width
        rows = []
        for i in range(0, height, tile_latent_stride_height):
            row = []
            for j in range(0, width, tile_latent_stride_width):
                tile = z[:, :, :, i:i + tile_latent_min_height, j:j + tile_latent_min_width]
                tile = self.post_quant_conv(tile)
                decoded = self.decoder(tile)
                row.append(decoded)
            rows.append(row)
        result_rows = []
        for i, row in enumerate(rows):
            result_row = []
            for j, tile in enumerate(row):
                if i > 0: tile = self.blend_v(rows[i - 1][j], tile, blend_height)
                if j > 0: tile = self.blend_h(row[j - 1], tile, blend_width)
                result_row.append(tile[:, :, :, :self.tile_sample_stride_height, :self.tile_sample_stride_width])
            result_rows.append(torch.cat(result_row, dim=-1))
        dec = torch.cat(result_rows, dim=3)[:, :, :, :sample_height, :sample_width]
        if not return_dict: return (dec,)
        return DecoderOutput(sample=dec)
    def _temporal_tiled_encode(self, x: torch.Tensor) -> AutoencoderKLOutput:
        batch_size, num_channels, num_frames, height, width = x.shape
        latent_num_frames = (num_frames - 1) // self.temporal_compression_ratio + 1
        tile_latent_min_num_frames = self.tile_sample_min_num_frames // self.temporal_compression_ratio
        tile_latent_stride_num_frames = self.tile_sample_stride_num_frames // self.temporal_compression_ratio
        blend_num_frames = tile_latent_min_num_frames - tile_latent_stride_num_frames
        row = []
        for i in range(0, num_frames, self.tile_sample_stride_num_frames):
            tile = x[:, :, i:i + self.tile_sample_min_num_frames + 1, :, :]
            if self.use_tiling and (height > self.tile_sample_min_height or width > self.tile_sample_min_width): tile = self.tiled_encode(tile)
            else:
                tile = self.encoder(tile)
                tile = self.quant_conv(tile)
            if i > 0: tile = tile[:, :, 1:, :, :]
            row.append(tile)
        result_row = []
        for i, tile in enumerate(row):
            if i > 0:
                tile = self.blend_t(row[i - 1], tile, blend_num_frames)
                result_row.append(tile[:, :, :tile_latent_stride_num_frames, :, :])
            else: result_row.append(tile[:, :, :tile_latent_stride_num_frames + 1, :, :])
        enc = torch.cat(result_row, dim=2)[:, :, :latent_num_frames]
        return enc
    def _temporal_tiled_decode(self, z: torch.Tensor, return_dict: bool=True) -> Union[DecoderOutput, torch.Tensor]:
        batch_size, num_channels, num_frames, height, width = z.shape
        num_sample_frames = (num_frames - 1) * self.temporal_compression_ratio + 1
        tile_latent_min_height = self.tile_sample_min_height // self.spatial_compression_ratio
        tile_latent_min_width = self.tile_sample_min_width // self.spatial_compression_ratio
        tile_latent_min_num_frames = self.tile_sample_min_num_frames // self.temporal_compression_ratio
        tile_latent_stride_num_frames = self.tile_sample_stride_num_frames // self.temporal_compression_ratio
        blend_num_frames = self.tile_sample_min_num_frames - self.tile_sample_stride_num_frames
        row = []
        for i in range(0, num_frames, tile_latent_stride_num_frames):
            tile = z[:, :, i:i + tile_latent_min_num_frames + 1, :, :]
            if self.use_tiling and (tile.shape[-1] > tile_latent_min_width or tile.shape[-2] > tile_latent_min_height): decoded = self.tiled_decode(tile, return_dict=True).sample
            else:
                tile = self.post_quant_conv(tile)
                decoded = self.decoder(tile)
            if i > 0: decoded = decoded[:, :, 1:, :, :]
            row.append(decoded)
        result_row = []
        for i, tile in enumerate(row):
            if i > 0:
                tile = self.blend_t(row[i - 1], tile, blend_num_frames)
                result_row.append(tile[:, :, :self.tile_sample_stride_num_frames, :, :])
            else: result_row.append(tile[:, :, :self.tile_sample_stride_num_frames + 1, :, :])
        dec = torch.cat(result_row, dim=2)[:, :, :num_sample_frames]
        if not return_dict: return (dec,)
        return DecoderOutput(sample=dec)
    def forward(self, sample: torch.Tensor, sample_posterior: bool=False, return_dict: bool=True, generator: Optional[torch.Generator]=None) -> Union[DecoderOutput, torch.Tensor]:
        """Args:"""
        x = sample
        posterior = self.encode(x).latent_dist
        if sample_posterior: z = posterior.sample(generator=generator)
        else: z = posterior.mode()
        dec = self.decode(z, return_dict=return_dict)
        return dec
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
