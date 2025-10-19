'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from .normalization import AdaLayerNorm, AdaLayerNormContinuous, AdaLayerNormZero, RMSNorm, SAPI5AdaLayerNormZeroX, SD35AdaLayerNormZeroX
from .activations import GEGLU, GELU, ApproximateGELU, FP32SiLU, LinearActivation, SwiGLU
from .attention_processor import Attention, JointAttnProcessor2_0
from .embeddings import SinusoidalPositionalEmbedding
from ..utils.torch_utils import maybe_allow_in_graph
from typing import Any, Dict, List, Optional, Tuple
from ..utils import deprecate
import torch.nn.functional as F
from torch import nn
import torch
def _chunked_feed_forward(ff: nn.Module, hidden_states: torch.Tensor, chunk_dim: int, chunk_size: int):
    if hidden_states.shape[chunk_dim] % chunk_size != 0: raise ValueError(f'`hidden_states` dimension to be chunked: {hidden_states.shape[chunk_dim]} has to be divisible by chunk size: {chunk_size}. Make sure to set an appropriate `chunk_size` when calling `unet.enable_forward_chunking`.')
    num_chunks = hidden_states.shape[chunk_dim] // chunk_size
    ff_output = torch.cat([ff(hid_slice) for hid_slice in hidden_states.chunk(num_chunks, dim=chunk_dim)], dim=chunk_dim)
    return ff_output
@maybe_allow_in_graph
class GatedSelfAttentionDense(nn.Module):
    def __init__(self, query_dim: int, context_dim: int, n_heads: int, d_head: int):
        super().__init__()
        self.linear = nn.Linear(context_dim, query_dim)
        self.attn = Attention(query_dim=query_dim, heads=n_heads, dim_head=d_head)
        self.ff = FeedForward(query_dim, activation_fn='geglu')
        self.norm1 = nn.LayerNorm(query_dim)
        self.norm2 = nn.LayerNorm(query_dim)
        self.register_parameter('alpha_attn', nn.Parameter(torch.tensor(0.0)))
        self.register_parameter('alpha_dense', nn.Parameter(torch.tensor(0.0)))
        self.enabled = True
    def forward(self, x: torch.Tensor, objs: torch.Tensor) -> torch.Tensor:
        if not self.enabled: return x
        n_visual = x.shape[1]
        objs = self.linear(objs)
        x = x + self.alpha_attn.tanh() * self.attn(self.norm1(torch.cat([x, objs], dim=1)))[:, :n_visual, :]
        x = x + self.alpha_dense.tanh() * self.ff(self.norm2(x))
        return x
@maybe_allow_in_graph
class JointTransformerBlock(nn.Module):
    def __init__(self, dim: int, num_attention_heads: int, attention_head_dim: int, context_pre_only: bool=False, qk_norm: Optional[str]=None, use_dual_attention: bool=False):
        super().__init__()
        self.use_dual_attention = use_dual_attention
        self.context_pre_only = context_pre_only
        context_norm_type = 'ada_norm_continous' if context_pre_only else 'ada_norm_zero'
        if use_dual_attention:
            try: self.norm1 = SD35AdaLayerNormZeroX(dim)
            except: self.norm1 = SAPI5AdaLayerNormZeroX(dim)
        else: self.norm1 = AdaLayerNormZero(dim)
        if context_norm_type == 'ada_norm_continous': self.norm1_context = AdaLayerNormContinuous(dim, dim, elementwise_affine=False, eps=1e-06, bias=True, norm_type='layer_norm')
        elif context_norm_type == 'ada_norm_zero': self.norm1_context = AdaLayerNormZero(dim)
        else: raise ValueError(f'Unknown context_norm_type: {context_norm_type}, currently only support `ada_norm_continous`, `ada_norm_zero`')
        if hasattr(F, 'scaled_dot_product_attention'): processor = JointAttnProcessor2_0()
        else: raise ValueError('The current PyTorch version does not support the `scaled_dot_product_attention` function.')
        self.attn = Attention(query_dim=dim, cross_attention_dim=None, added_kv_proj_dim=dim, dim_head=attention_head_dim, heads=num_attention_heads, out_dim=dim,
        context_pre_only=context_pre_only, bias=True, processor=processor, qk_norm=qk_norm, eps=1e-06)
        if use_dual_attention: self.attn2 = Attention(query_dim=dim, cross_attention_dim=None, dim_head=attention_head_dim, heads=num_attention_heads,
        out_dim=dim, bias=True, processor=processor, qk_norm=qk_norm, eps=1e-06)
        else: self.attn2 = None
        self.norm2 = nn.LayerNorm(dim, elementwise_affine=False, eps=1e-06)
        self.ff = FeedForward(dim=dim, dim_out=dim, activation_fn='gelu-approximate')
        if not context_pre_only:
            self.norm2_context = nn.LayerNorm(dim, elementwise_affine=False, eps=1e-06)
            self.ff_context = FeedForward(dim=dim, dim_out=dim, activation_fn='gelu-approximate')
        else:
            self.norm2_context = None
            self.ff_context = None
        self._chunk_size = None
        self._chunk_dim = 0
    def set_chunk_feed_forward(self, chunk_size: Optional[int], dim: int=0):
        self._chunk_size = chunk_size
        self._chunk_dim = dim
    def forward(self, hidden_states: torch.FloatTensor, encoder_hidden_states: torch.FloatTensor, temb: torch.FloatTensor, joint_attention_kwargs: Optional[Dict[str, Any]]=None):
        joint_attention_kwargs = joint_attention_kwargs or {}
        if self.use_dual_attention: norm_hidden_states, gate_msa, shift_mlp, scale_mlp, gate_mlp, norm_hidden_states2, gate_msa2 = self.norm1(hidden_states, emb=temb)
        else: norm_hidden_states, gate_msa, shift_mlp, scale_mlp, gate_mlp = self.norm1(hidden_states, emb=temb)
        if self.context_pre_only: norm_encoder_hidden_states = self.norm1_context(encoder_hidden_states, temb)
        else: norm_encoder_hidden_states, c_gate_msa, c_shift_mlp, c_scale_mlp, c_gate_mlp = self.norm1_context(encoder_hidden_states, emb=temb)
        attn_output, context_attn_output = self.attn(hidden_states=norm_hidden_states, encoder_hidden_states=norm_encoder_hidden_states, **joint_attention_kwargs)
        attn_output = gate_msa.unsqueeze(1) * attn_output
        hidden_states = hidden_states + attn_output
        if self.use_dual_attention:
            attn_output2 = self.attn2(hidden_states=norm_hidden_states2, **joint_attention_kwargs)
            attn_output2 = gate_msa2.unsqueeze(1) * attn_output2
            hidden_states = hidden_states + attn_output2
        norm_hidden_states = self.norm2(hidden_states)
        norm_hidden_states = norm_hidden_states * (1 + scale_mlp[:, None]) + shift_mlp[:, None]
        if self._chunk_size is not None: ff_output = _chunked_feed_forward(self.ff, norm_hidden_states, self._chunk_dim, self._chunk_size)
        else: ff_output = self.ff(norm_hidden_states)
        ff_output = gate_mlp.unsqueeze(1) * ff_output
        hidden_states = hidden_states + ff_output
        if self.context_pre_only: encoder_hidden_states = None
        else:
            context_attn_output = c_gate_msa.unsqueeze(1) * context_attn_output
            encoder_hidden_states = encoder_hidden_states + context_attn_output
            norm_encoder_hidden_states = self.norm2_context(encoder_hidden_states)
            norm_encoder_hidden_states = norm_encoder_hidden_states * (1 + c_scale_mlp[:, None]) + c_shift_mlp[:, None]
            if self._chunk_size is not None: context_ff_output = _chunked_feed_forward(self.ff_context, norm_encoder_hidden_states, self._chunk_dim, self._chunk_size)
            else: context_ff_output = self.ff_context(norm_encoder_hidden_states)
            encoder_hidden_states = encoder_hidden_states + c_gate_mlp.unsqueeze(1) * context_ff_output
        return (encoder_hidden_states, hidden_states)
@maybe_allow_in_graph
class BasicTransformerBlock(nn.Module):
    def __init__(self, dim: int, num_attention_heads: int, attention_head_dim: int, dropout=0.0, cross_attention_dim: Optional[int]=None,
    activation_fn: str='geglu', num_embeds_ada_norm: Optional[int]=None, attention_bias: bool=False, only_cross_attention: bool=False, double_self_attention: bool=False,
    upcast_attention: bool=False, norm_elementwise_affine: bool=True, norm_type: str='layer_norm', norm_eps: float=1e-05, final_dropout: bool=False, attention_type: str='default',
    positional_embeddings: Optional[str]=None, num_positional_embeddings: Optional[int]=None, ada_norm_continous_conditioning_embedding_dim: Optional[int]=None,
    ada_norm_bias: Optional[int]=None, ff_inner_dim: Optional[int]=None, ff_bias: bool=True, attention_out_bias: bool=True):
        super().__init__()
        self.dim = dim
        self.num_attention_heads = num_attention_heads
        self.attention_head_dim = attention_head_dim
        self.dropout = dropout
        self.cross_attention_dim = cross_attention_dim
        self.activation_fn = activation_fn
        self.attention_bias = attention_bias
        self.double_self_attention = double_self_attention
        self.norm_elementwise_affine = norm_elementwise_affine
        self.positional_embeddings = positional_embeddings
        self.num_positional_embeddings = num_positional_embeddings
        self.only_cross_attention = only_cross_attention
        self.use_ada_layer_norm_zero = num_embeds_ada_norm is not None and norm_type == 'ada_norm_zero'
        self.use_ada_layer_norm = num_embeds_ada_norm is not None and norm_type == 'ada_norm'
        self.use_ada_layer_norm_single = norm_type == 'ada_norm_single'
        self.use_layer_norm = norm_type == 'layer_norm'
        self.use_ada_layer_norm_continuous = norm_type == 'ada_norm_continuous'
        if norm_type in ('ada_norm', 'ada_norm_zero') and num_embeds_ada_norm is None: raise ValueError(f'`norm_type` is set to {norm_type}, but `num_embeds_ada_norm` is not defined. Please make sure to define `num_embeds_ada_norm` if setting `norm_type` to {norm_type}.')
        self.norm_type = norm_type
        self.num_embeds_ada_norm = num_embeds_ada_norm
        if positional_embeddings and num_positional_embeddings is None: raise ValueError('If `positional_embedding` type is defined, `num_positition_embeddings` must also be defined.')
        if positional_embeddings == 'sinusoidal': self.pos_embed = SinusoidalPositionalEmbedding(dim, max_seq_length=num_positional_embeddings)
        else: self.pos_embed = None
        if norm_type == 'ada_norm': self.norm1 = AdaLayerNorm(dim, num_embeds_ada_norm)
        elif norm_type == 'ada_norm_zero': self.norm1 = AdaLayerNormZero(dim, num_embeds_ada_norm)
        elif norm_type == 'ada_norm_continuous': self.norm1 = AdaLayerNormContinuous(dim, ada_norm_continous_conditioning_embedding_dim, norm_elementwise_affine, norm_eps, ada_norm_bias, 'rms_norm')
        else: self.norm1 = nn.LayerNorm(dim, elementwise_affine=norm_elementwise_affine, eps=norm_eps)
        self.attn1 = Attention(query_dim=dim, heads=num_attention_heads, dim_head=attention_head_dim, dropout=dropout, bias=attention_bias, cross_attention_dim=cross_attention_dim if only_cross_attention else None,
        upcast_attention=upcast_attention, out_bias=attention_out_bias)
        if cross_attention_dim is not None or double_self_attention:
            if norm_type == 'ada_norm': self.norm2 = AdaLayerNorm(dim, num_embeds_ada_norm)
            elif norm_type == 'ada_norm_continuous': self.norm2 = AdaLayerNormContinuous(dim, ada_norm_continous_conditioning_embedding_dim, norm_elementwise_affine, norm_eps, ada_norm_bias, 'rms_norm')
            else: self.norm2 = nn.LayerNorm(dim, norm_eps, norm_elementwise_affine)
            self.attn2 = Attention(query_dim=dim, cross_attention_dim=cross_attention_dim if not double_self_attention else None, heads=num_attention_heads, dim_head=attention_head_dim, dropout=dropout,
            bias=attention_bias, upcast_attention=upcast_attention, out_bias=attention_out_bias)
        else:
            if norm_type == 'ada_norm_single': self.norm2 = nn.LayerNorm(dim, norm_eps, norm_elementwise_affine)
            else: self.norm2 = None
            self.attn2 = None
        if norm_type == 'ada_norm_continuous': self.norm3 = AdaLayerNormContinuous(dim, ada_norm_continous_conditioning_embedding_dim, norm_elementwise_affine, norm_eps, ada_norm_bias, 'layer_norm')
        elif norm_type in ['ada_norm_zero', 'ada_norm', 'layer_norm']: self.norm3 = nn.LayerNorm(dim, norm_eps, norm_elementwise_affine)
        elif norm_type == 'layer_norm_i2vgen': self.norm3 = None
        self.ff = FeedForward(dim, dropout=dropout, activation_fn=activation_fn, final_dropout=final_dropout, inner_dim=ff_inner_dim, bias=ff_bias)
        if attention_type == 'gated' or attention_type == 'gated-text-image': self.fuser = GatedSelfAttentionDense(dim, cross_attention_dim, num_attention_heads, attention_head_dim)
        if norm_type == 'ada_norm_single': self.scale_shift_table = nn.Parameter(torch.randn(6, dim) / dim ** 0.5)
        self._chunk_size = None
        self._chunk_dim = 0
    def set_chunk_feed_forward(self, chunk_size: Optional[int], dim: int=0):
        self._chunk_size = chunk_size
        self._chunk_dim = dim
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor]=None, encoder_hidden_states: Optional[torch.Tensor]=None, encoder_attention_mask: Optional[torch.Tensor]=None,
    timestep: Optional[torch.LongTensor]=None, cross_attention_kwargs: Dict[str, Any]=None, class_labels: Optional[torch.LongTensor]=None, added_cond_kwargs: Optional[Dict[str, torch.Tensor]]=None) -> torch.Tensor:
        batch_size = hidden_states.shape[0]
        if self.norm_type == 'ada_norm': norm_hidden_states = self.norm1(hidden_states, timestep)
        elif self.norm_type == 'ada_norm_zero': norm_hidden_states, gate_msa, shift_mlp, scale_mlp, gate_mlp = self.norm1(hidden_states, timestep, class_labels, hidden_dtype=hidden_states.dtype)
        elif self.norm_type in ['layer_norm', 'layer_norm_i2vgen']: norm_hidden_states = self.norm1(hidden_states)
        elif self.norm_type == 'ada_norm_continuous': norm_hidden_states = self.norm1(hidden_states, added_cond_kwargs['pooled_text_emb'])
        elif self.norm_type == 'ada_norm_single':
            shift_msa, scale_msa, gate_msa, shift_mlp, scale_mlp, gate_mlp = (self.scale_shift_table[None] + timestep.reshape(batch_size, 6, -1)).chunk(6, dim=1)
            norm_hidden_states = self.norm1(hidden_states)
            norm_hidden_states = norm_hidden_states * (1 + scale_msa) + shift_msa
        else: raise ValueError('Incorrect norm used')
        if self.pos_embed is not None: norm_hidden_states = self.pos_embed(norm_hidden_states)
        cross_attention_kwargs = cross_attention_kwargs.copy() if cross_attention_kwargs is not None else {}
        gligen_kwargs = cross_attention_kwargs.pop('gligen', None)
        attn_output = self.attn1(norm_hidden_states, encoder_hidden_states=encoder_hidden_states if self.only_cross_attention else None, attention_mask=attention_mask, **cross_attention_kwargs)
        if self.norm_type == 'ada_norm_zero': attn_output = gate_msa.unsqueeze(1) * attn_output
        elif self.norm_type == 'ada_norm_single': attn_output = gate_msa * attn_output
        hidden_states = attn_output + hidden_states
        if hidden_states.ndim == 4: hidden_states = hidden_states.squeeze(1)
        if gligen_kwargs is not None: hidden_states = self.fuser(hidden_states, gligen_kwargs['objs'])
        if self.attn2 is not None:
            if self.norm_type == 'ada_norm': norm_hidden_states = self.norm2(hidden_states, timestep)
            elif self.norm_type in ['ada_norm_zero', 'layer_norm', 'layer_norm_i2vgen']: norm_hidden_states = self.norm2(hidden_states)
            elif self.norm_type == 'ada_norm_single': norm_hidden_states = hidden_states
            elif self.norm_type == 'ada_norm_continuous': norm_hidden_states = self.norm2(hidden_states, added_cond_kwargs['pooled_text_emb'])
            else: raise ValueError('Incorrect norm')
            if self.pos_embed is not None and self.norm_type != 'ada_norm_single': norm_hidden_states = self.pos_embed(norm_hidden_states)
            attn_output = self.attn2(norm_hidden_states, encoder_hidden_states=encoder_hidden_states, attention_mask=encoder_attention_mask, **cross_attention_kwargs)
            hidden_states = attn_output + hidden_states
        if self.norm_type == 'ada_norm_continuous': norm_hidden_states = self.norm3(hidden_states, added_cond_kwargs['pooled_text_emb'])
        elif not self.norm_type == 'ada_norm_single': norm_hidden_states = self.norm3(hidden_states)
        if self.norm_type == 'ada_norm_zero': norm_hidden_states = norm_hidden_states * (1 + scale_mlp[:, None]) + shift_mlp[:, None]
        if self.norm_type == 'ada_norm_single':
            norm_hidden_states = self.norm2(hidden_states)
            norm_hidden_states = norm_hidden_states * (1 + scale_mlp) + shift_mlp
        if self._chunk_size is not None: ff_output = _chunked_feed_forward(self.ff, norm_hidden_states, self._chunk_dim, self._chunk_size)
        else: ff_output = self.ff(norm_hidden_states)
        if self.norm_type == 'ada_norm_zero': ff_output = gate_mlp.unsqueeze(1) * ff_output
        elif self.norm_type == 'ada_norm_single': ff_output = gate_mlp * ff_output
        hidden_states = ff_output + hidden_states
        if hidden_states.ndim == 4: hidden_states = hidden_states.squeeze(1)
        return hidden_states
class LuminaFeedForward(nn.Module):
    def __init__(self, dim: int, inner_dim: int, multiple_of: Optional[int]=256, ffn_dim_multiplier: Optional[float]=None):
        super().__init__()
        inner_dim = int(2 * inner_dim / 3)
        if ffn_dim_multiplier is not None: inner_dim = int(ffn_dim_multiplier * inner_dim)
        inner_dim = multiple_of * ((inner_dim + multiple_of - 1) // multiple_of)
        self.linear_1 = nn.Linear(dim, inner_dim, bias=False)
        self.linear_2 = nn.Linear(inner_dim, dim, bias=False)
        self.linear_3 = nn.Linear(dim, inner_dim, bias=False)
        self.silu = FP32SiLU()
    def forward(self, x): return self.linear_2(self.silu(self.linear_1(x)) * self.linear_3(x))
@maybe_allow_in_graph
class TemporalBasicTransformerBlock(nn.Module):
    def __init__(self, dim: int, time_mix_inner_dim: int, num_attention_heads: int, attention_head_dim: int, cross_attention_dim: Optional[int]=None):
        super().__init__()
        self.is_res = dim == time_mix_inner_dim
        self.norm_in = nn.LayerNorm(dim)
        self.ff_in = FeedForward(dim, dim_out=time_mix_inner_dim, activation_fn='geglu')
        self.norm1 = nn.LayerNorm(time_mix_inner_dim)
        self.attn1 = Attention(query_dim=time_mix_inner_dim, heads=num_attention_heads, dim_head=attention_head_dim, cross_attention_dim=None)
        if cross_attention_dim is not None:
            self.norm2 = nn.LayerNorm(time_mix_inner_dim)
            self.attn2 = Attention(query_dim=time_mix_inner_dim, cross_attention_dim=cross_attention_dim, heads=num_attention_heads, dim_head=attention_head_dim)
        else:
            self.norm2 = None
            self.attn2 = None
        self.norm3 = nn.LayerNorm(time_mix_inner_dim)
        self.ff = FeedForward(time_mix_inner_dim, activation_fn='geglu')
        self._chunk_size = None
        self._chunk_dim = None
    def set_chunk_feed_forward(self, chunk_size: Optional[int], **kwargs):
        self._chunk_size = chunk_size
        self._chunk_dim = 1
    def forward(self, hidden_states: torch.Tensor, num_frames: int, encoder_hidden_states: Optional[torch.Tensor]=None) -> torch.Tensor:
        batch_size = hidden_states.shape[0]
        batch_frames, seq_length, channels = hidden_states.shape
        batch_size = batch_frames // num_frames
        hidden_states = hidden_states[None, :].reshape(batch_size, num_frames, seq_length, channels)
        hidden_states = hidden_states.permute(0, 2, 1, 3)
        hidden_states = hidden_states.reshape(batch_size * seq_length, num_frames, channels)
        residual = hidden_states
        hidden_states = self.norm_in(hidden_states)
        if self._chunk_size is not None: hidden_states = _chunked_feed_forward(self.ff_in, hidden_states, self._chunk_dim, self._chunk_size)
        else: hidden_states = self.ff_in(hidden_states)
        if self.is_res: hidden_states = hidden_states + residual
        norm_hidden_states = self.norm1(hidden_states)
        attn_output = self.attn1(norm_hidden_states, encoder_hidden_states=None)
        hidden_states = attn_output + hidden_states
        if self.attn2 is not None:
            norm_hidden_states = self.norm2(hidden_states)
            attn_output = self.attn2(norm_hidden_states, encoder_hidden_states=encoder_hidden_states)
            hidden_states = attn_output + hidden_states
        norm_hidden_states = self.norm3(hidden_states)
        if self._chunk_size is not None: ff_output = _chunked_feed_forward(self.ff, norm_hidden_states, self._chunk_dim, self._chunk_size)
        else: ff_output = self.ff(norm_hidden_states)
        if self.is_res: hidden_states = ff_output + hidden_states
        else: hidden_states = ff_output
        hidden_states = hidden_states[None, :].reshape(batch_size, seq_length, num_frames, channels)
        hidden_states = hidden_states.permute(0, 2, 1, 3)
        hidden_states = hidden_states.reshape(batch_size * num_frames, seq_length, channels)
        return hidden_states
class SkipFFTransformerBlock(nn.Module):
    def __init__(self, dim: int, num_attention_heads: int, attention_head_dim: int, kv_input_dim: int, kv_input_dim_proj_use_bias: bool, dropout=0.0,
    cross_attention_dim: Optional[int]=None, attention_bias: bool=False, attention_out_bias: bool=True):
        super().__init__()
        if kv_input_dim != dim: self.kv_mapper = nn.Linear(kv_input_dim, dim, kv_input_dim_proj_use_bias)
        else: self.kv_mapper = None
        self.norm1 = RMSNorm(dim, 1e-06)
        self.attn1 = Attention(query_dim=dim, heads=num_attention_heads, dim_head=attention_head_dim, dropout=dropout, bias=attention_bias, cross_attention_dim=cross_attention_dim, out_bias=attention_out_bias)
        self.norm2 = RMSNorm(dim, 1e-06)
        self.attn2 = Attention(query_dim=dim, cross_attention_dim=cross_attention_dim, heads=num_attention_heads, dim_head=attention_head_dim, dropout=dropout, bias=attention_bias, out_bias=attention_out_bias)
    def forward(self, hidden_states, encoder_hidden_states, cross_attention_kwargs):
        cross_attention_kwargs = cross_attention_kwargs.copy() if cross_attention_kwargs is not None else {}
        if self.kv_mapper is not None: encoder_hidden_states = self.kv_mapper(F.silu(encoder_hidden_states))
        norm_hidden_states = self.norm1(hidden_states)
        attn_output = self.attn1(norm_hidden_states, encoder_hidden_states=encoder_hidden_states, **cross_attention_kwargs)
        hidden_states = attn_output + hidden_states
        norm_hidden_states = self.norm2(hidden_states)
        attn_output = self.attn2(norm_hidden_states, encoder_hidden_states=encoder_hidden_states, **cross_attention_kwargs)
        hidden_states = attn_output + hidden_states
        return hidden_states
@maybe_allow_in_graph
class FreeNoiseTransformerBlock(nn.Module):
    def __init__(self, dim: int, num_attention_heads: int, attention_head_dim: int, dropout: float=0.0, cross_attention_dim: Optional[int]=None, activation_fn: str='geglu',
    num_embeds_ada_norm: Optional[int]=None, attention_bias: bool=False, only_cross_attention: bool=False, double_self_attention: bool=False, upcast_attention: bool=False,
    norm_elementwise_affine: bool=True, norm_type: str='layer_norm', norm_eps: float=1e-05, final_dropout: bool=False, positional_embeddings: Optional[str]=None,
    num_positional_embeddings: Optional[int]=None, ff_inner_dim: Optional[int]=None, ff_bias: bool=True, attention_out_bias: bool=True, context_length: int=16, context_stride: int=4, weighting_scheme: str='pyramid'):
        super().__init__()
        self.dim = dim
        self.num_attention_heads = num_attention_heads
        self.attention_head_dim = attention_head_dim
        self.dropout = dropout
        self.cross_attention_dim = cross_attention_dim
        self.activation_fn = activation_fn
        self.attention_bias = attention_bias
        self.double_self_attention = double_self_attention
        self.norm_elementwise_affine = norm_elementwise_affine
        self.positional_embeddings = positional_embeddings
        self.num_positional_embeddings = num_positional_embeddings
        self.only_cross_attention = only_cross_attention
        self.set_free_noise_properties(context_length, context_stride, weighting_scheme)
        self.use_ada_layer_norm_zero = num_embeds_ada_norm is not None and norm_type == 'ada_norm_zero'
        self.use_ada_layer_norm = num_embeds_ada_norm is not None and norm_type == 'ada_norm'
        self.use_ada_layer_norm_single = norm_type == 'ada_norm_single'
        self.use_layer_norm = norm_type == 'layer_norm'
        self.use_ada_layer_norm_continuous = norm_type == 'ada_norm_continuous'
        if norm_type in ('ada_norm', 'ada_norm_zero') and num_embeds_ada_norm is None: raise ValueError(f'`norm_type` is set to {norm_type}, but `num_embeds_ada_norm` is not defined. Please make sure to define `num_embeds_ada_norm` if setting `norm_type` to {norm_type}.')
        self.norm_type = norm_type
        self.num_embeds_ada_norm = num_embeds_ada_norm
        if positional_embeddings and num_positional_embeddings is None: raise ValueError('If `positional_embedding` type is defined, `num_positition_embeddings` must also be defined.')
        if positional_embeddings == 'sinusoidal': self.pos_embed = SinusoidalPositionalEmbedding(dim, max_seq_length=num_positional_embeddings)
        else: self.pos_embed = None
        self.norm1 = nn.LayerNorm(dim, elementwise_affine=norm_elementwise_affine, eps=norm_eps)
        self.attn1 = Attention(query_dim=dim, heads=num_attention_heads, dim_head=attention_head_dim, dropout=dropout, bias=attention_bias,
        cross_attention_dim=cross_attention_dim if only_cross_attention else None, upcast_attention=upcast_attention, out_bias=attention_out_bias)
        if cross_attention_dim is not None or double_self_attention:
            self.norm2 = nn.LayerNorm(dim, norm_eps, norm_elementwise_affine)
            self.attn2 = Attention(query_dim=dim, cross_attention_dim=cross_attention_dim if not double_self_attention else None, heads=num_attention_heads,
            dim_head=attention_head_dim, dropout=dropout, bias=attention_bias, upcast_attention=upcast_attention, out_bias=attention_out_bias)
        self.ff = FeedForward(dim, dropout=dropout, activation_fn=activation_fn, final_dropout=final_dropout, inner_dim=ff_inner_dim, bias=ff_bias)
        self.norm3 = nn.LayerNorm(dim, norm_eps, norm_elementwise_affine)
        self._chunk_size = None
        self._chunk_dim = 0
    def _get_frame_indices(self, num_frames: int) -> List[Tuple[int, int]]:
        frame_indices = []
        for i in range(0, num_frames - self.context_length + 1, self.context_stride):
            window_start = i
            window_end = min(num_frames, i + self.context_length)
            frame_indices.append((window_start, window_end))
        return frame_indices
    def _get_frame_weights(self, num_frames: int, weighting_scheme: str='pyramid') -> List[float]:
        if weighting_scheme == 'flat': weights = [1.0] * num_frames
        elif weighting_scheme == 'pyramid':
            if num_frames % 2 == 0:
                mid = num_frames // 2
                weights = list(range(1, mid + 1))
                weights = weights + weights[::-1]
            else:
                mid = (num_frames + 1) // 2
                weights = list(range(1, mid))
                weights = weights + [mid] + weights[::-1]
        elif weighting_scheme == 'delayed_reverse_sawtooth':
            if num_frames % 2 == 0:
                mid = num_frames // 2
                weights = [0.01] * (mid - 1) + [mid]
                weights = weights + list(range(mid, 0, -1))
            else:
                mid = (num_frames + 1) // 2
                weights = [0.01] * mid
                weights = weights + list(range(mid, 0, -1))
        else: raise ValueError(f'Unsupported value for weighting_scheme={weighting_scheme}')
        return weights
    def set_free_noise_properties(self, context_length: int, context_stride: int, weighting_scheme: str='pyramid') -> None:
        self.context_length = context_length
        self.context_stride = context_stride
        self.weighting_scheme = weighting_scheme
    def set_chunk_feed_forward(self, chunk_size: Optional[int], dim: int=0) -> None:
        self._chunk_size = chunk_size
        self._chunk_dim = dim
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor]=None, encoder_hidden_states: Optional[torch.Tensor]=None, encoder_attention_mask: Optional[torch.Tensor]=None,
    cross_attention_kwargs: Dict[str, Any]=None, *args, **kwargs) -> torch.Tensor:
        cross_attention_kwargs = cross_attention_kwargs.copy() if cross_attention_kwargs is not None else {}
        device = hidden_states.device
        dtype = hidden_states.dtype
        num_frames = hidden_states.size(1)
        frame_indices = self._get_frame_indices(num_frames)
        frame_weights = self._get_frame_weights(self.context_length, self.weighting_scheme)
        frame_weights = torch.tensor(frame_weights, device=device, dtype=dtype).unsqueeze(0).unsqueeze(-1)
        is_last_frame_batch_complete = frame_indices[-1][1] == num_frames
        if not is_last_frame_batch_complete:
            if num_frames < self.context_length: raise ValueError(f'Expected num_frames={num_frames!r} to be greater or equal than self.context_length={self.context_length!r}')
            last_frame_batch_length = num_frames - frame_indices[-1][1]
            frame_indices.append((num_frames - self.context_length, num_frames))
        num_times_accumulated = torch.zeros((1, num_frames, 1), device=device)
        accumulated_values = torch.zeros_like(hidden_states)
        for i, (frame_start, frame_end) in enumerate(frame_indices):
            weights = torch.ones_like(num_times_accumulated[:, frame_start:frame_end])
            weights *= frame_weights
            hidden_states_chunk = hidden_states[:, frame_start:frame_end]
            norm_hidden_states = self.norm1(hidden_states_chunk)
            if self.pos_embed is not None: norm_hidden_states = self.pos_embed(norm_hidden_states)
            attn_output = self.attn1(norm_hidden_states, encoder_hidden_states=encoder_hidden_states if self.only_cross_attention else None, attention_mask=attention_mask, **cross_attention_kwargs)
            hidden_states_chunk = attn_output + hidden_states_chunk
            if hidden_states_chunk.ndim == 4: hidden_states_chunk = hidden_states_chunk.squeeze(1)
            if self.attn2 is not None:
                norm_hidden_states = self.norm2(hidden_states_chunk)
                if self.pos_embed is not None and self.norm_type != 'ada_norm_single': norm_hidden_states = self.pos_embed(norm_hidden_states)
                attn_output = self.attn2(norm_hidden_states, encoder_hidden_states=encoder_hidden_states, attention_mask=encoder_attention_mask, **cross_attention_kwargs)
                hidden_states_chunk = attn_output + hidden_states_chunk
            if i == len(frame_indices) - 1 and (not is_last_frame_batch_complete):
                accumulated_values[:, -last_frame_batch_length:] += hidden_states_chunk[:, -last_frame_batch_length:] * weights[:, -last_frame_batch_length:]
                num_times_accumulated[:, -last_frame_batch_length:] += weights[:, -last_frame_batch_length]
            else:
                accumulated_values[:, frame_start:frame_end] += hidden_states_chunk * weights
                num_times_accumulated[:, frame_start:frame_end] += weights
        hidden_states = torch.cat([torch.where(num_times_split > 0, accumulated_split / num_times_split, accumulated_split) for accumulated_split, num_times_split in zip(accumulated_values.split(self.context_length, dim=1),
        num_times_accumulated.split(self.context_length, dim=1))], dim=1).to(dtype)
        norm_hidden_states = self.norm3(hidden_states)
        if self._chunk_size is not None: ff_output = _chunked_feed_forward(self.ff, norm_hidden_states, self._chunk_dim, self._chunk_size)
        else: ff_output = self.ff(norm_hidden_states)
        hidden_states = ff_output + hidden_states
        if hidden_states.ndim == 4: hidden_states = hidden_states.squeeze(1)
        return hidden_states
class FeedForward(nn.Module):
    def __init__(self, dim: int, dim_out: Optional[int]=None, mult: int=4, dropout: float=0.0, activation_fn: str='geglu', final_dropout: bool=False, inner_dim=None, bias: bool=True):
        super().__init__()
        if inner_dim is None: inner_dim = int(dim * mult)
        dim_out = dim_out if dim_out is not None else dim
        if activation_fn == 'gelu': act_fn = GELU(dim, inner_dim, bias=bias)
        if activation_fn == 'gelu-approximate': act_fn = GELU(dim, inner_dim, approximate='tanh', bias=bias)
        elif activation_fn == 'geglu': act_fn = GEGLU(dim, inner_dim, bias=bias)
        elif activation_fn == 'geglu-approximate': act_fn = ApproximateGELU(dim, inner_dim, bias=bias)
        elif activation_fn == 'swiglu': act_fn = SwiGLU(dim, inner_dim, bias=bias)
        elif activation_fn == 'linear-silu': act_fn = LinearActivation(dim, inner_dim, bias=bias, activation='silu')
        self.net = nn.ModuleList([])
        self.net.append(act_fn)
        self.net.append(nn.Dropout(dropout))
        self.net.append(nn.Linear(inner_dim, dim_out, bias=bias))
        if final_dropout: self.net.append(nn.Dropout(dropout))
    def forward(self, hidden_states: torch.Tensor, *args, **kwargs) -> torch.Tensor:
        if len(args) > 0 or kwargs.get('scale', None) is not None:
            deprecation_message = 'The `scale` argument is deprecated and will be ignored. Please remove it, as passing it will raise an error in the future. `scale` should directly be passed while calling the underlying pipeline component i.e., via `cross_attention_kwargs`.'
            deprecate('scale', '1.0.0', deprecation_message)
        for module in self.net: hidden_states = module(hidden_states)
        return hidden_states
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
