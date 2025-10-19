'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import torch
from torch import nn
from sapiens_transformers import CLIPPreTrainedModel, CLIPVisionModel
from ...models.attention import BasicTransformerBlock
class PaintByExampleImageEncoder(CLIPPreTrainedModel):
    def __init__(self, config, proj_size=None):
        super().__init__(config)
        self.proj_size = proj_size or getattr(config, 'projection_dim', 768)
        self.model = CLIPVisionModel(config)
        self.mapper = PaintByExampleMapper(config)
        self.final_layer_norm = nn.LayerNorm(config.hidden_size)
        self.proj_out = nn.Linear(config.hidden_size, self.proj_size)
        self.uncond_vector = nn.Parameter(torch.randn((1, 1, self.proj_size)))
    def forward(self, pixel_values, return_uncond_vector=False):
        clip_output = self.model(pixel_values=pixel_values)
        latent_states = clip_output.pooler_output
        latent_states = self.mapper(latent_states[:, None])
        latent_states = self.final_layer_norm(latent_states)
        latent_states = self.proj_out(latent_states)
        if return_uncond_vector: return (latent_states, self.uncond_vector)
        return latent_states
class PaintByExampleMapper(nn.Module):
    def __init__(self, config):
        super().__init__()
        num_layers = (config.num_hidden_layers + 1) // 5
        hid_size = config.hidden_size
        num_heads = 1
        self.blocks = nn.ModuleList([BasicTransformerBlock(hid_size, num_heads, hid_size, activation_fn='gelu', attention_bias=True) for _ in range(num_layers)])
    def forward(self, hidden_states):
        for block in self.blocks: hidden_states = block(hidden_states)
        return hidden_states
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
