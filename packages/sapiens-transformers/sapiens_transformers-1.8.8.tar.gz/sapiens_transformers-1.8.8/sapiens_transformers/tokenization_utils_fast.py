"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .tokenization_utils_base import (INIT_TOKENIZER_DOCSTRING, AddedToken, BatchEncoding, PreTokenizedInput, PreTokenizedInputPair,
PreTrainedTokenizerBase, SpecialTokensMixin, TextInput, TextInputPair, TruncationStrategy)
from tokenizers.trainers import BpeTrainer, UnigramTrainer, WordLevelTrainer, WordPieceTrainer
from .utils import PaddingStrategy, add_end_docstrings, logging
from .modeling_gguf_pytorch_utils import load_gguf_checkpoint
from .convert_slow_tokenizer import convert_slow_tokenizer
from typing import Any, Dict, List, Optional, Tuple, Union
import tokenizers.pre_tokenizers as pre_tokenizers_fast
from tokenizers.decoders import Decoder as DecoderFast
from .integrations.ggml import convert_gguf_tokenizer
from .tokenization_utils import PreTrainedTokenizer
from tokenizers import Tokenizer as TokenizerFast
from tokenizers import Encoding as EncodingFast
from collections import defaultdict
import json
import copy
import os
logger = logging.get_logger(__name__)
TOKENIZER_FILE = "tokenizer.json"
SPECIAL_TOKENS_MAP_FILE = "special_tokens_map.json"
TOKENIZER_CONFIG_FILE = "tokenizer_config.json"
TIKTOKEN_VOCAB_FILE = "tokenizer.model"
ADDED_TOKENS_FILE = "added_tokens.json"
INIT_TOKENIZER_DOCSTRING += """
        tokenizer_object ([`tokenizers.Tokenizer`]):
            A [`tokenizers.Tokenizer`] object from HF tokenizers to instantiate from. See [Using tokenizers from HF
            tokenizers](../fast_tokenizers) for more information.
        tokenizer_file ([`str`]):
            A path to a local JSON file representing a previously serialized [`tokenizers.Tokenizer`] object from HF
            tokenizers.
"""
MODEL_TO_TRAINER_MAPPING = {"BPE": BpeTrainer, "Unigram": UnigramTrainer, "WordLevel": WordLevelTrainer, "WordPiece": WordPieceTrainer}
VOCAB_FILES_NAMES = {"tokenizer_file": TOKENIZER_FILE, "vocab_file": TIKTOKEN_VOCAB_FILE}
@add_end_docstrings(INIT_TOKENIZER_DOCSTRING)
class PreTrainedTokenizerFast(PreTrainedTokenizerBase):
    vocab_files_names = VOCAB_FILES_NAMES
    slow_tokenizer_class: PreTrainedTokenizer = None
    def __init__(self, *args, **kwargs):
        tokenizer_object = kwargs.pop("tokenizer_object", None)
        slow_tokenizer = kwargs.pop("__slow_tokenizer", None)
        gguf_file = kwargs.pop("gguf_file", None)
        fast_tokenizer_file = kwargs.pop("tokenizer_file", None)
        from_slow = kwargs.pop("from_slow", False)
        added_tokens_decoder = kwargs.pop("added_tokens_decoder", {})
        if from_slow and slow_tokenizer is None and self.slow_tokenizer_class is None: raise ValueError("Cannot instantiate this tokenizer from a slow version. If it's based on sentencepiece, make sure you have sentencepiece installed.")
        if tokenizer_object is not None: fast_tokenizer = copy.deepcopy(tokenizer_object)
        elif fast_tokenizer_file is not None and not from_slow: fast_tokenizer = TokenizerFast.from_file(fast_tokenizer_file)
        elif slow_tokenizer: fast_tokenizer = convert_slow_tokenizer(slow_tokenizer)
        elif gguf_file is not None:
            gguf_param = load_gguf_checkpoint(kwargs.get("vocab_file"))
            architecture = gguf_param["config"]["model_type"]
            tokenizer_dict = gguf_param["tokenizer"]
            tokenizer_config = gguf_param["tokenizer_config"]
            fast_tokenizer, additional_kwargs = convert_gguf_tokenizer(architecture, tokenizer_dict)
            kwargs.update(tokenizer_config)
            if len(additional_kwargs) > 0: kwargs.update(additional_kwargs)
        elif self.slow_tokenizer_class is not None and slow_tokenizer is not False:
            slow_tokenizer = self.slow_tokenizer_class(*args, **kwargs)
            fast_tokenizer = convert_slow_tokenizer(slow_tokenizer)
        elif not slow_tokenizer:
            self.vocab_file = kwargs.get("vocab_file", None)
            self.additional_special_tokens = kwargs.get("additional_special_tokens", [])
            fast_tokenizer = convert_slow_tokenizer(self, from_tiktoken=True)
            slow_tokenizer = None
        else: raise ValueError("Couldn't instantiate the backend tokenizer from one of: \n(1) a `tokenizers` library serialization file, \n(2) a slow tokenizer instance to convert or \n(3) an equivalent slow tokenizer class to instantiate and convert. \nYou need to have sentencepiece or tiktoken installed to convert a slow tokenizer to a fast one.")
        self._tokenizer = fast_tokenizer
        if slow_tokenizer is not None: kwargs.update(slow_tokenizer.init_kwargs)
        self._decode_use_source_tokenizer = False
        _truncation = self._tokenizer.truncation
        if _truncation is not None:
            self._tokenizer.enable_truncation(**_truncation)
            kwargs.setdefault("max_length", _truncation["max_length"])
            kwargs.setdefault("truncation_side", _truncation["direction"])
            kwargs.setdefault("stride", _truncation["stride"])
            kwargs.setdefault("truncation_strategy", _truncation["strategy"])
        else: self._tokenizer.no_truncation()
        _padding = self._tokenizer.padding
        if _padding is not None:
            self._tokenizer.enable_padding(**_padding)
            kwargs.setdefault("pad_token", _padding["pad_token"])
            kwargs.setdefault("pad_token_type_id", _padding["pad_type_id"])
            kwargs.setdefault("padding_side", _padding["direction"])
            kwargs.setdefault("max_length", _padding["length"])
            kwargs.setdefault("pad_to_multiple_of", _padding["pad_to_multiple_of"])
        super().__init__(**kwargs)
        self._tokenizer.encode_special_tokens = self.split_special_tokens
        added_tokens_decoder_hash = {hash(repr(token)) for token in self.added_tokens_decoder}
        tokens_to_add = [token for index, token in sorted(added_tokens_decoder.items(), key=lambda x: x[0]) if hash(repr(token)) not in added_tokens_decoder_hash]
        encoder = list(self.added_tokens_encoder.keys()) + [str(token) for token in tokens_to_add]
        tokens_to_add += [token for token in self.all_special_tokens_extended if token not in encoder and token not in tokens_to_add]
        if len(tokens_to_add) > 0:
            tokens = []
            special_tokens = self.all_special_tokens
            for token in tokens_to_add:
                is_special = ((token.special or str(token) in special_tokens) if isinstance(token, AddedToken) else str(token) in special_tokens)
                if isinstance(token, str): token = AddedToken(token, special=is_special)
                else: token.special = is_special
                tokens.append(token)
            if tokens: self.add_tokens(tokens)
    @property
    def is_fast(self) -> bool: return True
    @property
    def can_save_slow_tokenizer(self) -> bool: return True
    @property
    def vocab_size(self) -> int: return self._tokenizer.get_vocab_size(with_added_tokens=False)
    def get_vocab(self) -> Dict[str, int]: return self._tokenizer.get_vocab(with_added_tokens=True)
    @property
    def vocab(self) -> Dict[str, int]: return self.get_vocab()
    @property
    def added_tokens_encoder(self) -> Dict[str, int]: return {k.content: v for v, k in sorted(self.added_tokens_decoder.items(), key=lambda item: item[0])}
    @property
    def added_tokens_decoder(self) -> Dict[int, AddedToken]: return self._tokenizer.get_added_tokens_decoder()
    def get_added_vocab(self) -> Dict[str, int]: return {k.content: v for v, k in sorted(self.added_tokens_decoder.items(), key=lambda item: item[0])}
    def __len__(self) -> int: return self._tokenizer.get_vocab_size(with_added_tokens=True)
    @property
    def backend_tokenizer(self) -> TokenizerFast: return self._tokenizer
    @property
    def decoder(self) -> DecoderFast: return self._tokenizer.decoder
    def _convert_encoding(self, encoding: EncodingFast, return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False,
    return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False, return_length: bool = False, verbose: bool = True) -> Tuple[Dict[str, Any], List[EncodingFast]]:
        if return_token_type_ids is None: return_token_type_ids = "token_type_ids" in self.model_input_names
        if return_attention_mask is None: return_attention_mask = "attention_mask" in self.model_input_names
        if return_overflowing_tokens and encoding.overflowing is not None: encodings = [encoding] + encoding.overflowing
        else: encodings = [encoding]
        encoding_dict = defaultdict(list)
        for e in encodings:
            encoding_dict["input_ids"].append(e.ids)
            if return_token_type_ids: encoding_dict["token_type_ids"].append(e.type_ids)
            if return_attention_mask: encoding_dict["attention_mask"].append(e.attention_mask)
            if return_special_tokens_mask: encoding_dict["special_tokens_mask"].append(e.special_tokens_mask)
            if return_offsets_mapping: encoding_dict["offset_mapping"].append(e.offsets)
            if return_length: encoding_dict["length"].append(len(e.ids))
        return encoding_dict, encodings
    def convert_tokens_to_ids(self, tokens: Union[str, List[str]]) -> Union[int, List[int]]:
        if tokens is None: return None
        if isinstance(tokens, str): return self._convert_token_to_id_with_added_voc(tokens)
        return [self._convert_token_to_id_with_added_voc(token) for token in tokens]
    def _convert_token_to_id_with_added_voc(self, token: str) -> int:
        index = self._tokenizer.token_to_id(token)
        if index is None: return self.unk_token_id
        return index
    def _convert_id_to_token(self, index: int) -> Optional[str]: return self._tokenizer.id_to_token(int(index))
    def _add_tokens(self, new_tokens: List[Union[str, AddedToken]], special_tokens=False) -> int:
        if special_tokens: return self._tokenizer.add_special_tokens(new_tokens)
        return self._tokenizer.add_tokens(new_tokens)
    def num_special_tokens_to_add(self, pair: bool = False) -> int: return self._tokenizer.num_special_tokens_to_add(pair)
    def convert_ids_to_tokens(self, ids: Union[int, List[int]], skip_special_tokens: bool = False) -> Union[str, List[str]]:
        if isinstance(ids, int): return self._tokenizer.id_to_token(ids)
        tokens = []
        for index in ids:
            index = int(index)
            if skip_special_tokens and index in self.all_special_ids: continue
            tokens.append(self._tokenizer.id_to_token(index))
        return tokens
    def tokenize(self, text: str, pair: Optional[str] = None, add_special_tokens: bool = False, **kwargs) -> List[str]: return self.encode_plus(text=text, text_pair=pair, add_special_tokens=add_special_tokens, **kwargs).tokens()
    def set_truncation_and_padding(self, padding_strategy: PaddingStrategy, truncation_strategy: TruncationStrategy, max_length: int, stride: int, pad_to_multiple_of: Optional[int], padding_side: Optional[bool]):
        _truncation = self._tokenizer.truncation
        _padding = self._tokenizer.padding
        if truncation_strategy == TruncationStrategy.DO_NOT_TRUNCATE:
            if _truncation is not None: self._tokenizer.no_truncation()
        else:
            target = {"max_length": max_length, "stride": stride, "strategy": truncation_strategy.value, "direction": self.truncation_side}
            if _truncation is None: current = None
            else: current = {k: _truncation.get(k, None) for k in target}
            if current != target: self._tokenizer.enable_truncation(**target)
        if padding_strategy == PaddingStrategy.DO_NOT_PAD:
            if _padding is not None: self._tokenizer.no_padding()
        else:
            length = max_length if padding_strategy == PaddingStrategy.MAX_LENGTH else None
            target = {"length": length, "direction": padding_side if padding_side is not None else self.padding_side, "pad_id": self.pad_token_id, "pad_token": self.pad_token, "pad_type_id": self.pad_token_type_id, "pad_to_multiple_of": pad_to_multiple_of}
            if _padding != target: self._tokenizer.enable_padding(**target)
    def _batch_encode_plus(self, batch_text_or_text_pairs: Union[List[TextInput], List[TextInputPair], List[PreTokenizedInput], List[PreTokenizedInputPair]], add_special_tokens: bool = True, padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD,
    truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE, max_length: Optional[int] = None, stride: int = 0, is_split_into_words: bool = False, pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None,
    return_tensors: Optional[str] = None, return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False,
    return_length: bool = False, verbose: bool = True, split_special_tokens: bool = False) -> BatchEncoding:
        if not isinstance(batch_text_or_text_pairs, (tuple, list)): raise TypeError(f"batch_text_or_text_pairs has to be a list or a tuple (got {type(batch_text_or_text_pairs)})")
        self.set_truncation_and_padding(padding_strategy=padding_strategy, truncation_strategy=truncation_strategy, max_length=max_length, stride=stride, pad_to_multiple_of=pad_to_multiple_of, padding_side=padding_side)
        if self._tokenizer.encode_special_tokens != split_special_tokens: self._tokenizer.encode_special_tokens = split_special_tokens
        encodings = self._tokenizer.encode_batch(batch_text_or_text_pairs, add_special_tokens=add_special_tokens, is_pretokenized=is_split_into_words)
        tokens_and_encodings = [self._convert_encoding(encoding=encoding, return_token_type_ids=return_token_type_ids, return_attention_mask=return_attention_mask, return_overflowing_tokens=return_overflowing_tokens,
        return_special_tokens_mask=return_special_tokens_mask, return_offsets_mapping=return_offsets_mapping, return_length=return_length, verbose=verbose) for encoding in encodings]
        sanitized_tokens = {}
        for key in tokens_and_encodings[0][0].keys():
            stack = [e for item, _ in tokens_and_encodings for e in item[key]]
            sanitized_tokens[key] = stack
        sanitized_encodings = [e for _, item in tokens_and_encodings for e in item]
        if return_overflowing_tokens:
            overflow_to_sample_mapping = []
            for i, (toks, _) in enumerate(tokens_and_encodings): overflow_to_sample_mapping += [i] * len(toks["input_ids"])
            sanitized_tokens["overflow_to_sample_mapping"] = overflow_to_sample_mapping
        for input_ids in sanitized_tokens["input_ids"]: self._eventual_warn_about_too_long_sequence(input_ids, max_length, verbose)
        return BatchEncoding(sanitized_tokens, sanitized_encodings, tensor_type=return_tensors)
    def _encode_plus(self, text: Union[TextInput, PreTokenizedInput], text_pair: Optional[Union[TextInput, PreTokenizedInput]] = None, add_special_tokens: bool = True, padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD,
    truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE, max_length: Optional[int] = None, stride: int = 0, is_split_into_words: bool = False, pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None,
    return_tensors: Optional[bool] = None, return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False,
    return_length: bool = False, verbose: bool = True, split_special_tokens: bool = False, **kwargs) -> BatchEncoding:
        batched_input = [(text, text_pair)] if text_pair else [text]
        batched_output = self._batch_encode_plus(batched_input, is_split_into_words=is_split_into_words, add_special_tokens=add_special_tokens, padding_strategy=padding_strategy, truncation_strategy=truncation_strategy, max_length=max_length,
        stride=stride, pad_to_multiple_of=pad_to_multiple_of, padding_side=padding_side, return_tensors=return_tensors, return_token_type_ids=return_token_type_ids, return_attention_mask=return_attention_mask, return_overflowing_tokens=return_overflowing_tokens,
        return_special_tokens_mask=return_special_tokens_mask, return_offsets_mapping=return_offsets_mapping, return_length=return_length, verbose=verbose, split_special_tokens=split_special_tokens, **kwargs)
        if return_tensors is None and not return_overflowing_tokens: batched_output = BatchEncoding({key: value[0] if len(value) > 0 and isinstance(value[0], list) else value for key, value in batched_output.items()}, batched_output.encodings)
        self._eventual_warn_about_too_long_sequence(batched_output["input_ids"], max_length, verbose)
        return batched_output
    def convert_tokens_to_string(self, tokens: List[str]) -> str: return self.backend_tokenizer.decoder.decode(tokens)
    def _decode(self, token_ids: Union[int, List[int]], skip_special_tokens: bool = False, clean_up_tokenization_spaces: bool = None, **kwargs) -> str:
        self._decode_use_source_tokenizer = kwargs.pop("use_source_tokenizer", False)
        if isinstance(token_ids, int): token_ids = [token_ids]
        text = self._tokenizer.decode(token_ids, skip_special_tokens=skip_special_tokens)
        clean_up_tokenization_spaces = (clean_up_tokenization_spaces if clean_up_tokenization_spaces is not None else self.clean_up_tokenization_spaces)
        if clean_up_tokenization_spaces:
            clean_text = self.clean_up_tokenization(text)
            return clean_text
        else: return text
    def _save_pretrained(self, save_directory: Union[str, os.PathLike], file_names: Tuple[str], legacy_format: Optional[bool] = None, filename_prefix: Optional[str] = None) -> Tuple[str]:
        save_directory = str(save_directory)
        if self.slow_tokenizer_class is None and legacy_format is True: raise ValueError("Your tokenizer does not have a legacy version defined and therefore cannot register this version. You might consider leaving the legacy_format at `None` or setting it to `False`.")
        save_slow = ((legacy_format is None or legacy_format is True) and self.slow_tokenizer_class is not None and self.can_save_slow_tokenizer)
        save_fast = legacy_format is None or legacy_format is False
        if save_slow:
            added_tokens_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + ADDED_TOKENS_FILE)
            added_vocab = {tok: index for tok, index in self.added_tokens_encoder.items() if index >= self.vocab_size}
            if added_vocab:
                with open(added_tokens_file, "w", encoding="utf-8") as f:
                    out_str = json.dumps(added_vocab, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
                    f.write(out_str)
            vocab_files = self.save_vocabulary(save_directory, filename_prefix=filename_prefix)
            file_names = file_names + vocab_files + (added_tokens_file,)
        if save_fast:
            tokenizer_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + TOKENIZER_FILE)
            self.backend_tokenizer.save(tokenizer_file)
            file_names = file_names + (tokenizer_file,)
        return file_names
    def train_new_from_iterator(self, text_iterator, vocab_size, length=None, new_special_tokens=None, special_tokens_map=None, **kwargs):
        tokenizer_json = json.loads(self._tokenizer.to_str())
        added_tokens = tokenizer_json.pop("added_tokens")
        post_processor = tokenizer_json.pop("post_processor")
        unk_token = None
        if tokenizer_json["model"]["type"] == "BPE":
            tokenizer_json["model"]["vocab"] = {}
            tokenizer_json["model"]["merges"] = []
        elif tokenizer_json["model"]["type"] == "Unigram":
            if tokenizer_json["model"]["unk_id"] is not None:
                unk_id = tokenizer_json["model"]["unk_id"]
                unk_token = tokenizer_json["model"]["vocab"][unk_id][0]
                if special_tokens_map is not None and unk_token in special_tokens_map: unk_token = special_tokens_map[unk_token]
                tokenizer_json["model"]["unk_id"] = 0
                tokenizer_json["model"]["vocab"] = [[unk_token, 0.0]]
        elif tokenizer_json["model"]["type"] in ["WordLevel", "WordPiece"]: tokenizer_json["model"]["vocab"] = {}
        else: raise ValueError(f"This method does not support this type of tokenizer (found {tokenizer_json['model']['type']}) only BPE, Unigram, WordLevel and WordPiece.")
        if (special_tokens_map is not None and "unk_token" in tokenizer_json["model"] and tokenizer_json["model"]["unk_token"] in special_tokens_map): tokenizer_json["model"]["unk_token"] = special_tokens_map[tokenizer_json["model"]["unk_token"]]
        tokenizer = TokenizerFast.from_str(json.dumps(tokenizer_json))
        special_tokens = []
        for added_token in added_tokens:
            special = added_token.pop("special", None)
            _ = added_token.pop("id", None)
            if tokenizer_json["model"]["type"] != "Unigram" and not special: continue
            if special_tokens_map is not None and added_token["content"] in special_tokens_map: added_token["content"] = special_tokens_map[added_token["content"]]
            special_tokens.append(AddedToken(**added_token))
        if new_special_tokens is not None: special_tokens.extend(new_special_tokens)
        if (tokenizer_json["model"]["type"] == "BPE" and "continuing_subword_prefix" not in kwargs and tokenizer_json["model"]["continuing_subword_prefix"] is not None): kwargs["continuing_subword_prefix"] = tokenizer_json["model"]["continuing_subword_prefix"]
        if (tokenizer_json["model"]["type"] == "BPE" and "end_of_word_suffix" not in kwargs and tokenizer_json["model"]["end_of_word_suffix"] is not None): kwargs["end_of_word_suffix"] = tokenizer_json["model"]["end_of_word_suffix"]
        if tokenizer_json["model"]["type"] == "Unigram" and unk_token is not None: kwargs["unk_token"] = unk_token
        if (tokenizer_json["pre_tokenizer"] is not None and tokenizer_json["pre_tokenizer"]["type"] == "ByteLevel" or tokenizer_json["pre_tokenizer"]["type"] == "Sequence" and "pretokenizers" in tokenizer_json["pre_tokenizer"] and any(pretokenizer["type"] == "ByteLevel" for pretokenizer in tokenizer_json["pre_tokenizer"]["pretokenizers"])): kwargs["initial_alphabet"] = pre_tokenizers_fast.ByteLevel.alphabet()
        trainer_class = MODEL_TO_TRAINER_MAPPING[tokenizer_json["model"]["type"]]
        trainer = trainer_class(vocab_size=vocab_size, special_tokens=special_tokens, **kwargs)
        tokenizer.train_from_iterator(text_iterator, length=length, trainer=trainer)
        if post_processor is not None:
            trained_tokenizer_json = json.loads(tokenizer.to_str())
            if "special_tokens" in post_processor:
                for key in post_processor["special_tokens"]:
                    tokens = post_processor["special_tokens"][key]["tokens"]
                    if special_tokens_map is not None: tokens = [special_tokens_map.get(token, token) for token in tokens]
                    post_processor["special_tokens"][key]["tokens"] = tokens
                    for token in tokens:
                        token_id = tokenizer.token_to_id(token)
                        if token_id is None: raise ValueError("Attempted to set a token in the post processor that does not exist in the mapping")
                    post_processor["special_tokens"][key]["ids"] = [tokenizer.token_to_id(token) for token in tokens]
            for special_token in ["cls", "sep"]:
                if special_token in post_processor:
                    token, _ = post_processor[special_token]
                    if special_tokens_map is not None and token in special_tokens_map: token = special_tokens_map[token]
                    token_id = tokenizer.token_to_id(token)
                    if token_id is None: raise ValueError("Attempted to set a token in the post processor that does not exist in the mapping")
                    post_processor[special_token] = [token, token_id]
            trained_tokenizer_json["post_processor"] = post_processor
            tokenizer = TokenizerFast.from_str(json.dumps(trained_tokenizer_json))
        kwargs = self.init_kwargs.copy()
        special_tokens_list = SpecialTokensMixin.SPECIAL_TOKENS_ATTRIBUTES.copy()
        special_tokens_list.remove("additional_special_tokens")
        for token in special_tokens_list:
            if getattr(self, f"_{token}") is not None:
                special_token = getattr(self, token)
                if special_tokens_map is not None and special_token in special_tokens_map: special_token = special_tokens_map[special_token]
                special_token_full = getattr(self, f"_{token}")
                if isinstance(special_token_full, AddedToken): kwargs[token] = AddedToken(special_token, single_word=special_token_full.single_word, lstrip=special_token_full.lstrip, rstrip=special_token_full.rstrip, normalized=special_token_full.normalized, special=True)
                else: kwargs[token] = special_token
        additional_special_tokens = self.additional_special_tokens
        if new_special_tokens is not None: additional_special_tokens.extend(new_special_tokens)
        if len(additional_special_tokens) > 0: kwargs["additional_special_tokens"] = additional_special_tokens
        return self.__class__(tokenizer_object=tokenizer, **kwargs)
class SapiensPreTrainedTokenizerFast(PreTrainedTokenizerFast): pass
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
