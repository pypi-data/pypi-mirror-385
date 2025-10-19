'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..attention_processor import Attention, AttentionProcessor, AuraFlowAttnProcessor2_0, FusedAuraFlowAttnProcessor2_0
from ...configuration_utils import ConfigMixin, register_to_config
from ..normalization import AdaLayerNormZero, FP32LayerNorm
from ..modeling_outputs import Transformer2DModelOutput
from ...utils.torch_utils import maybe_allow_in_graph
from ..embeddings import TimestepEmbedding, Timesteps
from ...utils import is_torch_version
from ..modeling_utils import ModelMixin
from typing import Any, Dict, Union
import torch.nn.functional as F
import torch.nn as nn
import torch
def find_multiple(n: int, k: int) -> int:
    if n % k == 0: return n
    return n + k - n % k
class AuraFlowPatchEmbed(nn.Module):
    def __init__(self, height=224, width=224, patch_size=16, in_channels=3, embed_dim=768, pos_embed_max_size=None):
        super().__init__()
        self.num_patches = height // patch_size * (width // patch_size)
        self.pos_embed_max_size = pos_embed_max_size
        self.proj = nn.Linear(patch_size * patch_size * in_channels, embed_dim)
        self.pos_embed = nn.Parameter(torch.randn(1, pos_embed_max_size, embed_dim) * 0.1)
        self.patch_size = patch_size
        self.height, self.width = (height // patch_size, width // patch_size)
        self.base_size = height // patch_size
    def pe_selection_index_based_on_dim(self, h, w):
        h_p, w_p = (h // self.patch_size, w // self.patch_size)
        original_pe_indexes = torch.arange(self.pos_embed.shape[1])
        h_max, w_max = (int(self.pos_embed_max_size ** 0.5), int(self.pos_embed_max_size ** 0.5))
        original_pe_indexes = original_pe_indexes.view(h_max, w_max)
        starth = h_max // 2 - h_p // 2
        endh = starth + h_p
        startw = w_max // 2 - w_p // 2
        endw = startw + w_p
        original_pe_indexes = original_pe_indexes[starth:endh, startw:endw]
        return original_pe_indexes.flatten()
    def forward(self, latent):
        batch_size, num_channels, height, width = latent.size()
        latent = latent.view(batch_size, num_channels, height // self.patch_size, self.patch_size, width // self.patch_size, self.patch_size)
        latent = latent.permute(0, 2, 4, 1, 3, 5).flatten(-3).flatten(1, 2)
        latent = self.proj(latent)
        pe_index = self.pe_selection_index_based_on_dim(height, width)
        return latent + self.pos_embed[:, pe_index]
class AuraFlowFeedForward(nn.Module):
    def __init__(self, dim, hidden_dim=None) -> None:
        super().__init__()
        if hidden_dim is None: hidden_dim = 4 * dim
        final_hidden_dim = int(2 * hidden_dim / 3)
        final_hidden_dim = find_multiple(final_hidden_dim, 256)
        self.linear_1 = nn.Linear(dim, final_hidden_dim, bias=False)
        self.linear_2 = nn.Linear(dim, final_hidden_dim, bias=False)
        self.out_projection = nn.Linear(final_hidden_dim, dim, bias=False)
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.silu(self.linear_1(x)) * self.linear_2(x)
        x = self.out_projection(x)
        return x
class AuraFlowPreFinalBlock(nn.Module):
    def __init__(self, embedding_dim: int, conditioning_embedding_dim: int):
        super().__init__()
        self.silu = nn.SiLU()
        self.linear = nn.Linear(conditioning_embedding_dim, embedding_dim * 2, bias=False)
    def forward(self, x: torch.Tensor, conditioning_embedding: torch.Tensor) -> torch.Tensor:
        emb = self.linear(self.silu(conditioning_embedding).to(x.dtype))
        scale, shift = torch.chunk(emb, 2, dim=1)
        x = x * (1 + scale)[:, None, :] + shift[:, None, :]
        return x
@maybe_allow_in_graph
class AuraFlowSingleTransformerBlock(nn.Module):
    def __init__(self, dim, num_attention_heads, attention_head_dim):
        super().__init__()
        self.norm1 = AdaLayerNormZero(dim, bias=False, norm_type='fp32_layer_norm')
        processor = AuraFlowAttnProcessor2_0()
        self.attn = Attention(query_dim=dim, cross_attention_dim=None, dim_head=attention_head_dim, heads=num_attention_heads, qk_norm='fp32_layer_norm',
        out_dim=dim, bias=False, out_bias=False, processor=processor)
        self.norm2 = FP32LayerNorm(dim, elementwise_affine=False, bias=False)
        self.ff = AuraFlowFeedForward(dim, dim * 4)
    def forward(self, hidden_states: torch.FloatTensor, temb: torch.FloatTensor):
        residual = hidden_states
        norm_hidden_states, gate_msa, shift_mlp, scale_mlp, gate_mlp = self.norm1(hidden_states, emb=temb)
        attn_output = self.attn(hidden_states=norm_hidden_states)
        hidden_states = self.norm2(residual + gate_msa.unsqueeze(1) * attn_output)
        hidden_states = hidden_states * (1 + scale_mlp[:, None]) + shift_mlp[:, None]
        ff_output = self.ff(hidden_states)
        hidden_states = gate_mlp.unsqueeze(1) * ff_output
        hidden_states = residual + hidden_states
        return hidden_states
@maybe_allow_in_graph
class AuraFlowJointTransformerBlock(nn.Module):
    def __init__(self, dim, num_attention_heads, attention_head_dim):
        super().__init__()
        self.norm1 = AdaLayerNormZero(dim, bias=False, norm_type='fp32_layer_norm')
        self.norm1_context = AdaLayerNormZero(dim, bias=False, norm_type='fp32_layer_norm')
        processor = AuraFlowAttnProcessor2_0()
        self.attn = Attention(query_dim=dim, cross_attention_dim=None, added_kv_proj_dim=dim, added_proj_bias=False, dim_head=attention_head_dim, heads=num_attention_heads,
        qk_norm='fp32_layer_norm', out_dim=dim, bias=False, out_bias=False, processor=processor, context_pre_only=False)
        self.norm2 = FP32LayerNorm(dim, elementwise_affine=False, bias=False)
        self.ff = AuraFlowFeedForward(dim, dim * 4)
        self.norm2_context = FP32LayerNorm(dim, elementwise_affine=False, bias=False)
        self.ff_context = AuraFlowFeedForward(dim, dim * 4)
    def forward(self, hidden_states: torch.FloatTensor, encoder_hidden_states: torch.FloatTensor, temb: torch.FloatTensor):
        residual = hidden_states
        residual_context = encoder_hidden_states
        norm_hidden_states, gate_msa, shift_mlp, scale_mlp, gate_mlp = self.norm1(hidden_states, emb=temb)
        norm_encoder_hidden_states, c_gate_msa, c_shift_mlp, c_scale_mlp, c_gate_mlp = self.norm1_context(encoder_hidden_states, emb=temb)
        attn_output, context_attn_output = self.attn(hidden_states=norm_hidden_states, encoder_hidden_states=norm_encoder_hidden_states)
        hidden_states = self.norm2(residual + gate_msa.unsqueeze(1) * attn_output)
        hidden_states = hidden_states * (1 + scale_mlp[:, None]) + shift_mlp[:, None]
        hidden_states = gate_mlp.unsqueeze(1) * self.ff(hidden_states)
        hidden_states = residual + hidden_states
        encoder_hidden_states = self.norm2_context(residual_context + c_gate_msa.unsqueeze(1) * context_attn_output)
        encoder_hidden_states = encoder_hidden_states * (1 + c_scale_mlp[:, None]) + c_shift_mlp[:, None]
        encoder_hidden_states = c_gate_mlp.unsqueeze(1) * self.ff_context(encoder_hidden_states)
        encoder_hidden_states = residual_context + encoder_hidden_states
        return (encoder_hidden_states, hidden_states)
class AuraFlowTransformer2DModel(ModelMixin, ConfigMixin):
    _no_split_modules = ['AuraFlowJointTransformerBlock', 'AuraFlowSingleTransformerBlock', 'AuraFlowPatchEmbed']
    _supports_gradient_checkpointing = True
    @register_to_config
    def __init__(self, sample_size: int=64, patch_size: int=2, in_channels: int=4, num_mmdit_layers: int=4, num_single_dit_layers: int=32, attention_head_dim: int=256,
    num_attention_heads: int=12, joint_attention_dim: int=2048, caption_projection_dim: int=3072, out_channels: int=4, pos_embed_max_size: int=1024):
        super().__init__()
        default_out_channels = in_channels
        self.out_channels = out_channels if out_channels is not None else default_out_channels
        self.inner_dim = self.config.num_attention_heads * self.config.attention_head_dim
        self.pos_embed = AuraFlowPatchEmbed(height=self.config.sample_size, width=self.config.sample_size, patch_size=self.config.patch_size, in_channels=self.config.in_channels,
        embed_dim=self.inner_dim, pos_embed_max_size=pos_embed_max_size)
        self.context_embedder = nn.Linear(self.config.joint_attention_dim, self.config.caption_projection_dim, bias=False)
        self.time_step_embed = Timesteps(num_channels=256, downscale_freq_shift=0, scale=1000, flip_sin_to_cos=True)
        self.time_step_proj = TimestepEmbedding(in_channels=256, time_embed_dim=self.inner_dim)
        self.joint_transformer_blocks = nn.ModuleList([AuraFlowJointTransformerBlock(dim=self.inner_dim, num_attention_heads=self.config.num_attention_heads,
        attention_head_dim=self.config.attention_head_dim) for i in range(self.config.num_mmdit_layers)])
        self.single_transformer_blocks = nn.ModuleList([AuraFlowSingleTransformerBlock(dim=self.inner_dim, num_attention_heads=self.config.num_attention_heads,
        attention_head_dim=self.config.attention_head_dim) for _ in range(self.config.num_single_dit_layers)])
        self.norm_out = AuraFlowPreFinalBlock(self.inner_dim, self.inner_dim)
        self.proj_out = nn.Linear(self.inner_dim, patch_size * patch_size * self.out_channels, bias=False)
        self.register_tokens = nn.Parameter(torch.randn(1, 8, self.inner_dim) * 0.02)
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
        self.set_attn_processor(FusedAuraFlowAttnProcessor2_0())
    def unfuse_qkv_projections(self):
        if self.original_attn_processors is not None: self.set_attn_processor(self.original_attn_processors)
    def _set_gradient_checkpointing(self, module, value=False):
        if hasattr(module, 'gradient_checkpointing'): module.gradient_checkpointing = value
    def forward(self, hidden_states: torch.FloatTensor, encoder_hidden_states: torch.FloatTensor=None, timestep: torch.LongTensor=None,
    return_dict: bool=True) -> Union[torch.FloatTensor, Transformer2DModelOutput]:
        height, width = hidden_states.shape[-2:]
        hidden_states = self.pos_embed(hidden_states)
        temb = self.time_step_embed(timestep).to(dtype=next(self.parameters()).dtype)
        temb = self.time_step_proj(temb)
        encoder_hidden_states = self.context_embedder(encoder_hidden_states)
        encoder_hidden_states = torch.cat([self.register_tokens.repeat(encoder_hidden_states.size(0), 1, 1), encoder_hidden_states], dim=1)
        for index_block, block in enumerate(self.joint_transformer_blocks):
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module, return_dict=None):
                    def custom_forward(*inputs):
                        if return_dict is not None: return module(*inputs, return_dict=return_dict)
                        else: return module(*inputs)
                    return custom_forward
                ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
                encoder_hidden_states, hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(block), hidden_states, encoder_hidden_states, temb, **ckpt_kwargs)
            else: encoder_hidden_states, hidden_states = block(hidden_states=hidden_states, encoder_hidden_states=encoder_hidden_states, temb=temb)
        if len(self.single_transformer_blocks) > 0:
            encoder_seq_len = encoder_hidden_states.size(1)
            combined_hidden_states = torch.cat([encoder_hidden_states, hidden_states], dim=1)
            for index_block, block in enumerate(self.single_transformer_blocks):
                if torch.is_grad_enabled() and self.gradient_checkpointing:
                    def create_custom_forward(module, return_dict=None):
                        def custom_forward(*inputs):
                            if return_dict is not None: return module(*inputs, return_dict=return_dict)
                            else: return module(*inputs)
                        return custom_forward
                    ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
                    combined_hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(block), combined_hidden_states, temb, **ckpt_kwargs)
                else: combined_hidden_states = block(hidden_states=combined_hidden_states, temb=temb)
            hidden_states = combined_hidden_states[:, encoder_seq_len:]
        hidden_states = self.norm_out(hidden_states, temb)
        hidden_states = self.proj_out(hidden_states)
        patch_size = self.config.patch_size
        out_channels = self.config.out_channels
        height = height // patch_size
        width = width // patch_size
        hidden_states = hidden_states.reshape(shape=(hidden_states.shape[0], height, width, patch_size, patch_size, out_channels))
        hidden_states = torch.einsum('nhwpqc->nchpwq', hidden_states)
        output = hidden_states.reshape(shape=(hidden_states.shape[0], out_channels, height * patch_size, width * patch_size))
        if not return_dict: return (output,)
        return Transformer2DModelOutput(sample=output)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
