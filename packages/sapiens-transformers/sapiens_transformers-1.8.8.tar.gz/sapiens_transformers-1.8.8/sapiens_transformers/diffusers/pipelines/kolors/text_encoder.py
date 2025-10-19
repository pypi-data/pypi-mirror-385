'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import math
from typing import List, Optional, Tuple
import torch
import torch.nn.functional as F
from torch import nn
from torch.nn import LayerNorm
from torch.nn.utils import skip_init
from sapiens_transformers import PretrainedConfig, PreTrainedModel
from sapiens_transformers.modeling_outputs import BaseModelOutputWithPast
class ChatGLMConfig(PretrainedConfig):
    model_type = 'chatglm'
    def __init__(self, num_layers=28, padded_vocab_size=65024, hidden_size=4096, ffn_hidden_size=13696, kv_channels=128, num_attention_heads=32, seq_length=2048, hidden_dropout=0.0,
    classifier_dropout=None, attention_dropout=0.0, layernorm_epsilon=1e-05, rmsnorm=True, apply_residual_connection_post_layernorm=False, post_layer_norm=True, add_bias_linear=False,
    add_qkv_bias=False, bias_dropout_fusion=True, multi_query_attention=False, multi_query_group_num=1, apply_query_key_layer_scaling=True, attention_softmax_in_fp32=True,
    fp32_residual_connection=False, quantization_bit=0, pre_seq_len=None, prefix_projection=False, **kwargs):
        self.num_layers = num_layers
        self.vocab_size = padded_vocab_size
        self.padded_vocab_size = padded_vocab_size
        self.hidden_size = hidden_size
        self.ffn_hidden_size = ffn_hidden_size
        self.kv_channels = kv_channels
        self.num_attention_heads = num_attention_heads
        self.seq_length = seq_length
        self.hidden_dropout = hidden_dropout
        self.classifier_dropout = classifier_dropout
        self.attention_dropout = attention_dropout
        self.layernorm_epsilon = layernorm_epsilon
        self.rmsnorm = rmsnorm
        self.apply_residual_connection_post_layernorm = apply_residual_connection_post_layernorm
        self.post_layer_norm = post_layer_norm
        self.add_bias_linear = add_bias_linear
        self.add_qkv_bias = add_qkv_bias
        self.bias_dropout_fusion = bias_dropout_fusion
        self.multi_query_attention = multi_query_attention
        self.multi_query_group_num = multi_query_group_num
        self.apply_query_key_layer_scaling = apply_query_key_layer_scaling
        self.attention_softmax_in_fp32 = attention_softmax_in_fp32
        self.fp32_residual_connection = fp32_residual_connection
        self.quantization_bit = quantization_bit
        self.pre_seq_len = pre_seq_len
        self.prefix_projection = prefix_projection
        super().__init__(**kwargs)
class RMSNorm(torch.nn.Module):
    def __init__(self, normalized_shape, eps=1e-05, device=None, dtype=None, **kwargs):
        super().__init__()
        self.weight = torch.nn.Parameter(torch.empty(normalized_shape, device=device, dtype=dtype))
        self.eps = eps
    def forward(self, hidden_states: torch.Tensor):
        input_dtype = hidden_states.dtype
        variance = hidden_states.to(torch.float32).pow(2).mean(-1, keepdim=True)
        hidden_states = hidden_states * torch.rsqrt(variance + self.eps)
        return (self.weight * hidden_states).to(input_dtype)
def _config_to_kwargs(args):
    common_kwargs = {'dtype': args.torch_dtype}
    return common_kwargs
class CoreAttention(torch.nn.Module):
    def __init__(self, config: ChatGLMConfig, layer_number):
        super(CoreAttention, self).__init__()
        self.apply_query_key_layer_scaling = config.apply_query_key_layer_scaling
        self.attention_softmax_in_fp32 = config.attention_softmax_in_fp32
        if self.apply_query_key_layer_scaling: self.attention_softmax_in_fp32 = True
        self.layer_number = max(1, layer_number)
        projection_size = config.kv_channels * config.num_attention_heads
        self.hidden_size_per_partition = projection_size
        self.hidden_size_per_attention_head = projection_size // config.num_attention_heads
        self.num_attention_heads_per_partition = config.num_attention_heads
        coeff = None
        self.norm_factor = math.sqrt(self.hidden_size_per_attention_head)
        if self.apply_query_key_layer_scaling:
            coeff = self.layer_number
            self.norm_factor *= coeff
        self.coeff = coeff
        self.attention_dropout = torch.nn.Dropout(config.attention_dropout)
    def forward(self, query_layer, key_layer, value_layer, attention_mask):
        pytorch_major_version = int(torch.__version__.split('.')[0])
        if pytorch_major_version >= 2:
            query_layer, key_layer, value_layer = [k.permute(1, 2, 0, 3) for k in [query_layer, key_layer, value_layer]]
            if attention_mask is None and query_layer.shape[2] == key_layer.shape[2]: context_layer = torch.nn.functional.scaled_dot_product_attention(query_layer, key_layer, value_layer, is_causal=True)
            else:
                if attention_mask is not None: attention_mask = ~attention_mask
                context_layer = torch.nn.functional.scaled_dot_product_attention(query_layer, key_layer, value_layer, attention_mask)
            context_layer = context_layer.permute(2, 0, 1, 3)
            new_context_layer_shape = context_layer.size()[:-2] + (self.hidden_size_per_partition,)
            context_layer = context_layer.reshape(*new_context_layer_shape)
        else:
            output_size = (query_layer.size(1), query_layer.size(2), query_layer.size(0), key_layer.size(0))
            query_layer = query_layer.view(output_size[2], output_size[0] * output_size[1], -1)
            key_layer = key_layer.view(output_size[3], output_size[0] * output_size[1], -1)
            matmul_input_buffer = torch.empty(output_size[0] * output_size[1], output_size[2], output_size[3], dtype=query_layer.dtype, device=query_layer.device)
            matmul_result = torch.baddbmm(matmul_input_buffer, query_layer.transpose(0, 1), key_layer.transpose(0, 1).transpose(1, 2), beta=0.0, alpha=1.0 / self.norm_factor)
            attention_scores = matmul_result.view(*output_size)
            if self.attention_softmax_in_fp32: attention_scores = attention_scores.float()
            if self.coeff is not None: attention_scores = attention_scores * self.coeff
            if attention_mask is None and attention_scores.shape[2] == attention_scores.shape[3]:
                attention_mask = torch.ones(output_size[0], 1, output_size[2], output_size[3], device=attention_scores.device, dtype=torch.bool)
                attention_mask.tril_()
                attention_mask = ~attention_mask
            if attention_mask is not None: attention_scores = attention_scores.masked_fill(attention_mask, float('-inf'))
            attention_probs = F.softmax(attention_scores, dim=-1)
            attention_probs = attention_probs.type_as(value_layer)
            attention_probs = self.attention_dropout(attention_probs)
            output_size = (value_layer.size(1), value_layer.size(2), query_layer.size(0), value_layer.size(3))
            value_layer = value_layer.view(value_layer.size(0), output_size[0] * output_size[1], -1)
            attention_probs = attention_probs.view(output_size[0] * output_size[1], output_size[2], -1)
            context_layer = torch.bmm(attention_probs, value_layer.transpose(0, 1))
            context_layer = context_layer.view(*output_size)
            context_layer = context_layer.permute(2, 0, 1, 3).contiguous()
            new_context_layer_shape = context_layer.size()[:-2] + (self.hidden_size_per_partition,)
            context_layer = context_layer.view(*new_context_layer_shape)
        return context_layer
def split_tensor_along_last_dim(tensor: torch.Tensor, num_partitions: int, contiguous_split_chunks: bool=False) -> List[torch.Tensor]:
    """Returns:"""
    last_dim = tensor.dim() - 1
    last_dim_size = tensor.size()[last_dim] // num_partitions
    tensor_list = torch.split(tensor, last_dim_size, dim=last_dim)
    if contiguous_split_chunks: return tuple((chunk.contiguous() for chunk in tensor_list))
    return tensor_list
@torch.jit.script
def apply_rotary_pos_emb(x: torch.Tensor, rope_cache: torch.Tensor) -> torch.Tensor:
    sq, _b, np, _hn = (x.size(0), x.size(1), x.size(2), x.size(3))
    rot_dim = rope_cache.shape[-2] * 2
    x, x_pass = (x[..., :rot_dim], x[..., rot_dim:])
    rope_cache = rope_cache[:sq]
    xshaped = x.reshape(sq, -1, np, rot_dim // 2, 2)
    rope_cache = rope_cache.view(sq, -1, 1, xshaped.size(3), 2)
    x_out2 = torch.stack([xshaped[..., 0] * rope_cache[..., 0] - xshaped[..., 1] * rope_cache[..., 1], xshaped[..., 1] * rope_cache[..., 0] + xshaped[..., 0] * rope_cache[..., 1]], -1)
    x_out2 = x_out2.flatten(3)
    return torch.cat((x_out2, x_pass), dim=-1)
class SelfAttention(torch.nn.Module):
    def __init__(self, config: ChatGLMConfig, layer_number, device=None):
        super(SelfAttention, self).__init__()
        self.layer_number = max(1, layer_number)
        self.projection_size = config.kv_channels * config.num_attention_heads
        self.hidden_size_per_attention_head = self.projection_size // config.num_attention_heads
        self.num_attention_heads_per_partition = config.num_attention_heads
        self.multi_query_attention = config.multi_query_attention
        self.qkv_hidden_size = 3 * self.projection_size
        if self.multi_query_attention:
            self.num_multi_query_groups_per_partition = config.multi_query_group_num
            self.qkv_hidden_size = self.projection_size + 2 * self.hidden_size_per_attention_head * config.multi_query_group_num
        self.query_key_value = nn.Linear(config.hidden_size, self.qkv_hidden_size, bias=config.add_bias_linear or config.add_qkv_bias, device=device, **_config_to_kwargs(config))
        self.core_attention = CoreAttention(config, self.layer_number)
        self.dense = nn.Linear(self.projection_size, config.hidden_size, bias=config.add_bias_linear, device=device, **_config_to_kwargs(config))
    def _allocate_memory(self, inference_max_sequence_len, batch_size, device=None, dtype=None):
        if self.multi_query_attention: num_attention_heads = self.num_multi_query_groups_per_partition
        else: num_attention_heads = self.num_attention_heads_per_partition
        return torch.empty(inference_max_sequence_len, batch_size, num_attention_heads, self.hidden_size_per_attention_head, dtype=dtype, device=device)
    def forward(self, hidden_states, attention_mask, rotary_pos_emb, kv_cache=None, use_cache=True):
        mixed_x_layer = self.query_key_value(hidden_states)
        if self.multi_query_attention:
            query_layer, key_layer, value_layer = mixed_x_layer.split([self.num_attention_heads_per_partition * self.hidden_size_per_attention_head,
            self.num_multi_query_groups_per_partition * self.hidden_size_per_attention_head,
            self.num_multi_query_groups_per_partition * self.hidden_size_per_attention_head], dim=-1)
            query_layer = query_layer.view(query_layer.size()[:-1] + (self.num_attention_heads_per_partition, self.hidden_size_per_attention_head))
            key_layer = key_layer.view(key_layer.size()[:-1] + (self.num_multi_query_groups_per_partition, self.hidden_size_per_attention_head))
            value_layer = value_layer.view(value_layer.size()[:-1] + (self.num_multi_query_groups_per_partition, self.hidden_size_per_attention_head))
        else:
            new_tensor_shape = mixed_x_layer.size()[:-1] + (self.num_attention_heads_per_partition, 3 * self.hidden_size_per_attention_head)
            mixed_x_layer = mixed_x_layer.view(*new_tensor_shape)
            query_layer, key_layer, value_layer = split_tensor_along_last_dim(mixed_x_layer, 3)
        if rotary_pos_emb is not None:
            query_layer = apply_rotary_pos_emb(query_layer, rotary_pos_emb)
            key_layer = apply_rotary_pos_emb(key_layer, rotary_pos_emb)
        if kv_cache is not None:
            cache_k, cache_v = kv_cache
            key_layer = torch.cat((cache_k, key_layer), dim=0)
            value_layer = torch.cat((cache_v, value_layer), dim=0)
        if use_cache: kv_cache = (key_layer, value_layer)
        else: kv_cache = None
        if self.multi_query_attention:
            key_layer = key_layer.unsqueeze(-2)
            key_layer = key_layer.expand(-1, -1, -1, self.num_attention_heads_per_partition // self.num_multi_query_groups_per_partition, -1)
            key_layer = key_layer.contiguous().view(key_layer.size()[:2] + (self.num_attention_heads_per_partition, self.hidden_size_per_attention_head))
            value_layer = value_layer.unsqueeze(-2)
            value_layer = value_layer.expand(-1, -1, -1, self.num_attention_heads_per_partition // self.num_multi_query_groups_per_partition, -1)
            value_layer = value_layer.contiguous().view(value_layer.size()[:2] + (self.num_attention_heads_per_partition, self.hidden_size_per_attention_head))
        context_layer = self.core_attention(query_layer, key_layer, value_layer, attention_mask)
        output = self.dense(context_layer)
        return (output, kv_cache)
class MLP(torch.nn.Module):
    def __init__(self, config: ChatGLMConfig, device=None):
        super(MLP, self).__init__()
        self.add_bias = config.add_bias_linear
        self.dense_h_to_4h = nn.Linear(config.hidden_size, config.ffn_hidden_size * 2, bias=self.add_bias, device=device, **_config_to_kwargs(config))
        def swiglu(x):
            x = torch.chunk(x, 2, dim=-1)
            return F.silu(x[0]) * x[1]
        self.activation_func = swiglu
        self.dense_4h_to_h = nn.Linear(config.ffn_hidden_size, config.hidden_size, bias=self.add_bias, device=device, **_config_to_kwargs(config))
    def forward(self, hidden_states):
        intermediate_parallel = self.dense_h_to_4h(hidden_states)
        intermediate_parallel = self.activation_func(intermediate_parallel)
        output = self.dense_4h_to_h(intermediate_parallel)
        return output
class GLMBlock(torch.nn.Module):
    def __init__(self, config: ChatGLMConfig, layer_number, device=None):
        super(GLMBlock, self).__init__()
        self.layer_number = layer_number
        self.apply_residual_connection_post_layernorm = config.apply_residual_connection_post_layernorm
        self.fp32_residual_connection = config.fp32_residual_connection
        LayerNormFunc = RMSNorm if config.rmsnorm else LayerNorm
        self.input_layernorm = LayerNormFunc(config.hidden_size, eps=config.layernorm_epsilon, device=device, dtype=config.torch_dtype)
        self.self_attention = SelfAttention(config, layer_number, device=device)
        self.hidden_dropout = config.hidden_dropout
        self.post_attention_layernorm = LayerNormFunc(config.hidden_size, eps=config.layernorm_epsilon, device=device, dtype=config.torch_dtype)
        self.mlp = MLP(config, device=device)
    def forward(self, hidden_states, attention_mask, rotary_pos_emb, kv_cache=None, use_cache=True):
        layernorm_output = self.input_layernorm(hidden_states)
        attention_output, kv_cache = self.self_attention(layernorm_output, attention_mask, rotary_pos_emb, kv_cache=kv_cache, use_cache=use_cache)
        if self.apply_residual_connection_post_layernorm: residual = layernorm_output
        else: residual = hidden_states
        layernorm_input = torch.nn.functional.dropout(attention_output, p=self.hidden_dropout, training=self.training)
        layernorm_input = residual + layernorm_input
        layernorm_output = self.post_attention_layernorm(layernorm_input)
        mlp_output = self.mlp(layernorm_output)
        if self.apply_residual_connection_post_layernorm: residual = layernorm_output
        else: residual = layernorm_input
        output = torch.nn.functional.dropout(mlp_output, p=self.hidden_dropout, training=self.training)
        output = residual + output
        return (output, kv_cache)
class GLMTransformer(torch.nn.Module):
    def __init__(self, config: ChatGLMConfig, device=None):
        super(GLMTransformer, self).__init__()
        self.fp32_residual_connection = config.fp32_residual_connection
        self.post_layer_norm = config.post_layer_norm
        self.num_layers = config.num_layers
        def build_layer(layer_number): return GLMBlock(config, layer_number, device=device)
        self.layers = torch.nn.ModuleList([build_layer(i + 1) for i in range(self.num_layers)])
        if self.post_layer_norm:
            LayerNormFunc = RMSNorm if config.rmsnorm else LayerNorm
            self.final_layernorm = LayerNormFunc(config.hidden_size, eps=config.layernorm_epsilon, device=device, dtype=config.torch_dtype)
        self.gradient_checkpointing = False
    def _get_layer(self, layer_number): return self.layers[layer_number]
    def forward(self, hidden_states, attention_mask, rotary_pos_emb, kv_caches=None, use_cache: Optional[bool]=True, output_hidden_states: Optional[bool]=False):
        if not kv_caches: kv_caches = [None for _ in range(self.num_layers)]
        presents = () if use_cache else None
        if torch.is_grad_enabled() and self.gradient_checkpointing:
            if use_cache: use_cache = False
        all_self_attentions = None
        all_hidden_states = () if output_hidden_states else None
        for index in range(self.num_layers):
            if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
            layer = self._get_layer(index)
            if torch.is_grad_enabled() and self.gradient_checkpointing: layer_ret = torch.utils.checkpoint.checkpoint(layer,
            hidden_states, attention_mask, rotary_pos_emb, kv_caches[index], use_cache)
            else: layer_ret = layer(hidden_states, attention_mask, rotary_pos_emb, kv_cache=kv_caches[index], use_cache=use_cache)
            hidden_states, kv_cache = layer_ret
            if use_cache: presents = presents + (kv_cache,)
        if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        if self.post_layer_norm: hidden_states = self.final_layernorm(hidden_states)
        return (hidden_states, presents, all_hidden_states, all_self_attentions)
class ChatGLMPreTrainedModel(PreTrainedModel):
    is_parallelizable = False
    supports_gradient_checkpointing = True
    config_class = ChatGLMConfig
    base_model_prefix = 'transformer'
    _no_split_modules = ['GLMBlock']
    def _init_weights(self, module: nn.Module): return
    def get_masks(self, input_ids, past_key_values, padding_mask=None):
        batch_size, seq_length = input_ids.shape
        full_attention_mask = torch.ones(batch_size, seq_length, seq_length, device=input_ids.device)
        full_attention_mask.tril_()
        past_length = 0
        if past_key_values: past_length = past_key_values[0][0].shape[0]
        if past_length: full_attention_mask = torch.cat((torch.ones(batch_size, seq_length, past_length, device=input_ids.device), full_attention_mask), dim=-1)
        if padding_mask is not None: full_attention_mask = full_attention_mask * padding_mask.unsqueeze(1)
        if not past_length and padding_mask is not None: full_attention_mask -= padding_mask.unsqueeze(-1) - 1
        full_attention_mask = (full_attention_mask < 0.5).bool()
        full_attention_mask.unsqueeze_(1)
        return full_attention_mask
    def get_position_ids(self, input_ids, device):
        batch_size, seq_length = input_ids.shape
        position_ids = torch.arange(seq_length, dtype=torch.long, device=device).unsqueeze(0).repeat(batch_size, 1)
        return position_ids
    def _set_gradient_checkpointing(self, module, value=False):
        if isinstance(module, GLMTransformer): module.gradient_checkpointing = value
def default_init(cls, *args, **kwargs): return cls(*args, **kwargs)
class Embedding(torch.nn.Module):
    def __init__(self, config: ChatGLMConfig, device=None):
        super(Embedding, self).__init__()
        self.hidden_size = config.hidden_size
        self.word_embeddings = nn.Embedding(config.padded_vocab_size, self.hidden_size, dtype=config.torch_dtype, device=device)
        self.fp32_residual_connection = config.fp32_residual_connection
    def forward(self, input_ids):
        words_embeddings = self.word_embeddings(input_ids)
        embeddings = words_embeddings
        embeddings = embeddings.transpose(0, 1).contiguous()
        if self.fp32_residual_connection: embeddings = embeddings.float()
        return embeddings
class RotaryEmbedding(nn.Module):
    def __init__(self, dim, original_impl=False, device=None, dtype=None):
        super().__init__()
        inv_freq = 1.0 / 10000 ** (torch.arange(0, dim, 2, device=device).to(dtype=dtype) / dim)
        self.register_buffer('inv_freq', inv_freq)
        self.dim = dim
        self.original_impl = original_impl
    def forward_impl(self, seq_len: int, n_elem: int, dtype: torch.dtype, device: torch.device, base: int=10000):
        theta = 1.0 / base ** (torch.arange(0, n_elem, 2, dtype=torch.float, device=device) / n_elem)
        seq_idx = torch.arange(seq_len, dtype=torch.float, device=device)
        idx_theta = torch.outer(seq_idx, theta).float()
        cache = torch.stack([torch.cos(idx_theta), torch.sin(idx_theta)], dim=-1)
        if dtype in (torch.float16, torch.bfloat16, torch.int8): cache = cache.bfloat16() if dtype == torch.bfloat16 else cache.half()
        return cache
    def forward(self, max_seq_len, offset=0): return self.forward_impl(max_seq_len, self.dim, dtype=self.inv_freq.dtype, device=self.inv_freq.device)
class PrefixEncoder(torch.nn.Module):
    def __init__(self, config: ChatGLMConfig):
        super().__init__()
        self.prefix_projection = config.prefix_projection
        if self.prefix_projection:
            kv_size = config.num_layers * config.kv_channels * config.multi_query_group_num * 2
            self.embedding = torch.nn.Embedding(config.pre_seq_len, kv_size)
            self.trans = torch.nn.Sequential(torch.nn.Linear(kv_size, config.hidden_size), torch.nn.Tanh(), torch.nn.Linear(config.hidden_size, kv_size))
        else: self.embedding = torch.nn.Embedding(config.pre_seq_len, config.num_layers * config.kv_channels * config.multi_query_group_num * 2)
    def forward(self, prefix: torch.Tensor):
        if self.prefix_projection:
            prefix_tokens = self.embedding(prefix)
            past_key_values = self.trans(prefix_tokens)
        else: past_key_values = self.embedding(prefix)
        return past_key_values
class ChatGLMModel(ChatGLMPreTrainedModel):
    def __init__(self, config: ChatGLMConfig, device=None, empty_init=True):
        super().__init__(config)
        if empty_init: init_method = skip_init
        else: init_method = default_init
        init_kwargs = {}
        if device is not None: init_kwargs['device'] = device
        self.embedding = init_method(Embedding, config, **init_kwargs)
        self.num_layers = config.num_layers
        self.multi_query_group_num = config.multi_query_group_num
        self.kv_channels = config.kv_channels
        self.seq_length = config.seq_length
        rotary_dim = config.hidden_size // config.num_attention_heads if config.kv_channels is None else config.kv_channels
        self.rotary_pos_emb = RotaryEmbedding(rotary_dim // 2, original_impl=config.original_rope, device=device, dtype=config.torch_dtype)
        self.encoder = init_method(GLMTransformer, config, **init_kwargs)
        self.output_layer = init_method(nn.Linear, config.hidden_size, config.padded_vocab_size, bias=False, dtype=config.torch_dtype, **init_kwargs)
        self.pre_seq_len = config.pre_seq_len
        self.prefix_projection = config.prefix_projection
        if self.pre_seq_len is not None:
            for param in self.parameters(): param.requires_grad = False
            self.prefix_tokens = torch.arange(self.pre_seq_len).long()
            self.prefix_encoder = PrefixEncoder(config)
            self.dropout = torch.nn.Dropout(0.1)
    def get_input_embeddings(self): return self.embedding.word_embeddings
    def get_prompt(self, batch_size, device, dtype=torch.half):
        prefix_tokens = self.prefix_tokens.unsqueeze(0).expand(batch_size, -1).to(device)
        past_key_values = self.prefix_encoder(prefix_tokens).type(dtype)
        past_key_values = past_key_values.view(batch_size, self.pre_seq_len, self.num_layers * 2, self.multi_query_group_num, self.kv_channels)
        past_key_values = self.dropout(past_key_values)
        past_key_values = past_key_values.permute([2, 1, 0, 3, 4]).split(2)
        return past_key_values
    def forward(self, input_ids, position_ids: Optional[torch.Tensor]=None, attention_mask: Optional[torch.BoolTensor]=None,
    full_attention_mask: Optional[torch.BoolTensor]=None, past_key_values: Optional[Tuple[Tuple[torch.Tensor, torch.Tensor], ...]]=None,
    inputs_embeds: Optional[torch.Tensor]=None, use_cache: Optional[bool]=None, output_hidden_states: Optional[bool]=None, return_dict: Optional[bool]=None):
        output_hidden_states = output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
        use_cache = use_cache if use_cache is not None else self.config.use_cache
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        batch_size, seq_length = input_ids.shape
        if inputs_embeds is None: inputs_embeds = self.embedding(input_ids)
        if self.pre_seq_len is not None:
            if past_key_values is None: past_key_values = self.get_prompt(batch_size=batch_size, device=input_ids.device, dtype=inputs_embeds.dtype)
            if attention_mask is not None: attention_mask = torch.cat([attention_mask.new_ones((batch_size, self.pre_seq_len)), attention_mask], dim=-1)
        if full_attention_mask is None:
            if attention_mask is not None and (not attention_mask.all()) or (past_key_values and seq_length != 1): full_attention_mask = self.get_masks(input_ids, past_key_values, padding_mask=attention_mask)
        rotary_pos_emb = self.rotary_pos_emb(self.seq_length)
        if position_ids is not None: rotary_pos_emb = rotary_pos_emb[position_ids]
        else: rotary_pos_emb = rotary_pos_emb[None, :seq_length]
        rotary_pos_emb = rotary_pos_emb.transpose(0, 1).contiguous()
        hidden_states, presents, all_hidden_states, all_self_attentions = self.encoder(inputs_embeds, full_attention_mask,
        rotary_pos_emb=rotary_pos_emb, kv_caches=past_key_values, use_cache=use_cache, output_hidden_states=output_hidden_states)
        if not return_dict: return tuple((v for v in [hidden_states, presents, all_hidden_states, all_self_attentions] if v is not None))
        return BaseModelOutputWithPast(last_hidden_state=hidden_states, past_key_values=presents, hidden_states=all_hidden_states, attentions=all_self_attentions)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
