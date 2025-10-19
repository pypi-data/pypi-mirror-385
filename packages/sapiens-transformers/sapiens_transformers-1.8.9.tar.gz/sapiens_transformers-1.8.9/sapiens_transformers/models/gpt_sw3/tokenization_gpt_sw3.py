"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
import re
import unicodedata
from shutil import copyfile
from typing import Any, Dict, List, Optional, Tuple, Union
import sentencepiece as spm
from ...tokenization_utils import PreTrainedTokenizer
from ...utils import is_torch_available, logging
if is_torch_available(): import torch
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "spiece.model"}
class GPTSw3Tokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, vocab_file, do_lower_case=False, remove_space=False, keep_accents=False, pad_token=None, unk_token=None, eos_token=None, bos_token=None,
    sp_model_kwargs: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        self.sp_model_kwargs = {} if sp_model_kwargs is None else sp_model_kwargs
        name_or_path = kwargs.get("name_or_path")
        if name_or_path is None:
            logger.warning("name_or_path not provided, will work for all GPTSw3 models except gpt-sw3-7b, you are testing the model, this can safely be ignored")
            name_or_path = "None"
        eos_token = "<|endoftext|>" if eos_token is None else eos_token
        unk_token = "<unk>" if unk_token is None else unk_token
        if "gpt-sw3-7b" in name_or_path:
            pad_token = unk_token if pad_token is None else pad_token
            bos_token = eos_token if bos_token is None else bos_token
        else:
            pad_token = "<pad>" if pad_token is None else pad_token
            bos_token = "<s>" if bos_token is None else bos_token
        self.do_lower_case = do_lower_case
        self.remove_space = remove_space
        self.keep_accents = keep_accents
        self.vocab_file = vocab_file
        self.sp_model = spm.SentencePieceProcessor(**self.sp_model_kwargs)
        self.sp_model.Load(vocab_file)
        self.whitespaces = {" ", " ", " ", " ", " ", "　", " ", " ", " ", " ", "￼", ""}
        self.non_printing_characters_re = re.compile(f"[{''.join(map(chr, list(range(0, 9)) + list(range(11, 32)) + list(range(127, 160)) + [160, 173, 8203]))}]")
        super().__init__(do_lower_case=do_lower_case, remove_space=remove_space, keep_accents=keep_accents, bos_token=bos_token, eos_token=eos_token, unk_token=unk_token,
        pad_token=pad_token, sp_model_kwargs=self.sp_model_kwargs, **kwargs)
    def __getstate__(self):
        state = self.__dict__.copy()
        state["sp_model"] = None
        return state
    def __setstate__(self, d):
        self.__dict__ = d
        if not hasattr(self, "sp_model_kwargs"): self.sp_model_kwargs = {}
        self.sp_model = spm.SentencePieceProcessor(**self.sp_model_kwargs)
        self.sp_model.Load(self.vocab_file)
    @property
    def vocab_size(self) -> int: return len(self.sp_model)
    def preprocess_text(self, text: str) -> str:
        text = self.non_printing_characters_re.sub("", text)
        text = "".join([char if char not in self.whitespaces else " " for char in text])
        text = unicodedata.normalize("NFC", text)
        return text
    def _tokenize(self, text: str, **kwargs) -> List[str]:
        text = self.preprocess_text(text)
        return self.sp_model.encode(text, out_type=str)
    def _convert_token_to_id(self, token: str) -> int: return self.sp_model.PieceToId(token)
    def _convert_id_to_token(self, index: int) -> str: return self.sp_model.IdToPiece(index)
    @staticmethod
    def clean_up_tokenization(out_string: str) -> str: return out_string
    def convert_tokens_to_string(self, tokens: List[str]) -> str:
        current_sub_tokens = []
        out_string = ""
        prev_is_special = False
        for token in tokens:
            if token in self.all_special_tokens:
                if not prev_is_special: out_string += " "
                out_string += self.sp_model.decode(current_sub_tokens) + token
                prev_is_special = True
                current_sub_tokens = []
            else:
                current_sub_tokens.append(token)
                prev_is_special = False
        out_string += self.sp_model.decode(current_sub_tokens)
        return out_string
    def get_vocab(self) -> Dict[str, int]:
        vocab = {self.convert_ids_to_tokens(i): i for i in range(self.vocab_size)}
        vocab.update(self.added_tokens_encoder)
        return vocab
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        if not os.path.isdir(save_directory):
            logger.error(f"Vocabulary path ({save_directory}) should be a directory")
            return
        out_vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab_file"])
        if os.path.abspath(self.vocab_file) != os.path.abspath(out_vocab_file) and os.path.isfile(self.vocab_file): copyfile(self.vocab_file, out_vocab_file)
        elif not os.path.isfile(self.vocab_file):
            with open(out_vocab_file, "wb") as fi:
                content_spiece_model = self.sp_model.serialized_model_proto()
                fi.write(content_spiece_model)
        return (out_vocab_file,)
    def encode_fast(self, text: Union[str, List[str]], return_tensors: Union[str, bool] = False) -> Union[List[int], List[List[int]], "torch.Tensor"]:
        if isinstance(text, str):
            text = self.preprocess_text(text)
            token_ids = self.sp_model.encode(text)
        else:
            text = [self.preprocess_text(t) for t in text]
            token_ids = self.sp_model.encode(text)
        if return_tensors is True or return_tensors == "pt": token_ids = torch.tensor(token_ids)
        return token_ids
    def decode_fast(self, token_ids: Union[int, List[int]]) -> str: return self.sp_model.decode(token_ids)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
