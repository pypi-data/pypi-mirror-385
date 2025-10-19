'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from .activations import FP32SiLU, get_activation
from typing import List, Optional, Tuple, Union
from .attention_processor import Attention
import torch.nn.functional as F
from ..utils import deprecate
from torch import nn
import numpy as np
import torch
import math
def get_timestep_embedding(timesteps: torch.Tensor, embedding_dim: int, flip_sin_to_cos: bool=False, downscale_freq_shift: float=1, scale: float=1, max_period: int=10000):
    assert len(timesteps.shape) == 1, 'Timesteps should be a 1d-array'
    half_dim = embedding_dim // 2
    exponent = -math.log(max_period) * torch.arange(start=0, end=half_dim, dtype=torch.float32, device=timesteps.device)
    exponent = exponent / (half_dim - downscale_freq_shift)
    emb = torch.exp(exponent)
    emb = timesteps[:, None].float() * emb[None, :]
    emb = scale * emb
    emb = torch.cat([torch.sin(emb), torch.cos(emb)], dim=-1)
    if flip_sin_to_cos: emb = torch.cat([emb[:, half_dim:], emb[:, :half_dim]], dim=-1)
    if embedding_dim % 2 == 1: emb = torch.nn.functional.pad(emb, (0, 1, 0, 0))
    return emb
def get_3d_sincos_pos_embed(embed_dim: int, spatial_size: Union[int, Tuple[int, int]], temporal_size: int, spatial_interpolation_scale: float=1.0, temporal_interpolation_scale: float=1.0,
device: Optional[torch.device]=None, output_type: str='np') -> torch.Tensor:
    """Returns:"""
    if output_type == 'np': return _get_3d_sincos_pos_embed_np(embed_dim=embed_dim, spatial_size=spatial_size, temporal_size=temporal_size, spatial_interpolation_scale=spatial_interpolation_scale,
    temporal_interpolation_scale=temporal_interpolation_scale)
    if embed_dim % 4 != 0: raise ValueError('`embed_dim` must be divisible by 4')
    if isinstance(spatial_size, int): spatial_size = (spatial_size, spatial_size)
    embed_dim_spatial = 3 * embed_dim // 4
    embed_dim_temporal = embed_dim // 4
    grid_h = torch.arange(spatial_size[1], device=device, dtype=torch.float32) / spatial_interpolation_scale
    grid_w = torch.arange(spatial_size[0], device=device, dtype=torch.float32) / spatial_interpolation_scale
    grid = torch.meshgrid(grid_w, grid_h, indexing='xy')
    grid = torch.stack(grid, dim=0)
    grid = grid.reshape([2, 1, spatial_size[1], spatial_size[0]])
    pos_embed_spatial = get_2d_sincos_pos_embed_from_grid(embed_dim_spatial, grid, output_type='pt')
    grid_t = torch.arange(temporal_size, device=device, dtype=torch.float32) / temporal_interpolation_scale
    pos_embed_temporal = get_1d_sincos_pos_embed_from_grid(embed_dim_temporal, grid_t, output_type='pt')
    pos_embed_spatial = pos_embed_spatial[None, :, :]
    pos_embed_spatial = pos_embed_spatial.repeat_interleave(temporal_size, dim=0)
    pos_embed_temporal = pos_embed_temporal[:, None, :]
    pos_embed_temporal = pos_embed_temporal.repeat_interleave(spatial_size[0] * spatial_size[1], dim=1)
    pos_embed = torch.concat([pos_embed_temporal, pos_embed_spatial], dim=-1)
    return pos_embed
def _get_3d_sincos_pos_embed_np(embed_dim: int, spatial_size: Union[int, Tuple[int, int]], temporal_size: int, spatial_interpolation_scale: float=1.0, temporal_interpolation_scale: float=1.0) -> np.ndarray:
    """Returns:"""
    deprecation_message = "`get_3d_sincos_pos_embed` uses `torch` and supports `device`. `from_numpy` is no longer required.  Pass `output_type='pt' to use the new version now."
    deprecate("output_type=='np'", '0.33.0', deprecation_message, standard_warn=False)
    if embed_dim % 4 != 0: raise ValueError('`embed_dim` must be divisible by 4')
    if isinstance(spatial_size, int): spatial_size = (spatial_size, spatial_size)
    embed_dim_spatial = 3 * embed_dim // 4
    embed_dim_temporal = embed_dim // 4
    grid_h = np.arange(spatial_size[1], dtype=np.float32) / spatial_interpolation_scale
    grid_w = np.arange(spatial_size[0], dtype=np.float32) / spatial_interpolation_scale
    grid = np.meshgrid(grid_w, grid_h)
    grid = np.stack(grid, axis=0)
    grid = grid.reshape([2, 1, spatial_size[1], spatial_size[0]])
    pos_embed_spatial = get_2d_sincos_pos_embed_from_grid(embed_dim_spatial, grid)
    grid_t = np.arange(temporal_size, dtype=np.float32) / temporal_interpolation_scale
    pos_embed_temporal = get_1d_sincos_pos_embed_from_grid(embed_dim_temporal, grid_t)
    pos_embed_spatial = pos_embed_spatial[np.newaxis, :, :]
    pos_embed_spatial = np.repeat(pos_embed_spatial, temporal_size, axis=0)
    pos_embed_temporal = pos_embed_temporal[:, np.newaxis, :]
    pos_embed_temporal = np.repeat(pos_embed_temporal, spatial_size[0] * spatial_size[1], axis=1)
    pos_embed = np.concatenate([pos_embed_temporal, pos_embed_spatial], axis=-1)
    return pos_embed
def get_2d_sincos_pos_embed(embed_dim, grid_size, cls_token=False, extra_tokens=0, interpolation_scale=1.0, base_size=16, device: Optional[torch.device]=None, output_type: str='np'):
    """Returns:"""
    if output_type == 'np':
        deprecation_message = "`get_2d_sincos_pos_embed` uses `torch` and supports `device`. `from_numpy` is no longer required.  Pass `output_type='pt' to use the new version now."
        deprecate("output_type=='np'", '0.33.0', deprecation_message, standard_warn=False)
        return get_2d_sincos_pos_embed_np(embed_dim=embed_dim, grid_size=grid_size, cls_token=cls_token, extra_tokens=extra_tokens, interpolation_scale=interpolation_scale, base_size=base_size)
    if isinstance(grid_size, int): grid_size = (grid_size, grid_size)
    grid_h = torch.arange(grid_size[0], device=device, dtype=torch.float32) / (grid_size[0] / base_size) / interpolation_scale
    grid_w = torch.arange(grid_size[1], device=device, dtype=torch.float32) / (grid_size[1] / base_size) / interpolation_scale
    grid = torch.meshgrid(grid_w, grid_h, indexing='xy')
    grid = torch.stack(grid, dim=0)
    grid = grid.reshape([2, 1, grid_size[1], grid_size[0]])
    pos_embed = get_2d_sincos_pos_embed_from_grid(embed_dim, grid, output_type=output_type)
    if cls_token and extra_tokens > 0: pos_embed = torch.concat([torch.zeros([extra_tokens, embed_dim]), pos_embed], dim=0)
    return pos_embed
def get_2d_sincos_pos_embed_from_grid(embed_dim, grid, output_type='np'):
    """Returns:"""
    if output_type == 'np':
        deprecation_message = "`get_2d_sincos_pos_embed_from_grid` uses `torch` and supports `device`. `from_numpy` is no longer required.  Pass `output_type='pt' to use the new version now."
        deprecate("output_type=='np'", '0.33.0', deprecation_message, standard_warn=False)
        return get_2d_sincos_pos_embed_from_grid_np(embed_dim=embed_dim, grid=grid)
    if embed_dim % 2 != 0: raise ValueError('embed_dim must be divisible by 2')
    emb_h = get_1d_sincos_pos_embed_from_grid(embed_dim // 2, grid[0], output_type=output_type)
    emb_w = get_1d_sincos_pos_embed_from_grid(embed_dim // 2, grid[1], output_type=output_type)
    emb = torch.concat([emb_h, emb_w], dim=1)
    return emb
def get_1d_sincos_pos_embed_from_grid(embed_dim, pos, output_type='np'):
    """Returns:"""
    if output_type == 'np':
        deprecation_message = "`get_1d_sincos_pos_embed_from_grid` uses `torch` and supports `device`. `from_numpy` is no longer required.  Pass `output_type='pt' to use the new version now."
        deprecate("output_type=='np'", '0.33.0', deprecation_message, standard_warn=False)
        return get_1d_sincos_pos_embed_from_grid_np(embed_dim=embed_dim, pos=pos)
    if embed_dim % 2 != 0: raise ValueError('embed_dim must be divisible by 2')
    omega = torch.arange(embed_dim // 2, device=pos.device, dtype=torch.float64)
    omega /= embed_dim / 2.0
    omega = 1.0 / 10000 ** omega
    pos = pos.reshape(-1)
    out = torch.outer(pos, omega)
    emb_sin = torch.sin(out)
    emb_cos = torch.cos(out)
    emb = torch.concat([emb_sin, emb_cos], dim=1)
    return emb
def get_2d_sincos_pos_embed_np(embed_dim, grid_size, cls_token=False, extra_tokens=0, interpolation_scale=1.0, base_size=16):
    """Returns:"""
    if isinstance(grid_size, int): grid_size = (grid_size, grid_size)
    grid_h = np.arange(grid_size[0], dtype=np.float32) / (grid_size[0] / base_size) / interpolation_scale
    grid_w = np.arange(grid_size[1], dtype=np.float32) / (grid_size[1] / base_size) / interpolation_scale
    grid = np.meshgrid(grid_w, grid_h)
    grid = np.stack(grid, axis=0)
    grid = grid.reshape([2, 1, grid_size[1], grid_size[0]])
    pos_embed = get_2d_sincos_pos_embed_from_grid_np(embed_dim, grid)
    if cls_token and extra_tokens > 0: pos_embed = np.concatenate([np.zeros([extra_tokens, embed_dim]), pos_embed], axis=0)
    return pos_embed
def get_2d_sincos_pos_embed_from_grid_np(embed_dim, grid):
    """Returns:"""
    if embed_dim % 2 != 0: raise ValueError('embed_dim must be divisible by 2')
    emb_h = get_1d_sincos_pos_embed_from_grid_np(embed_dim // 2, grid[0])
    emb_w = get_1d_sincos_pos_embed_from_grid_np(embed_dim // 2, grid[1])
    emb = np.concatenate([emb_h, emb_w], axis=1)
    return emb
def get_1d_sincos_pos_embed_from_grid_np(embed_dim, pos):
    """Returns:"""
    if embed_dim % 2 != 0: raise ValueError('embed_dim must be divisible by 2')
    omega = np.arange(embed_dim // 2, dtype=np.float64)
    omega /= embed_dim / 2.0
    omega = 1.0 / 10000 ** omega
    pos = pos.reshape(-1)
    out = np.einsum('m,d->md', pos, omega)
    emb_sin = np.sin(out)
    emb_cos = np.cos(out)
    emb = np.concatenate([emb_sin, emb_cos], axis=1)
    return emb
class PatchEmbed(nn.Module):
    """Args:"""
    def __init__(self, height=224, width=224, patch_size=16, in_channels=3, embed_dim=768, layer_norm=False, flatten=True, bias=True, interpolation_scale=1, pos_embed_type='sincos', pos_embed_max_size=None):
        super().__init__()
        num_patches = height // patch_size * (width // patch_size)
        self.flatten = flatten
        self.layer_norm = layer_norm
        self.pos_embed_max_size = pos_embed_max_size
        self.proj = nn.Conv2d(in_channels, embed_dim, kernel_size=(patch_size, patch_size), stride=patch_size, bias=bias)
        if layer_norm: self.norm = nn.LayerNorm(embed_dim, elementwise_affine=False, eps=1e-06)
        else: self.norm = None
        self.patch_size = patch_size
        self.height, self.width = (height // patch_size, width // patch_size)
        self.base_size = height // patch_size
        self.interpolation_scale = interpolation_scale
        if pos_embed_max_size: grid_size = pos_embed_max_size
        else: grid_size = int(num_patches ** 0.5)
        if pos_embed_type is None: self.pos_embed = None
        elif pos_embed_type == 'sincos':
            pos_embed = get_2d_sincos_pos_embed(embed_dim, grid_size, base_size=self.base_size, interpolation_scale=self.interpolation_scale, output_type='pt')
            persistent = True if pos_embed_max_size else False
            self.register_buffer('pos_embed', pos_embed.float().unsqueeze(0), persistent=persistent)
        else: raise ValueError(f'Unsupported pos_embed_type: {pos_embed_type}')
    def cropped_pos_embed(self, height, width):
        if self.pos_embed_max_size is None: raise ValueError('`pos_embed_max_size` must be set for cropping.')
        height = height // self.patch_size
        width = width // self.patch_size
        if height > self.pos_embed_max_size: raise ValueError(f'Height ({height}) cannot be greater than `pos_embed_max_size`: {self.pos_embed_max_size}.')
        if width > self.pos_embed_max_size: raise ValueError(f'Width ({width}) cannot be greater than `pos_embed_max_size`: {self.pos_embed_max_size}.')
        top = (self.pos_embed_max_size - height) // 2
        left = (self.pos_embed_max_size - width) // 2
        spatial_pos_embed = self.pos_embed.reshape(1, self.pos_embed_max_size, self.pos_embed_max_size, -1)
        spatial_pos_embed = spatial_pos_embed[:, top:top + height, left:left + width, :]
        spatial_pos_embed = spatial_pos_embed.reshape(1, -1, spatial_pos_embed.shape[-1])
        return spatial_pos_embed
    def forward(self, latent):
        if self.pos_embed_max_size is not None: height, width = latent.shape[-2:]
        else: height, width = (latent.shape[-2] // self.patch_size, latent.shape[-1] // self.patch_size)
        latent = self.proj(latent)
        if self.flatten: latent = latent.flatten(2).transpose(1, 2)
        if self.layer_norm: latent = self.norm(latent)
        if self.pos_embed is None: return latent.to(latent.dtype)
        if self.pos_embed_max_size: pos_embed = self.cropped_pos_embed(height, width)
        elif self.height != height or self.width != width:
            pos_embed = get_2d_sincos_pos_embed(embed_dim=self.pos_embed.shape[-1], grid_size=(height, width), base_size=self.base_size, interpolation_scale=self.interpolation_scale, device=latent.device, output_type='pt')
            pos_embed = pos_embed.float().unsqueeze(0)
        else: pos_embed = self.pos_embed
        return (latent + pos_embed).to(latent.dtype)
class LuminaPatchEmbed(nn.Module):
    """Args:"""
    def __init__(self, patch_size=2, in_channels=4, embed_dim=768, bias=True):
        super().__init__()
        self.patch_size = patch_size
        self.proj = nn.Linear(in_features=patch_size * patch_size * in_channels, out_features=embed_dim, bias=bias)
    def forward(self, x, freqs_cis):
        """Returns:"""
        freqs_cis = freqs_cis.to(x[0].device)
        patch_height = patch_width = self.patch_size
        batch_size, channel, height, width = x.size()
        height_tokens, width_tokens = (height // patch_height, width // patch_width)
        x = x.view(batch_size, channel, height_tokens, patch_height, width_tokens, patch_width).permute(0, 2, 4, 1, 3, 5)
        x = x.flatten(3)
        x = self.proj(x)
        x = x.flatten(1, 2)
        mask = torch.ones(x.shape[0], x.shape[1], dtype=torch.int32, device=x.device)
        return (x, mask, [(height, width)] * batch_size, freqs_cis[:height_tokens, :width_tokens].flatten(0, 1).unsqueeze(0))
class CogVideoXPatchEmbed(nn.Module):
    def __init__(self, patch_size: int=2, patch_size_t: Optional[int]=None, in_channels: int=16, embed_dim: int=1920, text_embed_dim: int=4096, bias: bool=True, sample_width: int=90, sample_height: int=60,
    sample_frames: int=49, temporal_compression_ratio: int=4, max_text_seq_length: int=226, spatial_interpolation_scale: float=1.875, temporal_interpolation_scale: float=1.0, use_positional_embeddings: bool=True,
    use_learned_positional_embeddings: bool=True) -> None:
        super().__init__()
        self.patch_size = patch_size
        self.patch_size_t = patch_size_t
        self.embed_dim = embed_dim
        self.sample_height = sample_height
        self.sample_width = sample_width
        self.sample_frames = sample_frames
        self.temporal_compression_ratio = temporal_compression_ratio
        self.max_text_seq_length = max_text_seq_length
        self.spatial_interpolation_scale = spatial_interpolation_scale
        self.temporal_interpolation_scale = temporal_interpolation_scale
        self.use_positional_embeddings = use_positional_embeddings
        self.use_learned_positional_embeddings = use_learned_positional_embeddings
        if patch_size_t is None: self.proj = nn.Conv2d(in_channels, embed_dim, kernel_size=(patch_size, patch_size), stride=patch_size, bias=bias)
        else: self.proj = nn.Linear(in_channels * patch_size * patch_size * patch_size_t, embed_dim)
        self.text_proj = nn.Linear(text_embed_dim, embed_dim)
        if use_positional_embeddings or use_learned_positional_embeddings:
            persistent = use_learned_positional_embeddings
            pos_embedding = self._get_positional_embeddings(sample_height, sample_width, sample_frames)
            self.register_buffer('pos_embedding', pos_embedding, persistent=persistent)
    def _get_positional_embeddings(self, sample_height: int, sample_width: int, sample_frames: int, device: Optional[torch.device]=None) -> torch.Tensor:
        post_patch_height = sample_height // self.patch_size
        post_patch_width = sample_width // self.patch_size
        post_time_compression_frames = (sample_frames - 1) // self.temporal_compression_ratio + 1
        num_patches = post_patch_height * post_patch_width * post_time_compression_frames
        pos_embedding = get_3d_sincos_pos_embed(self.embed_dim, (post_patch_width, post_patch_height), post_time_compression_frames, self.spatial_interpolation_scale,
        self.temporal_interpolation_scale, device=device, output_type='pt')
        pos_embedding = pos_embedding.flatten(0, 1)
        joint_pos_embedding = pos_embedding.new_zeros(1, self.max_text_seq_length + num_patches, self.embed_dim, requires_grad=False)
        joint_pos_embedding.data[:, self.max_text_seq_length:].copy_(pos_embedding)
        return joint_pos_embedding
    def forward(self, text_embeds: torch.Tensor, image_embeds: torch.Tensor):
        """Args:"""
        text_embeds = self.text_proj(text_embeds)
        batch_size, num_frames, channels, height, width = image_embeds.shape
        if self.patch_size_t is None:
            image_embeds = image_embeds.reshape(-1, channels, height, width)
            image_embeds = self.proj(image_embeds)
            image_embeds = image_embeds.view(batch_size, num_frames, *image_embeds.shape[1:])
            image_embeds = image_embeds.flatten(3).transpose(2, 3)
            image_embeds = image_embeds.flatten(1, 2)
        else:
            p = self.patch_size
            p_t = self.patch_size_t
            image_embeds = image_embeds.permute(0, 1, 3, 4, 2)
            image_embeds = image_embeds.reshape(batch_size, num_frames // p_t, p_t, height // p, p, width // p, p, channels)
            image_embeds = image_embeds.permute(0, 1, 3, 5, 7, 2, 4, 6).flatten(4, 7).flatten(1, 3)
            image_embeds = self.proj(image_embeds)
        embeds = torch.cat([text_embeds, image_embeds], dim=1).contiguous()
        if self.use_positional_embeddings or self.use_learned_positional_embeddings:
            if self.use_learned_positional_embeddings and (self.sample_width != width or self.sample_height != height): raise ValueError("It is currently not possible to generate videos at a different resolution that the defaults. This should only be the case with 'THUDM/CogVideoX-5b-I2V'.If you think this is incorrect, please open an issue at https://github.com/huggingface/diffusers/issues.")
            pre_time_compression_frames = (num_frames - 1) * self.temporal_compression_ratio + 1
            if self.sample_height != height or self.sample_width != width or self.sample_frames != pre_time_compression_frames: pos_embedding = self._get_positional_embeddings(height, width, pre_time_compression_frames, device=embeds.device)
            else: pos_embedding = self.pos_embedding
            pos_embedding = pos_embedding.to(dtype=embeds.dtype)
            embeds = embeds + pos_embedding
        return embeds
class CogView3PlusPatchEmbed(nn.Module):
    def __init__(self, in_channels: int=16, hidden_size: int=2560, patch_size: int=2, text_hidden_size: int=4096, pos_embed_max_size: int=128):
        super().__init__()
        self.in_channels = in_channels
        self.hidden_size = hidden_size
        self.patch_size = patch_size
        self.text_hidden_size = text_hidden_size
        self.pos_embed_max_size = pos_embed_max_size
        self.proj = nn.Linear(in_channels * patch_size ** 2, hidden_size)
        self.text_proj = nn.Linear(text_hidden_size, hidden_size)
        pos_embed = get_2d_sincos_pos_embed(hidden_size, pos_embed_max_size, base_size=pos_embed_max_size, output_type='pt')
        pos_embed = pos_embed.reshape(pos_embed_max_size, pos_embed_max_size, hidden_size)
        self.register_buffer('pos_embed', pos_embed.float(), persistent=False)
    def forward(self, hidden_states: torch.Tensor, encoder_hidden_states: torch.Tensor) -> torch.Tensor:
        batch_size, channel, height, width = hidden_states.shape
        if height % self.patch_size != 0 or width % self.patch_size != 0: raise ValueError('Height and width must be divisible by patch size')
        height = height // self.patch_size
        width = width // self.patch_size
        hidden_states = hidden_states.view(batch_size, channel, height, self.patch_size, width, self.patch_size)
        hidden_states = hidden_states.permute(0, 2, 4, 1, 3, 5).contiguous()
        hidden_states = hidden_states.view(batch_size, height * width, channel * self.patch_size * self.patch_size)
        hidden_states = self.proj(hidden_states)
        encoder_hidden_states = self.text_proj(encoder_hidden_states)
        hidden_states = torch.cat([encoder_hidden_states, hidden_states], dim=1)
        text_length = encoder_hidden_states.shape[1]
        image_pos_embed = self.pos_embed[:height, :width].reshape(height * width, -1)
        text_pos_embed = torch.zeros((text_length, self.hidden_size), dtype=image_pos_embed.dtype, device=image_pos_embed.device)
        pos_embed = torch.cat([text_pos_embed, image_pos_embed], dim=0)[None, ...]
        return (hidden_states + pos_embed).to(hidden_states.dtype)
def get_3d_rotary_pos_embed(embed_dim, crops_coords, grid_size, temporal_size, theta: int=10000, use_real: bool=True, grid_type: str='linspace', max_size: Optional[Tuple[int, int]]=None,
device: Optional[torch.device]=None) -> Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
    """Returns:"""
    if use_real is not True: raise ValueError(' `use_real = False` is not currently supported for get_3d_rotary_pos_embed')
    if grid_type == 'linspace':
        start, stop = crops_coords
        grid_size_h, grid_size_w = grid_size
        grid_h = torch.linspace(start[0], stop[0] * (grid_size_h - 1) / grid_size_h, grid_size_h, device=device, dtype=torch.float32)
        grid_w = torch.linspace(start[1], stop[1] * (grid_size_w - 1) / grid_size_w, grid_size_w, device=device, dtype=torch.float32)
        grid_t = torch.arange(temporal_size, device=device, dtype=torch.float32)
        grid_t = torch.linspace(0, temporal_size * (temporal_size - 1) / temporal_size, temporal_size, device=device, dtype=torch.float32)
    elif grid_type == 'slice':
        max_h, max_w = max_size
        grid_size_h, grid_size_w = grid_size
        grid_h = torch.arange(max_h, device=device, dtype=torch.float32)
        grid_w = torch.arange(max_w, device=device, dtype=torch.float32)
        grid_t = torch.arange(temporal_size, device=device, dtype=torch.float32)
    else: raise ValueError('Invalid value passed for `grid_type`.')
    dim_t = embed_dim // 4
    dim_h = embed_dim // 8 * 3
    dim_w = embed_dim // 8 * 3
    freqs_t = get_1d_rotary_pos_embed(dim_t, grid_t, theta=theta, use_real=True)
    freqs_h = get_1d_rotary_pos_embed(dim_h, grid_h, theta=theta, use_real=True)
    freqs_w = get_1d_rotary_pos_embed(dim_w, grid_w, theta=theta, use_real=True)
    def combine_time_height_width(freqs_t, freqs_h, freqs_w):
        freqs_t = freqs_t[:, None, None, :].expand(-1, grid_size_h, grid_size_w, -1)
        freqs_h = freqs_h[None, :, None, :].expand(temporal_size, -1, grid_size_w, -1)
        freqs_w = freqs_w[None, None, :, :].expand(temporal_size, grid_size_h, -1, -1)
        freqs = torch.cat([freqs_t, freqs_h, freqs_w], dim=-1)
        freqs = freqs.view(temporal_size * grid_size_h * grid_size_w, -1)
        return freqs
    t_cos, t_sin = freqs_t
    h_cos, h_sin = freqs_h
    w_cos, w_sin = freqs_w
    if grid_type == 'slice':
        t_cos, t_sin = (t_cos[:temporal_size], t_sin[:temporal_size])
        h_cos, h_sin = (h_cos[:grid_size_h], h_sin[:grid_size_h])
        w_cos, w_sin = (w_cos[:grid_size_w], w_sin[:grid_size_w])
    cos = combine_time_height_width(t_cos, h_cos, w_cos)
    sin = combine_time_height_width(t_sin, h_sin, w_sin)
    return (cos, sin)
def get_3d_rotary_pos_embed_allegro(embed_dim, crops_coords, grid_size, temporal_size, interpolation_scale: Tuple[float, float, float]=(1.0, 1.0, 1.0), theta: int=10000,
device: Optional[torch.device]=None) -> Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
    start, stop = crops_coords
    grid_size_h, grid_size_w = grid_size
    interpolation_scale_t, interpolation_scale_h, interpolation_scale_w = interpolation_scale
    grid_t = torch.linspace(0, temporal_size * (temporal_size - 1) / temporal_size, temporal_size, device=device, dtype=torch.float32)
    grid_h = torch.linspace(start[0], stop[0] * (grid_size_h - 1) / grid_size_h, grid_size_h, device=device, dtype=torch.float32)
    grid_w = torch.linspace(start[1], stop[1] * (grid_size_w - 1) / grid_size_w, grid_size_w, device=device, dtype=torch.float32)
    dim_t = embed_dim // 3
    dim_h = embed_dim // 3
    dim_w = embed_dim // 3
    freqs_t = get_1d_rotary_pos_embed(dim_t, grid_t / interpolation_scale_t, theta=theta, use_real=True, repeat_interleave_real=False)
    freqs_h = get_1d_rotary_pos_embed(dim_h, grid_h / interpolation_scale_h, theta=theta, use_real=True, repeat_interleave_real=False)
    freqs_w = get_1d_rotary_pos_embed(dim_w, grid_w / interpolation_scale_w, theta=theta, use_real=True, repeat_interleave_real=False)
    return (freqs_t, freqs_h, freqs_w, grid_t, grid_h, grid_w)
def get_2d_rotary_pos_embed(embed_dim, crops_coords, grid_size, use_real=True, device: Optional[torch.device]=None, output_type: str='np'):
    """Returns:"""
    if output_type == 'np':
        deprecation_message = "`get_2d_sincos_pos_embed` uses `torch` and supports `device`. `from_numpy` is no longer required.  Pass `output_type='pt' to use the new version now."
        deprecate("output_type=='np'", '0.33.0', deprecation_message, standard_warn=False)
        return _get_2d_rotary_pos_embed_np(embed_dim=embed_dim, crops_coords=crops_coords, grid_size=grid_size, use_real=use_real)
    start, stop = crops_coords
    grid_h = torch.linspace(start[0], stop[0] * (grid_size[0] - 1) / grid_size[0], grid_size[0], device=device, dtype=torch.float32)
    grid_w = torch.linspace(start[1], stop[1] * (grid_size[1] - 1) / grid_size[1], grid_size[1], device=device, dtype=torch.float32)
    grid = torch.meshgrid(grid_w, grid_h, indexing='xy')
    grid = torch.stack(grid, dim=0)
    grid = grid.reshape([2, 1, *grid.shape[1:]])
    pos_embed = get_2d_rotary_pos_embed_from_grid(embed_dim, grid, use_real=use_real)
    return pos_embed
def _get_2d_rotary_pos_embed_np(embed_dim, crops_coords, grid_size, use_real=True):
    """Returns:"""
    start, stop = crops_coords
    grid_h = np.linspace(start[0], stop[0], grid_size[0], endpoint=False, dtype=np.float32)
    grid_w = np.linspace(start[1], stop[1], grid_size[1], endpoint=False, dtype=np.float32)
    grid = np.meshgrid(grid_w, grid_h)
    grid = np.stack(grid, axis=0)
    grid = grid.reshape([2, 1, *grid.shape[1:]])
    pos_embed = get_2d_rotary_pos_embed_from_grid(embed_dim, grid, use_real=use_real)
    return pos_embed
def get_2d_rotary_pos_embed_from_grid(embed_dim, grid, use_real=False):
    """Returns:"""
    assert embed_dim % 4 == 0
    emb_h = get_1d_rotary_pos_embed(embed_dim // 2, grid[0].reshape(-1), use_real=use_real)
    emb_w = get_1d_rotary_pos_embed(embed_dim // 2, grid[1].reshape(-1), use_real=use_real)
    if use_real:
        cos = torch.cat([emb_h[0], emb_w[0]], dim=1)
        sin = torch.cat([emb_h[1], emb_w[1]], dim=1)
        return (cos, sin)
    else:
        emb = torch.cat([emb_h, emb_w], dim=1)
        return emb
def get_2d_rotary_pos_embed_lumina(embed_dim, len_h, len_w, linear_factor=1.0, ntk_factor=1.0):
    """Returns:"""
    assert embed_dim % 4 == 0
    emb_h = get_1d_rotary_pos_embed(embed_dim // 2, len_h, linear_factor=linear_factor, ntk_factor=ntk_factor)
    emb_w = get_1d_rotary_pos_embed(embed_dim // 2, len_w, linear_factor=linear_factor, ntk_factor=ntk_factor)
    emb_h = emb_h.view(len_h, 1, embed_dim // 4, 1).repeat(1, len_w, 1, 1)
    emb_w = emb_w.view(1, len_w, embed_dim // 4, 1).repeat(len_h, 1, 1, 1)
    emb = torch.cat([emb_h, emb_w], dim=-1).flatten(2)
    return emb
def get_1d_rotary_pos_embed(dim: int, pos: Union[np.ndarray, int], theta: float=10000.0, use_real=False, linear_factor=1.0, ntk_factor=1.0, repeat_interleave_real=True, freqs_dtype=torch.float32):
    """Returns:"""
    assert dim % 2 == 0
    if isinstance(pos, int): pos = torch.arange(pos)
    if isinstance(pos, np.ndarray): pos = torch.from_numpy(pos)
    theta = theta * ntk_factor
    freqs = 1.0 / theta ** (torch.arange(0, dim, 2, dtype=freqs_dtype, device=pos.device)[:dim // 2] / dim) / linear_factor
    freqs = torch.outer(pos, freqs)
    if use_real and repeat_interleave_real:
        freqs_cos = freqs.cos().repeat_interleave(2, dim=1).float()
        freqs_sin = freqs.sin().repeat_interleave(2, dim=1).float()
        return (freqs_cos, freqs_sin)
    elif use_real:
        freqs_cos = torch.cat([freqs.cos(), freqs.cos()], dim=-1).float()
        freqs_sin = torch.cat([freqs.sin(), freqs.sin()], dim=-1).float()
        return (freqs_cos, freqs_sin)
    else:
        freqs_cis = torch.polar(torch.ones_like(freqs), freqs)
        return freqs_cis
def apply_rotary_emb(x: torch.Tensor, freqs_cis: Union[torch.Tensor, Tuple[torch.Tensor]], use_real: bool=True, use_real_unbind_dim: int=-1) -> Tuple[torch.Tensor, torch.Tensor]:
    """Returns:"""
    if use_real:
        cos, sin = freqs_cis
        cos = cos[None, None]
        sin = sin[None, None]
        cos, sin = (cos.to(x.device), sin.to(x.device))
        if use_real_unbind_dim == -1:
            x_real, x_imag = x.reshape(*x.shape[:-1], -1, 2).unbind(-1)
            x_rotated = torch.stack([-x_imag, x_real], dim=-1).flatten(3)
        elif use_real_unbind_dim == -2:
            x_real, x_imag = x.reshape(*x.shape[:-1], 2, -1).unbind(-2)
            x_rotated = torch.cat([-x_imag, x_real], dim=-1)
        else: raise ValueError(f'`use_real_unbind_dim={use_real_unbind_dim}` but should be -1 or -2.')
        out = (x.float() * cos + x_rotated.float() * sin).to(x.dtype)
        return out
    else:
        x_rotated = torch.view_as_complex(x.float().reshape(*x.shape[:-1], -1, 2))
        freqs_cis = freqs_cis.unsqueeze(2)
        x_out = torch.view_as_real(x_rotated * freqs_cis).flatten(3)
        return x_out.type_as(x)
def apply_rotary_emb_allegro(x: torch.Tensor, freqs_cis, positions):
    def apply_1d_rope(tokens, pos, cos, sin):
        cos = F.embedding(pos, cos)[:, None, :, :]
        sin = F.embedding(pos, sin)[:, None, :, :]
        x1, x2 = (tokens[..., :tokens.shape[-1] // 2], tokens[..., tokens.shape[-1] // 2:])
        tokens_rotated = torch.cat((-x2, x1), dim=-1)
        return (tokens.float() * cos + tokens_rotated.float() * sin).to(tokens.dtype)
    (t_cos, t_sin), (h_cos, h_sin), (w_cos, w_sin) = freqs_cis
    t, h, w = x.chunk(3, dim=-1)
    t = apply_1d_rope(t, positions[0], t_cos, t_sin)
    h = apply_1d_rope(h, positions[1], h_cos, h_sin)
    w = apply_1d_rope(w, positions[2], w_cos, w_sin)
    x = torch.cat([t, h, w], dim=-1)
    return x
class FluxPosEmbed(nn.Module):
    def __init__(self, theta: int, axes_dim: List[int]):
        super().__init__()
        self.theta = theta
        self.axes_dim = axes_dim
    def forward(self, ids: torch.Tensor) -> torch.Tensor:
        n_axes = ids.shape[-1]
        cos_out = []
        sin_out = []
        pos = ids.float()
        is_mps = ids.device.type == 'mps'
        freqs_dtype = torch.float32 if is_mps else torch.float64
        for i in range(n_axes):
            cos, sin = get_1d_rotary_pos_embed(self.axes_dim[i], pos[:, i], theta=self.theta, repeat_interleave_real=True, use_real=True, freqs_dtype=freqs_dtype)
            cos_out.append(cos)
            sin_out.append(sin)
        freqs_cos = torch.cat(cos_out, dim=-1).to(ids.device)
        freqs_sin = torch.cat(sin_out, dim=-1).to(ids.device)
        return (freqs_cos, freqs_sin)
class TimestepEmbedding(nn.Module):
    def __init__(self, in_channels: int, time_embed_dim: int, act_fn: str='silu', out_dim: int=None, post_act_fn: Optional[str]=None, cond_proj_dim=None, sample_proj_bias=True):
        super().__init__()
        self.linear_1 = nn.Linear(in_channels, time_embed_dim, sample_proj_bias)
        if cond_proj_dim is not None: self.cond_proj = nn.Linear(cond_proj_dim, in_channels, bias=False)
        else: self.cond_proj = None
        self.act = get_activation(act_fn)
        if out_dim is not None: time_embed_dim_out = out_dim
        else: time_embed_dim_out = time_embed_dim
        self.linear_2 = nn.Linear(time_embed_dim, time_embed_dim_out, sample_proj_bias)
        if post_act_fn is None: self.post_act = None
        else: self.post_act = get_activation(post_act_fn)
    def forward(self, sample, condition=None):
        if condition is not None: sample = sample + self.cond_proj(condition)
        sample = self.linear_1(sample)
        if self.act is not None: sample = self.act(sample)
        sample = self.linear_2(sample)
        if self.post_act is not None: sample = self.post_act(sample)
        return sample
class Timesteps(nn.Module):
    def __init__(self, num_channels: int, flip_sin_to_cos: bool, downscale_freq_shift: float, scale: int=1):
        super().__init__()
        self.num_channels = num_channels
        self.flip_sin_to_cos = flip_sin_to_cos
        self.downscale_freq_shift = downscale_freq_shift
        self.scale = scale
    def forward(self, timesteps):
        t_emb = get_timestep_embedding(timesteps, self.num_channels, flip_sin_to_cos=self.flip_sin_to_cos, downscale_freq_shift=self.downscale_freq_shift, scale=self.scale)
        return t_emb
class SAPIPhotoGenPosEmbed(nn.Module):
    def __init__(self, theta: int, axes_dim: List[int]):
        super().__init__()
        self.theta = theta
        self.axes_dim = axes_dim
    def forward(self, ids: torch.Tensor) -> torch.Tensor:
        n_axes = ids.shape[-1]
        cos_out = []
        sin_out = []
        pos = ids.float()
        is_mps = ids.device.type == 'mps'
        freqs_dtype = torch.float32 if is_mps else torch.float64
        for i in range(n_axes):
            cos, sin = get_1d_rotary_pos_embed(self.axes_dim[i], pos[:, i], theta=self.theta, repeat_interleave_real=True, use_real=True, freqs_dtype=freqs_dtype)
            cos_out.append(cos)
            sin_out.append(sin)
        freqs_cos = torch.cat(cos_out, dim=-1).to(ids.device)
        freqs_sin = torch.cat(sin_out, dim=-1).to(ids.device)
        return (freqs_cos, freqs_sin)
class GaussianFourierProjection(nn.Module):
    def __init__(self, embedding_size: int=256, scale: float=1.0, set_W_to_weight=True, log=True, flip_sin_to_cos=False):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(embedding_size) * scale, requires_grad=False)
        self.log = log
        self.flip_sin_to_cos = flip_sin_to_cos
        if set_W_to_weight:
            del self.weight
            self.W = nn.Parameter(torch.randn(embedding_size) * scale, requires_grad=False)
            self.weight = self.W
            del self.W
    def forward(self, x):
        if self.log: x = torch.log(x)
        x_proj = x[:, None] * self.weight[None, :] * 2 * np.pi
        if self.flip_sin_to_cos: out = torch.cat([torch.cos(x_proj), torch.sin(x_proj)], dim=-1)
        else: out = torch.cat([torch.sin(x_proj), torch.cos(x_proj)], dim=-1)
        return out
class SinusoidalPositionalEmbedding(nn.Module):
    """Args:"""
    def __init__(self, embed_dim: int, max_seq_length: int=32):
        super().__init__()
        position = torch.arange(max_seq_length).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, embed_dim, 2) * (-math.log(10000.0) / embed_dim))
        pe = torch.zeros(1, max_seq_length, embed_dim)
        pe[0, :, 0::2] = torch.sin(position * div_term)
        pe[0, :, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)
    def forward(self, x):
        _, seq_length, _ = x.shape
        x = x + self.pe[:, :seq_length]
        return x
class ImagePositionalEmbeddings(nn.Module):
    """Args:"""
    def __init__(self, num_embed: int, height: int, width: int, embed_dim: int):
        super().__init__()
        self.height = height
        self.width = width
        self.num_embed = num_embed
        self.embed_dim = embed_dim
        self.emb = nn.Embedding(self.num_embed, embed_dim)
        self.height_emb = nn.Embedding(self.height, embed_dim)
        self.width_emb = nn.Embedding(self.width, embed_dim)
    def forward(self, index):
        emb = self.emb(index)
        height_emb = self.height_emb(torch.arange(self.height, device=index.device).view(1, self.height))
        height_emb = height_emb.unsqueeze(2)
        width_emb = self.width_emb(torch.arange(self.width, device=index.device).view(1, self.width))
        width_emb = width_emb.unsqueeze(1)
        pos_emb = height_emb + width_emb
        pos_emb = pos_emb.view(1, self.height * self.width, -1)
        emb = emb + pos_emb[:, :emb.shape[1], :]
        return emb
class LabelEmbedding(nn.Module):
    """Args:"""
    def __init__(self, num_classes, hidden_size, dropout_prob):
        super().__init__()
        use_cfg_embedding = dropout_prob > 0
        self.embedding_table = nn.Embedding(num_classes + use_cfg_embedding, hidden_size)
        self.num_classes = num_classes
        self.dropout_prob = dropout_prob
    def token_drop(self, labels, force_drop_ids=None):
        if force_drop_ids is None: drop_ids = torch.rand(labels.shape[0], device=labels.device) < self.dropout_prob
        else: drop_ids = torch.tensor(force_drop_ids == 1)
        labels = torch.where(drop_ids, self.num_classes, labels)
        return labels
    def forward(self, labels: torch.LongTensor, force_drop_ids=None):
        use_dropout = self.dropout_prob > 0
        if self.training and use_dropout or force_drop_ids is not None: labels = self.token_drop(labels, force_drop_ids)
        embeddings = self.embedding_table(labels)
        return embeddings
class TextImageProjection(nn.Module):
    def __init__(self, text_embed_dim: int=1024, image_embed_dim: int=768, cross_attention_dim: int=768, num_image_text_embeds: int=10):
        super().__init__()
        self.num_image_text_embeds = num_image_text_embeds
        self.image_embeds = nn.Linear(image_embed_dim, self.num_image_text_embeds * cross_attention_dim)
        self.text_proj = nn.Linear(text_embed_dim, cross_attention_dim)
    def forward(self, text_embeds: torch.Tensor, image_embeds: torch.Tensor):
        batch_size = text_embeds.shape[0]
        image_text_embeds = self.image_embeds(image_embeds)
        image_text_embeds = image_text_embeds.reshape(batch_size, self.num_image_text_embeds, -1)
        text_embeds = self.text_proj(text_embeds)
        return torch.cat([image_text_embeds, text_embeds], dim=1)
class ImageProjection(nn.Module):
    def __init__(self, image_embed_dim: int=768, cross_attention_dim: int=768, num_image_text_embeds: int=32):
        super().__init__()
        self.num_image_text_embeds = num_image_text_embeds
        self.image_embeds = nn.Linear(image_embed_dim, self.num_image_text_embeds * cross_attention_dim)
        self.norm = nn.LayerNorm(cross_attention_dim)
    def forward(self, image_embeds: torch.Tensor):
        batch_size = image_embeds.shape[0]
        image_embeds = self.image_embeds(image_embeds.to(self.image_embeds.weight.dtype))
        image_embeds = image_embeds.reshape(batch_size, self.num_image_text_embeds, -1)
        image_embeds = self.norm(image_embeds)
        return image_embeds
class IPAdapterFullImageProjection(nn.Module):
    def __init__(self, image_embed_dim=1024, cross_attention_dim=1024):
        super().__init__()
        from .attention import FeedForward
        self.ff = FeedForward(image_embed_dim, cross_attention_dim, mult=1, activation_fn='gelu')
        self.norm = nn.LayerNorm(cross_attention_dim)
    def forward(self, image_embeds: torch.Tensor): return self.norm(self.ff(image_embeds))
class IPAdapterFaceIDImageProjection(nn.Module):
    def __init__(self, image_embed_dim=1024, cross_attention_dim=1024, mult=1, num_tokens=1):
        super().__init__()
        from .attention import FeedForward
        self.num_tokens = num_tokens
        self.cross_attention_dim = cross_attention_dim
        self.ff = FeedForward(image_embed_dim, cross_attention_dim * num_tokens, mult=mult, activation_fn='gelu')
        self.norm = nn.LayerNorm(cross_attention_dim)
    def forward(self, image_embeds: torch.Tensor):
        x = self.ff(image_embeds)
        x = x.reshape(-1, self.num_tokens, self.cross_attention_dim)
        return self.norm(x)
class CombinedTimestepLabelEmbeddings(nn.Module):
    def __init__(self, num_classes, embedding_dim, class_dropout_prob=0.1):
        super().__init__()
        self.time_proj = Timesteps(num_channels=256, flip_sin_to_cos=True, downscale_freq_shift=1)
        self.timestep_embedder = TimestepEmbedding(in_channels=256, time_embed_dim=embedding_dim)
        self.class_embedder = LabelEmbedding(num_classes, embedding_dim, class_dropout_prob)
    def forward(self, timestep, class_labels, hidden_dtype=None):
        timesteps_proj = self.time_proj(timestep)
        timesteps_emb = self.timestep_embedder(timesteps_proj.to(dtype=hidden_dtype))
        class_labels = self.class_embedder(class_labels)
        conditioning = timesteps_emb + class_labels
        return conditioning
class CombinedTimestepTextProjEmbeddings(nn.Module):
    def __init__(self, embedding_dim, pooled_projection_dim):
        super().__init__()
        self.time_proj = Timesteps(num_channels=256, flip_sin_to_cos=True, downscale_freq_shift=0)
        self.timestep_embedder = TimestepEmbedding(in_channels=256, time_embed_dim=embedding_dim)
        self.text_embedder = PixArtAlphaTextProjection(pooled_projection_dim, embedding_dim, act_fn='silu')
    def forward(self, timestep, pooled_projection):
        timesteps_proj = self.time_proj(timestep)
        timesteps_emb = self.timestep_embedder(timesteps_proj.to(dtype=pooled_projection.dtype))
        pooled_projections = self.text_embedder(pooled_projection)
        conditioning = timesteps_emb + pooled_projections
        return conditioning
class CombinedTimestepGuidanceTextProjEmbeddings(nn.Module):
    def __init__(self, embedding_dim, pooled_projection_dim):
        super().__init__()
        self.time_proj = Timesteps(num_channels=256, flip_sin_to_cos=True, downscale_freq_shift=0)
        self.timestep_embedder = TimestepEmbedding(in_channels=256, time_embed_dim=embedding_dim)
        self.guidance_embedder = TimestepEmbedding(in_channels=256, time_embed_dim=embedding_dim)
        self.text_embedder = PixArtAlphaTextProjection(pooled_projection_dim, embedding_dim, act_fn='silu')
    def forward(self, timestep, guidance, pooled_projection):
        timesteps_proj = self.time_proj(timestep)
        timesteps_emb = self.timestep_embedder(timesteps_proj.to(dtype=pooled_projection.dtype))
        guidance_proj = self.time_proj(guidance)
        guidance_emb = self.guidance_embedder(guidance_proj.to(dtype=pooled_projection.dtype))
        time_guidance_emb = timesteps_emb + guidance_emb
        pooled_projections = self.text_embedder(pooled_projection)
        conditioning = time_guidance_emb + pooled_projections
        return conditioning
class CogView3CombinedTimestepSizeEmbeddings(nn.Module):
    def __init__(self, embedding_dim: int, condition_dim: int, pooled_projection_dim: int, timesteps_dim: int=256):
        super().__init__()
        self.time_proj = Timesteps(num_channels=timesteps_dim, flip_sin_to_cos=True, downscale_freq_shift=0)
        self.condition_proj = Timesteps(num_channels=condition_dim, flip_sin_to_cos=True, downscale_freq_shift=0)
        self.timestep_embedder = TimestepEmbedding(in_channels=timesteps_dim, time_embed_dim=embedding_dim)
        self.condition_embedder = PixArtAlphaTextProjection(pooled_projection_dim, embedding_dim, act_fn='silu')
    def forward(self, timestep: torch.Tensor, original_size: torch.Tensor, target_size: torch.Tensor, crop_coords: torch.Tensor, hidden_dtype: torch.dtype) -> torch.Tensor:
        timesteps_proj = self.time_proj(timestep)
        original_size_proj = self.condition_proj(original_size.flatten()).view(original_size.size(0), -1)
        crop_coords_proj = self.condition_proj(crop_coords.flatten()).view(crop_coords.size(0), -1)
        target_size_proj = self.condition_proj(target_size.flatten()).view(target_size.size(0), -1)
        condition_proj = torch.cat([original_size_proj, crop_coords_proj, target_size_proj], dim=1)
        timesteps_emb = self.timestep_embedder(timesteps_proj.to(dtype=hidden_dtype))
        condition_emb = self.condition_embedder(condition_proj.to(dtype=hidden_dtype))
        conditioning = timesteps_emb + condition_emb
        return conditioning
class HunyuanDiTAttentionPool(nn.Module):
    def __init__(self, spacial_dim: int, embed_dim: int, num_heads: int, output_dim: int=None):
        super().__init__()
        self.positional_embedding = nn.Parameter(torch.randn(spacial_dim + 1, embed_dim) / embed_dim ** 0.5)
        self.k_proj = nn.Linear(embed_dim, embed_dim)
        self.q_proj = nn.Linear(embed_dim, embed_dim)
        self.v_proj = nn.Linear(embed_dim, embed_dim)
        self.c_proj = nn.Linear(embed_dim, output_dim or embed_dim)
        self.num_heads = num_heads
    def forward(self, x):
        x = x.permute(1, 0, 2)
        x = torch.cat([x.mean(dim=0, keepdim=True), x], dim=0)
        x = x + self.positional_embedding[:, None, :].to(x.dtype)
        x, _ = F.multi_head_attention_forward(query=x[:1], key=x, value=x, embed_dim_to_check=x.shape[-1], num_heads=self.num_heads, q_proj_weight=self.q_proj.weight,
        k_proj_weight=self.k_proj.weight, v_proj_weight=self.v_proj.weight, in_proj_weight=None, in_proj_bias=torch.cat([self.q_proj.bias, self.k_proj.bias, self.v_proj.bias]), bias_k=None,
        bias_v=None, add_zero_attn=False, dropout_p=0, out_proj_weight=self.c_proj.weight, out_proj_bias=self.c_proj.bias, use_separate_proj_weight=True, training=self.training, need_weights=False)
        return x.squeeze(0)
class HunyuanCombinedTimestepTextSizeStyleEmbedding(nn.Module):
    def __init__(self, embedding_dim, pooled_projection_dim=1024, seq_len=256, cross_attention_dim=2048, use_style_cond_and_image_meta_size=True):
        super().__init__()
        self.time_proj = Timesteps(num_channels=256, flip_sin_to_cos=True, downscale_freq_shift=0)
        self.timestep_embedder = TimestepEmbedding(in_channels=256, time_embed_dim=embedding_dim)
        self.size_proj = Timesteps(num_channels=256, flip_sin_to_cos=True, downscale_freq_shift=0)
        self.pooler = HunyuanDiTAttentionPool(seq_len, cross_attention_dim, num_heads=8, output_dim=pooled_projection_dim)
        self.use_style_cond_and_image_meta_size = use_style_cond_and_image_meta_size
        if use_style_cond_and_image_meta_size:
            self.style_embedder = nn.Embedding(1, embedding_dim)
            extra_in_dim = 256 * 6 + embedding_dim + pooled_projection_dim
        else: extra_in_dim = pooled_projection_dim
        self.extra_embedder = PixArtAlphaTextProjection(in_features=extra_in_dim, hidden_size=embedding_dim * 4, out_features=embedding_dim, act_fn='silu_fp32')
    def forward(self, timestep, encoder_hidden_states, image_meta_size, style, hidden_dtype=None):
        timesteps_proj = self.time_proj(timestep)
        timesteps_emb = self.timestep_embedder(timesteps_proj.to(dtype=hidden_dtype))
        pooled_projections = self.pooler(encoder_hidden_states)
        if self.use_style_cond_and_image_meta_size:
            image_meta_size = self.size_proj(image_meta_size.view(-1))
            image_meta_size = image_meta_size.to(dtype=hidden_dtype)
            image_meta_size = image_meta_size.view(-1, 6 * 256)
            style_embedding = self.style_embedder(style)
            extra_cond = torch.cat([pooled_projections, image_meta_size, style_embedding], dim=1)
        else: extra_cond = torch.cat([pooled_projections], dim=1)
        conditioning = timesteps_emb + self.extra_embedder(extra_cond)
        return conditioning
class LuminaCombinedTimestepCaptionEmbedding(nn.Module):
    def __init__(self, hidden_size=4096, cross_attention_dim=2048, frequency_embedding_size=256):
        super().__init__()
        self.time_proj = Timesteps(num_channels=frequency_embedding_size, flip_sin_to_cos=True, downscale_freq_shift=0.0)
        self.timestep_embedder = TimestepEmbedding(in_channels=frequency_embedding_size, time_embed_dim=hidden_size)
        self.caption_embedder = nn.Sequential(nn.LayerNorm(cross_attention_dim), nn.Linear(cross_attention_dim, hidden_size, bias=True))
    def forward(self, timestep, caption_feat, caption_mask):
        time_freq = self.time_proj(timestep)
        time_embed = self.timestep_embedder(time_freq.to(dtype=self.timestep_embedder.linear_1.weight.dtype))
        caption_mask_float = caption_mask.float().unsqueeze(-1)
        caption_feats_pool = (caption_feat * caption_mask_float).sum(dim=1) / caption_mask_float.sum(dim=1)
        caption_feats_pool = caption_feats_pool.to(caption_feat)
        caption_embed = self.caption_embedder(caption_feats_pool)
        conditioning = time_embed + caption_embed
        return conditioning
class MochiCombinedTimestepCaptionEmbedding(nn.Module):
    def __init__(self, embedding_dim: int, pooled_projection_dim: int, text_embed_dim: int, time_embed_dim: int=256, num_attention_heads: int=8) -> None:
        super().__init__()
        self.time_proj = Timesteps(num_channels=time_embed_dim, flip_sin_to_cos=True, downscale_freq_shift=0.0)
        self.timestep_embedder = TimestepEmbedding(in_channels=time_embed_dim, time_embed_dim=embedding_dim)
        self.pooler = MochiAttentionPool(num_attention_heads=num_attention_heads, embed_dim=text_embed_dim, output_dim=embedding_dim)
        self.caption_proj = nn.Linear(text_embed_dim, pooled_projection_dim)
    def forward(self, timestep: torch.LongTensor, encoder_hidden_states: torch.Tensor, encoder_attention_mask: torch.Tensor, hidden_dtype: Optional[torch.dtype]=None):
        time_proj = self.time_proj(timestep)
        time_emb = self.timestep_embedder(time_proj.to(dtype=hidden_dtype))
        pooled_projections = self.pooler(encoder_hidden_states, encoder_attention_mask)
        caption_proj = self.caption_proj(encoder_hidden_states)
        conditioning = time_emb + pooled_projections
        return (conditioning, caption_proj)
class TextTimeEmbedding(nn.Module):
    def __init__(self, encoder_dim: int, time_embed_dim: int, num_heads: int=64):
        super().__init__()
        self.norm1 = nn.LayerNorm(encoder_dim)
        self.pool = AttentionPooling(num_heads, encoder_dim)
        self.proj = nn.Linear(encoder_dim, time_embed_dim)
        self.norm2 = nn.LayerNorm(time_embed_dim)
    def forward(self, hidden_states):
        hidden_states = self.norm1(hidden_states)
        hidden_states = self.pool(hidden_states)
        hidden_states = self.proj(hidden_states)
        hidden_states = self.norm2(hidden_states)
        return hidden_states
class TextImageTimeEmbedding(nn.Module):
    def __init__(self, text_embed_dim: int=768, image_embed_dim: int=768, time_embed_dim: int=1536):
        super().__init__()
        self.text_proj = nn.Linear(text_embed_dim, time_embed_dim)
        self.text_norm = nn.LayerNorm(time_embed_dim)
        self.image_proj = nn.Linear(image_embed_dim, time_embed_dim)
    def forward(self, text_embeds: torch.Tensor, image_embeds: torch.Tensor):
        time_text_embeds = self.text_proj(text_embeds)
        time_text_embeds = self.text_norm(time_text_embeds)
        time_image_embeds = self.image_proj(image_embeds)
        return time_image_embeds + time_text_embeds
class ImageTimeEmbedding(nn.Module):
    def __init__(self, image_embed_dim: int=768, time_embed_dim: int=1536):
        super().__init__()
        self.image_proj = nn.Linear(image_embed_dim, time_embed_dim)
        self.image_norm = nn.LayerNorm(time_embed_dim)
    def forward(self, image_embeds: torch.Tensor):
        time_image_embeds = self.image_proj(image_embeds)
        time_image_embeds = self.image_norm(time_image_embeds)
        return time_image_embeds
class ImageHintTimeEmbedding(nn.Module):
    def __init__(self, image_embed_dim: int=768, time_embed_dim: int=1536):
        super().__init__()
        self.image_proj = nn.Linear(image_embed_dim, time_embed_dim)
        self.image_norm = nn.LayerNorm(time_embed_dim)
        self.input_hint_block = nn.Sequential(nn.Conv2d(3, 16, 3, padding=1), nn.SiLU(), nn.Conv2d(16, 16, 3, padding=1), nn.SiLU(), nn.Conv2d(16, 32, 3, padding=1, stride=2), nn.SiLU(),
        nn.Conv2d(32, 32, 3, padding=1), nn.SiLU(), nn.Conv2d(32, 96, 3, padding=1, stride=2), nn.SiLU(), nn.Conv2d(96, 96, 3, padding=1), nn.SiLU(),
        nn.Conv2d(96, 256, 3, padding=1, stride=2), nn.SiLU(), nn.Conv2d(256, 4, 3, padding=1))
    def forward(self, image_embeds: torch.Tensor, hint: torch.Tensor):
        time_image_embeds = self.image_proj(image_embeds)
        time_image_embeds = self.image_norm(time_image_embeds)
        hint = self.input_hint_block(hint)
        return (time_image_embeds, hint)
class AttentionPooling(nn.Module):
    def __init__(self, num_heads, embed_dim, dtype=None):
        super().__init__()
        self.dtype = dtype
        self.positional_embedding = nn.Parameter(torch.randn(1, embed_dim) / embed_dim ** 0.5)
        self.k_proj = nn.Linear(embed_dim, embed_dim, dtype=self.dtype)
        self.q_proj = nn.Linear(embed_dim, embed_dim, dtype=self.dtype)
        self.v_proj = nn.Linear(embed_dim, embed_dim, dtype=self.dtype)
        self.num_heads = num_heads
        self.dim_per_head = embed_dim // self.num_heads
    def forward(self, x):
        bs, length, width = x.size()
        def shape(x):
            x = x.view(bs, -1, self.num_heads, self.dim_per_head)
            x = x.transpose(1, 2)
            x = x.reshape(bs * self.num_heads, -1, self.dim_per_head)
            x = x.transpose(1, 2)
            return x
        class_token = x.mean(dim=1, keepdim=True) + self.positional_embedding.to(x.dtype)
        x = torch.cat([class_token, x], dim=1)
        q = shape(self.q_proj(class_token))
        k = shape(self.k_proj(x))
        v = shape(self.v_proj(x))
        scale = 1 / math.sqrt(math.sqrt(self.dim_per_head))
        weight = torch.einsum('bct,bcs->bts', q * scale, k * scale)
        weight = torch.softmax(weight.float(), dim=-1).type(weight.dtype)
        a = torch.einsum('bts,bcs->bct', weight, v)
        a = a.reshape(bs, -1, 1).transpose(1, 2)
        return a[:, 0, :]
class MochiAttentionPool(nn.Module):
    def __init__(self, num_attention_heads: int, embed_dim: int, output_dim: Optional[int]=None) -> None:
        super().__init__()
        self.output_dim = output_dim or embed_dim
        self.num_attention_heads = num_attention_heads
        self.to_kv = nn.Linear(embed_dim, 2 * embed_dim)
        self.to_q = nn.Linear(embed_dim, embed_dim)
        self.to_out = nn.Linear(embed_dim, self.output_dim)
    @staticmethod
    def pool_tokens(x: torch.Tensor, mask: torch.Tensor, *, keepdim=False) -> torch.Tensor:
        """Returns:"""
        assert x.size(1) == mask.size(1)
        assert x.size(0) == mask.size(0)
        mask = mask[:, :, None].to(dtype=x.dtype)
        mask = mask / mask.sum(dim=1, keepdim=True).clamp(min=1)
        pooled = (x * mask).sum(dim=1, keepdim=keepdim)
        return pooled
    def forward(self, x: torch.Tensor, mask: torch.BoolTensor) -> torch.Tensor:
        """Returns:"""
        D = x.size(2)
        attn_mask = mask[:, None, None, :].bool()
        attn_mask = F.pad(attn_mask, (1, 0), value=True)
        x_pool = self.pool_tokens(x, mask, keepdim=True)
        x = torch.cat([x_pool, x], dim=1)
        kv = self.to_kv(x)
        q = self.to_q(x[:, 0])
        head_dim = D // self.num_attention_heads
        kv = kv.unflatten(2, (2, self.num_attention_heads, head_dim))
        kv = kv.transpose(1, 3)
        k, v = kv.unbind(2)
        q = q.unflatten(1, (self.num_attention_heads, head_dim))
        q = q.unsqueeze(2)
        x = F.scaled_dot_product_attention(q, k, v, attn_mask=attn_mask, dropout_p=0.0)
        x = x.squeeze(2).flatten(1, 2)
        x = self.to_out(x)
        return x
def get_fourier_embeds_from_boundingbox(embed_dim, box):
    """Returns:"""
    batch_size, num_boxes = box.shape[:2]
    emb = 100 ** (torch.arange(embed_dim) / embed_dim)
    emb = emb[None, None, None].to(device=box.device, dtype=box.dtype)
    emb = emb * box.unsqueeze(-1)
    emb = torch.stack((emb.sin(), emb.cos()), dim=-1)
    emb = emb.permute(0, 1, 3, 4, 2).reshape(batch_size, num_boxes, embed_dim * 2 * 4)
    return emb
class GLIGENTextBoundingboxProjection(nn.Module):
    def __init__(self, positive_len, out_dim, feature_type='text-only', fourier_freqs=8):
        super().__init__()
        self.positive_len = positive_len
        self.out_dim = out_dim
        self.fourier_embedder_dim = fourier_freqs
        self.position_dim = fourier_freqs * 2 * 4
        if isinstance(out_dim, tuple): out_dim = out_dim[0]
        if feature_type == 'text-only':
            self.linears = nn.Sequential(nn.Linear(self.positive_len + self.position_dim, 512), nn.SiLU(), nn.Linear(512, 512), nn.SiLU(), nn.Linear(512, out_dim))
            self.null_positive_feature = torch.nn.Parameter(torch.zeros([self.positive_len]))
        elif feature_type == 'text-image':
            self.linears_text = nn.Sequential(nn.Linear(self.positive_len + self.position_dim, 512), nn.SiLU(), nn.Linear(512, 512), nn.SiLU(), nn.Linear(512, out_dim))
            self.linears_image = nn.Sequential(nn.Linear(self.positive_len + self.position_dim, 512), nn.SiLU(), nn.Linear(512, 512), nn.SiLU(), nn.Linear(512, out_dim))
            self.null_text_feature = torch.nn.Parameter(torch.zeros([self.positive_len]))
            self.null_image_feature = torch.nn.Parameter(torch.zeros([self.positive_len]))
        self.null_position_feature = torch.nn.Parameter(torch.zeros([self.position_dim]))
    def forward(self, boxes, masks, positive_embeddings=None, phrases_masks=None, image_masks=None, phrases_embeddings=None, image_embeddings=None):
        masks = masks.unsqueeze(-1)
        xyxy_embedding = get_fourier_embeds_from_boundingbox(self.fourier_embedder_dim, boxes)
        xyxy_null = self.null_position_feature.view(1, 1, -1)
        xyxy_embedding = xyxy_embedding * masks + (1 - masks) * xyxy_null
        if positive_embeddings is not None:
            positive_null = self.null_positive_feature.view(1, 1, -1)
            positive_embeddings = positive_embeddings * masks + (1 - masks) * positive_null
            objs = self.linears(torch.cat([positive_embeddings, xyxy_embedding], dim=-1))
        else:
            phrases_masks = phrases_masks.unsqueeze(-1)
            image_masks = image_masks.unsqueeze(-1)
            text_null = self.null_text_feature.view(1, 1, -1)
            image_null = self.null_image_feature.view(1, 1, -1)
            phrases_embeddings = phrases_embeddings * phrases_masks + (1 - phrases_masks) * text_null
            image_embeddings = image_embeddings * image_masks + (1 - image_masks) * image_null
            objs_text = self.linears_text(torch.cat([phrases_embeddings, xyxy_embedding], dim=-1))
            objs_image = self.linears_image(torch.cat([image_embeddings, xyxy_embedding], dim=-1))
            objs = torch.cat([objs_text, objs_image], dim=1)
        return objs
class PixArtAlphaCombinedTimestepSizeEmbeddings(nn.Module):
    def __init__(self, embedding_dim, size_emb_dim, use_additional_conditions: bool=False):
        super().__init__()
        self.outdim = size_emb_dim
        self.time_proj = Timesteps(num_channels=256, flip_sin_to_cos=True, downscale_freq_shift=0)
        self.timestep_embedder = TimestepEmbedding(in_channels=256, time_embed_dim=embedding_dim)
        self.use_additional_conditions = use_additional_conditions
        if use_additional_conditions:
            self.additional_condition_proj = Timesteps(num_channels=256, flip_sin_to_cos=True, downscale_freq_shift=0)
            self.resolution_embedder = TimestepEmbedding(in_channels=256, time_embed_dim=size_emb_dim)
            self.aspect_ratio_embedder = TimestepEmbedding(in_channels=256, time_embed_dim=size_emb_dim)
    def forward(self, timestep, resolution, aspect_ratio, batch_size, hidden_dtype):
        timesteps_proj = self.time_proj(timestep)
        timesteps_emb = self.timestep_embedder(timesteps_proj.to(dtype=hidden_dtype))
        if self.use_additional_conditions:
            resolution_emb = self.additional_condition_proj(resolution.flatten()).to(hidden_dtype)
            resolution_emb = self.resolution_embedder(resolution_emb).reshape(batch_size, -1)
            aspect_ratio_emb = self.additional_condition_proj(aspect_ratio.flatten()).to(hidden_dtype)
            aspect_ratio_emb = self.aspect_ratio_embedder(aspect_ratio_emb).reshape(batch_size, -1)
            conditioning = timesteps_emb + torch.cat([resolution_emb, aspect_ratio_emb], dim=1)
        else: conditioning = timesteps_emb
        return conditioning
class PixArtAlphaTextProjection(nn.Module):
    def __init__(self, in_features, hidden_size, out_features=None, act_fn='gelu_tanh'):
        super().__init__()
        if out_features is None: out_features = hidden_size
        self.linear_1 = nn.Linear(in_features=in_features, out_features=hidden_size, bias=True)
        if act_fn == 'gelu_tanh': self.act_1 = nn.GELU(approximate='tanh')
        elif act_fn == 'silu': self.act_1 = nn.SiLU()
        elif act_fn == 'silu_fp32': self.act_1 = FP32SiLU()
        else: raise ValueError(f'Unknown activation function: {act_fn}')
        self.linear_2 = nn.Linear(in_features=hidden_size, out_features=out_features, bias=True)
    def forward(self, caption):
        hidden_states = self.linear_1(caption)
        hidden_states = self.act_1(hidden_states)
        hidden_states = self.linear_2(hidden_states)
        return hidden_states
class IPAdapterPlusImageProjectionBlock(nn.Module):
    def __init__(self, embed_dims: int=768, dim_head: int=64, heads: int=16, ffn_ratio: float=4) -> None:
        super().__init__()
        from .attention import FeedForward
        self.ln0 = nn.LayerNorm(embed_dims)
        self.ln1 = nn.LayerNorm(embed_dims)
        self.attn = Attention(query_dim=embed_dims, dim_head=dim_head, heads=heads, out_bias=False)
        self.ff = nn.Sequential(nn.LayerNorm(embed_dims), FeedForward(embed_dims, embed_dims, activation_fn='gelu', mult=ffn_ratio, bias=False))
    def forward(self, x, latents, residual):
        encoder_hidden_states = self.ln0(x)
        latents = self.ln1(latents)
        encoder_hidden_states = torch.cat([encoder_hidden_states, latents], dim=-2)
        latents = self.attn(latents, encoder_hidden_states) + residual
        latents = self.ff(latents) + latents
        return latents
class IPAdapterPlusImageProjection(nn.Module):
    """Args:"""
    def __init__(self, embed_dims: int=768, output_dims: int=1024, hidden_dims: int=1280, depth: int=4, dim_head: int=64, heads: int=16, num_queries: int=8, ffn_ratio: float=4) -> None:
        super().__init__()
        self.latents = nn.Parameter(torch.randn(1, num_queries, hidden_dims) / hidden_dims ** 0.5)
        self.proj_in = nn.Linear(embed_dims, hidden_dims)
        self.proj_out = nn.Linear(hidden_dims, output_dims)
        self.norm_out = nn.LayerNorm(output_dims)
        self.layers = nn.ModuleList([IPAdapterPlusImageProjectionBlock(hidden_dims, dim_head, heads, ffn_ratio) for _ in range(depth)])
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Returns:"""
        latents = self.latents.repeat(x.size(0), 1, 1)
        x = self.proj_in(x)
        for block in self.layers:
            residual = latents
            latents = block(x, latents, residual)
        latents = self.proj_out(latents)
        return self.norm_out(latents)
class IPAdapterFaceIDPlusImageProjection(nn.Module):
    """Args:"""
    def __init__(self, embed_dims: int=768, output_dims: int=768, hidden_dims: int=1280, id_embeddings_dim: int=512, depth: int=4, dim_head: int=64, heads: int=16, num_tokens: int=4,
    num_queries: int=8, ffn_ratio: float=4, ffproj_ratio: int=2) -> None:
        super().__init__()
        from .attention import FeedForward
        self.num_tokens = num_tokens
        self.embed_dim = embed_dims
        self.clip_embeds = None
        self.shortcut = False
        self.shortcut_scale = 1.0
        self.proj = FeedForward(id_embeddings_dim, embed_dims * num_tokens, activation_fn='gelu', mult=ffproj_ratio)
        self.norm = nn.LayerNorm(embed_dims)
        self.proj_in = nn.Linear(hidden_dims, embed_dims)
        self.proj_out = nn.Linear(embed_dims, output_dims)
        self.norm_out = nn.LayerNorm(output_dims)
        self.layers = nn.ModuleList([IPAdapterPlusImageProjectionBlock(embed_dims, dim_head, heads, ffn_ratio) for _ in range(depth)])
    def forward(self, id_embeds: torch.Tensor) -> torch.Tensor:
        """Returns:"""
        id_embeds = id_embeds.to(self.clip_embeds.dtype)
        id_embeds = self.proj(id_embeds)
        id_embeds = id_embeds.reshape(-1, self.num_tokens, self.embed_dim)
        id_embeds = self.norm(id_embeds)
        latents = id_embeds
        clip_embeds = self.proj_in(self.clip_embeds)
        x = clip_embeds.reshape(-1, clip_embeds.shape[2], clip_embeds.shape[3])
        for block in self.layers:
            residual = latents
            latents = block(x, latents, residual)
        latents = self.proj_out(latents)
        out = self.norm_out(latents)
        if self.shortcut: out = id_embeds + self.shortcut_scale * out
        return out
class IPAdapterTimeImageProjectionBlock(nn.Module):
    """Args:"""
    def __init__(self, hidden_dim: int=1280, dim_head: int=64, heads: int=20, ffn_ratio: int=4) -> None:
        super().__init__()
        from .attention import FeedForward
        self.ln0 = nn.LayerNorm(hidden_dim)
        self.ln1 = nn.LayerNorm(hidden_dim)
        self.attn = Attention(query_dim=hidden_dim, cross_attention_dim=hidden_dim, dim_head=dim_head, heads=heads, bias=False, out_bias=False)
        self.ff = FeedForward(hidden_dim, hidden_dim, activation_fn='gelu', mult=ffn_ratio, bias=False)
        self.adaln_silu = nn.SiLU()
        self.adaln_proj = nn.Linear(hidden_dim, 4 * hidden_dim)
        self.adaln_norm = nn.LayerNorm(hidden_dim)
        self.attn.scale = 1 / math.sqrt(math.sqrt(dim_head))
        self.attn.fuse_projections()
        self.attn.to_k = None
        self.attn.to_v = None
    def forward(self, x: torch.Tensor, latents: torch.Tensor, timestep_emb: torch.Tensor) -> torch.Tensor:
        """Returns:"""
        emb = self.adaln_proj(self.adaln_silu(timestep_emb))
        shift_msa, scale_msa, shift_mlp, scale_mlp = emb.chunk(4, dim=1)
        residual = latents
        x = self.ln0(x)
        latents = self.ln1(latents) * (1 + scale_msa[:, None]) + shift_msa[:, None]
        batch_size = latents.shape[0]
        query = self.attn.to_q(latents)
        kv_input = torch.cat((x, latents), dim=-2)
        key, value = self.attn.to_kv(kv_input).chunk(2, dim=-1)
        inner_dim = key.shape[-1]
        head_dim = inner_dim // self.attn.heads
        query = query.view(batch_size, -1, self.attn.heads, head_dim).transpose(1, 2)
        key = key.view(batch_size, -1, self.attn.heads, head_dim).transpose(1, 2)
        value = value.view(batch_size, -1, self.attn.heads, head_dim).transpose(1, 2)
        weight = query * self.attn.scale @ (key * self.attn.scale).transpose(-2, -1)
        weight = torch.softmax(weight.float(), dim=-1).type(weight.dtype)
        latents = weight @ value
        latents = latents.transpose(1, 2).reshape(batch_size, -1, self.attn.heads * head_dim)
        latents = self.attn.to_out[0](latents)
        latents = self.attn.to_out[1](latents)
        latents = latents + residual
        residual = latents
        latents = self.adaln_norm(latents) * (1 + scale_mlp[:, None]) + shift_mlp[:, None]
        return self.ff(latents) + residual
class IPAdapterTimeImageProjection(nn.Module):
    """Args:"""
    def __init__(self, embed_dim: int=1152, output_dim: int=2432, hidden_dim: int=1280, depth: int=4, dim_head: int=64, heads: int=20, num_queries: int=64, ffn_ratio: int=4,
    timestep_in_dim: int=320, timestep_flip_sin_to_cos: bool=True, timestep_freq_shift: int=0) -> None:
        super().__init__()
        self.latents = nn.Parameter(torch.randn(1, num_queries, hidden_dim) / hidden_dim ** 0.5)
        self.proj_in = nn.Linear(embed_dim, hidden_dim)
        self.proj_out = nn.Linear(hidden_dim, output_dim)
        self.norm_out = nn.LayerNorm(output_dim)
        self.layers = nn.ModuleList([IPAdapterTimeImageProjectionBlock(hidden_dim, dim_head, heads, ffn_ratio) for _ in range(depth)])
        self.time_proj = Timesteps(timestep_in_dim, timestep_flip_sin_to_cos, timestep_freq_shift)
        self.time_embedding = TimestepEmbedding(timestep_in_dim, hidden_dim, act_fn='silu')
    def forward(self, x: torch.Tensor, timestep: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Returns:"""
        timestep_emb = self.time_proj(timestep).to(dtype=x.dtype)
        timestep_emb = self.time_embedding(timestep_emb)
        latents = self.latents.repeat(x.size(0), 1, 1)
        x = self.proj_in(x)
        x = x + timestep_emb[:, None]
        for block in self.layers: latents = block(x, latents, timestep_emb)
        latents = self.proj_out(latents)
        latents = self.norm_out(latents)
        return (latents, timestep_emb)
class MultiIPAdapterImageProjection(nn.Module):
    def __init__(self, IPAdapterImageProjectionLayers: Union[List[nn.Module], Tuple[nn.Module]]):
        super().__init__()
        self.image_projection_layers = nn.ModuleList(IPAdapterImageProjectionLayers)
    def forward(self, image_embeds: List[torch.Tensor]):
        projected_image_embeds = []
        if not isinstance(image_embeds, list):
            deprecation_message = 'You have passed a tensor as `image_embeds`.This is deprecated and will be removed in a future release. Please make sure to update your script to pass `image_embeds` as a list of tensors to suppress this warning.'
            deprecate('image_embeds not a list', '1.0.0', deprecation_message, standard_warn=False)
            image_embeds = [image_embeds.unsqueeze(1)]
        if len(image_embeds) != len(self.image_projection_layers): raise ValueError(f'image_embeds must have the same length as image_projection_layers, got {len(image_embeds)} and {len(self.image_projection_layers)}')
        for image_embed, image_projection_layer in zip(image_embeds, self.image_projection_layers):
            batch_size, num_images = (image_embed.shape[0], image_embed.shape[1])
            image_embed = image_embed.reshape((batch_size * num_images,) + image_embed.shape[2:])
            image_embed = image_projection_layer(image_embed)
            image_embed = image_embed.reshape((batch_size, num_images) + image_embed.shape[1:])
            projected_image_embeds.append(image_embed)
        return projected_image_embeds
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
