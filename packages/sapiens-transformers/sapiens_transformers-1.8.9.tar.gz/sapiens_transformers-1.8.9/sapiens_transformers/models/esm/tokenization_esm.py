"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from typing import List, Optional
from ...tokenization_utils import PreTrainedTokenizer
from ...utils import logging
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "vocab.txt"}
def load_vocab_file(vocab_file):
    with open(vocab_file, "r") as f:
        lines = f.read().splitlines()
        return [l.strip() for l in lines]
class EsmTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, vocab_file, unk_token="<unk>", cls_token="<cls>", pad_token="<pad>", mask_token="<mask>", eos_token="<eos>", **kwargs):
        self.all_tokens = load_vocab_file(vocab_file)
        self._id_to_token = dict(enumerate(self.all_tokens))
        self._token_to_id = {tok: ind for ind, tok in enumerate(self.all_tokens)}
        super().__init__(unk_token=unk_token, cls_token=cls_token, pad_token=pad_token, mask_token=mask_token, eos_token=eos_token, **kwargs)
        self.unique_no_split_tokens = self.all_tokens
        self._update_trie(self.unique_no_split_tokens)
    def _convert_id_to_token(self, index: int) -> str: return self._id_to_token.get(index, self.unk_token)
    def _convert_token_to_id(self, token: str) -> int: return self._token_to_id.get(token, self._token_to_id.get(self.unk_token))
    def _tokenize(self, text, **kwargs): return text.split()
    def get_vocab(self):
        base_vocab = self._token_to_id.copy()
        base_vocab.update(self.added_tokens_encoder)
        return base_vocab
    def token_to_id(self, token: str) -> int: return self._token_to_id.get(token, self._token_to_id.get(self.unk_token))
    def id_to_token(self, index: int) -> str: return self._id_to_token.get(index, self.unk_token)
    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        cls = [self.cls_token_id]
        sep = [self.eos_token_id]
        if token_ids_1 is None:
            if self.eos_token_id is None: return cls + token_ids_0
            else: return cls + token_ids_0 + sep
        elif self.eos_token_id is None: raise ValueError("Cannot tokenize multiple sequences when EOS token is not set!")
        return cls + token_ids_0 + sep + token_ids_1 + sep
    def get_special_tokens_mask(self, token_ids_0: List, token_ids_1: Optional[List] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens:
            if token_ids_1 is not None: raise ValueError("You should not supply a second sequence if the provided sequence of ids is already formatted with special tokens for the model.")
            return [1 if token in self.all_special_ids else 0 for token in token_ids_0]
        mask = [1] + ([0] * len(token_ids_0)) + [1]
        if token_ids_1 is not None: mask += [0] * len(token_ids_1) + [1]
        return mask
    def save_vocabulary(self, save_directory, filename_prefix):
        vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + "vocab.txt")
        with open(vocab_file, "w") as f: f.write("\n".join(self.all_tokens))
        return (vocab_file,)
    @property
    def vocab_size(self) -> int: return len(self.all_tokens)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
