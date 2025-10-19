"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class TimesformerConfig(PretrainedConfig):
    model_type = "timesformer"
    def __init__(self, image_size=224, patch_size=16, num_channels=3, num_frames=8, hidden_size=768, num_hidden_layers=12, num_attention_heads=12, intermediate_size=3072,
    hidden_act="gelu", hidden_dropout_prob=0.0, attention_probs_dropout_prob=0.0, initializer_range=0.02, layer_norm_eps=1e-6, qkv_bias=True, attention_type="divided_space_time",
    drop_path_rate=0, **kwargs):
        super().__init__(**kwargs)
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.num_frames = num_frames
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.intermediate_size = intermediate_size
        self.hidden_act = hidden_act
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.qkv_bias = qkv_bias
        self.attention_type = attention_type
        self.drop_path_rate = drop_path_rate
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
