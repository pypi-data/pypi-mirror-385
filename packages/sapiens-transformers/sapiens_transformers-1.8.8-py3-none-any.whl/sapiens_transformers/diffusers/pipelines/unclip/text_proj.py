'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import torch
from torch import nn
from ...configuration_utils import ConfigMixin, register_to_config
from ...models import ModelMixin
class UnCLIPTextProjModel(ModelMixin, ConfigMixin):
    @register_to_config
    def __init__(self, *, clip_extra_context_tokens: int=4, clip_embeddings_dim: int=768, time_embed_dim: int, cross_attention_dim):
        super().__init__()
        self.learned_classifier_free_guidance_embeddings = nn.Parameter(torch.zeros(clip_embeddings_dim))
        self.embedding_proj = nn.Linear(clip_embeddings_dim, time_embed_dim)
        self.clip_image_embeddings_project_to_time_embeddings = nn.Linear(clip_embeddings_dim, time_embed_dim)
        self.clip_extra_context_tokens = clip_extra_context_tokens
        self.clip_extra_context_tokens_proj = nn.Linear(clip_embeddings_dim, self.clip_extra_context_tokens * cross_attention_dim)
        self.encoder_hidden_states_proj = nn.Linear(clip_embeddings_dim, cross_attention_dim)
        self.text_encoder_hidden_states_norm = nn.LayerNorm(cross_attention_dim)
    def forward(self, *, image_embeddings, prompt_embeds, text_encoder_hidden_states, do_classifier_free_guidance):
        if do_classifier_free_guidance:
            image_embeddings_batch_size = image_embeddings.shape[0]
            classifier_free_guidance_embeddings = self.learned_classifier_free_guidance_embeddings.unsqueeze(0)
            classifier_free_guidance_embeddings = classifier_free_guidance_embeddings.expand(image_embeddings_batch_size, -1)
            image_embeddings = torch.cat([classifier_free_guidance_embeddings, image_embeddings], dim=0)
        assert image_embeddings.shape[0] == prompt_embeds.shape[0]
        batch_size = prompt_embeds.shape[0]
        time_projected_prompt_embeds = self.embedding_proj(prompt_embeds)
        time_projected_image_embeddings = self.clip_image_embeddings_project_to_time_embeddings(image_embeddings)
        additive_clip_time_embeddings = time_projected_image_embeddings + time_projected_prompt_embeds
        clip_extra_context_tokens = self.clip_extra_context_tokens_proj(image_embeddings)
        clip_extra_context_tokens = clip_extra_context_tokens.reshape(batch_size, -1, self.clip_extra_context_tokens)
        clip_extra_context_tokens = clip_extra_context_tokens.permute(0, 2, 1)
        text_encoder_hidden_states = self.encoder_hidden_states_proj(text_encoder_hidden_states)
        text_encoder_hidden_states = self.text_encoder_hidden_states_norm(text_encoder_hidden_states)
        text_encoder_hidden_states = torch.cat([clip_extra_context_tokens, text_encoder_hidden_states], dim=1)
        return (text_encoder_hidden_states, additive_clip_time_embeddings)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
