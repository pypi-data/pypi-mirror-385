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
class DDIMSchedulerOutput(BaseOutput):
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
def rescale_zero_terminal_snr(alphas_cumprod):
    """Returns:"""
    alphas_bar_sqrt = alphas_cumprod.sqrt()
    alphas_bar_sqrt_0 = alphas_bar_sqrt[0].clone()
    alphas_bar_sqrt_T = alphas_bar_sqrt[-1].clone()
    alphas_bar_sqrt -= alphas_bar_sqrt_T
    alphas_bar_sqrt *= alphas_bar_sqrt_0 / (alphas_bar_sqrt_0 - alphas_bar_sqrt_T)
    alphas_bar = alphas_bar_sqrt ** 2
    return alphas_bar
class CogVideoXDPMScheduler(SchedulerMixin, ConfigMixin):
    """Args:"""
    _compatibles = [e.name for e in KarrasDiffusionSchedulers]
    order = 1
    @register_to_config
    def __init__(self, num_train_timesteps: int=1000, beta_start: float=0.00085, beta_end: float=0.012, beta_schedule: str='scaled_linear', trained_betas: Optional[Union[np.ndarray,
    List[float]]]=None, clip_sample: bool=True, set_alpha_to_one: bool=True, steps_offset: int=0, prediction_type: str='epsilon', clip_sample_range: float=1.0,
    sample_max_value: float=1.0, timestep_spacing: str='leading', rescale_betas_zero_snr: bool=False, snr_shift_scale: float=3.0):
        if trained_betas is not None: self.betas = torch.tensor(trained_betas, dtype=torch.float32)
        elif beta_schedule == 'linear': self.betas = torch.linspace(beta_start, beta_end, num_train_timesteps, dtype=torch.float32)
        elif beta_schedule == 'scaled_linear': self.betas = torch.linspace(beta_start ** 0.5, beta_end ** 0.5, num_train_timesteps, dtype=torch.float64) ** 2
        elif beta_schedule == 'squaredcos_cap_v2': self.betas = betas_for_alpha_bar(num_train_timesteps)
        else: raise NotImplementedError(f'{beta_schedule} is not implemented for {self.__class__}')
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)
        self.alphas_cumprod = self.alphas_cumprod / (snr_shift_scale + (1 - snr_shift_scale) * self.alphas_cumprod)
        if rescale_betas_zero_snr: self.alphas_cumprod = rescale_zero_terminal_snr(self.alphas_cumprod)
        self.final_alpha_cumprod = torch.tensor(1.0) if set_alpha_to_one else self.alphas_cumprod[0]
        self.init_noise_sigma = 1.0
        self.num_inference_steps = None
        self.timesteps = torch.from_numpy(np.arange(0, num_train_timesteps)[::-1].copy().astype(np.int64))
    def _get_variance(self, timestep, prev_timestep):
        alpha_prod_t = self.alphas_cumprod[timestep]
        alpha_prod_t_prev = self.alphas_cumprod[prev_timestep] if prev_timestep >= 0 else self.final_alpha_cumprod
        beta_prod_t = 1 - alpha_prod_t
        beta_prod_t_prev = 1 - alpha_prod_t_prev
        variance = beta_prod_t_prev / beta_prod_t * (1 - alpha_prod_t / alpha_prod_t_prev)
        return variance
    def scale_model_input(self, sample: torch.Tensor, timestep: Optional[int]=None) -> torch.Tensor:
        """Returns:"""
        return sample
    def set_timesteps(self, num_inference_steps: int, device: Union[str, torch.device]=None):
        """Args:"""
        if num_inference_steps > self.config.num_train_timesteps: raise ValueError(f'`num_inference_steps`: {num_inference_steps} cannot be larger than `self.config.train_timesteps`: {self.config.num_train_timesteps} as the unet model trained with this scheduler can only handle maximal {self.config.num_train_timesteps} timesteps.')
        self.num_inference_steps = num_inference_steps
        if self.config.timestep_spacing == 'linspace': timesteps = np.linspace(0, self.config.num_train_timesteps - 1, num_inference_steps).round()[::-1].copy().astype(np.int64)
        elif self.config.timestep_spacing == 'leading':
            step_ratio = self.config.num_train_timesteps // self.num_inference_steps
            timesteps = (np.arange(0, num_inference_steps) * step_ratio).round()[::-1].copy().astype(np.int64)
            timesteps += self.config.steps_offset
        elif self.config.timestep_spacing == 'trailing':
            step_ratio = self.config.num_train_timesteps / self.num_inference_steps
            timesteps = np.round(np.arange(self.config.num_train_timesteps, 0, -step_ratio)).astype(np.int64)
            timesteps -= 1
        else: raise ValueError(f"{self.config.timestep_spacing} is not supported. Please make sure to choose one of 'leading' or 'trailing'.")
        self.timesteps = torch.from_numpy(timesteps).to(device)
    def get_variables(self, alpha_prod_t, alpha_prod_t_prev, alpha_prod_t_back=None):
        lamb = ((alpha_prod_t / (1 - alpha_prod_t)) ** 0.5).log()
        lamb_next = ((alpha_prod_t_prev / (1 - alpha_prod_t_prev)) ** 0.5).log()
        h = lamb_next - lamb
        if alpha_prod_t_back is not None:
            lamb_previous = ((alpha_prod_t_back / (1 - alpha_prod_t_back)) ** 0.5).log()
            h_last = lamb - lamb_previous
            r = h_last / h
            return (h, r, lamb, lamb_next)
        else: return (h, None, lamb, lamb_next)
    def get_mult(self, h, r, alpha_prod_t, alpha_prod_t_prev, alpha_prod_t_back):
        mult1 = ((1 - alpha_prod_t_prev) / (1 - alpha_prod_t)) ** 0.5 * (-h).exp()
        mult2 = (-2 * h).expm1() * alpha_prod_t_prev ** 0.5
        if alpha_prod_t_back is not None:
            mult3 = 1 + 1 / (2 * r)
            mult4 = 1 / (2 * r)
            return (mult1, mult2, mult3, mult4)
        else: return (mult1, mult2)
    def step(self, model_output: torch.Tensor, old_pred_original_sample: torch.Tensor, timestep: int, timestep_back: int, sample: torch.Tensor, eta: float=0.0, use_clipped_model_output: bool=False,
    generator=None, variance_noise: Optional[torch.Tensor]=None, return_dict: bool=False) -> Union[DDIMSchedulerOutput, Tuple]:
        """Returns:"""
        if self.num_inference_steps is None: raise ValueError("Number of inference steps is 'None', you need to run 'set_timesteps' after creating the scheduler")
        prev_timestep = timestep - self.config.num_train_timesteps // self.num_inference_steps
        alpha_prod_t = self.alphas_cumprod[timestep]
        alpha_prod_t_prev = self.alphas_cumprod[prev_timestep] if prev_timestep >= 0 else self.final_alpha_cumprod
        alpha_prod_t_back = self.alphas_cumprod[timestep_back] if timestep_back is not None else None
        beta_prod_t = 1 - alpha_prod_t
        if self.config.prediction_type == 'epsilon': pred_original_sample = (sample - beta_prod_t ** 0.5 * model_output) / alpha_prod_t ** 0.5
        elif self.config.prediction_type == 'sample': pred_original_sample = model_output
        elif self.config.prediction_type == 'v_prediction': pred_original_sample = alpha_prod_t ** 0.5 * sample - beta_prod_t ** 0.5 * model_output
        else: raise ValueError(f'prediction_type given as {self.config.prediction_type} must be one of `epsilon`, `sample`, or `v_prediction`')
        h, r, lamb, lamb_next = self.get_variables(alpha_prod_t, alpha_prod_t_prev, alpha_prod_t_back)
        mult = list(self.get_mult(h, r, alpha_prod_t, alpha_prod_t_prev, alpha_prod_t_back))
        mult_noise = (1 - alpha_prod_t_prev) ** 0.5 * (1 - (-2 * h).exp()) ** 0.5
        noise = randn_tensor(sample.shape, generator=generator, device=sample.device, dtype=sample.dtype)
        prev_sample = mult[0] * sample - mult[1] * pred_original_sample + mult_noise * noise
        if old_pred_original_sample is None or prev_timestep < 0: return (prev_sample, pred_original_sample)
        else:
            denoised_d = mult[2] * pred_original_sample - mult[3] * old_pred_original_sample
            noise = randn_tensor(sample.shape, generator=generator, device=sample.device, dtype=sample.dtype)
            x_advanced = mult[0] * sample - mult[1] * denoised_d + mult_noise * noise
            prev_sample = x_advanced
        if not return_dict: return (prev_sample, pred_original_sample)
        return DDIMSchedulerOutput(prev_sample=prev_sample, pred_original_sample=pred_original_sample)
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
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
