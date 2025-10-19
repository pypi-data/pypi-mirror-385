'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..utils.import_utils import is_torch_npu_available, is_torch_version
import torch.nn.functional as F
from ..utils import deprecate
from torch import nn
import torch
if is_torch_npu_available(): import torch_npu
ACTIVATION_FUNCTIONS = {'swish': nn.SiLU(), 'silu': nn.SiLU(), 'mish': nn.Mish(), 'gelu': nn.GELU(), 'relu': nn.ReLU()}
def get_activation(act_fn: str) -> nn.Module:
    """Returns:"""
    act_fn = act_fn.lower()
    if act_fn in ACTIVATION_FUNCTIONS: return ACTIVATION_FUNCTIONS[act_fn]
    else: raise ValueError(f'Unsupported activation function: {act_fn}')
class FP32SiLU(nn.Module):
    def __init__(self): super().__init__()
    def forward(self, inputs: torch.Tensor) -> torch.Tensor: return F.silu(inputs.float(), inplace=False).to(inputs.dtype)
class GELU(nn.Module):
    def __init__(self, dim_in: int, dim_out: int, approximate: str='none', bias: bool=True):
        super().__init__()
        self.proj = nn.Linear(dim_in, dim_out, bias=bias)
        self.approximate = approximate
    def gelu(self, gate: torch.Tensor) -> torch.Tensor:
        if gate.device.type == 'mps' and is_torch_version('<', '2.0.0'): return F.gelu(gate.to(dtype=torch.float32), approximate=self.approximate).to(dtype=gate.dtype)
        return F.gelu(gate, approximate=self.approximate)
    def forward(self, hidden_states):
        hidden_states = self.proj(hidden_states)
        hidden_states = self.gelu(hidden_states)
        return hidden_states
class GEGLU(nn.Module):
    def __init__(self, dim_in: int, dim_out: int, bias: bool=True):
        super().__init__()
        self.proj = nn.Linear(dim_in, dim_out * 2, bias=bias)
    def gelu(self, gate: torch.Tensor) -> torch.Tensor:
        if gate.device.type == 'mps' and is_torch_version('<', '2.0.0'): return F.gelu(gate.to(dtype=torch.float32)).to(dtype=gate.dtype)
        return F.gelu(gate)
    def forward(self, hidden_states, *args, **kwargs):
        if len(args) > 0 or kwargs.get('scale', None) is not None:
            deprecation_message = 'The `scale` argument is deprecated and will be ignored. Please remove it, as passing it will raise an error in the future. `scale` should directly be passed while calling the underlying pipeline component i.e., via `cross_attention_kwargs`.'
            deprecate('scale', '1.0.0', deprecation_message)
        hidden_states = self.proj(hidden_states)
        if is_torch_npu_available(): return torch_npu.npu_geglu(hidden_states, dim=-1, approximate=1)[0]
        else:
            hidden_states, gate = hidden_states.chunk(2, dim=-1)
            return hidden_states * self.gelu(gate)
class SwiGLU(nn.Module):
    def __init__(self, dim_in: int, dim_out: int, bias: bool=True):
        super().__init__()
        self.proj = nn.Linear(dim_in, dim_out * 2, bias=bias)
        self.activation = nn.SiLU()
    def forward(self, hidden_states):
        hidden_states = self.proj(hidden_states)
        hidden_states, gate = hidden_states.chunk(2, dim=-1)
        return hidden_states * self.activation(gate)
class ApproximateGELU(nn.Module):
    def __init__(self, dim_in: int, dim_out: int, bias: bool=True):
        super().__init__()
        self.proj = nn.Linear(dim_in, dim_out, bias=bias)
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.proj(x)
        return x * torch.sigmoid(1.702 * x)
class LinearActivation(nn.Module):
    def __init__(self, dim_in: int, dim_out: int, bias: bool=True, activation: str='silu'):
        super().__init__()
        self.proj = nn.Linear(dim_in, dim_out, bias=bias)
        self.activation = get_activation(activation)
    def forward(self, hidden_states):
        hidden_states = self.proj(hidden_states)
        return self.activation(hidden_states)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
