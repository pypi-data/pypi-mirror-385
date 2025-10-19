'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import List, Optional, Tuple, Union
import torch
from ....models import UNet2DModel
from ....schedulers import ScoreSdeVeScheduler
from ....utils.torch_utils import randn_tensor
from ...pipeline_utils import DiffusionPipeline, ImagePipelineOutput
class ScoreSdeVePipeline(DiffusionPipeline):
    unet: UNet2DModel
    scheduler: ScoreSdeVeScheduler
    def __init__(self, unet: UNet2DModel, scheduler: ScoreSdeVeScheduler):
        super().__init__()
        self.register_modules(unet=unet, scheduler=scheduler)
    @torch.no_grad()
    def __call__(self, batch_size: int=1, num_inference_steps: int=2000, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, output_type: Optional[str]='pil',
    return_dict: bool=True, **kwargs) -> Union[ImagePipelineOutput, Tuple]:
        """Returns:"""
        img_size = self.unet.config.sample_size
        shape = (batch_size, 3, img_size, img_size)
        model = self.unet
        sample = randn_tensor(shape, generator=generator) * self.scheduler.init_noise_sigma
        sample = sample.to(self.device)
        self.scheduler.set_timesteps(num_inference_steps)
        self.scheduler.set_sigmas(num_inference_steps)
        for i, t in enumerate(self.progress_bar(self.scheduler.timesteps)):
            sigma_t = self.scheduler.sigmas[i] * torch.ones(shape[0], device=self.device)
            for _ in range(self.scheduler.config.correct_steps):
                model_output = self.unet(sample, sigma_t).sample
                sample = self.scheduler.step_correct(model_output, sample, generator=generator).prev_sample
            model_output = model(sample, sigma_t).sample
            output = self.scheduler.step_pred(model_output, t, sample, generator=generator)
            sample, sample_mean = (output.prev_sample, output.prev_sample_mean)
        sample = sample_mean.clamp(0, 1)
        sample = sample.cpu().permute(0, 2, 3, 1).numpy()
        if output_type == 'pil': sample = self.numpy_to_pil(sample)
        if not return_dict: return (sample,)
        return ImagePipelineOutput(images=sample)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
