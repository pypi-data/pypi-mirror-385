'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...configuration_utils import ConfigMixin, register_to_config
from ...utils.sapiens_accelerator_utils import apply_forward_hook
from ...utils.torch_utils import randn_tensor
from typing import Optional, Tuple, Union
from ..modeling_utils import ModelMixin
from torch.nn.utils import weight_norm
from dataclasses import dataclass
from ...utils import BaseOutput
import torch.nn as nn
import numpy as np
import torch
import math
class Snake1d(nn.Module):
    def __init__(self, hidden_dim, logscale=True):
        super().__init__()
        self.alpha = nn.Parameter(torch.zeros(1, hidden_dim, 1))
        self.beta = nn.Parameter(torch.zeros(1, hidden_dim, 1))
        self.alpha.requires_grad = True
        self.beta.requires_grad = True
        self.logscale = logscale
    def forward(self, hidden_states):
        shape = hidden_states.shape
        alpha = self.alpha if not self.logscale else torch.exp(self.alpha)
        beta = self.beta if not self.logscale else torch.exp(self.beta)
        hidden_states = hidden_states.reshape(shape[0], shape[1], -1)
        hidden_states = hidden_states + (beta + 1e-09).reciprocal() * torch.sin(alpha * hidden_states).pow(2)
        hidden_states = hidden_states.reshape(shape)
        return hidden_states
class OobleckResidualUnit(nn.Module):
    def __init__(self, dimension: int=16, dilation: int=1):
        super().__init__()
        pad = (7 - 1) * dilation // 2
        self.snake1 = Snake1d(dimension)
        self.conv1 = weight_norm(nn.Conv1d(dimension, dimension, kernel_size=7, dilation=dilation, padding=pad))
        self.snake2 = Snake1d(dimension)
        self.conv2 = weight_norm(nn.Conv1d(dimension, dimension, kernel_size=1))
    def forward(self, hidden_state):
        """Returns:"""
        output_tensor = hidden_state
        output_tensor = self.conv1(self.snake1(output_tensor))
        output_tensor = self.conv2(self.snake2(output_tensor))
        padding = (hidden_state.shape[-1] - output_tensor.shape[-1]) // 2
        if padding > 0: hidden_state = hidden_state[..., padding:-padding]
        output_tensor = hidden_state + output_tensor
        return output_tensor
class OobleckEncoderBlock(nn.Module):
    def __init__(self, input_dim, output_dim, stride: int=1):
        super().__init__()
        self.res_unit1 = OobleckResidualUnit(input_dim, dilation=1)
        self.res_unit2 = OobleckResidualUnit(input_dim, dilation=3)
        self.res_unit3 = OobleckResidualUnit(input_dim, dilation=9)
        self.snake1 = Snake1d(input_dim)
        self.conv1 = weight_norm(nn.Conv1d(input_dim, output_dim, kernel_size=2 * stride, stride=stride, padding=math.ceil(stride / 2)))
    def forward(self, hidden_state):
        hidden_state = self.res_unit1(hidden_state)
        hidden_state = self.res_unit2(hidden_state)
        hidden_state = self.snake1(self.res_unit3(hidden_state))
        hidden_state = self.conv1(hidden_state)
        return hidden_state
class OobleckDecoderBlock(nn.Module):
    def __init__(self, input_dim, output_dim, stride: int=1):
        super().__init__()
        self.snake1 = Snake1d(input_dim)
        self.conv_t1 = weight_norm(nn.ConvTranspose1d(input_dim, output_dim, kernel_size=2 * stride, stride=stride, padding=math.ceil(stride / 2)))
        self.res_unit1 = OobleckResidualUnit(output_dim, dilation=1)
        self.res_unit2 = OobleckResidualUnit(output_dim, dilation=3)
        self.res_unit3 = OobleckResidualUnit(output_dim, dilation=9)
    def forward(self, hidden_state):
        hidden_state = self.snake1(hidden_state)
        hidden_state = self.conv_t1(hidden_state)
        hidden_state = self.res_unit1(hidden_state)
        hidden_state = self.res_unit2(hidden_state)
        hidden_state = self.res_unit3(hidden_state)
        return hidden_state
class OobleckDiagonalGaussianDistribution(object):
    def __init__(self, parameters: torch.Tensor, deterministic: bool=False):
        self.parameters = parameters
        self.mean, self.scale = parameters.chunk(2, dim=1)
        self.std = nn.functional.softplus(self.scale) + 0.0001
        self.var = self.std * self.std
        self.logvar = torch.log(self.var)
        self.deterministic = deterministic
    def sample(self, generator: Optional[torch.Generator]=None) -> torch.Tensor:
        sample = randn_tensor(self.mean.shape, generator=generator, device=self.parameters.device, dtype=self.parameters.dtype)
        x = self.mean + self.std * sample
        return x
    def kl(self, other: 'OobleckDiagonalGaussianDistribution'=None) -> torch.Tensor:
        if self.deterministic: return torch.Tensor([0.0])
        elif other is None: return (self.mean * self.mean + self.var - self.logvar - 1.0).sum(1).mean()
        else:
            normalized_diff = torch.pow(self.mean - other.mean, 2) / other.var
            var_ratio = self.var / other.var
            logvar_diff = self.logvar - other.logvar
            kl = normalized_diff + var_ratio + logvar_diff - 1
            kl = kl.sum(1).mean()
            return kl
    def mode(self) -> torch.Tensor: return self.mean
@dataclass
class AutoencoderOobleckOutput(BaseOutput):
    """Args:"""
    latent_dist: 'OobleckDiagonalGaussianDistribution'
@dataclass
class OobleckDecoderOutput(BaseOutput):
    """Args:"""
    sample: torch.Tensor
class OobleckEncoder(nn.Module):
    def __init__(self, encoder_hidden_size, audio_channels, downsampling_ratios, channel_multiples):
        super().__init__()
        strides = downsampling_ratios
        channel_multiples = [1] + channel_multiples
        self.conv1 = weight_norm(nn.Conv1d(audio_channels, encoder_hidden_size, kernel_size=7, padding=3))
        self.block = []
        for stride_index, stride in enumerate(strides): self.block += [OobleckEncoderBlock(input_dim=encoder_hidden_size * channel_multiples[stride_index],
        output_dim=encoder_hidden_size * channel_multiples[stride_index + 1], stride=stride)]
        self.block = nn.ModuleList(self.block)
        d_model = encoder_hidden_size * channel_multiples[-1]
        self.snake1 = Snake1d(d_model)
        self.conv2 = weight_norm(nn.Conv1d(d_model, encoder_hidden_size, kernel_size=3, padding=1))
    def forward(self, hidden_state):
        hidden_state = self.conv1(hidden_state)
        for module in self.block: hidden_state = module(hidden_state)
        hidden_state = self.snake1(hidden_state)
        hidden_state = self.conv2(hidden_state)
        return hidden_state
class OobleckDecoder(nn.Module):
    def __init__(self, channels, input_channels, audio_channels, upsampling_ratios, channel_multiples):
        super().__init__()
        strides = upsampling_ratios
        channel_multiples = [1] + channel_multiples
        self.conv1 = weight_norm(nn.Conv1d(input_channels, channels * channel_multiples[-1], kernel_size=7, padding=3))
        block = []
        for stride_index, stride in enumerate(strides): block += [OobleckDecoderBlock(input_dim=channels * channel_multiples[len(strides) - stride_index],
        output_dim=channels * channel_multiples[len(strides) - stride_index - 1], stride=stride)]
        self.block = nn.ModuleList(block)
        output_dim = channels
        self.snake1 = Snake1d(output_dim)
        self.conv2 = weight_norm(nn.Conv1d(channels, audio_channels, kernel_size=7, padding=3, bias=False))
    def forward(self, hidden_state):
        hidden_state = self.conv1(hidden_state)
        for layer in self.block: hidden_state = layer(hidden_state)
        hidden_state = self.snake1(hidden_state)
        hidden_state = self.conv2(hidden_state)
        return hidden_state
class AutoencoderOobleck(ModelMixin, ConfigMixin):
    _supports_gradient_checkpointing = False
    @register_to_config
    def __init__(self, encoder_hidden_size=128, downsampling_ratios=[2, 4, 4, 8, 8], channel_multiples=[1, 2, 4, 8, 16], decoder_channels=128,
    decoder_input_channels=64, audio_channels=2, sampling_rate=44100):
        super().__init__()
        self.encoder_hidden_size = encoder_hidden_size
        self.downsampling_ratios = downsampling_ratios
        self.decoder_channels = decoder_channels
        self.upsampling_ratios = downsampling_ratios[::-1]
        self.hop_length = int(np.prod(downsampling_ratios))
        self.sampling_rate = sampling_rate
        self.encoder = OobleckEncoder(encoder_hidden_size=encoder_hidden_size, audio_channels=audio_channels, downsampling_ratios=downsampling_ratios, channel_multiples=channel_multiples)
        self.decoder = OobleckDecoder(channels=decoder_channels, input_channels=decoder_input_channels, audio_channels=audio_channels,
        upsampling_ratios=self.upsampling_ratios, channel_multiples=channel_multiples)
        self.use_slicing = False
    def enable_slicing(self): self.use_slicing = True
    def disable_slicing(self): self.use_slicing = False
    @apply_forward_hook
    def encode(self, x: torch.Tensor, return_dict: bool=True) -> Union[AutoencoderOobleckOutput, Tuple[OobleckDiagonalGaussianDistribution]]:
        """Returns:"""
        if self.use_slicing and x.shape[0] > 1:
            encoded_slices = [self.encoder(x_slice) for x_slice in x.split(1)]
            h = torch.cat(encoded_slices)
        else: h = self.encoder(x)
        posterior = OobleckDiagonalGaussianDistribution(h)
        if not return_dict: return (posterior,)
        return AutoencoderOobleckOutput(latent_dist=posterior)
    def _decode(self, z: torch.Tensor, return_dict: bool=True) -> Union[OobleckDecoderOutput, torch.Tensor]:
        dec = self.decoder(z)
        if not return_dict: return (dec,)
        return OobleckDecoderOutput(sample=dec)
    @apply_forward_hook
    def decode(self, z: torch.FloatTensor, return_dict: bool=True, generator=None) -> Union[OobleckDecoderOutput, torch.FloatTensor]:
        """Returns:"""
        if self.use_slicing and z.shape[0] > 1:
            decoded_slices = [self._decode(z_slice).sample for z_slice in z.split(1)]
            decoded = torch.cat(decoded_slices)
        else: decoded = self._decode(z).sample
        if not return_dict: return (decoded,)
        return OobleckDecoderOutput(sample=decoded)
    def forward(self, sample: torch.Tensor, sample_posterior: bool=False, return_dict: bool=True, generator: Optional[torch.Generator]=None) -> Union[OobleckDecoderOutput, torch.Tensor]:
        """Args:"""
        x = sample
        posterior = self.encode(x).latent_dist
        if sample_posterior: z = posterior.sample(generator=generator)
        else: z = posterior.mode()
        dec = self.decode(z).sample
        if not return_dict: return (dec,)
        return OobleckDecoderOutput(sample=dec)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
