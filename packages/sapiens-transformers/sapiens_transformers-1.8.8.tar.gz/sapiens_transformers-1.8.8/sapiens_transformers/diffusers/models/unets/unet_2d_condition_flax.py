'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from .unet_2d_blocks_flax import FlaxCrossAttnDownBlock2D, FlaxCrossAttnUpBlock2D, FlaxDownBlock2D, FlaxUNetMidBlock2DCrossAttn, FlaxUpBlock2D
from ...configuration_utils import ConfigMixin, flax_register_to_config
from ..embeddings_flax import FlaxTimestepEmbedding, FlaxTimesteps
from ..modeling_flax_utils import FlaxModelMixin
from typing import Dict, Optional, Tuple, Union
from flax.core.frozen_dict import FrozenDict
from ...utils import BaseOutput
import flax.linen as nn
import jax.numpy as jnp
import flax
import jax
@flax.struct.dataclass
class FlaxUNet2DConditionOutput(BaseOutput):
    """Args:"""
    sample: jnp.ndarray
@flax_register_to_config
class FlaxUNet2DConditionModel(nn.Module, FlaxModelMixin, ConfigMixin):
    sample_size: int = 32
    in_channels: int = 4
    out_channels: int = 4
    down_block_types: Tuple[str, ...] = ('CrossAttnDownBlock2D', 'CrossAttnDownBlock2D', 'CrossAttnDownBlock2D', 'DownBlock2D')
    up_block_types: Tuple[str, ...] = ('UpBlock2D', 'CrossAttnUpBlock2D', 'CrossAttnUpBlock2D', 'CrossAttnUpBlock2D')
    mid_block_type: Optional[str] = 'UNetMidBlock2DCrossAttn'
    only_cross_attention: Union[bool, Tuple[bool]] = False
    block_out_channels: Tuple[int, ...] = (320, 640, 1280, 1280)
    layers_per_block: int = 2
    attention_head_dim: Union[int, Tuple[int, ...]] = 8
    num_attention_heads: Optional[Union[int, Tuple[int, ...]]] = None
    cross_attention_dim: int = 1280
    dropout: float = 0.0
    use_linear_projection: bool = False
    dtype: jnp.dtype = jnp.float32
    flip_sin_to_cos: bool = True
    freq_shift: int = 0
    use_memory_efficient_attention: bool = False
    split_head_dim: bool = False
    transformer_layers_per_block: Union[int, Tuple[int, ...]] = 1
    addition_embed_type: Optional[str] = None
    addition_time_embed_dim: Optional[int] = None
    addition_embed_type_num_heads: int = 64
    projection_class_embeddings_input_dim: Optional[int] = None
    def init_weights(self, rng: jax.Array) -> FrozenDict:
        sample_shape = (1, self.in_channels, self.sample_size, self.sample_size)
        sample = jnp.zeros(sample_shape, dtype=jnp.float32)
        timesteps = jnp.ones((1,), dtype=jnp.int32)
        encoder_hidden_states = jnp.zeros((1, 1, self.cross_attention_dim), dtype=jnp.float32)
        params_rng, dropout_rng = jax.random.split(rng)
        rngs = {'params': params_rng, 'dropout': dropout_rng}
        added_cond_kwargs = None
        if self.addition_embed_type == 'text_time':
            is_refiner = 5 * self.config.addition_time_embed_dim + self.config.cross_attention_dim == self.config.projection_class_embeddings_input_dim
            num_micro_conditions = 5 if is_refiner else 6
            text_embeds_dim = self.config.projection_class_embeddings_input_dim - num_micro_conditions * self.config.addition_time_embed_dim
            time_ids_channels = self.projection_class_embeddings_input_dim - text_embeds_dim
            time_ids_dims = time_ids_channels // self.addition_time_embed_dim
            added_cond_kwargs = {'text_embeds': jnp.zeros((1, text_embeds_dim), dtype=jnp.float32), 'time_ids': jnp.zeros((1, time_ids_dims), dtype=jnp.float32)}
        return self.init(rngs, sample, timesteps, encoder_hidden_states, added_cond_kwargs)['params']
    def setup(self) -> None:
        block_out_channels = self.block_out_channels
        time_embed_dim = block_out_channels[0] * 4
        if self.num_attention_heads is not None: raise ValueError('At the moment it is not possible to define the number of attention heads via `num_attention_heads` because of a naming issue as described in https://github.com/huggingface/diffusers/issues/2011#issuecomment-1547958131. Passing `num_attention_heads` will only be supported in diffusers v0.19.')
        num_attention_heads = self.num_attention_heads or self.attention_head_dim
        self.conv_in = nn.Conv(block_out_channels[0], kernel_size=(3, 3), strides=(1, 1), padding=((1, 1), (1, 1)), dtype=self.dtype)
        self.time_proj = FlaxTimesteps(block_out_channels[0], flip_sin_to_cos=self.flip_sin_to_cos, freq_shift=self.config.freq_shift)
        self.time_embedding = FlaxTimestepEmbedding(time_embed_dim, dtype=self.dtype)
        only_cross_attention = self.only_cross_attention
        if isinstance(only_cross_attention, bool): only_cross_attention = (only_cross_attention,) * len(self.down_block_types)
        if isinstance(num_attention_heads, int): num_attention_heads = (num_attention_heads,) * len(self.down_block_types)
        transformer_layers_per_block = self.transformer_layers_per_block
        if isinstance(transformer_layers_per_block, int): transformer_layers_per_block = [transformer_layers_per_block] * len(self.down_block_types)
        if self.addition_embed_type is None: self.add_embedding = None
        elif self.addition_embed_type == 'text_time':
            if self.addition_time_embed_dim is None: raise ValueError(f'addition_embed_type {self.addition_embed_type} requires `addition_time_embed_dim` to not be None')
            self.add_time_proj = FlaxTimesteps(self.addition_time_embed_dim, self.flip_sin_to_cos, self.freq_shift)
            self.add_embedding = FlaxTimestepEmbedding(time_embed_dim, dtype=self.dtype)
        else: raise ValueError(f'addition_embed_type: {self.addition_embed_type} must be None or `text_time`.')
        down_blocks = []
        output_channel = block_out_channels[0]
        for i, down_block_type in enumerate(self.down_block_types):
            input_channel = output_channel
            output_channel = block_out_channels[i]
            is_final_block = i == len(block_out_channels) - 1
            if down_block_type == 'CrossAttnDownBlock2D': down_block = FlaxCrossAttnDownBlock2D(in_channels=input_channel, out_channels=output_channel, dropout=self.dropout,
            num_layers=self.layers_per_block, transformer_layers_per_block=transformer_layers_per_block[i], num_attention_heads=num_attention_heads[i], add_downsample=not is_final_block,
            use_linear_projection=self.use_linear_projection, only_cross_attention=only_cross_attention[i], use_memory_efficient_attention=self.use_memory_efficient_attention, split_head_dim=self.split_head_dim, dtype=self.dtype)
            else: down_block = FlaxDownBlock2D(in_channels=input_channel, out_channels=output_channel, dropout=self.dropout, num_layers=self.layers_per_block, add_downsample=not is_final_block, dtype=self.dtype)
            down_blocks.append(down_block)
        self.down_blocks = down_blocks
        if self.config.mid_block_type == 'UNetMidBlock2DCrossAttn': self.mid_block = FlaxUNetMidBlock2DCrossAttn(in_channels=block_out_channels[-1], dropout=self.dropout, num_attention_heads=num_attention_heads[-1],
        transformer_layers_per_block=transformer_layers_per_block[-1], use_linear_projection=self.use_linear_projection, use_memory_efficient_attention=self.use_memory_efficient_attention, split_head_dim=self.split_head_dim, dtype=self.dtype)
        elif self.config.mid_block_type is None: self.mid_block = None
        else: raise ValueError(f'Unexpected mid_block_type {self.config.mid_block_type}')
        up_blocks = []
        reversed_block_out_channels = list(reversed(block_out_channels))
        reversed_num_attention_heads = list(reversed(num_attention_heads))
        only_cross_attention = list(reversed(only_cross_attention))
        output_channel = reversed_block_out_channels[0]
        reversed_transformer_layers_per_block = list(reversed(transformer_layers_per_block))
        for i, up_block_type in enumerate(self.up_block_types):
            prev_output_channel = output_channel
            output_channel = reversed_block_out_channels[i]
            input_channel = reversed_block_out_channels[min(i + 1, len(block_out_channels) - 1)]
            is_final_block = i == len(block_out_channels) - 1
            if up_block_type == 'CrossAttnUpBlock2D': up_block = FlaxCrossAttnUpBlock2D(in_channels=input_channel, out_channels=output_channel, prev_output_channel=prev_output_channel, num_layers=self.layers_per_block + 1,
            transformer_layers_per_block=reversed_transformer_layers_per_block[i], num_attention_heads=reversed_num_attention_heads[i], add_upsample=not is_final_block, dropout=self.dropout, use_linear_projection=self.use_linear_projection,
            only_cross_attention=only_cross_attention[i], use_memory_efficient_attention=self.use_memory_efficient_attention, split_head_dim=self.split_head_dim, dtype=self.dtype)
            else: up_block = FlaxUpBlock2D(in_channels=input_channel, out_channels=output_channel, prev_output_channel=prev_output_channel, num_layers=self.layers_per_block + 1, add_upsample=not is_final_block, dropout=self.dropout, dtype=self.dtype)
            up_blocks.append(up_block)
            prev_output_channel = output_channel
        self.up_blocks = up_blocks
        self.conv_norm_out = nn.GroupNorm(num_groups=32, epsilon=1e-05)
        self.conv_out = nn.Conv(self.out_channels, kernel_size=(3, 3), strides=(1, 1), padding=((1, 1), (1, 1)), dtype=self.dtype)
    def __call__(self, sample: jnp.ndarray, timesteps: Union[jnp.ndarray, float, int], encoder_hidden_states: jnp.ndarray, added_cond_kwargs: Optional[Union[Dict, FrozenDict]]=None,
    down_block_additional_residuals: Optional[Tuple[jnp.ndarray, ...]]=None, mid_block_additional_residual: Optional[jnp.ndarray]=None, return_dict: bool=True, train: bool=False) -> Union[FlaxUNet2DConditionOutput, Tuple[jnp.ndarray]]:
        """Returns:"""
        if not isinstance(timesteps, jnp.ndarray): timesteps = jnp.array([timesteps], dtype=jnp.int32)
        elif isinstance(timesteps, jnp.ndarray) and len(timesteps.shape) == 0:
            timesteps = timesteps.astype(dtype=jnp.float32)
            timesteps = jnp.expand_dims(timesteps, 0)
        t_emb = self.time_proj(timesteps)
        t_emb = self.time_embedding(t_emb)
        aug_emb = None
        if self.addition_embed_type == 'text_time':
            if added_cond_kwargs is None: raise ValueError(f'Need to provide argument `added_cond_kwargs` for {self.__class__} when using `addition_embed_type={self.addition_embed_type}`')
            text_embeds = added_cond_kwargs.get('text_embeds')
            if text_embeds is None: raise ValueError(f"{self.__class__} has the config param `addition_embed_type` set to 'text_time' which requires the keyword argument `text_embeds` to be passed in `added_cond_kwargs`")
            time_ids = added_cond_kwargs.get('time_ids')
            if time_ids is None: raise ValueError(f"{self.__class__} has the config param `addition_embed_type` set to 'text_time' which requires the keyword argument `time_ids` to be passed in `added_cond_kwargs`")
            time_embeds = self.add_time_proj(jnp.ravel(time_ids))
            time_embeds = jnp.reshape(time_embeds, (text_embeds.shape[0], -1))
            add_embeds = jnp.concatenate([text_embeds, time_embeds], axis=-1)
            aug_emb = self.add_embedding(add_embeds)
        t_emb = t_emb + aug_emb if aug_emb is not None else t_emb
        sample = jnp.transpose(sample, (0, 2, 3, 1))
        sample = self.conv_in(sample)
        down_block_res_samples = (sample,)
        for down_block in self.down_blocks:
            if isinstance(down_block, FlaxCrossAttnDownBlock2D): sample, res_samples = down_block(sample, t_emb, encoder_hidden_states, deterministic=not train)
            else: sample, res_samples = down_block(sample, t_emb, deterministic=not train)
            down_block_res_samples += res_samples
        if down_block_additional_residuals is not None:
            new_down_block_res_samples = ()
            for down_block_res_sample, down_block_additional_residual in zip(down_block_res_samples, down_block_additional_residuals):
                down_block_res_sample += down_block_additional_residual
                new_down_block_res_samples += (down_block_res_sample,)
            down_block_res_samples = new_down_block_res_samples
        if self.mid_block is not None: sample = self.mid_block(sample, t_emb, encoder_hidden_states, deterministic=not train)
        if mid_block_additional_residual is not None: sample += mid_block_additional_residual
        for up_block in self.up_blocks:
            res_samples = down_block_res_samples[-(self.layers_per_block + 1):]
            down_block_res_samples = down_block_res_samples[:-(self.layers_per_block + 1)]
            if isinstance(up_block, FlaxCrossAttnUpBlock2D): sample = up_block(sample, temb=t_emb, encoder_hidden_states=encoder_hidden_states, res_hidden_states_tuple=res_samples, deterministic=not train)
            else: sample = up_block(sample, temb=t_emb, res_hidden_states_tuple=res_samples, deterministic=not train)
        sample = self.conv_norm_out(sample)
        sample = nn.silu(sample)
        sample = self.conv_out(sample)
        sample = jnp.transpose(sample, (0, 3, 1, 2))
        if not return_dict: return (sample,)
        return FlaxUNet2DConditionOutput(sample=sample)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
