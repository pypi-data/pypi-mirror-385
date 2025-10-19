"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from dataclasses import dataclass
from typing import Optional, Tuple, Union
import torch
import torch.utils.checkpoint
from torch import nn
from torch.nn import CrossEntropyLoss
from ...activations import ACT2FN
from ...generation import GenerationMixin
from ...modeling_utils import PreTrainedModel
from ...utils import (ModelOutput, add_code_sample_docstrings, add_start_docstrings, add_start_docstrings_to_model_forward, logging)
from ...utils.import_utils import is_causal_conv1d_available, is_mamba_2_ssm_available
from .configuration_mamba2 import Mamba2Config
logger = logging.get_logger(__name__)
if is_mamba_2_ssm_available():
    from mamba_ssm.ops.triton.selective_state_update import selective_state_update
    from mamba_ssm.ops.triton.ssd_combined import mamba_chunk_scan_combined, mamba_split_conv1d_scan_combined
else: selective_state_update = None
if is_causal_conv1d_available(): from causal_conv1d import causal_conv1d_fn, causal_conv1d_update
else: causal_conv1d_update, causal_conv1d_fn = None, None
is_fast_path_available = all((selective_state_update, causal_conv1d_fn, causal_conv1d_update))
_CHECKPOINT_FOR_DOC = "mistralai/mamba-codestral-7B-v0.1"
_CONFIG_FOR_DOC = "Mamba2Config"
def pad_tensor_by_size(input_tensor: torch.Tensor, pad_size: int):
    pad_shape = (0, 0, 0, 0, 0, pad_size, 0, 0) if len(input_tensor.shape) == 4 else (0, 0, 0, pad_size, 0, 0)
    return torch.nn.functional.pad(input_tensor, pad_shape, mode="constant", value=0)
def reshape_into_chunks(input_tensor, pad_size, chunk_size):
    input_tensor = pad_tensor_by_size(input_tensor, pad_size)
    if len(input_tensor.shape) == 3: return input_tensor.reshape(input_tensor.shape[0], -1, chunk_size, input_tensor.shape[2])
    else: return input_tensor.reshape(input_tensor.shape[0], -1, chunk_size, input_tensor.shape[2], input_tensor.shape[3])
def segment_sum(input_tensor):
    chunk_size = input_tensor.size(-1)
    input_tensor = input_tensor[..., None].expand(*input_tensor.size(), chunk_size)
    mask = torch.tril(torch.ones(chunk_size, chunk_size, device=input_tensor.device, dtype=torch.bool), diagonal=-1)
    input_tensor = input_tensor.masked_fill(~mask, 0)
    tensor_segsum = torch.cumsum(input_tensor, dim=-2)
    mask = torch.tril(torch.ones(chunk_size, chunk_size, device=input_tensor.device, dtype=torch.bool), diagonal=0)
    tensor_segsum = tensor_segsum.masked_fill(~mask, -torch.inf)
    return tensor_segsum
class Mamba2Cache:
    def __init__(self, config: Mamba2Config, batch_size: int, dtype: torch.dtype = torch.float16, device: Optional[str] = None):
        self.seqlen_offset = 0
        self.dtype = dtype
        self.conv_kernel_size = config.conv_kernel
        self.intermediate_size = int(config.expand * config.hidden_size)
        self.conv_states = {i: torch.zeros(batch_size, self.intermediate_size + 2 * config.n_groups * config.state_size, self.conv_kernel_size, device=device, dtype=dtype) for i in range(config.num_hidden_layers)}
        self.ssm_states = {i: torch.zeros(batch_size, config.num_heads, config.head_dim, config.state_size, device=device, dtype=dtype) for i in range(config.num_hidden_layers)}
        self.activation = config.hidden_act
        self.act = ACT2FN[config.hidden_act]
    def update_conv_state(self, layer_idx: int, new_conv_state: torch.Tensor, cache_position: torch.LongTensor) -> torch.Tensor:
        conv_state = self.conv_states[layer_idx]
        cache_position = cache_position.clamp(0, self.conv_kernel_size - 1)
        conv_state = conv_state.roll(shifts=-1, dims=-1)
        conv_state[:, :, cache_position] = new_conv_state.to(conv_state.device)
        self.conv_states[layer_idx].zero_()
        self.conv_states[layer_idx] += conv_state
        return self.conv_states[layer_idx]
    def reset(self):
        self.conv_states.zero_()
        self.ssm_states.zero_()
class MambaRMSNormGated(torch.nn.Module):
    def __init__(self, hidden_size, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size))
        self.variance_epsilon = eps
    def forward(self, hidden_states, gate=None):
        input_dtype = hidden_states.dtype
        hidden_states = hidden_states.to(torch.float32)
        if gate is not None: hidden_states = hidden_states * nn.functional.silu(gate.to(torch.float32))
        variance = hidden_states.pow(2).mean(-1, keepdim=True)
        hidden_states = hidden_states * torch.rsqrt(variance + self.variance_epsilon)
        return self.weight * hidden_states.to(input_dtype)
class Mamba2Mixer(nn.Module):
    def __init__(self, config: Mamba2Config, layer_idx: int):
        super().__init__()
        self.num_heads = config.num_heads
        self.hidden_size = config.hidden_size
        self.ssm_state_size = config.state_size
        self.conv_kernel_size = config.conv_kernel
        self.intermediate_size = int(config.expand * self.hidden_size)
        self.time_step_rank = int(config.time_step_rank)
        self.layer_idx = layer_idx
        self.use_conv_bias = config.use_conv_bias
        self.activation = config.hidden_act
        self.act = ACT2FN[config.hidden_act]
        self.layer_norm_epsilon = config.layer_norm_epsilon
        self.rms_norm = config.rms_norm
        self.n_groups = config.n_groups
        self.head_dim = config.head_dim
        self.chunk_size = config.chunk_size
        self.time_step_limit = config.time_step_limit
        self.time_step_min = config.time_step_min
        self.time_step_max = config.time_step_max
        self.conv_dim = self.intermediate_size + 2 * self.n_groups * self.ssm_state_size
        self.conv1d = nn.Conv1d(in_channels=self.conv_dim, out_channels=self.conv_dim, bias=config.use_conv_bias, kernel_size=config.conv_kernel, groups=self.conv_dim, padding=config.conv_kernel - 1)
        projection_size = self.intermediate_size + self.conv_dim + self.num_heads
        self.in_proj = nn.Linear(self.hidden_size, projection_size, bias=config.use_bias)
        self.dt_bias = nn.Parameter(torch.ones(self.num_heads))
        A = torch.arange(1, self.num_heads + 1)
        self.A_log = nn.Parameter(torch.log(A))
        self.A_log._no_weight_decay = True
        self.norm = MambaRMSNormGated(self.intermediate_size, eps=self.layer_norm_epsilon)
        self.D = nn.Parameter(torch.ones(self.num_heads))
        self.D._no_weight_decay = True
        self.out_proj = nn.Linear(self.intermediate_size, self.hidden_size, bias=config.use_bias)
        self.use_bias = config.use_bias
        if not is_fast_path_available: logger.warning_once("The fast path is not available because on of `(selective_state_update, causal_conv1d_fn, causal_conv1d_update)` is None. Falling back to the naive implementation. To install follow https://github.com/state-spaces/mamba/#installation and https://github.com/Dao-AILab/causal-conv1d")
    def cuda_kernels_forward(self, hidden_states: torch.Tensor, cache_params: Optional[Mamba2Cache] = None, cache_position: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.Tensor] = None):
        batch_size, seq_len, _ = hidden_states.shape
        groups_time_state_size = self.n_groups * self.ssm_state_size
        d_to_remove = 2 * self.intermediate_size + 2 * self.n_groups * self.ssm_state_size + self.num_heads
        if cache_params is not None and cache_params.seqlen_offset > 0:
            in_projected_states = self.in_proj(hidden_states.squeeze(1))
            d_mlp = (in_projected_states.shape[-1] - d_to_remove) // 2
            split_projection_dim = [d_mlp, d_mlp, self.intermediate_size, self.conv_dim, self.num_heads]
            _, _, gate, hidden_states_B_C, dt = torch.split(in_projected_states, split_projection_dim, dim=-1)
            hidden_states_B_C = causal_conv1d_update(hidden_states_B_C, cache_params.conv_states[self.layer_idx], self.conv1d.weight.squeeze(1), self.conv1d.bias, self.activation)
            hidden_states, B, C = torch.split(hidden_states_B_C, [self.intermediate_size, groups_time_state_size, groups_time_state_size], dim=-1)
            A = -torch.exp(self.A_log.float())
            A = A[:, None, ...][:, :, None].expand(-1, self.head_dim, self.ssm_state_size).to(dtype=torch.float32)
            dt = dt[:, :, None].expand(-1, -1, self.head_dim)
            dt_bias = self.dt_bias[:, None, ...].expand(-1, self.head_dim)
            D = self.D[:, None, ...].expand(-1, self.head_dim)
            B = B.view(batch_size, self.n_groups, B.shape[1] // self.n_groups)
            C = C.view(batch_size, self.n_groups, C.shape[1] // self.n_groups)
            hidden_states_reshaped = hidden_states.view(batch_size, self.num_heads, self.head_dim)
            hidden_states = selective_state_update(cache_params.ssm_states[self.layer_idx], hidden_states_reshaped, dt, A, B, C, D, z=None, dt_bias=dt_bias, dt_softplus=True)
            hidden_states = hidden_states.view(batch_size, self.num_heads * self.head_dim)
            hidden_states = self.norm(hidden_states, gate)
            out = self.out_proj(hidden_states)[:, None, ...]
        else:
            if attention_mask is not None and attention_mask.shape[1] > 1 and attention_mask.shape[0] > 1:
                dtype = hidden_states.dtype
                hidden_states = (hidden_states * attention_mask[:, :, None]).to(dtype)
            projected_states = self.in_proj(hidden_states)
            A = -torch.exp(self.A_log.float())
            dt_limit_kwargs = {} if self.time_step_limit == (0.0, float("inf")) else {"dt_limit": self.time_step_limit}
            if self.training and cache_params is None:
                out, ssm_state = mamba_split_conv1d_scan_combined(projected_states, self.conv1d.weight.squeeze(1), self.conv1d.bias, self.dt_bias, A, D=self.D, chunk_size=self.chunk_size,
                seq_idx=None, activation=self.activation, rmsnorm_weight=self.norm.weight, rmsnorm_eps=self.norm.variance_epsilon, outproj_weight=self.out_proj.weight,
                outproj_bias=self.out_proj.bias, headdim=self.head_dim, ngroups=self.n_groups, norm_before_gate=False, return_final_states=True, **dt_limit_kwargs)
            else:
                gate, hidden_states_B_C, time_step = torch.split(projected_states, [self.intermediate_size, self.conv_dim, self.num_heads], dim=-1)
                if causal_conv1d_fn is None or self.activation not in ["silu", "swish"]: hidden_states_B_C = self.act(self.conv1d(hidden_states_B_C.transpose(1, 2)).transpose(1, 2)[:, :seq_len])
                else: hidden_states_B_C = causal_conv1d_fn(x=hidden_states_B_C.transpose(1, 2), weight=self.conv1d.weight.squeeze(1), bias=self.conv1d.bias, activation=self.activation).transpose(1, 2)[:, :seq_len]
                hidden_states, B, C = torch.split(hidden_states_B_C, [self.intermediate_size, groups_time_state_size, groups_time_state_size], dim=-1)
                if attention_mask is not None and attention_mask.shape[1] > 1 and attention_mask.shape[0] > 1:
                    dtype = hidden_states.dtype
                    hidden_states = (hidden_states * attention_mask[:, :, None]).to(dtype)
                scan_output, ssm_state = mamba_chunk_scan_combined(hidden_states.view(batch_size, seq_len, -1, self.head_dim), time_step, A, B.view(batch_size, seq_len, self.n_groups, -1),
                C.view(batch_size, seq_len, self.n_groups, -1), chunk_size=self.chunk_size, D=self.D, z=None, seq_idx=None, return_final_states=True, dt_bias=self.dt_bias,
                dt_softplus=True, **dt_limit_kwargs)
                if ssm_state is not None and cache_params is not None: cache_params.ssm_states[self.layer_idx].copy_(ssm_state)
                scan_output = scan_output.view(batch_size, seq_len, -1)
                scan_output = self.norm(scan_output, gate)
                out = self.out_proj(scan_output)
        return out
    def torch_forward(self, input_states, cache_params: Optional[Mamba2Cache]=None, cache_position:Optional[torch.LongTensor]=None, attention_mask: Optional[torch.Tensor]=None):
        batch_size, seq_len, _ = input_states.shape
        dtype = input_states.dtype
        projected_states =  self.in_proj(input_states.squeeze(1))
        d_mlp = (projected_states.shape[-1] - 2 * self.intermediate_size -  2 * self.n_groups * self.ssm_state_size- self.num_heads) // 2
        _, _, gate, hidden_states, dt = projected_states.split([d_mlp, d_mlp, self.intermediate_size,  self.conv_dim, self.num_heads], dim=-1)
        if cache_params is not None:
            ssm_state = cache_params.ssm_states[self.layer_idx].clone()
            ssm_state = ssm_state.to(hidden_states.device)
            if cache_params.seqlen_offset > 0:
                conv_state = cache_params.conv_states[self.layer_idx]
                conv_state = torch.roll(conv_state, shifts=-1, dims=-1)
                conv_state[:, :, -1] = hidden_states[:, 0, :] if hidden_states.ndim == 3 else hidden_states
                cache_params.conv_states[self.layer_idx].copy_(conv_state)
                hidden_states = torch.sum(conv_state.to(projected_states.device) * self.conv1d.weight[:, 0, :], dim=-1)
                if self.use_conv_bias: hidden_states += self.conv1d.bias
                hidden_states = self.act(hidden_states).to(dtype)[:, None, ...]
            else:
                hidden_states = hidden_states.transpose(1,2)
                conv_state = nn.functional.pad(hidden_states, (self.conv_kernel_size - hidden_states.shape[-1], 0))
                cache_params.conv_states[self.layer_idx].copy_(conv_state)
                hidden_states = self.act(self.conv1d(hidden_states).transpose(1,2))[:, :seq_len, :]
                if attention_mask is not None and attention_mask.shape[1] > 1 and attention_mask.shape[0] > 1:
                    dtype = hidden_states.dtype
                    hidden_states = (hidden_states * attention_mask[:, :, None]).to(dtype)
        else:
            ssm_state = torch.zeros((batch_size, self.num_heads, self.head_dim, self.ssm_state_size), device=hidden_states.device, dtype=dtype)
            hidden_states = self.act(self.conv1d(hidden_states.transpose(1, 2))[..., :seq_len].transpose(1, 2))
        hidden_states, B, C = torch.split(hidden_states, [self.intermediate_size, self.n_groups * self.ssm_state_size, self.n_groups * self.ssm_state_size], dim=-1)
        A = -torch.exp(self.A_log.float())
        if cache_params is not None and cache_params.seqlen_offset > 0:
            dt = dt[:, None, ...] if dt.ndim == 2 else dt[:, 0, :][:, None, ...]
            dt = dt.transpose(1, 2).expand(batch_size, dt.shape[-1], self.head_dim)
            dt_bias = self.dt_bias[..., None].expand(self.dt_bias.shape[0], self.head_dim)
            dt = torch.nn.functional.softplus(dt + dt_bias.to(dt.dtype))
            dt = torch.clamp(dt, self.time_step_min)
            A = A[..., None, None].expand(self.num_heads, self.head_dim, self.ssm_state_size).to(dtype=torch.float32)
            dA = torch.exp(dt[..., None] * A)
            B = B.reshape(batch_size, self.n_groups, -1)[..., None, :]
            B = B.expand(batch_size, self.n_groups, self.num_heads // self.n_groups, B.shape[-1]).contiguous()
            B = B.reshape(batch_size, -1, B.shape[-1])
            dB = dt[..., None] * B[..., None, :]
            hidden_states = hidden_states.reshape(batch_size, -1, self.head_dim)
            dBx = dB * hidden_states[..., None]
            cache_params.ssm_states[self.layer_idx].copy_(cache_params.ssm_states[self.layer_idx] * dA + dBx)
            C = C.reshape(batch_size, self.n_groups, -1)[..., None, :]
            C = C.expand(batch_size, self.n_groups, self.num_heads // self.n_groups, C.shape[-1]).contiguous()
            C = C.reshape(batch_size, -1, C.shape[-1])
            ssm_states = cache_params.ssm_states[self.layer_idx].to(C.dtype)
            ssm_states_reshaped = ssm_states.view(batch_size * self.num_heads, self.head_dim, self.ssm_state_size)
            C_reshaped = C.view(batch_size * self.num_heads, self.ssm_state_size, 1)
            y = torch.bmm(ssm_states_reshaped, C_reshaped)
            y = y.view(batch_size, self.num_heads, self.head_dim)
            D = self.D[..., None].expand(self.D.shape[0], self.head_dim)
            y = (y + hidden_states * D).to(y.dtype)
            y = y.reshape(batch_size, -1)[:, None, ...]
        else:
            dt = nn.functional.softplus(dt + self.dt_bias)
            dt = torch.clamp(dt, self.time_step_min)
            hidden_states = hidden_states.reshape(batch_size, seq_len, -1, self.head_dim).float()
            B = B.reshape(batch_size, seq_len,  -1, self.ssm_state_size).float()
            C = C.reshape(batch_size, seq_len, -1, self.ssm_state_size).float()
            B = B.repeat(1, 1, self.num_heads // self.n_groups, 1)
            C = C.repeat(1, 1, self.num_heads // self.n_groups, 1)
            pad_size = (self.chunk_size - seq_len % self.chunk_size) % self.chunk_size
            D_residual = self.D[..., None] * pad_tensor_by_size(hidden_states, pad_size)
            hidden_states = hidden_states * dt[..., None]
            A = A.to(hidden_states.dtype) * dt
            hidden_states, A, B, C = [reshape_into_chunks(t, pad_size, self.chunk_size) for t in (hidden_states, A, B, C)]
            A = A.permute(0, 3, 1, 2)
            A_cumsum = torch.cumsum(A, dim=-1)
            L = torch.exp(segment_sum(A))
            G_intermediate = C[:, :, :, None, :, :] * B[:, :, None, :, : ,:]
            G = G_intermediate.sum(dim=-1)
            M_intermediate = G[..., None] * L.permute(0, 2, 3, 4, 1)[..., None]
            M = M_intermediate.sum(dim=-1)
            Y_diag = (M[..., None] * hidden_states[:, :, None]).sum(3)
            decay_states = torch.exp((A_cumsum[:, :, :, -1:] - A_cumsum))
            B_decay_contraction = B * decay_states.permute(0, 2, 3, 1)[..., None]
            states = (B_decay_contraction.permute(0, 1, 3, 2, 4)[..., None]  * hidden_states.permute(0, 1, 3, 2, 4)[..., None, :]).sum(dim=3).permute(0, 1, 2, 4, 3)
            if cache_params is not None and cache_params.seqlen_offset > 0: previous_states = cache_params.ssm_states[self.layer_idx][:, None, ...]
            else: previous_states = torch.zeros_like(states[:, :1])
            states = torch.cat([previous_states, states], dim=1)
            decay_chunk = torch.exp(segment_sum(nn.functional.pad(A_cumsum[:, :, :, -1], (1, 0))))
            states_permuted = states.permute(0, 2, 1, 3, 4)
            result = (decay_chunk[..., None, None] * states_permuted[:, :, None, ...]).sum(dim=2)
            new_states = result.permute(0, 2, 1, 3, 4)
            states, ssm_state = new_states[:, :-1], new_states[:, -1]
            state_decay_out = torch.exp(A_cumsum)
            C_times_states = (C[..., None, :] * states[:, :, None, ...])
            state_decay_out_permuted = state_decay_out.permute(0, 2, 3, 1)
            Y_off = (C_times_states.sum(-1) * state_decay_out_permuted[..., None])
            y = Y_diag + Y_off
            y = y.reshape(batch_size, -1, self.num_heads, self.head_dim)
            y = y + D_residual
            if pad_size > 0: y = y[:, :seq_len, :, :]
            y = y.reshape(batch_size, seq_len, -1)
            if ssm_state is not None and cache_params is not None: cache_params.ssm_states[self.layer_idx].copy_(ssm_state)
        scan_output = self.norm(y, gate)
        contextualized_states = self.out_proj(scan_output.to(dtype))
        return contextualized_states
    def forward(self, hidden_states, cache_params: Optional[Mamba2Cache] = None, cache_position: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.Tensor] = None):
        if is_fast_path_available and "cuda" in self.in_proj.weight.device.type: return self.cuda_kernels_forward(hidden_states, cache_params, cache_position, attention_mask)
        dtype = hidden_states.dtype
        if attention_mask is not None and attention_mask.shape[1] > 1 and attention_mask.shape[0] > 1: hidden_states = (hidden_states * attention_mask[:, :, None]).to(dtype)
        return self.torch_forward(hidden_states, cache_params, cache_position, attention_mask)
class Mamba2RMSNorm(nn.Module):
    def __init__(self, hidden_size, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size))
        self.variance_epsilon = eps
    def forward(self, hidden_states):
        input_dtype = hidden_states.dtype
        hidden_states = hidden_states.to(torch.float32)
        variance = hidden_states.pow(2).mean(-1, keepdim=True)
        hidden_states = hidden_states * torch.rsqrt(variance + self.variance_epsilon)
        return self.weight * hidden_states.to(input_dtype)
class Mamba2Block(nn.Module):
    def __init__(self, config, layer_idx):
        super().__init__()
        self.config = config
        self.layer_idx = layer_idx
        self.residual_in_fp32 = config.residual_in_fp32
        self.norm = Mamba2RMSNorm(config.hidden_size, eps=config.layer_norm_epsilon)
        self.mixer = Mamba2Mixer(config, layer_idx=layer_idx)
    def forward(self, hidden_states, cache_params: Optional[Mamba2Cache] = None, cache_position: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.Tensor] = None):
        residual = hidden_states
        hidden_states = self.norm(hidden_states.to(dtype=self.norm.weight.dtype))
        if self.residual_in_fp32: residual = residual.to(torch.float32)
        hidden_states = self.mixer(hidden_states, cache_params=cache_params, cache_position=cache_position, attention_mask=attention_mask)
        hidden_states = residual + hidden_states
        return hidden_states
class Mamba2PreTrainedModel(PreTrainedModel):
    config_class = Mamba2Config
    base_model_prefix = "backbone"
    _no_split_modules = ["Mamba2Block"]
    supports_gradient_checkpointing = True
    _is_stateful = True
    def _init_weights(self, module):
        if isinstance(module, Mamba2Mixer):
            module.A_log._no_weight_decay = True
            module.D._no_weight_decay = True
            dt = torch.exp(torch.rand(self.config.num_heads) * (math.log(self.config.time_step_max) - math.log(self.config.time_step_min)) + math.log(self.config.time_step_min)).clamp(min=self.config.time_step_floor)
            inv_dt = dt + torch.log(-torch.expm1(-dt))
            with torch.no_grad(): module.dt_bias.copy_(inv_dt)
            module.dt_bias._no_reinit = True
        if isinstance(module, nn.Linear):
            if module.bias is not None:
                if not getattr(module.bias, "_no_reinit", False): nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding): nn.init.normal_(module.weight, std=self.config.initializer_range)
        if self.config.rescale_prenorm_residual:
            for name, p in module.named_parameters():
                if name in ["out_proj.weight"]:
                    nn.init.kaiming_uniform_(p, a=math.sqrt(5))
                    with torch.no_grad(): p /= math.sqrt(self.config.num_hidden_layers)
@dataclass
class Mamba2Output(ModelOutput):
    """Args:"""
    last_hidden_state: Optional[torch.FloatTensor] = None
    cache_params: Optional[Mamba2Cache] = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
@dataclass
class Mamba2CausalLMOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    logits: Optional[torch.FloatTensor] = None
    cache_params: Optional[Mamba2Cache] = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
MAMBA2_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`Mamba2Config`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
MAMBA2_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size, input_ids_length)`):
            Indices of input sequence tokens in the vocabulary.
            If `cache_params.seqlen_offset>0`, only `input_ids` that do not have their past calculated should be passed as
            `input_ids`.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        inputs_embeds (`torch.FloatTensor` of shape `(batch_size, sequence_length, hidden_size)`, *optional*):
            Optionally, instead of passing `input_ids` you can choose to directly pass an embedded representation. This
            is useful if you want more control over how to convert `input_ids` indices into associated vectors than the
            model's internal embedding lookup matrix.
        cache_params (`Mamba2Cache`, *optional*):
            If passed along, the model uses the previous state in all the blocks (which will give the output for the
            `input_ids` provided as if the model add `state_input_ids + input_ids` as context).
        use_cache (`bool`, *optional*):
            If set to `True`, the `cache_params` is returned and can be used to quickly generate the next logits.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
@add_start_docstrings("The bare MAMBA2 Model transformer outputting raw hidden-states without any specific head on top.", MAMBA2_START_DOCSTRING)
class Mamba2Model(Mamba2PreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.embeddings = nn.Embedding(config.vocab_size, config.hidden_size)
        self.layers = nn.ModuleList([Mamba2Block(config, layer_idx=idx) for idx in range(config.num_hidden_layers)])
        self.gradient_checkpointing = False
        self.norm_f = Mamba2RMSNorm(config.hidden_size, eps=config.layer_norm_epsilon)
        self._register_load_state_dict_pre_hook(self.load_hook)
        self.post_init()
    def load_hook(self, state_dict, prefix, *args):
        for k in state_dict:
            if "embedding." in k:
                state_dict[k.replace("embedding.", "embeddings.")] = state_dict.pop(k)
                break
    def get_input_embeddings(self): return self.embeddings
    def set_input_embeddings(self, new_embeddings): self.embeddings = new_embeddings
    @add_start_docstrings_to_model_forward(MAMBA2_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, inputs_embeds: Optional[torch.LongTensor] = None, cache_params: Optional[Mamba2Cache] = None,
    use_cache: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, cache_position: Optional[torch.LongTensor] = None,
    attention_mask: Optional[torch.Tensor] = None, **kwargs) -> Union[Tuple, Mamba2Output]:
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        use_cache = use_cache if use_cache is not None else (self.config.use_cache if not self.training else False)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if (input_ids is None) ^ (inputs_embeds is not None): raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time, and must specify either one")
        if inputs_embeds is None: inputs_embeds = self.embeddings(input_ids)
        if self.gradient_checkpointing and self.training and use_cache: use_cache = False
        if use_cache:
            if cache_params is None:
                cache_params = Mamba2Cache(self.config, inputs_embeds.size(0), device=inputs_embeds.device, dtype=inputs_embeds.dtype)
                cache_position = torch.arange(0, self.config.conv_kernel, device=inputs_embeds.device)
            elif cache_position is None: raise ValueError("You have to specify the `cache_position` manually when `use_cache=True` and `cache_params` is passed, you don't have to pass a `cache_params` if you are in prefilling stage because in that case it will be initialized for you automatically")
        else: cache_params = None
        hidden_states = inputs_embeds
        all_hidden_states = () if output_hidden_states else None
        for mixer_block in self.layers:
            if self.gradient_checkpointing and self.training: hidden_states = self._gradient_checkpointing_func(mixer_block.__call__, hidden_states, cache_params, cache_position, attention_mask)
            else: hidden_states = mixer_block(hidden_states, cache_params=cache_params, cache_position=cache_position, attention_mask=attention_mask)
            if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        if use_cache: cache_params.seqlen_offset += inputs_embeds.shape[1]
        hidden_states = self.norm_f(hidden_states)
        if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, cache_params, all_hidden_states] if v is not None)
        return Mamba2Output(last_hidden_state=hidden_states, cache_params=cache_params if use_cache else None, hidden_states=all_hidden_states)
@add_start_docstrings("The MAMBA2 Model transformer with a language modeling head on top (linear layer with weights not tied to the input embeddings).", MAMBA2_START_DOCSTRING)
class Mamba2ForCausalLM(Mamba2PreTrainedModel, GenerationMixin):
    _tied_weights_keys = []
    def __init__(self, config):
        super().__init__(config)
        self.backbone = Mamba2Model(config)
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        self.post_init()
    def get_output_embeddings(self): return self.lm_head
    def set_output_embeddings(self, new_embeddings): self.lm_head = new_embeddings
    def get_input_embeddings(self): return self.backbone.get_input_embeddings()
    def set_input_embeddings(self, new_embeddings): return self.backbone.set_input_embeddings(new_embeddings)
    def prepare_inputs_for_generation(self, input_ids, inputs_embeds=None, use_cache=None, cache_params: Optional[Mamba2Cache] = None, cache_position: Optional[torch.LongTensor] = None,
    attention_mask: Optional[torch.Tensor] = None, **kwargs):
        if inputs_embeds is not None: past_len = inputs_embeds.shape[1] + input_ids.shape[1]
        else: past_len = input_ids.shape[1]
        if use_cache:
            if cache_position is None: raise ValueError("`cache_position` should not be None as it should have been initialized in `model.generate`, you are responsible for passing in a valid `cache_position` if you are calling `prepare_inputs_for_generation` directly with `use_cache=True`")
            if cache_position[0] > 0:
                input_ids = input_ids[:, -1][..., None]
                attention_mask = attention_mask[:, -1][..., None]
            else:
                cache_position = torch.arange(0, past_len, device=input_ids.device)
                extended_mask = torch.ones(attention_mask.size(0), past_len - attention_mask.shape[1], device=attention_mask.device)
                attention_mask = torch.cat([attention_mask, extended_mask], dim=1)
                cache_params = None
        if attention_mask.shape[1] < past_len:
            extended_mask = torch.ones(attention_mask.size(0), past_len - attention_mask.shape[1], device=attention_mask.device)
            attention_mask = torch.cat([attention_mask, extended_mask], dim=1)
        if inputs_embeds is not None and cache_params is None: model_inputs = {"inputs_embeds": inputs_embeds}
        else: model_inputs = {"input_ids": input_ids}
        model_inputs.update({"attention_mask": attention_mask, "cache_params": cache_params, "use_cache": use_cache, "cache_position": cache_position})
        return model_inputs
    @add_start_docstrings_to_model_forward(MAMBA2_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, inputs_embeds: Optional[torch.FloatTensor] = None, cache_params: Optional[Mamba2Cache] = None,
    labels: Optional[torch.LongTensor] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, use_cache: Optional[bool] = None,
    cache_position: Optional[torch.Tensor] = None, attention_mask: Optional[torch.Tensor] = None, **kwargs) -> Union[Tuple, Mamba2CausalLMOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        mamba2_outputs = self.backbone(input_ids, cache_params=cache_params, inputs_embeds=inputs_embeds, output_hidden_states=output_hidden_states, return_dict=return_dict,
        use_cache=use_cache, cache_position=cache_position, attention_mask=attention_mask)
        hidden_states = mamba2_outputs[0]
        logits = self.lm_head(hidden_states.to(self.lm_head.weight.dtype)).float()
        loss = None
        if labels is not None:
            labels = labels.to(logits.device)
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            loss_fct = CrossEntropyLoss()
            loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
        if not return_dict:
            output = (logits,) + mamba2_outputs[1:]
            return ((loss,) + output) if loss is not None else output
        return Mamba2CausalLMOutput(loss=loss, logits=logits, cache_params=mamba2_outputs.cache_params, hidden_states=mamba2_outputs.hidden_states)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
