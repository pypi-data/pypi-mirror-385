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
import torch
from ..configuration_utils import ConfigMixin, register_to_config
from ..utils import BaseOutput
from .scheduling_utils import SchedulerMixin
def gumbel_noise(t, generator=None):
    device = generator.device if generator is not None else t.device
    noise = torch.zeros_like(t, device=device).uniform_(0, 1, generator=generator).to(t.device)
    return -torch.log((-torch.log(noise.clamp(1e-20))).clamp(1e-20))
def mask_by_random_topk(mask_len, probs, temperature=1.0, generator=None):
    confidence = torch.log(probs.clamp(1e-20)) + temperature * gumbel_noise(probs, generator=generator)
    sorted_confidence = torch.sort(confidence, dim=-1).values
    cut_off = torch.gather(sorted_confidence, 1, mask_len.long())
    masking = confidence < cut_off
    return masking
@dataclass
class AmusedSchedulerOutput(BaseOutput):
    """Args:"""
    prev_sample: torch.Tensor
    pred_original_sample: torch.Tensor = None
class AmusedScheduler(SchedulerMixin, ConfigMixin):
    order = 1
    temperatures: torch.Tensor
    @register_to_config
    def __init__(self, mask_token_id: int, masking_schedule: str='cosine'):
        self.temperatures = None
        self.timesteps = None
    def set_timesteps(self, num_inference_steps: int, temperature: Union[int, Tuple[int, int], List[int]]=(2, 0), device: Union[str, torch.device]=None):
        self.timesteps = torch.arange(num_inference_steps, device=device).flip(0)
        if isinstance(temperature, (tuple, list)): self.temperatures = torch.linspace(temperature[0], temperature[1], num_inference_steps, device=device)
        else: self.temperatures = torch.linspace(temperature, 0.01, num_inference_steps, device=device)
    def step(self, model_output: torch.Tensor, timestep: torch.long, sample: torch.LongTensor, starting_mask_ratio: int=1, generator: Optional[torch.Generator]=None,
    return_dict: bool=True) -> Union[AmusedSchedulerOutput, Tuple]:
        two_dim_input = sample.ndim == 3 and model_output.ndim == 4
        if two_dim_input:
            batch_size, codebook_size, height, width = model_output.shape
            sample = sample.reshape(batch_size, height * width)
            model_output = model_output.reshape(batch_size, codebook_size, height * width).permute(0, 2, 1)
        unknown_map = sample == self.config.mask_token_id
        probs = model_output.softmax(dim=-1)
        device = probs.device
        probs_ = probs.to(generator.device) if generator is not None else probs
        if probs_.device.type == 'cpu' and probs_.dtype != torch.float32: probs_ = probs_.float()
        probs_ = probs_.reshape(-1, probs.size(-1))
        pred_original_sample = torch.multinomial(probs_, 1, generator=generator).to(device=device)
        pred_original_sample = pred_original_sample[:, 0].view(*probs.shape[:-1])
        pred_original_sample = torch.where(unknown_map, pred_original_sample, sample)
        if timestep == 0: prev_sample = pred_original_sample
        else:
            seq_len = sample.shape[1]
            step_idx = (self.timesteps == timestep).nonzero()
            ratio = (step_idx + 1) / len(self.timesteps)
            if self.config.masking_schedule == 'cosine': mask_ratio = torch.cos(ratio * math.pi / 2)
            elif self.config.masking_schedule == 'linear': mask_ratio = 1 - ratio
            else: raise ValueError(f'unknown masking schedule {self.config.masking_schedule}')
            mask_ratio = starting_mask_ratio * mask_ratio
            mask_len = (seq_len * mask_ratio).floor()
            mask_len = torch.min(unknown_map.sum(dim=-1, keepdim=True) - 1, mask_len)
            mask_len = torch.max(torch.tensor([1], device=model_output.device), mask_len)
            selected_probs = torch.gather(probs, -1, pred_original_sample[:, :, None])[:, :, 0]
            selected_probs = torch.where(unknown_map, selected_probs, torch.finfo(selected_probs.dtype).max)
            masking = mask_by_random_topk(mask_len, selected_probs, self.temperatures[step_idx], generator)
            prev_sample = torch.where(masking, self.config.mask_token_id, pred_original_sample)
        if two_dim_input:
            prev_sample = prev_sample.reshape(batch_size, height, width)
            pred_original_sample = pred_original_sample.reshape(batch_size, height, width)
        if not return_dict: return (prev_sample, pred_original_sample)
        return AmusedSchedulerOutput(prev_sample, pred_original_sample)
    def add_noise(self, sample, timesteps, generator=None):
        step_idx = (self.timesteps == timesteps).nonzero()
        ratio = (step_idx + 1) / len(self.timesteps)
        if self.config.masking_schedule == 'cosine': mask_ratio = torch.cos(ratio * math.pi / 2)
        elif self.config.masking_schedule == 'linear': mask_ratio = 1 - ratio
        else: raise ValueError(f'unknown masking schedule {self.config.masking_schedule}')
        mask_indices = torch.rand(sample.shape, device=generator.device if generator is not None else sample.device, generator=generator).to(sample.device) < mask_ratio
        masked_sample = sample.clone()
        masked_sample[mask_indices] = self.config.mask_token_id
        return masked_sample
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
