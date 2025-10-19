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
from ..utils import deprecate, is_scipy_available
from ..utils.torch_utils import randn_tensor
from .scheduling_utils import KarrasDiffusionSchedulers, SchedulerMixin, SchedulerOutput
if is_scipy_available(): import scipy.stats
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
class DPMSolverSinglestepScheduler(SchedulerMixin, ConfigMixin):
    """Args:"""
    _compatibles = [e.name for e in KarrasDiffusionSchedulers]
    order = 1
    @register_to_config
    def __init__(self, num_train_timesteps: int=1000, beta_start: float=0.0001, beta_end: float=0.02, beta_schedule: str='linear', trained_betas: Optional[np.ndarray]=None, solver_order: int=2,
    prediction_type: str='epsilon', thresholding: bool=False, dynamic_thresholding_ratio: float=0.995, sample_max_value: float=1.0, algorithm_type: str='dpmsolver++', solver_type: str='midpoint',
    lower_order_final: bool=False, use_karras_sigmas: Optional[bool]=False, use_exponential_sigmas: Optional[bool]=False, use_beta_sigmas: Optional[bool]=False,
    use_flow_sigmas: Optional[bool]=False, flow_shift: Optional[float]=1.0, final_sigmas_type: Optional[str]='zero', lambda_min_clipped: float=-float('inf'), variance_type: Optional[str]=None):
        if self.config.use_beta_sigmas and (not is_scipy_available()): raise ImportError('Make sure to install scipy if you want to use beta sigmas.')
        if sum([self.config.use_beta_sigmas, self.config.use_exponential_sigmas, self.config.use_karras_sigmas]) > 1: raise ValueError('Only one of `config.use_beta_sigmas`, `config.use_exponential_sigmas`, `config.use_karras_sigmas` can be used.')
        if algorithm_type == 'dpmsolver':
            deprecation_message = 'algorithm_type `dpmsolver` is deprecated and will be removed in a future version. Choose from `dpmsolver++` or `sde-dpmsolver++` instead'
            deprecate('algorithm_types=dpmsolver', '1.0.0', deprecation_message)
        if trained_betas is not None: self.betas = torch.tensor(trained_betas, dtype=torch.float32)
        elif beta_schedule == 'linear': self.betas = torch.linspace(beta_start, beta_end, num_train_timesteps, dtype=torch.float32)
        elif beta_schedule == 'scaled_linear': self.betas = torch.linspace(beta_start ** 0.5, beta_end ** 0.5, num_train_timesteps, dtype=torch.float32) ** 2
        elif beta_schedule == 'squaredcos_cap_v2': self.betas = betas_for_alpha_bar(num_train_timesteps)
        else: raise NotImplementedError(f'{beta_schedule} is not implemented for {self.__class__}')
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)
        self.alpha_t = torch.sqrt(self.alphas_cumprod)
        self.sigma_t = torch.sqrt(1 - self.alphas_cumprod)
        self.lambda_t = torch.log(self.alpha_t) - torch.log(self.sigma_t)
        self.sigmas = ((1 - self.alphas_cumprod) / self.alphas_cumprod) ** 0.5
        self.init_noise_sigma = 1.0
        if algorithm_type not in ['dpmsolver', 'dpmsolver++', 'sde-dpmsolver++']:
            if algorithm_type == 'deis': self.register_to_config(algorithm_type='dpmsolver++')
            else: raise NotImplementedError(f'{algorithm_type} is not implemented for {self.__class__}')
        if solver_type not in ['midpoint', 'heun']:
            if solver_type in ['logrho', 'bh1', 'bh2']: self.register_to_config(solver_type='midpoint')
            else: raise NotImplementedError(f'{solver_type} is not implemented for {self.__class__}')
        if algorithm_type not in ['dpmsolver++', 'sde-dpmsolver++'] and final_sigmas_type == 'zero': raise ValueError(f'`final_sigmas_type` {final_sigmas_type} is not supported for `algorithm_type` {algorithm_type}. Please chooose `sigma_min` instead.')
        self.num_inference_steps = None
        timesteps = np.linspace(0, num_train_timesteps - 1, num_train_timesteps, dtype=np.float32)[::-1].copy()
        self.timesteps = torch.from_numpy(timesteps)
        self.model_outputs = [None] * solver_order
        self.sample = None
        self.order_list = self.get_order_list(num_train_timesteps)
        self._step_index = None
        self._begin_index = None
        self.sigmas = self.sigmas.to('cpu')
    def get_order_list(self, num_inference_steps: int) -> List[int]:
        """Args:"""
        steps = num_inference_steps
        order = self.config.solver_order
        if order > 3: raise ValueError('Order > 3 is not supported by this scheduler')
        if self.config.lower_order_final:
            if order == 3:
                if steps % 3 == 0: orders = [1, 2, 3] * (steps // 3 - 1) + [1, 2] + [1]
                elif steps % 3 == 1: orders = [1, 2, 3] * (steps // 3) + [1]
                else: orders = [1, 2, 3] * (steps // 3) + [1, 2]
            elif order == 2:
                if steps % 2 == 0: orders = [1, 2] * (steps // 2 - 1) + [1, 1]
                else: orders = [1, 2] * (steps // 2) + [1]
            elif order == 1: orders = [1] * steps
        elif order == 3: orders = [1, 2, 3] * (steps // 3)
        elif order == 2: orders = [1, 2] * (steps // 2)
        elif order == 1: orders = [1] * steps
        if self.config.final_sigmas_type == 'zero': orders[-1] = 1
        return orders
    @property
    def step_index(self): return self._step_index
    @property
    def begin_index(self): return self._begin_index
    def set_begin_index(self, begin_index: int=0):
        """Args:"""
        self._begin_index = begin_index
    def set_timesteps(self, num_inference_steps: int=None, device: Union[str, torch.device]=None, timesteps: Optional[List[int]]=None):
        """Args:"""
        if num_inference_steps is None and timesteps is None: raise ValueError('Must pass exactly one of  `num_inference_steps` or `timesteps`.')
        if num_inference_steps is not None and timesteps is not None: raise ValueError('Must pass exactly one of  `num_inference_steps` or `timesteps`.')
        if timesteps is not None and self.config.use_karras_sigmas: raise ValueError('Cannot use `timesteps` when `config.use_karras_sigmas=True`.')
        if timesteps is not None and self.config.use_exponential_sigmas: raise ValueError('Cannot set `timesteps` with `config.use_exponential_sigmas = True`.')
        if timesteps is not None and self.config.use_beta_sigmas: raise ValueError('Cannot set `timesteps` with `config.use_beta_sigmas = True`.')
        num_inference_steps = num_inference_steps or len(timesteps)
        self.num_inference_steps = num_inference_steps
        if timesteps is not None: timesteps = np.array(timesteps).astype(np.int64)
        else:
            clipped_idx = torch.searchsorted(torch.flip(self.lambda_t, [0]), self.config.lambda_min_clipped)
            clipped_idx = clipped_idx.item()
            timesteps = np.linspace(0, self.config.num_train_timesteps - 1 - clipped_idx, num_inference_steps + 1).round()[::-1][:-1].copy().astype(np.int64)
        sigmas = np.array(((1 - self.alphas_cumprod) / self.alphas_cumprod) ** 0.5)
        log_sigmas = np.log(sigmas)
        if self.config.use_karras_sigmas:
            sigmas = np.flip(sigmas).copy()
            sigmas = self._convert_to_karras(in_sigmas=sigmas, num_inference_steps=num_inference_steps)
            timesteps = np.array([self._sigma_to_t(sigma, log_sigmas) for sigma in sigmas]).round()
        elif self.config.use_exponential_sigmas:
            sigmas = np.flip(sigmas).copy()
            sigmas = self._convert_to_exponential(in_sigmas=sigmas, num_inference_steps=num_inference_steps)
            timesteps = np.array([self._sigma_to_t(sigma, log_sigmas) for sigma in sigmas])
        elif self.config.use_beta_sigmas:
            sigmas = np.flip(sigmas).copy()
            sigmas = self._convert_to_beta(in_sigmas=sigmas, num_inference_steps=num_inference_steps)
            timesteps = np.array([self._sigma_to_t(sigma, log_sigmas) for sigma in sigmas])
        elif self.config.use_flow_sigmas:
            alphas = np.linspace(1, 1 / self.config.num_train_timesteps, num_inference_steps + 1)
            sigmas = 1.0 - alphas
            sigmas = np.flip(self.config.flow_shift * sigmas / (1 + (self.config.flow_shift - 1) * sigmas))[:-1].copy()
            timesteps = (sigmas * self.config.num_train_timesteps).copy()
        else: sigmas = np.interp(timesteps, np.arange(0, len(sigmas)), sigmas)
        if self.config.final_sigmas_type == 'sigma_min': sigma_last = ((1 - self.alphas_cumprod[0]) / self.alphas_cumprod[0]) ** 0.5
        elif self.config.final_sigmas_type == 'zero': sigma_last = 0
        else: raise ValueError(f' `final_sigmas_type` must be one of `sigma_min` or `zero`, but got {self.config.final_sigmas_type}')
        sigmas = np.concatenate([sigmas, [sigma_last]]).astype(np.float32)
        self.sigmas = torch.from_numpy(sigmas).to(device=device)
        self.timesteps = torch.from_numpy(timesteps).to(device=device, dtype=torch.int64)
        self.model_outputs = [None] * self.config.solver_order
        self.sample = None
        if not self.config.lower_order_final and num_inference_steps % self.config.solver_order != 0: self.register_to_config(lower_order_final=True)
        if not self.config.lower_order_final and self.config.final_sigmas_type == 'zero': self.register_to_config(lower_order_final=True)
        self.order_list = self.get_order_list(num_inference_steps)
        self._step_index = None
        self._begin_index = None
        self.sigmas = self.sigmas.to('cpu')
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
    def _sigma_to_t(self, sigma, log_sigmas):
        log_sigma = np.log(np.maximum(sigma, 1e-10))
        dists = log_sigma - log_sigmas[:, np.newaxis]
        low_idx = np.cumsum(dists >= 0, axis=0).argmax(axis=0).clip(max=log_sigmas.shape[0] - 2)
        high_idx = low_idx + 1
        low = log_sigmas[low_idx]
        high = log_sigmas[high_idx]
        w = (low - log_sigma) / (low - high)
        w = np.clip(w, 0, 1)
        t = (1 - w) * low_idx + w * high_idx
        t = t.reshape(sigma.shape)
        return t
    def _sigma_to_alpha_sigma_t(self, sigma):
        if self.config.use_flow_sigmas:
            alpha_t = 1 - sigma
            sigma_t = sigma
        else:
            alpha_t = 1 / (sigma ** 2 + 1) ** 0.5
            sigma_t = sigma * alpha_t
        return (alpha_t, sigma_t)
    def _convert_to_karras(self, in_sigmas: torch.Tensor, num_inference_steps) -> torch.Tensor:
        if hasattr(self.config, 'sigma_min'): sigma_min = self.config.sigma_min
        else: sigma_min = None
        if hasattr(self.config, 'sigma_max'): sigma_max = self.config.sigma_max
        else: sigma_max = None
        sigma_min = sigma_min if sigma_min is not None else in_sigmas[-1].item()
        sigma_max = sigma_max if sigma_max is not None else in_sigmas[0].item()
        rho = 7.0
        ramp = np.linspace(0, 1, num_inference_steps)
        min_inv_rho = sigma_min ** (1 / rho)
        max_inv_rho = sigma_max ** (1 / rho)
        sigmas = (max_inv_rho + ramp * (min_inv_rho - max_inv_rho)) ** rho
        return sigmas
    def _convert_to_exponential(self, in_sigmas: torch.Tensor, num_inference_steps: int) -> torch.Tensor:
        if hasattr(self.config, 'sigma_min'): sigma_min = self.config.sigma_min
        else: sigma_min = None
        if hasattr(self.config, 'sigma_max'): sigma_max = self.config.sigma_max
        else: sigma_max = None
        sigma_min = sigma_min if sigma_min is not None else in_sigmas[-1].item()
        sigma_max = sigma_max if sigma_max is not None else in_sigmas[0].item()
        sigmas = np.exp(np.linspace(math.log(sigma_max), math.log(sigma_min), num_inference_steps))
        return sigmas
    def _convert_to_beta(self, in_sigmas: torch.Tensor, num_inference_steps: int, alpha: float=0.6, beta: float=0.6) -> torch.Tensor:
        if hasattr(self.config, 'sigma_min'): sigma_min = self.config.sigma_min
        else: sigma_min = None
        if hasattr(self.config, 'sigma_max'): sigma_max = self.config.sigma_max
        else: sigma_max = None
        sigma_min = sigma_min if sigma_min is not None else in_sigmas[-1].item()
        sigma_max = sigma_max if sigma_max is not None else in_sigmas[0].item()
        sigmas = np.array([sigma_min + ppf * (sigma_max - sigma_min) for ppf in [scipy.stats.beta.ppf(timestep, alpha, beta) for timestep in 1 - np.linspace(0, 1, num_inference_steps)]])
        return sigmas
    def convert_model_output(self, model_output: torch.Tensor, *args, sample: torch.Tensor=None, **kwargs) -> torch.Tensor:
        """Returns:"""
        timestep = args[0] if len(args) > 0 else kwargs.pop('timestep', None)
        if sample is None:
            if len(args) > 1: sample = args[1]
            else: raise ValueError('missing `sample` as a required keyward argument')
        if timestep is not None: deprecate('timesteps', '1.0.0', 'Passing `timesteps` is deprecated and has no effect as model output conversion is now handled via an internal counter `self.step_index`')
        if self.config.algorithm_type in ['dpmsolver++', 'sde-dpmsolver++']:
            if self.config.prediction_type == 'epsilon':
                if self.config.variance_type in ['learned', 'learned_range']: model_output = model_output[:, :3]
                sigma = self.sigmas[self.step_index]
                alpha_t, sigma_t = self._sigma_to_alpha_sigma_t(sigma)
                x0_pred = (sample - sigma_t * model_output) / alpha_t
            elif self.config.prediction_type == 'sample': x0_pred = model_output
            elif self.config.prediction_type == 'v_prediction':
                sigma = self.sigmas[self.step_index]
                alpha_t, sigma_t = self._sigma_to_alpha_sigma_t(sigma)
                x0_pred = alpha_t * sample - sigma_t * model_output
            elif self.config.prediction_type == 'flow_prediction':
                sigma_t = self.sigmas[self.step_index]
                x0_pred = sample - sigma_t * model_output
            else: raise ValueError(f'prediction_type given as {self.config.prediction_type} must be one of `epsilon`, `sample`, `v_prediction`, or `flow_prediction` for the DPMSolverSinglestepScheduler.')
            if self.config.thresholding: x0_pred = self._threshold_sample(x0_pred)
            return x0_pred
        elif self.config.algorithm_type == 'dpmsolver':
            if self.config.prediction_type == 'epsilon':
                if self.config.variance_type in ['learned', 'learned_range']: epsilon = model_output[:, :3]
                else: epsilon = model_output
            elif self.config.prediction_type == 'sample':
                sigma = self.sigmas[self.step_index]
                alpha_t, sigma_t = self._sigma_to_alpha_sigma_t(sigma)
                epsilon = (sample - alpha_t * model_output) / sigma_t
            elif self.config.prediction_type == 'v_prediction':
                sigma = self.sigmas[self.step_index]
                alpha_t, sigma_t = self._sigma_to_alpha_sigma_t(sigma)
                epsilon = alpha_t * model_output + sigma_t * sample
            else: raise ValueError(f'prediction_type given as {self.config.prediction_type} must be one of `epsilon`, `sample`, or `v_prediction` for the DPMSolverSinglestepScheduler.')
            if self.config.thresholding:
                alpha_t, sigma_t = (self.alpha_t[timestep], self.sigma_t[timestep])
                x0_pred = (sample - sigma_t * epsilon) / alpha_t
                x0_pred = self._threshold_sample(x0_pred)
                epsilon = (sample - alpha_t * x0_pred) / sigma_t
            return epsilon
    def dpm_solver_first_order_update(self, model_output: torch.Tensor, *args, sample: torch.Tensor=None, noise: Optional[torch.Tensor]=None, **kwargs) -> torch.Tensor:
        """Returns:"""
        timestep = args[0] if len(args) > 0 else kwargs.pop('timestep', None)
        prev_timestep = args[1] if len(args) > 1 else kwargs.pop('prev_timestep', None)
        if sample is None:
            if len(args) > 2: sample = args[2]
            else: raise ValueError(' missing `sample` as a required keyward argument')
        if timestep is not None: deprecate('timesteps', '1.0.0', 'Passing `timesteps` is deprecated and has no effect as model output conversion is now handled via an internal counter `self.step_index`')
        if prev_timestep is not None: deprecate('prev_timestep', '1.0.0', 'Passing `prev_timestep` is deprecated and has no effect as model output conversion is now handled via an internal counter `self.step_index`')
        sigma_t, sigma_s = (self.sigmas[self.step_index + 1], self.sigmas[self.step_index])
        alpha_t, sigma_t = self._sigma_to_alpha_sigma_t(sigma_t)
        alpha_s, sigma_s = self._sigma_to_alpha_sigma_t(sigma_s)
        lambda_t = torch.log(alpha_t) - torch.log(sigma_t)
        lambda_s = torch.log(alpha_s) - torch.log(sigma_s)
        h = lambda_t - lambda_s
        if self.config.algorithm_type == 'dpmsolver++': x_t = sigma_t / sigma_s * sample - alpha_t * (torch.exp(-h) - 1.0) * model_output
        elif self.config.algorithm_type == 'dpmsolver': x_t = alpha_t / alpha_s * sample - sigma_t * (torch.exp(h) - 1.0) * model_output
        elif self.config.algorithm_type == 'sde-dpmsolver++':
            assert noise is not None
            x_t = sigma_t / sigma_s * torch.exp(-h) * sample + alpha_t * (1 - torch.exp(-2.0 * h)) * model_output + sigma_t * torch.sqrt(1.0 - torch.exp(-2 * h)) * noise
        return x_t
    def singlestep_dpm_solver_second_order_update(self, model_output_list: List[torch.Tensor], *args, sample: torch.Tensor=None, noise: Optional[torch.Tensor]=None, **kwargs) -> torch.Tensor:
        """Returns:"""
        timestep_list = args[0] if len(args) > 0 else kwargs.pop('timestep_list', None)
        prev_timestep = args[1] if len(args) > 1 else kwargs.pop('prev_timestep', None)
        if sample is None:
            if len(args) > 2: sample = args[2]
            else: raise ValueError(' missing `sample` as a required keyward argument')
        if timestep_list is not None: deprecate('timestep_list', '1.0.0', 'Passing `timestep_list` is deprecated and has no effect as model output conversion is now handled via an internal counter `self.step_index`')
        if prev_timestep is not None: deprecate('prev_timestep', '1.0.0', 'Passing `prev_timestep` is deprecated and has no effect as model output conversion is now handled via an internal counter `self.step_index`')
        sigma_t, sigma_s0, sigma_s1 = (self.sigmas[self.step_index + 1], self.sigmas[self.step_index], self.sigmas[self.step_index - 1])
        alpha_t, sigma_t = self._sigma_to_alpha_sigma_t(sigma_t)
        alpha_s0, sigma_s0 = self._sigma_to_alpha_sigma_t(sigma_s0)
        alpha_s1, sigma_s1 = self._sigma_to_alpha_sigma_t(sigma_s1)
        lambda_t = torch.log(alpha_t) - torch.log(sigma_t)
        lambda_s0 = torch.log(alpha_s0) - torch.log(sigma_s0)
        lambda_s1 = torch.log(alpha_s1) - torch.log(sigma_s1)
        m0, m1 = (model_output_list[-1], model_output_list[-2])
        h, h_0 = (lambda_t - lambda_s1, lambda_s0 - lambda_s1)
        r0 = h_0 / h
        D0, D1 = (m1, 1.0 / r0 * (m0 - m1))
        if self.config.algorithm_type == 'dpmsolver++':
            if self.config.solver_type == 'midpoint': x_t = sigma_t / sigma_s1 * sample - alpha_t * (torch.exp(-h) - 1.0) * D0 - 0.5 * (alpha_t * (torch.exp(-h) - 1.0)) * D1
            elif self.config.solver_type == 'heun': x_t = sigma_t / sigma_s1 * sample - alpha_t * (torch.exp(-h) - 1.0) * D0 + alpha_t * ((torch.exp(-h) - 1.0) / h + 1.0) * D1
        elif self.config.algorithm_type == 'dpmsolver':
            if self.config.solver_type == 'midpoint': x_t = alpha_t / alpha_s1 * sample - sigma_t * (torch.exp(h) - 1.0) * D0 - 0.5 * (sigma_t * (torch.exp(h) - 1.0)) * D1
            elif self.config.solver_type == 'heun': x_t = alpha_t / alpha_s1 * sample - sigma_t * (torch.exp(h) - 1.0) * D0 - sigma_t * ((torch.exp(h) - 1.0) / h - 1.0) * D1
        elif self.config.algorithm_type == 'sde-dpmsolver++':
            assert noise is not None
            if self.config.solver_type == 'midpoint': x_t = sigma_t / sigma_s1 * torch.exp(-h) * sample + alpha_t * (1 - torch.exp(-2.0 * h)) * D0 + 0.5 * (alpha_t * (1 - torch.exp(-2.0 * h))) * D1 + sigma_t * torch.sqrt(1.0 - torch.exp(-2 * h)) * noise
            elif self.config.solver_type == 'heun': x_t = sigma_t / sigma_s1 * torch.exp(-h) * sample + alpha_t * (1 - torch.exp(-2.0 * h)) * D0 + alpha_t * ((1.0 - torch.exp(-2.0 * h)) / (-2.0 * h) + 1.0) * D1 + sigma_t * torch.sqrt(1.0 - torch.exp(-2 * h)) * noise
        return x_t
    def singlestep_dpm_solver_third_order_update(self, model_output_list: List[torch.Tensor], *args, sample: torch.Tensor=None, noise: Optional[torch.Tensor]=None, **kwargs) -> torch.Tensor:
        """Returns:"""
        timestep_list = args[0] if len(args) > 0 else kwargs.pop('timestep_list', None)
        prev_timestep = args[1] if len(args) > 1 else kwargs.pop('prev_timestep', None)
        if sample is None:
            if len(args) > 2: sample = args[2]
            else: raise ValueError(' missing`sample` as a required keyward argument')
        if timestep_list is not None: deprecate('timestep_list', '1.0.0', 'Passing `timestep_list` is deprecated and has no effect as model output conversion is now handled via an internal counter `self.step_index`')
        if prev_timestep is not None: deprecate('prev_timestep', '1.0.0', 'Passing `prev_timestep` is deprecated and has no effect as model output conversion is now handled via an internal counter `self.step_index`')
        sigma_t, sigma_s0, sigma_s1, sigma_s2 = (self.sigmas[self.step_index + 1], self.sigmas[self.step_index], self.sigmas[self.step_index - 1], self.sigmas[self.step_index - 2])
        alpha_t, sigma_t = self._sigma_to_alpha_sigma_t(sigma_t)
        alpha_s0, sigma_s0 = self._sigma_to_alpha_sigma_t(sigma_s0)
        alpha_s1, sigma_s1 = self._sigma_to_alpha_sigma_t(sigma_s1)
        alpha_s2, sigma_s2 = self._sigma_to_alpha_sigma_t(sigma_s2)
        lambda_t = torch.log(alpha_t) - torch.log(sigma_t)
        lambda_s0 = torch.log(alpha_s0) - torch.log(sigma_s0)
        lambda_s1 = torch.log(alpha_s1) - torch.log(sigma_s1)
        lambda_s2 = torch.log(alpha_s2) - torch.log(sigma_s2)
        m0, m1, m2 = (model_output_list[-1], model_output_list[-2], model_output_list[-3])
        h, h_0, h_1 = (lambda_t - lambda_s2, lambda_s0 - lambda_s2, lambda_s1 - lambda_s2)
        r0, r1 = (h_0 / h, h_1 / h)
        D0 = m2
        D1_0, D1_1 = (1.0 / r1 * (m1 - m2), 1.0 / r0 * (m0 - m2))
        D1 = (r0 * D1_0 - r1 * D1_1) / (r0 - r1)
        D2 = 2.0 * (D1_1 - D1_0) / (r0 - r1)
        if self.config.algorithm_type == 'dpmsolver++':
            if self.config.solver_type == 'midpoint': x_t = sigma_t / sigma_s2 * sample - alpha_t * (torch.exp(-h) - 1.0) * D0 + alpha_t * ((torch.exp(-h) - 1.0) / h + 1.0) * D1_1
            elif self.config.solver_type == 'heun': x_t = sigma_t / sigma_s2 * sample - alpha_t * (torch.exp(-h) - 1.0) * D0 + alpha_t * ((torch.exp(-h) - 1.0) / h + 1.0) * D1 - alpha_t * ((torch.exp(-h) - 1.0 + h) / h ** 2 - 0.5) * D2
        elif self.config.algorithm_type == 'dpmsolver':
            if self.config.solver_type == 'midpoint': x_t = alpha_t / alpha_s2 * sample - sigma_t * (torch.exp(h) - 1.0) * D0 - sigma_t * ((torch.exp(h) - 1.0) / h - 1.0) * D1_1
            elif self.config.solver_type == 'heun': x_t = alpha_t / alpha_s2 * sample - sigma_t * (torch.exp(h) - 1.0) * D0 - sigma_t * ((torch.exp(h) - 1.0) / h - 1.0) * D1 - sigma_t * ((torch.exp(h) - 1.0 - h) / h ** 2 - 0.5) * D2
        elif self.config.algorithm_type == 'sde-dpmsolver++':
            assert noise is not None
            if self.config.solver_type == 'midpoint': x_t = sigma_t / sigma_s2 * torch.exp(-h) * sample + alpha_t * (1.0 - torch.exp(-2.0 * h)) * D0 + alpha_t * ((1.0 - torch.exp(-2.0 * h)) / (-2.0 * h) + 1.0) * D1_1 + sigma_t * torch.sqrt(1.0 - torch.exp(-2 * h)) * noise
            elif self.config.solver_type == 'heun': x_t = sigma_t / sigma_s2 * torch.exp(-h) * sample + alpha_t * (1.0 - torch.exp(-2.0 * h)) * D0 + alpha_t * ((1.0 - torch.exp(-2.0 * h)) / (-2.0 * h) + 1.0) * D1 + alpha_t * ((1.0 - torch.exp(-2.0 * h) + -2.0 * h) / (-2.0 * h) ** 2 - 0.5) * D2 + sigma_t * torch.sqrt(1.0 - torch.exp(-2 * h)) * noise
        return x_t
    def singlestep_dpm_solver_update(self, model_output_list: List[torch.Tensor], *args, sample: torch.Tensor=None, order: int=None, noise: Optional[torch.Tensor]=None, **kwargs) -> torch.Tensor:
        """Returns:"""
        timestep_list = args[0] if len(args) > 0 else kwargs.pop('timestep_list', None)
        prev_timestep = args[1] if len(args) > 1 else kwargs.pop('prev_timestep', None)
        if sample is None:
            if len(args) > 2: sample = args[2]
            else: raise ValueError(' missing`sample` as a required keyward argument')
        if order is None:
            if len(args) > 3: order = args[3]
            else: raise ValueError(' missing `order` as a required keyward argument')
        if timestep_list is not None: deprecate('timestep_list', '1.0.0', 'Passing `timestep_list` is deprecated and has no effect as model output conversion is now handled via an internal counter `self.step_index`')
        if prev_timestep is not None: deprecate('prev_timestep', '1.0.0', 'Passing `prev_timestep` is deprecated and has no effect as model output conversion is now handled via an internal counter `self.step_index`')
        if order == 1: return self.dpm_solver_first_order_update(model_output_list[-1], sample=sample, noise=noise)
        elif order == 2: return self.singlestep_dpm_solver_second_order_update(model_output_list, sample=sample, noise=noise)
        elif order == 3: return self.singlestep_dpm_solver_third_order_update(model_output_list, sample=sample, noise=noise)
        else: raise ValueError(f'Order must be 1, 2, 3, got {order}')
    def index_for_timestep(self, timestep, schedule_timesteps=None):
        if schedule_timesteps is None: schedule_timesteps = self.timesteps
        index_candidates = (schedule_timesteps == timestep).nonzero()
        if len(index_candidates) == 0: step_index = len(self.timesteps) - 1
        elif len(index_candidates) > 1: step_index = index_candidates[1].item()
        else: step_index = index_candidates[0].item()
        return step_index
    def _init_step_index(self, timestep):
        if self.begin_index is None:
            if isinstance(timestep, torch.Tensor): timestep = timestep.to(self.timesteps.device)
            self._step_index = self.index_for_timestep(timestep)
        else: self._step_index = self._begin_index
    def step(self, model_output: torch.Tensor, timestep: Union[int, torch.Tensor], sample: torch.Tensor, generator=None, return_dict: bool=True) -> Union[SchedulerOutput, Tuple]:
        """Returns:"""
        if self.num_inference_steps is None: raise ValueError("Number of inference steps is 'None', you need to run 'set_timesteps' after creating the scheduler")
        if self.step_index is None: self._init_step_index(timestep)
        model_output = self.convert_model_output(model_output, sample=sample)
        for i in range(self.config.solver_order - 1): self.model_outputs[i] = self.model_outputs[i + 1]
        self.model_outputs[-1] = model_output
        if self.config.algorithm_type == 'sde-dpmsolver++': noise = randn_tensor(model_output.shape, generator=generator, device=model_output.device, dtype=model_output.dtype)
        else: noise = None
        order = self.order_list[self.step_index]
        while self.model_outputs[-order] is None: order -= 1
        if order == 1: self.sample = sample
        prev_sample = self.singlestep_dpm_solver_update(self.model_outputs, sample=self.sample, order=order, noise=noise)
        self._step_index += 1
        if not return_dict: return (prev_sample,)
        return SchedulerOutput(prev_sample=prev_sample)
    def scale_model_input(self, sample: torch.Tensor, *args, **kwargs) -> torch.Tensor:
        """Returns:"""
        return sample
    def add_noise(self, original_samples: torch.Tensor, noise: torch.Tensor, timesteps: torch.IntTensor) -> torch.Tensor:
        sigmas = self.sigmas.to(device=original_samples.device, dtype=original_samples.dtype)
        if original_samples.device.type == 'mps' and torch.is_floating_point(timesteps):
            schedule_timesteps = self.timesteps.to(original_samples.device, dtype=torch.float32)
            timesteps = timesteps.to(original_samples.device, dtype=torch.float32)
        else:
            schedule_timesteps = self.timesteps.to(original_samples.device)
            timesteps = timesteps.to(original_samples.device)
        if self.begin_index is None: step_indices = [self.index_for_timestep(t, schedule_timesteps) for t in timesteps]
        elif self.step_index is not None: step_indices = [self.step_index] * timesteps.shape[0]
        else: step_indices = [self.begin_index] * timesteps.shape[0]
        sigma = sigmas[step_indices].flatten()
        while len(sigma.shape) < len(original_samples.shape): sigma = sigma.unsqueeze(-1)
        alpha_t, sigma_t = self._sigma_to_alpha_sigma_t(sigma)
        noisy_samples = alpha_t * original_samples + sigma_t * noise
        return noisy_samples
    def __len__(self): return self.config.num_train_timesteps
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
