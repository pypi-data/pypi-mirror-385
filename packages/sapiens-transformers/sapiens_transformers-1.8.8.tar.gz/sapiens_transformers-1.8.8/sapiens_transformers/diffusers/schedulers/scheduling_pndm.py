'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import math
from typing import List, Optional, Tuple, Union
import numpy as np
import torch
from ..configuration_utils import ConfigMixin, register_to_config
from .scheduling_utils import KarrasDiffusionSchedulers, SchedulerMixin, SchedulerOutput
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
class PNDMScheduler(SchedulerMixin, ConfigMixin):
    """Args:"""
    _compatibles = [e.name for e in KarrasDiffusionSchedulers]
    order = 1
    @register_to_config
    def __init__(self, num_train_timesteps: int=1000, beta_start: float=0.0001, beta_end: float=0.02, beta_schedule: str='linear', trained_betas: Optional[Union[np.ndarray, List[float]]]=None,
    skip_prk_steps: bool=False, set_alpha_to_one: bool=False, prediction_type: str='epsilon', timestep_spacing: str='leading', steps_offset: int=0):
        if trained_betas is not None: self.betas = torch.tensor(trained_betas, dtype=torch.float32)
        elif beta_schedule == 'linear': self.betas = torch.linspace(beta_start, beta_end, num_train_timesteps, dtype=torch.float32)
        elif beta_schedule == 'scaled_linear': self.betas = torch.linspace(beta_start ** 0.5, beta_end ** 0.5, num_train_timesteps, dtype=torch.float32) ** 2
        elif beta_schedule == 'squaredcos_cap_v2': self.betas = betas_for_alpha_bar(num_train_timesteps)
        else: raise NotImplementedError(f'{beta_schedule} is not implemented for {self.__class__}')
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)
        self.final_alpha_cumprod = torch.tensor(1.0) if set_alpha_to_one else self.alphas_cumprod[0]
        self.init_noise_sigma = 1.0
        self.pndm_order = 4
        self.cur_model_output = 0
        self.counter = 0
        self.cur_sample = None
        self.ets = []
        self.num_inference_steps = None
        self._timesteps = np.arange(0, num_train_timesteps)[::-1].copy()
        self.prk_timesteps = None
        self.plms_timesteps = None
        self.timesteps = None
    def set_timesteps(self, num_inference_steps: int, device: Union[str, torch.device]=None):
        """Args:"""
        self.num_inference_steps = num_inference_steps
        if self.config.timestep_spacing == 'linspace': self._timesteps = np.linspace(0, self.config.num_train_timesteps - 1, num_inference_steps).round().astype(np.int64)
        elif self.config.timestep_spacing == 'leading':
            step_ratio = self.config.num_train_timesteps // self.num_inference_steps
            self._timesteps = (np.arange(0, num_inference_steps) * step_ratio).round()
            self._timesteps += self.config.steps_offset
        elif self.config.timestep_spacing == 'trailing':
            step_ratio = self.config.num_train_timesteps / self.num_inference_steps
            self._timesteps = np.round(np.arange(self.config.num_train_timesteps, 0, -step_ratio))[::-1].astype(np.int64)
            self._timesteps -= 1
        else: raise ValueError(f"{self.config.timestep_spacing} is not supported. Please make sure to choose one of 'linspace', 'leading' or 'trailing'.")
        if self.config.skip_prk_steps:
            self.prk_timesteps = np.array([])
            self.plms_timesteps = np.concatenate([self._timesteps[:-1], self._timesteps[-2:-1], self._timesteps[-1:]])[::-1].copy()
        else:
            prk_timesteps = np.array(self._timesteps[-self.pndm_order:]).repeat(2) + np.tile(np.array([0, self.config.num_train_timesteps // num_inference_steps // 2]), self.pndm_order)
            self.prk_timesteps = prk_timesteps[:-1].repeat(2)[1:-1][::-1].copy()
            self.plms_timesteps = self._timesteps[:-3][::-1].copy()
        timesteps = np.concatenate([self.prk_timesteps, self.plms_timesteps]).astype(np.int64)
        self.timesteps = torch.from_numpy(timesteps).to(device)
        self.ets = []
        self.counter = 0
        self.cur_model_output = 0
    def step(self, model_output: torch.Tensor, timestep: int, sample: torch.Tensor, return_dict: bool=True) -> Union[SchedulerOutput, Tuple]:
        """Returns:"""
        if self.counter < len(self.prk_timesteps) and (not self.config.skip_prk_steps): return self.step_prk(model_output=model_output, timestep=timestep, sample=sample, return_dict=return_dict)
        else: return self.step_plms(model_output=model_output, timestep=timestep, sample=sample, return_dict=return_dict)
    def step_prk(self, model_output: torch.Tensor, timestep: int, sample: torch.Tensor, return_dict: bool=True) -> Union[SchedulerOutput, Tuple]:
        """Returns:"""
        if self.num_inference_steps is None: raise ValueError("Number of inference steps is 'None', you need to run 'set_timesteps' after creating the scheduler")
        diff_to_prev = 0 if self.counter % 2 else self.config.num_train_timesteps // self.num_inference_steps // 2
        prev_timestep = timestep - diff_to_prev
        timestep = self.prk_timesteps[self.counter // 4 * 4]
        if self.counter % 4 == 0:
            self.cur_model_output += 1 / 6 * model_output
            self.ets.append(model_output)
            self.cur_sample = sample
        elif (self.counter - 1) % 4 == 0: self.cur_model_output += 1 / 3 * model_output
        elif (self.counter - 2) % 4 == 0: self.cur_model_output += 1 / 3 * model_output
        elif (self.counter - 3) % 4 == 0:
            model_output = self.cur_model_output + 1 / 6 * model_output
            self.cur_model_output = 0
        cur_sample = self.cur_sample if self.cur_sample is not None else sample
        prev_sample = self._get_prev_sample(cur_sample, timestep, prev_timestep, model_output)
        self.counter += 1
        if not return_dict: return (prev_sample,)
        return SchedulerOutput(prev_sample=prev_sample)
    def step_plms(self, model_output: torch.Tensor, timestep: int, sample: torch.Tensor, return_dict: bool=True) -> Union[SchedulerOutput, Tuple]:
        """Returns:"""
        if self.num_inference_steps is None: raise ValueError("Number of inference steps is 'None', you need to run 'set_timesteps' after creating the scheduler")
        if not self.config.skip_prk_steps and len(self.ets) < 3:
            raise ValueError(f"{self.__class__} can only be run AFTER scheduler has been run in 'prk' mode for at least 12 iterations See: https://github.com/huggingface/diffusers/blob/main/src/diffusers/pipelines/pipeline_pndm.py for more information.")
        prev_timestep = timestep - self.config.num_train_timesteps // self.num_inference_steps
        if self.counter != 1:
            self.ets = self.ets[-3:]
            self.ets.append(model_output)
        else:
            prev_timestep = timestep
            timestep = timestep + self.config.num_train_timesteps // self.num_inference_steps
        if len(self.ets) == 1 and self.counter == 0:
            model_output = model_output
            self.cur_sample = sample
        elif len(self.ets) == 1 and self.counter == 1:
            model_output = (model_output + self.ets[-1]) / 2
            sample = self.cur_sample
            self.cur_sample = None
        elif len(self.ets) == 2: model_output = (3 * self.ets[-1] - self.ets[-2]) / 2
        elif len(self.ets) == 3: model_output = (23 * self.ets[-1] - 16 * self.ets[-2] + 5 * self.ets[-3]) / 12
        else: model_output = 1 / 24 * (55 * self.ets[-1] - 59 * self.ets[-2] + 37 * self.ets[-3] - 9 * self.ets[-4])
        prev_sample = self._get_prev_sample(sample, timestep, prev_timestep, model_output)
        self.counter += 1
        if not return_dict: return (prev_sample,)
        return SchedulerOutput(prev_sample=prev_sample)
    def scale_model_input(self, sample: torch.Tensor, *args, **kwargs) -> torch.Tensor:
        """Returns:"""
        return sample
    def _get_prev_sample(self, sample, timestep, prev_timestep, model_output):
        alpha_prod_t = self.alphas_cumprod[timestep]
        alpha_prod_t_prev = self.alphas_cumprod[prev_timestep] if prev_timestep >= 0 else self.final_alpha_cumprod
        beta_prod_t = 1 - alpha_prod_t
        beta_prod_t_prev = 1 - alpha_prod_t_prev
        if self.config.prediction_type == 'v_prediction': model_output = alpha_prod_t ** 0.5 * model_output + beta_prod_t ** 0.5 * sample
        elif self.config.prediction_type != 'epsilon': raise ValueError(f'prediction_type given as {self.config.prediction_type} must be one of `epsilon` or `v_prediction`')
        sample_coeff = (alpha_prod_t_prev / alpha_prod_t) ** 0.5
        model_output_denom_coeff = alpha_prod_t * beta_prod_t_prev ** 0.5 + (alpha_prod_t * beta_prod_t * alpha_prod_t_prev) ** 0.5
        prev_sample = sample_coeff * sample - (alpha_prod_t_prev - alpha_prod_t) * model_output / model_output_denom_coeff
        return prev_sample
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
    def __len__(self): return self.config.num_train_timesteps
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
