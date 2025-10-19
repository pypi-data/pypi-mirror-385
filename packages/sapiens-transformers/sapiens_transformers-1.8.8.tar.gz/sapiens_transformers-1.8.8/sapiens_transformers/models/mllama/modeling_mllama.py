"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from typing import List, Optional, Tuple, Union
import torch
import torch.nn.functional as F
import torch.utils.checkpoint
from torch import nn
from torch.nn import CrossEntropyLoss
from ... import PreTrainedModel
from ...activations import ACT2FN
from ...cache_utils import Cache
from ...generation import GenerationMixin
from ...modeling_attn_mask_utils import AttentionMaskConverter
from ...modeling_outputs import BaseModelOutput, BaseModelOutputWithPast, CausalLMOutputWithPast
from ...modeling_rope_utils import ROPE_INIT_FUNCTIONS
from ...utils import (add_start_docstrings, add_start_docstrings_to_model_forward, logging, replace_return_docstrings)
from .configuration_mllama import MllamaConfig, MllamaTextConfig, MllamaVisionConfig
logger = logging.get_logger(__name__)
def _prepare_4d_causal_attention_mask_with_cache_position(attention_mask: torch.Tensor, sequence_length: int, target_length: int, dtype: torch.dtype, device: torch.device,
min_dtype: float, cache_position: torch.Tensor, batch_size: int):
    if attention_mask is not None and attention_mask.dim() == 4: causal_mask = attention_mask
    else:
        causal_mask = torch.full((sequence_length, target_length), fill_value=min_dtype, dtype=dtype, device=device)
        if sequence_length != 1: causal_mask = torch.triu(causal_mask, diagonal=1)
        causal_mask *= torch.arange(target_length, device=device) > cache_position.reshape(-1, 1)
        causal_mask = causal_mask[None, None, :, :].expand(batch_size, 1, -1, -1)
        if attention_mask is not None:
            causal_mask = causal_mask.clone()
            mask_length = attention_mask.shape[-1]
            padding_mask = causal_mask[:, :, :, :mask_length] + attention_mask[:, None, None, :]
            padding_mask = padding_mask == 0
            causal_mask[:, :, :, :mask_length] = causal_mask[:, :, :, :mask_length].masked_fill(padding_mask, min_dtype)
    return causal_mask
def _prepare_cross_attention_mask(cross_attention_mask: torch.Tensor, num_vision_tokens: int, dtype: str) -> Tuple[torch.Tensor, torch.Tensor]:
    batch_size, text_total_length, *_ = cross_attention_mask.shape
    cross_attention_mask = cross_attention_mask.repeat_interleave(num_vision_tokens, dim=3)
    cross_attention_mask = cross_attention_mask.view(batch_size, text_total_length, -1)
    cross_attention_mask = cross_attention_mask.unsqueeze(1)
    inverted_cross_attn_mask = (1.0 - cross_attention_mask).to(dtype)
    cross_attention_mask = inverted_cross_attn_mask.masked_fill(inverted_cross_attn_mask.to(torch.bool), torch.finfo(dtype).min)
    negative_inf_value = torch.finfo(dtype).min
    full_text_row_masked_out_mask = ((cross_attention_mask != negative_inf_value).any(dim=-1).type_as(cross_attention_mask)[..., None])
    cross_attention_mask *= full_text_row_masked_out_mask
    return cross_attention_mask, full_text_row_masked_out_mask
def _prepare_aspect_ratio_attention_mask(aspect_ratio_mask: torch.Tensor, num_patches: int, target_length: int, dtype: torch.dtype) -> torch.Tensor:
    batch_size, max_num_tiles = aspect_ratio_mask.shape
    attention_mask = aspect_ratio_mask.view(batch_size, max_num_tiles, 1, 1).to(dtype)
    attention_mask = attention_mask.repeat(1, 1, target_length, 1)
    pad_patches = target_length - num_patches
    attention_mask[:, :, -pad_patches:] = 0
    attention_mask = 1 - attention_mask
    attention_mask = attention_mask.reshape(batch_size, max_num_tiles * target_length, 1)
    attention_mask = attention_mask @ attention_mask.transpose(-1, -2) * torch.finfo(dtype).min
    attention_mask = attention_mask.unsqueeze(1)
    return attention_mask
class MllamaPrecomputedAspectRatioEmbedding(nn.Module):
    def __init__(self, config: MllamaVisionConfig, is_gated: bool = True):
        super().__init__()
        self.max_num_tiles = config.max_num_tiles
        self.hidden_size = config.hidden_size
        self.max_aspect_ratio_id = config.max_aspect_ratio_id
        self.is_gated = is_gated
        self.embedding = nn.Embedding(self.max_aspect_ratio_id + 1, self.max_num_tiles * self.hidden_size)
        if is_gated: self.gate = nn.Parameter(torch.zeros(1))
    def forward(self, hidden_state: torch.Tensor, aspect_ratio_ids: torch.Tensor) -> torch.Tensor:
        embeddings = self.embedding(aspect_ratio_ids)
        embeddings = embeddings.reshape(-1, self.max_num_tiles, 1, self.hidden_size)
        if self.is_gated: embeddings = embeddings * self.gate.tanh()
        hidden_state = hidden_state + embeddings
        return hidden_state
class MllamaPrecomputedPositionEmbedding(nn.Module):
    def __init__(self, config: MllamaVisionConfig):
        super().__init__()
        self.max_num_tiles = config.max_num_tiles
        self.max_aspect_ratio_id = config.max_aspect_ratio_id
        self.num_patches = (config.image_size // config.patch_size) ** 2 + 1
        self.hidden_size = config.hidden_size
        self.scale = config.hidden_size**-0.5
        self.gate = nn.Parameter(torch.zeros(1))
        position_embedding = torch.randn(self.num_patches, self.hidden_size)
        self.embedding = nn.Parameter(self.scale * position_embedding)
        self.tile_embedding = nn.Embedding(self.max_aspect_ratio_id + 1, self.max_num_tiles * self.num_patches * self.hidden_size)
    def forward(self, hidden_state: torch.Tensor, aspect_ratio_ids: torch.Tensor) -> torch.Tensor:
        gated_position_embedding = (1 - self.gate.tanh()) * self.embedding
        hidden_state = hidden_state + gated_position_embedding.view(1, 1, self.num_patches, self.hidden_size)
        tile_position_embedding = self.tile_embedding(aspect_ratio_ids)
        batch_size = hidden_state.shape[0]
        tile_position_embedding = tile_position_embedding.reshape(batch_size, self.max_num_tiles, self.num_patches, self.hidden_size)
        gated_tile_position_embedding = self.gate.tanh() * tile_position_embedding
        hidden_state = hidden_state + gated_tile_position_embedding
        return hidden_state
class MllamaVisionMLP(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.activation_fn = ACT2FN[config.hidden_act]
        self.fc1 = nn.Linear(config.hidden_size, config.intermediate_size)
        self.fc2 = nn.Linear(config.intermediate_size, config.hidden_size)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.fc1(hidden_states)
        hidden_states = self.activation_fn(hidden_states)
        hidden_states = self.fc2(hidden_states)
        return hidden_states
class MllamaVisionAttention(nn.Module):
    def __init__(self, config: MllamaVisionConfig):
        super().__init__()
        self.embed_dim = config.hidden_size
        self.num_heads = config.attention_heads
        self.head_dim = config.hidden_size // config.attention_heads
        self.q_proj = nn.Linear(self.embed_dim, self.num_heads * self.head_dim, bias=False)
        self.k_proj = nn.Linear(self.embed_dim, self.num_heads * self.head_dim, bias=False)
        self.v_proj = nn.Linear(self.embed_dim, self.num_heads * self.head_dim, bias=False)
        self.o_proj = nn.Linear(self.num_heads * self.head_dim, self.embed_dim, bias=False)
    def forward(self, hidden_state: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, output_attentions: bool = None) -> torch.Tensor:
        query = self.q_proj(hidden_state)
        key = self.k_proj(hidden_state)
        value = self.v_proj(hidden_state)
        batch_size, q_seq_len, _ = query.shape
        _, kv_seq_len, _ = key.shape
        query = query.view(batch_size, q_seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        key = key.view(batch_size, kv_seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        value = value.view(batch_size, kv_seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        attn_weights = torch.matmul(query, key.transpose(2, 3)) / math.sqrt(self.head_dim)
        if attention_mask is not None:
            causal_mask = attention_mask[:, :, :, : key.shape[-2]]
            attn_weights = attn_weights + causal_mask
        attn_weights = nn.functional.softmax(attn_weights, dim=-1, dtype=torch.float32).to(query.dtype)
        attn_output = torch.matmul(attn_weights, value)
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.reshape(batch_size, q_seq_len, -1)
        output = self.o_proj(attn_output)
        if not output_attentions: attn_weights = None
        return output, attn_weights
class MllamaVisionSdpaAttention(MllamaVisionAttention):
    def forward(self, hidden_state: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, output_attentions: bool = None) -> torch.Tensor:
        if output_attentions:
            logger.warning_once("MllamaModel is using MllamaVisionSdpaAttention, but `torch.nn.functional.scaled_dot_product_attention` does not support `output_attentions=True`. Falling back to the manual attention implementation, "+'but specifying the manual implementation will be required from sapiens_transformers version v5.0.0 onwards. This warning can be removed using the argument `attn_implementation="eager"` when loading the model.')
            return super().forward(hidden_state=hidden_state, attention_mask=attention_mask, output_attentions=output_attentions)
        query = self.q_proj(hidden_state)
        key = self.k_proj(hidden_state)
        value = self.v_proj(hidden_state)
        batch_size, q_seq_len, _ = query.shape
        _, kv_seq_len, _ = key.shape
        query = query.view(batch_size, q_seq_len, self.num_heads, self.head_dim)
        key = key.view(batch_size, kv_seq_len, self.num_heads, self.head_dim)
        value = value.view(batch_size, kv_seq_len, self.num_heads, self.head_dim)
        query = query.transpose(1, 2)
        key = key.transpose(1, 2)
        value = value.transpose(1, 2)
        attn_output = F.scaled_dot_product_attention(query, key, value, attn_mask=attention_mask)
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.reshape(batch_size, q_seq_len, -1)
        output = self.o_proj(attn_output)
        return output, None
MLLAMA_VISION_ATTENTION_CLASSES = {"eager": MllamaVisionAttention, "sdpa": MllamaVisionSdpaAttention}
class MllamaVisionEncoderLayer(nn.Module):
    def __init__(self, config: MllamaVisionConfig, is_gated: bool = False):
        super().__init__()
        self.hidden_size = config.hidden_size
        self.num_attention_heads = config.attention_heads
        self.is_gated = is_gated
        self.intermediate_size = config.intermediate_size
        self.self_attn = MLLAMA_VISION_ATTENTION_CLASSES[config._attn_implementation](config)
        self.mlp = MllamaVisionMLP(config)
        self.input_layernorm = nn.LayerNorm(self.hidden_size, eps=config.norm_eps)
        self.post_attention_layernorm = nn.LayerNorm(self.hidden_size, eps=config.norm_eps)
        if is_gated:
            self.gate_attn = nn.Parameter(torch.ones(1) * math.pi / 4)
            self.gate_ffn = nn.Parameter(torch.ones(1) * math.pi / 4)
    def forward(self, hidden_state: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, output_attentions: bool = None):
        residual = hidden_state
        hidden_state = self.input_layernorm(hidden_state)
        hidden_state, attn_weights = self.self_attn(hidden_state, attention_mask=attention_mask)
        if self.is_gated: hidden_state = self.gate_attn.tanh() * hidden_state
        hidden_state = residual + hidden_state
        residual = hidden_state
        hidden_state = self.post_attention_layernorm(hidden_state)
        hidden_state = self.mlp(hidden_state)
        if self.is_gated: hidden_state = self.gate_ffn.tanh() * hidden_state
        hidden_state = residual + hidden_state
        outputs = (hidden_state,)
        if output_attentions: outputs += (attn_weights,)
        return outputs
class MllamaVisionEncoder(nn.Module):
    def __init__(self, config: MllamaVisionConfig, num_layers=32, is_gated=False):
        super().__init__()
        self.config = config
        self.layers = nn.ModuleList([MllamaVisionEncoderLayer(config, is_gated) for _ in range(num_layers)])
        self.gradient_checkpointing = False
        self.config = config
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutput]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        encoder_states = () if output_hidden_states else None
        all_attentions = () if output_attentions else None
        for encoder_layer in self.layers:
            if output_hidden_states: encoder_states = encoder_states + (hidden_states,)
            if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(encoder_layer.__call__, hidden_states, attention_mask, output_attentions)
            else: layer_outputs = encoder_layer(hidden_state=hidden_states, attention_mask=attention_mask, output_attentions=output_attentions)
            if output_attentions: all_attentions = all_attentions + (layer_outputs[1],)
            hidden_states = layer_outputs[0]
        if output_hidden_states: encoder_states = encoder_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, encoder_states, all_attentions] if v is not None)
        return BaseModelOutput(last_hidden_state=hidden_states, hidden_states=encoder_states, attentions=all_attentions)
class MllamaTextRMSNorm(nn.Module):
    def __init__(self, hidden_size, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size))
        self.variance_epsilon = eps
    def forward(self, hidden_states):
        input_dtype = hidden_states.dtype
        hidden_states = hidden_states.to(torch.float32)
        variance = hidden_states.pow(2).mean(-1, keepdim=True)
        hidden_states = hidden_states * torch.rsqrt(variance + self.variance_epsilon)
        return self.weight * hidden_states.to(input_dtype)
    def extra_repr(self): return f"{tuple(self.weight.shape)}, eps={self.variance_epsilon}"
class MllamaTextCrossAttention(nn.Module):
    def __init__(self, config: Optional[MllamaTextConfig] = None, layer_idx: Optional[int] = None):
        super().__init__()
        self.config = config
        self.num_heads = self.config.num_attention_heads
        self.num_key_value_heads = self.config.num_key_value_heads
        self.dropout = config.dropout
        self.hidden_size = config.hidden_size
        self.head_dim = config.hidden_size // self.num_heads
        self.layer_idx = layer_idx
        self.num_key_value_groups = self.num_heads // self.num_key_value_heads
        self.q_proj = nn.Linear(self.hidden_size, self.num_heads * self.head_dim, bias=False)
        self.k_proj = nn.Linear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=False)
        self.v_proj = nn.Linear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=False)
        self.o_proj = nn.Linear(self.num_heads * self.head_dim, self.hidden_size, bias=False)
        self.q_norm = MllamaTextRMSNorm(self.head_dim, eps=config.rms_norm_eps)
        self.k_norm = MllamaTextRMSNorm(self.head_dim, eps=config.rms_norm_eps)
    def forward(self, hidden_states: torch.Tensor, cross_attention_states: Optional[torch.Tensor] = None, past_key_value: Optional[Cache] = None, attention_mask: Optional[torch.Tensor] = None,
    output_attentions: bool = False, use_cache: bool = None, cache_position: Optional[torch.LongTensor] = None) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        bsz, q_len, _ = hidden_states.size()
        query_states = self.q_proj(hidden_states)
        query_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        query_states = self.q_norm(query_states)
        if cross_attention_states is not None:
            key_states = self.k_proj(cross_attention_states)
            value_states = self.v_proj(cross_attention_states)
            key_states = key_states.view(bsz, -1, self.num_key_value_heads, self.head_dim).transpose(1, 2)
            value_states = value_states.view(bsz, -1, self.num_key_value_heads, self.head_dim).transpose(1, 2)
            key_states = repeat_kv(key_states, self.num_key_value_groups)
            value_states = repeat_kv(value_states, self.num_key_value_groups)
            key_states = self.k_norm(key_states)
            if past_key_value is not None: key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, {"cache_position": cache_position})
        elif cache_position[0] != 0: key_states, value_states = (past_key_value.key_cache[self.layer_idx], past_key_value.value_cache[self.layer_idx])
        else: raise ValueError("Cross attention layer can't find neither `cross_attn_states` nor cached values for key/values!")
        attn_weights = torch.matmul(query_states, key_states.transpose(2, 3)) / math.sqrt(self.head_dim)
        if attention_mask is not None:
            causal_mask = attention_mask[:, :, :, : key_states.shape[-2]]
            attn_weights = attn_weights + causal_mask
        attn_weights = nn.functional.softmax(attn_weights, dim=-1, dtype=torch.float32).to(query_states.dtype)
        attn_weights = nn.functional.dropout(attn_weights, p=self.dropout, training=self.training)
        attn_output = torch.matmul(attn_weights, value_states)
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.reshape(bsz, q_len, -1)
        attn_output = self.o_proj(attn_output)
        if not output_attentions: attn_weights = None
        return attn_output, attn_weights, past_key_value
class MllamaTextCrossSdpaAttention(MllamaTextCrossAttention):
    def forward(self, hidden_states: torch.Tensor, cross_attention_states: Optional[torch.Tensor] = None, past_key_value: Optional[Cache] = None, attention_mask: Optional[torch.Tensor] = None,
    output_attentions: bool = False, use_cache: bool = None, cache_position: Optional[torch.LongTensor] = None) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        if output_attentions:
            logger.warning_once("MllamaModel is using MllamaTextCrossSdpaAttention, but `torch.nn.functional.scaled_dot_product_attention` does not support `output_attentions=True`. Falling back to the manual attention implementation, "+'but specifying the manual implementation will be required from sapiens_transformers version v5.0.0 onwards. This warning can be removed using the argument `attn_implementation="eager"` when loading the model.')
            return super().forward(hidden_states=hidden_states, cross_attention_states=cross_attention_states, attention_mask=attention_mask, past_key_value=past_key_value,
            output_attentions=output_attentions, use_cache=use_cache, cache_position=cache_position)
        bsz, q_len, _ = hidden_states.size()
        query_states = self.q_proj(hidden_states)
        query_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        query_states = self.q_norm(query_states)
        if cross_attention_states is not None:
            key_states = self.k_proj(cross_attention_states)
            value_states = self.v_proj(cross_attention_states)
            key_states = key_states.view(bsz, -1, self.num_key_value_heads, self.head_dim).transpose(1, 2)
            value_states = value_states.view(bsz, -1, self.num_key_value_heads, self.head_dim).transpose(1, 2)
            if past_key_value is not None: key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, {"cache_position": cache_position})
        elif cache_position[0] != 0: key_states, value_states = (past_key_value.key_cache[self.layer_idx], past_key_value.value_cache[self.layer_idx])
        else: raise ValueError("Cross attention layer can't find neither `cross_attn_states` nor cached values for key/values!")
        key_states = repeat_kv(key_states, self.num_key_value_groups)
        value_states = repeat_kv(value_states, self.num_key_value_groups)
        key_states = self.k_norm(key_states)
        if query_states.device.type == "cuda" and attention_mask is not None:
            query_states = query_states.contiguous()
            key_states = key_states.contiguous()
            value_states = value_states.contiguous()
        is_causal = True if attention_mask is None and q_len > 1 else False
        attn_output = torch.nn.functional.scaled_dot_product_attention(query_states, key_states, value_states, attn_mask=attention_mask, dropout_p=self.dropout if self.training else 0.0, is_causal=is_causal)
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.reshape(bsz, q_len, -1)
        attn_output = self.o_proj(attn_output)
        return attn_output, None, past_key_value
def rotate_half(x):
    x1 = x[..., : x.shape[-1] // 2]
    x2 = x[..., x.shape[-1] // 2 :]
    return torch.cat((-x2, x1), dim=-1)
def apply_rotary_pos_emb(q, k, cos, sin, position_ids=None, unsqueeze_dim=1):
    cos = cos.unsqueeze(unsqueeze_dim)
    sin = sin.unsqueeze(unsqueeze_dim)
    q_embed = (q * cos) + (rotate_half(q) * sin)
    k_embed = (k * cos) + (rotate_half(k) * sin)
    return q_embed, k_embed
def repeat_kv(hidden_states: torch.Tensor, n_rep: int) -> torch.Tensor:
    batch, num_key_value_heads, slen, head_dim = hidden_states.shape
    if n_rep == 1: return hidden_states
    hidden_states = hidden_states[:, :, None, :, :].expand(batch, num_key_value_heads, n_rep, slen, head_dim)
    return hidden_states.reshape(batch, num_key_value_heads * n_rep, slen, head_dim)
class MllamaTextSelfAttention(nn.Module):
    def __init__(self, config: MllamaTextConfig, layer_idx: int):
        super().__init__()
        self.config = config
        self.num_heads = config.num_attention_heads
        self.dropout = config.dropout
        self.hidden_size = config.hidden_size
        self.num_key_value_heads = config.num_key_value_heads
        self.head_dim = config.hidden_size // self.num_heads
        self.num_key_value_groups = self.num_heads // self.num_key_value_heads
        self.rope_theta = config.rope_theta
        self.layer_idx = layer_idx
        self.q_proj = nn.Linear(self.hidden_size, self.num_heads * self.head_dim, bias=False)
        self.k_proj = nn.Linear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=False)
        self.v_proj = nn.Linear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=False)
        self.o_proj = nn.Linear(self.num_heads * self.head_dim, self.hidden_size, bias=False)
    def forward(self, hidden_states: torch.Tensor, attention_mask: torch.Tensor, position_embeddings: torch.Tensor, output_attentions: bool = False, use_cache: bool = False,
    past_key_value=None, cache_position=None, **kwargs):
        bsz, q_len, _ = hidden_states.size()
        query_states = self.q_proj(hidden_states)
        key_states = self.k_proj(hidden_states)
        value_states = self.v_proj(hidden_states)
        query_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        key_states = key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        value_states = value_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        cos, sin = position_embeddings
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)
        if past_key_value is not None:
            cache_kwargs = {"sin": sin, "cos": cos, "cache_position": cache_position}
            key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, cache_kwargs)
        key_states = repeat_kv(key_states, self.num_key_value_groups)
        value_states = repeat_kv(value_states, self.num_key_value_groups)
        attn_weights = torch.matmul(query_states, key_states.transpose(2, 3)) / math.sqrt(self.head_dim)
        if attention_mask is not None:
            causal_mask = attention_mask[:, :, :, : key_states.shape[-2]]
            attn_weights = attn_weights + causal_mask
        attn_weights = nn.functional.softmax(attn_weights, dim=-1, dtype=torch.float32).to(query_states.dtype)
        attn_weights = nn.functional.dropout(attn_weights, p=self.dropout, training=self.training)
        attn_output = torch.matmul(attn_weights, value_states)
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.view(bsz, q_len, -1)
        attn_output = self.o_proj(attn_output)
        if not output_attentions: attn_weights = None
        return attn_output, attn_weights, past_key_value
class MllamaTextSelfSdpaAttention(MllamaTextSelfAttention):
    def forward(self, hidden_states: torch.Tensor, attention_mask: torch.Tensor, position_embeddings: torch.Tensor, output_attentions: bool = False, use_cache: bool = False,
    past_key_value=None, cache_position=None, **kwargs):
        if output_attentions:
            logger.warning_once("MllamaModel is using MllamaTextSelfSdpaAttention, but `torch.nn.functional.scaled_dot_product_attention` does not support `output_attentions=True`. Falling back to the manual attention implementation, "+'but specifying the manual implementation will be required from sapiens_transformers version v5.0.0 onwards. This warning can be removed using the argument `attn_implementation="eager"` when loading the model.')
            return super().forward(hidden_states=hidden_states, attention_mask=attention_mask, position_embeddings=position_embeddings, past_key_value=past_key_value,
            output_attentions=output_attentions, use_cache=use_cache, cache_position=cache_position, **kwargs)
        bsz, q_len, _ = hidden_states.size()
        query_states = self.q_proj(hidden_states)
        key_states = self.k_proj(hidden_states)
        value_states = self.v_proj(hidden_states)
        query_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        key_states = key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        value_states = value_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        cos, sin = position_embeddings
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)
        if past_key_value is not None:
            cache_kwargs = {"sin": sin, "cos": cos, "cache_position": cache_position}
            key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, cache_kwargs)
        key_states = repeat_kv(key_states, self.num_key_value_groups)
        value_states = repeat_kv(value_states, self.num_key_value_groups)
        causal_mask = attention_mask
        if attention_mask is not None: causal_mask = causal_mask[:, :, :, : key_states.shape[-2]]
        if query_states.device.type == "cuda" and causal_mask is not None:
            query_states = query_states.contiguous()
            key_states = key_states.contiguous()
            value_states = value_states.contiguous()
        is_causal = True if causal_mask is None and q_len > 1 else False
        attn_output = torch.nn.functional.scaled_dot_product_attention(query_states, key_states, value_states, attn_mask=causal_mask, dropout_p=self.dropout if self.training else 0.0, is_causal=is_causal)
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.view(bsz, q_len, -1)
        attn_output = self.o_proj(attn_output)
        return attn_output, None, past_key_value
MLLAMA_TEXT_CROSS_ATTENTION_CLASSES = {"eager": MllamaTextCrossAttention, "sdpa": MllamaTextCrossSdpaAttention}
MLLAMA_TEXT_ATTENTION_CLASSES = {"eager": MllamaTextSelfAttention, "sdpa": MllamaTextSelfSdpaAttention}
class MllamaTextMLP(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.hidden_size = config.hidden_size
        self.intermediate_size = config.intermediate_size
        self.gate_proj = nn.Linear(self.hidden_size, self.intermediate_size, bias=False)
        self.up_proj = nn.Linear(self.hidden_size, self.intermediate_size, bias=False)
        self.down_proj = nn.Linear(self.intermediate_size, self.hidden_size, bias=False)
        self.act_fn = ACT2FN[config.hidden_act]
    def forward(self, x): return self.down_proj(self.act_fn(self.gate_proj(x)) * self.up_proj(x))
class MllamaSelfAttentionDecoderLayer(nn.Module):
    def __init__(self, config: MllamaTextConfig, layer_idx: int):
        super().__init__()
        self.hidden_size = config.hidden_size
        self.self_attn = MLLAMA_TEXT_ATTENTION_CLASSES[config._attn_implementation](config=config, layer_idx=layer_idx)
        self.mlp = MllamaTextMLP(config)
        self.input_layernorm = MllamaTextRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.post_attention_layernorm = MllamaTextRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.layer_idx = layer_idx
    def forward(self, hidden_states: torch.Tensor, cross_attention_states: Optional[torch.Tensor] = None, cross_attention_mask: Optional[torch.Tensor] = None,
    attention_mask: Optional[torch.Tensor] = None, full_text_row_masked_out_mask: Optional[Tuple[torch.Tensor, torch.Tensor]] = None, position_ids: Optional[torch.LongTensor] = None,
    past_key_value: Optional[Cache] = None, output_attentions: Optional[bool] = False, use_cache: Optional[bool] = False, cache_position: Optional[torch.LongTensor] = None,
    position_embeddings: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[torch.FloatTensor, Optional[Tuple[torch.FloatTensor, torch.FloatTensor]]]:
        residual = hidden_states
        hidden_states = self.input_layernorm(hidden_states)
        hidden_states, self_attn_weights, present_key_value = self.self_attn(hidden_states=hidden_states, attention_mask=attention_mask, position_ids=position_ids,
        past_key_value=past_key_value, output_attentions=output_attentions, use_cache=use_cache, cache_position=cache_position, position_embeddings=position_embeddings)
        hidden_states = residual + hidden_states
        residual = hidden_states
        hidden_states = self.post_attention_layernorm(hidden_states)
        hidden_states = self.mlp(hidden_states)
        hidden_states = residual + hidden_states
        outputs = (hidden_states,)
        if output_attentions: outputs += (self_attn_weights,)
        if use_cache: outputs += (present_key_value,)
        return outputs
class MllamaCrossAttentionDecoderLayer(torch.nn.Module):
    def __init__(self, config: MllamaTextConfig, layer_idx: int) -> None:
        super().__init__()
        self.layer_idx = layer_idx
        self.cross_attn = MLLAMA_TEXT_CROSS_ATTENTION_CLASSES[config._attn_implementation](config, layer_idx=layer_idx)
        self.input_layernorm = MllamaTextRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.cross_attn_attn_gate = torch.nn.Parameter(torch.zeros(1))
        self.mlp = MllamaTextMLP(config)
        self.post_attention_layernorm = MllamaTextRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.cross_attn_mlp_gate = torch.nn.Parameter(torch.zeros(1))
    def forward(self, hidden_states: torch.Tensor, cross_attention_states: torch.Tensor, cross_attention_mask: torch.Tensor, attention_mask: torch.Tensor, full_text_row_masked_out_mask: Tuple[torch.Tensor, torch.Tensor],
    position_ids: Optional[torch.LongTensor] = None, past_key_value: Optional[Cache] = None, output_attentions: Optional[bool] = False, use_cache: Optional[bool] = False,
    cache_position: Optional[torch.LongTensor] = None, position_embeddings: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor]:
        residual = hidden_states
        hidden_states = self.input_layernorm(hidden_states)
        hidden_states, attn_weights, past_key_value = self.cross_attn(hidden_states=hidden_states, attention_mask=cross_attention_mask, cross_attention_states=cross_attention_states,
        past_key_value=past_key_value, output_attentions=output_attentions, cache_position=cache_position)
        hidden_states = residual + self.cross_attn_attn_gate.tanh() * hidden_states
        residual = hidden_states
        hidden_states = self.post_attention_layernorm(hidden_states)
        hidden_states = self.mlp(hidden_states)
        if full_text_row_masked_out_mask is not None: hidden_states = full_text_row_masked_out_mask[:, 0] * hidden_states
        hidden_states = residual + self.cross_attn_mlp_gate.tanh() * hidden_states
        outputs = (hidden_states,)
        if output_attentions: outputs += (attn_weights,)
        if use_cache: outputs += (past_key_value,)
        return outputs
class MllamaRotaryEmbedding(nn.Module):
    def __init__(self, config: MllamaTextConfig, device=None):
        super().__init__()
        self.rope_type = config.rope_scaling["rope_type"]
        self.max_seq_len_cached = config.max_position_embeddings
        self.original_max_seq_len = config.max_position_embeddings
        self.config = config
        self.rope_init_fn = ROPE_INIT_FUNCTIONS[self.rope_type]
        inv_freq, self.attention_scaling = self.rope_init_fn(self.config, device)
        self.register_buffer("inv_freq", inv_freq, persistent=False)
        self.original_inv_freq = self.inv_freq
    def _dynamic_frequency_update(self, position_ids, device):
        seq_len = torch.max(position_ids) + 1
        if seq_len > self.max_seq_len_cached:
            inv_freq, self.attention_scaling = self.rope_init_fn(self.config, device, seq_len=seq_len, **self.rope_kwargs)
            self.register_buffer("inv_freq", inv_freq, persistent=False)
            self.max_seq_len_cached = seq_len
        if seq_len < self.original_max_seq_len and self.max_seq_len_cached > self.original_max_seq_len:
            self.register_buffer("inv_freq", self.original_inv_freq, persistent=False)
            self.max_seq_len_cached = self.original_max_seq_len
    @torch.no_grad()
    def forward(self, x, position_ids):
        if "dynamic" in self.rope_type: self._dynamic_frequency_update(position_ids, device=x.device)
        inv_freq_expanded = self.inv_freq[None, :, None].float().expand(position_ids.shape[0], -1, 1)
        position_ids_expanded = position_ids[:, None, :].float()
        device_type = x.device.type
        device_type = device_type if isinstance(device_type, str) and device_type != "mps" else "cpu"
        with torch.autocast(device_type=device_type, enabled=False):
            freqs = (inv_freq_expanded.float() @ position_ids_expanded.float()).transpose(1, 2)
            emb = torch.cat((freqs, freqs), dim=-1)
            cos = emb.cos()
            sin = emb.sin()
        cos = cos * self.attention_scaling
        sin = sin * self.attention_scaling
        return cos.to(dtype=x.dtype), sin.to(dtype=x.dtype)
class MllamaPreTrainedModel(PreTrainedModel):
    config_class = MllamaConfig
    base_model_prefix = "model"
    supports_gradient_checkpointing = True
    _no_split_modules = ["MllamaVisionEncoderLayer", "MllamaCrossAttentionDecoderLayer", "MllamaSelfAttentionDecoderLayer"]
    _supports_cache_class = True
    _supports_static_cache = False
    _supports_sdpa = True
    _supports_quantized_cache = True
    def _init_weights(self, module):
        std = self.config.get_text_config().initializer_range
        if isinstance(module, (nn.Linear, nn.Conv2d)):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.Parameter): module.data.normal_(mean=0.0, std=std)
        elif isinstance(module, MllamaVisionModel): nn.init.normal_(module.class_embedding.data, std=std)
        elif isinstance(module, MllamaPrecomputedPositionEmbedding): nn.init.normal_(module.embedding.data, std=std)
        elif isinstance(module, MllamaVisionEncoderLayer) and module.is_gated:
            nn.init.normal_(module.gate_attn.data, std=std)
            nn.init.normal_(module.gate_ffn.data, std=std)
MLLAMA_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`MllamaConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
MLLAMA_VISION_INPUTS_DOCSTRING = r"""
    Args:
        pixel_values (`torch.FloatTensor` of shape `(batch_size, max_num_images, max_num_tiles, channels, image_size, image_size)):
            The tensors corresponding to the input images. Pixel values can be obtained using
            [`AutoImageProcessor`]. See [`MllamaImageProcessor.__call__`] for details ([]`MllamaProcessor`] uses
            [`MllamaImageProcessor`] for processing images).
        aspect_ratio_mask (`torch.Tensor` of shape `(batch_size, max_num_images, max_num_tiles)`, *optional*):
            Mask to avoid performing attention on padding tiles. Mask values selected in `[0, 1]`:
            - 1 for tiles that are *not masked*,
            - 0 for tiles that are *masked*.
        aspect_ratio_ids (`torch.Tensor` of shape `(batch_size, max_num_images)`, *optional*):
            Aspect ratio ids used to select the appropriate precomputed tile embeddings based on the aspect ratio of each input image.
            These ids correspond to indices in the model's list of supported aspect ratios, offset by 1.
            For example, if the model supports aspect ratios [[1, 1], [1, 2], [2, 1]]:
            - An image with aspect ratio [1, 1] would have ID 1
            - An image with aspect ratio [1, 2] would have ID 2
            - An image with aspect ratio [2, 1] would have ID 3
            The id 0 is reserved for padding (i.e., no image).
            If an image has aspect ratio [1, 2], that means it was split into 2 tiles horizontally, and its `aspect_ratio_id` would be 2.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
MLLAMA_TEXT_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary. Padding will be ignored by default should you provide
            it.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        attention_mask (`torch.Tensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            If `past_key_values` is used, optionally only the last `input_ids` have to be input (see
            `past_key_values`).
            If you want to change padding behavior, you should read [`modeling_opt._prepare_decoder_attention_mask`]
            and modify to your needs. See diagram 1 in [the paper](https://arxiv.org/abs/1910.13461) for more
            information on the default strategy.
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        cross_attention_mask (`torch.Tensor` of shape `(batch_size, seq_length, max_num_images, max_num_tiles)`, *optional*):
            Cross-attention mask to control the interaction between text tokens and image tiles.
            This 4D tensor defines which image tiles each text token should attend to.
            For each text token (in seq_length):
            - 1 indicates the token *should attend* to the corresponding image tile
            - 0 indicates the token *should not attend* to the corresponding image tile
        cross_attention_states (`torch.FloatTensor`, *optional*):
            Output of the vision model, used for cross-attention. This tensor contains the processed image features that
            the language model will attend to.
        position_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Indices of positions of each input sequence tokens in the position embeddings. Selected in the range `[0,
            config.n_positions - 1]`.
            [What are position IDs?](../glossary#position-ids)
        past_key_values (`Cache` or `tuple(tuple(torch.FloatTensor))`, *optional*):
            Pre-computed hidden-states (key and values in the self-attention blocks and in the cross-attention
            blocks) that can be used to speed up sequential decoding. This typically consists in the `past_key_values`
            returned by the model at a previous stage of decoding, when `use_cache=True` or `config.use_cache=True`.
            Two formats are allowed:
            - a [`~cache_utils.Cache`] instance;
            - Tuple of `tuple(torch.FloatTensor)` of length `config.n_layers`, with each tuple having 2 tensors of
            shape `(batch_size, num_heads, sequence_length, embed_size_per_head)`. This is also known as the legacy
            cache format.
            The model will output the same cache format that is fed as input. If no `past_key_values` are passed, the
            legacy cache format will be returned.
            If `past_key_values` are used, the user can optionally input only the last `input_ids` (those that don't
            have their past key value states given to this model) of shape `(batch_size, 1)` instead of all `input_ids`
            of shape `(batch_size, sequence_length)`.
        inputs_embeds (`torch.FloatTensor` of shape `(batch_size, sequence_length, hidden_size)`, *optional*):
            Optionally, instead of passing `input_ids` you can choose to directly pass an embedded representation. This
            is useful if you want more control over how to convert `input_ids` indices into associated vectors than the
            model's internal embedding lookup matrix.
        use_cache (`bool`, *optional*):
            If set to `True`, `past_key_values` key value states are returned and can be used to speed up decoding (see
            `past_key_values`).
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
        cache_position (`torch.LongTensor` of shape `(sequence_length)`, *optional*):
            Indices depicting the position of the input sequence tokens in the sequence. Contrarily to `position_ids`,
            this tensor is not affected by padding. It is used to update the cache in the correct position and to infer
            the complete sequence length.
"""
MLLAMA_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary. Padding will be ignored by default should you provide
            it.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        pixel_values (`torch.FloatTensor` of shape `(batch_size, max_num_images, max_num_tiles, channels, image_size, image_size)):
            The tensors corresponding to the input images. Pixel values can be obtained using
            [`AutoImageProcessor`]. See [`MllamaImageProcessor.__call__`] for details ([]`MllamaProcessor`] uses
            [`MllamaImageProcessor`] for processing images).
        aspect_ratio_mask (`torch.Tensor` of shape `(batch_size, max_num_images, max_num_tiles)`, *optional*):
            Mask to avoid performing attention on padding tiles. Mask values selected in `[0, 1]`:
            - 1 for tiles that are *not masked*,
            - 0 for tiles that are *masked*.
        aspect_ratio_ids (`torch.Tensor` of shape `(batch_size, max_num_images)`, *optional*):
            Aspect ratio ids used to select the appropriate precomputed tile embeddings based on the aspect ratio of each input image.
            These ids correspond to indices in the model's list of supported aspect ratios, offset by 1.
            For example, if the model supports aspect ratios [[1, 1], [1, 2], [2, 1]]:
            - An image with aspect ratio [1, 1] would have ID 1
            - An image with aspect ratio [1, 2] would have ID 2
            - An image with aspect ratio [2, 1] would have ID 3
            The id 0 is reserved for padding (i.e., no image).
            If an image has aspect ratio [1, 2], that means it was split into 2 tiles horizontally, and its `aspect_ratio_id` would be 2.
        attention_mask (`torch.Tensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            If `past_key_values` is used, optionally only the last `input_ids` have to be input (see
            `past_key_values`).
            If you want to change padding behavior, you should read [`modeling_opt._prepare_decoder_attention_mask`]
            and modify to your needs. See diagram 1 in [the paper](https://arxiv.org/abs/1910.13461) for more
            information on the default strategy.
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        cross_attention_mask (`torch.Tensor` of shape `(batch_size, seq_length, max_num_images, max_num_tiles)`, *optional*):
            Cross-attention mask to control the interaction between text tokens and image tiles.
            This 4D tensor defines which image tiles each text token should attend to.
            For each text token (in seq_length):
            - 1 indicates the token *should attend* to the corresponding image tile
            - 0 indicates the token *should not attend* to the corresponding image tile
        cross_attention_states (`torch.FloatTensor`, *optional*):
            Output of the vision model, used for cross-attention. This tensor contains the processed image features that
            the language model will attend to.
        position_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Indices of positions of each input sequence tokens in the position embeddings. Selected in the range `[0,
            config.n_positions - 1]`.
            [What are position IDs?](../glossary#position-ids)
        past_key_values (`Cache` or `tuple(tuple(torch.FloatTensor))`, *optional*):
            Pre-computed hidden-states (key and values in the self-attention blocks and in the cross-attention
            blocks) that can be used to speed up sequential decoding. This typically consists in the `past_key_values`
            returned by the model at a previous stage of decoding, when `use_cache=True` or `config.use_cache=True`.
            Two formats are allowed:
            - a [`~cache_utils.Cache`] instance;
            - Tuple of `tuple(torch.FloatTensor)` of length `config.n_layers`, with each tuple having 2 tensors of
            shape `(batch_size, num_heads, sequence_length, embed_size_per_head)`. This is also known as the legacy
            cache format.
            The model will output the same cache format that is fed as input. If no `past_key_values` are passed, the
            legacy cache format will be returned.
            If `past_key_values` are used, the user can optionally input only the last `input_ids` (those that don't
            have their past key value states given to this model) of shape `(batch_size, 1)` instead of all `input_ids`
            of shape `(batch_size, sequence_length)`.
        inputs_embeds (`torch.FloatTensor` of shape `(batch_size, sequence_length, hidden_size)`, *optional*):
            Optionally, instead of passing `input_ids` you can choose to directly pass an embedded representation. This
            is useful if you want more control over how to convert `input_ids` indices into associated vectors than the
            model's internal embedding lookup matrix.
        use_cache (`bool`, *optional*):
            If set to `True`, `past_key_values` key value states are returned and can be used to speed up decoding (see
            `past_key_values`).
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
        cache_position (`torch.LongTensor` of shape `(sequence_length)`, *optional*):
            Indices depicting the position of the input sequence tokens in the sequence. Contrarily to `position_ids`,
            this tensor is not affected by padding. It is used to update the cache in the correct position and to infer
            the complete sequence length.
"""
@add_start_docstrings("The Mllama Vision Model which consists of two vision encoders.", MLLAMA_START_DOCSTRING)
class MllamaVisionModel(MllamaPreTrainedModel):
    config_class = MllamaVisionConfig
    base_model_prefix = "vision_model"
    def __init__(self, config: MllamaVisionConfig):
        super().__init__(config)
        self.image_size = config.image_size
        self.patch_size = config.patch_size
        self.max_num_tiles = config.max_num_tiles
        self.hidden_size = config.hidden_size
        self.num_channels = config.num_channels
        self.intermediate_layers_indices = config.intermediate_layers_indices
        self.num_patches = (self.image_size // self.patch_size) ** 2 + 1
        self.scale = config.hidden_size**-0.5
        self.patch_embedding = nn.Conv2d(in_channels=config.num_channels, out_channels=self.hidden_size, kernel_size=self.patch_size, stride=self.patch_size, padding="valid", bias=False)
        self.class_embedding = nn.Parameter(self.scale * torch.randn(self.hidden_size))
        self.gated_positional_embedding = MllamaPrecomputedPositionEmbedding(config)
        self.pre_tile_positional_embedding = MllamaPrecomputedAspectRatioEmbedding(config, is_gated=True)
        self.post_tile_positional_embedding = MllamaPrecomputedAspectRatioEmbedding(config, is_gated=True)
        self.layernorm_pre = nn.LayerNorm(self.hidden_size)
        self.layernorm_post = nn.LayerNorm(self.hidden_size)
        self.transformer = MllamaVisionEncoder(config, config.num_hidden_layers, is_gated=False)
        self.global_transformer = MllamaVisionEncoder(config, config.num_global_layers, is_gated=True)
        self.post_init()
    def get_input_embeddings(self): return self.patch_embedding
    def apply_class_embedding(self, hidden_state: torch.Tensor) -> torch.Tensor:
        batch_size, _, hidden_size = hidden_state.shape
        class_embedding = self.class_embedding.expand(batch_size, 1, hidden_size)
        hidden_state = torch.cat([class_embedding, hidden_state], dim=1)
        return hidden_state
    @add_start_docstrings_to_model_forward(MLLAMA_VISION_INPUTS_DOCSTRING)
    def forward(self, pixel_values: torch.Tensor, aspect_ratio_ids: torch.Tensor, aspect_ratio_mask: torch.Tensor, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[BaseModelOutput, Tuple[torch.Tensor, ...]]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        batch_size, num_concurrent_media, num_tiles, num_channels, height, width = pixel_values.shape
        pixel_values = pixel_values.reshape(batch_size * num_concurrent_media * num_tiles, num_channels, height, width)
        aspect_ratio_ids = aspect_ratio_ids.reshape(batch_size * num_concurrent_media, -1)
        patch_embeds = self.patch_embedding(pixel_values.to(self.dtype).to(self.device))
        hidden_state = patch_embeds.flatten(2).transpose(1, 2)
        _, num_patches, dim = hidden_state.shape
        hidden_state = hidden_state.reshape(batch_size * num_concurrent_media, num_tiles, -1, dim)
        hidden_state = self.pre_tile_positional_embedding(hidden_state, aspect_ratio_ids)
        hidden_state = hidden_state.reshape(batch_size * num_concurrent_media * num_tiles, num_patches, dim)
        hidden_state = self.apply_class_embedding(hidden_state)
        num_patches += 1
        hidden_state = hidden_state.reshape(batch_size * num_concurrent_media, num_tiles, num_patches, dim)
        hidden_state = self.gated_positional_embedding(hidden_state, aspect_ratio_ids)
        hidden_state = self.layernorm_pre(hidden_state)
        num_padding_patches = (8 - (hidden_state.shape[-2] % 8)) % 8
        padding = (0, 0, 0, num_padding_patches)
        hidden_state = F.pad(hidden_state, padding, mode="constant", value=0)
        slice_index = -num_padding_patches if num_padding_patches > 0 else None
        attention_mask = aspect_ratio_mask.reshape(batch_size * num_concurrent_media, -1)
        attention_mask = _prepare_aspect_ratio_attention_mask(aspect_ratio_mask=attention_mask, num_patches=self.num_patches, target_length=hidden_state.shape[2], dtype=self.dtype)
        hidden_state = hidden_state.view(batch_size * num_concurrent_media, -1, dim)
        output = self.transformer(hidden_state, attention_mask=attention_mask, output_hidden_states=True, output_attentions=output_attentions)
        hidden_state = output[0]
        hidden_state = self.layernorm_post(hidden_state)
        hidden_state = hidden_state.reshape(batch_size * num_concurrent_media, num_tiles, num_patches + num_padding_patches, dim)
        hidden_state = self.post_tile_positional_embedding(hidden_state, aspect_ratio_ids)
        hidden_state = hidden_state.reshape(batch_size * num_concurrent_media, num_tiles * (num_patches + num_padding_patches), dim)
        global_output = self.global_transformer(hidden_state, attention_mask=attention_mask, output_hidden_states=output_hidden_states, output_attentions=output_attentions)
        hidden_state = global_output[0]
        hidden_state = hidden_state.reshape(batch_size * num_concurrent_media, num_tiles, num_patches + num_padding_patches, dim)
        hidden_state = hidden_state[:, :, :slice_index]
        hidden_state = hidden_state.reshape(batch_size, num_concurrent_media, num_tiles, num_patches, dim)
        all_intermediate_hidden_states = output[1]
        intermediate_hidden_states = torch.stack(all_intermediate_hidden_states, dim=-1)
        intermediate_hidden_states = intermediate_hidden_states[..., self.intermediate_layers_indices]
        intermediate_hidden_states = intermediate_hidden_states.reshape(batch_size * num_concurrent_media, num_tiles, num_patches + num_padding_patches, -1)
        intermediate_hidden_states = intermediate_hidden_states[:, :, :slice_index]
        intermediate_hidden_states = intermediate_hidden_states.reshape(batch_size, num_concurrent_media, num_tiles, num_patches, -1)
        hidden_state = torch.cat([hidden_state, intermediate_hidden_states], dim=-1)
        if output_hidden_states: hidden_states = tuple(all_intermediate_hidden_states) + tuple(global_output[1])
        else: hidden_states = None
        if output_attentions:
            global_attn = tuple(global_output[2]) if output_hidden_states else tuple(global_output[1])
            attentions = tuple(output[2]) + global_attn
        else: attentions = None
        if not return_dict: return tuple(v for v in [hidden_state, hidden_states, attentions] if v is not None)
        return BaseModelOutput(last_hidden_state=hidden_state, hidden_states=hidden_states, attentions=attentions)
@add_start_docstrings("The Mllama Text Model which consists of transformer with self and cross attention layers.", MLLAMA_START_DOCSTRING)
class MllamaTextModel(MllamaPreTrainedModel):
    config_class = MllamaTextConfig
    base_model_prefix = "language_model.model"
    def __init__(self, config: MllamaTextConfig):
        super().__init__(config)
        self.padding_idx = config.pad_token_id
        self.vocab_size = config.vocab_size
        self.embed_tokens = nn.Embedding(config.vocab_size + 8, config.hidden_size, self.padding_idx)
        self.cross_attention_layers = config.cross_attention_layers
        layers = []
        for layer_idx in range(config.num_hidden_layers):
            if layer_idx in self.cross_attention_layers: layers.append(MllamaCrossAttentionDecoderLayer(config, layer_idx))
            else: layers.append(MllamaSelfAttentionDecoderLayer(config, layer_idx))
        self.layers = nn.ModuleList(layers)
        self.norm = MllamaTextRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.rotary_emb = MllamaRotaryEmbedding(config=config)
        self.gradient_checkpointing = False
        self.post_init()
    def get_input_embeddings(self): return self.embed_tokens
    def set_input_embeddings(self, value): self.embed_tokens = value
    @add_start_docstrings_to_model_forward(MLLAMA_TEXT_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None,
    cross_attention_states: Optional[torch.FloatTensor] = None, cross_attention_mask: Optional[torch.Tensor] = None, full_text_row_masked_out_mask: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
    past_key_values: Optional[Union[Cache, List[torch.FloatTensor]]] = None, inputs_embeds: Optional[torch.FloatTensor] = None, use_cache: Optional[bool] = None,
    output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None,
    cache_position: Optional[torch.LongTensor] = None) -> Union[Tuple, BaseModelOutputWithPast]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        use_cache = use_cache if use_cache is not None else self.config.use_cache
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if (input_ids is None) ^ (inputs_embeds is not None): raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time, and must specify either one")
        if self.gradient_checkpointing and self.training and use_cache:
            logger.warning_once("`use_cache=True` is incompatible with gradient checkpointing. Setting `use_cache=False`.")
            use_cache = False
        if inputs_embeds is None: inputs_embeds = self.embed_tokens(input_ids)
        hidden_states = inputs_embeds
        if cache_position is None:
            past_seen_tokens = past_key_values.get_seq_length() if past_key_values is not None else 0
            cache_position = torch.arange(past_seen_tokens, past_seen_tokens + inputs_embeds.shape[1], device=inputs_embeds.device)
        if position_ids is None: position_ids = cache_position.unsqueeze(0)
        causal_mask = self._update_causal_mask(attention_mask, inputs_embeds, cache_position, past_key_values, output_attentions)
        position_embeddings = self.rotary_emb(hidden_states, position_ids)
        all_hidden_states = () if output_hidden_states else None
        all_self_attns = () if output_attentions else None
        next_decoder_cache = None
        for idx, decoder_layer in enumerate(self.layers):
            if output_hidden_states: all_hidden_states += (hidden_states,)
            is_cross_attention_layer = idx in self.cross_attention_layers
            is_cross_attention_cache_empty = past_key_values is None or (past_key_values is not None and past_key_values.get_seq_length(idx) == 0)
            if is_cross_attention_layer and cross_attention_states is None and is_cross_attention_cache_empty: continue
            if self.gradient_checkpointing and self.training:
                layer_outputs = self._gradient_checkpointing_func(decoder_layer.__call__, hidden_states, cross_attention_states, cross_attention_mask, causal_mask,
                full_text_row_masked_out_mask, position_ids, past_key_values, output_attentions, use_cache, cache_position, position_embeddings)
            else:
                layer_outputs = decoder_layer(hidden_states, cross_attention_states=cross_attention_states, cross_attention_mask=cross_attention_mask, attention_mask=causal_mask,
                full_text_row_masked_out_mask=full_text_row_masked_out_mask, position_ids=position_ids, past_key_value=past_key_values, output_attentions=output_attentions,
                use_cache=use_cache, cache_position=cache_position, position_embeddings=position_embeddings)
            hidden_states = layer_outputs[0]
            if use_cache: next_decoder_cache = layer_outputs[2 if output_attentions else 1]
            if output_attentions: all_self_attns += (layer_outputs[1],)
        hidden_states = self.norm(hidden_states)
        if output_hidden_states: all_hidden_states += (hidden_states,)
        next_cache = next_decoder_cache if use_cache else None
        if not return_dict: return tuple(v for v in [hidden_states, next_cache, all_hidden_states, all_self_attns] if v is not None)
        return BaseModelOutputWithPast(last_hidden_state=hidden_states, past_key_values=next_cache, hidden_states=all_hidden_states, attentions=all_self_attns)
    def _update_causal_mask(self, attention_mask: torch.Tensor, input_tensor: torch.Tensor, cache_position: torch.Tensor, past_key_values: Cache, output_attentions: bool):
        if self.config._attn_implementation == "flash_attention_2":
            if attention_mask is not None and 0.0 in attention_mask: return attention_mask
            return None
        past_seen_tokens = past_key_values.get_seq_length() if past_key_values is not None else 0
        if self.config._attn_implementation == "sdpa" and not output_attentions:
            if AttentionMaskConverter._ignore_causal_mask_sdpa(attention_mask, inputs_embeds=input_tensor, past_key_values_length=past_seen_tokens, is_training=self.training): return None
        dtype, device = input_tensor.dtype, input_tensor.device
        min_dtype = torch.finfo(dtype).min
        sequence_length = input_tensor.shape[1]
        target_length = (attention_mask.shape[-1] if isinstance(attention_mask, torch.Tensor) else past_seen_tokens + sequence_length + 1)
        causal_mask = _prepare_4d_causal_attention_mask_with_cache_position(attention_mask, sequence_length=sequence_length, target_length=target_length, dtype=dtype,
        device=device, min_dtype=min_dtype, cache_position=cache_position, batch_size=input_tensor.shape[0])
        if (self.config._attn_implementation == "sdpa" and attention_mask is not None and attention_mask.device.type == "cuda" and not output_attentions): causal_mask = AttentionMaskConverter._unmask_unattended(causal_mask, min_dtype)
        return causal_mask
@add_start_docstrings("The Mllama Text Model with a language modeling head on top.", MLLAMA_START_DOCSTRING)
class MllamaForCausalLM(MllamaPreTrainedModel, GenerationMixin):
    config_class = MllamaTextConfig
    base_model_prefix = "language_model"
    _tied_weights_keys = ["lm_head.weight"]
    def __init__(self, config):
        super().__init__(config.get_text_config())
        self.text_config = config.get_text_config()
        self.vocab_size = self.text_config.vocab_size
        self.model = MllamaTextModel._from_config(self.text_config, attn_implementation=config._attn_implementation)
        self.lm_head = nn.Linear(self.text_config.hidden_size, self.vocab_size, bias=False)
        self.post_init()
    def get_input_embeddings(self): return self.model.embed_tokens
    def set_input_embeddings(self, value): self.model.embed_tokens = value
    def get_output_embeddings(self): return self.lm_head
    def set_output_embeddings(self, new_embeddings): self.lm_head = new_embeddings
    def set_decoder(self, decoder): self.model = decoder
    def get_decoder(self): return self.model
    @add_start_docstrings_to_model_forward(MLLAMA_INPUTS_DOCSTRING)
    def forward(self, input_ids: torch.LongTensor = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None,
    cross_attention_states: Optional[torch.LongTensor] = None, cross_attention_mask: Optional[torch.LongTensor] = None, full_text_row_masked_out_mask: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
    past_key_values: Optional[Union[Cache, List[torch.FloatTensor]]] = None, inputs_embeds: Optional[torch.FloatTensor] = None, labels: Optional[torch.LongTensor] = None,
    use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None,
    cache_position: Optional[torch.LongTensor] = None, num_logits_to_keep: int = 0) -> Union[Tuple, CausalLMOutputWithPast]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.model(input_ids=input_ids, cross_attention_states=cross_attention_states, attention_mask=attention_mask, position_ids=position_ids,
        cross_attention_mask=cross_attention_mask, full_text_row_masked_out_mask=full_text_row_masked_out_mask, past_key_values=past_key_values,
        inputs_embeds=inputs_embeds, use_cache=use_cache, output_attentions=output_attentions, output_hidden_states=output_hidden_states,
        return_dict=return_dict, cache_position=cache_position)
        hidden_states = outputs[0]
        logits = self.lm_head(hidden_states[:, -num_logits_to_keep:, :]).float()
        loss = None
        if labels is not None:
            logits = logits.float()
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            loss_fct = CrossEntropyLoss()
            shift_logits = shift_logits.view(-1, self.config.vocab_size)
            shift_labels = shift_labels.view(-1)
            shift_labels = shift_labels.to(shift_logits.device)
            loss = loss_fct(shift_logits, shift_labels)
        if not return_dict:
            output = (logits,) + outputs[1:]
            return (loss,) + output if loss is not None else output
        return CausalLMOutputWithPast(loss=loss, logits=logits, past_key_values=outputs.past_key_values, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
    def prepare_inputs_for_generation(self, input_ids, past_key_values=None, attention_mask=None, inputs_embeds=None, cache_position=None, position_ids=None,
    use_cache=True, num_logits_to_keep=None, **kwargs):
        if past_key_values is not None:
            if inputs_embeds is not None: input_ids = input_ids[:, -cache_position.shape[0] :]
            elif input_ids.shape[1] != cache_position.shape[0]: input_ids = input_ids[:, cache_position]
        if attention_mask is not None and position_ids is None:
            position_ids = attention_mask.long().cumsum(-1) - 1
            position_ids.masked_fill_(attention_mask == 0, 1)
            if past_key_values:
                position_ids = position_ids[:, -input_ids.shape[1] :]
                position_ids = position_ids.clone(memory_format=torch.contiguous_format)
        if inputs_embeds is not None and cache_position[0] == 0: model_inputs = {"inputs_embeds": inputs_embeds, "input_ids": None}
        else: model_inputs = {"input_ids": input_ids.clone(memory_format=torch.contiguous_format), "inputs_embeds": None}
        if num_logits_to_keep is not None: model_inputs["num_logits_to_keep"] = num_logits_to_keep
        model_inputs.update({"position_ids": position_ids, "cache_position": cache_position, "past_key_values": past_key_values, "use_cache": use_cache, "attention_mask": attention_mask})
        return model_inputs
@add_start_docstrings("The Mllama model which consists of a vision encoder and a language model.", MLLAMA_START_DOCSTRING)
class MllamaForConditionalGeneration(MllamaPreTrainedModel, GenerationMixin):
    def __init__(self, config: MllamaConfig):
        super().__init__(config)
        self.vocab_size = config.text_config.vocab_size
        self.hidden_size = config.text_config.hidden_size
        self.max_num_tiles = config.vision_config.max_num_tiles
        self.vision_output_dim = config.vision_config.vision_output_dim
        self.pad_token_id = self.config.pad_token_id if self.config.pad_token_id is not None else -1
        self.vision_model = MllamaVisionModel._from_config(config.vision_config, attn_implementation=config._attn_implementation)
        self.language_model = MllamaForCausalLM._from_config(config.text_config, attn_implementation=config._attn_implementation)
        self.multi_modal_projector = nn.Linear(config.vision_config.vision_output_dim, config.text_config.hidden_size, bias=True)
        self.post_init()
    def get_input_embeddings(self): return self.language_model.get_input_embeddings()
    def set_input_embeddings(self, value): self.language_model.set_input_embeddings(value)
    def get_output_embeddings(self): return self.language_model.get_output_embeddings()
    def set_output_embeddings(self, new_embeddings): self.language_model.set_output_embeddings(new_embeddings)
    def set_decoder(self, decoder): self.language_model.set_decoder(decoder)
    def get_decoder(self): return self.language_model.get_decoder()
    def tie_weights(self): return self.language_model.tie_weights()
    @add_start_docstrings_to_model_forward(MLLAMA_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, pixel_values: Optional[torch.FloatTensor] = None, aspect_ratio_mask: Optional[torch.Tensor] = None,
    aspect_ratio_ids: Optional[torch.Tensor] = None, attention_mask: Optional[torch.Tensor] = None, cross_attention_mask: Optional[torch.Tensor] = None, cross_attention_states: Optional[torch.Tensor] = None,
    position_ids: Optional[torch.LongTensor] = None, past_key_values: Optional[List[torch.FloatTensor]] = None, inputs_embeds: Optional[torch.FloatTensor] = None,
    labels: Optional[torch.LongTensor] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None, cache_position: Optional[torch.LongTensor] = None, num_logits_to_keep: int = 0) -> Union[Tuple, CausalLMOutputWithPast]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if (input_ids is None) ^ (inputs_embeds is not None): raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time, and must specify either one")
        if pixel_values is not None and inputs_embeds is not None: raise ValueError("You cannot specify both pixel_values and inputs_embeds at the same time, and must specify either one")
        if pixel_values is not None and cross_attention_states is not None: raise ValueError("`pixel_values` and `cross_attention_states` cannot be provided simultaneously")
        if pixel_values is not None:
            if aspect_ratio_ids is None: raise ValueError("`aspect_ratio_ids` must be provided if `pixel_values` is provided")
            vision_outputs = self.vision_model(pixel_values=pixel_values, aspect_ratio_ids=aspect_ratio_ids, aspect_ratio_mask=aspect_ratio_mask, output_hidden_states=output_hidden_states,
            output_attentions=output_attentions, return_dict=return_dict)
            cross_attention_states = vision_outputs[0]
            cross_attention_states = self.multi_modal_projector(cross_attention_states).reshape(-1, cross_attention_states.shape[-2], self.hidden_size)
        if cross_attention_mask is not None: cross_attention_mask, full_text_row_masked_out_mask = _prepare_cross_attention_mask(cross_attention_mask, num_vision_tokens=self.vision_model.num_patches, dtype=self.dtype)
        else: full_text_row_masked_out_mask = None
        if cross_attention_mask is not None and cache_position is not None:
            cross_attention_mask = cross_attention_mask[:, :, cache_position]
            full_text_row_masked_out_mask = full_text_row_masked_out_mask[:, :, cache_position]
        outputs = self.language_model(input_ids=input_ids, attention_mask=attention_mask, position_ids=position_ids, cross_attention_states=cross_attention_states,
        cross_attention_mask=cross_attention_mask, full_text_row_masked_out_mask=full_text_row_masked_out_mask, past_key_values=past_key_values, use_cache=use_cache,
        inputs_embeds=inputs_embeds, labels=labels, output_hidden_states=output_hidden_states, output_attentions=output_attentions, return_dict=return_dict,
        cache_position=cache_position, num_logits_to_keep=num_logits_to_keep)
        return outputs
    def prepare_inputs_for_generation(self, input_ids=None, inputs_embeds=None, attention_mask=None, position_ids=None, pixel_values=None, aspect_ratio_ids=None,
    aspect_ratio_mask=None, cross_attention_mask=None, past_key_values=None, use_cache=False, cache_position=None, num_logits_to_keep=None, **kwargs):
        if past_key_values is not None:
            if inputs_embeds is not None: input_ids = input_ids[:, -cache_position.shape[0] :]
            elif input_ids.shape[1] != cache_position.shape[0]: input_ids = input_ids[:, cache_position]
        if attention_mask is not None and position_ids is None:
            position_ids = attention_mask.long().cumsum(-1) - 1
            position_ids.masked_fill_(attention_mask == 0, 1)
            if past_key_values:
                position_ids = position_ids[:, -input_ids.shape[1] :]
                position_ids = position_ids.clone(memory_format=torch.contiguous_format)
        if inputs_embeds is not None and cache_position[0] == 0: model_inputs = {"inputs_embeds": inputs_embeds, "input_ids": None}
        else: model_inputs = {"input_ids": input_ids.clone(memory_format=torch.contiguous_format), "inputs_embeds": None}
        if num_logits_to_keep is not None: model_inputs["num_logits_to_keep"] = num_logits_to_keep
        model_inputs.update({"position_ids": position_ids, "cache_position": cache_position, "past_key_values": past_key_values, "use_cache": use_cache, "attention_mask": attention_mask, "cross_attention_mask": cross_attention_mask})
        if (input_ids == self.config.image_token_index).any():
            model_inputs["pixel_values"] = pixel_values
            model_inputs["aspect_ratio_ids"] = aspect_ratio_ids
            model_inputs["aspect_ratio_mask"] = aspect_ratio_mask
        return model_inputs
    def _update_model_kwargs_for_generation(self, outputs, model_kwargs, is_encoder_decoder, **kwargs):
        cross_attention_mask_prev = model_kwargs.get("cross_attention_mask", None)
        model_kwargs = super()._update_model_kwargs_for_generation(outputs=outputs, model_kwargs=model_kwargs, is_encoder_decoder=is_encoder_decoder, **kwargs)
        if cross_attention_mask_prev is not None: model_kwargs["cross_attention_mask"] = torch.cat([cross_attention_mask_prev, cross_attention_mask_prev[:, -1:, ...]], dim=1)
        return model_kwargs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
