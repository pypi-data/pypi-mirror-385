"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PretrainedConfig
class GemmaConfig(PretrainedConfig):
    model_type = "gemma"
    keys_to_ignore_at_inference = ["past_key_values"]
    def __init__(self, vocab_size=256000, hidden_size=3072, intermediate_size=24576, num_hidden_layers=28, num_attention_heads=16, num_key_value_heads=16, head_dim=256,
    hidden_act="gelu_pytorch_tanh", hidden_activation=None, max_position_embeddings=8192, initializer_range=0.02, rms_norm_eps=1e-6, use_cache=True, pad_token_id=0,
    eos_token_id=1, bos_token_id=2, tie_word_embeddings=True, rope_theta=10000.0, attention_bias=False, attention_dropout=0.0, **kwargs):
        self.vocab_size = vocab_size
        self.max_position_embeddings = max_position_embeddings
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.head_dim = head_dim
        self.num_key_value_heads = num_key_value_heads
        self.hidden_act = hidden_act
        self.hidden_activation = hidden_activation
        self.initializer_range = initializer_range
        self.rms_norm_eps = rms_norm_eps
        self.use_cache = use_cache
        self.rope_theta = rope_theta
        self.attention_bias = attention_bias
        self.attention_dropout = attention_dropout
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, tie_word_embeddings=tie_word_embeddings, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
