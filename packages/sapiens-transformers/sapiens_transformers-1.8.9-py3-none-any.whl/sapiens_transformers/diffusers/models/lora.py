'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..utils.import_utils import is_transformers_available
from typing import Optional, Tuple, Union
from ..utils import deprecate
import torch.nn.functional as F
from torch import nn
import torch
if is_transformers_available(): from sapiens_transformers import CLIPTextModel, CLIPTextModelWithProjection
def text_encoder_attn_modules(text_encoder):
    attn_modules = []
    if isinstance(text_encoder, (CLIPTextModel, CLIPTextModelWithProjection)):
        for i, layer in enumerate(text_encoder.text_model.encoder.layers):
            name = f'text_model.encoder.layers.{i}.self_attn'
            mod = layer.self_attn
            attn_modules.append((name, mod))
    else: raise ValueError(f'do not know how to get attention modules for: {text_encoder.__class__.__name__}')
    return attn_modules
def text_encoder_mlp_modules(text_encoder):
    mlp_modules = []
    if isinstance(text_encoder, (CLIPTextModel, CLIPTextModelWithProjection)):
        for i, layer in enumerate(text_encoder.text_model.encoder.layers):
            mlp_mod = layer.mlp
            name = f'text_model.encoder.layers.{i}.mlp'
            mlp_modules.append((name, mlp_mod))
    else: raise ValueError(f'do not know how to get mlp modules for: {text_encoder.__class__.__name__}')
    return mlp_modules
def adjust_lora_scale_text_encoder(text_encoder, lora_scale: float=1.0):
    for _, attn_module in text_encoder_attn_modules(text_encoder):
        if isinstance(attn_module.q_proj, PatchedLoraProjection):
            attn_module.q_proj.lora_scale = lora_scale
            attn_module.k_proj.lora_scale = lora_scale
            attn_module.v_proj.lora_scale = lora_scale
            attn_module.out_proj.lora_scale = lora_scale
    for _, mlp_module in text_encoder_mlp_modules(text_encoder):
        if isinstance(mlp_module.fc1, PatchedLoraProjection):
            mlp_module.fc1.lora_scale = lora_scale
            mlp_module.fc2.lora_scale = lora_scale
class PatchedLoraProjection(torch.nn.Module):
    def __init__(self, regular_linear_layer, lora_scale=1, network_alpha=None, rank=4, dtype=None):
        deprecation_message = 'Use of `PatchedLoraProjection` is deprecated. Please switch to PEFT backend by installing PEFT: `pip install peft`.'
        deprecate('PatchedLoraProjection', '1.0.0', deprecation_message)
        super().__init__()
        from ..models.lora import LoRALinearLayer
        self.regular_linear_layer = regular_linear_layer
        device = self.regular_linear_layer.weight.device
        if dtype is None: dtype = self.regular_linear_layer.weight.dtype
        self.lora_linear_layer = LoRALinearLayer(self.regular_linear_layer.in_features, self.regular_linear_layer.out_features, network_alpha=network_alpha, device=device, dtype=dtype, rank=rank)
        self.lora_scale = lora_scale
    def state_dict(self, *args, destination=None, prefix='', keep_vars=False):
        if self.lora_linear_layer is None: return self.regular_linear_layer.state_dict(*args, destination=destination, prefix=prefix, keep_vars=keep_vars)
        return super().state_dict(*args, destination=destination, prefix=prefix, keep_vars=keep_vars)
    def _fuse_lora(self, lora_scale=1.0, safe_fusing=False):
        if self.lora_linear_layer is None: return
        dtype, device = (self.regular_linear_layer.weight.data.dtype, self.regular_linear_layer.weight.data.device)
        w_orig = self.regular_linear_layer.weight.data.float()
        w_up = self.lora_linear_layer.up.weight.data.float()
        w_down = self.lora_linear_layer.down.weight.data.float()
        if self.lora_linear_layer.network_alpha is not None: w_up = w_up * self.lora_linear_layer.network_alpha / self.lora_linear_layer.rank
        fused_weight = w_orig + lora_scale * torch.bmm(w_up[None, :], w_down[None, :])[0]
        if safe_fusing and torch.isnan(fused_weight).any().item(): raise ValueError(f'This LoRA weight seems to be broken. Encountered NaN values when trying to fuse LoRA weights for {self}.LoRA weights will not be fused.')
        self.regular_linear_layer.weight.data = fused_weight.to(device=device, dtype=dtype)
        self.lora_linear_layer = None
        self.w_up = w_up.cpu()
        self.w_down = w_down.cpu()
        self.lora_scale = lora_scale
    def _unfuse_lora(self):
        if not (getattr(self, 'w_up', None) is not None and getattr(self, 'w_down', None) is not None): return
        fused_weight = self.regular_linear_layer.weight.data
        dtype, device = (fused_weight.dtype, fused_weight.device)
        w_up = self.w_up.to(device=device).float()
        w_down = self.w_down.to(device).float()
        unfused_weight = fused_weight.float() - self.lora_scale * torch.bmm(w_up[None, :], w_down[None, :])[0]
        self.regular_linear_layer.weight.data = unfused_weight.to(device=device, dtype=dtype)
        self.w_up = None
        self.w_down = None
    def forward(self, input):
        if self.lora_scale is None: self.lora_scale = 1.0
        if self.lora_linear_layer is None: return self.regular_linear_layer(input)
        return self.regular_linear_layer(input) + self.lora_scale * self.lora_linear_layer(input)
class LoRALinearLayer(nn.Module):
    def __init__(self, in_features: int, out_features: int, rank: int=4, network_alpha: Optional[float]=None, device: Optional[Union[torch.device, str]]=None, dtype: Optional[torch.dtype]=None):
        super().__init__()
        deprecation_message = 'Use of `LoRALinearLayer` is deprecated. Please switch to PEFT backend by installing PEFT: `pip install peft`.'
        deprecate('LoRALinearLayer', '1.0.0', deprecation_message)
        self.down = nn.Linear(in_features, rank, bias=False, device=device, dtype=dtype)
        self.up = nn.Linear(rank, out_features, bias=False, device=device, dtype=dtype)
        self.network_alpha = network_alpha
        self.rank = rank
        self.out_features = out_features
        self.in_features = in_features
        nn.init.normal_(self.down.weight, std=1 / rank)
        nn.init.zeros_(self.up.weight)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        orig_dtype = hidden_states.dtype
        dtype = self.down.weight.dtype
        down_hidden_states = self.down(hidden_states.to(dtype))
        up_hidden_states = self.up(down_hidden_states)
        if self.network_alpha is not None: up_hidden_states *= self.network_alpha / self.rank
        return up_hidden_states.to(orig_dtype)
class LoRAConv2dLayer(nn.Module):
    def __init__(self, in_features: int, out_features: int, rank: int=4, kernel_size: Union[int, Tuple[int, int]]=(1, 1), stride: Union[int, Tuple[int, int]]=(1, 1),
    padding: Union[int, Tuple[int, int], str]=0, network_alpha: Optional[float]=None):
        super().__init__()
        deprecation_message = 'Use of `LoRAConv2dLayer` is deprecated. Please switch to PEFT backend by installing PEFT: `pip install peft`.'
        deprecate('LoRAConv2dLayer', '1.0.0', deprecation_message)
        self.down = nn.Conv2d(in_features, rank, kernel_size=kernel_size, stride=stride, padding=padding, bias=False)
        self.up = nn.Conv2d(rank, out_features, kernel_size=(1, 1), stride=(1, 1), bias=False)
        self.network_alpha = network_alpha
        self.rank = rank
        nn.init.normal_(self.down.weight, std=1 / rank)
        nn.init.zeros_(self.up.weight)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        orig_dtype = hidden_states.dtype
        dtype = self.down.weight.dtype
        down_hidden_states = self.down(hidden_states.to(dtype))
        up_hidden_states = self.up(down_hidden_states)
        if self.network_alpha is not None: up_hidden_states *= self.network_alpha / self.rank
        return up_hidden_states.to(orig_dtype)
class LoRACompatibleConv(nn.Conv2d):
    def __init__(self, *args, lora_layer: Optional[LoRAConv2dLayer]=None, **kwargs):
        deprecation_message = 'Use of `LoRACompatibleConv` is deprecated. Please switch to PEFT backend by installing PEFT: `pip install peft`.'
        deprecate('LoRACompatibleConv', '1.0.0', deprecation_message)
        super().__init__(*args, **kwargs)
        self.lora_layer = lora_layer
    def set_lora_layer(self, lora_layer: Optional[LoRAConv2dLayer]):
        deprecation_message = 'Use of `set_lora_layer()` is deprecated. Please switch to PEFT backend by installing PEFT: `pip install peft`.'
        deprecate('set_lora_layer', '1.0.0', deprecation_message)
        self.lora_layer = lora_layer
    def _fuse_lora(self, lora_scale: float=1.0, safe_fusing: bool=False):
        if self.lora_layer is None: return
        dtype, device = (self.weight.data.dtype, self.weight.data.device)
        w_orig = self.weight.data.float()
        w_up = self.lora_layer.up.weight.data.float()
        w_down = self.lora_layer.down.weight.data.float()
        if self.lora_layer.network_alpha is not None: w_up = w_up * self.lora_layer.network_alpha / self.lora_layer.rank
        fusion = torch.mm(w_up.flatten(start_dim=1), w_down.flatten(start_dim=1))
        fusion = fusion.reshape(w_orig.shape)
        fused_weight = w_orig + lora_scale * fusion
        if safe_fusing and torch.isnan(fused_weight).any().item(): raise ValueError(f'This LoRA weight seems to be broken. Encountered NaN values when trying to fuse LoRA weights for {self}.LoRA weights will not be fused.')
        self.weight.data = fused_weight.to(device=device, dtype=dtype)
        self.lora_layer = None
        self.w_up = w_up.cpu()
        self.w_down = w_down.cpu()
        self._lora_scale = lora_scale
    def _unfuse_lora(self):
        if not (getattr(self, 'w_up', None) is not None and getattr(self, 'w_down', None) is not None): return
        fused_weight = self.weight.data
        dtype, device = (fused_weight.data.dtype, fused_weight.data.device)
        self.w_up = self.w_up.to(device=device).float()
        self.w_down = self.w_down.to(device).float()
        fusion = torch.mm(self.w_up.flatten(start_dim=1), self.w_down.flatten(start_dim=1))
        fusion = fusion.reshape(fused_weight.shape)
        unfused_weight = fused_weight.float() - self._lora_scale * fusion
        self.weight.data = unfused_weight.to(device=device, dtype=dtype)
        self.w_up = None
        self.w_down = None
    def forward(self, hidden_states: torch.Tensor, scale: float=1.0) -> torch.Tensor:
        if self.padding_mode != 'zeros':
            hidden_states = F.pad(hidden_states, self._reversed_padding_repeated_twice, mode=self.padding_mode)
            padding = (0, 0)
        else: padding = self.padding
        original_outputs = F.conv2d(hidden_states, self.weight, self.bias, self.stride, padding, self.dilation, self.groups)
        if self.lora_layer is None: return original_outputs
        else: return original_outputs + scale * self.lora_layer(hidden_states)
class LoRACompatibleLinear(nn.Linear):
    def __init__(self, *args, lora_layer: Optional[LoRALinearLayer]=None, **kwargs):
        deprecation_message = 'Use of `LoRACompatibleLinear` is deprecated. Please switch to PEFT backend by installing PEFT: `pip install peft`.'
        deprecate('LoRACompatibleLinear', '1.0.0', deprecation_message)
        super().__init__(*args, **kwargs)
        self.lora_layer = lora_layer
    def set_lora_layer(self, lora_layer: Optional[LoRALinearLayer]):
        deprecation_message = 'Use of `set_lora_layer()` is deprecated. Please switch to PEFT backend by installing PEFT: `pip install peft`.'
        deprecate('set_lora_layer', '1.0.0', deprecation_message)
        self.lora_layer = lora_layer
    def _fuse_lora(self, lora_scale: float=1.0, safe_fusing: bool=False):
        if self.lora_layer is None: return
        dtype, device = (self.weight.data.dtype, self.weight.data.device)
        w_orig = self.weight.data.float()
        w_up = self.lora_layer.up.weight.data.float()
        w_down = self.lora_layer.down.weight.data.float()
        if self.lora_layer.network_alpha is not None: w_up = w_up * self.lora_layer.network_alpha / self.lora_layer.rank
        fused_weight = w_orig + lora_scale * torch.bmm(w_up[None, :], w_down[None, :])[0]
        if safe_fusing and torch.isnan(fused_weight).any().item(): raise ValueError(f'This LoRA weight seems to be broken. Encountered NaN values when trying to fuse LoRA weights for {self}.LoRA weights will not be fused.')
        self.weight.data = fused_weight.to(device=device, dtype=dtype)
        self.lora_layer = None
        self.w_up = w_up.cpu()
        self.w_down = w_down.cpu()
        self._lora_scale = lora_scale
    def _unfuse_lora(self):
        if not (getattr(self, 'w_up', None) is not None and getattr(self, 'w_down', None) is not None): return
        fused_weight = self.weight.data
        dtype, device = (fused_weight.dtype, fused_weight.device)
        w_up = self.w_up.to(device=device).float()
        w_down = self.w_down.to(device).float()
        unfused_weight = fused_weight.float() - self._lora_scale * torch.bmm(w_up[None, :], w_down[None, :])[0]
        self.weight.data = unfused_weight.to(device=device, dtype=dtype)
        self.w_up = None
        self.w_down = None
    def forward(self, hidden_states: torch.Tensor, scale: float=1.0) -> torch.Tensor:
        if self.lora_layer is None:
            out = super().forward(hidden_states)
            return out
        else:
            out = super().forward(hidden_states) + scale * self.lora_layer(hidden_states)
            return out
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
