"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PretrainedConfig
from ...utils import logging
from ..auto import CONFIG_MAPPING
logger = logging.get_logger(__name__)
class Qwen2AudioEncoderConfig(PretrainedConfig):
    model_type = "qwen2_audio_encoder"
    def __init__(self, num_mel_bins=128, encoder_layers=32, encoder_attention_heads=20, encoder_ffn_dim=5120, encoder_layerdrop=0.0, d_model=1280, dropout=0.0,
    attention_dropout=0.0, activation_function="gelu", activation_dropout=0.0, scale_embedding=False, init_std=0.02, max_source_positions=1500, **kwargs):
        super().__init__(**kwargs)
        self.num_mel_bins = num_mel_bins
        self.d_model = d_model
        self.encoder_layers = encoder_layers
        self.encoder_attention_heads = encoder_attention_heads
        self.encoder_ffn_dim = encoder_ffn_dim
        self.dropout = dropout
        self.attention_dropout = attention_dropout
        self.activation_function = activation_function
        self.activation_dropout = activation_dropout
        self.encoder_layerdrop = encoder_layerdrop
        self.num_hidden_layers = encoder_layers
        self.init_std = init_std
        self.scale_embedding = scale_embedding
        self.max_source_positions = max_source_positions
class Qwen2AudioConfig(PretrainedConfig):
    model_type = "qwen2_audio"
    is_composition = False
    def __init__(self, audio_config=None, text_config=None, audio_token_index=151646, **kwargs):
        self.audio_token_index = audio_token_index
        if isinstance(audio_config, dict):
            audio_config["model_type"] = (audio_config["model_type"] if "model_type" in audio_config else "qwen2_audio_encoder")
            audio_config = CONFIG_MAPPING[audio_config["model_type"]](**audio_config)
        elif audio_config is None: audio_config = CONFIG_MAPPING["qwen2_audio_encoder"](d_model=1280, encoder_attention_heads=20, encoder_ffn_dim=5120, encoder_layerdrop=0.0, encoder_layers=32,
        num_mel_bins=128, max_source_positions=1500, scale_embedding=False, activation_function="gelu")
        self.audio_config = audio_config
        if isinstance(text_config, dict):
            text_config["model_type"] = text_config["model_type"] if "model_type" in text_config else "qwen2"
            text_config = CONFIG_MAPPING[text_config["model_type"]](**text_config)
        elif text_config is None: text_config = CONFIG_MAPPING["qwen2"]()
        self.text_config = text_config
        super().__init__(**kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
