'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import math
from typing import Any, Callable, List, Optional, Tuple, Union
import numpy as np
import torch
from ....models import T5FilmDecoder
from ....schedulers import DDPMScheduler
from ....utils import is_onnx_available
from ....utils.torch_utils import randn_tensor
if is_onnx_available(): from ...onnx_utils import OnnxRuntimeModel
from ...pipeline_utils import AudioPipelineOutput, DiffusionPipeline
from .continuous_encoder import SpectrogramContEncoder
from .notes_encoder import SpectrogramNotesEncoder
TARGET_FEATURE_LENGTH = 256
class SpectrogramDiffusionPipeline(DiffusionPipeline):
    """Args:"""
    _optional_components = ['melgan']
    def __init__(self, notes_encoder: SpectrogramNotesEncoder, continuous_encoder: SpectrogramContEncoder, decoder: T5FilmDecoder,
    scheduler: DDPMScheduler, melgan: OnnxRuntimeModel if is_onnx_available() else Any) -> None:
        super().__init__()
        self.min_value = math.log(1e-05)
        self.max_value = 4.0
        self.n_dims = 128
        self.register_modules(notes_encoder=notes_encoder, continuous_encoder=continuous_encoder, decoder=decoder, scheduler=scheduler, melgan=melgan)
    def scale_features(self, features, output_range=(-1.0, 1.0), clip=False):
        min_out, max_out = output_range
        if clip: features = torch.clip(features, self.min_value, self.max_value)
        zero_one = (features - self.min_value) / (self.max_value - self.min_value)
        return zero_one * (max_out - min_out) + min_out
    def scale_to_features(self, outputs, input_range=(-1.0, 1.0), clip=False):
        min_out, max_out = input_range
        outputs = torch.clip(outputs, min_out, max_out) if clip else outputs
        zero_one = (outputs - min_out) / (max_out - min_out)
        return zero_one * (self.max_value - self.min_value) + self.min_value
    def encode(self, input_tokens, continuous_inputs, continuous_mask):
        tokens_mask = input_tokens > 0
        tokens_encoded, tokens_mask = self.notes_encoder(encoder_input_tokens=input_tokens, encoder_inputs_mask=tokens_mask)
        continuous_encoded, continuous_mask = self.continuous_encoder(encoder_inputs=continuous_inputs, encoder_inputs_mask=continuous_mask)
        return [(tokens_encoded, tokens_mask), (continuous_encoded, continuous_mask)]
    def decode(self, encodings_and_masks, input_tokens, noise_time):
        timesteps = noise_time
        if not torch.is_tensor(timesteps): timesteps = torch.tensor([timesteps], dtype=torch.long, device=input_tokens.device)
        elif torch.is_tensor(timesteps) and len(timesteps.shape) == 0: timesteps = timesteps[None].to(input_tokens.device)
        timesteps = timesteps * torch.ones(input_tokens.shape[0], dtype=timesteps.dtype, device=timesteps.device)
        logits = self.decoder(encodings_and_masks=encodings_and_masks, decoder_input_tokens=input_tokens, decoder_noise_time=timesteps)
        return logits
    @torch.no_grad()
    def __call__(self, input_tokens: List[List[int]], generator: Optional[torch.Generator]=None, num_inference_steps: int=100, return_dict: bool=True,
    output_type: str='np', callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: int=1) -> Union[AudioPipelineOutput, Tuple]:
        if callback_steps is None or (callback_steps is not None and (not isinstance(callback_steps, int) or callback_steps <= 0)): raise ValueError(f'`callback_steps` has to be a positive integer but is {callback_steps} of type {type(callback_steps)}.')
        """Returns:"""
        pred_mel = np.zeros([1, TARGET_FEATURE_LENGTH, self.n_dims], dtype=np.float32)
        full_pred_mel = np.zeros([1, 0, self.n_dims], np.float32)
        ones = torch.ones((1, TARGET_FEATURE_LENGTH), dtype=bool, device=self.device)
        for i, encoder_input_tokens in enumerate(input_tokens):
            if i == 0:
                encoder_continuous_inputs = torch.from_numpy(pred_mel[:1].copy()).to(device=self.device, dtype=self.decoder.dtype)
                encoder_continuous_mask = torch.zeros((1, TARGET_FEATURE_LENGTH), dtype=bool, device=self.device)
            else: encoder_continuous_mask = ones
            encoder_continuous_inputs = self.scale_features(encoder_continuous_inputs, output_range=[-1.0, 1.0], clip=True)
            encodings_and_masks = self.encode(input_tokens=torch.IntTensor([encoder_input_tokens]).to(device=self.device),
            continuous_inputs=encoder_continuous_inputs, continuous_mask=encoder_continuous_mask)
            x = randn_tensor(shape=encoder_continuous_inputs.shape, generator=generator, device=self.device, dtype=self.decoder.dtype)
            self.scheduler.set_timesteps(num_inference_steps)
            for j, t in enumerate(self.progress_bar(self.scheduler.timesteps)):
                output = self.decode(encodings_and_masks=encodings_and_masks, input_tokens=x, noise_time=t / self.scheduler.config.num_train_timesteps)
                x = self.scheduler.step(output, t, x, generator=generator).prev_sample
            mel = self.scale_to_features(x, input_range=[-1.0, 1.0])
            encoder_continuous_inputs = mel[:1]
            pred_mel = mel.cpu().float().numpy()
            full_pred_mel = np.concatenate([full_pred_mel, pred_mel[:1]], axis=1)
            if callback is not None and i % callback_steps == 0: callback(i, full_pred_mel)
        if output_type == 'np' and (not is_onnx_available()): raise ValueError("Cannot return output in 'np' format if ONNX is not available. Make sure to have ONNX installed or set 'output_type' to 'mel'.")
        elif output_type == 'np' and self.melgan is None: raise ValueError("Cannot return output in 'np' format if melgan component is not defined. Make sure to define `self.melgan` or set 'output_type' to 'mel'.")
        if output_type == 'np': output = self.melgan(input_features=full_pred_mel.astype(np.float32))
        else: output = full_pred_mel
        if not return_dict: return (output,)
        return AudioPipelineOutput(audios=output)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
