'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..unets.unet_2d_blocks import AutoencoderTinyBlock, UNetMidBlock2D, get_down_block, get_up_block
from ...utils import BaseOutput, is_torch_version
from ...utils.torch_utils import randn_tensor
from ..attention_processor import SpatialNorm
from ..activations import get_activation
from typing import Optional, Tuple
from dataclasses import dataclass
import torch.nn as nn
import numpy as np
import torch
@dataclass
class EncoderOutput(BaseOutput):
    """Args:"""
    latent: torch.Tensor
@dataclass
class DecoderOutput(BaseOutput):
    """Args:"""
    sample: torch.Tensor
    commit_loss: Optional[torch.FloatTensor] = None
class Encoder(nn.Module):
    """Args:"""
    def __init__(self, in_channels: int=3, out_channels: int=3, down_block_types: Tuple[str, ...]=('DownEncoderBlock2D',), block_out_channels: Tuple[int, ...]=(64,), layers_per_block: int=2,
    norm_num_groups: int=32, act_fn: str='silu', double_z: bool=True, mid_block_add_attention=True):
        super().__init__()
        self.layers_per_block = layers_per_block
        self.conv_in = nn.Conv2d(in_channels, block_out_channels[0], kernel_size=3, stride=1, padding=1)
        self.down_blocks = nn.ModuleList([])
        output_channel = block_out_channels[0]
        for i, down_block_type in enumerate(down_block_types):
            input_channel = output_channel
            output_channel = block_out_channels[i]
            is_final_block = i == len(block_out_channels) - 1
            down_block = get_down_block(down_block_type, num_layers=self.layers_per_block, in_channels=input_channel, out_channels=output_channel, add_downsample=not is_final_block,
            resnet_eps=1e-06, downsample_padding=0, resnet_act_fn=act_fn, resnet_groups=norm_num_groups, attention_head_dim=output_channel, temb_channels=None)
            self.down_blocks.append(down_block)
        self.mid_block = UNetMidBlock2D(in_channels=block_out_channels[-1], resnet_eps=1e-06, resnet_act_fn=act_fn, output_scale_factor=1, resnet_time_scale_shift='default',
        attention_head_dim=block_out_channels[-1], resnet_groups=norm_num_groups, temb_channels=None, add_attention=mid_block_add_attention)
        self.conv_norm_out = nn.GroupNorm(num_channels=block_out_channels[-1], num_groups=norm_num_groups, eps=1e-06)
        self.conv_act = nn.SiLU()
        conv_out_channels = 2 * out_channels if double_z else out_channels
        self.conv_out = nn.Conv2d(block_out_channels[-1], conv_out_channels, 3, padding=1)
        self.gradient_checkpointing = False
    def forward(self, sample: torch.Tensor) -> torch.Tensor:
        sample = self.conv_in(sample)
        if torch.is_grad_enabled() and self.gradient_checkpointing:
            def create_custom_forward(module):
                def custom_forward(*inputs): return module(*inputs)
                return custom_forward
            if is_torch_version('>=', '1.11.0'):
                for down_block in self.down_blocks: sample = torch.utils.checkpoint.checkpoint(create_custom_forward(down_block), sample, use_reentrant=False)
                sample = torch.utils.checkpoint.checkpoint(create_custom_forward(self.mid_block), sample, use_reentrant=False)
            else:
                for down_block in self.down_blocks: sample = torch.utils.checkpoint.checkpoint(create_custom_forward(down_block), sample)
                sample = torch.utils.checkpoint.checkpoint(create_custom_forward(self.mid_block), sample)
        else:
            for down_block in self.down_blocks: sample = down_block(sample)
            sample = self.mid_block(sample)
        sample = self.conv_norm_out(sample)
        sample = self.conv_act(sample)
        sample = self.conv_out(sample)
        return sample
class Decoder(nn.Module):
    """Args:"""
    def __init__(self, in_channels: int=3, out_channels: int=3, up_block_types: Tuple[str, ...]=('UpDecoderBlock2D',), block_out_channels: Tuple[int, ...]=(64,), layers_per_block: int=2,
    norm_num_groups: int=32, act_fn: str='silu', norm_type: str='group', mid_block_add_attention=True):
        super().__init__()
        self.layers_per_block = layers_per_block
        self.conv_in = nn.Conv2d(in_channels, block_out_channels[-1], kernel_size=3, stride=1, padding=1)
        self.up_blocks = nn.ModuleList([])
        temb_channels = in_channels if norm_type == 'spatial' else None
        self.mid_block = UNetMidBlock2D(in_channels=block_out_channels[-1], resnet_eps=1e-06, resnet_act_fn=act_fn, output_scale_factor=1,
        resnet_time_scale_shift='default' if norm_type == 'group' else norm_type, attention_head_dim=block_out_channels[-1],
        resnet_groups=norm_num_groups, temb_channels=temb_channels, add_attention=mid_block_add_attention)
        reversed_block_out_channels = list(reversed(block_out_channels))
        output_channel = reversed_block_out_channels[0]
        for i, up_block_type in enumerate(up_block_types):
            prev_output_channel = output_channel
            output_channel = reversed_block_out_channels[i]
            is_final_block = i == len(block_out_channels) - 1
            up_block = get_up_block(up_block_type, num_layers=self.layers_per_block + 1, in_channels=prev_output_channel, out_channels=output_channel, prev_output_channel=None,
            add_upsample=not is_final_block, resnet_eps=1e-06, resnet_act_fn=act_fn, resnet_groups=norm_num_groups, attention_head_dim=output_channel,
            temb_channels=temb_channels, resnet_time_scale_shift=norm_type)
            self.up_blocks.append(up_block)
            prev_output_channel = output_channel
        if norm_type == 'spatial': self.conv_norm_out = SpatialNorm(block_out_channels[0], temb_channels)
        else: self.conv_norm_out = nn.GroupNorm(num_channels=block_out_channels[0], num_groups=norm_num_groups, eps=1e-06)
        self.conv_act = nn.SiLU()
        self.conv_out = nn.Conv2d(block_out_channels[0], out_channels, 3, padding=1)
        self.gradient_checkpointing = False
    def forward(self, sample: torch.Tensor, latent_embeds: Optional[torch.Tensor]=None) -> torch.Tensor:
        sample = self.conv_in(sample)
        upscale_dtype = next(iter(self.up_blocks.parameters())).dtype
        if torch.is_grad_enabled() and self.gradient_checkpointing:
            def create_custom_forward(module):
                def custom_forward(*inputs): return module(*inputs)
                return custom_forward
            if is_torch_version('>=', '1.11.0'):
                sample = torch.utils.checkpoint.checkpoint(create_custom_forward(self.mid_block), sample, latent_embeds, use_reentrant=False)
                sample = sample.to(upscale_dtype)
                for up_block in self.up_blocks: sample = torch.utils.checkpoint.checkpoint(create_custom_forward(up_block), sample, latent_embeds, use_reentrant=False)
            else:
                sample = torch.utils.checkpoint.checkpoint(create_custom_forward(self.mid_block), sample, latent_embeds)
                sample = sample.to(upscale_dtype)
                for up_block in self.up_blocks: sample = torch.utils.checkpoint.checkpoint(create_custom_forward(up_block), sample, latent_embeds)
        else:
            sample = self.mid_block(sample, latent_embeds)
            sample = sample.to(upscale_dtype)
            for up_block in self.up_blocks: sample = up_block(sample, latent_embeds)
        if latent_embeds is None: sample = self.conv_norm_out(sample)
        else: sample = self.conv_norm_out(sample, latent_embeds)
        sample = self.conv_act(sample)
        sample = self.conv_out(sample)
        return sample
class UpSample(nn.Module):
    """Args:"""
    def __init__(self, in_channels: int, out_channels: int) -> None:
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.deconv = nn.ConvTranspose2d(in_channels, out_channels, kernel_size=4, stride=2, padding=1)
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = torch.relu(x)
        x = self.deconv(x)
        return x
class MaskConditionEncoder(nn.Module):
    def __init__(self, in_ch: int, out_ch: int=192, res_ch: int=768, stride: int=16) -> None:
        super().__init__()
        channels = []
        while stride > 1:
            stride = stride // 2
            in_ch_ = out_ch * 2
            if out_ch > res_ch: out_ch = res_ch
            if stride == 1: in_ch_ = res_ch
            channels.append((in_ch_, out_ch))
            out_ch *= 2
        out_channels = []
        for _in_ch, _out_ch in channels: out_channels.append(_out_ch)
        out_channels.append(channels[-1][0])
        layers = []
        in_ch_ = in_ch
        for l in range(len(out_channels)):
            out_ch_ = out_channels[l]
            if l == 0 or l == 1: layers.append(nn.Conv2d(in_ch_, out_ch_, kernel_size=3, stride=1, padding=1))
            else: layers.append(nn.Conv2d(in_ch_, out_ch_, kernel_size=4, stride=2, padding=1))
            in_ch_ = out_ch_
        self.layers = nn.Sequential(*layers)
    def forward(self, x: torch.Tensor, mask=None) -> torch.Tensor:
        out = {}
        for l in range(len(self.layers)):
            layer = self.layers[l]
            x = layer(x)
            out[str(tuple(x.shape))] = x
            x = torch.relu(x)
        return out
class MaskConditionDecoder(nn.Module):
    """Args:"""
    def __init__(self, in_channels: int=3, out_channels: int=3, up_block_types: Tuple[str, ...]=('UpDecoderBlock2D',), block_out_channels: Tuple[int, ...]=(64,),
    layers_per_block: int=2, norm_num_groups: int=32, act_fn: str='silu', norm_type: str='group'):
        super().__init__()
        self.layers_per_block = layers_per_block
        self.conv_in = nn.Conv2d(in_channels, block_out_channels[-1], kernel_size=3, stride=1, padding=1)
        self.up_blocks = nn.ModuleList([])
        temb_channels = in_channels if norm_type == 'spatial' else None
        self.mid_block = UNetMidBlock2D(in_channels=block_out_channels[-1], resnet_eps=1e-06, resnet_act_fn=act_fn, output_scale_factor=1,
        resnet_time_scale_shift='default' if norm_type == 'group' else norm_type, attention_head_dim=block_out_channels[-1], resnet_groups=norm_num_groups, temb_channels=temb_channels)
        reversed_block_out_channels = list(reversed(block_out_channels))
        output_channel = reversed_block_out_channels[0]
        for i, up_block_type in enumerate(up_block_types):
            prev_output_channel = output_channel
            output_channel = reversed_block_out_channels[i]
            is_final_block = i == len(block_out_channels) - 1
            up_block = get_up_block(up_block_type, num_layers=self.layers_per_block + 1, in_channels=prev_output_channel, out_channels=output_channel,
            prev_output_channel=None, add_upsample=not is_final_block, resnet_eps=1e-06, resnet_act_fn=act_fn, resnet_groups=norm_num_groups, attention_head_dim=output_channel,
            temb_channels=temb_channels, resnet_time_scale_shift=norm_type)
            self.up_blocks.append(up_block)
            prev_output_channel = output_channel
        self.condition_encoder = MaskConditionEncoder(in_ch=out_channels, out_ch=block_out_channels[0], res_ch=block_out_channels[-1])
        if norm_type == 'spatial': self.conv_norm_out = SpatialNorm(block_out_channels[0], temb_channels)
        else: self.conv_norm_out = nn.GroupNorm(num_channels=block_out_channels[0], num_groups=norm_num_groups, eps=1e-06)
        self.conv_act = nn.SiLU()
        self.conv_out = nn.Conv2d(block_out_channels[0], out_channels, 3, padding=1)
        self.gradient_checkpointing = False
    def forward(self, z: torch.Tensor, image: Optional[torch.Tensor]=None, mask: Optional[torch.Tensor]=None, latent_embeds: Optional[torch.Tensor]=None) -> torch.Tensor:
        sample = z
        sample = self.conv_in(sample)
        upscale_dtype = next(iter(self.up_blocks.parameters())).dtype
        if torch.is_grad_enabled() and self.gradient_checkpointing:
            def create_custom_forward(module):
                def custom_forward(*inputs): return module(*inputs)
                return custom_forward
            if is_torch_version('>=', '1.11.0'):
                sample = torch.utils.checkpoint.checkpoint(create_custom_forward(self.mid_block), sample, latent_embeds, use_reentrant=False)
                sample = sample.to(upscale_dtype)
                if image is not None and mask is not None:
                    masked_image = (1 - mask) * image
                    im_x = torch.utils.checkpoint.checkpoint(create_custom_forward(self.condition_encoder), masked_image, mask, use_reentrant=False)
                for up_block in self.up_blocks:
                    if image is not None and mask is not None:
                        sample_ = im_x[str(tuple(sample.shape))]
                        mask_ = nn.functional.interpolate(mask, size=sample.shape[-2:], mode='nearest')
                        sample = sample * mask_ + sample_ * (1 - mask_)
                    sample = torch.utils.checkpoint.checkpoint(create_custom_forward(up_block), sample, latent_embeds, use_reentrant=False)
                if image is not None and mask is not None: sample = sample * mask + im_x[str(tuple(sample.shape))] * (1 - mask)
            else:
                sample = torch.utils.checkpoint.checkpoint(create_custom_forward(self.mid_block), sample, latent_embeds)
                sample = sample.to(upscale_dtype)
                if image is not None and mask is not None:
                    masked_image = (1 - mask) * image
                    im_x = torch.utils.checkpoint.checkpoint(create_custom_forward(self.condition_encoder), masked_image, mask)
                for up_block in self.up_blocks:
                    if image is not None and mask is not None:
                        sample_ = im_x[str(tuple(sample.shape))]
                        mask_ = nn.functional.interpolate(mask, size=sample.shape[-2:], mode='nearest')
                        sample = sample * mask_ + sample_ * (1 - mask_)
                    sample = torch.utils.checkpoint.checkpoint(create_custom_forward(up_block), sample, latent_embeds)
                if image is not None and mask is not None: sample = sample * mask + im_x[str(tuple(sample.shape))] * (1 - mask)
        else:
            sample = self.mid_block(sample, latent_embeds)
            sample = sample.to(upscale_dtype)
            if image is not None and mask is not None:
                masked_image = (1 - mask) * image
                im_x = self.condition_encoder(masked_image, mask)
            for up_block in self.up_blocks:
                if image is not None and mask is not None:
                    sample_ = im_x[str(tuple(sample.shape))]
                    mask_ = nn.functional.interpolate(mask, size=sample.shape[-2:], mode='nearest')
                    sample = sample * mask_ + sample_ * (1 - mask_)
                sample = up_block(sample, latent_embeds)
            if image is not None and mask is not None: sample = sample * mask + im_x[str(tuple(sample.shape))] * (1 - mask)
        if latent_embeds is None: sample = self.conv_norm_out(sample)
        else: sample = self.conv_norm_out(sample, latent_embeds)
        sample = self.conv_act(sample)
        sample = self.conv_out(sample)
        return sample
class VectorQuantizer(nn.Module):
    def __init__(self, n_e: int, vq_embed_dim: int, beta: float, remap=None, unknown_index: str='random', sane_index_shape: bool=False, legacy: bool=True):
        super().__init__()
        self.n_e = n_e
        self.vq_embed_dim = vq_embed_dim
        self.beta = beta
        self.legacy = legacy
        self.embedding = nn.Embedding(self.n_e, self.vq_embed_dim)
        self.embedding.weight.data.uniform_(-1.0 / self.n_e, 1.0 / self.n_e)
        self.remap = remap
        if self.remap is not None:
            self.register_buffer('used', torch.tensor(np.load(self.remap)))
            self.used: torch.Tensor
            self.re_embed = self.used.shape[0]
            self.unknown_index = unknown_index
            if self.unknown_index == 'extra':
                self.unknown_index = self.re_embed
                self.re_embed = self.re_embed + 1
        else: self.re_embed = n_e
        self.sane_index_shape = sane_index_shape
    def remap_to_used(self, inds: torch.LongTensor) -> torch.LongTensor:
        ishape = inds.shape
        assert len(ishape) > 1
        inds = inds.reshape(ishape[0], -1)
        used = self.used.to(inds)
        match = (inds[:, :, None] == used[None, None, ...]).long()
        new = match.argmax(-1)
        unknown = match.sum(2) < 1
        if self.unknown_index == 'random': new[unknown] = torch.randint(0, self.re_embed, size=new[unknown].shape).to(device=new.device)
        else: new[unknown] = self.unknown_index
        return new.reshape(ishape)
    def unmap_to_all(self, inds: torch.LongTensor) -> torch.LongTensor:
        ishape = inds.shape
        assert len(ishape) > 1
        inds = inds.reshape(ishape[0], -1)
        used = self.used.to(inds)
        if self.re_embed > self.used.shape[0]: inds[inds >= self.used.shape[0]] = 0
        back = torch.gather(used[None, :][inds.shape[0] * [0], :], 1, inds)
        return back.reshape(ishape)
    def forward(self, z: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, Tuple]:
        z = z.permute(0, 2, 3, 1).contiguous()
        z_flattened = z.view(-1, self.vq_embed_dim)
        min_encoding_indices = torch.argmin(torch.cdist(z_flattened, self.embedding.weight), dim=1)
        z_q = self.embedding(min_encoding_indices).view(z.shape)
        perplexity = None
        min_encodings = None
        if not self.legacy: loss = self.beta * torch.mean((z_q.detach() - z) ** 2) + torch.mean((z_q - z.detach()) ** 2)
        else: loss = torch.mean((z_q.detach() - z) ** 2) + self.beta * torch.mean((z_q - z.detach()) ** 2)
        z_q: torch.Tensor = z + (z_q - z).detach()
        z_q = z_q.permute(0, 3, 1, 2).contiguous()
        if self.remap is not None:
            min_encoding_indices = min_encoding_indices.reshape(z.shape[0], -1)
            min_encoding_indices = self.remap_to_used(min_encoding_indices)
            min_encoding_indices = min_encoding_indices.reshape(-1, 1)
        if self.sane_index_shape: min_encoding_indices = min_encoding_indices.reshape(z_q.shape[0], z_q.shape[2], z_q.shape[3])
        return (z_q, loss, (perplexity, min_encodings, min_encoding_indices))
    def get_codebook_entry(self, indices: torch.LongTensor, shape: Tuple[int, ...]) -> torch.Tensor:
        if self.remap is not None:
            indices = indices.reshape(shape[0], -1)
            indices = self.unmap_to_all(indices)
            indices = indices.reshape(-1)
        z_q: torch.Tensor = self.embedding(indices)
        if shape is not None:
            z_q = z_q.view(shape)
            z_q = z_q.permute(0, 3, 1, 2).contiguous()
        return z_q
class DiagonalGaussianDistribution(object):
    def __init__(self, parameters: torch.Tensor, deterministic: bool=False):
        self.parameters = parameters
        self.mean, self.logvar = torch.chunk(parameters, 2, dim=1)
        self.logvar = torch.clamp(self.logvar, -30.0, 20.0)
        self.deterministic = deterministic
        self.std = torch.exp(0.5 * self.logvar)
        self.var = torch.exp(self.logvar)
        if self.deterministic: self.var = self.std = torch.zeros_like(self.mean, device=self.parameters.device, dtype=self.parameters.dtype)
    def sample(self, generator: Optional[torch.Generator]=None) -> torch.Tensor:
        sample = randn_tensor(self.mean.shape, generator=generator, device=self.parameters.device, dtype=self.parameters.dtype)
        x = self.mean + self.std * sample
        return x
    def kl(self, other: 'DiagonalGaussianDistribution'=None) -> torch.Tensor:
        if self.deterministic: return torch.Tensor([0.0])
        elif other is None: return 0.5 * torch.sum(torch.pow(self.mean, 2) + self.var - 1.0 - self.logvar, dim=[1, 2, 3])
        else: return 0.5 * torch.sum(torch.pow(self.mean - other.mean, 2) / other.var + self.var / other.var - 1.0 - self.logvar + other.logvar, dim=[1, 2, 3])
    def nll(self, sample: torch.Tensor, dims: Tuple[int, ...]=[1, 2, 3]) -> torch.Tensor:
        if self.deterministic: return torch.Tensor([0.0])
        logtwopi = np.log(2.0 * np.pi)
        return 0.5 * torch.sum(logtwopi + self.logvar + torch.pow(sample - self.mean, 2) / self.var, dim=dims)
    def mode(self) -> torch.Tensor: return self.mean
class EncoderTiny(nn.Module):
    """Args:"""
    def __init__(self, in_channels: int, out_channels: int, num_blocks: Tuple[int, ...], block_out_channels: Tuple[int, ...], act_fn: str):
        super().__init__()
        layers = []
        for i, num_block in enumerate(num_blocks):
            num_channels = block_out_channels[i]
            if i == 0: layers.append(nn.Conv2d(in_channels, num_channels, kernel_size=3, padding=1))
            else: layers.append(nn.Conv2d(num_channels, num_channels, kernel_size=3, padding=1, stride=2, bias=False))
            for _ in range(num_block): layers.append(AutoencoderTinyBlock(num_channels, num_channels, act_fn))
        layers.append(nn.Conv2d(block_out_channels[-1], out_channels, kernel_size=3, padding=1))
        self.layers = nn.Sequential(*layers)
        self.gradient_checkpointing = False
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if torch.is_grad_enabled() and self.gradient_checkpointing:
            def create_custom_forward(module):
                def custom_forward(*inputs): return module(*inputs)
                return custom_forward
            if is_torch_version('>=', '1.11.0'): x = torch.utils.checkpoint.checkpoint(create_custom_forward(self.layers), x, use_reentrant=False)
            else: x = torch.utils.checkpoint.checkpoint(create_custom_forward(self.layers), x)
        else: x = self.layers(x.add(1).div(2))
        return x
class DecoderTiny(nn.Module):
    """Args:"""
    def __init__(self, in_channels: int, out_channels: int, num_blocks: Tuple[int, ...], block_out_channels: Tuple[int, ...], upsampling_scaling_factor: int, act_fn: str, upsample_fn: str):
        super().__init__()
        layers = [nn.Conv2d(in_channels, block_out_channels[0], kernel_size=3, padding=1), get_activation(act_fn)]
        for i, num_block in enumerate(num_blocks):
            is_final_block = i == len(num_blocks) - 1
            num_channels = block_out_channels[i]
            for _ in range(num_block): layers.append(AutoencoderTinyBlock(num_channels, num_channels, act_fn))
            if not is_final_block: layers.append(nn.Upsample(scale_factor=upsampling_scaling_factor, mode=upsample_fn))
            conv_out_channel = num_channels if not is_final_block else out_channels
            layers.append(nn.Conv2d(num_channels, conv_out_channel, kernel_size=3, padding=1, bias=is_final_block))
        self.layers = nn.Sequential(*layers)
        self.gradient_checkpointing = False
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = torch.tanh(x / 3) * 3
        if torch.is_grad_enabled() and self.gradient_checkpointing:
            def create_custom_forward(module):
                def custom_forward(*inputs): return module(*inputs)
                return custom_forward
            if is_torch_version('>=', '1.11.0'): x = torch.utils.checkpoint.checkpoint(create_custom_forward(self.layers), x, use_reentrant=False)
            else: x = torch.utils.checkpoint.checkpoint(create_custom_forward(self.layers), x)
        else: x = self.layers(x)
        return x.mul(2).sub(1)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
