'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from .vae import DecoderOutput, DiagonalGaussianDistribution, Encoder, MaskConditionDecoder
from ...configuration_utils import ConfigMixin, register_to_config
from ...utils.sapiens_accelerator_utils import apply_forward_hook
from ..modeling_outputs import AutoencoderKLOutput
from typing import Optional, Tuple, Union
from ..modeling_utils import ModelMixin
import torch.nn as nn
import torch
class AsymmetricAutoencoderKL(ModelMixin, ConfigMixin):
    @register_to_config
    def __init__(self, in_channels: int=3, out_channels: int=3, down_block_types: Tuple[str, ...]=('DownEncoderBlock2D',), down_block_out_channels: Tuple[int, ...]=(64,),
    layers_per_down_block: int=1, up_block_types: Tuple[str, ...]=('UpDecoderBlock2D',), up_block_out_channels: Tuple[int, ...]=(64,), layers_per_up_block: int=1, act_fn: str='silu',
    latent_channels: int=4, norm_num_groups: int=32, sample_size: int=32, scaling_factor: float=0.18215) -> None:
        super().__init__()
        self.encoder = Encoder(in_channels=in_channels, out_channels=latent_channels, down_block_types=down_block_types, block_out_channels=down_block_out_channels,
        layers_per_block=layers_per_down_block, act_fn=act_fn, norm_num_groups=norm_num_groups, double_z=True)
        self.decoder = MaskConditionDecoder(in_channels=latent_channels, out_channels=out_channels, up_block_types=up_block_types, block_out_channels=up_block_out_channels,
        layers_per_block=layers_per_up_block, act_fn=act_fn, norm_num_groups=norm_num_groups)
        self.quant_conv = nn.Conv2d(2 * latent_channels, 2 * latent_channels, 1)
        self.post_quant_conv = nn.Conv2d(latent_channels, latent_channels, 1)
        self.use_slicing = False
        self.use_tiling = False
        self.register_to_config(block_out_channels=up_block_out_channels)
        self.register_to_config(force_upcast=False)
    @apply_forward_hook
    def encode(self, x: torch.Tensor, return_dict: bool=True) -> Union[AutoencoderKLOutput, Tuple[torch.Tensor]]:
        h = self.encoder(x)
        moments = self.quant_conv(h)
        posterior = DiagonalGaussianDistribution(moments)
        if not return_dict: return (posterior,)
        return AutoencoderKLOutput(latent_dist=posterior)
    def _decode(self, z: torch.Tensor, image: Optional[torch.Tensor]=None, mask: Optional[torch.Tensor]=None, return_dict: bool=True) -> Union[DecoderOutput, Tuple[torch.Tensor]]:
        z = self.post_quant_conv(z)
        dec = self.decoder(z, image, mask)
        if not return_dict: return (dec,)
        return DecoderOutput(sample=dec)
    @apply_forward_hook
    def decode(self, z: torch.Tensor, generator: Optional[torch.Generator]=None, image: Optional[torch.Tensor]=None, mask: Optional[torch.Tensor]=None, return_dict: bool=True) -> Union[DecoderOutput, Tuple[torch.Tensor]]:
        decoded = self._decode(z, image, mask).sample
        if not return_dict: return (decoded,)
        return DecoderOutput(sample=decoded)
    def forward(self, sample: torch.Tensor, mask: Optional[torch.Tensor]=None, sample_posterior: bool=False, return_dict: bool=True, generator: Optional[torch.Generator]=None) -> Union[DecoderOutput, Tuple[torch.Tensor]]:
        """Args:"""
        x = sample
        posterior = self.encode(x).latent_dist
        if sample_posterior: z = posterior.sample(generator=generator)
        else: z = posterior.mode()
        dec = self.decode(z, generator, sample, mask).sample
        if not return_dict: return (dec,)
        return DecoderOutput(sample=dec)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
