'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...models.attention_processor import Attention, AttentionProcessor, SAPIPhotoGenAttnProcessor2_0, SAPIPhotoGenAttnProcessor2_0_NPU, FusedSAPIPhotoGenAttnProcessor2_0
from ..embeddings import CombinedTimestepGuidanceTextProjEmbeddings, CombinedTimestepTextProjEmbeddings, SAPIPhotoGenPosEmbed
from ...utils import USE_PEFT_BACKEND, is_torch_version, scale_lora_layers, unscale_lora_layers
from ...models.normalization import AdaLayerNormContinuous, AdaLayerNormZero, AdaLayerNormZeroSingle
from ...loaders import SAPIPhotoGenTransformer2DLoadersMixin, FromOriginalModelMixin, PeftAdapterMixin
from ...configuration_utils import ConfigMixin, register_to_config
from ...utils.import_utils import is_torch_npu_available
from ..modeling_outputs import Transformer2DModelOutput
from ...utils.torch_utils import maybe_allow_in_graph
from typing import Any, Dict, Optional, Tuple, Union
from ...models.modeling_utils import ModelMixin
from ...models.attention import FeedForward
import torch.nn.functional as F
import torch.nn as nn
import numpy as np
import torch
@maybe_allow_in_graph
class SAPIPhotoGenSingleTransformerBlock(nn.Module):
    def __init__(self, dim, num_attention_heads, attention_head_dim, mlp_ratio=4.0):
        super().__init__()
        self.mlp_hidden_dim = int(dim * mlp_ratio)
        self.norm = AdaLayerNormZeroSingle(dim)
        self.proj_mlp = nn.Linear(dim, self.mlp_hidden_dim)
        self.act_mlp = nn.GELU(approximate='tanh')
        self.proj_out = nn.Linear(dim + self.mlp_hidden_dim, dim)
        if is_torch_npu_available(): processor = SAPIPhotoGenAttnProcessor2_0_NPU()
        else: processor = SAPIPhotoGenAttnProcessor2_0()
        self.attn = Attention(query_dim=dim, cross_attention_dim=None, dim_head=attention_head_dim, heads=num_attention_heads, out_dim=dim, bias=True, processor=processor, qk_norm='rms_norm', eps=1e-06, pre_only=True)
    def forward(self, hidden_states: torch.FloatTensor, temb: torch.FloatTensor, image_rotary_emb=None, joint_attention_kwargs=None):
        residual = hidden_states
        norm_hidden_states, gate = self.norm(hidden_states, emb=temb)
        mlp_hidden_states = self.act_mlp(self.proj_mlp(norm_hidden_states))
        joint_attention_kwargs = joint_attention_kwargs or {}
        attn_output = self.attn(hidden_states=norm_hidden_states, image_rotary_emb=image_rotary_emb, **joint_attention_kwargs)
        hidden_states = torch.cat([attn_output, mlp_hidden_states], dim=2)
        gate = gate.unsqueeze(1)
        hidden_states = gate * self.proj_out(hidden_states)
        hidden_states = residual + hidden_states
        if hidden_states.dtype == torch.float16: hidden_states = hidden_states.clip(-65504, 65504)
        return hidden_states
@maybe_allow_in_graph
class SAPIPhotoGenTransformerBlock(nn.Module):
    def __init__(self, dim, num_attention_heads, attention_head_dim, qk_norm='rms_norm', eps=1e-06):
        super().__init__()
        self.norm1 = AdaLayerNormZero(dim)
        self.norm1_context = AdaLayerNormZero(dim)
        if hasattr(F, 'scaled_dot_product_attention'): processor = SAPIPhotoGenAttnProcessor2_0()
        else: raise ValueError('The current PyTorch version does not support the `scaled_dot_product_attention` function.')
        self.attn = Attention(query_dim=dim, cross_attention_dim=None, added_kv_proj_dim=dim, dim_head=attention_head_dim, heads=num_attention_heads, out_dim=dim, context_pre_only=False, bias=True, processor=processor, qk_norm=qk_norm, eps=eps)
        self.norm2 = nn.LayerNorm(dim, elementwise_affine=False, eps=1e-06)
        self.ff = FeedForward(dim=dim, dim_out=dim, activation_fn='gelu-approximate')
        self.norm2_context = nn.LayerNorm(dim, elementwise_affine=False, eps=1e-06)
        self.ff_context = FeedForward(dim=dim, dim_out=dim, activation_fn='gelu-approximate')
        self._chunk_size = None
        self._chunk_dim = 0
    def forward(self, hidden_states: torch.FloatTensor, encoder_hidden_states: torch.FloatTensor, temb: torch.FloatTensor, image_rotary_emb=None, joint_attention_kwargs=None):
        norm_hidden_states, gate_msa, shift_mlp, scale_mlp, gate_mlp = self.norm1(hidden_states, emb=temb)
        norm_encoder_hidden_states, c_gate_msa, c_shift_mlp, c_scale_mlp, c_gate_mlp = self.norm1_context(encoder_hidden_states, emb=temb)
        joint_attention_kwargs = joint_attention_kwargs or {}
        attention_outputs = self.attn(hidden_states=norm_hidden_states, encoder_hidden_states=norm_encoder_hidden_states, image_rotary_emb=image_rotary_emb, **joint_attention_kwargs)
        if len(attention_outputs) == 2: attn_output, context_attn_output = attention_outputs
        elif len(attention_outputs) == 3: attn_output, context_attn_output, ip_attn_output = attention_outputs
        attn_output = gate_msa.unsqueeze(1) * attn_output
        hidden_states = hidden_states + attn_output
        norm_hidden_states = self.norm2(hidden_states)
        norm_hidden_states = norm_hidden_states * (1 + scale_mlp[:, None]) + shift_mlp[:, None]
        ff_output = self.ff(norm_hidden_states)
        ff_output = gate_mlp.unsqueeze(1) * ff_output
        hidden_states = hidden_states + ff_output
        if len(attention_outputs) == 3: hidden_states = hidden_states + ip_attn_output
        context_attn_output = c_gate_msa.unsqueeze(1) * context_attn_output
        encoder_hidden_states = encoder_hidden_states + context_attn_output
        norm_encoder_hidden_states = self.norm2_context(encoder_hidden_states)
        norm_encoder_hidden_states = norm_encoder_hidden_states * (1 + c_scale_mlp[:, None]) + c_shift_mlp[:, None]
        context_ff_output = self.ff_context(norm_encoder_hidden_states)
        encoder_hidden_states = encoder_hidden_states + c_gate_mlp.unsqueeze(1) * context_ff_output
        if encoder_hidden_states.dtype == torch.float16: encoder_hidden_states = encoder_hidden_states.clip(-65504, 65504)
        return (encoder_hidden_states, hidden_states)
class SAPIPhotoGenTransformer2DModel(ModelMixin, ConfigMixin, PeftAdapterMixin, FromOriginalModelMixin, SAPIPhotoGenTransformer2DLoadersMixin):
    _supports_gradient_checkpointing = True
    _no_split_modules = ['SAPIPhotoGenTransformerBlock', 'SAPIPhotoGenSingleTransformerBlock']
    @register_to_config
    def __init__(self, patch_size: int=1, in_channels: int=64, out_channels: Optional[int]=None, num_layers: int=19, num_single_layers: int=38, attention_head_dim: int=128, num_attention_heads: int=24,
    joint_attention_dim: int=4096, pooled_projection_dim: int=768, guidance_embeds: bool=False, axes_dims_rope: Tuple[int]=(16, 56, 56)):
        super().__init__()
        self.out_channels = out_channels or in_channels
        self.inner_dim = self.config.num_attention_heads * self.config.attention_head_dim
        self.pos_embed = SAPIPhotoGenPosEmbed(theta=10000, axes_dim=axes_dims_rope)
        text_time_guidance_cls = CombinedTimestepGuidanceTextProjEmbeddings if guidance_embeds else CombinedTimestepTextProjEmbeddings
        self.time_text_embed = text_time_guidance_cls(embedding_dim=self.inner_dim, pooled_projection_dim=self.config.pooled_projection_dim)
        self.context_embedder = nn.Linear(self.config.joint_attention_dim, self.inner_dim)
        self.x_embedder = nn.Linear(self.config.in_channels, self.inner_dim)
        self.transformer_blocks = nn.ModuleList([SAPIPhotoGenTransformerBlock(dim=self.inner_dim, num_attention_heads=self.config.num_attention_heads, attention_head_dim=self.config.attention_head_dim) for i in range(self.config.num_layers)])
        self.single_transformer_blocks = nn.ModuleList([SAPIPhotoGenSingleTransformerBlock(dim=self.inner_dim, num_attention_heads=self.config.num_attention_heads, attention_head_dim=self.config.attention_head_dim) for i in range(self.config.num_single_layers)])
        self.norm_out = AdaLayerNormContinuous(self.inner_dim, self.inner_dim, elementwise_affine=False, eps=1e-06)
        self.proj_out = nn.Linear(self.inner_dim, patch_size * patch_size * self.out_channels, bias=True)
        self.gradient_checkpointing = False
    @property
    def attn_processors(self) -> Dict[str, AttentionProcessor]:
        """Returns:"""
        processors = {}
        def fn_recursive_add_processors(name: str, module: torch.nn.Module, processors: Dict[str, AttentionProcessor]):
            if hasattr(module, 'get_processor'): processors[f'{name}.processor'] = module.get_processor()
            for sub_name, child in module.named_children(): fn_recursive_add_processors(f'{name}.{sub_name}', child, processors)
            return processors
        for name, module in self.named_children(): fn_recursive_add_processors(name, module, processors)
        return processors
    def set_attn_processor(self, processor: Union[AttentionProcessor, Dict[str, AttentionProcessor]]):
        count = len(self.attn_processors.keys())
        if isinstance(processor, dict) and len(processor) != count:
            raise ValueError(f'A dict of processors was passed, but the number of processors {len(processor)} does not match the number of attention layers: {count}. Please make sure to pass {count} processor classes.')
        def fn_recursive_attn_processor(name: str, module: torch.nn.Module, processor):
            if hasattr(module, 'set_processor'):
                if not isinstance(processor, dict): module.set_processor(processor)
                else: module.set_processor(processor.pop(f'{name}.processor'))
            for sub_name, child in module.named_children(): fn_recursive_attn_processor(f'{name}.{sub_name}', child, processor)
        for name, module in self.named_children(): fn_recursive_attn_processor(name, module, processor)
    def fuse_qkv_projections(self):
        self.original_attn_processors = None
        for _, attn_processor in self.attn_processors.items():
            if 'Added' in str(attn_processor.__class__.__name__): raise ValueError('`fuse_qkv_projections()` is not supported for models having added KV projections.')
        self.original_attn_processors = self.attn_processors
        for module in self.modules():
            if isinstance(module, Attention): module.fuse_projections(fuse=True)
        self.set_attn_processor(FusedSAPIPhotoGenAttnProcessor2_0())
    def unfuse_qkv_projections(self):
        if self.original_attn_processors is not None: self.set_attn_processor(self.original_attn_processors)
    def _set_gradient_checkpointing(self, module, value=False):
        if hasattr(module, 'gradient_checkpointing'): module.gradient_checkpointing = value
    def forward(self, hidden_states: torch.Tensor, encoder_hidden_states: torch.Tensor=None, pooled_projections: torch.Tensor=None, timestep: torch.LongTensor=None, img_ids: torch.Tensor=None,
    txt_ids: torch.Tensor=None, guidance: torch.Tensor=None, joint_attention_kwargs: Optional[Dict[str, Any]]=None, controlnet_block_samples=None, controlnet_single_block_samples=None, return_dict: bool=True,
    controlnet_blocks_repeat: bool=False) -> Union[torch.FloatTensor, Transformer2DModelOutput]:
        """Returns:"""
        if joint_attention_kwargs is not None:
            joint_attention_kwargs = joint_attention_kwargs.copy()
            lora_scale = joint_attention_kwargs.pop('scale', 1.0)
        else: lora_scale = 1.0
        if USE_PEFT_BACKEND: scale_lora_layers(self, lora_scale)
        hidden_states = self.x_embedder(hidden_states)
        timestep = timestep.to(hidden_states.dtype) * 1000
        if guidance is not None: guidance = guidance.to(hidden_states.dtype) * 1000
        else: guidance = None
        temb = self.time_text_embed(timestep, pooled_projections) if guidance is None else self.time_text_embed(timestep, guidance, pooled_projections)
        encoder_hidden_states = self.context_embedder(encoder_hidden_states)
        if txt_ids.ndim == 3: txt_ids = txt_ids[0]
        if img_ids.ndim == 3: img_ids = img_ids[0]
        ids = torch.cat((txt_ids, img_ids), dim=0)
        image_rotary_emb = self.pos_embed(ids)
        if joint_attention_kwargs is not None and 'ip_adapter_image_embeds' in joint_attention_kwargs:
            ip_adapter_image_embeds = joint_attention_kwargs.pop('ip_adapter_image_embeds')
            ip_hidden_states = self.encoder_hid_proj(ip_adapter_image_embeds)
            joint_attention_kwargs.update({'ip_hidden_states': ip_hidden_states})
        for index_block, block in enumerate(self.transformer_blocks):
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module, return_dict=None):
                    def custom_forward(*inputs):
                        if return_dict is not None: return module(*inputs, return_dict=return_dict)
                        else: return module(*inputs)
                    return custom_forward
                ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
                encoder_hidden_states, hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(block), hidden_states, encoder_hidden_states, temb, image_rotary_emb, **ckpt_kwargs)
            else: encoder_hidden_states, hidden_states = block(hidden_states=hidden_states, encoder_hidden_states=encoder_hidden_states, temb=temb, image_rotary_emb=image_rotary_emb, joint_attention_kwargs=joint_attention_kwargs)
            if controlnet_block_samples is not None:
                interval_control = len(self.transformer_blocks) / len(controlnet_block_samples)
                interval_control = int(np.ceil(interval_control))
                if controlnet_blocks_repeat: hidden_states = hidden_states + controlnet_block_samples[index_block % len(controlnet_block_samples)]
                else: hidden_states = hidden_states + controlnet_block_samples[index_block // interval_control]
        hidden_states = torch.cat([encoder_hidden_states, hidden_states], dim=1)
        for index_block, block in enumerate(self.single_transformer_blocks):
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module, return_dict=None):
                    def custom_forward(*inputs):
                        if return_dict is not None: return module(*inputs, return_dict=return_dict)
                        else: return module(*inputs)
                    return custom_forward
                ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
                hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(block), hidden_states, temb, image_rotary_emb, **ckpt_kwargs)
            else: hidden_states = block(hidden_states=hidden_states, temb=temb, image_rotary_emb=image_rotary_emb, joint_attention_kwargs=joint_attention_kwargs)
            if controlnet_single_block_samples is not None:
                interval_control = len(self.single_transformer_blocks) / len(controlnet_single_block_samples)
                interval_control = int(np.ceil(interval_control))
                hidden_states[:, encoder_hidden_states.shape[1]:, ...] = hidden_states[:, encoder_hidden_states.shape[1]:, ...] + controlnet_single_block_samples[index_block // interval_control]
        hidden_states = hidden_states[:, encoder_hidden_states.shape[1]:, ...]
        hidden_states = self.norm_out(hidden_states, temb)
        output = self.proj_out(hidden_states)
        if USE_PEFT_BACKEND: unscale_lora_layers(self, lora_scale)
        if not return_dict: return (output,)
        return Transformer2DModelOutput(sample=output)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
