'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..attention_processor import AllegroAttnProcessor2_0, Attention
from ...configuration_utils import ConfigMixin, register_to_config
from ..embeddings import PatchEmbed, PixArtAlphaTextProjection
from ..modeling_outputs import Transformer2DModelOutput
from ...utils.torch_utils import maybe_allow_in_graph
from ...utils import is_torch_version
from ..normalization import AdaLayerNormSingle
from typing import Any, Dict, Optional, Tuple
from ..modeling_utils import ModelMixin
from ..attention import FeedForward
import torch.nn.functional as F
import torch.nn as nn
import torch
@maybe_allow_in_graph
class AllegroTransformerBlock(nn.Module):
    """Args:"""
    def __init__(self, dim: int, num_attention_heads: int, attention_head_dim: int, dropout=0.0, cross_attention_dim: Optional[int]=None, activation_fn: str='geglu',
    attention_bias: bool=False, norm_elementwise_affine: bool=True, norm_eps: float=1e-05):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim, elementwise_affine=norm_elementwise_affine, eps=norm_eps)
        self.attn1 = Attention(query_dim=dim, heads=num_attention_heads, dim_head=attention_head_dim, dropout=dropout, bias=attention_bias, cross_attention_dim=None, processor=AllegroAttnProcessor2_0())
        self.norm2 = nn.LayerNorm(dim, elementwise_affine=norm_elementwise_affine, eps=norm_eps)
        self.attn2 = Attention(query_dim=dim, cross_attention_dim=cross_attention_dim, heads=num_attention_heads, dim_head=attention_head_dim, dropout=dropout, bias=attention_bias, processor=AllegroAttnProcessor2_0())
        self.norm3 = nn.LayerNorm(dim, elementwise_affine=norm_elementwise_affine, eps=norm_eps)
        self.ff = FeedForward(dim, dropout=dropout, activation_fn=activation_fn)
        self.scale_shift_table = nn.Parameter(torch.randn(6, dim) / dim ** 0.5)
    def forward(self, hidden_states: torch.Tensor, encoder_hidden_states: Optional[torch.Tensor]=None, temb: Optional[torch.LongTensor]=None, attention_mask: Optional[torch.Tensor]=None,
    encoder_attention_mask: Optional[torch.Tensor]=None, image_rotary_emb=None) -> torch.Tensor:
        batch_size = hidden_states.shape[0]
        shift_msa, scale_msa, gate_msa, shift_mlp, scale_mlp, gate_mlp = (self.scale_shift_table[None] + temb.reshape(batch_size, 6, -1)).chunk(6, dim=1)
        norm_hidden_states = self.norm1(hidden_states)
        norm_hidden_states = norm_hidden_states * (1 + scale_msa) + shift_msa
        norm_hidden_states = norm_hidden_states.squeeze(1)
        attn_output = self.attn1(norm_hidden_states, encoder_hidden_states=None, attention_mask=attention_mask, image_rotary_emb=image_rotary_emb)
        attn_output = gate_msa * attn_output
        hidden_states = attn_output + hidden_states
        if hidden_states.ndim == 4: hidden_states = hidden_states.squeeze(1)
        if self.attn2 is not None:
            norm_hidden_states = hidden_states
            attn_output = self.attn2(norm_hidden_states, encoder_hidden_states=encoder_hidden_states, attention_mask=encoder_attention_mask, image_rotary_emb=None)
            hidden_states = attn_output + hidden_states
        norm_hidden_states = self.norm2(hidden_states)
        norm_hidden_states = norm_hidden_states * (1 + scale_mlp) + shift_mlp
        ff_output = self.ff(norm_hidden_states)
        ff_output = gate_mlp * ff_output
        hidden_states = ff_output + hidden_states
        if hidden_states.ndim == 4: hidden_states = hidden_states.squeeze(1)
        return hidden_states
class AllegroTransformer3DModel(ModelMixin, ConfigMixin):
    _supports_gradient_checkpointing = True
    """Args:"""
    @register_to_config
    def __init__(self, patch_size: int=2, patch_size_t: int=1, num_attention_heads: int=24, attention_head_dim: int=96, in_channels: int=4, out_channels: int=4, num_layers: int=32,
    dropout: float=0.0, cross_attention_dim: int=2304, attention_bias: bool=True, sample_height: int=90, sample_width: int=160, sample_frames: int=22, activation_fn: str='gelu-approximate',
    norm_elementwise_affine: bool=False, norm_eps: float=1e-06, caption_channels: int=4096, interpolation_scale_h: float=2.0, interpolation_scale_w: float=2.0, interpolation_scale_t: float=2.2):
        super().__init__()
        self.inner_dim = num_attention_heads * attention_head_dim
        interpolation_scale_t = interpolation_scale_t if interpolation_scale_t is not None else (sample_frames - 1) // 16 + 1 if sample_frames % 2 == 1 else sample_frames // 16
        interpolation_scale_h = interpolation_scale_h if interpolation_scale_h is not None else sample_height / 30
        interpolation_scale_w = interpolation_scale_w if interpolation_scale_w is not None else sample_width / 40
        self.pos_embed = PatchEmbed(height=sample_height, width=sample_width, patch_size=patch_size, in_channels=in_channels, embed_dim=self.inner_dim, pos_embed_type=None)
        self.transformer_blocks = nn.ModuleList([AllegroTransformerBlock(self.inner_dim, num_attention_heads, attention_head_dim, dropout=dropout, cross_attention_dim=cross_attention_dim,
        activation_fn=activation_fn, attention_bias=attention_bias, norm_elementwise_affine=norm_elementwise_affine, norm_eps=norm_eps) for _ in range(num_layers)])
        self.norm_out = nn.LayerNorm(self.inner_dim, elementwise_affine=False, eps=1e-06)
        self.scale_shift_table = nn.Parameter(torch.randn(2, self.inner_dim) / self.inner_dim ** 0.5)
        self.proj_out = nn.Linear(self.inner_dim, patch_size * patch_size * out_channels)
        self.adaln_single = AdaLayerNormSingle(self.inner_dim, use_additional_conditions=False)
        self.caption_projection = PixArtAlphaTextProjection(in_features=caption_channels, hidden_size=self.inner_dim)
        self.gradient_checkpointing = False
    def _set_gradient_checkpointing(self, module, value=False): self.gradient_checkpointing = value
    def forward(self, hidden_states: torch.Tensor, encoder_hidden_states: torch.Tensor, timestep: torch.LongTensor, attention_mask: Optional[torch.Tensor]=None,
    encoder_attention_mask: Optional[torch.Tensor]=None, image_rotary_emb: Optional[Tuple[torch.Tensor, torch.Tensor]]=None, return_dict: bool=True):
        batch_size, num_channels, num_frames, height, width = hidden_states.shape
        p_t = self.config.patch_size_t
        p = self.config.patch_size
        post_patch_num_frames = num_frames // p_t
        post_patch_height = height // p
        post_patch_width = width // p
        if attention_mask is not None and attention_mask.ndim == 4:
            attention_mask = attention_mask.to(hidden_states.dtype)
            attention_mask = attention_mask[:, :num_frames]
            if attention_mask.numel() > 0:
                attention_mask = attention_mask.unsqueeze(1)
                attention_mask = F.max_pool3d(attention_mask, kernel_size=(p_t, p, p), stride=(p_t, p, p))
                attention_mask = attention_mask.flatten(1).view(batch_size, 1, -1)
            attention_mask = (1 - attention_mask.bool().to(hidden_states.dtype)) * -10000.0 if attention_mask.numel() > 0 else None
        if encoder_attention_mask is not None and encoder_attention_mask.ndim == 2:
            encoder_attention_mask = (1 - encoder_attention_mask.to(self.dtype)) * -10000.0
            encoder_attention_mask = encoder_attention_mask.unsqueeze(1)
        timestep, embedded_timestep = self.adaln_single(timestep, batch_size=batch_size, hidden_dtype=hidden_states.dtype)
        hidden_states = hidden_states.permute(0, 2, 1, 3, 4).flatten(0, 1)
        hidden_states = self.pos_embed(hidden_states)
        hidden_states = hidden_states.unflatten(0, (batch_size, -1)).flatten(1, 2)
        encoder_hidden_states = self.caption_projection(encoder_hidden_states)
        encoder_hidden_states = encoder_hidden_states.view(batch_size, -1, encoder_hidden_states.shape[-1])
        for i, block in enumerate(self.transformer_blocks):
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module):
                    def custom_forward(*inputs): return module(*inputs)
                    return custom_forward
                ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
                hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(block), hidden_states, encoder_hidden_states,
                timestep, attention_mask, encoder_attention_mask, image_rotary_emb, **ckpt_kwargs)
            else: hidden_states = block(hidden_states=hidden_states, encoder_hidden_states=encoder_hidden_states, temb=timestep, attention_mask=attention_mask,
            encoder_attention_mask=encoder_attention_mask, image_rotary_emb=image_rotary_emb)
        shift, scale = (self.scale_shift_table[None] + embedded_timestep[:, None]).chunk(2, dim=1)
        hidden_states = self.norm_out(hidden_states)
        hidden_states = hidden_states * (1 + scale) + shift
        hidden_states = self.proj_out(hidden_states)
        hidden_states = hidden_states.squeeze(1)
        hidden_states = hidden_states.reshape(batch_size, post_patch_num_frames, post_patch_height, post_patch_width, p_t, p, p, -1)
        hidden_states = hidden_states.permute(0, 7, 1, 4, 2, 5, 3, 6)
        output = hidden_states.reshape(batch_size, -1, num_frames, height, width)
        if not return_dict: return (output,)
        return Transformer2DModelOutput(sample=output)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
