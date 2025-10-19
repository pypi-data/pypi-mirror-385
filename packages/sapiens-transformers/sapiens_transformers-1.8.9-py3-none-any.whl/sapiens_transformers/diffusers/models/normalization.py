'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from .embeddings import CombinedTimestepLabelEmbeddings, PixArtAlphaCombinedTimestepSizeEmbeddings
from typing import Dict, Optional, Tuple
from .activations import get_activation
from ..utils import is_torch_version
import torch.nn.functional as F
import torch.nn as nn
import numbers
import torch
class AdaLayerNorm(nn.Module):
    def __init__(self, embedding_dim: int, num_embeddings: Optional[int]=None, output_dim: Optional[int]=None, norm_elementwise_affine: bool=False, norm_eps: float=1e-05, chunk_dim: int=0):
        super().__init__()
        self.chunk_dim = chunk_dim
        output_dim = output_dim or embedding_dim * 2
        if num_embeddings is not None: self.emb = nn.Embedding(num_embeddings, embedding_dim)
        else: self.emb = None
        self.silu = nn.SiLU()
        self.linear = nn.Linear(embedding_dim, output_dim)
        self.norm = nn.LayerNorm(output_dim // 2, norm_eps, norm_elementwise_affine)
    def forward(self, x: torch.Tensor, timestep: Optional[torch.Tensor]=None, temb: Optional[torch.Tensor]=None) -> torch.Tensor:
        if self.emb is not None: temb = self.emb(timestep)
        temb = self.linear(self.silu(temb))
        if self.chunk_dim == 1:
            shift, scale = temb.chunk(2, dim=1)
            shift = shift[:, None, :]
            scale = scale[:, None, :]
        else: scale, shift = temb.chunk(2, dim=0)
        x = self.norm(x) * (1 + scale) + shift
        return x
class FP32LayerNorm(nn.LayerNorm):
    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        origin_dtype = inputs.dtype
        return F.layer_norm(inputs.float(), self.normalized_shape, self.weight.float() if self.weight is not None else None, self.bias.float() if self.bias is not None else None, self.eps).to(origin_dtype)
class SD35AdaLayerNormZeroX(nn.Module):
    def __init__(self, embedding_dim: int, norm_type: str='layer_norm', bias: bool=True) -> None:
        super().__init__()
        self.silu = nn.SiLU()
        self.linear = nn.Linear(embedding_dim, 9 * embedding_dim, bias=bias)
        if norm_type == 'layer_norm': self.norm = nn.LayerNorm(embedding_dim, elementwise_affine=False, eps=1e-06)
        else: raise ValueError(f"Unsupported `norm_type` ({norm_type}) provided. Supported ones are: 'layer_norm'.")
    def forward(self, hidden_states: torch.Tensor, emb: Optional[torch.Tensor]=None) -> Tuple[torch.Tensor, ...]:
        emb = self.linear(self.silu(emb))
        shift_msa, scale_msa, gate_msa, shift_mlp, scale_mlp, gate_mlp, shift_msa2, scale_msa2, gate_msa2 = emb.chunk(9, dim=1)
        norm_hidden_states = self.norm(hidden_states)
        hidden_states = norm_hidden_states * (1 + scale_msa[:, None]) + shift_msa[:, None]
        norm_hidden_states2 = norm_hidden_states * (1 + scale_msa2[:, None]) + shift_msa2[:, None]
        return (hidden_states, gate_msa, shift_mlp, scale_mlp, gate_mlp, norm_hidden_states2, gate_msa2)
class AdaLayerNormZero(nn.Module):
    def __init__(self, embedding_dim: int, num_embeddings: Optional[int]=None, norm_type='layer_norm', bias=True):
        super().__init__()
        if num_embeddings is not None: self.emb = CombinedTimestepLabelEmbeddings(num_embeddings, embedding_dim)
        else: self.emb = None
        self.silu = nn.SiLU()
        self.linear = nn.Linear(embedding_dim, 6 * embedding_dim, bias=bias)
        if norm_type == 'layer_norm': self.norm = nn.LayerNorm(embedding_dim, elementwise_affine=False, eps=1e-06)
        elif norm_type == 'fp32_layer_norm': self.norm = FP32LayerNorm(embedding_dim, elementwise_affine=False, bias=False)
        else: raise ValueError(f"Unsupported `norm_type` ({norm_type}) provided. Supported ones are: 'layer_norm', 'fp32_layer_norm'.")
    def forward(self, x: torch.Tensor, timestep: Optional[torch.Tensor]=None, class_labels: Optional[torch.LongTensor]=None, hidden_dtype: Optional[torch.dtype]=None,
    emb: Optional[torch.Tensor]=None) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        if self.emb is not None: emb = self.emb(timestep, class_labels, hidden_dtype=hidden_dtype)
        emb = self.linear(self.silu(emb))
        shift_msa, scale_msa, gate_msa, shift_mlp, scale_mlp, gate_mlp = emb.chunk(6, dim=1)
        x = self.norm(x) * (1 + scale_msa[:, None]) + shift_msa[:, None]
        return (x, gate_msa, shift_mlp, scale_mlp, gate_mlp)
class AdaLayerNormZeroSingle(nn.Module):
    def __init__(self, embedding_dim: int, norm_type='layer_norm', bias=True):
        super().__init__()
        self.silu = nn.SiLU()
        self.linear = nn.Linear(embedding_dim, 3 * embedding_dim, bias=bias)
        if norm_type == 'layer_norm': self.norm = nn.LayerNorm(embedding_dim, elementwise_affine=False, eps=1e-06)
        else: raise ValueError(f"Unsupported `norm_type` ({norm_type}) provided. Supported ones are: 'layer_norm', 'fp32_layer_norm'.")
    def forward(self, x: torch.Tensor, emb: Optional[torch.Tensor]=None) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        emb = self.linear(self.silu(emb))
        shift_msa, scale_msa, gate_msa = emb.chunk(3, dim=1)
        x = self.norm(x) * (1 + scale_msa[:, None]) + shift_msa[:, None]
        return (x, gate_msa)
class LuminaRMSNormZero(nn.Module):
    def __init__(self, embedding_dim: int, norm_eps: float, norm_elementwise_affine: bool):
        super().__init__()
        self.silu = nn.SiLU()
        self.linear = nn.Linear(min(embedding_dim, 1024), 4 * embedding_dim, bias=True)
        self.norm = RMSNorm(embedding_dim, eps=norm_eps, elementwise_affine=norm_elementwise_affine)
    def forward(self, x: torch.Tensor, emb: Optional[torch.Tensor]=None) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        emb = self.linear(self.silu(emb))
        scale_msa, gate_msa, scale_mlp, gate_mlp = emb.chunk(4, dim=1)
        x = self.norm(x) * (1 + scale_msa[:, None])
        return (x, gate_msa, scale_mlp, gate_mlp)
class AdaLayerNormSingle(nn.Module):
    def __init__(self, embedding_dim: int, use_additional_conditions: bool=False):
        super().__init__()
        self.emb = PixArtAlphaCombinedTimestepSizeEmbeddings(embedding_dim, size_emb_dim=embedding_dim // 3, use_additional_conditions=use_additional_conditions)
        self.silu = nn.SiLU()
        self.linear = nn.Linear(embedding_dim, 6 * embedding_dim, bias=True)
    def forward(self, timestep: torch.Tensor, added_cond_kwargs: Optional[Dict[str, torch.Tensor]]=None, batch_size: Optional[int]=None,
    hidden_dtype: Optional[torch.dtype]=None) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        added_cond_kwargs = added_cond_kwargs or {'resolution': None, 'aspect_ratio': None}
        embedded_timestep = self.emb(timestep, **added_cond_kwargs, batch_size=batch_size, hidden_dtype=hidden_dtype)
        return (self.linear(self.silu(embedded_timestep)), embedded_timestep)
class AdaGroupNorm(nn.Module):
    def __init__(self, embedding_dim: int, out_dim: int, num_groups: int, act_fn: Optional[str]=None, eps: float=1e-05):
        super().__init__()
        self.num_groups = num_groups
        self.eps = eps
        if act_fn is None: self.act = None
        else: self.act = get_activation(act_fn)
        self.linear = nn.Linear(embedding_dim, out_dim * 2)
    def forward(self, x: torch.Tensor, emb: torch.Tensor) -> torch.Tensor:
        if self.act: emb = self.act(emb)
        emb = self.linear(emb)
        emb = emb[:, :, None, None]
        scale, shift = emb.chunk(2, dim=1)
        x = F.group_norm(x, self.num_groups, eps=self.eps)
        x = x * (1 + scale) + shift
        return x
class AdaLayerNormContinuous(nn.Module):
    def __init__(self, embedding_dim: int, conditioning_embedding_dim: int, elementwise_affine=True, eps=1e-05, bias=True, norm_type='layer_norm'):
        super().__init__()
        self.silu = nn.SiLU()
        self.linear = nn.Linear(conditioning_embedding_dim, embedding_dim * 2, bias=bias)
        if norm_type == 'layer_norm': self.norm = LayerNorm(embedding_dim, eps, elementwise_affine, bias)
        elif norm_type == 'rms_norm': self.norm = RMSNorm(embedding_dim, eps, elementwise_affine)
        else: raise ValueError(f'unknown norm_type {norm_type}')
    def forward(self, x: torch.Tensor, conditioning_embedding: torch.Tensor) -> torch.Tensor:
        emb = self.linear(self.silu(conditioning_embedding).to(x.dtype))
        scale, shift = torch.chunk(emb, 2, dim=1)
        x = self.norm(x) * (1 + scale)[:, None, :] + shift[:, None, :]
        return x
class LuminaLayerNormContinuous(nn.Module):
    def __init__(self, embedding_dim: int, conditioning_embedding_dim: int, elementwise_affine=True, eps=1e-05, bias=True, norm_type='layer_norm', out_dim: Optional[int]=None):
        super().__init__()
        self.silu = nn.SiLU()
        self.linear_1 = nn.Linear(conditioning_embedding_dim, embedding_dim, bias=bias)
        if norm_type == 'layer_norm': self.norm = LayerNorm(embedding_dim, eps, elementwise_affine, bias)
        elif norm_type == 'rms_norm': self.norm = RMSNorm(embedding_dim, eps=eps, elementwise_affine=elementwise_affine)
        else: raise ValueError(f'unknown norm_type {norm_type}')
        self.linear_2 = None
        if out_dim is not None: self.linear_2 = nn.Linear(embedding_dim, out_dim, bias=bias)
    def forward(self, x: torch.Tensor, conditioning_embedding: torch.Tensor) -> torch.Tensor:
        emb = self.linear_1(self.silu(conditioning_embedding).to(x.dtype))
        scale = emb
        x = self.norm(x) * (1 + scale)[:, None, :]
        if self.linear_2 is not None: x = self.linear_2(x)
        return x
class CogView3PlusAdaLayerNormZeroTextImage(nn.Module):
    def __init__(self, embedding_dim: int, dim: int):
        super().__init__()
        self.silu = nn.SiLU()
        self.linear = nn.Linear(embedding_dim, 12 * dim, bias=True)
        self.norm_x = nn.LayerNorm(dim, elementwise_affine=False, eps=1e-05)
        self.norm_c = nn.LayerNorm(dim, elementwise_affine=False, eps=1e-05)
    def forward(self, x: torch.Tensor, context: torch.Tensor, emb: Optional[torch.Tensor]=None) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        emb = self.linear(self.silu(emb))
        shift_msa, scale_msa, gate_msa, shift_mlp, scale_mlp, gate_mlp, c_shift_msa, c_scale_msa, c_gate_msa, c_shift_mlp, c_scale_mlp, c_gate_mlp = emb.chunk(12, dim=1)
        normed_x = self.norm_x(x)
        normed_context = self.norm_c(context)
        x = normed_x * (1 + scale_msa[:, None]) + shift_msa[:, None]
        context = normed_context * (1 + c_scale_msa[:, None]) + c_shift_msa[:, None]
        return (x, gate_msa, shift_mlp, scale_mlp, gate_mlp, context, c_gate_msa, c_shift_mlp, c_scale_mlp, c_gate_mlp)
class CogVideoXLayerNormZero(nn.Module):
    def __init__(self, conditioning_dim: int, embedding_dim: int, elementwise_affine: bool=True, eps: float=1e-05, bias: bool=True) -> None:
        super().__init__()
        self.silu = nn.SiLU()
        self.linear = nn.Linear(conditioning_dim, 6 * embedding_dim, bias=bias)
        self.norm = nn.LayerNorm(embedding_dim, eps=eps, elementwise_affine=elementwise_affine)
    def forward(self, hidden_states: torch.Tensor, encoder_hidden_states: torch.Tensor, temb: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        shift, scale, gate, enc_shift, enc_scale, enc_gate = self.linear(self.silu(temb)).chunk(6, dim=1)
        hidden_states = self.norm(hidden_states) * (1 + scale)[:, None, :] + shift[:, None, :]
        encoder_hidden_states = self.norm(encoder_hidden_states) * (1 + enc_scale)[:, None, :] + enc_shift[:, None, :]
        return (hidden_states, encoder_hidden_states, gate[:, None, :], enc_gate[:, None, :])
if is_torch_version('>=', '2.1.0'): LayerNorm = nn.LayerNorm
else:
    class LayerNorm(nn.Module):
        def __init__(self, dim, eps: float=1e-05, elementwise_affine: bool=True, bias: bool=True):
            super().__init__()
            self.eps = eps
            if isinstance(dim, numbers.Integral): dim = (dim,)
            self.dim = torch.Size(dim)
            if elementwise_affine:
                self.weight = nn.Parameter(torch.ones(dim))
                self.bias = nn.Parameter(torch.zeros(dim)) if bias else None
            else:
                self.weight = None
                self.bias = None
        def forward(self, input): return F.layer_norm(input, self.dim, self.weight, self.bias, self.eps)
class RMSNorm(nn.Module):
    def __init__(self, dim, eps: float, elementwise_affine: bool=True, bias: bool=False):
        super().__init__()
        self.eps = eps
        self.elementwise_affine = elementwise_affine
        if isinstance(dim, numbers.Integral): dim = (dim,)
        self.dim = torch.Size(dim)
        self.weight = None
        self.bias = None
        if elementwise_affine:
            self.weight = nn.Parameter(torch.ones(dim))
            if bias: self.bias = nn.Parameter(torch.zeros(dim))
    def forward(self, hidden_states):
        input_dtype = hidden_states.dtype
        variance = hidden_states.to(torch.float32).pow(2).mean(-1, keepdim=True)
        hidden_states = hidden_states * torch.rsqrt(variance + self.eps)
        if self.weight is not None:
            if self.weight.dtype in [torch.float16, torch.bfloat16]: hidden_states = hidden_states.to(self.weight.dtype)
            hidden_states = hidden_states * self.weight
            if self.bias is not None: hidden_states = hidden_states + self.bias
        else: hidden_states = hidden_states.to(input_dtype)
        return hidden_states
class MochiRMSNorm(nn.Module):
    def __init__(self, dim, eps: float, elementwise_affine: bool=True):
        super().__init__()
        self.eps = eps
        if isinstance(dim, numbers.Integral): dim = (dim,)
        self.dim = torch.Size(dim)
        if elementwise_affine: self.weight = nn.Parameter(torch.ones(dim))
        else: self.weight = None
    def forward(self, hidden_states):
        input_dtype = hidden_states.dtype
        variance = hidden_states.to(torch.float32).pow(2).mean(-1, keepdim=True)
        hidden_states = hidden_states * torch.rsqrt(variance + self.eps)
        if self.weight is not None: hidden_states = hidden_states * self.weight
        hidden_states = hidden_states.to(input_dtype)
        return hidden_states
class GlobalResponseNorm(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.gamma = nn.Parameter(torch.zeros(1, 1, 1, dim))
        self.beta = nn.Parameter(torch.zeros(1, 1, 1, dim))
    def forward(self, x):
        gx = torch.norm(x, p=2, dim=(1, 2), keepdim=True)
        nx = gx / (gx.mean(dim=-1, keepdim=True) + 1e-06)
        return self.gamma * (x * nx) + self.beta + x
class LpNorm(nn.Module):
    def __init__(self, p: int=2, dim: int=-1, eps: float=1e-12):
        super().__init__()
        self.p = p
        self.dim = dim
        self.eps = eps
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor: return F.normalize(hidden_states, p=self.p, dim=self.dim, eps=self.eps)
class SAPI5AdaLayerNormZeroX(nn.Module):
    def __init__(self, embedding_dim: int, norm_type: str='layer_norm', bias: bool=True) -> None:
        super().__init__()
        self.silu = nn.SiLU()
        self.linear = nn.Linear(embedding_dim, 9 * embedding_dim, bias=bias)
        if norm_type == 'layer_norm': self.norm = nn.LayerNorm(embedding_dim, elementwise_affine=False, eps=1e-06)
        else: raise ValueError(f"Unsupported `norm_type` ({norm_type}) provided. Supported ones are: 'layer_norm'.")
    def forward(self, hidden_states: torch.Tensor, emb: Optional[torch.Tensor]=None) -> Tuple[torch.Tensor, ...]:
        emb = self.linear(self.silu(emb))
        shift_msa, scale_msa, gate_msa, shift_mlp, scale_mlp, gate_mlp, shift_msa2, scale_msa2, gate_msa2 = emb.chunk(9, dim=1)
        norm_hidden_states = self.norm(hidden_states)
        hidden_states = norm_hidden_states * (1 + scale_msa[:, None]) + shift_msa[:, None]
        norm_hidden_states2 = norm_hidden_states * (1 + scale_msa2[:, None]) + shift_msa2[:, None]
        return (hidden_states, gate_msa, shift_mlp, scale_mlp, gate_mlp, norm_hidden_states2, gate_msa2)
def get_normalization(norm_type: str='batch_norm', num_features: Optional[int]=None, eps: float=1e-05, elementwise_affine: bool=True, bias: bool=True) -> nn.Module:
    if norm_type == 'rms_norm': norm = RMSNorm(num_features, eps=eps, elementwise_affine=elementwise_affine, bias=bias)
    elif norm_type == 'layer_norm': norm = nn.LayerNorm(num_features, eps=eps, elementwise_affine=elementwise_affine, bias=bias)
    elif norm_type == 'batch_norm': norm = nn.BatchNorm2d(num_features, eps=eps, affine=elementwise_affine)
    else: raise ValueError(f'norm_type={norm_type!r} is not supported.')
    return norm
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
