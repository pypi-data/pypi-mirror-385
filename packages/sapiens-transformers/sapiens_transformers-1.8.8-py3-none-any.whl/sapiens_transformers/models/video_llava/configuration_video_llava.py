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
class VideoLlavaConfig(PretrainedConfig):
    model_type = "video_llava"
    is_composition = False
    def __init__(self, vision_config=None, text_config=None, ignore_index=-100, image_token_index=32000, video_token_index=32001, projector_hidden_act="gelu",
    vision_feature_select_strategy="default", vision_feature_layer=-2, image_seq_length=256, video_seq_length=2056, **kwargs):
        self.ignore_index = ignore_index
        self.image_token_index = image_token_index
        self.video_token_index = video_token_index
        self.projector_hidden_act = projector_hidden_act
        self.vision_feature_select_strategy = vision_feature_select_strategy
        self.vision_feature_layer = vision_feature_layer
        self.image_seq_length = image_seq_length
        self.video_seq_length = video_seq_length
        self.vision_config = vision_config
        if isinstance(self.vision_config, dict):
            if "model_type" not in vision_config:
                vision_config["model_type"] = "clip_vision_model"
                logger.warning("Key=`model_type` not found in vision config, setting it to `clip_vision_model`")
            self.vision_config = CONFIG_MAPPING[vision_config["model_type"]](**vision_config)
        elif vision_config is None: self.vision_config = CONFIG_MAPPING["clip_vision_model"](intermediate_size=4096, hidden_size=1024, patch_size=14, image_size=224,
        num_hidden_layers=24, num_attention_heads=16, vocab_size=32000, projection_dim=768)
        if isinstance(text_config, dict):
            if "model_type" not in text_config:
                text_config["model_type"] = "llama"
                logger.warning("Key=`model_type` not found in text config, setting it to `llama`")
            text_config = CONFIG_MAPPING[text_config["model_type"]](**text_config)
        elif text_config is None: text_config = CONFIG_MAPPING["llama"]()
        self.text_config = text_config
        super().__init__(**kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
