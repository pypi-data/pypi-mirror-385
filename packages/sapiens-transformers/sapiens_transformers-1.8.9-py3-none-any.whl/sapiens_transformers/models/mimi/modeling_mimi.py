"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union
import torch
import torch.utils.checkpoint
from torch import nn
from ...activations import ACT2FN
from ...cache_utils import Cache, DynamicCache, StaticCache
from ...modeling_attn_mask_utils import AttentionMaskConverter
from ...modeling_outputs import BaseModelOutputWithPast
from ...modeling_utils import PreTrainedModel
from ...utils import (ModelOutput, add_start_docstrings, add_start_docstrings_to_model_forward, is_flash_attn_2_available, is_flash_attn_greater_or_equal_2_10,
logging, replace_return_docstrings)
from .configuration_mimi import MimiConfig
if is_flash_attn_2_available(): from ...modeling_flash_attention_utils import _flash_attention_forward
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "MimiConfig"
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
@dataclass
class MimiOutput(ModelOutput):
    """Args:"""
    audio_codes: torch.LongTensor = None
    audio_values: torch.FloatTensor = None
    encoder_past_key_values: Optional[Union[Cache, List[torch.FloatTensor]]] = None
    decoder_past_key_values: Optional[Union[Cache, List[torch.FloatTensor]]] = None
@dataclass
class MimiEncoderOutput(ModelOutput):
    """Args:"""
    audio_codes: torch.LongTensor = None
    encoder_past_key_values: Optional[Union[Cache, List[torch.FloatTensor]]] = None
@dataclass
class MimiDecoderOutput(ModelOutput):
    """Args:"""
    audio_values: torch.FloatTensor = None
    decoder_past_key_values: Optional[Union[Cache, List[torch.FloatTensor]]] = None
class MimiConv1d(nn.Module):
    def __init__(self, config, in_channels: int, out_channels: int, kernel_size: int, stride: int = 1, dilation: int = 1, groups: int = 1, pad_mode=None, bias: bool = True):
        super().__init__()
        self.causal = config.use_causal_conv
        self.pad_mode = config.pad_mode if pad_mode is None else pad_mode
        if stride > 1 and dilation > 1: logger.warning(f"MimiConv1d has been initialized with stride > 1 and dilation > 1 (kernel_size={kernel_size} stride={stride}, dilation={dilation}).")
        self.conv = nn.Conv1d(in_channels, out_channels, kernel_size, stride, dilation=dilation, groups=groups, bias=bias)
        kernel_size = self.conv.kernel_size[0]
        stride = torch.tensor(self.conv.stride[0], dtype=torch.int64)
        dilation = self.conv.dilation[0]
        kernel_size = torch.tensor((kernel_size - 1) * dilation + 1, dtype=torch.int64)
        self.register_buffer("stride", stride, persistent=False)
        self.register_buffer("kernel_size", kernel_size, persistent=False)
        self.register_buffer("padding_total", torch.tensor(kernel_size - stride, dtype=torch.int64), persistent=False)
        self.padding_right = self.padding_total // 2
        self.padding_left = self.padding_total - self.padding_right
    def apply_weight_norm(self):
        weight_norm = nn.utils.weight_norm
        if hasattr(nn.utils.parametrizations, "weight_norm"): weight_norm = nn.utils.parametrizations.weight_norm
        weight_norm(self.conv)
    def remove_weight_norm(self): nn.utils.remove_weight_norm(self.conv)
    def _get_extra_padding_for_conv1d(self, hidden_states: torch.Tensor) -> torch.Tensor:
        length = hidden_states.shape[-1]
        n_frames = (length - self.kernel_size + self.padding_total) / self.stride + 1
        n_frames = torch.ceil(n_frames).to(torch.int64) - 1
        ideal_length = n_frames * self.stride + self.kernel_size - self.padding_total
        return ideal_length - length
    @staticmethod
    def _pad1d(hidden_states: torch.Tensor, paddings: Tuple[int, int], mode: str = "zero", value: float = 0.0):
        length = hidden_states.shape[-1]
        padding_left, padding_right = paddings
        if not mode == "reflect": return nn.functional.pad(hidden_states, paddings, mode, value)
        max_pad = max(padding_left, padding_right)
        extra_pad = 0
        if length <= max_pad:
            extra_pad = max_pad - length + 1
            hidden_states = nn.functional.pad(hidden_states, (0, extra_pad))
        padded = nn.functional.pad(hidden_states, paddings, mode, value)
        end = padded.shape[-1] - extra_pad
        return padded[..., :end]
    def forward(self, hidden_states):
        extra_padding = self._get_extra_padding_for_conv1d(hidden_states)
        if self.causal: hidden_states = self._pad1d(hidden_states, (self.padding_total, extra_padding), mode=self.pad_mode)
        else: hidden_states = self._pad1d(hidden_states, (self.padding_left, self.padding_right + extra_padding), mode=self.pad_mode)
        hidden_states = self.conv(hidden_states)
        return hidden_states
class MimiConvTranspose1d(nn.Module):
    def __init__(self, config, in_channels: int, out_channels: int, kernel_size: int, stride: int = 1, groups: int = 1, bias=True):
        super().__init__()
        self.causal = config.use_causal_conv
        self.trim_right_ratio = config.trim_right_ratio
        self.conv = nn.ConvTranspose1d(in_channels, out_channels, kernel_size, stride, groups=groups, bias=bias)
        if not (self.causal or self.trim_right_ratio == 1.0): raise ValueError("`trim_right_ratio` != 1.0 only makes sense for causal convolutions")
        kernel_size = self.conv.kernel_size[0]
        stride = self.conv.stride[0]
        padding_total = kernel_size - stride
        if self.causal: self.padding_right = math.ceil(padding_total * self.trim_right_ratio)
        else: self.padding_right = padding_total // 2
        self.padding_left = padding_total - self.padding_right
    def apply_weight_norm(self):
        weight_norm = nn.utils.weight_norm
        if hasattr(nn.utils.parametrizations, "weight_norm"): weight_norm = nn.utils.parametrizations.weight_norm
        weight_norm(self.conv)
    def remove_weight_norm(self): nn.utils.remove_weight_norm(self.conv)
    def forward(self, hidden_states):
        hidden_states = self.conv(hidden_states)
        end = hidden_states.shape[-1] - self.padding_right
        hidden_states = hidden_states[..., self.padding_left : end]
        return hidden_states
class MimiResnetBlock(nn.Module):
    def __init__(self, config: MimiConfig, dim: int, dilations: List[int]):
        super().__init__()
        kernel_sizes = (config.residual_kernel_size, 1)
        if len(kernel_sizes) != len(dilations): raise ValueError("Number of kernel sizes should match number of dilations")
        hidden = dim // config.compress
        block = []
        for i, (kernel_size, dilation) in enumerate(zip(kernel_sizes, dilations)):
            in_chs = dim if i == 0 else hidden
            out_chs = dim if i == len(kernel_sizes) - 1 else hidden
            block += [nn.ELU()]
            block += [MimiConv1d(config, in_chs, out_chs, kernel_size, dilation=dilation)]
        self.block = nn.ModuleList(block)
        if config.use_conv_shortcut: self.shortcut = MimiConv1d(config, dim, dim, kernel_size=1)
        else: self.shortcut = nn.Identity()
    def forward(self, hidden_states):
        residual = hidden_states
        for layer in self.block: hidden_states = layer(hidden_states)
        return self.shortcut(residual) + hidden_states
class MimiEncoder(nn.Module):
    def __init__(self, config: MimiConfig):
        super().__init__()
        model = [MimiConv1d(config, config.audio_channels, config.num_filters, config.kernel_size)]
        scaling = 1
        for ratio in reversed(config.upsampling_ratios):
            current_scale = scaling * config.num_filters
            for j in range(config.num_residual_layers): model += [MimiResnetBlock(config, current_scale, [config.dilation_growth_rate**j, 1])]
            model += [nn.ELU()]
            model += [MimiConv1d(config, current_scale, current_scale * 2, kernel_size=ratio * 2, stride=ratio)]
            scaling *= 2
        model += [nn.ELU()]
        model += [MimiConv1d(config, scaling * config.num_filters, config.hidden_size, config.last_kernel_size)]
        self.layers = nn.ModuleList(model)
    def forward(self, hidden_states):
        for layer in self.layers: hidden_states = layer(hidden_states)
        return hidden_states
class MimiLayerScale(nn.Module):
    def __init__(self, config):
        super().__init__()
        channels = config.hidden_size
        initial_scale = config.layer_scale_initial_scale
        self.scale = nn.Parameter(torch.full((channels,), initial_scale, requires_grad=True))
    def forward(self, x: torch.Tensor): return self.scale * x
class MimiRotaryEmbedding(nn.Module):
    def __init__(self, dim, max_position_embeddings=2048, base=10000, device=None):
        super().__init__()
        self.dim = dim
        self.max_position_embeddings = max_position_embeddings
        self.base = base
        inv_freq = 1.0 / (self.base ** (torch.arange(0, self.dim, 2, dtype=torch.int64).float().to(device) / self.dim))
        self.register_buffer("inv_freq", inv_freq, persistent=False)
    @torch.no_grad()
    def forward(self, x, position_ids):
        inv_freq_expanded = self.inv_freq[None, :, None].float().expand(position_ids.shape[0], -1, 1)
        position_ids_expanded = position_ids[:, None, :].float()
        device_type = x.device.type
        device_type = device_type if isinstance(device_type, str) and device_type != "mps" else "cpu"
        with torch.autocast(device_type=device_type, enabled=False):
            freqs = (inv_freq_expanded.float() @ position_ids_expanded.float()).transpose(1, 2)
            emb = torch.cat((freqs, freqs), dim=-1)
            cos = emb.cos()
            sin = emb.sin()
        return cos.to(dtype=x.dtype), sin.to(dtype=x.dtype)
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
class MimiMLP(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.activation_fn = ACT2FN[config.hidden_act]
        self.fc1 = nn.Linear(config.hidden_size, config.intermediate_size, bias=False)
        self.fc2 = nn.Linear(config.intermediate_size, config.hidden_size, bias=False)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.fc1(hidden_states)
        hidden_states = self.activation_fn(hidden_states)
        hidden_states = self.fc2(hidden_states)
        return hidden_states
def repeat_kv(hidden_states: torch.Tensor, n_rep: int) -> torch.Tensor:
    batch, num_key_value_heads, slen, head_dim = hidden_states.shape
    if n_rep == 1: return hidden_states
    hidden_states = hidden_states[:, :, None, :, :].expand(batch, num_key_value_heads, n_rep, slen, head_dim)
    return hidden_states.reshape(batch, num_key_value_heads * n_rep, slen, head_dim)
class MimiAttention(nn.Module):
    def __init__(self, config: MimiConfig, layer_idx: Optional[int] = None):
        super().__init__()
        self.config = config
        self.layer_idx = layer_idx
        if layer_idx is None: logger.warning_once(f"Instantiating {self.__class__.__name__} without passing a `layer_idx` is not recommended and will lead to errors during the forward call if caching is used. Please make sure to provide a `layer_idx` when creating this class.")
        self.attention_dropout = config.attention_dropout
        self.hidden_size = config.hidden_size
        self.num_heads = config.num_attention_heads
        self.head_dim = config.head_dim
        self.num_key_value_heads = config.num_key_value_heads
        self.num_key_value_groups = self.num_heads // self.num_key_value_heads
        self.max_position_embeddings = config.max_position_embeddings
        self.rope_theta = config.rope_theta
        self.is_causal = True
        self.scaling = 1 / math.sqrt(config.head_dim)
        if self.hidden_size % self.num_heads != 0: raise ValueError(f"hidden_size must be divisible by num_heads (got `hidden_size`: {self.hidden_size} and `num_heads`: {self.num_heads}).")
        self.q_proj = nn.Linear(self.hidden_size, self.num_heads * self.head_dim, bias=config.attention_bias)
        self.k_proj = nn.Linear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=config.attention_bias)
        self.v_proj = nn.Linear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=config.attention_bias)
        self.o_proj = nn.Linear(self.num_heads * self.head_dim, self.hidden_size, bias=config.attention_bias)
        self.rotary_emb = MimiRotaryEmbedding(self.head_dim, max_position_embeddings=self.max_position_embeddings, base=self.rope_theta)
        self.sliding_window = config.sliding_window
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_value: Optional[Cache] = None,
    output_attentions: bool = False, use_cache: bool = False, cache_position: Optional[torch.LongTensor] = None) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        bsz, q_len, _ = hidden_states.size()
        query_states = self.q_proj(hidden_states)
        key_states = self.k_proj(hidden_states)
        value_states = self.v_proj(hidden_states)
        query_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        key_states = key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        value_states = value_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        cos, sin = self.rotary_emb(value_states, position_ids)
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)
        if past_key_value is not None:
            cache_kwargs = {"sin": sin, "cos": cos, "cache_position": cache_position}
            key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, cache_kwargs)
        key_states = repeat_kv(key_states, self.num_key_value_groups)
        value_states = repeat_kv(value_states, self.num_key_value_groups)
        attn_weights = torch.matmul(query_states, key_states.transpose(2, 3)) * self.scaling
        if attention_mask is not None:
            causal_mask = attention_mask[:, :, :, : key_states.shape[-2]]
            attn_weights = attn_weights + causal_mask
        attn_weights = nn.functional.softmax(attn_weights, dim=-1, dtype=torch.float32).to(query_states.dtype)
        attn_weights = nn.functional.dropout(attn_weights, p=self.attention_dropout, training=self.training)
        attn_output = torch.matmul(attn_weights, value_states)
        if attn_output.size() != (bsz, self.num_heads, q_len, self.head_dim): raise ValueError(f"`attn_output` should be of size {(bsz, self.num_heads, q_len, self.head_dim)}, but is {attn_output.size()}")
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.view(bsz, q_len, -1)
        attn_output = self.o_proj(attn_output)
        if not output_attentions: attn_weights = None
        return attn_output, attn_weights, past_key_value
class MimiFlashAttention2(MimiAttention):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._flash_attn_uses_top_left_mask = not is_flash_attn_greater_or_equal_2_10()
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.LongTensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_value: Optional[Cache] = None,
    output_attentions: bool = False, use_cache: bool = False, cache_position: Optional[torch.LongTensor] = None) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        if isinstance(past_key_value, StaticCache): raise ValueError("`static` cache implementation is not compatible with `attn_implementation==flash_attention_2` make sure to use `sdpa` in the mean time")
        output_attentions = False
        bsz, q_len, _ = hidden_states.size()
        query_states = self.q_proj(hidden_states)
        key_states = self.k_proj(hidden_states)
        value_states = self.v_proj(hidden_states)
        query_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        key_states = key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        value_states = value_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        cos, sin = self.rotary_emb(value_states, position_ids)
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)
        if past_key_value is not None:
            cache_kwargs = {"sin": sin, "cos": cos, "cache_position": cache_position}
            key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, cache_kwargs)
        query_states = query_states.transpose(1, 2)
        key_states = key_states.transpose(1, 2)
        value_states = value_states.transpose(1, 2)
        dropout_rate = self.attention_dropout if self.training else 0.0
        input_dtype = query_states.dtype
        if input_dtype == torch.float32:
            if torch.is_autocast_enabled(): target_dtype = torch.get_autocast_gpu_dtype()
            elif hasattr(self.config, "_pre_quantization_dtype"): target_dtype = self.config._pre_quantization_dtype
            else: target_dtype = self.q_proj.weight.dtype
            logger.warning_once(f"The input hidden states seems to be silently casted in float32, this might be related to the fact you have upcasted embedding or layer norm layers in float32. We will cast back the input in {target_dtype}.")
            query_states = query_states.to(target_dtype)
            key_states = key_states.to(target_dtype)
            value_states = value_states.to(target_dtype)
        attn_output = _flash_attention_forward(query_states, key_states, value_states, attention_mask, q_len, position_ids=position_ids, dropout=dropout_rate,
        sliding_window=getattr(self, "sliding_window", None), is_causal=self.is_causal, use_top_left_mask=self._flash_attn_uses_top_left_mask)
        attn_output = attn_output.reshape(bsz, q_len, -1).contiguous()
        attn_output = self.o_proj(attn_output)
        if not output_attentions: attn_weights = None
        return attn_output, attn_weights, past_key_value
class MimiSdpaAttention(MimiAttention):
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_value: Optional[Cache] = None,
    output_attentions: bool = False, use_cache: bool = False, cache_position: Optional[torch.LongTensor] = None, **kwargs) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        if output_attentions:
            logger.warning_once("MimiModel is using MimiSdpaAttention, but `torch.nn.functional.scaled_dot_product_attention` does not support `output_attentions=True`. Falling back to the manual attention implementation, "+'but specifying the manual implementation will be required from sapiens_transformers version v5.0.0 onwards. This warning can be removed using the argument `attn_implementation="eager"` when loading the model.')
            return super().forward(hidden_states=hidden_states, attention_mask=attention_mask, position_ids=position_ids, past_key_value=past_key_value, output_attentions=output_attentions,
            use_cache=use_cache, cache_position=cache_position)
        bsz, q_len, _ = hidden_states.size()
        query_states = self.q_proj(hidden_states)
        key_states = self.k_proj(hidden_states)
        value_states = self.v_proj(hidden_states)
        query_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        key_states = key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        value_states = value_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        cos, sin = self.rotary_emb(value_states, position_ids)
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
        attn_output = torch.nn.functional.scaled_dot_product_attention(query_states, key_states, value_states, attn_mask=causal_mask, dropout_p=self.attention_dropout if self.training else 0.0, is_causal=is_causal)
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.view(bsz, q_len, -1)
        attn_output = self.o_proj(attn_output)
        return attn_output, None, past_key_value
MIMI_ATTENTION_CLASSES = {"eager": MimiAttention, "flash_attention_2": MimiFlashAttention2, "sdpa": MimiSdpaAttention}
class MimiTransformerLayer(nn.Module):
    def __init__(self, config: MimiConfig, layer_idx: int):
        super().__init__()
        self.hidden_size = config.hidden_size
        self.self_attn = MIMI_ATTENTION_CLASSES[config._attn_implementation](config=config, layer_idx=layer_idx)
        self.mlp = MimiMLP(config)
        self.input_layernorm = nn.LayerNorm(config.hidden_size, eps=config.norm_eps)
        self.post_attention_layernorm = nn.LayerNorm(config.hidden_size, eps=config.norm_eps)
        self.self_attn_layer_scale = MimiLayerScale(config)
        self.mlp_layer_scale = MimiLayerScale(config)
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_value: Optional[Cache] = None,
    output_attentions: Optional[bool] = False, use_cache: Optional[bool] = False, cache_position: Optional[torch.LongTensor] = None,
    **kwargs) -> Tuple[torch.FloatTensor, Optional[Tuple[torch.FloatTensor, torch.FloatTensor]]]:
        residual = hidden_states
        hidden_states = self.input_layernorm(hidden_states)
        hidden_states, self_attn_weights, present_key_value = self.self_attn(hidden_states=hidden_states, attention_mask=attention_mask,
        position_ids=position_ids, past_key_value=past_key_value, output_attentions=output_attentions, use_cache=use_cache, cache_position=cache_position, **kwargs)
        hidden_states = residual + self.self_attn_layer_scale(hidden_states)
        residual = hidden_states
        hidden_states = self.post_attention_layernorm(hidden_states)
        hidden_states = self.mlp(hidden_states)
        hidden_states = residual + self.mlp_layer_scale(hidden_states)
        outputs = (hidden_states,)
        if output_attentions: outputs += (self_attn_weights,)
        if use_cache: outputs += (present_key_value,)
        return outputs
class MimiTransformerModel(nn.Module):
    def __init__(self, config: MimiConfig):
        super().__init__()
        self.layers = nn.ModuleList([MimiTransformerLayer(config, layer_idx) for layer_idx in range(config.num_hidden_layers)])
        self._attn_implementation = config._attn_implementation
        self.gradient_checkpointing = False
        self.config = config
    def forward(self, hidden_states: torch.LongTensor = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None,
    past_key_values: Optional[Union[Cache, List[torch.FloatTensor]]] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, cache_position: Optional[torch.LongTensor] = None) -> Union[Tuple, BaseModelOutputWithPast]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        use_cache = use_cache if use_cache is not None else self.config.use_cache
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if self.gradient_checkpointing and self.training and use_cache:
            logger.warning_once("`use_cache=True` is incompatible with gradient checkpointing. Setting `use_cache=False`.")
            use_cache = False
        if use_cache and not isinstance(past_key_values, Cache):
            if past_key_values is None: past_key_values = DynamicCache()
            else:
                past_key_values = DynamicCache.from_legacy_cache(past_key_values)
                logger.warning_once("We detected that you are passing `past_key_values` as a tuple of tuples. This is deprecated and will be removed in v1.0.")
        if cache_position is None:
            past_seen_tokens = past_key_values.get_seq_length() if past_key_values is not None else 0
            cache_position = torch.arange(past_seen_tokens, past_seen_tokens + hidden_states.shape[1], device=hidden_states.device)
        if position_ids is None: position_ids = cache_position.unsqueeze(0)
        causal_mask = None
        if attention_mask is not None: causal_mask = self._update_causal_mask(attention_mask, hidden_states, cache_position, past_key_values, output_attentions)
        all_hidden_states = () if output_hidden_states else None
        all_self_attns = () if output_attentions else None
        next_decoder_cache = None
        for decoder_layer in self.layers:
            if output_hidden_states: all_hidden_states += (hidden_states,)
            if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(decoder_layer.__call__, hidden_states, causal_mask, position_ids, past_key_values, output_attentions, use_cache, cache_position)
            else:
                layer_outputs = decoder_layer(hidden_states, attention_mask=causal_mask, position_ids=position_ids, past_key_value=past_key_values, output_attentions=output_attentions,
                use_cache=use_cache, cache_position=cache_position)
            hidden_states = layer_outputs[0]
            if use_cache: next_decoder_cache = layer_outputs[2 if output_attentions else 1]
            if output_attentions: all_self_attns += (layer_outputs[1],)
        if output_hidden_states: all_hidden_states += (hidden_states,)
        next_cache = next_decoder_cache if use_cache else None
        if not return_dict: return tuple(v for v in [hidden_states, next_cache, all_hidden_states, all_self_attns] if v is not None)
        return BaseModelOutputWithPast(last_hidden_state=hidden_states, past_key_values=next_cache, hidden_states=all_hidden_states, attentions=all_self_attns)
    def _update_causal_mask(self, attention_mask: torch.Tensor, input_tensor: torch.Tensor, cache_position: torch.Tensor, past_key_values: Cache, output_attentions: bool):
        if self.config._attn_implementation == "flash_attention_2":
            if attention_mask is not None and 0.0 in attention_mask: return attention_mask
            return None
        past_seen_tokens = past_key_values.get_seq_length() if past_key_values is not None else 0
        using_static_cache = isinstance(past_key_values, StaticCache)
        if self.config._attn_implementation == "sdpa" and not using_static_cache and not output_attentions:
            if AttentionMaskConverter._ignore_causal_mask_sdpa(attention_mask, inputs_embeds=input_tensor, past_key_values_length=past_seen_tokens, is_training=self.training): return None
        dtype, device = input_tensor.dtype, input_tensor.device
        min_dtype = torch.finfo(dtype).min
        sequence_length = input_tensor.shape[1]
        if using_static_cache: target_length = past_key_values.get_max_length()
        else: target_length = (attention_mask.shape[-1] if isinstance(attention_mask, torch.Tensor) else past_seen_tokens + sequence_length + 1)
        causal_mask = _prepare_4d_causal_attention_mask_with_cache_position(attention_mask, sequence_length=sequence_length, target_length=target_length, dtype=dtype,
        device=device, min_dtype=min_dtype, cache_position=cache_position, batch_size=input_tensor.shape[0])
        if (self.config._attn_implementation == "sdpa" and attention_mask is not None and attention_mask.device.type == "cuda" and not output_attentions): causal_mask = AttentionMaskConverter._unmask_unattended(causal_mask, min_dtype)
        return causal_mask
class MimiDecoder(nn.Module):
    def __init__(self, config: MimiConfig):
        super().__init__()
        scaling = int(2 ** len(config.upsampling_ratios))
        model = [MimiConv1d(config, config.hidden_size, scaling * config.num_filters, config.kernel_size)]
        for ratio in config.upsampling_ratios:
            current_scale = scaling * config.num_filters
            model += [nn.ELU()]
            model += [MimiConvTranspose1d(config, current_scale, current_scale // 2, kernel_size=ratio * 2, stride=ratio)]
            for j in range(config.num_residual_layers): model += [MimiResnetBlock(config, current_scale // 2, (config.dilation_growth_rate**j, 1))]
            scaling //= 2
        model += [nn.ELU()]
        model += [MimiConv1d(config, config.num_filters, config.audio_channels, config.last_kernel_size)]
        self.layers = nn.ModuleList(model)
    def forward(self, hidden_states):
        for layer in self.layers: hidden_states = layer(hidden_states)
        return hidden_states
class MimiEuclideanCodebook(nn.Module):
    def __init__(self, config: MimiConfig, epsilon: float = 1e-5):
        super().__init__()
        embed = torch.zeros(config.codebook_size, config.codebook_dim)
        self.codebook_size = config.codebook_size
        self.register_buffer("initialized", torch.Tensor([True]))
        self.register_buffer("cluster_usage", torch.ones(config.codebook_size))
        self.register_buffer("embed_sum", embed)
        self._embed = None
        self.epsilon = epsilon
    @property
    def embed(self) -> torch.Tensor:
        if self._embed is None: self._embed = self.embed_sum / self.cluster_usage.clamp(min=self.epsilon)[:, None]
        return self._embed
    def quantize(self, hidden_states):
        dists = torch.cdist(hidden_states[None], self.embed[None], p=2)[0]
        embed_ind = dists.argmin(dim=-1)
        return embed_ind
    def encode(self, hidden_states):
        shape = hidden_states.shape
        hidden_states = hidden_states.reshape((-1, shape[-1]))
        embed_ind = self.quantize(hidden_states)
        embed_ind = embed_ind.view(*shape[:-1])
        return embed_ind
    def decode(self, embed_ind):
        quantize = nn.functional.embedding(embed_ind, self.embed)
        return quantize
class MimiVectorQuantization(nn.Module):
    def __init__(self, config: MimiConfig):
        super().__init__()
        self.codebook = MimiEuclideanCodebook(config)
    def encode(self, hidden_states):
        hidden_states = hidden_states.permute(0, 2, 1)
        embed_in = self.codebook.encode(hidden_states)
        return embed_in
    def decode(self, embed_ind):
        quantize = self.codebook.decode(embed_ind)
        quantize = quantize.permute(0, 2, 1)
        return quantize
class MimiResidualVectorQuantizer(nn.Module):
    def __init__(self, config: MimiConfig, num_quantizers: int = None):
        super().__init__()
        self.codebook_size = config.codebook_size
        self.frame_rate = config.frame_rate
        self.num_quantizers = num_quantizers if num_quantizers is not None else config.num_quantizers
        self.layers = nn.ModuleList([MimiVectorQuantization(config) for _ in range(self.num_quantizers)])
        self.input_proj = None
        self.output_proj = None
        if config.vector_quantization_hidden_dimension != config.hidden_size:
            self.input_proj = torch.nn.Conv1d(config.hidden_size, config.vector_quantization_hidden_dimension, 1, bias=False)
            self.output_proj = torch.nn.Conv1d(config.vector_quantization_hidden_dimension, config.hidden_size, 1, bias=False)
    def encode(self, embeddings: torch.Tensor, num_quantizers: Optional[int] = None) -> torch.Tensor:
        if self.input_proj is not None: embeddings = self.input_proj(embeddings)
        num_quantizers = num_quantizers if num_quantizers is not None else self.num_quantizers
        residual = embeddings
        all_indices = []
        for layer in self.layers[:num_quantizers]:
            indices = layer.encode(residual)
            quantized = layer.decode(indices)
            residual = residual - quantized
            all_indices.append(indices)
        out_indices = torch.stack(all_indices)
        return out_indices
    def decode(self, codes: torch.Tensor) -> torch.Tensor:
        quantized_out = torch.tensor(0.0, device=codes.device)
        codes = codes.transpose(0, 1)
        for i, indices in enumerate(codes):
            layer = self.layers[i]
            quantized = layer.decode(indices)
            quantized_out = quantized_out + quantized
        if self.output_proj is not None: quantized_out = self.output_proj(quantized_out)
        return quantized_out
class MimiSplitResidualVectorQuantizer(nn.Module):
    def __init__(self, config: MimiConfig):
        super().__init__()
        self.codebook_size = config.codebook_size
        self.frame_rate = config.frame_rate
        self.max_num_quantizers = config.num_quantizers
        self.num_semantic_quantizers = config.num_semantic_quantizers
        self.num_acoustic_quantizers = config.num_quantizers - config.num_semantic_quantizers
        self.semantic_residual_vector_quantizer = MimiResidualVectorQuantizer(config, self.num_semantic_quantizers)
        self.acoustic_residual_vector_quantizer = MimiResidualVectorQuantizer(config, self.num_acoustic_quantizers)
    def encode(self, embeddings: torch.Tensor, num_quantizers: Optional[float] = None) -> torch.Tensor:
        num_quantizers = self.max_num_quantizers if num_quantizers is None else num_quantizers
        if num_quantizers > self.max_num_quantizers: raise ValueError(f"The number of quantizers (i.e codebooks) asked should be lower than the total number of quantizers {self.max_num_quantizers}, but is currently {num_quantizers}.")
        if num_quantizers < self.num_semantic_quantizers: raise ValueError(f"The number of quantizers (i.e codebooks) asked should be higher than the number of semantic quantizers {self.num_semantic_quantizers}, but is currently {num_quantizers}.")
        codes = self.semantic_residual_vector_quantizer.encode(embeddings)
        if num_quantizers > self.num_semantic_quantizers:
            acoustic_codes = self.acoustic_residual_vector_quantizer.encode(embeddings, num_quantizers=num_quantizers - self.num_semantic_quantizers)
            codes = torch.cat([codes, acoustic_codes], dim=0)
        return codes
    def decode(self, codes: torch.Tensor) -> torch.Tensor:
        quantized_out = self.semantic_residual_vector_quantizer.decode(codes[:, : self.num_semantic_quantizers])
        if codes.shape[1] > self.num_semantic_quantizers: quantized_out += self.acoustic_residual_vector_quantizer.decode(codes[:, self.num_semantic_quantizers :])
        return quantized_out
class MimiPreTrainedModel(PreTrainedModel):
    config_class = MimiConfig
    base_model_prefix = "mimi"
    main_input_name = "input_values"
    supports_gradient_checkpointing = True
    _no_split_modules = ["MimiDecoderLayer"]
    _skip_keys_device_placement = "past_key_values"
    _supports_flash_attn_2 = True
    _supports_sdpa = True
    _supports_cache_class = True
    _supports_static_cache = True
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, (nn.LayerNorm, nn.GroupNorm)):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
        elif isinstance(module, nn.Conv1d):
            nn.init.kaiming_normal_(module.weight)
            if module.bias is not None:
                k = math.sqrt(module.groups / (module.in_channels * module.kernel_size[0]))
                nn.init.uniform_(module.bias, a=-k, b=k)
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.LSTM):
            for name, param in module.named_parameters():
                if "weight" in name: nn.init.xavier_uniform_(param)
                elif "bias" in name: nn.init.constant_(param, 0.0)
MIMI_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`MimiConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
MIMI_INPUTS_DOCSTRING = r"""
    Args:
        input_values (`torch.FloatTensor` of shape `(batch_size, channels, sequence_length)`, *optional*):
            Raw audio input converted to Float.
        padding_mask (`torch.Tensor` of shape `(batch_size, sequence_length)`, *optional*):
            Indicates which inputs are to be ignored due to padding, where elements are either 1 for *not masked* or 0
            for *masked*.
        num_quantizers (`int`, *optional*):
            Number of quantizers (i.e codebooks) to use. By default, all quantizers are used.
        audio_codes (`torch.LongTensor`  of shape `(batch_size, num_quantizers, codes_length)`, *optional*):
            Discret code embeddings computed using `model.encode`.
        encoder_past_key_values (`Cache`, *optional*):
            Pre-computed hidden-states (key and values in the self-attention blocks) that can be used to speed up sequential decoding of the encoder transformer.
            This typically consists in the `past_key_values` returned by the model at a previous stage of decoding, when `use_cache=True` or `config.use_cache=True`.
            The model will output the same cache format that is fed as input.
            If `past_key_values` are used, the user can optionally input only the last `audio_values` or `audio_codes (those that don't
            have their past key value states given to this model).
        decoder_past_key_values (`Cache`, *optional*):
            Pre-computed hidden-states (key and values in the self-attention blocks) that can be used to speed up sequential decoding of the decoder transformer.
            This typically consists in the `past_key_values` returned by the model at a previous stage of decoding, when `use_cache=True` or `config.use_cache=True`.
            The model will output the same cache format that is fed as input.
            If `past_key_values` are used, the user can optionally input only the last `audio_values` or `audio_codes (those that don't
            have their past key value states given to this model).
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
@add_start_docstrings("The Mimi neural audio codec model.", MIMI_START_DOCSTRING)
class MimiModel(MimiPreTrainedModel):
    def __init__(self, config: MimiConfig):
        super().__init__(config)
        self.config = config
        self.encoder = MimiEncoder(config)
        self.encoder_transformer = MimiTransformerModel(config)
        self.downsample = None
        self.upsample = None
        if config.frame_rate != config.encodec_frame_rate:
            self.downsample = MimiConv1d(config, config.hidden_size, config.hidden_size, kernel_size=2 * int(config.encodec_frame_rate / config.frame_rate), stride=2,
            bias=False, pad_mode="replicate")
            self.upsample = MimiConvTranspose1d(config, config.hidden_size, config.hidden_size, kernel_size=2 * int(config.encodec_frame_rate / config.frame_rate),
            stride=2, bias=False, groups=config.upsample_groups)
        self.decoder_transformer = MimiTransformerModel(config)
        self.decoder = MimiDecoder(config)
        self.quantizer = MimiSplitResidualVectorQuantizer(config)
        self.bits_per_codebook = int(math.log2(self.config.codebook_size))
        if 2**self.bits_per_codebook != self.config.codebook_size: raise ValueError("The codebook_size must be a power of 2.")
        self.post_init()
    def get_encoder(self): return self.encoder
    def get_decoder(self): return self.decoder
    def _encode_frame(self, input_values: torch.Tensor, num_quantizers: int, padding_mask: int, past_key_values: Optional[Union[Cache, List[torch.FloatTensor]]] = None,
    return_dict: Optional[bool] = None) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        embeddings = self.encoder(input_values)
        encoder_outputs = self.encoder_transformer(embeddings.transpose(1, 2), past_key_values=past_key_values, return_dict=return_dict)
        if return_dict: past_key_values = encoder_outputs.get("past_key_values")
        elif len(encoder_outputs) > 1: past_key_values = encoder_outputs[1]
        embeddings = encoder_outputs[0].transpose(1, 2)
        embeddings = self.downsample(embeddings)
        codes = self.quantizer.encode(embeddings, num_quantizers)
        codes = codes.transpose(0, 1)
        return codes, past_key_values
    def encode(self, input_values: torch.Tensor, padding_mask: torch.Tensor = None, num_quantizers: Optional[float] = None, encoder_past_key_values: Optional[Union[Cache, List[torch.FloatTensor]]] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple[torch.Tensor, Optional[torch.Tensor]], MimiEncoderOutput]:
        return_dict = return_dict if return_dict is not None else self.config.return_dict
        num_quantizers = self.config.num_quantizers if num_quantizers is None else num_quantizers
        if num_quantizers > self.config.num_quantizers: raise ValueError(f"The number of quantizers (i.e codebooks) asked should be lower than the total number of quantizers {self.config.num_quantizers}, but is currently {num_quantizers}.")
        _, channels, input_length = input_values.shape
        if channels < 1 or channels > 2: raise ValueError(f"Number of audio channels must be 1 or 2, but got {channels}")
        if padding_mask is None: padding_mask = torch.ones_like(input_values).bool()
        encoded_frames, encoder_past_key_values = self._encode_frame(input_values, num_quantizers, padding_mask.bool(), past_key_values=encoder_past_key_values, return_dict=return_dict)
        if not return_dict: return (encoded_frames, encoder_past_key_values)
        return MimiEncoderOutput(encoded_frames, encoder_past_key_values)
    def _decode_frame(self, codes: torch.Tensor, past_key_values: Optional[Union[Cache, List[torch.FloatTensor]]] = None, return_dict: Optional[bool] = None) -> torch.Tensor:
        embeddings = self.quantizer.decode(codes)
        embeddings = self.upsample(embeddings)
        decoder_outputs = self.decoder_transformer(embeddings.transpose(1, 2), past_key_values=past_key_values, return_dict=return_dict)
        if return_dict: past_key_values = decoder_outputs.get("past_key_values")
        elif len(decoder_outputs) > 1: past_key_values = decoder_outputs[1]
        embeddings = decoder_outputs[0].transpose(1, 2)
        outputs = self.decoder(embeddings)
        return outputs, past_key_values
    def decode(self, audio_codes: torch.Tensor, padding_mask: Optional[torch.Tensor] = None, decoder_past_key_values: Optional[Union[Cache, List[torch.FloatTensor]]] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple[torch.Tensor, torch.Tensor], MimiDecoderOutput]:
        return_dict = return_dict if return_dict is not None else self.config.return_dict
        audio_values, decoder_past_key_values = self._decode_frame(audio_codes, past_key_values=decoder_past_key_values, return_dict=return_dict)
        if padding_mask is not None and padding_mask.shape[-1] < audio_values.shape[-1]: audio_values = audio_values[..., : padding_mask.shape[-1]]
        if not return_dict: return (audio_values, decoder_past_key_values)
        return MimiDecoderOutput(audio_values, decoder_past_key_values)
    @add_start_docstrings_to_model_forward(MIMI_INPUTS_DOCSTRING)
    def forward(self, input_values: torch.Tensor, padding_mask: Optional[torch.Tensor] = None, num_quantizers: Optional[int] = None, audio_codes: Optional[torch.Tensor] = None,
    encoder_past_key_values: Optional[Union[Cache, List[torch.FloatTensor]]] = None, decoder_past_key_values: Optional[Union[Cache, List[torch.FloatTensor]]] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple[torch.Tensor, torch.Tensor], MimiOutput]:
        return_dict = return_dict if return_dict is not None else self.config.return_dict
        if padding_mask is None: padding_mask = torch.ones_like(input_values).bool()
        if audio_codes is None:
            encoder_outputs = self.encode(input_values, padding_mask, num_quantizers, encoder_past_key_values, return_dict=return_dict)
            audio_codes = encoder_outputs[0]
            if return_dict: encoder_past_key_values = encoder_outputs.get("past_key_values")
            elif len(encoder_outputs) > 1: encoder_past_key_values = encoder_outputs[1]
        decoder_outputs = self.decode(audio_codes, padding_mask, decoder_past_key_values, return_dict=return_dict)
        audio_values = decoder_outputs[0]
        if return_dict: decoder_past_key_values = decoder_outputs.get("past_key_values")
        elif len(decoder_outputs) > 1: decoder_past_key_values = decoder_outputs[1]
        if not return_dict: return (audio_codes, audio_values, encoder_past_key_values, decoder_past_key_values)
        return MimiOutput(audio_codes=audio_codes, audio_values=audio_values, encoder_past_key_values=encoder_past_key_values, decoder_past_key_values=decoder_past_key_values)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
