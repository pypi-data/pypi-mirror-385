"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from collections import OrderedDict
from typing import TYPE_CHECKING, Any, Mapping, Optional, Union
if TYPE_CHECKING:
    from ...processing_utils import ProcessorMixin
    from ...utils import TensorType
from ...configuration_utils import PretrainedConfig
from ...onnx import OnnxConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class ChineseCLIPTextConfig(PretrainedConfig):
    model_type = "chinese_clip_text_model"
    def __init__(self, vocab_size=30522, hidden_size=768, num_hidden_layers=12, num_attention_heads=12, intermediate_size=3072, hidden_act="gelu", hidden_dropout_prob=0.1,
    attention_probs_dropout_prob=0.1, max_position_embeddings=512, type_vocab_size=2, initializer_range=0.02, initializer_factor=1.0, layer_norm_eps=1e-12, pad_token_id=0,
    position_embedding_type="absolute", use_cache=True, **kwargs):
        super().__init__(pad_token_id=pad_token_id, **kwargs)
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.hidden_act = hidden_act
        self.intermediate_size = intermediate_size
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.max_position_embeddings = max_position_embeddings
        self.type_vocab_size = type_vocab_size
        self.initializer_range = initializer_range
        self.initializer_factor = initializer_factor
        self.layer_norm_eps = layer_norm_eps
        self.position_embedding_type = position_embedding_type
        self.use_cache = use_cache
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "chinese_clip": config_dict = config_dict["text_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class ChineseCLIPVisionConfig(PretrainedConfig):
    model_type = "chinese_clip_vision_model"
    def __init__(self, hidden_size=768, intermediate_size=3072, projection_dim=512, num_hidden_layers=12, num_attention_heads=12, num_channels=3, image_size=224,
    patch_size=32, hidden_act="quick_gelu", layer_norm_eps=1e-5, attention_dropout=0.0, initializer_range=0.02, initializer_factor=1.0, **kwargs):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.projection_dim = projection_dim
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.num_channels = num_channels
        self.patch_size = patch_size
        self.image_size = image_size
        self.initializer_range = initializer_range
        self.initializer_factor = initializer_factor
        self.attention_dropout = attention_dropout
        self.layer_norm_eps = layer_norm_eps
        self.hidden_act = hidden_act
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "chinese_clip": config_dict = config_dict["vision_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class ChineseCLIPConfig(PretrainedConfig):
    model_type = "chinese_clip"
    def __init__(self, text_config=None, vision_config=None, projection_dim=512, logit_scale_init_value=2.6592, **kwargs):
        text_config_dict = kwargs.pop("text_config_dict", None)
        vision_config_dict = kwargs.pop("vision_config_dict", None)
        super().__init__(**kwargs)
        if text_config_dict is not None:
            if text_config is None: text_config = {}
            _text_config_dict = ChineseCLIPTextConfig(**text_config_dict).to_dict()
            for key, value in _text_config_dict.items():
                if key in text_config and value != text_config[key] and key not in ["sapiens_transformers_version"]:
                    if key in text_config_dict: message = (f"`{key}` is found in both `text_config_dict` and `text_config` but with different values. "+f'The value `text_config_dict["{key}"]` will be used instead.')
                    else: message = (f"`text_config_dict` is provided which will be used to initialize `ChineseCLIPTextConfig`. "+f'The value `text_config["{key}"]` will be overridden.')
                    logger.info(message)
            text_config.update(_text_config_dict)
        if vision_config_dict is not None:
            if vision_config is None: vision_config = {}
            _vision_config_dict = ChineseCLIPVisionConfig(**vision_config_dict).to_dict()
            if "id2label" in _vision_config_dict: _vision_config_dict["id2label"] = {str(key): value for key, value in _vision_config_dict["id2label"].items()}
            for key, value in _vision_config_dict.items():
                if key in vision_config and value != vision_config[key] and key not in ["sapiens_transformers_version"]:
                    if key in vision_config_dict: message = (f"`{key}` is found in both `vision_config_dict` and `vision_config` but with different "+f'values. The value `vision_config_dict["{key}"]` will be used instead.')
                    else: message = (f"`vision_config_dict` is provided which will be used to initialize "+f'`ChineseCLIPVisionConfig`. The value `vision_config["{key}"]` will be overridden.')
                    logger.info(message)
            vision_config.update(_vision_config_dict)
        if text_config is None:
            text_config = {}
            logger.info("`text_config` is `None`. Initializing the `ChineseCLIPTextConfig` with default values.")
        if vision_config is None:
            vision_config = {}
            logger.info("`vision_config` is `None`. initializing the `ChineseCLIPVisionConfig` with default values.")
        self.text_config = ChineseCLIPTextConfig(**text_config)
        self.vision_config = ChineseCLIPVisionConfig(**vision_config)
        self.projection_dim = projection_dim
        self.logit_scale_init_value = logit_scale_init_value
        self.initializer_factor = 1.0
        self.initializer_range = 0.02
    @classmethod
    def from_text_vision_configs(cls, text_config: ChineseCLIPTextConfig, vision_config: ChineseCLIPVisionConfig, **kwargs): return cls(text_config=text_config.to_dict(), vision_config=vision_config.to_dict(), **kwargs)
class ChineseCLIPOnnxConfig(OnnxConfig):
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]: return OrderedDict([("input_ids", {0: "batch", 1: "sequence"}), ("pixel_values", {0: "batch", 1: "num_channels", 2: "height", 3: "width"}), ("attention_mask", {0: "batch", 1: "sequence"})])
    @property
    def outputs(self) -> Mapping[str, Mapping[int, str]]: return OrderedDict([("logits_per_image", {0: "batch"}), ("logits_per_text", {0: "batch"}), ("text_embeds", {0: "batch"}), ("image_embeds", {0: "batch"})])
    @property
    def atol_for_validation(self) -> float: return 1e-4
    def generate_dummy_inputs(self, processor: "ProcessorMixin", batch_size: int = -1, seq_length: int = -1, framework: Optional["TensorType"] = None) -> Mapping[str, Any]:
        text_input_dict = super().generate_dummy_inputs(processor.tokenizer, batch_size=batch_size, seq_length=seq_length, framework=framework)
        image_input_dict = super().generate_dummy_inputs(processor.image_processor, batch_size=batch_size, framework=framework)
        return {**text_input_dict, **image_input_dict}
    @property
    def default_onnx_opset(self) -> int: return 14
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
