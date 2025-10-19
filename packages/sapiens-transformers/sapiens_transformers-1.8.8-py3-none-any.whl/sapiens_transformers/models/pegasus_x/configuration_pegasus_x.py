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
class PegasusXConfig(PretrainedConfig):
    model_type = "pegasus_x"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {"num_attention_heads": "encoder_attention_heads", "hidden_size": "d_model"}
    def __init__(self, vocab_size=96103, max_position_embeddings=16384, encoder_layers=16, encoder_ffn_dim=4096, encoder_attention_heads=16, decoder_layers=16, decoder_ffn_dim=4096,
    decoder_attention_heads=16, encoder_layerdrop=0.0, decoder_layerdrop=0.0, use_cache=True, is_encoder_decoder=True, activation_function="gelu", d_model=1024,
    dropout=0.1, attention_dropout=0.0, activation_dropout=0.0, init_std=0.02, decoder_start_token_id=0, scale_embedding=True, pad_token_id=0, eos_token_id=1,
    forced_eos_token_id=1, num_global_tokens=32, block_size=512, stagger_local_blocks=True, **kwargs):
        self.vocab_size = vocab_size
        self.max_position_embeddings = max_position_embeddings
        self.d_model = d_model
        self.encoder_ffn_dim = encoder_ffn_dim
        self.encoder_layers = encoder_layers
        self.encoder_attention_heads = encoder_attention_heads
        self.decoder_ffn_dim = decoder_ffn_dim
        self.decoder_layers = decoder_layers
        self.decoder_attention_heads = decoder_attention_heads
        self.dropout = dropout
        self.attention_dropout = attention_dropout
        self.activation_dropout = activation_dropout
        self.activation_function = activation_function
        self.init_std = init_std
        self.encoder_layerdrop = encoder_layerdrop
        self.decoder_layerdrop = decoder_layerdrop
        self.use_cache = use_cache
        self.num_hidden_layers = encoder_layers
        self.scale_embedding = scale_embedding
        self.num_global_tokens = num_global_tokens
        self.block_size = block_size
        self.stagger_local_blocks = stagger_local_blocks
        super().__init__(pad_token_id=pad_token_id, eos_token_id=eos_token_id, is_encoder_decoder=is_encoder_decoder, decoder_start_token_id=decoder_start_token_id,
        forced_eos_token_id=forced_eos_token_id, **kwargs)
    @property
    def num_attention_heads(self) -> int: return self.encoder_attention_heads
    @property
    def hidden_size(self) -> int: return self.d_model
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
