"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from shutil import copyfile
from typing import Any, Dict, List, Optional, Tuple
import sentencepiece as spm
from ...tokenization_utils import AddedToken, BatchEncoding, PreTrainedTokenizer
from ...utils import logging
logger = logging.get_logger(__name__)
SPIECE_UNDERLINE = "▁"
VOCAB_FILES_NAMES = {"vocab_file": "sentencepiece.bpe.model"}
FAIRSEQ_LANGUAGE_CODES = ["ar_AR", "cs_CZ", "de_DE", "en_XX", "es_XX", "et_EE", "fi_FI", "fr_XX", "gu_IN", "hi_IN", "it_IT", "ja_XX", "kk_KZ", "ko_KR", "lt_LT", "lv_LV",
"my_MM", "ne_NP", "nl_XX", "ro_RO", "ru_RU", "si_LK", "tr_TR", "vi_VN", "zh_CN"]
class MBartTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    prefix_tokens: List[int] = []
    suffix_tokens: List[int] = []
    def __init__(self, vocab_file, bos_token="<s>", eos_token="</s>", sep_token="</s>", cls_token="<s>", unk_token="<unk>", pad_token="<pad>", mask_token="<mask>",
    tokenizer_file=None, src_lang=None, tgt_lang=None, sp_model_kwargs: Optional[Dict[str, Any]] = None, additional_special_tokens=None, **kwargs):
        mask_token = (AddedToken(mask_token, lstrip=True, normalized=False) if isinstance(mask_token, str) else mask_token)
        self.sp_model_kwargs = {} if sp_model_kwargs is None else sp_model_kwargs
        self.sp_model = spm.SentencePieceProcessor(**self.sp_model_kwargs)
        self.sp_model.Load(str(vocab_file))
        self.vocab_file = vocab_file
        self.fairseq_tokens_to_ids = {"<s>": 0, "<pad>": 1, "</s>": 2, "<unk>": 3}
        self.fairseq_offset = 1
        self.sp_model_size = len(self.sp_model)
        self.lang_code_to_id = {code: self.sp_model_size + i + self.fairseq_offset for i, code in enumerate(FAIRSEQ_LANGUAGE_CODES)}
        self.id_to_lang_code = {v: k for k, v in self.lang_code_to_id.items()}
        self.fairseq_tokens_to_ids["<mask>"] = len(self.sp_model) + len(self.lang_code_to_id) + self.fairseq_offset
        self.fairseq_tokens_to_ids.update(self.lang_code_to_id)
        self.fairseq_ids_to_tokens = {v: k for k, v in self.fairseq_tokens_to_ids.items()}
        _additional_special_tokens = list(self.lang_code_to_id.keys())
        if additional_special_tokens is not None: _additional_special_tokens.extend([t for t in additional_special_tokens if t not in _additional_special_tokens])
        super().__init__(bos_token=bos_token, eos_token=eos_token, unk_token=unk_token, sep_token=sep_token, cls_token=cls_token, pad_token=pad_token,
        mask_token=mask_token, tokenizer_file=None, src_lang=src_lang, tgt_lang=tgt_lang, additional_special_tokens=_additional_special_tokens, sp_model_kwargs=self.sp_model_kwargs, **kwargs)
        self._src_lang = src_lang if src_lang is not None else "en_XX"
        self.cur_lang_code_id = self.lang_code_to_id[self._src_lang]
        self.tgt_lang = tgt_lang
        self.set_src_lang_special_tokens(self._src_lang)
    def __getstate__(self):
        state = self.__dict__.copy()
        state["sp_model"] = None
        state["sp_model_proto"] = self.sp_model.serialized_model_proto()
        return state
    def __setstate__(self, d):
        self.__dict__ = d
        if not hasattr(self, "sp_model_kwargs"): self.sp_model_kwargs = {}
        self.sp_model = spm.SentencePieceProcessor(**self.sp_model_kwargs)
        self.sp_model.LoadFromSerializedProto(self.sp_model_proto)
    @property
    def vocab_size(self): return len(self.sp_model) + len(self.lang_code_to_id) + self.fairseq_offset + 1
    @property
    def src_lang(self) -> str: return self._src_lang
    @src_lang.setter
    def src_lang(self, new_src_lang: str) -> None:
        self._src_lang = new_src_lang
        self.set_src_lang_special_tokens(self._src_lang)
    def get_special_tokens_mask(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens: return super().get_special_tokens_mask(token_ids_0=token_ids_0, token_ids_1=token_ids_1, already_has_special_tokens=True)
        prefix_ones = [1] * len(self.prefix_tokens)
        suffix_ones = [1] * len(self.suffix_tokens)
        if token_ids_1 is None: return prefix_ones + ([0] * len(token_ids_0)) + suffix_ones
        return prefix_ones + ([0] * len(token_ids_0)) + ([0] * len(token_ids_1)) + suffix_ones
    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        if token_ids_1 is None: return self.prefix_tokens + token_ids_0 + self.suffix_tokens
        return self.prefix_tokens + token_ids_0 + token_ids_1 + self.suffix_tokens
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        sep = [self.sep_token_id]
        cls = [self.cls_token_id]
        if token_ids_1 is None: return len(cls + token_ids_0 + sep) * [0]
        return len(cls + token_ids_0 + sep + sep + token_ids_1 + sep) * [0]
    def _build_translation_inputs(self, raw_inputs, return_tensors: str, src_lang: Optional[str], tgt_lang: Optional[str], **extra_kwargs):
        if src_lang is None or tgt_lang is None: raise ValueError("Translation requires a `src_lang` and a `tgt_lang` for this model")
        self.src_lang = src_lang
        inputs = self(raw_inputs, add_special_tokens=True, return_tensors=return_tensors, **extra_kwargs)
        tgt_lang_id = self.convert_tokens_to_ids(tgt_lang)
        inputs["forced_bos_token_id"] = tgt_lang_id
        return inputs
    def get_vocab(self):
        vocab = {self.convert_ids_to_tokens(i): i for i in range(self.vocab_size)}
        vocab.update(self.added_tokens_encoder)
        return vocab
    def _tokenize(self, text: str) -> List[str]: return self.sp_model.encode(text, out_type=str)
    def _convert_token_to_id(self, token):
        if token in self.fairseq_tokens_to_ids: return self.fairseq_tokens_to_ids[token]
        spm_id = self.sp_model.PieceToId(token)
        return spm_id + self.fairseq_offset if spm_id else self.unk_token_id
    def _convert_id_to_token(self, index):
        if index in self.fairseq_ids_to_tokens: return self.fairseq_ids_to_tokens[index]
        return self.sp_model.IdToPiece(index - self.fairseq_offset)
    def convert_tokens_to_string(self, tokens):
        out_string = "".join(tokens).replace(SPIECE_UNDERLINE, " ").strip()
        return out_string
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
    def prepare_seq2seq_batch(self, src_texts: List[str], src_lang: str = "en_XX", tgt_texts: Optional[List[str]] = None, tgt_lang: str = "ro_RO", **kwargs) -> BatchEncoding:
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang
        return super().prepare_seq2seq_batch(src_texts, tgt_texts, **kwargs)
    def _switch_to_input_mode(self): return self.set_src_lang_special_tokens(self.src_lang)
    def _switch_to_target_mode(self): return self.set_tgt_lang_special_tokens(self.tgt_lang)
    def set_src_lang_special_tokens(self, src_lang) -> None:
        self.cur_lang_code = self.lang_code_to_id[src_lang]
        self.prefix_tokens = []
        self.suffix_tokens = [self.eos_token_id, self.cur_lang_code]
    def set_tgt_lang_special_tokens(self, lang: str) -> None:
        self.cur_lang_code = self.lang_code_to_id[lang]
        self.prefix_tokens = []
        self.suffix_tokens = [self.eos_token_id, self.cur_lang_code]
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
