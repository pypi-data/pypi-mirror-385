"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import functools
import operator
from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class WavLMConfig(PretrainedConfig):
    model_type = "wavlm"
    def __init__(self, vocab_size=32, hidden_size=768, num_hidden_layers=12, num_attention_heads=12, intermediate_size=3072, hidden_act="gelu", hidden_dropout=0.1,
    activation_dropout=0.1, attention_dropout=0.1, feat_proj_dropout=0.0, final_dropout=0.1, layerdrop=0.1, initializer_range=0.02, layer_norm_eps=1e-5, feat_extract_norm="group",
    feat_extract_activation="gelu", conv_dim=(512, 512, 512, 512, 512, 512, 512), conv_stride=(5, 2, 2, 2, 2, 2, 2), conv_kernel=(10, 3, 3, 3, 3, 2, 2), conv_bias=False,
    num_conv_pos_embeddings=128, num_conv_pos_embedding_groups=16, num_buckets=320, max_bucket_distance=800, do_stable_layer_norm=False, apply_spec_augment=True,
    mask_time_prob=0.05, mask_time_length=10, mask_time_min_masks=2, mask_feature_prob=0.0, mask_feature_length=10, num_codevectors_per_group=320, num_codevector_groups=2,
    contrastive_logits_temperature=0.1, num_negatives=100, codevector_dim=256, proj_codevector_dim=256, diversity_loss_weight=0.1, ctc_loss_reduction="mean",
    ctc_zero_infinity=False, use_weighted_layer_sum=False, classifier_proj_size=256, tdnn_dim=(512, 512, 512, 512, 1500), tdnn_kernel=(5, 3, 3, 1, 1), tdnn_dilation=(1, 2, 3, 1, 1),
    xvector_output_dim=512, num_ctc_classes=80, pad_token_id=0, bos_token_id=1, eos_token_id=2, add_adapter=False, adapter_kernel_size=3, adapter_stride=2, num_adapter_layers=3,
    output_hidden_size=None, **kwargs):
        super().__init__(**kwargs, pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id)
        self.hidden_size = hidden_size
        self.feat_extract_norm = feat_extract_norm
        self.feat_extract_activation = feat_extract_activation
        self.conv_dim = list(conv_dim)
        self.conv_stride = list(conv_stride)
        self.conv_kernel = list(conv_kernel)
        self.conv_bias = conv_bias
        self.num_buckets = num_buckets
        self.max_bucket_distance = max_bucket_distance
        self.num_conv_pos_embeddings = num_conv_pos_embeddings
        self.num_conv_pos_embedding_groups = num_conv_pos_embedding_groups
        self.num_feat_extract_layers = len(self.conv_dim)
        self.num_hidden_layers = num_hidden_layers
        self.intermediate_size = intermediate_size
        self.hidden_act = hidden_act
        self.num_attention_heads = num_attention_heads
        self.hidden_dropout = hidden_dropout
        self.attention_dropout = attention_dropout
        self.activation_dropout = activation_dropout
        self.feat_proj_dropout = feat_proj_dropout
        self.final_dropout = final_dropout
        self.layerdrop = layerdrop
        self.layer_norm_eps = layer_norm_eps
        self.initializer_range = initializer_range
        self.num_ctc_classes = num_ctc_classes
        self.vocab_size = vocab_size
        self.do_stable_layer_norm = do_stable_layer_norm
        self.use_weighted_layer_sum = use_weighted_layer_sum
        self.classifier_proj_size = classifier_proj_size
        if ((len(self.conv_stride) != self.num_feat_extract_layers) or (len(self.conv_kernel) != self.num_feat_extract_layers) or (len(self.conv_dim) != self.num_feat_extract_layers)): raise ValueError(f"Configuration for convolutional layers is incorrect. It is required that `len(config.conv_dim)` == `len(config.conv_stride)` == `len(config.conv_kernel)`, but is `len(config.conv_dim) = {len(self.conv_dim)}`, `len(config.conv_stride) = {len(self.conv_stride)}`, `len(config.conv_kernel) = {len(self.conv_kernel)}`.")
        self.apply_spec_augment = apply_spec_augment
        self.mask_time_prob = mask_time_prob
        self.mask_time_length = mask_time_length
        self.mask_time_min_masks = mask_time_min_masks
        self.mask_feature_prob = mask_feature_prob
        self.mask_feature_length = mask_feature_length
        self.num_codevectors_per_group = num_codevectors_per_group
        self.num_codevector_groups = num_codevector_groups
        self.contrastive_logits_temperature = contrastive_logits_temperature
        self.num_negatives = num_negatives
        self.codevector_dim = codevector_dim
        self.proj_codevector_dim = proj_codevector_dim
        self.diversity_loss_weight = diversity_loss_weight
        self.ctc_loss_reduction = ctc_loss_reduction
        self.ctc_zero_infinity = ctc_zero_infinity
        self.add_adapter = add_adapter
        self.adapter_kernel_size = adapter_kernel_size
        self.adapter_stride = adapter_stride
        self.num_adapter_layers = num_adapter_layers
        self.output_hidden_size = output_hidden_size or hidden_size
        self.classifier_proj_size = classifier_proj_size
        self.tdnn_dim = list(tdnn_dim)
        self.tdnn_kernel = list(tdnn_kernel)
        self.tdnn_dilation = list(tdnn_dilation)
        self.xvector_output_dim = xvector_output_dim
    @property
    def inputs_to_logits_ratio(self): return functools.reduce(operator.mul, self.conv_stride, 1)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
