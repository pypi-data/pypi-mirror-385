'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
from ..utils import is_torch_available
from .quantization_config import QuantizationConfigMixin
if TYPE_CHECKING: from ..models.modeling_utils import ModelMixin
if is_torch_available():
    import torch
class DiffusersQuantizer(ABC):
    requires_calibration = False
    required_packages = None
    def __init__(self, quantization_config: QuantizationConfigMixin, **kwargs):
        self.quantization_config = quantization_config
        self.modules_to_not_convert = kwargs.pop('modules_to_not_convert', [])
        self.pre_quantized = kwargs.pop('pre_quantized', True)
        if not self.pre_quantized and self.requires_calibration: raise ValueError(f'The quantization method {quantization_config.quant_method} does require the model to be pre-quantized. You explicitly passed `pre_quantized=False` meaning your model weights are not quantized. Make sure to pass `pre_quantized=True` while knowing what you are doing.')
    def update_torch_dtype(self, torch_dtype: 'torch.dtype') -> 'torch.dtype':
        """Args:"""
        return torch_dtype
    def update_device_map(self, device_map: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Args:"""
        return device_map
    def adjust_target_dtype(self, torch_dtype: 'torch.dtype') -> 'torch.dtype':
        """Args:"""
        return torch_dtype
    def update_missing_keys(self, model, missing_keys: List[str], prefix: str) -> List[str]:
        """Args:"""
        return missing_keys
    def get_special_dtypes_update(self, model, torch_dtype: 'torch.dtype') -> Dict[str, 'torch.dtype']:
        """Args:"""
        return {name: torch_dtype for name, _ in model.named_parameters() if any((m in name for m in self.modules_to_not_convert))}
    def adjust_max_memory(self, max_memory: Dict[str, Union[int, str]]) -> Dict[str, Union[int, str]]: return max_memory
    def check_if_quantized_param(self, model: 'ModelMixin', param_value: 'torch.Tensor', param_name: str, state_dict: Dict[str, Any], **kwargs) -> bool: return False
    def create_quantized_param(self, *args, **kwargs) -> 'torch.nn.Parameter': return
    def check_quantized_param_shape(self, *args, **kwargs): return True
    def validate_environment(self, *args, **kwargs): return
    def preprocess_model(self, model: 'ModelMixin', **kwargs):
        """Args:"""
        model.is_quantized = True
        model.quantization_method = self.quantization_config.quant_method
        return self._process_model_before_weight_loading(model, **kwargs)
    def postprocess_model(self, model: 'ModelMixin', **kwargs):
        """Args:"""
        return self._process_model_after_weight_loading(model, **kwargs)
    def dequantize(self, model):
        model = self._dequantize(model)
        del model.hf_quantizer
        return model
    def _dequantize(self, model): raise NotImplementedError(f'{self.quantization_config.quant_method} has no implementation of `dequantize`, please raise an issue on GitHub.')
    @abstractmethod
    def _process_model_before_weight_loading(self, model, **kwargs): ...
    @abstractmethod
    def _process_model_after_weight_loading(self, model, **kwargs): ...
    @property
    @abstractmethod
    def is_serializable(self): ...
    @property
    @abstractmethod
    def is_trainable(self): ...
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
