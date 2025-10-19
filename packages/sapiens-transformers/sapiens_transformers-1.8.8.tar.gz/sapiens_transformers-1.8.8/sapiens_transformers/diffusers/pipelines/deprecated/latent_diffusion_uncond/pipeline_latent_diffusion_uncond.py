'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from typing import List, Optional, Tuple, Union
import torch
from ....models import UNet2DModel, VQModel
from ....schedulers import DDIMScheduler
from ....utils.torch_utils import randn_tensor
from ...pipeline_utils import DiffusionPipeline, ImagePipelineOutput
class LDMPipeline(DiffusionPipeline):
    def __init__(self, vqvae: VQModel, unet: UNet2DModel, scheduler: DDIMScheduler):
        super().__init__()
        self.register_modules(vqvae=vqvae, unet=unet, scheduler=scheduler)
    @torch.no_grad()
    def __call__(self, batch_size: int=1, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, eta: float=0.0, num_inference_steps: int=50,
    output_type: Optional[str]='pil', return_dict: bool=True, **kwargs) -> Union[Tuple, ImagePipelineOutput]:
        """Returns:"""
        latents = randn_tensor((batch_size, self.unet.config.in_channels, self.unet.config.sample_size, self.unet.config.sample_size), generator=generator)
        latents = latents.to(self.device)
        latents = latents * self.scheduler.init_noise_sigma
        self.scheduler.set_timesteps(num_inference_steps)
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_kwargs = {}
        if accepts_eta: extra_kwargs['eta'] = eta
        for t in self.progress_bar(self.scheduler.timesteps):
            latent_model_input = self.scheduler.scale_model_input(latents, t)
            noise_prediction = self.unet(latent_model_input, t).sample
            latents = self.scheduler.step(noise_prediction, t, latents, **extra_kwargs).prev_sample
        latents = latents / self.vqvae.config.scaling_factor
        image = self.vqvae.decode(latents).sample
        image = (image / 2 + 0.5).clamp(0, 1)
        image = image.cpu().permute(0, 2, 3, 1).numpy()
        if output_type == 'pil': image = self.numpy_to_pil(image)
        if not return_dict: return (image,)
        return ImagePipelineOutput(images=image)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
