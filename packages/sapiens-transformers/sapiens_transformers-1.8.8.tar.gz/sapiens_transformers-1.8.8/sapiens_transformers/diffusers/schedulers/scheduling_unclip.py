'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import math
from dataclasses import dataclass
from typing import Optional, Tuple, Union
import numpy as np
import torch
from ..configuration_utils import ConfigMixin, register_to_config
from ..utils import BaseOutput
from ..utils.torch_utils import randn_tensor
from .scheduling_utils import SchedulerMixin
@dataclass
class UnCLIPSchedulerOutput(BaseOutput):
    """Args:"""
    prev_sample: torch.Tensor
    pred_original_sample: Optional[torch.Tensor] = None
def betas_for_alpha_bar(num_diffusion_timesteps, max_beta=0.999, alpha_transform_type='cosine'):
    """Returns:"""
    if alpha_transform_type == 'cosine':
        def alpha_bar_fn(t): return math.cos((t + 0.008) / 1.008 * math.pi / 2) ** 2
    elif alpha_transform_type == 'exp':
        def alpha_bar_fn(t): return math.exp(t * -12.0)
    else: raise ValueError(f'Unsupported alpha_transform_type: {alpha_transform_type}')
    betas = []
    for i in range(num_diffusion_timesteps):
        t1 = i / num_diffusion_timesteps
        t2 = (i + 1) / num_diffusion_timesteps
        betas.append(min(1 - alpha_bar_fn(t2) / alpha_bar_fn(t1), max_beta))
    return torch.tensor(betas, dtype=torch.float32)
class UnCLIPScheduler(SchedulerMixin, ConfigMixin):
    """Args:"""
    @register_to_config
    def __init__(self, num_train_timesteps: int=1000, variance_type: str='fixed_small_log', clip_sample: bool=True, clip_sample_range: Optional[float]=1.0, prediction_type: str='epsilon',
    beta_schedule: str='squaredcos_cap_v2'):
        if beta_schedule != 'squaredcos_cap_v2': raise ValueError("UnCLIPScheduler only supports `beta_schedule`: 'squaredcos_cap_v2'")
        self.betas = betas_for_alpha_bar(num_train_timesteps)
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)
        self.one = torch.tensor(1.0)
        self.init_noise_sigma = 1.0
        self.num_inference_steps = None
        self.timesteps = torch.from_numpy(np.arange(0, num_train_timesteps)[::-1].copy())
        self.variance_type = variance_type
    def scale_model_input(self, sample: torch.Tensor, timestep: Optional[int]=None) -> torch.Tensor:
        """Returns:"""
        return sample
    def set_timesteps(self, num_inference_steps: int, device: Union[str, torch.device]=None):
        """Args:"""
        self.num_inference_steps = num_inference_steps
        step_ratio = (self.config.num_train_timesteps - 1) / (self.num_inference_steps - 1)
        timesteps = (np.arange(0, num_inference_steps) * step_ratio).round()[::-1].copy().astype(np.int64)
        self.timesteps = torch.from_numpy(timesteps).to(device)
    def _get_variance(self, t, prev_timestep=None, predicted_variance=None, variance_type=None):
        if prev_timestep is None: prev_timestep = t - 1
        alpha_prod_t = self.alphas_cumprod[t]
        alpha_prod_t_prev = self.alphas_cumprod[prev_timestep] if prev_timestep >= 0 else self.one
        beta_prod_t = 1 - alpha_prod_t
        beta_prod_t_prev = 1 - alpha_prod_t_prev
        if prev_timestep == t - 1: beta = self.betas[t]
        else: beta = 1 - alpha_prod_t / alpha_prod_t_prev
        variance = beta_prod_t_prev / beta_prod_t * beta
        if variance_type is None: variance_type = self.config.variance_type
        if variance_type == 'fixed_small_log':
            variance = torch.log(torch.clamp(variance, min=1e-20))
            variance = torch.exp(0.5 * variance)
        elif variance_type == 'learned_range':
            min_log = variance.log()
            max_log = beta.log()
            frac = (predicted_variance + 1) / 2
            variance = frac * max_log + (1 - frac) * min_log
        return variance
    def step(self, model_output: torch.Tensor, timestep: int, sample: torch.Tensor, prev_timestep: Optional[int]=None, generator=None,
    return_dict: bool=True) -> Union[UnCLIPSchedulerOutput, Tuple]:
        """Returns:"""
        t = timestep
        if model_output.shape[1] == sample.shape[1] * 2 and self.variance_type == 'learned_range': model_output, predicted_variance = torch.split(model_output, sample.shape[1], dim=1)
        else: predicted_variance = None
        if prev_timestep is None: prev_timestep = t - 1
        alpha_prod_t = self.alphas_cumprod[t]
        alpha_prod_t_prev = self.alphas_cumprod[prev_timestep] if prev_timestep >= 0 else self.one
        beta_prod_t = 1 - alpha_prod_t
        beta_prod_t_prev = 1 - alpha_prod_t_prev
        if prev_timestep == t - 1:
            beta = self.betas[t]
            alpha = self.alphas[t]
        else:
            beta = 1 - alpha_prod_t / alpha_prod_t_prev
            alpha = 1 - beta
        if self.config.prediction_type == 'epsilon': pred_original_sample = (sample - beta_prod_t ** 0.5 * model_output) / alpha_prod_t ** 0.5
        elif self.config.prediction_type == 'sample': pred_original_sample = model_output
        else: raise ValueError(f'prediction_type given as {self.config.prediction_type} must be one of `epsilon` or `sample` for the UnCLIPScheduler.')
        if self.config.clip_sample: pred_original_sample = torch.clamp(pred_original_sample, -self.config.clip_sample_range, self.config.clip_sample_range)
        pred_original_sample_coeff = alpha_prod_t_prev ** 0.5 * beta / beta_prod_t
        current_sample_coeff = alpha ** 0.5 * beta_prod_t_prev / beta_prod_t
        pred_prev_sample = pred_original_sample_coeff * pred_original_sample + current_sample_coeff * sample
        variance = 0
        if t > 0:
            variance_noise = randn_tensor(model_output.shape, dtype=model_output.dtype, generator=generator, device=model_output.device)
            variance = self._get_variance(t, predicted_variance=predicted_variance, prev_timestep=prev_timestep)
            if self.variance_type == 'fixed_small_log': variance = variance
            elif self.variance_type == 'learned_range': variance = (0.5 * variance).exp()
            else: raise ValueError(f'variance_type given as {self.variance_type} must be one of `fixed_small_log` or `learned_range` for the UnCLIPScheduler.')
            variance = variance * variance_noise
        pred_prev_sample = pred_prev_sample + variance
        if not return_dict: return (pred_prev_sample, pred_original_sample)
        return UnCLIPSchedulerOutput(prev_sample=pred_prev_sample, pred_original_sample=pred_original_sample)
    def add_noise(self, original_samples: torch.Tensor, noise: torch.Tensor, timesteps: torch.IntTensor) -> torch.Tensor:
        self.alphas_cumprod = self.alphas_cumprod.to(device=original_samples.device)
        alphas_cumprod = self.alphas_cumprod.to(dtype=original_samples.dtype)
        timesteps = timesteps.to(original_samples.device)
        sqrt_alpha_prod = alphas_cumprod[timesteps] ** 0.5
        sqrt_alpha_prod = sqrt_alpha_prod.flatten()
        while len(sqrt_alpha_prod.shape) < len(original_samples.shape): sqrt_alpha_prod = sqrt_alpha_prod.unsqueeze(-1)
        sqrt_one_minus_alpha_prod = (1 - alphas_cumprod[timesteps]) ** 0.5
        sqrt_one_minus_alpha_prod = sqrt_one_minus_alpha_prod.flatten()
        while len(sqrt_one_minus_alpha_prod.shape) < len(original_samples.shape): sqrt_one_minus_alpha_prod = sqrt_one_minus_alpha_prod.unsqueeze(-1)
        noisy_samples = sqrt_alpha_prod * original_samples + sqrt_one_minus_alpha_prod * noise
        return noisy_samples
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
