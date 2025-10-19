'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..attention_processor import ADDED_KV_ATTENTION_PROCESSORS, CROSS_ATTENTION_PROCESSORS, Attention, AttentionProcessor, AttnAddedKVProcessor, AttnProcessor, FusedAttnProcessor2_0
from .vae import Decoder, DecoderOutput, DiagonalGaussianDistribution, Encoder
from ...configuration_utils import ConfigMixin, register_to_config
from ...loaders.single_file_model import FromOriginalModelMixin
from ...utils.sapiens_accelerator_utils import apply_forward_hook
from ..modeling_outputs import AutoencoderKLOutput
from typing import Dict, Optional, Tuple, Union
from ...loaders import PeftAdapterMixin
from ..modeling_utils import ModelMixin
from ...utils import deprecate
import torch.nn as nn
import torch
class AutoencoderKL(ModelMixin, ConfigMixin, FromOriginalModelMixin, PeftAdapterMixin):
    _supports_gradient_checkpointing = True
    _no_split_modules = ['BasicTransformerBlock', 'ResnetBlock2D']
    @register_to_config
    def __init__(self, in_channels: int=3, out_channels: int=3, down_block_types: Tuple[str]=('DownEncoderBlock2D',), up_block_types: Tuple[str]=('UpDecoderBlock2D',), block_out_channels: Tuple[int]=(64,),
    layers_per_block: int=1, act_fn: str='silu', latent_channels: int=4, norm_num_groups: int=32, sample_size: int=32, scaling_factor: float=0.18215, shift_factor: Optional[float]=None,
    latents_mean: Optional[Tuple[float]]=None, latents_std: Optional[Tuple[float]]=None, force_upcast: float=True, use_quant_conv: bool=True, use_post_quant_conv: bool=True, mid_block_add_attention: bool=True):
        super().__init__()
        self.encoder = Encoder(in_channels=in_channels, out_channels=latent_channels, down_block_types=down_block_types, block_out_channels=block_out_channels, layers_per_block=layers_per_block,
        act_fn=act_fn, norm_num_groups=norm_num_groups, double_z=True, mid_block_add_attention=mid_block_add_attention)
        self.decoder = Decoder(in_channels=latent_channels, out_channels=out_channels, up_block_types=up_block_types, block_out_channels=block_out_channels, layers_per_block=layers_per_block,
        norm_num_groups=norm_num_groups, act_fn=act_fn, mid_block_add_attention=mid_block_add_attention)
        self.quant_conv = nn.Conv2d(2 * latent_channels, 2 * latent_channels, 1) if use_quant_conv else None
        self.post_quant_conv = nn.Conv2d(latent_channels, latent_channels, 1) if use_post_quant_conv else None
        self.use_slicing = False
        self.use_tiling = False
        self.tile_sample_min_size = self.config.sample_size
        sample_size = self.config.sample_size[0] if isinstance(self.config.sample_size, (list, tuple)) else self.config.sample_size
        self.tile_latent_min_size = int(sample_size / 2 ** (len(self.config.block_out_channels) - 1))
        self.tile_overlap_factor = 0.25
    def _set_gradient_checkpointing(self, module, value=False):
        if isinstance(module, (Encoder, Decoder)): module.gradient_checkpointing = value
    def enable_tiling(self, use_tiling: bool=True): self.use_tiling = use_tiling
    def disable_tiling(self): self.enable_tiling(False)
    def enable_slicing(self): self.use_slicing = True
    def disable_slicing(self): self.use_slicing = False
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
    def _encode(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, num_channels, height, width = x.shape
        if self.use_tiling and (width > self.tile_sample_min_size or height > self.tile_sample_min_size): return self._tiled_encode(x)
        enc = self.encoder(x)
        if self.quant_conv is not None: enc = self.quant_conv(enc)
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
        if self.use_tiling and (z.shape[-1] > self.tile_latent_min_size or z.shape[-2] > self.tile_latent_min_size): return self.tiled_decode(z, return_dict=return_dict)
        if self.post_quant_conv is not None: z = self.post_quant_conv(z)
        dec = self.decoder(z)
        if not return_dict: return (dec,)
        return DecoderOutput(sample=dec)
    @apply_forward_hook
    def decode(self, z: torch.FloatTensor, return_dict: bool=True, generator=None) -> Union[DecoderOutput, torch.FloatTensor]:
        """Returns:"""
        if self.use_slicing and z.shape[0] > 1:
            decoded_slices = [self._decode(z_slice).sample for z_slice in z.split(1)]
            decoded = torch.cat(decoded_slices)
        else: decoded = self._decode(z).sample
        if not return_dict: return (decoded,)
        return DecoderOutput(sample=decoded)
    def blend_v(self, a: torch.Tensor, b: torch.Tensor, blend_extent: int) -> torch.Tensor:
        blend_extent = min(a.shape[2], b.shape[2], blend_extent)
        for y in range(blend_extent): b[:, :, y, :] = a[:, :, -blend_extent + y, :] * (1 - y / blend_extent) + b[:, :, y, :] * (y / blend_extent)
        return b
    def blend_h(self, a: torch.Tensor, b: torch.Tensor, blend_extent: int) -> torch.Tensor:
        blend_extent = min(a.shape[3], b.shape[3], blend_extent)
        for x in range(blend_extent): b[:, :, :, x] = a[:, :, :, -blend_extent + x] * (1 - x / blend_extent) + b[:, :, :, x] * (x / blend_extent)
        return b
    def _tiled_encode(self, x: torch.Tensor) -> torch.Tensor:
        """Returns:"""
        overlap_size = int(self.tile_sample_min_size * (1 - self.tile_overlap_factor))
        blend_extent = int(self.tile_latent_min_size * self.tile_overlap_factor)
        row_limit = self.tile_latent_min_size - blend_extent
        rows = []
        for i in range(0, x.shape[2], overlap_size):
            row = []
            for j in range(0, x.shape[3], overlap_size):
                tile = x[:, :, i:i + self.tile_sample_min_size, j:j + self.tile_sample_min_size]
                tile = self.encoder(tile)
                if self.config.use_quant_conv: tile = self.quant_conv(tile)
                row.append(tile)
            rows.append(row)
        result_rows = []
        for i, row in enumerate(rows):
            result_row = []
            for j, tile in enumerate(row):
                if i > 0: tile = self.blend_v(rows[i - 1][j], tile, blend_extent)
                if j > 0: tile = self.blend_h(row[j - 1], tile, blend_extent)
                result_row.append(tile[:, :, :row_limit, :row_limit])
            result_rows.append(torch.cat(result_row, dim=3))
        enc = torch.cat(result_rows, dim=2)
        return enc
    def tiled_encode(self, x: torch.Tensor, return_dict: bool=True) -> AutoencoderKLOutput:
        """Returns:"""
        deprecation_message = 'The tiled_encode implementation supporting the `return_dict` parameter is deprecated. In the future, the implementation of this method will be replaced with that of `_tiled_encode` and you will no longer be able to pass `return_dict`. You will also have to create a `DiagonalGaussianDistribution()` from the returned value.'
        deprecate('tiled_encode', '1.0.0', deprecation_message, standard_warn=False)
        overlap_size = int(self.tile_sample_min_size * (1 - self.tile_overlap_factor))
        blend_extent = int(self.tile_latent_min_size * self.tile_overlap_factor)
        row_limit = self.tile_latent_min_size - blend_extent
        rows = []
        for i in range(0, x.shape[2], overlap_size):
            row = []
            for j in range(0, x.shape[3], overlap_size):
                tile = x[:, :, i:i + self.tile_sample_min_size, j:j + self.tile_sample_min_size]
                tile = self.encoder(tile)
                if self.config.use_quant_conv: tile = self.quant_conv(tile)
                row.append(tile)
            rows.append(row)
        result_rows = []
        for i, row in enumerate(rows):
            result_row = []
            for j, tile in enumerate(row):
                if i > 0: tile = self.blend_v(rows[i - 1][j], tile, blend_extent)
                if j > 0: tile = self.blend_h(row[j - 1], tile, blend_extent)
                result_row.append(tile[:, :, :row_limit, :row_limit])
            result_rows.append(torch.cat(result_row, dim=3))
        moments = torch.cat(result_rows, dim=2)
        posterior = DiagonalGaussianDistribution(moments)
        if not return_dict: return (posterior,)
        return AutoencoderKLOutput(latent_dist=posterior)
    def tiled_decode(self, z: torch.Tensor, return_dict: bool=True) -> Union[DecoderOutput, torch.Tensor]:
        """Returns:"""
        overlap_size = int(self.tile_latent_min_size * (1 - self.tile_overlap_factor))
        blend_extent = int(self.tile_sample_min_size * self.tile_overlap_factor)
        row_limit = self.tile_sample_min_size - blend_extent
        rows = []
        for i in range(0, z.shape[2], overlap_size):
            row = []
            for j in range(0, z.shape[3], overlap_size):
                tile = z[:, :, i:i + self.tile_latent_min_size, j:j + self.tile_latent_min_size]
                if self.config.use_post_quant_conv: tile = self.post_quant_conv(tile)
                decoded = self.decoder(tile)
                row.append(decoded)
            rows.append(row)
        result_rows = []
        for i, row in enumerate(rows):
            result_row = []
            for j, tile in enumerate(row):
                if i > 0: tile = self.blend_v(rows[i - 1][j], tile, blend_extent)
                if j > 0: tile = self.blend_h(row[j - 1], tile, blend_extent)
                result_row.append(tile[:, :, :row_limit, :row_limit])
            result_rows.append(torch.cat(result_row, dim=3))
        dec = torch.cat(result_rows, dim=2)
        if not return_dict: return (dec,)
        return DecoderOutput(sample=dec)
    def forward(self, sample: torch.Tensor, sample_posterior: bool=False, return_dict: bool=True, generator: Optional[torch.Generator]=None) -> Union[DecoderOutput, torch.Tensor]:
        """Args:"""
        x = sample
        posterior = self.encode(x).latent_dist
        if sample_posterior: z = posterior.sample(generator=generator)
        else: z = posterior.mode()
        dec = self.decode(z).sample
        if not return_dict: return (dec,)
        return DecoderOutput(sample=dec)
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
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
