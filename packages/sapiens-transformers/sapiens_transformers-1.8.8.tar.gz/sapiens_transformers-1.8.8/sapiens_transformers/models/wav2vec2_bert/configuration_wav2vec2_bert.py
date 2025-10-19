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
class Wav2Vec2BertConfig(PretrainedConfig):
    model_type = "wav2vec2-bert"
    def __init__(self, vocab_size=None, hidden_size=1024, num_hidden_layers=24, num_attention_heads=16, intermediate_size=4096, feature_projection_input_dim=160,
    hidden_act="swish", hidden_dropout=0.0, activation_dropout=0.0, attention_dropout=0.0, feat_proj_dropout=0.0, final_dropout=0.1, layerdrop=0.1, initializer_range=0.02,
    layer_norm_eps=1e-5, apply_spec_augment=True, mask_time_prob=0.05, mask_time_length=10, mask_time_min_masks=2, mask_feature_prob=0.0, mask_feature_length=10,
    mask_feature_min_masks=0, ctc_loss_reduction="sum", ctc_zero_infinity=False, use_weighted_layer_sum=False, classifier_proj_size=768, tdnn_dim=(512, 512, 512, 512, 1500),
    tdnn_kernel=(5, 3, 3, 1, 1), tdnn_dilation=(1, 2, 3, 1, 1), xvector_output_dim=512, pad_token_id=0, bos_token_id=1, eos_token_id=2, add_adapter=False, adapter_kernel_size=3,
    adapter_stride=2, num_adapter_layers=1, adapter_act="relu", use_intermediate_ffn_before_adapter=False, output_hidden_size=None, position_embeddings_type="relative_key",
    rotary_embedding_base=10000, max_source_positions=5000, left_max_position_embeddings=64, right_max_position_embeddings=8, conv_depthwise_kernel_size=31, conformer_conv_dropout=0.1, **kwargs):
        super().__init__(**kwargs, pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id)
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.intermediate_size = intermediate_size
        self.hidden_act = hidden_act
        self.num_attention_heads = num_attention_heads
        self.feature_projection_input_dim = feature_projection_input_dim
        self.hidden_dropout = hidden_dropout
        self.attention_dropout = attention_dropout
        self.activation_dropout = activation_dropout
        self.feat_proj_dropout = feat_proj_dropout
        self.final_dropout = final_dropout
        self.layerdrop = layerdrop
        self.layer_norm_eps = layer_norm_eps
        self.initializer_range = initializer_range
        self.vocab_size = vocab_size
        self.use_weighted_layer_sum = use_weighted_layer_sum
        self.max_source_positions = max_source_positions
        if position_embeddings_type is not None and position_embeddings_type not in ["rotary", "relative", "relative_key"]: raise ValueError("`position_embeddings_type` is not valid. It must be one of the following values: `['rotary', 'relative', 'relative_key']` or left as `None`.")
        self.position_embeddings_type = position_embeddings_type
        self.rotary_embedding_base = rotary_embedding_base
        self.left_max_position_embeddings = left_max_position_embeddings
        self.right_max_position_embeddings = right_max_position_embeddings
        self.conv_depthwise_kernel_size = conv_depthwise_kernel_size
        self.conformer_conv_dropout = conformer_conv_dropout
        self.apply_spec_augment = apply_spec_augment
        self.mask_time_prob = mask_time_prob
        self.mask_time_length = mask_time_length
        self.mask_time_min_masks = mask_time_min_masks
        self.mask_feature_prob = mask_feature_prob
        self.mask_feature_length = mask_feature_length
        self.mask_feature_min_masks = mask_feature_min_masks
        self.ctc_loss_reduction = ctc_loss_reduction
        self.ctc_zero_infinity = ctc_zero_infinity
        self.add_adapter = add_adapter
        self.adapter_kernel_size = adapter_kernel_size
        self.adapter_stride = adapter_stride
        self.num_adapter_layers = num_adapter_layers
        self.adapter_act = adapter_act
        self.output_hidden_size = output_hidden_size if output_hidden_size is not None else hidden_size
        if use_intermediate_ffn_before_adapter and not add_adapter: raise ValueError("`use_intermediate_ffn_before_adapter` is `True` but `add_adapter` is `False`.")
        self.use_intermediate_ffn_before_adapter = use_intermediate_ffn_before_adapter
        self.classifier_proj_size = classifier_proj_size
        self.tdnn_dim = list(tdnn_dim)
        self.tdnn_kernel = list(tdnn_kernel)
        self.tdnn_dilation = list(tdnn_dilation)
        self.xvector_output_dim = xvector_output_dim
    @property
    def inputs_to_logits_ratio(self):
        ratio = self.feature_projection_input_dim * 2
        if self.add_adapter: ratio = ratio * (self.adapter_stride**self.num_adapter_layers)
        return ratio
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
