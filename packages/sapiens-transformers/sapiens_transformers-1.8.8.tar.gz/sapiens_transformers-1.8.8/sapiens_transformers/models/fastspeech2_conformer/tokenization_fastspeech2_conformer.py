"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import json
import os
from typing import Optional, Tuple
import regex
from ...tokenization_utils import PreTrainedTokenizer
from ...utils import logging, requires_backends
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "vocab.json"}
class FastSpeech2ConformerTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, vocab_file, bos_token="<sos/eos>", eos_token="<sos/eos>", pad_token="<blank>", unk_token="<unk>", should_strip_spaces=False, **kwargs):
        requires_backends(self, "g2p_en")
        with open(vocab_file, encoding="utf-8") as vocab_handle: self.encoder = json.load(vocab_handle)
        import g2p_en
        self.g2p = g2p_en.G2p()
        self.decoder = {v: k for k, v in self.encoder.items()}
        super().__init__(bos_token=bos_token, eos_token=eos_token, unk_token=unk_token, pad_token=pad_token, should_strip_spaces=should_strip_spaces, **kwargs)
        self.should_strip_spaces = should_strip_spaces
    @property
    def vocab_size(self): return len(self.decoder)
    def get_vocab(self): return dict(self.encoder, **self.added_tokens_encoder)
    def prepare_for_tokenization(self, text, is_split_into_words=False, **kwargs):
        text = regex.sub(";", ",", text)
        text = regex.sub(":", ",", text)
        text = regex.sub("-", " ", text)
        text = regex.sub("&", "and", text)
        text = regex.sub(r"[\(\)\[\]\<\>\"]+", "", text)
        text = regex.sub(r"\s+", " ", text)
        text = text.upper()
        return text, kwargs
    def _tokenize(self, text):
        tokens = self.g2p(text)
        if self.should_strip_spaces: tokens = list(filter(lambda s: s != " ", tokens))
        tokens.append(self.eos_token)
        return tokens
    def _convert_token_to_id(self, token): return self.encoder.get(token, self.encoder.get(self.unk_token))
    def _convert_id_to_token(self, index): return self.decoder.get(index, self.unk_token)
    def decode(self, token_ids, **kwargs):
        logger.warning("Phonemes cannot be reliably converted to a string due to the one-many mapping, converting to tokens instead.")
        return self.convert_ids_to_tokens(token_ids)
    def convert_tokens_to_string(self, tokens, **kwargs):
        logger.warning("Phonemes cannot be reliably converted to a string due to the one-many mapping, returning the tokens.")
        return tokens
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        if not os.path.isdir(save_directory):
            logger.error(f"Vocabulary path ({save_directory}) should be a directory")
            return
        vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab_file"])
        with open(vocab_file, "w", encoding="utf-8") as f: f.write(json.dumps(self.get_vocab(), ensure_ascii=False))
        return (vocab_file,)
    def __getstate__(self):
        state = self.__dict__.copy()
        state["g2p"] = None
        return state
    def __setstate__(self, d):
        self.__dict__ = d
        try:
            import g2p_en
            self.g2p = g2p_en.G2p()
        except ImportError: raise ImportError("You need to install g2p-en to use FastSpeech2ConformerTokenizer. See https://pypi.org/project/g2p-en/ for installation.")
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
