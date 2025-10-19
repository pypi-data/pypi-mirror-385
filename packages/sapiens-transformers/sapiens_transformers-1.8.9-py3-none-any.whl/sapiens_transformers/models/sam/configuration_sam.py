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
class SamPromptEncoderConfig(PretrainedConfig):
    def __init__(self, hidden_size=256, image_size=1024, patch_size=16, mask_input_channels=16, num_point_embeddings=4, hidden_act="gelu", layer_norm_eps=1e-6, **kwargs):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.image_size = image_size
        self.patch_size = patch_size
        self.image_embedding_size = image_size // patch_size
        self.mask_input_channels = mask_input_channels
        self.num_point_embeddings = num_point_embeddings
        self.hidden_act = hidden_act
        self.layer_norm_eps = layer_norm_eps
class SamMaskDecoderConfig(PretrainedConfig):
    def __init__(self, hidden_size=256, hidden_act="relu", mlp_dim=2048, num_hidden_layers=2, num_attention_heads=8, attention_downsample_rate=2, num_multimask_outputs=3,
    iou_head_depth=3, iou_head_hidden_dim=256, layer_norm_eps=1e-6, **kwargs):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.hidden_act = hidden_act
        self.mlp_dim = mlp_dim
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.attention_downsample_rate = attention_downsample_rate
        self.num_multimask_outputs = num_multimask_outputs
        self.iou_head_depth = iou_head_depth
        self.iou_head_hidden_dim = iou_head_hidden_dim
        self.layer_norm_eps = layer_norm_eps
class SamVisionConfig(PretrainedConfig):
    def __init__(self, hidden_size=768, output_channels=256, num_hidden_layers=12, num_attention_heads=12, num_channels=3, image_size=1024, patch_size=16, hidden_act="gelu",
    layer_norm_eps=1e-06, attention_dropout=0.0, initializer_range=1e-10, qkv_bias=True, mlp_ratio=4.0, use_abs_pos=True, use_rel_pos=True, window_size=14, global_attn_indexes=[2, 5, 8, 11],
    num_pos_feats=128, mlp_dim=None, **kwargs):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.output_channels = output_channels
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.num_channels = num_channels
        self.image_size = image_size
        self.patch_size = patch_size
        self.hidden_act = hidden_act
        self.layer_norm_eps = layer_norm_eps
        self.attention_dropout = attention_dropout
        self.initializer_range = initializer_range
        self.qkv_bias = qkv_bias
        self.mlp_ratio = mlp_ratio
        self.use_abs_pos = use_abs_pos
        self.use_rel_pos = use_rel_pos
        self.window_size = window_size
        self.global_attn_indexes = global_attn_indexes
        self.num_pos_feats = num_pos_feats
        self.mlp_dim = int(hidden_size * mlp_ratio) if mlp_dim is None else mlp_dim
class SamConfig(PretrainedConfig):
    model_type = "sam"
    def __init__(self, vision_config=None, prompt_encoder_config=None, mask_decoder_config=None, initializer_range=0.02, **kwargs):
        super().__init__(**kwargs)
        vision_config = vision_config if vision_config is not None else {}
        prompt_encoder_config = prompt_encoder_config if prompt_encoder_config is not None else {}
        mask_decoder_config = mask_decoder_config if mask_decoder_config is not None else {}
        if isinstance(vision_config, SamVisionConfig): vision_config = vision_config.to_dict()
        if isinstance(prompt_encoder_config, SamPromptEncoderConfig): prompt_encoder_config = prompt_encoder_config.to_dict()
        if isinstance(mask_decoder_config, SamMaskDecoderConfig): mask_decoder_config = mask_decoder_config.to_dict()
        self.vision_config = SamVisionConfig(**vision_config)
        self.prompt_encoder_config = SamPromptEncoderConfig(**prompt_encoder_config)
        self.mask_decoder_config = SamMaskDecoderConfig(**mask_decoder_config)
        self.initializer_range = initializer_range
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
