'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from .configuration_utils import ConfigMixin, register_to_config
from typing import Any, Dict, List
from .utils import CONFIG_NAME
class PipelineCallback(ConfigMixin):
    config_name = CONFIG_NAME
    @register_to_config
    def __init__(self, cutoff_step_ratio=1.0, cutoff_step_index=None):
        super().__init__()
        if cutoff_step_ratio is None and cutoff_step_index is None or (cutoff_step_ratio is not None and cutoff_step_index is not None): raise ValueError('Either cutoff_step_ratio or cutoff_step_index should be provided, not both or none.')
        if cutoff_step_ratio is not None and (not isinstance(cutoff_step_ratio, float) or not 0.0 <= cutoff_step_ratio <= 1.0): raise ValueError('cutoff_step_ratio must be a float between 0.0 and 1.0.')
    @property
    def tensor_inputs(self) -> List[str]: raise NotImplementedError(f'You need to set the attribute `tensor_inputs` for {self.__class__}')
    def callback_fn(self, pipeline, step_index, timesteps, callback_kwargs) -> Dict[str, Any]: raise NotImplementedError(f'You need to implement the method `callback_fn` for {self.__class__}')
    def __call__(self, pipeline, step_index, timestep, callback_kwargs) -> Dict[str, Any]: return self.callback_fn(pipeline, step_index, timestep, callback_kwargs)
class MultiPipelineCallbacks:
    def __init__(self, callbacks: List[PipelineCallback]): self.callbacks = callbacks
    @property
    def tensor_inputs(self) -> List[str]: return [input for callback in self.callbacks for input in callback.tensor_inputs]
    def __call__(self, pipeline, step_index, timestep, callback_kwargs) -> Dict[str, Any]:
        for callback in self.callbacks: callback_kwargs = callback(pipeline, step_index, timestep, callback_kwargs)
        return callback_kwargs
class SDCFGCutoffCallback(PipelineCallback):
    tensor_inputs = ['prompt_embeds']
    def callback_fn(self, pipeline, step_index, timestep, callback_kwargs) -> Dict[str, Any]:
        cutoff_step_ratio = self.config.cutoff_step_ratio
        cutoff_step_index = self.config.cutoff_step_index
        cutoff_step = cutoff_step_index if cutoff_step_index is not None else int(pipeline.num_timesteps * cutoff_step_ratio)
        if step_index == cutoff_step:
            prompt_embeds = callback_kwargs[self.tensor_inputs[0]]
            prompt_embeds = prompt_embeds[-1:]
            pipeline._guidance_scale = 0.0
            callback_kwargs[self.tensor_inputs[0]] = prompt_embeds
        return callback_kwargs
class SDXLCFGCutoffCallback(PipelineCallback):
    tensor_inputs = ['prompt_embeds', 'add_text_embeds', 'add_time_ids']
    def callback_fn(self, pipeline, step_index, timestep, callback_kwargs) -> Dict[str, Any]:
        cutoff_step_ratio = self.config.cutoff_step_ratio
        cutoff_step_index = self.config.cutoff_step_index
        cutoff_step = cutoff_step_index if cutoff_step_index is not None else int(pipeline.num_timesteps * cutoff_step_ratio)
        if step_index == cutoff_step:
            prompt_embeds = callback_kwargs[self.tensor_inputs[0]]
            prompt_embeds = prompt_embeds[-1:]
            add_text_embeds = callback_kwargs[self.tensor_inputs[1]]
            add_text_embeds = add_text_embeds[-1:]
            add_time_ids = callback_kwargs[self.tensor_inputs[2]]
            add_time_ids = add_time_ids[-1:]
            pipeline._guidance_scale = 0.0
            callback_kwargs[self.tensor_inputs[0]] = prompt_embeds
            callback_kwargs[self.tensor_inputs[1]] = add_text_embeds
            callback_kwargs[self.tensor_inputs[2]] = add_time_ids
        return callback_kwargs
class SDXLControlnetCFGCutoffCallback(PipelineCallback):
    tensor_inputs = ['prompt_embeds', 'add_text_embeds', 'add_time_ids', 'image']
    def callback_fn(self, pipeline, step_index, timestep, callback_kwargs) -> Dict[str, Any]:
        cutoff_step_ratio = self.config.cutoff_step_ratio
        cutoff_step_index = self.config.cutoff_step_index
        cutoff_step = cutoff_step_index if cutoff_step_index is not None else int(pipeline.num_timesteps * cutoff_step_ratio)
        if step_index == cutoff_step:
            prompt_embeds = callback_kwargs[self.tensor_inputs[0]]
            prompt_embeds = prompt_embeds[-1:]
            add_text_embeds = callback_kwargs[self.tensor_inputs[1]]
            add_text_embeds = add_text_embeds[-1:]
            add_time_ids = callback_kwargs[self.tensor_inputs[2]]
            add_time_ids = add_time_ids[-1:]
            image = callback_kwargs[self.tensor_inputs[3]]
            image = image[-1:]
            pipeline._guidance_scale = 0.0
            callback_kwargs[self.tensor_inputs[0]] = prompt_embeds
            callback_kwargs[self.tensor_inputs[1]] = add_text_embeds
            callback_kwargs[self.tensor_inputs[2]] = add_time_ids
            callback_kwargs[self.tensor_inputs[3]] = image
        return callback_kwargs
class IPAdapterScaleCutoffCallback(PipelineCallback):
    tensor_inputs = []
    def callback_fn(self, pipeline, step_index, timestep, callback_kwargs) -> Dict[str, Any]:
        cutoff_step_ratio = self.config.cutoff_step_ratio
        cutoff_step_index = self.config.cutoff_step_index
        cutoff_step = cutoff_step_index if cutoff_step_index is not None else int(pipeline.num_timesteps * cutoff_step_ratio)
        if step_index == cutoff_step: pipeline.set_ip_adapter_scale(0.0)
        return callback_kwargs
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
