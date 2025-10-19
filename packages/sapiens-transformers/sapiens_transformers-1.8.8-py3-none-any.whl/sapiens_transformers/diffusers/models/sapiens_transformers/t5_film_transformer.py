'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...configuration_utils import ConfigMixin, register_to_config
from ..embeddings import get_timestep_embedding
from ..attention_processor import Attention
from ..modeling_utils import ModelMixin
from typing import Optional, Tuple
from torch import nn
import torch
import math
class T5FilmDecoder(ModelMixin, ConfigMixin):
    """Args:"""
    @register_to_config
    def __init__(self, input_dims: int=128, targets_length: int=256, max_decoder_noise_time: float=2000.0, d_model: int=768, num_layers: int=12,
    num_heads: int=12, d_kv: int=64, d_ff: int=2048, dropout_rate: float=0.1):
        super().__init__()
        self.conditioning_emb = nn.Sequential(nn.Linear(d_model, d_model * 4, bias=False), nn.SiLU(), nn.Linear(d_model * 4, d_model * 4, bias=False), nn.SiLU())
        self.position_encoding = nn.Embedding(targets_length, d_model)
        self.position_encoding.weight.requires_grad = False
        self.continuous_inputs_projection = nn.Linear(input_dims, d_model, bias=False)
        self.dropout = nn.Dropout(p=dropout_rate)
        self.decoders = nn.ModuleList()
        for lyr_num in range(num_layers):
            lyr = DecoderLayer(d_model=d_model, d_kv=d_kv, num_heads=num_heads, d_ff=d_ff, dropout_rate=dropout_rate)
            self.decoders.append(lyr)
        self.decoder_norm = T5LayerNorm(d_model)
        self.post_dropout = nn.Dropout(p=dropout_rate)
        self.spec_out = nn.Linear(d_model, input_dims, bias=False)
    def encoder_decoder_mask(self, query_input: torch.Tensor, key_input: torch.Tensor) -> torch.Tensor:
        mask = torch.mul(query_input.unsqueeze(-1), key_input.unsqueeze(-2))
        return mask.unsqueeze(-3)
    def forward(self, encodings_and_masks, decoder_input_tokens, decoder_noise_time):
        batch, _, _ = decoder_input_tokens.shape
        assert decoder_noise_time.shape == (batch,)
        time_steps = get_timestep_embedding(decoder_noise_time * self.config.max_decoder_noise_time, embedding_dim=self.config.d_model, max_period=self.config.max_decoder_noise_time).to(dtype=self.dtype)
        conditioning_emb = self.conditioning_emb(time_steps).unsqueeze(1)
        assert conditioning_emb.shape == (batch, 1, self.config.d_model * 4)
        seq_length = decoder_input_tokens.shape[1]
        decoder_positions = torch.broadcast_to(torch.arange(seq_length, device=decoder_input_tokens.device), (batch, seq_length))
        position_encodings = self.position_encoding(decoder_positions)
        inputs = self.continuous_inputs_projection(decoder_input_tokens)
        inputs += position_encodings
        y = self.dropout(inputs)
        decoder_mask = torch.ones(decoder_input_tokens.shape[:2], device=decoder_input_tokens.device, dtype=inputs.dtype)
        encodings_and_encdec_masks = [(x, self.encoder_decoder_mask(decoder_mask, y)) for x, y in encodings_and_masks]
        encoded = torch.cat([x[0] for x in encodings_and_encdec_masks], dim=1)
        encoder_decoder_mask = torch.cat([x[1] for x in encodings_and_encdec_masks], dim=-1)
        for lyr in self.decoders: y = lyr(y, conditioning_emb=conditioning_emb, encoder_hidden_states=encoded, encoder_attention_mask=encoder_decoder_mask)[0]
        y = self.decoder_norm(y)
        y = self.post_dropout(y)
        spec_out = self.spec_out(y)
        return spec_out
class DecoderLayer(nn.Module):
    """Args:"""
    def __init__(self, d_model: int, d_kv: int, num_heads: int, d_ff: int, dropout_rate: float, layer_norm_epsilon: float=1e-06):
        super().__init__()
        self.layer = nn.ModuleList()
        self.layer.append(T5LayerSelfAttentionCond(d_model=d_model, d_kv=d_kv, num_heads=num_heads, dropout_rate=dropout_rate))
        self.layer.append(T5LayerCrossAttention(d_model=d_model, d_kv=d_kv, num_heads=num_heads, dropout_rate=dropout_rate, layer_norm_epsilon=layer_norm_epsilon))
        self.layer.append(T5LayerFFCond(d_model=d_model, d_ff=d_ff, dropout_rate=dropout_rate, layer_norm_epsilon=layer_norm_epsilon))
    def forward(self, hidden_states: torch.Tensor, conditioning_emb: Optional[torch.Tensor]=None, attention_mask: Optional[torch.Tensor]=None, encoder_hidden_states: Optional[torch.Tensor]=None,
    encoder_attention_mask: Optional[torch.Tensor]=None, encoder_decoder_position_bias=None) -> Tuple[torch.Tensor]:
        hidden_states = self.layer[0](hidden_states, conditioning_emb=conditioning_emb, attention_mask=attention_mask)
        if encoder_hidden_states is not None:
            encoder_extended_attention_mask = torch.where(encoder_attention_mask > 0, 0, -10000000000.0).to(encoder_hidden_states.dtype)
            hidden_states = self.layer[1](hidden_states, key_value_states=encoder_hidden_states, attention_mask=encoder_extended_attention_mask)
        hidden_states = self.layer[-1](hidden_states, conditioning_emb)
        return (hidden_states,)
class T5LayerSelfAttentionCond(nn.Module):
    """Args:"""
    def __init__(self, d_model: int, d_kv: int, num_heads: int, dropout_rate: float):
        super().__init__()
        self.layer_norm = T5LayerNorm(d_model)
        self.FiLMLayer = T5FiLMLayer(in_features=d_model * 4, out_features=d_model)
        self.attention = Attention(query_dim=d_model, heads=num_heads, dim_head=d_kv, out_bias=False, scale_qk=False)
        self.dropout = nn.Dropout(dropout_rate)
    def forward(self, hidden_states: torch.Tensor, conditioning_emb: Optional[torch.Tensor]=None, attention_mask: Optional[torch.Tensor]=None) -> torch.Tensor:
        normed_hidden_states = self.layer_norm(hidden_states)
        if conditioning_emb is not None: normed_hidden_states = self.FiLMLayer(normed_hidden_states, conditioning_emb)
        attention_output = self.attention(normed_hidden_states)
        hidden_states = hidden_states + self.dropout(attention_output)
        return hidden_states
class T5LayerCrossAttention(nn.Module):
    """Args:"""
    def __init__(self, d_model: int, d_kv: int, num_heads: int, dropout_rate: float, layer_norm_epsilon: float):
        super().__init__()
        self.attention = Attention(query_dim=d_model, heads=num_heads, dim_head=d_kv, out_bias=False, scale_qk=False)
        self.layer_norm = T5LayerNorm(d_model, eps=layer_norm_epsilon)
        self.dropout = nn.Dropout(dropout_rate)
    def forward(self, hidden_states: torch.Tensor, key_value_states: Optional[torch.Tensor]=None, attention_mask: Optional[torch.Tensor]=None) -> torch.Tensor:
        normed_hidden_states = self.layer_norm(hidden_states)
        attention_output = self.attention(normed_hidden_states, encoder_hidden_states=key_value_states, attention_mask=attention_mask.squeeze(1))
        layer_output = hidden_states + self.dropout(attention_output)
        return layer_output
class T5LayerFFCond(nn.Module):
    """Args:"""
    def __init__(self, d_model: int, d_ff: int, dropout_rate: float, layer_norm_epsilon: float):
        super().__init__()
        self.DenseReluDense = T5DenseGatedActDense(d_model=d_model, d_ff=d_ff, dropout_rate=dropout_rate)
        self.film = T5FiLMLayer(in_features=d_model * 4, out_features=d_model)
        self.layer_norm = T5LayerNorm(d_model, eps=layer_norm_epsilon)
        self.dropout = nn.Dropout(dropout_rate)
    def forward(self, hidden_states: torch.Tensor, conditioning_emb: Optional[torch.Tensor]=None) -> torch.Tensor:
        forwarded_states = self.layer_norm(hidden_states)
        if conditioning_emb is not None: forwarded_states = self.film(forwarded_states, conditioning_emb)
        forwarded_states = self.DenseReluDense(forwarded_states)
        hidden_states = hidden_states + self.dropout(forwarded_states)
        return hidden_states
class T5DenseGatedActDense(nn.Module):
    """Args:"""
    def __init__(self, d_model: int, d_ff: int, dropout_rate: float):
        super().__init__()
        self.wi_0 = nn.Linear(d_model, d_ff, bias=False)
        self.wi_1 = nn.Linear(d_model, d_ff, bias=False)
        self.wo = nn.Linear(d_ff, d_model, bias=False)
        self.dropout = nn.Dropout(dropout_rate)
        self.act = NewGELUActivation()
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_gelu = self.act(self.wi_0(hidden_states))
        hidden_linear = self.wi_1(hidden_states)
        hidden_states = hidden_gelu * hidden_linear
        hidden_states = self.dropout(hidden_states)
        hidden_states = self.wo(hidden_states)
        return hidden_states
class T5LayerNorm(nn.Module):
    """Args:"""
    def __init__(self, hidden_size: int, eps: float=1e-06):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size))
        self.variance_epsilon = eps
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        variance = hidden_states.to(torch.float32).pow(2).mean(-1, keepdim=True)
        hidden_states = hidden_states * torch.rsqrt(variance + self.variance_epsilon)
        if self.weight.dtype in [torch.float16, torch.bfloat16]: hidden_states = hidden_states.to(self.weight.dtype)
        return self.weight * hidden_states
class NewGELUActivation(nn.Module):
    def forward(self, input: torch.Tensor) -> torch.Tensor: return 0.5 * input * (1.0 + torch.tanh(math.sqrt(2.0 / math.pi) * (input + 0.044715 * torch.pow(input, 3.0))))
class T5FiLMLayer(nn.Module):
    """Args:"""
    def __init__(self, in_features: int, out_features: int):
        super().__init__()
        self.scale_bias = nn.Linear(in_features, out_features * 2, bias=False)
    def forward(self, x: torch.Tensor, conditioning_emb: torch.Tensor) -> torch.Tensor:
        emb = self.scale_bias(conditioning_emb)
        scale, shift = torch.chunk(emb, 2, -1)
        x = x * (1 + scale) + shift
        return x
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
