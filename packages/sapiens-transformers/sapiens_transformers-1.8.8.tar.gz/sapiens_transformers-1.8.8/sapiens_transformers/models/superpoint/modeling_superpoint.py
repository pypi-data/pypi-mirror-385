"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from dataclasses import dataclass
from typing import Optional, Tuple, Union
import torch
from torch import nn
from sapiens_transformers import PreTrainedModel
from sapiens_transformers.modeling_outputs import (BaseModelOutputWithNoAttention)
from sapiens_transformers.models.superpoint.configuration_superpoint import SuperPointConfig
from ...pytorch_utils import is_torch_greater_or_equal_than_1_13
from ...utils import (ModelOutput, add_start_docstrings, add_start_docstrings_to_model_forward, logging)
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "SuperPointConfig"
_CHECKPOINT_FOR_DOC = "magic-leap-community/superpoint"
def remove_keypoints_from_borders(keypoints: torch.Tensor, scores: torch.Tensor, border: int, height: int, width: int) -> Tuple[torch.Tensor, torch.Tensor]:
    mask_h = (keypoints[:, 0] >= border) & (keypoints[:, 0] < (height - border))
    mask_w = (keypoints[:, 1] >= border) & (keypoints[:, 1] < (width - border))
    mask = mask_h & mask_w
    return keypoints[mask], scores[mask]
def top_k_keypoints(keypoints: torch.Tensor, scores: torch.Tensor, k: int) -> Tuple[torch.Tensor, torch.Tensor]:
    if k >= len(keypoints): return keypoints, scores
    scores, indices = torch.topk(scores, k, dim=0)
    return keypoints[indices], scores
def simple_nms(scores: torch.Tensor, nms_radius: int) -> torch.Tensor:
    if nms_radius < 0: raise ValueError("Expected positive values for nms_radius")
    def max_pool(x): return nn.functional.max_pool2d(x, kernel_size=nms_radius * 2 + 1, stride=1, padding=nms_radius)
    zeros = torch.zeros_like(scores)
    max_mask = scores == max_pool(scores)
    for _ in range(2):
        supp_mask = max_pool(max_mask.float()) > 0
        supp_scores = torch.where(supp_mask, zeros, scores)
        new_max_mask = supp_scores == max_pool(supp_scores)
        max_mask = max_mask | (new_max_mask & (~supp_mask))
    return torch.where(max_mask, scores, zeros)
@dataclass
class SuperPointKeypointDescriptionOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    keypoints: Optional[torch.IntTensor] = None
    scores: Optional[torch.FloatTensor] = None
    descriptors: Optional[torch.FloatTensor] = None
    mask: Optional[torch.BoolTensor] = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
class SuperPointConvBlock(nn.Module):
    def __init__(self, config: SuperPointConfig, in_channels: int, out_channels: int, add_pooling: bool = False) -> None:
        super().__init__()
        self.conv_a = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=1, padding=1)
        self.conv_b = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1)
        self.relu = nn.ReLU(inplace=True)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2) if add_pooling else None
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.relu(self.conv_a(hidden_states))
        hidden_states = self.relu(self.conv_b(hidden_states))
        if self.pool is not None: hidden_states = self.pool(hidden_states)
        return hidden_states
class SuperPointEncoder(nn.Module):
    def __init__(self, config: SuperPointConfig) -> None:
        super().__init__()
        self.input_dim = 1
        conv_blocks = []
        conv_blocks.append(SuperPointConvBlock(config, self.input_dim, config.encoder_hidden_sizes[0], add_pooling=True))
        for i in range(1, len(config.encoder_hidden_sizes) - 1): conv_blocks.append(SuperPointConvBlock(config, config.encoder_hidden_sizes[i - 1], config.encoder_hidden_sizes[i], add_pooling=True))
        conv_blocks.append(SuperPointConvBlock(config, config.encoder_hidden_sizes[-2], config.encoder_hidden_sizes[-1], add_pooling=False))
        self.conv_blocks = nn.ModuleList(conv_blocks)
    def forward(self, input, output_hidden_states: Optional[bool] = False, return_dict: Optional[bool] = True) -> Union[Tuple, BaseModelOutputWithNoAttention]:
        all_hidden_states = () if output_hidden_states else None
        for conv_block in self.conv_blocks:
            input = conv_block(input)
            if output_hidden_states: all_hidden_states = all_hidden_states + (input,)
        output = input
        if not return_dict: return tuple(v for v in [output, all_hidden_states] if v is not None)
        return BaseModelOutputWithNoAttention(last_hidden_state=output, hidden_states=all_hidden_states)
class SuperPointInterestPointDecoder(nn.Module):
    def __init__(self, config: SuperPointConfig) -> None:
        super().__init__()
        self.keypoint_threshold = config.keypoint_threshold
        self.max_keypoints = config.max_keypoints
        self.nms_radius = config.nms_radius
        self.border_removal_distance = config.border_removal_distance
        self.relu = nn.ReLU(inplace=True)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv_score_a = nn.Conv2d(config.encoder_hidden_sizes[-1], config.decoder_hidden_size, kernel_size=3, stride=1, padding=1)
        self.conv_score_b = nn.Conv2d(config.decoder_hidden_size, config.keypoint_decoder_dim, kernel_size=1, stride=1, padding=0)
    def forward(self, encoded: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        scores = self._get_pixel_scores(encoded)
        keypoints, scores = self._extract_keypoints(scores)
        return keypoints, scores
    def _get_pixel_scores(self, encoded: torch.Tensor) -> torch.Tensor:
        scores = self.relu(self.conv_score_a(encoded))
        scores = self.conv_score_b(scores)
        scores = nn.functional.softmax(scores, 1)[:, :-1]
        batch_size, _, height, width = scores.shape
        scores = scores.permute(0, 2, 3, 1).reshape(batch_size, height, width, 8, 8)
        scores = scores.permute(0, 1, 3, 2, 4).reshape(batch_size, height * 8, width * 8)
        scores = simple_nms(scores, self.nms_radius)
        return scores
    def _extract_keypoints(self, scores: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        _, height, width = scores.shape
        keypoints = torch.nonzero(scores[0] > self.keypoint_threshold)
        scores = scores[0][tuple(keypoints.t())]
        keypoints, scores = remove_keypoints_from_borders(keypoints, scores, self.border_removal_distance, height * 8, width * 8)
        if self.max_keypoints >= 0: keypoints, scores = top_k_keypoints(keypoints, scores, self.max_keypoints)
        keypoints = torch.flip(keypoints, [1]).float()
        return keypoints, scores
class SuperPointDescriptorDecoder(nn.Module):
    def __init__(self, config: SuperPointConfig) -> None:
        super().__init__()
        self.relu = nn.ReLU(inplace=True)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv_descriptor_a = nn.Conv2d(config.encoder_hidden_sizes[-1], config.decoder_hidden_size, kernel_size=3, stride=1, padding=1)
        self.conv_descriptor_b = nn.Conv2d(config.decoder_hidden_size, config.descriptor_decoder_dim, kernel_size=1, stride=1, padding=0)
    def forward(self, encoded: torch.Tensor, keypoints: torch.Tensor) -> torch.Tensor:
        descriptors = self.conv_descriptor_b(self.relu(self.conv_descriptor_a(encoded)))
        descriptors = nn.functional.normalize(descriptors, p=2, dim=1)
        descriptors = self._sample_descriptors(keypoints[None], descriptors[0][None], 8)[0]
        descriptors = torch.transpose(descriptors, 0, 1)
        return descriptors
    @staticmethod
    def _sample_descriptors(keypoints, descriptors, scale: int = 8) -> torch.Tensor:
        batch_size, num_channels, height, width = descriptors.shape
        keypoints = keypoints - scale / 2 + 0.5
        divisor = torch.tensor([[(width * scale - scale / 2 - 0.5), (height * scale - scale / 2 - 0.5)]])
        divisor = divisor.to(keypoints)
        keypoints /= divisor
        keypoints = keypoints * 2 - 1
        kwargs = {"align_corners": True} if is_torch_greater_or_equal_than_1_13 else {}
        keypoints = keypoints.view(batch_size, 1, -1, 2)
        descriptors = nn.functional.grid_sample(descriptors, keypoints, mode="bilinear", **kwargs)
        descriptors = descriptors.reshape(batch_size, num_channels, -1)
        descriptors = nn.functional.normalize(descriptors, p=2, dim=1)
        return descriptors
class SuperPointPreTrainedModel(PreTrainedModel):
    config_class = SuperPointConfig
    base_model_prefix = "superpoint"
    main_input_name = "pixel_values"
    supports_gradient_checkpointing = False
    def _init_weights(self, module: Union[nn.Linear, nn.Conv2d, nn.LayerNorm]) -> None:
        if isinstance(module, (nn.Linear, nn.Conv2d)):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
    def extract_one_channel_pixel_values(self, pixel_values: torch.FloatTensor) -> torch.FloatTensor: return pixel_values[:, 0, :, :][:, None, :, :]
SUPERPOINT_START_DOCSTRING = r"""
    This model is a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass. Use it
    as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage and
    behavior.
    Parameters:
        config ([`SuperPointConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
    """
SUPERPOINT_INPUTS_DOCSTRING = r"""
Args:
    pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`):
        Pixel values. Pixel values can be obtained using [`SuperPointImageProcessor`]. See
        [`SuperPointImageProcessor.__call__`] for details.
    output_hidden_states (`bool`, *optional*):
        Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for more
        detail.
    return_dict (`bool`, *optional*):
        Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
    """
@add_start_docstrings("SuperPoint model outputting keypoints and descriptors.", SUPERPOINT_START_DOCSTRING)
class SuperPointForKeypointDetection(SuperPointPreTrainedModel):
    def __init__(self, config: SuperPointConfig) -> None:
        super().__init__(config)
        self.config = config
        self.encoder = SuperPointEncoder(config)
        self.keypoint_decoder = SuperPointInterestPointDecoder(config)
        self.descriptor_decoder = SuperPointDescriptorDecoder(config)
        self.post_init()
    @add_start_docstrings_to_model_forward(SUPERPOINT_INPUTS_DOCSTRING)
    def forward(self, pixel_values: torch.FloatTensor, labels: Optional[torch.LongTensor] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple, SuperPointKeypointDescriptionOutput]:
        loss = None
        if labels is not None: raise ValueError("SuperPoint does not support training for now.")
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        pixel_values = self.extract_one_channel_pixel_values(pixel_values)
        batch_size = pixel_values.shape[0]
        encoder_outputs = self.encoder(pixel_values, output_hidden_states=output_hidden_states, return_dict=return_dict)
        last_hidden_state = encoder_outputs[0]
        list_keypoints_scores = [self.keypoint_decoder(last_hidden_state[None, ...]) for last_hidden_state in last_hidden_state]
        list_keypoints = [keypoints_scores[0] for keypoints_scores in list_keypoints_scores]
        list_scores = [keypoints_scores[1] for keypoints_scores in list_keypoints_scores]
        list_descriptors = [self.descriptor_decoder(last_hidden_state[None, ...], keypoints[None, ...]) for last_hidden_state, keypoints in zip(last_hidden_state, list_keypoints)]
        maximum_num_keypoints = max(keypoints.shape[0] for keypoints in list_keypoints)
        keypoints = torch.zeros((batch_size, maximum_num_keypoints, 2), device=pixel_values.device)
        scores = torch.zeros((batch_size, maximum_num_keypoints), device=pixel_values.device)
        descriptors = torch.zeros((batch_size, maximum_num_keypoints, self.config.descriptor_decoder_dim), device=pixel_values.device)
        mask = torch.zeros((batch_size, maximum_num_keypoints), device=pixel_values.device, dtype=torch.int)
        for i, (_keypoints, _scores, _descriptors) in enumerate(zip(list_keypoints, list_scores, list_descriptors)):
            keypoints[i, : _keypoints.shape[0]] = _keypoints
            scores[i, : _scores.shape[0]] = _scores
            descriptors[i, : _descriptors.shape[0]] = _descriptors
            mask[i, : _scores.shape[0]] = 1
        hidden_states = encoder_outputs[1] if output_hidden_states else None
        if not return_dict: return tuple(v for v in [loss, keypoints, scores, descriptors, mask, hidden_states] if v is not None)
        return SuperPointKeypointDescriptionOutput(loss=loss, keypoints=keypoints, scores=scores, descriptors=descriptors, mask=mask, hidden_states=hidden_states)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
