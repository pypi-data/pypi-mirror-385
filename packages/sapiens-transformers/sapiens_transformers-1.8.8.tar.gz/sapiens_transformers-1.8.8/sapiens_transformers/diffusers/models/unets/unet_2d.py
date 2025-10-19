'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..embeddings import GaussianFourierProjection, TimestepEmbedding, Timesteps
from .unet_2d_blocks import UNetMidBlock2D, get_down_block, get_up_block
from ...configuration_utils import ConfigMixin, register_to_config
from typing import Optional, Tuple, Union
from ..modeling_utils import ModelMixin
from dataclasses import dataclass
from ...utils import BaseOutput
import torch.nn as nn
import torch
@dataclass
class UNet2DOutput(BaseOutput):
    """Args:"""
    sample: torch.Tensor
class UNet2DModel(ModelMixin, ConfigMixin):
    _supports_gradient_checkpointing = True
    @register_to_config
    def __init__(self, sample_size: Optional[Union[int, Tuple[int, int]]]=None, in_channels: int=3, out_channels: int=3, center_input_sample: bool=False, time_embedding_type: str='positional',
    time_embedding_dim: Optional[int]=None, freq_shift: int=0, flip_sin_to_cos: bool=True, down_block_types: Tuple[str, ...]=('DownBlock2D', 'AttnDownBlock2D', 'AttnDownBlock2D', 'AttnDownBlock2D'),
    up_block_types: Tuple[str, ...]=('AttnUpBlock2D', 'AttnUpBlock2D', 'AttnUpBlock2D', 'UpBlock2D'), block_out_channels: Tuple[int, ...]=(224, 448, 672, 896), layers_per_block: int=2,
    mid_block_scale_factor: float=1, downsample_padding: int=1, downsample_type: str='conv', upsample_type: str='conv', dropout: float=0.0, act_fn: str='silu', attention_head_dim: Optional[int]=8,
    norm_num_groups: int=32, attn_norm_num_groups: Optional[int]=None, norm_eps: float=1e-05, resnet_time_scale_shift: str='default', add_attention: bool=True, class_embed_type: Optional[str]=None,
    num_class_embeds: Optional[int]=None, num_train_timesteps: Optional[int]=None):
        super().__init__()
        self.sample_size = sample_size
        time_embed_dim = time_embedding_dim or block_out_channels[0] * 4
        if len(down_block_types) != len(up_block_types): raise ValueError(f'Must provide the same number of `down_block_types` as `up_block_types`. `down_block_types`: {down_block_types}. `up_block_types`: {up_block_types}.')
        if len(block_out_channels) != len(down_block_types): raise ValueError(f'Must provide the same number of `block_out_channels` as `down_block_types`. `block_out_channels`: {block_out_channels}. `down_block_types`: {down_block_types}.')
        self.conv_in = nn.Conv2d(in_channels, block_out_channels[0], kernel_size=3, padding=(1, 1))
        if time_embedding_type == 'fourier':
            self.time_proj = GaussianFourierProjection(embedding_size=block_out_channels[0], scale=16)
            timestep_input_dim = 2 * block_out_channels[0]
        elif time_embedding_type == 'positional':
            self.time_proj = Timesteps(block_out_channels[0], flip_sin_to_cos, freq_shift)
            timestep_input_dim = block_out_channels[0]
        elif time_embedding_type == 'learned':
            self.time_proj = nn.Embedding(num_train_timesteps, block_out_channels[0])
            timestep_input_dim = block_out_channels[0]
        self.time_embedding = TimestepEmbedding(timestep_input_dim, time_embed_dim)
        if class_embed_type is None and num_class_embeds is not None: self.class_embedding = nn.Embedding(num_class_embeds, time_embed_dim)
        elif class_embed_type == 'timestep': self.class_embedding = TimestepEmbedding(timestep_input_dim, time_embed_dim)
        elif class_embed_type == 'identity': self.class_embedding = nn.Identity(time_embed_dim, time_embed_dim)
        else: self.class_embedding = None
        self.down_blocks = nn.ModuleList([])
        self.mid_block = None
        self.up_blocks = nn.ModuleList([])
        output_channel = block_out_channels[0]
        for i, down_block_type in enumerate(down_block_types):
            input_channel = output_channel
            output_channel = block_out_channels[i]
            is_final_block = i == len(block_out_channels) - 1
            down_block = get_down_block(down_block_type, num_layers=layers_per_block, in_channels=input_channel, out_channels=output_channel, temb_channels=time_embed_dim, add_downsample=not is_final_block,
            resnet_eps=norm_eps, resnet_act_fn=act_fn, resnet_groups=norm_num_groups, attention_head_dim=attention_head_dim if attention_head_dim is not None else output_channel, downsample_padding=downsample_padding,
            resnet_time_scale_shift=resnet_time_scale_shift, downsample_type=downsample_type, dropout=dropout)
            self.down_blocks.append(down_block)
        self.mid_block = UNetMidBlock2D(in_channels=block_out_channels[-1], temb_channels=time_embed_dim, dropout=dropout, resnet_eps=norm_eps, resnet_act_fn=act_fn, output_scale_factor=mid_block_scale_factor,
        resnet_time_scale_shift=resnet_time_scale_shift, attention_head_dim=attention_head_dim if attention_head_dim is not None else block_out_channels[-1],
        resnet_groups=norm_num_groups, attn_groups=attn_norm_num_groups, add_attention=add_attention)
        reversed_block_out_channels = list(reversed(block_out_channels))
        output_channel = reversed_block_out_channels[0]
        for i, up_block_type in enumerate(up_block_types):
            prev_output_channel = output_channel
            output_channel = reversed_block_out_channels[i]
            input_channel = reversed_block_out_channels[min(i + 1, len(block_out_channels) - 1)]
            is_final_block = i == len(block_out_channels) - 1
            up_block = get_up_block(up_block_type, num_layers=layers_per_block + 1, in_channels=input_channel, out_channels=output_channel, prev_output_channel=prev_output_channel,
            temb_channels=time_embed_dim, add_upsample=not is_final_block, resnet_eps=norm_eps, resnet_act_fn=act_fn, resnet_groups=norm_num_groups,
            attention_head_dim=attention_head_dim if attention_head_dim is not None else output_channel, resnet_time_scale_shift=resnet_time_scale_shift, upsample_type=upsample_type, dropout=dropout)
            self.up_blocks.append(up_block)
            prev_output_channel = output_channel
        num_groups_out = norm_num_groups if norm_num_groups is not None else min(block_out_channels[0] // 4, 32)
        self.conv_norm_out = nn.GroupNorm(num_channels=block_out_channels[0], num_groups=num_groups_out, eps=norm_eps)
        self.conv_act = nn.SiLU()
        self.conv_out = nn.Conv2d(block_out_channels[0], out_channels, kernel_size=3, padding=1)
    def _set_gradient_checkpointing(self, module, value=False):
        if hasattr(module, 'gradient_checkpointing'): module.gradient_checkpointing = value
    def forward(self, sample: torch.Tensor, timestep: Union[torch.Tensor, float, int], class_labels: Optional[torch.Tensor]=None, return_dict: bool=True) -> Union[UNet2DOutput, Tuple]:
        """Returns:"""
        if self.config.center_input_sample: sample = 2 * sample - 1.0
        timesteps = timestep
        if not torch.is_tensor(timesteps): timesteps = torch.tensor([timesteps], dtype=torch.long, device=sample.device)
        elif torch.is_tensor(timesteps) and len(timesteps.shape) == 0: timesteps = timesteps[None].to(sample.device)
        timesteps = timesteps * torch.ones(sample.shape[0], dtype=timesteps.dtype, device=timesteps.device)
        t_emb = self.time_proj(timesteps)
        t_emb = t_emb.to(dtype=self.dtype)
        emb = self.time_embedding(t_emb)
        if self.class_embedding is not None:
            if class_labels is None: raise ValueError('class_labels should be provided when doing class conditioning')
            if self.config.class_embed_type == 'timestep': class_labels = self.time_proj(class_labels)
            class_emb = self.class_embedding(class_labels).to(dtype=self.dtype)
            emb = emb + class_emb
        elif self.class_embedding is None and class_labels is not None: raise ValueError('class_embedding needs to be initialized in order to use class conditioning')
        skip_sample = sample
        sample = self.conv_in(sample)
        down_block_res_samples = (sample,)
        for downsample_block in self.down_blocks:
            if hasattr(downsample_block, 'skip_conv'): sample, res_samples, skip_sample = downsample_block(hidden_states=sample, temb=emb, skip_sample=skip_sample)
            else: sample, res_samples = downsample_block(hidden_states=sample, temb=emb)
            down_block_res_samples += res_samples
        sample = self.mid_block(sample, emb)
        skip_sample = None
        for upsample_block in self.up_blocks:
            res_samples = down_block_res_samples[-len(upsample_block.resnets):]
            down_block_res_samples = down_block_res_samples[:-len(upsample_block.resnets)]
            if hasattr(upsample_block, 'skip_conv'): sample, skip_sample = upsample_block(sample, res_samples, emb, skip_sample)
            else: sample = upsample_block(sample, res_samples, emb)
        sample = self.conv_norm_out(sample)
        sample = self.conv_act(sample)
        sample = self.conv_out(sample)
        if skip_sample is not None: sample += skip_sample
        if self.config.time_embedding_type == 'fourier':
            timesteps = timesteps.reshape((sample.shape[0], *[1] * len(sample.shape[1:])))
            sample = sample / timesteps
        if not return_dict: return (sample,)
        return UNet2DOutput(sample=sample)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
