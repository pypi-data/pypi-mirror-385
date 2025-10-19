"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from dataclasses import dataclass
from typing import Optional, Tuple, Union
import torch
import torch.utils.checkpoint
from torch import nn
from ...activations import ACT2FN
from ...modeling_outputs import BaseModelOutput, BaseModelOutputWithPooling
from ...utils import ModelOutput, logging
from .configuration_idefics import IdeficsVisionConfig
logger = logging.get_logger(__name__)
@dataclass
class IdeficsVisionModelOutput(ModelOutput):
    """Args:"""
    image_embeds: Optional[torch.FloatTensor] = None
    last_hidden_state: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[Tuple[torch.FloatTensor, ...]] = None
class IdeficsVisionEmbeddings(nn.Module):
    def __init__(self, config: IdeficsVisionConfig):
        super().__init__()
        self.config = config
        self.embed_dim = config.hidden_size
        self.image_size = config.image_size
        self.patch_size = config.patch_size
        self.class_embedding = nn.Parameter(torch.randn(self.embed_dim))
        self.patch_embedding = nn.Conv2d(in_channels=config.num_channels, out_channels=self.embed_dim, kernel_size=self.patch_size, stride=self.patch_size, bias=False)
        self.num_patches = (self.image_size // self.patch_size) ** 2
        self.num_positions = self.num_patches + 1
        self.position_embedding = nn.Embedding(self.num_positions, self.embed_dim)
        self.register_buffer("position_ids", torch.arange(self.num_positions).expand((1, -1)), persistent=False)
    def interpolate_pos_encoding(self, embeddings: torch.Tensor, height: int, width: int) -> torch.Tensor:
        num_patches = embeddings.shape[1] - 1
        pos_embed = self.position_embedding(self.position_ids)
        num_positions = pos_embed.shape[1] - 1
        if num_patches == num_positions and height == width: return pos_embed
        class_pos_embed = pos_embed[:, 0]
        patch_pos_embed = pos_embed[:, 1:]
        embed_dim = embeddings.shape[-1]
        num_h_patches = height // self.config.patch_size
        num_w_patches = width // self.config.patch_size
        num_h_patches, num_w_patches = num_h_patches + 0.1, num_w_patches + 0.1
        sqrt_num_positions = math.sqrt(num_positions)
        patch_pos_embed = patch_pos_embed.reshape(1, int(sqrt_num_positions), int(sqrt_num_positions), embed_dim)
        patch_pos_embed = patch_pos_embed.permute(0, 3, 1, 2)
        fp32_upcasting = patch_pos_embed.dtype == torch.bfloat16
        if fp32_upcasting:
            logger.warning_once("Upcasting patch_pos_embed to fp32 for interpolation since `upsample_bicubic2d_out_frame` in nn.functional.interpolate is not implemented for 'torch.bfloat16' dtype. This will result in a slight overhead.")
            patch_pos_embed = patch_pos_embed.to(torch.float)
        patch_pos_embed = nn.functional.interpolate(patch_pos_embed, scale_factor=(num_h_patches / sqrt_num_positions, num_w_patches / sqrt_num_positions), mode="bicubic", align_corners=False)
        if fp32_upcasting: patch_pos_embed = patch_pos_embed.to(torch.bfloat16)
        if int(num_h_patches) != patch_pos_embed.shape[-2] or int(num_w_patches) != patch_pos_embed.shape[-1]: raise ValueError(f"Number of patches for images ({int(num_h_patches), int(num_w_patches)}) don't match the shape of position embedding ({patch_pos_embed.shape[-2], patch_pos_embed.shape[-1]})")
        patch_pos_embed = patch_pos_embed.permute(0, 2, 3, 1).view(1, -1, embed_dim)
        return torch.cat((class_pos_embed.unsqueeze(0), patch_pos_embed), dim=1)
    def forward(self, pixel_values: torch.FloatTensor, interpolate_pos_encoding: bool = False) -> torch.Tensor:
        batch_size, num_channels, height, width = pixel_values.shape
        if not interpolate_pos_encoding:
            if height != self.image_size or width != self.image_size: raise ValueError(f"Input image size ({height}*{width}) doesn't match model ({self.image_size}*{self.image_size}). You should try to set `interpolate_pos_encoding=True`")
        target_dtype = self.patch_embedding.weight.dtype
        patch_embeds = self.patch_embedding(pixel_values.to(dtype=target_dtype))
        patch_embeds = patch_embeds.flatten(2).transpose(1, 2)
        class_embeds = self.class_embedding.expand(batch_size, 1, -1)
        embeddings = torch.cat([class_embeds, patch_embeds], dim=1)
        if interpolate_pos_encoding: embeddings = embeddings + self.interpolate_pos_encoding(embeddings, height, width)
        else: embeddings = embeddings + self.position_embedding(self.position_ids)
        return embeddings
class IdeficsVisionAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.embed_dim = config.hidden_size
        self.num_heads = config.num_attention_heads
        self.head_dim = self.embed_dim // self.num_heads
        if self.head_dim * self.num_heads != self.embed_dim: raise ValueError(f"embed_dim must be divisible by num_heads (got `embed_dim`: {self.embed_dim} and `num_heads`: {self.num_heads}).")
        self.scale = self.head_dim**-0.5
        self.dropout = config.attention_dropout
        self.k_proj = nn.Linear(self.embed_dim, self.embed_dim)
        self.v_proj = nn.Linear(self.embed_dim, self.embed_dim)
        self.q_proj = nn.Linear(self.embed_dim, self.embed_dim)
        self.out_proj = nn.Linear(self.embed_dim, self.embed_dim)
    def _shape(self, tensor: torch.Tensor, seq_len: int, bsz: int): return tensor.view(bsz, seq_len, self.num_heads, self.head_dim).transpose(1, 2).contiguous()
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, causal_attention_mask: Optional[torch.Tensor] = None,
    output_attentions: Optional[bool] = False) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        bsz, tgt_len, embed_dim = hidden_states.size()
        query_states = self.q_proj(hidden_states) * self.scale
        key_states = self._shape(self.k_proj(hidden_states), -1, bsz)
        value_states = self._shape(self.v_proj(hidden_states), -1, bsz)
        proj_shape = (bsz * self.num_heads, -1, self.head_dim)
        query_states = self._shape(query_states, tgt_len, bsz).view(*proj_shape)
        key_states = key_states.view(*proj_shape)
        value_states = value_states.view(*proj_shape)
        src_len = key_states.size(1)
        attn_weights = torch.bmm(query_states, key_states.transpose(1, 2))
        if attn_weights.size() != (bsz * self.num_heads, tgt_len, src_len): raise ValueError(f"Attention weights should be of size {(bsz * self.num_heads, tgt_len, src_len)}, but is {attn_weights.size()}")
        if causal_attention_mask is not None:
            if causal_attention_mask.size() != (bsz, 1, tgt_len, src_len): raise ValueError(f"Attention mask should be of size {(bsz, 1, tgt_len, src_len)}, but is {causal_attention_mask.size()}")
            attn_weights = attn_weights.view(bsz, self.num_heads, tgt_len, src_len) + causal_attention_mask
            attn_weights = attn_weights.view(bsz * self.num_heads, tgt_len, src_len)
        if attention_mask is not None:
            if attention_mask.size() != (bsz, 1, tgt_len, src_len): raise ValueError(f"Attention mask should be of size {(bsz, 1, tgt_len, src_len)}, but is {attention_mask.size()}")
            attn_weights = attn_weights.view(bsz, self.num_heads, tgt_len, src_len) + attention_mask
            attn_weights = attn_weights.view(bsz * self.num_heads, tgt_len, src_len)
        attn_weights = nn.functional.softmax(attn_weights, dim=-1)
        if output_attentions:
            attn_weights_reshaped = attn_weights.view(bsz, self.num_heads, tgt_len, src_len)
            attn_weights = attn_weights_reshaped.view(bsz * self.num_heads, tgt_len, src_len)
        else: attn_weights_reshaped = None
        attn_probs = nn.functional.dropout(attn_weights, p=self.dropout, training=self.training)
        attn_output = torch.bmm(attn_probs, value_states)
        if attn_output.size() != (bsz * self.num_heads, tgt_len, self.head_dim): raise ValueError(f"`attn_output` should be of size {(bsz, self.num_heads, tgt_len, self.head_dim)}, but is {attn_output.size()}")
        attn_output = attn_output.view(bsz, self.num_heads, tgt_len, self.head_dim)
        attn_output = attn_output.transpose(1, 2)
        attn_output = attn_output.reshape(bsz, tgt_len, embed_dim)
        attn_output = self.out_proj(attn_output)
        return attn_output, attn_weights_reshaped
class IdeficsVisionMLP(nn.Module):
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
class IdeficsVisionEncoderLayer(nn.Module):
    def __init__(self, config: IdeficsVisionConfig):
        super().__init__()
        self.embed_dim = config.hidden_size
        self.self_attn = IdeficsVisionAttention(config)
        self.layer_norm1 = nn.LayerNorm(self.embed_dim, eps=config.layer_norm_eps)
        self.mlp = IdeficsVisionMLP(config)
        self.layer_norm2 = nn.LayerNorm(self.embed_dim, eps=config.layer_norm_eps)
    def forward(self, hidden_states: torch.Tensor, attention_mask: torch.Tensor, causal_attention_mask: torch.Tensor, output_attentions: Optional[bool] = False) -> Tuple[torch.FloatTensor]:
        residual = hidden_states
        hidden_states = self.layer_norm1(hidden_states)
        hidden_states, attn_weights = self.self_attn(hidden_states=hidden_states, attention_mask=attention_mask, causal_attention_mask=causal_attention_mask, output_attentions=output_attentions)
        hidden_states = residual + hidden_states
        residual = hidden_states
        hidden_states = self.layer_norm2(hidden_states)
        hidden_states = self.mlp(hidden_states)
        hidden_states = residual + hidden_states
        outputs = (hidden_states,)
        if output_attentions: outputs += (attn_weights,)
        return outputs
class IdeficsVisionEncoder(nn.Module):
    def __init__(self, config: IdeficsVisionConfig):
        super().__init__()
        self.config = config
        self.layers = nn.ModuleList([IdeficsVisionEncoderLayer(config) for _ in range(config.num_hidden_layers)])
        self.gradient_checkpointing = False
    def forward(self, inputs_embeds, attention_mask: Optional[torch.Tensor] = None, causal_attention_mask: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutput]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        encoder_states = () if output_hidden_states else None
        all_attentions = () if output_attentions else None
        hidden_states = inputs_embeds
        for idx, encoder_layer in enumerate(self.layers):
            if output_hidden_states: encoder_states = encoder_states + (hidden_states,)
            if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(encoder_layer.__call__, hidden_states, attention_mask, causal_attention_mask, output_attentions)
            else: layer_outputs = encoder_layer(hidden_states, attention_mask, causal_attention_mask, output_attentions=output_attentions)
            hidden_states = layer_outputs[0]
            if output_attentions: all_attentions = all_attentions + (layer_outputs[1],)
        if output_hidden_states: encoder_states = encoder_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, encoder_states, all_attentions] if v is not None)
        return BaseModelOutput(last_hidden_state=hidden_states, hidden_states=encoder_states, attentions=all_attentions)
class IdeficsVisionTransformer(nn.Module):
    def __init__(self, config: IdeficsVisionConfig):
        super().__init__()
        self.config = config
        embed_dim = config.hidden_size
        self.embeddings = IdeficsVisionEmbeddings(config)
        self.pre_layrnorm = nn.LayerNorm(embed_dim, eps=config.layer_norm_eps)
        self.encoder = IdeficsVisionEncoder(config)
        self.post_layernorm = nn.LayerNorm(embed_dim, eps=config.layer_norm_eps)
    def forward(self, pixel_values: Optional[torch.FloatTensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, interpolate_pos_encoding: Optional[bool] = False,
    return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutputWithPooling]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if pixel_values is None: raise ValueError("You have to specify pixel_values")
        hidden_states = self.embeddings(pixel_values, interpolate_pos_encoding=interpolate_pos_encoding)
        hidden_states = self.pre_layrnorm(hidden_states)
        encoder_outputs = self.encoder(inputs_embeds=hidden_states, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        last_hidden_state = encoder_outputs[0]
        pooled_output = last_hidden_state[:, 0, :]
        pooled_output = self.post_layernorm(pooled_output)
        if not return_dict: return (last_hidden_state, pooled_output) + encoder_outputs[1:]
        return BaseModelOutputWithPooling(last_hidden_state=last_hidden_state, pooler_output=pooled_output, hidden_states=encoder_outputs.hidden_states, attentions=encoder_outputs.attentions)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
