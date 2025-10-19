"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union
import torch
import torch.utils.checkpoint
from torch import nn
from ...activations import ACT2FN
from ...file_utils import (add_start_docstrings, add_start_docstrings_to_model_forward, replace_return_docstrings)
from ...modeling_outputs import DepthEstimatorOutput
from ...modeling_utils import PreTrainedModel
from ...utils import ModelOutput, logging
from ...utils.backbone_utils import load_backbone
from .configuration_zoedepth import ZoeDepthConfig
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "ZoeDepthConfig"
@dataclass
class ZoeDepthDepthEstimatorOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    predicted_depth: torch.FloatTensor = None
    domain_logits: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[Tuple[torch.FloatTensor, ...]] = None
class ZoeDepthReassembleStage(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.readout_type = config.readout_type
        self.layers = nn.ModuleList()
        for neck_hidden_size, factor in zip(config.neck_hidden_sizes, config.reassemble_factors): self.layers.append(ZoeDepthReassembleLayer(config, channels=neck_hidden_size, factor=factor))
        if config.readout_type == "project":
            self.readout_projects = nn.ModuleList()
            hidden_size = config.backbone_hidden_size
            for _ in config.neck_hidden_sizes: self.readout_projects.append(nn.Sequential(nn.Linear(2 * hidden_size, hidden_size), ACT2FN[config.hidden_act]))
    def forward(self, hidden_states: List[torch.Tensor], patch_height, patch_width) -> List[torch.Tensor]:
        batch_size = hidden_states[0].shape[0]
        hidden_states = torch.cat(hidden_states, dim=0)
        cls_token, hidden_states = hidden_states[:, 0], hidden_states[:, 1:]
        total_batch_size, sequence_length, num_channels = hidden_states.shape
        hidden_states = hidden_states.reshape(total_batch_size, patch_height, patch_width, num_channels)
        hidden_states = hidden_states.permute(0, 3, 1, 2).contiguous()
        if self.readout_type == "project":
            hidden_states = hidden_states.flatten(2).permute((0, 2, 1))
            readout = cls_token.unsqueeze(dim=1).expand_as(hidden_states)
            hidden_states = torch.cat((hidden_states, readout), -1)
        elif self.readout_type == "add": hidden_states = hidden_states + cls_token.unsqueeze(-1)
        out = []
        for stage_idx, hidden_state in enumerate(hidden_states.split(batch_size, dim=0)):
            if self.readout_type == "project": hidden_state = self.readout_projects[stage_idx](hidden_state)
            hidden_state = hidden_state.permute(0, 2, 1).reshape(batch_size, -1, patch_height, patch_width)
            hidden_state = self.layers[stage_idx](hidden_state)
            out.append(hidden_state)
        return out
class ZoeDepthReassembleLayer(nn.Module):
    def __init__(self, config, channels, factor):
        super().__init__()
        hidden_size = config.backbone_hidden_size
        self.projection = nn.Conv2d(in_channels=hidden_size, out_channels=channels, kernel_size=1)
        if factor > 1: self.resize = nn.ConvTranspose2d(channels, channels, kernel_size=factor, stride=factor, padding=0)
        elif factor == 1: self.resize = nn.Identity()
        elif factor < 1: self.resize = nn.Conv2d(channels, channels, kernel_size=3, stride=int(1 / factor), padding=1)
    def forward(self, hidden_state):
        hidden_state = self.projection(hidden_state)
        hidden_state = self.resize(hidden_state)
        return hidden_state
class ZoeDepthFeatureFusionStage(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.layers = nn.ModuleList()
        for _ in range(len(config.neck_hidden_sizes)): self.layers.append(ZoeDepthFeatureFusionLayer(config))
    def forward(self, hidden_states):
        hidden_states = hidden_states[::-1]
        fused_hidden_states = []
        fused_hidden_state = self.layers[0](hidden_states[0])
        fused_hidden_states.append(fused_hidden_state)
        for hidden_state, layer in zip(hidden_states[1:], self.layers[1:]):
            fused_hidden_state = layer(fused_hidden_state, hidden_state)
            fused_hidden_states.append(fused_hidden_state)
        return fused_hidden_states
class ZoeDepthPreActResidualLayer(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.use_batch_norm = config.use_batch_norm_in_fusion_residual
        use_bias_in_fusion_residual = (config.use_bias_in_fusion_residual if config.use_bias_in_fusion_residual is not None else not self.use_batch_norm)
        self.activation1 = nn.ReLU()
        self.convolution1 = nn.Conv2d(config.fusion_hidden_size, config.fusion_hidden_size, kernel_size=3, stride=1, padding=1, bias=use_bias_in_fusion_residual)
        self.activation2 = nn.ReLU()
        self.convolution2 = nn.Conv2d(config.fusion_hidden_size, config.fusion_hidden_size, kernel_size=3, stride=1, padding=1, bias=use_bias_in_fusion_residual)
        if self.use_batch_norm:
            self.batch_norm1 = nn.BatchNorm2d(config.fusion_hidden_size, eps=config.batch_norm_eps)
            self.batch_norm2 = nn.BatchNorm2d(config.fusion_hidden_size, eps=config.batch_norm_eps)
    def forward(self, hidden_state: torch.Tensor) -> torch.Tensor:
        residual = hidden_state
        hidden_state = self.activation1(hidden_state)
        hidden_state = self.convolution1(hidden_state)
        if self.use_batch_norm: hidden_state = self.batch_norm1(hidden_state)
        hidden_state = self.activation2(hidden_state)
        hidden_state = self.convolution2(hidden_state)
        if self.use_batch_norm: hidden_state = self.batch_norm2(hidden_state)
        return hidden_state + residual
class ZoeDepthFeatureFusionLayer(nn.Module):
    def __init__(self, config, align_corners=True):
        super().__init__()
        self.align_corners = align_corners
        self.projection = nn.Conv2d(config.fusion_hidden_size, config.fusion_hidden_size, kernel_size=1, bias=True)
        self.residual_layer1 = ZoeDepthPreActResidualLayer(config)
        self.residual_layer2 = ZoeDepthPreActResidualLayer(config)
    def forward(self, hidden_state, residual=None):
        if residual is not None:
            if hidden_state.shape != residual.shape: residual = nn.functional.interpolate(residual, size=(hidden_state.shape[2], hidden_state.shape[3]), mode="bilinear", align_corners=False)
            hidden_state = hidden_state + self.residual_layer1(residual)
        hidden_state = self.residual_layer2(hidden_state)
        hidden_state = nn.functional.interpolate(hidden_state, scale_factor=2, mode="bilinear", align_corners=self.align_corners)
        hidden_state = self.projection(hidden_state)
        return hidden_state
class ZoeDepthNeck(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        if config.backbone_config is not None and config.backbone_config.model_type in ["swinv2"]: self.reassemble_stage = None
        else: self.reassemble_stage = ZoeDepthReassembleStage(config)
        self.convs = nn.ModuleList()
        for channel in config.neck_hidden_sizes: self.convs.append(nn.Conv2d(channel, config.fusion_hidden_size, kernel_size=3, padding=1, bias=False))
        self.fusion_stage = ZoeDepthFeatureFusionStage(config)
    def forward(self, hidden_states: List[torch.Tensor], patch_height, patch_width) -> List[torch.Tensor]:
        if not isinstance(hidden_states, (tuple, list)): raise TypeError("hidden_states should be a tuple or list of tensors")
        if len(hidden_states) != len(self.config.neck_hidden_sizes): raise ValueError("The number of hidden states should be equal to the number of neck hidden sizes.")
        if self.reassemble_stage is not None: hidden_states = self.reassemble_stage(hidden_states, patch_height, patch_width)
        features = [self.convs[i](feature) for i, feature in enumerate(hidden_states)]
        output = self.fusion_stage(features)
        return output, features[-1]
class ZoeDepthRelativeDepthEstimationHead(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.head_in_index = config.head_in_index
        self.projection = None
        if config.add_projection: self.projection = nn.Conv2d(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        features = config.fusion_hidden_size
        self.conv1 = nn.Conv2d(features, features // 2, kernel_size=3, stride=1, padding=1)
        self.upsample = nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True)
        self.conv2 = nn.Conv2d(features // 2, config.num_relative_features, kernel_size=3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(config.num_relative_features, 1, kernel_size=1, stride=1, padding=0)
    def forward(self, hidden_states: List[torch.Tensor]) -> torch.Tensor:
        hidden_states = hidden_states[self.head_in_index]
        if self.projection is not None:
            hidden_states = self.projection(hidden_states)
            hidden_states = nn.ReLU()(hidden_states)
        hidden_states = self.conv1(hidden_states)
        hidden_states = self.upsample(hidden_states)
        hidden_states = self.conv2(hidden_states)
        hidden_states = nn.ReLU()(hidden_states)
        features = hidden_states
        hidden_states = self.conv3(hidden_states)
        hidden_states = nn.ReLU()(hidden_states)
        predicted_depth = hidden_states.squeeze(dim=1)
        return predicted_depth, features
def log_binom(n, k, eps=1e-7):
    n = n + eps
    k = k + eps
    return n * torch.log(n) - k * torch.log(k) - (n - k) * torch.log(n - k + eps)
class LogBinomialSoftmax(nn.Module):
    def __init__(self, n_classes=256, act=torch.softmax):
        super().__init__()
        self.k = n_classes
        self.act = act
        self.register_buffer("k_idx", torch.arange(0, n_classes).view(1, -1, 1, 1), persistent=False)
        self.register_buffer("k_minus_1", torch.Tensor([self.k - 1]).view(1, -1, 1, 1), persistent=False)
    def forward(self, probabilities, temperature=1.0, eps=1e-4):
        if probabilities.ndim == 3: probabilities = probabilities.unsqueeze(1)
        one_minus_probabilities = torch.clamp(1 - probabilities, eps, 1)
        probabilities = torch.clamp(probabilities, eps, 1)
        y = (log_binom(self.k_minus_1, self.k_idx) + self.k_idx * torch.log(probabilities) + (self.k_minus_1 - self.k_idx) * torch.log(one_minus_probabilities))
        return self.act(y / temperature, dim=1)
class ZoeDepthConditionalLogBinomialSoftmax(nn.Module):
    def __init__(self, config, in_features, condition_dim, n_classes=256, bottleneck_factor=2):
        super().__init__()
        bottleneck = (in_features + condition_dim) // bottleneck_factor
        self.mlp = nn.Sequential(nn.Conv2d(in_features + condition_dim, bottleneck, kernel_size=1, stride=1, padding=0), nn.GELU(), nn.Conv2d(bottleneck, 2 + 2, kernel_size=1, stride=1, padding=0), nn.Softplus())
        self.p_eps = 1e-4
        self.max_temp = config.max_temp
        self.min_temp = config.min_temp
        self.log_binomial_transform = LogBinomialSoftmax(n_classes, act=torch.softmax)
    def forward(self, main_feature, condition_feature):
        probabilities_and_temperature = self.mlp(torch.concat((main_feature, condition_feature), dim=1))
        probabilities, temperature = (probabilities_and_temperature[:, :2, ...], probabilities_and_temperature[:, 2:, ...])
        probabilities = probabilities + self.p_eps
        probabilities = probabilities[:, 0, ...] / (probabilities[:, 0, ...] + probabilities[:, 1, ...])
        temperature = temperature + self.p_eps
        temperature = temperature[:, 0, ...] / (temperature[:, 0, ...] + temperature[:, 1, ...])
        temperature = temperature.unsqueeze(1)
        temperature = (self.max_temp - self.min_temp) * temperature + self.min_temp
        return self.log_binomial_transform(probabilities, temperature)
class ZoeDepthSeedBinRegressor(nn.Module):
    def __init__(self, config, n_bins=16, mlp_dim=256, min_depth=1e-3, max_depth=10):
        super().__init__()
        self.in_features = config.bottleneck_features
        self.bin_centers_type = config.bin_centers_type
        self.min_depth = min_depth
        self.max_depth = max_depth
        self.conv1 = nn.Conv2d(self.in_features, mlp_dim, 1, 1, 0)
        self.act1 = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(mlp_dim, n_bins, 1, 1, 0)
        self.act2 = nn.ReLU(inplace=True) if self.bin_centers_type == "normed" else nn.Softplus()
    def forward(self, x):
        x = self.conv1(x)
        x = self.act1(x)
        x = self.conv2(x)
        bin_centers = self.act2(x)
        if self.bin_centers_type == "normed":
            bin_centers = bin_centers + 1e-3
            bin_widths_normed = bin_centers / bin_centers.sum(dim=1, keepdim=True)
            bin_widths = (self.max_depth - self.min_depth) * bin_widths_normed
            bin_widths = nn.functional.pad(bin_widths, (0, 0, 0, 0, 1, 0), mode="constant", value=self.min_depth)
            bin_edges = torch.cumsum(bin_widths, dim=1)
            bin_centers = 0.5 * (bin_edges[:, :-1, ...] + bin_edges[:, 1:, ...])
            return bin_widths_normed, bin_centers
        else: return bin_centers, bin_centers
@torch.jit.script
def inv_attractor(dx, alpha: float = 300, gamma: int = 2): return dx.div(1 + alpha * dx.pow(gamma))
class ZoeDepthAttractorLayer(nn.Module):
    def __init__(self, config, n_bins, n_attractors=16, min_depth=1e-3, max_depth=10, memory_efficient=False):
        super().__init__()
        self.alpha = config.attractor_alpha
        self.gemma = config.attractor_gamma
        self.kind = config.attractor_kind
        self.n_attractors = n_attractors
        self.n_bins = n_bins
        self.min_depth = min_depth
        self.max_depth = max_depth
        self.memory_efficient = memory_efficient
        in_features = mlp_dim = config.bin_embedding_dim
        self.conv1 = nn.Conv2d(in_features, mlp_dim, 1, 1, 0)
        self.act1 = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(mlp_dim, n_attractors * 2, 1, 1, 0)
        self.act2 = nn.ReLU(inplace=True)
    def forward(self, x, prev_bin, prev_bin_embedding=None, interpolate=True):
        if prev_bin_embedding is not None:
            if interpolate: prev_bin_embedding = nn.functional.interpolate(prev_bin_embedding, x.shape[-2:], mode="bilinear", align_corners=True)
            x = x + prev_bin_embedding
        x = self.conv1(x)
        x = self.act1(x)
        x = self.conv2(x)
        attractors = self.act2(x)
        attractors = attractors + 1e-3
        batch_size, _, height, width = attractors.shape
        attractors = attractors.view(batch_size, self.n_attractors, 2, height, width)
        attractors_normed = attractors[:, :, 0, ...]
        bin_centers = nn.functional.interpolate(prev_bin, (height, width), mode="bilinear", align_corners=True)
        if not self.memory_efficient:
            func = {"mean": torch.mean, "sum": torch.sum}[self.kind]
            delta_c = func(inv_attractor(attractors_normed.unsqueeze(2) - bin_centers.unsqueeze(1)), dim=1)
        else:
            delta_c = torch.zeros_like(bin_centers, device=bin_centers.device)
            for i in range(self.n_attractors): delta_c += inv_attractor(attractors_normed[:, i, ...].unsqueeze(1) - bin_centers)
            if self.kind == "mean": delta_c = delta_c / self.n_attractors
        bin_new_centers = bin_centers + delta_c
        bin_centers = (self.max_depth - self.min_depth) * bin_new_centers + self.min_depth
        bin_centers, _ = torch.sort(bin_centers, dim=1)
        bin_centers = torch.clip(bin_centers, self.min_depth, self.max_depth)
        return bin_new_centers, bin_centers
class ZoeDepthAttractorLayerUnnormed(nn.Module):
    def __init__(self, config, n_bins, n_attractors=16, min_depth=1e-3, max_depth=10, memory_efficient=True):
        super().__init__()
        self.n_attractors = n_attractors
        self.n_bins = n_bins
        self.min_depth = min_depth
        self.max_depth = max_depth
        self.alpha = config.attractor_alpha
        self.gamma = config.attractor_alpha
        self.kind = config.attractor_kind
        self.memory_efficient = memory_efficient
        in_features = mlp_dim = config.bin_embedding_dim
        self.conv1 = nn.Conv2d(in_features, mlp_dim, 1, 1, 0)
        self.act1 = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(mlp_dim, n_attractors, 1, 1, 0)
        self.act2 = nn.Softplus()
    def forward(self, x, prev_bin, prev_bin_embedding=None, interpolate=True):
        if prev_bin_embedding is not None:
            if interpolate: prev_bin_embedding = nn.functional.interpolate(prev_bin_embedding, x.shape[-2:], mode="bilinear", align_corners=True)
            x = x + prev_bin_embedding
        x = self.conv1(x)
        x = self.act1(x)
        x = self.conv2(x)
        attractors = self.act2(x)
        height, width = attractors.shape[-2:]
        bin_centers = nn.functional.interpolate(prev_bin, (height, width), mode="bilinear", align_corners=True)
        if not self.memory_efficient:
            func = {"mean": torch.mean, "sum": torch.sum}[self.kind]
            delta_c = func(inv_attractor(attractors.unsqueeze(2) - bin_centers.unsqueeze(1)), dim=1)
        else:
            delta_c = torch.zeros_like(bin_centers, device=bin_centers.device)
            for i in range(self.n_attractors): delta_c += inv_attractor(attractors[:, i, ...].unsqueeze(1) - bin_centers)
            if self.kind == "mean": delta_c = delta_c / self.n_attractors
        bin_new_centers = bin_centers + delta_c
        bin_centers = bin_new_centers
        return bin_new_centers, bin_centers
class ZoeDepthProjector(nn.Module):
    def __init__(self, in_features, out_features, mlp_dim=128):
        super().__init__()
        self.conv1 = nn.Conv2d(in_features, mlp_dim, 1, 1, 0)
        self.act = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(mlp_dim, out_features, 1, 1, 0)
    def forward(self, hidden_state: torch.Tensor) -> torch.Tensor:
        hidden_state = self.conv1(hidden_state)
        hidden_state = self.act(hidden_state)
        hidden_state = self.conv2(hidden_state)
        return hidden_state
class ZoeDepthMultiheadAttention(nn.Module):
    def __init__(self, hidden_size, num_attention_heads, dropout):
        super().__init__()
        if hidden_size % num_attention_heads != 0: raise ValueError(f"The hidden size ({hidden_size}) is not a multiple of the number of attention heads ({num_attention_heads})")
        self.num_attention_heads = num_attention_heads
        self.attention_head_size = int(hidden_size / num_attention_heads)
        self.all_head_size = self.num_attention_heads * self.attention_head_size
        self.query = nn.Linear(hidden_size, self.all_head_size)
        self.key = nn.Linear(hidden_size, self.all_head_size)
        self.value = nn.Linear(hidden_size, self.all_head_size)
        self.out_proj = nn.Linear(hidden_size, hidden_size)
        self.dropout = nn.Dropout(dropout)
    def transpose_for_scores(self, x: torch.Tensor) -> torch.Tensor:
        new_x_shape = x.size()[:-1] + (self.num_attention_heads, self.attention_head_size)
        x = x.view(new_x_shape)
        return x.permute(0, 2, 1, 3)
    def forward(self, queries: torch.Tensor, keys: torch.Tensor, values: torch.Tensor, attention_mask: Optional[torch.FloatTensor] = None, output_attentions: Optional[bool] = False) -> Tuple[torch.Tensor]:
        query_layer = self.transpose_for_scores(self.query(queries))
        key_layer = self.transpose_for_scores(self.key(keys))
        value_layer = self.transpose_for_scores(self.value(values))
        attention_scores = torch.matmul(query_layer, key_layer.transpose(-1, -2))
        attention_scores = attention_scores / math.sqrt(self.attention_head_size)
        if attention_mask is not None: attention_scores = attention_scores + attention_mask
        attention_probs = nn.functional.softmax(attention_scores, dim=-1)
        attention_probs = self.dropout(attention_probs)
        context_layer = torch.matmul(attention_probs, value_layer)
        context_layer = context_layer.permute(0, 2, 1, 3).contiguous()
        new_context_layer_shape = context_layer.size()[:-2] + (self.all_head_size,)
        context_layer = context_layer.view(new_context_layer_shape)
        context_layer = self.out_proj(context_layer)
        outputs = (context_layer, attention_probs) if output_attentions else (context_layer,)
        return outputs
class ZoeDepthTransformerEncoderLayer(nn.Module):
    def __init__(self, config, dropout=0.1, activation="relu"):
        super().__init__()
        hidden_size = config.patch_transformer_hidden_size
        intermediate_size = config.patch_transformer_intermediate_size
        num_attention_heads = config.patch_transformer_num_attention_heads
        self.self_attn = ZoeDepthMultiheadAttention(hidden_size, num_attention_heads, dropout=dropout)
        self.linear1 = nn.Linear(hidden_size, intermediate_size)
        self.dropout = nn.Dropout(dropout)
        self.linear2 = nn.Linear(intermediate_size, hidden_size)
        self.norm1 = nn.LayerNorm(hidden_size)
        self.norm2 = nn.LayerNorm(hidden_size)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
        self.activation = ACT2FN[activation]
    def forward(self, src, src_mask: Optional[torch.Tensor] = None):
        queries = keys = src
        src2 = self.self_attn(queries=queries, keys=keys, values=src, attention_mask=src_mask)[0]
        src = src + self.dropout1(src2)
        src = self.norm1(src)
        src2 = self.linear2(self.dropout(self.activation(self.linear1(src))))
        src = src + self.dropout2(src2)
        src = self.norm2(src)
        return src
class ZoeDepthPatchTransformerEncoder(nn.Module):
    def __init__(self, config):
        super().__init__()
        in_channels = config.bottleneck_features
        self.transformer_encoder = nn.ModuleList([ZoeDepthTransformerEncoderLayer(config) for _ in range(config.num_patch_transformer_layers)])
        self.embedding_convPxP = nn.Conv2d(in_channels, config.patch_transformer_hidden_size, kernel_size=1, stride=1, padding=0)
    def positional_encoding_1d(self, batch_size, sequence_length, embedding_dim, device="cpu", dtype=torch.float32):
        position = torch.arange(0, sequence_length, dtype=dtype, device=device).unsqueeze(1)
        index = torch.arange(0, embedding_dim, 2, dtype=dtype, device=device).unsqueeze(0)
        div_term = torch.exp(index * (-torch.log(torch.tensor(10000.0, device=device)) / embedding_dim))
        pos_encoding = position * div_term
        pos_encoding = torch.cat([torch.sin(pos_encoding), torch.cos(pos_encoding)], dim=1)
        pos_encoding = pos_encoding.unsqueeze(dim=0).repeat(batch_size, 1, 1)
        return pos_encoding
    def forward(self, x):
        embeddings = self.embedding_convPxP(x).flatten(2)
        embeddings = nn.functional.pad(embeddings, (1, 0))
        embeddings = embeddings.permute(0, 2, 1)
        batch_size, sequence_length, embedding_dim = embeddings.shape
        embeddings = embeddings + self.positional_encoding_1d(batch_size, sequence_length, embedding_dim, device=embeddings.device, dtype=embeddings.dtype)
        for i in range(4): embeddings = self.transformer_encoder[i](embeddings)
        return embeddings
class ZoeDepthMLPClassifier(nn.Module):
    def __init__(self, in_features, out_features) -> None:
        super().__init__()
        hidden_features = in_features
        self.linear1 = nn.Linear(in_features, hidden_features)
        self.activation = nn.ReLU()
        self.linear2 = nn.Linear(hidden_features, out_features)
    def forward(self, hidden_state):
        hidden_state = self.linear1(hidden_state)
        hidden_state = self.activation(hidden_state)
        domain_logits = self.linear2(hidden_state)
        return domain_logits
class ZoeDepthMultipleMetricDepthEstimationHeads(nn.Module):
    def __init__(self, config):
        super().__init__()
        bin_embedding_dim = config.bin_embedding_dim
        n_attractors = config.num_attractors
        self.bin_configurations = config.bin_configurations
        self.bin_centers_type = config.bin_centers_type
        bottleneck_features = config.bottleneck_features
        self.conv2 = nn.Conv2d(bottleneck_features, bottleneck_features, kernel_size=1, stride=1, padding=0)
        self.patch_transformer = ZoeDepthPatchTransformerEncoder(config)
        self.mlp_classifier = ZoeDepthMLPClassifier(in_features=128, out_features=2)
        if self.bin_centers_type == "normed": Attractor = ZoeDepthAttractorLayer
        elif self.bin_centers_type == "softplus": Attractor = ZoeDepthAttractorLayerUnnormed
        self.seed_bin_regressors = nn.ModuleDict({conf["name"]: ZoeDepthSeedBinRegressor(config, n_bins=conf["n_bins"], mlp_dim=bin_embedding_dim // 2, min_depth=conf["min_depth"],
        max_depth=conf["max_depth"]) for conf in config.bin_configurations})
        self.seed_projector = ZoeDepthProjector(in_features=bottleneck_features, out_features=bin_embedding_dim, mlp_dim=bin_embedding_dim // 2)
        self.projectors = nn.ModuleList([ZoeDepthProjector(in_features=config.fusion_hidden_size, out_features=bin_embedding_dim, mlp_dim=bin_embedding_dim // 2) for _ in range(4)])
        self.attractors = nn.ModuleDict({configuration["name"]: nn.ModuleList([Attractor(config, n_bins=n_attractors[i], min_depth=configuration["min_depth"],
        max_depth=configuration["max_depth"]) for i in range(len(n_attractors))]) for configuration in config.bin_configurations})
        last_in = config.num_relative_features
        self.conditional_log_binomial = nn.ModuleDict({configuration["name"]: ZoeDepthConditionalLogBinomialSoftmax(config, last_in, bin_embedding_dim, configuration["n_bins"], bottleneck_factor=4) for configuration in config.bin_configurations})
    def forward(self, outconv_activation, bottleneck, feature_blocks, relative_depth):
        x = self.conv2(bottleneck)
        embedding = self.patch_transformer(x)[:, 0, :]
        domain_logits = self.mlp_classifier(embedding)
        domain_vote = torch.softmax(domain_logits.sum(dim=0, keepdim=True), dim=-1)
        names = [configuration["name"] for configuration in self.bin_configurations]
        bin_configurations_name = names[torch.argmax(domain_vote, dim=-1).squeeze().item()]
        try: conf = [config for config in self.bin_configurations if config["name"] == bin_configurations_name][0]
        except IndexError: raise ValueError(f"bin_configurations_name {bin_configurations_name} not found in bin_configurationss")
        min_depth = conf["min_depth"]
        max_depth = conf["max_depth"]
        seed_bin_regressor = self.seed_bin_regressors[bin_configurations_name]
        _, seed_bin_centers = seed_bin_regressor(x)
        if self.bin_centers_type in ["normed", "hybrid2"]: prev_bin = (seed_bin_centers - min_depth) / (max_depth - min_depth)
        else: prev_bin = seed_bin_centers
        prev_bin_embedding = self.seed_projector(x)
        attractors = self.attractors[bin_configurations_name]
        for projector, attractor, feature in zip(self.projectors, attractors, feature_blocks):
            bin_embedding = projector(feature)
            bin, bin_centers = attractor(bin_embedding, prev_bin, prev_bin_embedding, interpolate=True)
            prev_bin = bin
            prev_bin_embedding = bin_embedding
        last = outconv_activation
        bin_centers = nn.functional.interpolate(bin_centers, last.shape[-2:], mode="bilinear", align_corners=True)
        bin_embedding = nn.functional.interpolate(bin_embedding, last.shape[-2:], mode="bilinear", align_corners=True)
        conditional_log_binomial = self.conditional_log_binomial[bin_configurations_name]
        x = conditional_log_binomial(last, bin_embedding)
        out = torch.sum(x * bin_centers, dim=1, keepdim=True)
        return out, domain_logits
class ZoeDepthMetricDepthEstimationHead(nn.Module):
    def __init__(self, config):
        super().__init__()
        bin_configuration = config.bin_configurations[0]
        n_bins = bin_configuration["n_bins"]
        min_depth = bin_configuration["min_depth"]
        max_depth = bin_configuration["max_depth"]
        bin_embedding_dim = config.bin_embedding_dim
        n_attractors = config.num_attractors
        bin_centers_type = config.bin_centers_type
        self.min_depth = min_depth
        self.max_depth = max_depth
        self.bin_centers_type = bin_centers_type
        bottleneck_features = config.bottleneck_features
        self.conv2 = nn.Conv2d(bottleneck_features, bottleneck_features, kernel_size=1, stride=1, padding=0)
        if self.bin_centers_type == "normed": Attractor = ZoeDepthAttractorLayer
        elif self.bin_centers_type == "softplus": Attractor = ZoeDepthAttractorLayerUnnormed
        self.seed_bin_regressor = ZoeDepthSeedBinRegressor(config, n_bins=n_bins, min_depth=min_depth, max_depth=max_depth)
        self.seed_projector = ZoeDepthProjector(in_features=bottleneck_features, out_features=bin_embedding_dim)
        self.projectors = nn.ModuleList([ZoeDepthProjector(in_features=config.fusion_hidden_size, out_features=bin_embedding_dim) for _ in range(4)])
        self.attractors = nn.ModuleList([Attractor(config, n_bins=n_bins, n_attractors=n_attractors[i], min_depth=min_depth, max_depth=max_depth) for i in range(4)])
        last_in = config.num_relative_features + 1
        self.conditional_log_binomial = ZoeDepthConditionalLogBinomialSoftmax(config, last_in, bin_embedding_dim, n_classes=n_bins)
    def forward(self, outconv_activation, bottleneck, feature_blocks, relative_depth):
        x = self.conv2(bottleneck)
        _, seed_bin_centers = self.seed_bin_regressor(x)
        if self.bin_centers_type in ["normed", "hybrid2"]: prev_bin = (seed_bin_centers - self.min_depth) / (self.max_depth - self.min_depth)
        else: prev_bin = seed_bin_centers
        prev_bin_embedding = self.seed_projector(x)
        for projector, attractor, feature in zip(self.projectors, self.attractors, feature_blocks):
            bin_embedding = projector(feature)
            bin, bin_centers = attractor(bin_embedding, prev_bin, prev_bin_embedding, interpolate=True)
            prev_bin = bin.clone()
            prev_bin_embedding = bin_embedding.clone()
        last = outconv_activation
        relative_conditioning = relative_depth.unsqueeze(1)
        relative_conditioning = nn.functional.interpolate(relative_conditioning, size=last.shape[2:], mode="bilinear", align_corners=True)
        last = torch.cat([last, relative_conditioning], dim=1)
        bin_embedding = nn.functional.interpolate(bin_embedding, last.shape[-2:], mode="bilinear", align_corners=True)
        x = self.conditional_log_binomial(last, bin_embedding)
        bin_centers = nn.functional.interpolate(bin_centers, x.shape[-2:], mode="bilinear", align_corners=True)
        out = torch.sum(x * bin_centers, dim=1, keepdim=True)
        return out, None
class ZoeDepthPreTrainedModel(PreTrainedModel):
    config_class = ZoeDepthConfig
    base_model_prefix = "zoedepth"
    main_input_name = "pixel_values"
    supports_gradient_checkpointing = True
    def _init_weights(self, module):
        if isinstance(module, (nn.Linear, nn.Conv2d, nn.ConvTranspose2d)):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
ZOEDEPTH_START_DOCSTRING = r"""
    This model is a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass. Use it
    as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage and
    behavior.
    Parameters:
        config ([`ViTConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
ZOEDEPTH_INPUTS_DOCSTRING = r"""
    Args:
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`):
            Pixel values. Pixel values can be obtained using [`AutoImageProcessor`]. See [`DPTImageProcessor.__call__`]
            for details.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~file_utils.ModelOutput`] instead of a plain tuple.
"""
@add_start_docstrings("ZoeDepth model with one or multiple metric depth estimation head(s) on top.", ZOEDEPTH_START_DOCSTRING)
class ZoeDepthForDepthEstimation(ZoeDepthPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.backbone = load_backbone(config)
        if hasattr(self.backbone.config, "hidden_size") and hasattr(self.backbone.config, "patch_size"):
            config.backbone_hidden_size = self.backbone.config.hidden_size
            self.patch_size = self.backbone.config.patch_size
        else: raise ValueError("ZoeDepth assumes the backbone's config to have `hidden_size` and `patch_size` attributes")
        self.neck = ZoeDepthNeck(config)
        self.relative_head = ZoeDepthRelativeDepthEstimationHead(config)
        self.metric_head = (ZoeDepthMultipleMetricDepthEstimationHeads(config) if len(config.bin_configurations) > 1 else ZoeDepthMetricDepthEstimationHead(config))
        self.post_init()
    @add_start_docstrings_to_model_forward(ZOEDEPTH_INPUTS_DOCSTRING)
    def forward(self, pixel_values: torch.FloatTensor, labels: Optional[torch.LongTensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple[torch.Tensor], DepthEstimatorOutput]:
        loss = None
        if labels is not None: raise NotImplementedError("Training is not implemented yet")
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        outputs = self.backbone.forward_with_filtered_kwargs(pixel_values, output_hidden_states=output_hidden_states, output_attentions=output_attentions)
        hidden_states = outputs.feature_maps
        _, _, height, width = pixel_values.shape
        patch_size = self.patch_size
        patch_height = height // patch_size
        patch_width = width // patch_size
        hidden_states, features = self.neck(hidden_states, patch_height, patch_width)
        out = [features] + hidden_states
        relative_depth, features = self.relative_head(hidden_states)
        out = [features] + out
        metric_depth, domain_logits = self.metric_head(outconv_activation=out[0], bottleneck=out[1], feature_blocks=out[2:], relative_depth=relative_depth)
        metric_depth = metric_depth.squeeze(dim=1)
        if not return_dict:
            if domain_logits is not None: output = (metric_depth, domain_logits) + outputs[1:]
            else: output = (metric_depth,) + outputs[1:]
            return ((loss,) + output) if loss is not None else output
        return ZoeDepthDepthEstimatorOutput(loss=loss, predicted_depth=metric_depth, domain_logits=domain_logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
