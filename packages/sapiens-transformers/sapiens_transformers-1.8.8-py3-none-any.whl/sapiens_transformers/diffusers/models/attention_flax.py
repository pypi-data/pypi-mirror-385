'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import jax.numpy as jnp
import flax.linen as nn
import functools
import math
import jax
def _query_chunk_attention(query, key, value, precision, key_chunk_size: int=4096):
    num_kv, num_heads, k_features = key.shape[-3:]
    v_features = value.shape[-1]
    key_chunk_size = min(key_chunk_size, num_kv)
    query = query / jnp.sqrt(k_features)
    @functools.partial(jax.checkpoint, prevent_cse=False)
    def summarize_chunk(query, key, value):
        attn_weights = jnp.einsum('...qhd,...khd->...qhk', query, key, precision=precision)
        max_score = jnp.max(attn_weights, axis=-1, keepdims=True)
        max_score = jax.lax.stop_gradient(max_score)
        exp_weights = jnp.exp(attn_weights - max_score)
        exp_values = jnp.einsum('...vhf,...qhv->...qhf', value, exp_weights, precision=precision)
        max_score = jnp.einsum('...qhk->...qh', max_score)
        return (exp_values, exp_weights.sum(axis=-1), max_score)
    def chunk_scanner(chunk_idx):
        key_chunk = jax.lax.dynamic_slice(operand=key, start_indices=[0] * (key.ndim - 3) + [chunk_idx, 0, 0], slice_sizes=list(key.shape[:-3]) + [key_chunk_size, num_heads, k_features])
        value_chunk = jax.lax.dynamic_slice(operand=value, start_indices=[0] * (value.ndim - 3) + [chunk_idx, 0, 0], slice_sizes=list(value.shape[:-3]) + [key_chunk_size, num_heads, v_features])
        return summarize_chunk(query, key_chunk, value_chunk)
    chunk_values, chunk_weights, chunk_max = jax.lax.map(f=chunk_scanner, xs=jnp.arange(0, num_kv, key_chunk_size))
    global_max = jnp.max(chunk_max, axis=0, keepdims=True)
    max_diffs = jnp.exp(chunk_max - global_max)
    chunk_values *= jnp.expand_dims(max_diffs, axis=-1)
    chunk_weights *= max_diffs
    all_values = chunk_values.sum(axis=0)
    all_weights = jnp.expand_dims(chunk_weights, -1).sum(axis=0)
    return all_values / all_weights
def jax_memory_efficient_attention(query, key, value, precision=jax.lax.Precision.HIGHEST, query_chunk_size: int=1024, key_chunk_size: int=4096):
    """Returns:"""
    num_q, num_heads, q_features = query.shape[-3:]
    def chunk_scanner(chunk_idx, _):
        query_chunk = jax.lax.dynamic_slice(operand=query, start_indices=[0] * (query.ndim - 3) + [chunk_idx, 0, 0], slice_sizes=list(query.shape[:-3]) + [min(query_chunk_size, num_q), num_heads, q_features])
        return (chunk_idx + query_chunk_size, _query_chunk_attention(query=query_chunk, key=key, value=value, precision=precision, key_chunk_size=key_chunk_size))
    _, res = jax.lax.scan(f=chunk_scanner, init=0, xs=None, length=math.ceil(num_q / query_chunk_size))
    return jnp.concatenate(res, axis=-3)
class FlaxAttention(nn.Module):
    query_dim: int
    heads: int = 8
    dim_head: int = 64
    dropout: float = 0.0
    use_memory_efficient_attention: bool = False
    split_head_dim: bool = False
    dtype: jnp.dtype = jnp.float32
    def setup(self):
        inner_dim = self.dim_head * self.heads
        self.scale = self.dim_head ** (-0.5)
        self.query = nn.Dense(inner_dim, use_bias=False, dtype=self.dtype, name='to_q')
        self.key = nn.Dense(inner_dim, use_bias=False, dtype=self.dtype, name='to_k')
        self.value = nn.Dense(inner_dim, use_bias=False, dtype=self.dtype, name='to_v')
        self.proj_attn = nn.Dense(self.query_dim, dtype=self.dtype, name='to_out_0')
        self.dropout_layer = nn.Dropout(rate=self.dropout)
    def reshape_heads_to_batch_dim(self, tensor):
        batch_size, seq_len, dim = tensor.shape
        head_size = self.heads
        tensor = tensor.reshape(batch_size, seq_len, head_size, dim // head_size)
        tensor = jnp.transpose(tensor, (0, 2, 1, 3))
        tensor = tensor.reshape(batch_size * head_size, seq_len, dim // head_size)
        return tensor
    def reshape_batch_dim_to_heads(self, tensor):
        batch_size, seq_len, dim = tensor.shape
        head_size = self.heads
        tensor = tensor.reshape(batch_size // head_size, head_size, seq_len, dim)
        tensor = jnp.transpose(tensor, (0, 2, 1, 3))
        tensor = tensor.reshape(batch_size // head_size, seq_len, dim * head_size)
        return tensor
    def __call__(self, hidden_states, context=None, deterministic=True):
        context = hidden_states if context is None else context
        query_proj = self.query(hidden_states)
        key_proj = self.key(context)
        value_proj = self.value(context)
        if self.split_head_dim:
            b = hidden_states.shape[0]
            query_states = jnp.reshape(query_proj, (b, -1, self.heads, self.dim_head))
            key_states = jnp.reshape(key_proj, (b, -1, self.heads, self.dim_head))
            value_states = jnp.reshape(value_proj, (b, -1, self.heads, self.dim_head))
        else:
            query_states = self.reshape_heads_to_batch_dim(query_proj)
            key_states = self.reshape_heads_to_batch_dim(key_proj)
            value_states = self.reshape_heads_to_batch_dim(value_proj)
        if self.use_memory_efficient_attention:
            query_states = query_states.transpose(1, 0, 2)
            key_states = key_states.transpose(1, 0, 2)
            value_states = value_states.transpose(1, 0, 2)
            flatten_latent_dim = query_states.shape[-3]
            if flatten_latent_dim % 64 == 0: query_chunk_size = int(flatten_latent_dim / 64)
            elif flatten_latent_dim % 16 == 0: query_chunk_size = int(flatten_latent_dim / 16)
            elif flatten_latent_dim % 4 == 0: query_chunk_size = int(flatten_latent_dim / 4)
            else: query_chunk_size = int(flatten_latent_dim)
            hidden_states = jax_memory_efficient_attention(query_states, key_states, value_states, query_chunk_size=query_chunk_size, key_chunk_size=4096 * 4)
            hidden_states = hidden_states.transpose(1, 0, 2)
            hidden_states = self.reshape_batch_dim_to_heads(hidden_states)
        else:
            if self.split_head_dim: attention_scores = jnp.einsum('b t n h, b f n h -> b n f t', key_states, query_states)
            else: attention_scores = jnp.einsum('b i d, b j d->b i j', query_states, key_states)
            attention_scores = attention_scores * self.scale
            attention_probs = nn.softmax(attention_scores, axis=-1 if self.split_head_dim else 2)
            if self.split_head_dim:
                hidden_states = jnp.einsum('b n f t, b t n h -> b f n h', attention_probs, value_states)
                b = hidden_states.shape[0]
                hidden_states = jnp.reshape(hidden_states, (b, -1, self.heads * self.dim_head))
            else:
                hidden_states = jnp.einsum('b i j, b j d -> b i d', attention_probs, value_states)
                hidden_states = self.reshape_batch_dim_to_heads(hidden_states)
        hidden_states = self.proj_attn(hidden_states)
        return self.dropout_layer(hidden_states, deterministic=deterministic)
class FlaxBasicTransformerBlock(nn.Module):
    dim: int
    n_heads: int
    d_head: int
    dropout: float = 0.0
    only_cross_attention: bool = False
    dtype: jnp.dtype = jnp.float32
    use_memory_efficient_attention: bool = False
    split_head_dim: bool = False
    def setup(self):
        self.attn1 = FlaxAttention(self.dim, self.n_heads, self.d_head, self.dropout, self.use_memory_efficient_attention, self.split_head_dim, dtype=self.dtype)
        self.attn2 = FlaxAttention(self.dim, self.n_heads, self.d_head, self.dropout, self.use_memory_efficient_attention, self.split_head_dim, dtype=self.dtype)
        self.ff = FlaxFeedForward(dim=self.dim, dropout=self.dropout, dtype=self.dtype)
        self.norm1 = nn.LayerNorm(epsilon=1e-05, dtype=self.dtype)
        self.norm2 = nn.LayerNorm(epsilon=1e-05, dtype=self.dtype)
        self.norm3 = nn.LayerNorm(epsilon=1e-05, dtype=self.dtype)
        self.dropout_layer = nn.Dropout(rate=self.dropout)
    def __call__(self, hidden_states, context, deterministic=True):
        residual = hidden_states
        if self.only_cross_attention: hidden_states = self.attn1(self.norm1(hidden_states), context, deterministic=deterministic)
        else: hidden_states = self.attn1(self.norm1(hidden_states), deterministic=deterministic)
        hidden_states = hidden_states + residual
        residual = hidden_states
        hidden_states = self.attn2(self.norm2(hidden_states), context, deterministic=deterministic)
        hidden_states = hidden_states + residual
        residual = hidden_states
        hidden_states = self.ff(self.norm3(hidden_states), deterministic=deterministic)
        hidden_states = hidden_states + residual
        return self.dropout_layer(hidden_states, deterministic=deterministic)
class FlaxTransformer2DModel(nn.Module):
    in_channels: int
    n_heads: int
    d_head: int
    depth: int = 1
    dropout: float = 0.0
    use_linear_projection: bool = False
    only_cross_attention: bool = False
    dtype: jnp.dtype = jnp.float32
    use_memory_efficient_attention: bool = False
    split_head_dim: bool = False
    def setup(self):
        self.norm = nn.GroupNorm(num_groups=32, epsilon=1e-05)
        inner_dim = self.n_heads * self.d_head
        if self.use_linear_projection: self.proj_in = nn.Dense(inner_dim, dtype=self.dtype)
        else: self.proj_in = nn.Conv(inner_dim, kernel_size=(1, 1), strides=(1, 1), padding='VALID', dtype=self.dtype)
        self.transformer_blocks = [FlaxBasicTransformerBlock(inner_dim, self.n_heads, self.d_head, dropout=self.dropout, only_cross_attention=self.only_cross_attention,
        dtype=self.dtype, use_memory_efficient_attention=self.use_memory_efficient_attention, split_head_dim=self.split_head_dim) for _ in range(self.depth)]
        if self.use_linear_projection: self.proj_out = nn.Dense(inner_dim, dtype=self.dtype)
        else: self.proj_out = nn.Conv(inner_dim, kernel_size=(1, 1), strides=(1, 1), padding='VALID', dtype=self.dtype)
        self.dropout_layer = nn.Dropout(rate=self.dropout)
    def __call__(self, hidden_states, context, deterministic=True):
        batch, height, width, channels = hidden_states.shape
        residual = hidden_states
        hidden_states = self.norm(hidden_states)
        if self.use_linear_projection:
            hidden_states = hidden_states.reshape(batch, height * width, channels)
            hidden_states = self.proj_in(hidden_states)
        else:
            hidden_states = self.proj_in(hidden_states)
            hidden_states = hidden_states.reshape(batch, height * width, channels)
        for transformer_block in self.transformer_blocks: hidden_states = transformer_block(hidden_states, context, deterministic=deterministic)
        if self.use_linear_projection:
            hidden_states = self.proj_out(hidden_states)
            hidden_states = hidden_states.reshape(batch, height, width, channels)
        else:
            hidden_states = hidden_states.reshape(batch, height, width, channels)
            hidden_states = self.proj_out(hidden_states)
        hidden_states = hidden_states + residual
        return self.dropout_layer(hidden_states, deterministic=deterministic)
class FlaxFeedForward(nn.Module):
    dim: int
    dropout: float = 0.0
    dtype: jnp.dtype = jnp.float32
    def setup(self):
        self.net_0 = FlaxGEGLU(self.dim, self.dropout, self.dtype)
        self.net_2 = nn.Dense(self.dim, dtype=self.dtype)
    def __call__(self, hidden_states, deterministic=True):
        hidden_states = self.net_0(hidden_states, deterministic=deterministic)
        hidden_states = self.net_2(hidden_states)
        return hidden_states
class FlaxGEGLU(nn.Module):
    dim: int
    dropout: float = 0.0
    dtype: jnp.dtype = jnp.float32
    def setup(self):
        inner_dim = self.dim * 4
        self.proj = nn.Dense(inner_dim * 2, dtype=self.dtype)
        self.dropout_layer = nn.Dropout(rate=self.dropout)
    def __call__(self, hidden_states, deterministic=True):
        hidden_states = self.proj(hidden_states)
        hidden_linear, hidden_gelu = jnp.split(hidden_states, 2, axis=2)
        return self.dropout_layer(hidden_linear * nn.gelu(hidden_gelu), deterministic=deterministic)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
