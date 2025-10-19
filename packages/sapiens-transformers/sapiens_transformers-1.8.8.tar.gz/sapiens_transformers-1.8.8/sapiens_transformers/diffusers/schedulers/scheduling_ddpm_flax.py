'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from dataclasses import dataclass
from typing import Optional, Tuple, Union
import flax
import jax
import jax.numpy as jnp
from ..configuration_utils import ConfigMixin, register_to_config
from .scheduling_utils_flax import CommonSchedulerState, FlaxKarrasDiffusionSchedulers, FlaxSchedulerMixin, FlaxSchedulerOutput, add_noise_common, get_velocity_common
@flax.struct.dataclass
class DDPMSchedulerState:
    common: CommonSchedulerState
    init_noise_sigma: jnp.ndarray
    timesteps: jnp.ndarray
    num_inference_steps: Optional[int] = None
    @classmethod
    def create(cls, common: CommonSchedulerState, init_noise_sigma: jnp.ndarray, timesteps: jnp.ndarray): return cls(common=common, init_noise_sigma=init_noise_sigma, timesteps=timesteps)
@dataclass
class FlaxDDPMSchedulerOutput(FlaxSchedulerOutput):
    state: DDPMSchedulerState
class FlaxDDPMScheduler(FlaxSchedulerMixin, ConfigMixin):
    """Args:"""
    _compatibles = [e.name for e in FlaxKarrasDiffusionSchedulers]
    dtype: jnp.dtype
    @property
    def has_state(self): return True
    @register_to_config
    def __init__(self, num_train_timesteps: int=1000, beta_start: float=0.0001, beta_end: float=0.02, beta_schedule: str='linear', trained_betas: Optional[jnp.ndarray]=None,
    variance_type: str='fixed_small', clip_sample: bool=True, prediction_type: str='epsilon', dtype: jnp.dtype=jnp.float32): self.dtype = dtype
    def create_state(self, common: Optional[CommonSchedulerState]=None) -> DDPMSchedulerState:
        if common is None: common = CommonSchedulerState.create(self)
        init_noise_sigma = jnp.array(1.0, dtype=self.dtype)
        timesteps = jnp.arange(0, self.config.num_train_timesteps).round()[::-1]
        return DDPMSchedulerState.create(common=common, init_noise_sigma=init_noise_sigma, timesteps=timesteps)
    def scale_model_input(self, state: DDPMSchedulerState, sample: jnp.ndarray, timestep: Optional[int]=None) -> jnp.ndarray:
        """Returns:"""
        return sample
    def set_timesteps(self, state: DDPMSchedulerState, num_inference_steps: int, shape: Tuple=()) -> DDPMSchedulerState:
        """Args:"""
        step_ratio = self.config.num_train_timesteps // num_inference_steps
        timesteps = (jnp.arange(0, num_inference_steps) * step_ratio).round()[::-1]
        return state.replace(num_inference_steps=num_inference_steps, timesteps=timesteps)
    def _get_variance(self, state: DDPMSchedulerState, t, predicted_variance=None, variance_type=None):
        alpha_prod_t = state.common.alphas_cumprod[t]
        alpha_prod_t_prev = jnp.where(t > 0, state.common.alphas_cumprod[t - 1], jnp.array(1.0, dtype=self.dtype))
        variance = (1 - alpha_prod_t_prev) / (1 - alpha_prod_t) * state.common.betas[t]
        if variance_type is None: variance_type = self.config.variance_type
        if variance_type == 'fixed_small': variance = jnp.clip(variance, a_min=1e-20)
        elif variance_type == 'fixed_small_log': variance = jnp.log(jnp.clip(variance, a_min=1e-20))
        elif variance_type == 'fixed_large': variance = state.common.betas[t]
        elif variance_type == 'fixed_large_log': variance = jnp.log(state.common.betas[t])
        elif variance_type == 'learned': return predicted_variance
        elif variance_type == 'learned_range':
            min_log = variance
            max_log = state.common.betas[t]
            frac = (predicted_variance + 1) / 2
            variance = frac * max_log + (1 - frac) * min_log
        return variance
    def step(self, state: DDPMSchedulerState, model_output: jnp.ndarray, timestep: int, sample: jnp.ndarray, key: Optional[jax.Array]=None,
    return_dict: bool=True) -> Union[FlaxDDPMSchedulerOutput, Tuple]:
        """Returns:"""
        t = timestep
        if key is None: key = jax.random.key(0)
        if len(model_output.shape) > 1 and model_output.shape[1] == sample.shape[1] * 2 and (self.config.variance_type in ['learned', 'learned_range']): model_output, predicted_variance = jnp.split(model_output, sample.shape[1], axis=1)
        else: predicted_variance = None
        alpha_prod_t = state.common.alphas_cumprod[t]
        alpha_prod_t_prev = jnp.where(t > 0, state.common.alphas_cumprod[t - 1], jnp.array(1.0, dtype=self.dtype))
        beta_prod_t = 1 - alpha_prod_t
        beta_prod_t_prev = 1 - alpha_prod_t_prev
        if self.config.prediction_type == 'epsilon': pred_original_sample = (sample - beta_prod_t ** 0.5 * model_output) / alpha_prod_t ** 0.5
        elif self.config.prediction_type == 'sample': pred_original_sample = model_output
        elif self.config.prediction_type == 'v_prediction': pred_original_sample = alpha_prod_t ** 0.5 * sample - beta_prod_t ** 0.5 * model_output
        else: raise ValueError(f'prediction_type given as {self.config.prediction_type} must be one of `epsilon`, `sample`  for the FlaxDDPMScheduler.')
        if self.config.clip_sample: pred_original_sample = jnp.clip(pred_original_sample, -1, 1)
        pred_original_sample_coeff = alpha_prod_t_prev ** 0.5 * state.common.betas[t] / beta_prod_t
        current_sample_coeff = state.common.alphas[t] ** 0.5 * beta_prod_t_prev / beta_prod_t
        pred_prev_sample = pred_original_sample_coeff * pred_original_sample + current_sample_coeff * sample
        def random_variance():
            split_key = jax.random.split(key, num=1)[0]
            noise = jax.random.normal(split_key, shape=model_output.shape, dtype=self.dtype)
            return self._get_variance(state, t, predicted_variance=predicted_variance) ** 0.5 * noise
        variance = jnp.where(t > 0, random_variance(), jnp.zeros(model_output.shape, dtype=self.dtype))
        pred_prev_sample = pred_prev_sample + variance
        if not return_dict: return (pred_prev_sample, state)
        return FlaxDDPMSchedulerOutput(prev_sample=pred_prev_sample, state=state)
    def add_noise(self, state: DDPMSchedulerState, original_samples: jnp.ndarray, noise: jnp.ndarray, timesteps: jnp.ndarray) -> jnp.ndarray: return add_noise_common(state.common, original_samples, noise, timesteps)
    def get_velocity(self, state: DDPMSchedulerState, sample: jnp.ndarray, noise: jnp.ndarray, timesteps: jnp.ndarray) -> jnp.ndarray: return get_velocity_common(state.common, sample, noise, timesteps)
    def __len__(self): return self.config.num_train_timesteps
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
