'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union
import numpy as np
import torch
from ..configuration_utils import ConfigMixin, register_to_config
from ..utils import BaseOutput
from ..utils.torch_utils import randn_tensor
from .scheduling_utils import KarrasDiffusionSchedulers, SchedulerMixin
@dataclass
class DDPMSchedulerOutput(BaseOutput):
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
def rescale_zero_terminal_snr(betas):
    """Returns:"""
    alphas = 1.0 - betas
    alphas_cumprod = torch.cumprod(alphas, dim=0)
    alphas_bar_sqrt = alphas_cumprod.sqrt()
    alphas_bar_sqrt_0 = alphas_bar_sqrt[0].clone()
    alphas_bar_sqrt_T = alphas_bar_sqrt[-1].clone()
    alphas_bar_sqrt -= alphas_bar_sqrt_T
    alphas_bar_sqrt *= alphas_bar_sqrt_0 / (alphas_bar_sqrt_0 - alphas_bar_sqrt_T)
    alphas_bar = alphas_bar_sqrt ** 2
    alphas = alphas_bar[1:] / alphas_bar[:-1]
    alphas = torch.cat([alphas_bar[0:1], alphas])
    betas = 1 - alphas
    return betas
class DDPMScheduler(SchedulerMixin, ConfigMixin):
    """Args:"""
    _compatibles = [e.name for e in KarrasDiffusionSchedulers]
    order = 1
    @register_to_config
    def __init__(self, num_train_timesteps: int=1000, beta_start: float=0.0001, beta_end: float=0.02, beta_schedule: str='linear', trained_betas: Optional[Union[np.ndarray, List[float]]]=None,
    variance_type: str='fixed_small', clip_sample: bool=True, prediction_type: str='epsilon', thresholding: bool=False, dynamic_thresholding_ratio: float=0.995, clip_sample_range: float=1.0,
    sample_max_value: float=1.0, timestep_spacing: str='leading', steps_offset: int=0, rescale_betas_zero_snr: bool=False):
        if trained_betas is not None: self.betas = torch.tensor(trained_betas, dtype=torch.float32)
        elif beta_schedule == 'linear': self.betas = torch.linspace(beta_start, beta_end, num_train_timesteps, dtype=torch.float32)
        elif beta_schedule == 'scaled_linear': self.betas = torch.linspace(beta_start ** 0.5, beta_end ** 0.5, num_train_timesteps, dtype=torch.float32) ** 2
        elif beta_schedule == 'squaredcos_cap_v2': self.betas = betas_for_alpha_bar(num_train_timesteps)
        elif beta_schedule == 'sigmoid':
            betas = torch.linspace(-6, 6, num_train_timesteps)
            self.betas = torch.sigmoid(betas) * (beta_end - beta_start) + beta_start
        else: raise NotImplementedError(f'{beta_schedule} is not implemented for {self.__class__}')
        if rescale_betas_zero_snr: self.betas = rescale_zero_terminal_snr(self.betas)
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)
        self.one = torch.tensor(1.0)
        self.init_noise_sigma = 1.0
        self.custom_timesteps = False
        self.num_inference_steps = None
        self.timesteps = torch.from_numpy(np.arange(0, num_train_timesteps)[::-1].copy())
        self.variance_type = variance_type
    def scale_model_input(self, sample: torch.Tensor, timestep: Optional[int]=None) -> torch.Tensor:
        """Returns:"""
        return sample
    def set_timesteps(self, num_inference_steps: Optional[int]=None, device: Union[str, torch.device]=None, timesteps: Optional[List[int]]=None):
        """Args:"""
        if num_inference_steps is not None and timesteps is not None: raise ValueError('Can only pass one of `num_inference_steps` or `custom_timesteps`.')
        if timesteps is not None:
            for i in range(1, len(timesteps)):
                if timesteps[i] >= timesteps[i - 1]: raise ValueError('`custom_timesteps` must be in descending order.')
            if timesteps[0] >= self.config.num_train_timesteps: raise ValueError(f'`timesteps` must start before `self.config.train_timesteps`: {self.config.num_train_timesteps}.')
            timesteps = np.array(timesteps, dtype=np.int64)
            self.custom_timesteps = True
        else:
            if num_inference_steps > self.config.num_train_timesteps: raise ValueError(f'`num_inference_steps`: {num_inference_steps} cannot be larger than `self.config.train_timesteps`: {self.config.num_train_timesteps} as the unet model trained with this scheduler can only handle maximal {self.config.num_train_timesteps} timesteps.')
            self.num_inference_steps = num_inference_steps
            self.custom_timesteps = False
            if self.config.timestep_spacing == 'linspace': timesteps = np.linspace(0, self.config.num_train_timesteps - 1, num_inference_steps).round()[::-1].copy().astype(np.int64)
            elif self.config.timestep_spacing == 'leading':
                step_ratio = self.config.num_train_timesteps // self.num_inference_steps
                timesteps = (np.arange(0, num_inference_steps) * step_ratio).round()[::-1].copy().astype(np.int64)
                timesteps += self.config.steps_offset
            elif self.config.timestep_spacing == 'trailing':
                step_ratio = self.config.num_train_timesteps / self.num_inference_steps
                timesteps = np.round(np.arange(self.config.num_train_timesteps, 0, -step_ratio)).astype(np.int64)
                timesteps -= 1
            else: raise ValueError(f"{self.config.timestep_spacing} is not supported. Please make sure to choose one of 'linspace', 'leading' or 'trailing'.")
        self.timesteps = torch.from_numpy(timesteps).to(device)
    def _get_variance(self, t, predicted_variance=None, variance_type=None):
        prev_t = self.previous_timestep(t)
        alpha_prod_t = self.alphas_cumprod[t]
        alpha_prod_t_prev = self.alphas_cumprod[prev_t] if prev_t >= 0 else self.one
        current_beta_t = 1 - alpha_prod_t / alpha_prod_t_prev
        variance = (1 - alpha_prod_t_prev) / (1 - alpha_prod_t) * current_beta_t
        variance = torch.clamp(variance, min=1e-20)
        if variance_type is None: variance_type = self.config.variance_type
        if variance_type == 'fixed_small': variance = variance
        elif variance_type == 'fixed_small_log':
            variance = torch.log(variance)
            variance = torch.exp(0.5 * variance)
        elif variance_type == 'fixed_large': variance = current_beta_t
        elif variance_type == 'fixed_large_log': variance = torch.log(current_beta_t)
        elif variance_type == 'learned': return predicted_variance
        elif variance_type == 'learned_range':
            min_log = torch.log(variance)
            max_log = torch.log(current_beta_t)
            frac = (predicted_variance + 1) / 2
            variance = frac * max_log + (1 - frac) * min_log
        return variance
    def _threshold_sample(self, sample: torch.Tensor) -> torch.Tensor:
        dtype = sample.dtype
        batch_size, channels, *remaining_dims = sample.shape
        if dtype not in (torch.float32, torch.float64): sample = sample.float()
        sample = sample.reshape(batch_size, channels * np.prod(remaining_dims))
        abs_sample = sample.abs()
        s = torch.quantile(abs_sample, self.config.dynamic_thresholding_ratio, dim=1)
        s = torch.clamp(s, min=1, max=self.config.sample_max_value)
        s = s.unsqueeze(1)
        sample = torch.clamp(sample, -s, s) / s
        sample = sample.reshape(batch_size, channels, *remaining_dims)
        sample = sample.to(dtype)
        return sample
    def step(self, model_output: torch.Tensor, timestep: int, sample: torch.Tensor, generator=None, return_dict: bool=True) -> Union[DDPMSchedulerOutput, Tuple]:
        """Returns:"""
        t = timestep
        prev_t = self.previous_timestep(t)
        if model_output.shape[1] == sample.shape[1] * 2 and self.variance_type in ['learned', 'learned_range']: model_output, predicted_variance = torch.split(model_output, sample.shape[1], dim=1)
        else: predicted_variance = None
        alpha_prod_t = self.alphas_cumprod[t]
        alpha_prod_t_prev = self.alphas_cumprod[prev_t] if prev_t >= 0 else self.one
        beta_prod_t = 1 - alpha_prod_t
        beta_prod_t_prev = 1 - alpha_prod_t_prev
        current_alpha_t = alpha_prod_t / alpha_prod_t_prev
        current_beta_t = 1 - current_alpha_t
        if self.config.prediction_type == 'epsilon': pred_original_sample = (sample - beta_prod_t ** 0.5 * model_output) / alpha_prod_t ** 0.5
        elif self.config.prediction_type == 'sample': pred_original_sample = model_output
        elif self.config.prediction_type == 'v_prediction': pred_original_sample = alpha_prod_t ** 0.5 * sample - beta_prod_t ** 0.5 * model_output
        else: raise ValueError(f'prediction_type given as {self.config.prediction_type} must be one of `epsilon`, `sample` or `v_prediction`  for the DDPMScheduler.')
        if self.config.thresholding: pred_original_sample = self._threshold_sample(pred_original_sample)
        elif self.config.clip_sample: pred_original_sample = pred_original_sample.clamp(-self.config.clip_sample_range, self.config.clip_sample_range)
        pred_original_sample_coeff = alpha_prod_t_prev ** 0.5 * current_beta_t / beta_prod_t
        current_sample_coeff = current_alpha_t ** 0.5 * beta_prod_t_prev / beta_prod_t
        pred_prev_sample = pred_original_sample_coeff * pred_original_sample + current_sample_coeff * sample
        variance = 0
        if t > 0:
            device = model_output.device
            variance_noise = randn_tensor(model_output.shape, generator=generator, device=device, dtype=model_output.dtype)
            if self.variance_type == 'fixed_small_log': variance = self._get_variance(t, predicted_variance=predicted_variance) * variance_noise
            elif self.variance_type == 'learned_range':
                variance = self._get_variance(t, predicted_variance=predicted_variance)
                variance = torch.exp(0.5 * variance) * variance_noise
            else: variance = self._get_variance(t, predicted_variance=predicted_variance) ** 0.5 * variance_noise
        pred_prev_sample = pred_prev_sample + variance
        if not return_dict: return (pred_prev_sample, pred_original_sample)
        return DDPMSchedulerOutput(prev_sample=pred_prev_sample, pred_original_sample=pred_original_sample)
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
    def get_velocity(self, sample: torch.Tensor, noise: torch.Tensor, timesteps: torch.IntTensor) -> torch.Tensor:
        self.alphas_cumprod = self.alphas_cumprod.to(device=sample.device)
        alphas_cumprod = self.alphas_cumprod.to(dtype=sample.dtype)
        timesteps = timesteps.to(sample.device)
        sqrt_alpha_prod = alphas_cumprod[timesteps] ** 0.5
        sqrt_alpha_prod = sqrt_alpha_prod.flatten()
        while len(sqrt_alpha_prod.shape) < len(sample.shape): sqrt_alpha_prod = sqrt_alpha_prod.unsqueeze(-1)
        sqrt_one_minus_alpha_prod = (1 - alphas_cumprod[timesteps]) ** 0.5
        sqrt_one_minus_alpha_prod = sqrt_one_minus_alpha_prod.flatten()
        while len(sqrt_one_minus_alpha_prod.shape) < len(sample.shape): sqrt_one_minus_alpha_prod = sqrt_one_minus_alpha_prod.unsqueeze(-1)
        velocity = sqrt_alpha_prod * noise - sqrt_one_minus_alpha_prod * sample
        return velocity
    def __len__(self): return self.config.num_train_timesteps
    def previous_timestep(self, timestep):
        if self.custom_timesteps or self.num_inference_steps:
            index = (self.timesteps == timestep).nonzero(as_tuple=True)[0][0]
            if index == self.timesteps.shape[0] - 1: prev_t = torch.tensor(-1)
            else: prev_t = self.timesteps[index + 1]
        else: prev_t = timestep - 1
        return prev_t
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
