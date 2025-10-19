'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import Optional, Tuple
import jax
import jax.numpy as jnp
from flax import linen as nn
from flax.core.frozen_dict import FrozenDict
from sapiens_transformers import CLIPConfig, FlaxPreTrainedModel
from sapiens_transformers.models.clip.modeling_flax_clip import FlaxCLIPVisionModule
def jax_cosine_distance(emb_1, emb_2, eps=1e-12):
    norm_emb_1 = jnp.divide(emb_1.T, jnp.clip(jnp.linalg.norm(emb_1, axis=1), a_min=eps)).T
    norm_emb_2 = jnp.divide(emb_2.T, jnp.clip(jnp.linalg.norm(emb_2, axis=1), a_min=eps)).T
    return jnp.matmul(norm_emb_1, norm_emb_2.T)
class FlaxStableDiffusionSafetyCheckerModule(nn.Module):
    config: CLIPConfig
    dtype: jnp.dtype = jnp.float32
    def setup(self):
        self.vision_model = FlaxCLIPVisionModule(self.config.vision_config)
        self.visual_projection = nn.Dense(self.config.projection_dim, use_bias=False, dtype=self.dtype)
        self.concept_embeds = self.param('concept_embeds', jax.nn.initializers.ones, (17, self.config.projection_dim))
        self.special_care_embeds = self.param('special_care_embeds', jax.nn.initializers.ones, (3, self.config.projection_dim))
        self.concept_embeds_weights = self.param('concept_embeds_weights', jax.nn.initializers.ones, (17,))
        self.special_care_embeds_weights = self.param('special_care_embeds_weights', jax.nn.initializers.ones, (3,))
    def __call__(self, clip_input):
        pooled_output = self.vision_model(clip_input)[1]
        image_embeds = self.visual_projection(pooled_output)
        special_cos_dist = jax_cosine_distance(image_embeds, self.special_care_embeds)
        cos_dist = jax_cosine_distance(image_embeds, self.concept_embeds)
        adjustment = 0.0
        special_scores = special_cos_dist - self.special_care_embeds_weights[None, :] + adjustment
        special_scores = jnp.round(special_scores, 3)
        is_special_care = jnp.any(special_scores > 0, axis=1, keepdims=True)
        special_adjustment = is_special_care * 0.01
        concept_scores = cos_dist - self.concept_embeds_weights[None, :] + special_adjustment
        concept_scores = jnp.round(concept_scores, 3)
        has_nsfw_concepts = jnp.any(concept_scores > 0, axis=1)
        return has_nsfw_concepts
class FlaxStableDiffusionSafetyChecker(FlaxPreTrainedModel):
    config_class = CLIPConfig
    main_input_name = 'clip_input'
    module_class = FlaxStableDiffusionSafetyCheckerModule
    def __init__(self, config: CLIPConfig, input_shape: Optional[Tuple]=None, seed: int=0, dtype: jnp.dtype=jnp.float32, _do_init: bool=True, **kwargs):
        if input_shape is None: input_shape = (1, 224, 224, 3)
        module = self.module_class(config=config, dtype=dtype, **kwargs)
        super().__init__(config, module, input_shape=input_shape, seed=seed, dtype=dtype, _do_init=_do_init)
    def init_weights(self, rng: jax.Array, input_shape: Tuple, params: FrozenDict=None) -> FrozenDict:
        clip_input = jax.random.normal(rng, input_shape)
        params_rng, dropout_rng = jax.random.split(rng)
        rngs = {'params': params_rng, 'dropout': dropout_rng}
        random_params = self.module.init(rngs, clip_input)['params']
        return random_params
    def __call__(self, clip_input, params: dict=None):
        clip_input = jnp.transpose(clip_input, (0, 2, 3, 1))
        return self.module.apply({'params': params or self.params}, jnp.array(clip_input, dtype=jnp.float32), rngs={})
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
