"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import collections
import itertools
import json
import os
import unicodedata
from typing import Dict, List, Optional, Tuple, Union
from ...tokenization_utils import PreTrainedTokenizer, _is_control, _is_punctuation, _is_whitespace
from ...tokenization_utils_base import (ENCODE_KWARGS_DOCSTRING, ENCODE_PLUS_ADDITIONAL_KWARGS_DOCSTRING, BatchEncoding, EncodedInput, EncodedInputPair, PaddingStrategy,
PreTokenizedInput, PreTokenizedInputPair, TensorType, TextInput, TextInputPair, TruncationStrategy)
from ...utils import add_end_docstrings, logging
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {'vocab_file': 'vocab.txt', 'word_shape_file': 'word_shape.json', 'word_pronunciation_file': 'word_pronunciation.json'}
def load_vocab(vocab_file):
    vocab = collections.OrderedDict()
    with open(vocab_file, "r", encoding="utf-8") as reader: tokens = reader.readlines()
    for index, token in enumerate(tokens):
        token = token.rstrip("\n")
        vocab[token] = index
    return vocab
def whitespace_tokenize(text):
    text = text.strip()
    if not text: return []
    tokens = text.split()
    return tokens
class RoCBertTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    def __init__(self, vocab_file, word_shape_file, word_pronunciation_file, do_lower_case=True, do_basic_tokenize=True, never_split=None, unk_token="[UNK]",
    sep_token="[SEP]", pad_token="[PAD]", cls_token="[CLS]", mask_token="[MASK]", tokenize_chinese_chars=True, strip_accents=None, **kwargs):
        for cur_file in [vocab_file, word_shape_file, word_pronunciation_file]:
            if cur_file is None or not os.path.isfile(cur_file): raise ValueError(f"Can't find a vocabulary file at path '{vocab_file}'. To load the vocabulary from a Google pretrained model use `tokenizer = RoCBertTokenizer.from_pretrained(PRETRAINED_MODEL_NAME)`")
        self.vocab = load_vocab(vocab_file)
        with open(word_shape_file, "r", encoding="utf8") as in_file: self.word_shape = json.load(in_file)
        with open(word_pronunciation_file, "r", encoding="utf8") as in_file: self.word_pronunciation = json.load(in_file)
        self.ids_to_tokens = collections.OrderedDict([(ids, tok) for tok, ids in self.vocab.items()])
        self.do_basic_tokenize = do_basic_tokenize
        if do_basic_tokenize: self.basic_tokenizer = RoCBertBasicTokenizer(do_lower_case=do_lower_case, never_split=never_split, tokenize_chinese_chars=tokenize_chinese_chars, strip_accents=strip_accents)
        self.wordpiece_tokenizer = RoCBertWordpieceTokenizer(vocab=self.vocab, unk_token=str(unk_token))
        super().__init__(do_lower_case=do_lower_case, do_basic_tokenize=do_basic_tokenize, never_split=never_split, unk_token=unk_token, sep_token=sep_token,
        pad_token=pad_token, cls_token=cls_token, mask_token=mask_token, tokenize_chinese_chars=tokenize_chinese_chars, strip_accents=strip_accents, **kwargs)
    @property
    def do_lower_case(self): return self.basic_tokenizer.do_lower_case
    @property
    def vocab_size(self): return len(self.vocab)
    def get_vocab(self): return dict(self.vocab, **self.added_tokens_encoder)
    def _tokenize(self, text, split_special_tokens=False):
        split_tokens = []
        if self.do_basic_tokenize:
            for token in self.basic_tokenizer.tokenize(text, never_split=self.all_special_tokens if not split_special_tokens else None):
                if token in self.basic_tokenizer.never_split: split_tokens.append(token)
                else: split_tokens += self.wordpiece_tokenizer.tokenize(token)
        else: split_tokens = self.wordpiece_tokenizer.tokenize(text)
        return split_tokens
    def _encode_plus(self, text: Union[TextInput, PreTokenizedInput, EncodedInput], text_pair: Optional[Union[TextInput, PreTokenizedInput, EncodedInput]] = None,
    add_special_tokens: bool = True, padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD, truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE,
    max_length: Optional[int] = None, stride: int = 0, is_split_into_words: bool = False, pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None,
    return_tensors: Optional[Union[str, TensorType]] = None, return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None,
    return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False, return_length: bool = False,
    verbose: bool = True, **kwargs) -> BatchEncoding:
        def get_input_ids(text):
            if isinstance(text, str):
                tokens = self.tokenize(text, **kwargs)
                tokens_ids = self.convert_tokens_to_ids(tokens)
                tokens_shape_ids = self.convert_tokens_to_shape_ids(tokens)
                tokens_proun_ids = self.convert_tokens_to_pronunciation_ids(tokens)
                return tokens_ids, tokens_shape_ids, tokens_proun_ids
            elif isinstance(text, (list, tuple)) and len(text) > 0 and isinstance(text[0], str):
                if is_split_into_words:
                    tokens = list(itertools.chain(*(self.tokenize(t, is_split_into_words=True, **kwargs) for t in text)))
                    tokens_ids = self.convert_tokens_to_ids(tokens)
                    tokens_shape_ids = self.convert_tokens_to_shape_ids(tokens)
                    tokens_proun_ids = self.convert_tokens_to_pronunciation_ids(tokens)
                    return tokens_ids, tokens_shape_ids, tokens_proun_ids
                else:
                    tokens_ids = self.convert_tokens_to_ids(text)
                    tokens_shape_ids = self.convert_tokens_to_shape_ids(text)
                    tokens_proun_ids = self.convert_tokens_to_pronunciation_ids(text)
                    return tokens_ids, tokens_shape_ids, tokens_proun_ids
            elif isinstance(text, (list, tuple)) and len(text) > 0 and isinstance(text[0], int): return text, [0] * len(text), [0] * len(text)
            else:
                if is_split_into_words: raise ValueError(f"Input {text} is not valid. Should be a string or a list/tuple of strings when `is_split_into_words=True`.")
                else: raise ValueError(f"Input {text} is not valid. Should be a string, a list/tuple of strings or a list/tuple of integers.")
        if return_offsets_mapping: raise NotImplementedError("return_offset_mapping is not available when using Python tokenizers. To use this feature, change your tokenizer to one deriving from sapiens_transformers.PreTrainedTokenizerFast.")
        first_ids, first_shape_ids, first_proun_ids = get_input_ids(text)
        if text_pair is not None: second_ids, second_shape_ids, second_proun_ids = get_input_ids(text_pair)
        else: second_ids, second_shape_ids, second_proun_ids = None, None, None
        return self.prepare_for_model(first_ids, first_shape_ids, first_proun_ids, pair_ids=second_ids, pair_shape_ids=second_shape_ids, pair_pronunciation_ids=second_proun_ids,
        add_special_tokens=add_special_tokens, padding=padding_strategy.value, truncation=truncation_strategy.value, max_length=max_length, stride=stride, pad_to_multiple_of=pad_to_multiple_of,
        padding_side=padding_side, return_tensors=return_tensors, prepend_batch_axis=True, return_attention_mask=return_attention_mask, return_token_type_ids=return_token_type_ids,
        return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask, return_length=return_length, verbose=verbose)
    @add_end_docstrings(ENCODE_KWARGS_DOCSTRING, ENCODE_PLUS_ADDITIONAL_KWARGS_DOCSTRING)
    def prepare_for_model(self, ids: List[int], shape_ids: List[int], pronunciation_ids: List[int], pair_ids: Optional[List[int]] = None, pair_shape_ids: Optional[List[int]] = None,
    pair_pronunciation_ids: Optional[List[int]] = None, add_special_tokens: bool = True, padding: Union[bool, str, PaddingStrategy] = False, truncation: Union[bool, str, TruncationStrategy] = None,
    max_length: Optional[int] = None, stride: int = 0, pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None,
    return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False,
    return_offsets_mapping: bool = False, return_length: bool = False, verbose: bool = True, prepend_batch_axis: bool = False, **kwargs) -> BatchEncoding:
        padding_strategy, truncation_strategy, max_length, kwargs = self._get_padding_truncation_strategies(padding=padding, truncation=truncation, max_length=max_length,
        pad_to_multiple_of=pad_to_multiple_of, verbose=verbose, **kwargs)
        pair = bool(pair_ids is not None)
        len_ids = len(ids)
        len_pair_ids = len(pair_ids) if pair else 0
        if return_token_type_ids and not add_special_tokens: raise ValueError("Asking to return token_type_ids while setting add_special_tokens to False results in an undefined behavior. Please set add_special_tokens to True or set return_token_type_ids to None.")
        if (return_overflowing_tokens and truncation_strategy == TruncationStrategy.LONGEST_FIRST and pair_ids is not None): raise ValueError("Not possible to return overflowing tokens for pair of sequences with the `longest_first`. Please select another truncation strategy than `longest_first`, for instance `only_second` or `only_first`.")
        if return_token_type_ids is None: return_token_type_ids = "token_type_ids" in self.model_input_names
        if return_attention_mask is None: return_attention_mask = "attention_mask" in self.model_input_names
        encoded_inputs = {}
        total_len = len_ids + len_pair_ids + (self.num_special_tokens_to_add(pair=pair) if add_special_tokens else 0)
        overflowing_tokens = []
        if truncation_strategy != TruncationStrategy.DO_NOT_TRUNCATE and max_length and total_len > max_length:
            ids, pair_ids, overflowing_tokens = self.truncate_sequences(ids, pair_ids=pair_ids, num_tokens_to_remove=total_len - max_length, truncation_strategy=truncation_strategy, stride=stride)
            shape_ids, pair_shape_ids, _ = self.truncate_sequences(shape_ids, pair_ids=pair_shape_ids, num_tokens_to_remove=total_len - max_length, truncation_strategy=truncation_strategy, stride=stride)
            pronunciation_ids, pair_pronunciation_ids, _ = self.truncate_sequences(pronunciation_ids, pair_ids=pair_pronunciation_ids, num_tokens_to_remove=total_len - max_length, truncation_strategy=truncation_strategy, stride=stride)
        if return_overflowing_tokens:
            encoded_inputs["overflowing_tokens"] = overflowing_tokens
            encoded_inputs["num_truncated_tokens"] = total_len - max_length
        if add_special_tokens:
            sequence = self.build_inputs_with_special_tokens(ids, pair_ids)
            token_type_ids = self.create_token_type_ids_from_sequences(ids, pair_ids)
            input_shape_ids = self.build_inputs_with_special_tokens(shape_ids, pair_shape_ids, self.word_shape["[UNK]"], self.word_shape["[UNK]"])
            input_pronunciation_ids = self.build_inputs_with_special_tokens(pronunciation_ids, pair_pronunciation_ids, self.word_pronunciation["[UNK]"], self.word_pronunciation["[UNK]"])
        else:
            sequence = ids + pair_ids if pair_ids else ids
            token_type_ids = [0] * len(ids) + ([0] * len(pair_ids) if pair_ids else [])
            input_shape_ids = shape_ids + pair_shape_ids if pair_shape_ids else shape_ids
            input_pronunciation_ids = (pronunciation_ids + pair_pronunciation_ids if pair_pronunciation_ids else pronunciation_ids)
        encoded_inputs["input_ids"] = sequence
        encoded_inputs["input_shape_ids"] = input_shape_ids
        encoded_inputs["input_pronunciation_ids"] = input_pronunciation_ids
        if return_token_type_ids: encoded_inputs["token_type_ids"] = token_type_ids
        if return_special_tokens_mask:
            if add_special_tokens: encoded_inputs["special_tokens_mask"] = self.get_special_tokens_mask(ids, pair_ids)
            else: encoded_inputs["special_tokens_mask"] = [0] * len(sequence)
        self._eventual_warn_about_too_long_sequence(encoded_inputs["input_ids"], max_length, verbose)
        if padding_strategy != PaddingStrategy.DO_NOT_PAD or return_attention_mask: encoded_inputs = self.pad(encoded_inputs, max_length=max_length, padding=padding_strategy.value,
        pad_to_multiple_of=pad_to_multiple_of, padding_side=padding_side, return_attention_mask=return_attention_mask)
        if return_length: encoded_inputs["length"] = len(encoded_inputs["input_ids"])
        batch_outputs = BatchEncoding(encoded_inputs, tensor_type=return_tensors, prepend_batch_axis=prepend_batch_axis)
        return batch_outputs
    def _pad(self, encoded_inputs: Union[Dict[str, EncodedInput], BatchEncoding], max_length: Optional[int] = None, padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD,
    pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None, return_attention_mask: Optional[bool] = None) -> dict:
        if return_attention_mask is None: return_attention_mask = "attention_mask" in self.model_input_names
        required_input = encoded_inputs[self.model_input_names[0]]
        if padding_strategy == PaddingStrategy.LONGEST: max_length = len(required_input)
        if max_length is not None and pad_to_multiple_of is not None and (max_length % pad_to_multiple_of != 0): max_length = ((max_length // pad_to_multiple_of) + 1) * pad_to_multiple_of
        needs_to_be_padded = padding_strategy != PaddingStrategy.DO_NOT_PAD and len(required_input) != max_length
        if return_attention_mask and "attention_mask" not in encoded_inputs: encoded_inputs["attention_mask"] = [1] * len(required_input)
        if needs_to_be_padded:
            difference = max_length - len(required_input)
            padding_side = padding_side if padding_side is not None else self.padding_side
            if padding_side == "right":
                if return_attention_mask: encoded_inputs["attention_mask"] = encoded_inputs["attention_mask"] + [0] * difference
                if "token_type_ids" in encoded_inputs: encoded_inputs["token_type_ids"] = (encoded_inputs["token_type_ids"] + [self.pad_token_type_id] * difference)
                if "special_tokens_mask" in encoded_inputs: encoded_inputs["special_tokens_mask"] = encoded_inputs["special_tokens_mask"] + [1] * difference
                for key in ["input_shape_ids", "input_pronunciation_ids"]:
                    if key in encoded_inputs: encoded_inputs[key] = encoded_inputs[key] + [self.pad_token_id] * difference
                encoded_inputs[self.model_input_names[0]] = required_input + [self.pad_token_id] * difference
            elif padding_side == "left":
                if return_attention_mask: encoded_inputs["attention_mask"] = [0] * difference + encoded_inputs["attention_mask"]
                if "token_type_ids" in encoded_inputs: encoded_inputs["token_type_ids"] = [self.pad_token_type_id] * difference + encoded_inputs["token_type_ids"]
                if "special_tokens_mask" in encoded_inputs: encoded_inputs["special_tokens_mask"] = [1] * difference + encoded_inputs["special_tokens_mask"]
                for key in ["input_shape_ids", "input_pronunciation_ids"]:
                    if key in encoded_inputs: encoded_inputs[key] = [self.pad_token_id] * difference + encoded_inputs[key]
                encoded_inputs[self.model_input_names[0]] = [self.pad_token_id] * difference + required_input
            else: raise ValueError("Invalid padding strategy:" + str(padding_side))
        return encoded_inputs
    def _batch_encode_plus(self, batch_text_or_text_pairs: Union[List[TextInput], List[TextInputPair], List[PreTokenizedInput], List[PreTokenizedInputPair], List[EncodedInput], List[EncodedInputPair]],
    add_special_tokens: bool = True, padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD, truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE,
    max_length: Optional[int] = None, stride: int = 0, is_split_into_words: bool = False, pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None,
    return_tensors: Optional[Union[str, TensorType]] = None, return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None,
    return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False, return_length: bool = False,
    verbose: bool = True, **kwargs) -> BatchEncoding:
        def get_input_ids(text):
            if isinstance(text, str):
                tokens = self.tokenize(text, **kwargs)
                tokens_ids = self.convert_tokens_to_ids(tokens)
                tokens_shape_ids = self.convert_tokens_to_shape_ids(tokens)
                tokens_proun_ids = self.convert_tokens_to_pronunciation_ids(tokens)
                return tokens_ids, tokens_shape_ids, tokens_proun_ids
            elif isinstance(text, (list, tuple)) and len(text) > 0 and isinstance(text[0], str):
                if is_split_into_words:
                    tokens = list(itertools.chain(*(self.tokenize(t, is_split_into_words=True, **kwargs) for t in text)))
                    tokens_ids = self.convert_tokens_to_ids(tokens)
                    tokens_shape_ids = self.convert_tokens_to_shape_ids(tokens)
                    tokens_proun_ids = self.convert_tokens_to_pronunciation_ids(tokens)
                    return tokens_ids, tokens_shape_ids, tokens_proun_ids
                else:
                    tokens_ids = self.convert_tokens_to_ids(text)
                    tokens_shape_ids = self.convert_tokens_to_shape_ids(text)
                    tokens_proun_ids = self.convert_tokens_to_pronunciation_ids(text)
                    return tokens_ids, tokens_shape_ids, tokens_proun_ids
            elif isinstance(text, (list, tuple)) and len(text) > 0 and isinstance(text[0], int): return text, [0] * len(text), [0] * len(text)
            else: raise ValueError("Input is not valid. Should be a string, a list/tuple of strings or a list/tuple of integers.")
        if return_offsets_mapping: raise NotImplementedError("return_offset_mapping is not available when using Python tokenizers. To use this feature, change your tokenizer to one deriving from sapiens_transformers.PreTrainedTokenizerFast.")
        input_ids = []
        input_shape_ids = []
        input_pronunciation_ids = []
        for ids_or_pair_ids in batch_text_or_text_pairs:
            if not isinstance(ids_or_pair_ids, (list, tuple)): ids, pair_ids = ids_or_pair_ids, None
            elif is_split_into_words and not isinstance(ids_or_pair_ids[0], (list, tuple)): ids, pair_ids = ids_or_pair_ids, None
            else: ids, pair_ids = ids_or_pair_ids
            first_ids, first_shape_ids, first_proun_ids = get_input_ids(ids)
            if pair_ids is not None: second_ids, second_shape_ids, second_proun_ids = get_input_ids(pair_ids)
            else: second_ids, second_shape_ids, second_proun_ids = None, None, None
            input_ids.append((first_ids, second_ids))
            input_shape_ids.append((first_shape_ids, second_shape_ids))
            input_pronunciation_ids.append((first_proun_ids, second_proun_ids))
        batch_outputs = self._batch_prepare_for_model(input_ids, batch_shape_ids_pairs=input_shape_ids, batch_pronunciation_ids_pairs=input_pronunciation_ids,
        add_special_tokens=add_special_tokens, padding_strategy=padding_strategy, truncation_strategy=truncation_strategy, max_length=max_length, stride=stride,
        pad_to_multiple_of=pad_to_multiple_of, padding_side=padding_side, return_attention_mask=return_attention_mask, return_token_type_ids=return_token_type_ids,
        return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask, return_length=return_length,
        return_tensors=return_tensors, verbose=verbose)
        return BatchEncoding(batch_outputs)
    @add_end_docstrings(ENCODE_KWARGS_DOCSTRING, ENCODE_PLUS_ADDITIONAL_KWARGS_DOCSTRING)
    def _batch_prepare_for_model(self, batch_ids_pairs: List[Union[PreTokenizedInputPair, Tuple[List[int], None]]], batch_shape_ids_pairs: List[Union[PreTokenizedInputPair, Tuple[List[int], None]]],
    batch_pronunciation_ids_pairs: List[Union[PreTokenizedInputPair, Tuple[List[int], None]]], add_special_tokens: bool = True, padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD,
    truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE, max_length: Optional[int] = None, stride: int = 0, pad_to_multiple_of: Optional[int] = None,
    padding_side: Optional[bool] = None, return_tensors: Optional[str] = None, return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None,
    return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_length: bool = False, verbose: bool = True) -> BatchEncoding:
        batch_outputs = {}
        for i, (first_ids, second_ids) in enumerate(batch_ids_pairs):
            first_shape_ids, second_shape_ids = batch_shape_ids_pairs[i]
            first_pronunciation_ids, second_pronunciation_ids = batch_pronunciation_ids_pairs[i]
            outputs = self.prepare_for_model(first_ids, first_shape_ids, first_pronunciation_ids, pair_ids=second_ids, pair_shape_ids=second_shape_ids, pair_pronunciation_ids=second_pronunciation_ids,
            add_special_tokens=add_special_tokens, padding=PaddingStrategy.DO_NOT_PAD.value, truncation=truncation_strategy.value, max_length=max_length, stride=stride,
            pad_to_multiple_of=None, padding_side=None, return_attention_mask=False, return_token_type_ids=return_token_type_ids, return_overflowing_tokens=return_overflowing_tokens,
            return_special_tokens_mask=return_special_tokens_mask, return_length=return_length, return_tensors=None, prepend_batch_axis=False, verbose=verbose)
            for key, value in outputs.items():
                if key not in batch_outputs: batch_outputs[key] = []
                batch_outputs[key].append(value)
        batch_outputs = self.pad(batch_outputs, padding=padding_strategy.value, max_length=max_length, pad_to_multiple_of=pad_to_multiple_of, padding_side=padding_side, return_attention_mask=return_attention_mask)
        batch_outputs = BatchEncoding(batch_outputs, tensor_type=return_tensors)
        return batch_outputs
    def _convert_token_to_id(self, token): return self.vocab.get(token, self.vocab.get(self.unk_token))
    def _convert_token_to_shape_id(self, token): return self.word_shape.get(token, self.word_shape.get(self.unk_token))
    def convert_tokens_to_shape_ids(self, tokens: Union[str, List[str]]) -> Union[int, List[int]]:
        if tokens is None: return None
        ids = []
        for token in tokens: ids.append(self._convert_token_to_shape_id(token))
        return ids
    def _convert_token_to_pronunciation_id(self, token): return self.word_pronunciation.get(token, self.word_pronunciation.get(self.unk_token))
    def convert_tokens_to_pronunciation_ids(self, tokens: Union[str, List[str]]) -> Union[int, List[int]]:
        if tokens is None: return None
        ids = []
        for token in tokens: ids.append(self._convert_token_to_pronunciation_id(token))
        return ids
    def _convert_id_to_token(self, index): return self.ids_to_tokens.get(index, self.unk_token)
    def convert_tokens_to_string(self, tokens):
        out_string = " ".join(tokens).replace(" ##", "").strip()
        return out_string
    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None, cls_token_id: int = None, sep_token_id: int = None) -> List[int]:
        cls = [self.cls_token_id] if cls_token_id is None else [cls_token_id]
        sep = [self.sep_token_id] if sep_token_id is None else [sep_token_id]
        if token_ids_1 is None: return cls + token_ids_0 + sep
        return cls + token_ids_0 + sep + token_ids_1 + sep
    def get_special_tokens_mask(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens: return super().get_special_tokens_mask(token_ids_0=token_ids_0, token_ids_1=token_ids_1, already_has_special_tokens=True)
        if token_ids_1 is not None: return [1] + ([0] * len(token_ids_0)) + [1] + ([0] * len(token_ids_1)) + [1]
        return [1] + ([0] * len(token_ids_0)) + [1]
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        sep = [self.sep_token_id]
        cls = [self.cls_token_id]
        if token_ids_1 is None: return len(cls + token_ids_0 + sep) * [0]
        return len(cls + token_ids_0 + sep) * [0] + len(token_ids_1 + sep) * [1]
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str, str, str]:
        index = 0
        if os.path.isdir(save_directory):
            vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + self.vocab_files_names["vocab_file"])
            word_shape_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + self.vocab_files_names["word_shape_file"])
            word_pronunciation_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + self.vocab_files_names["word_pronunciation_file"])
        else: raise ValueError(f"Can't find a directory at path '{save_directory}'. To load the vocabulary from a Google pretrained model use `tokenizer = RoCBertTokenizer.from_pretrained(PRETRAINED_MODEL_NAME)`")
        with open(vocab_file, "w", encoding="utf-8") as writer:
            for token, token_index in sorted(self.vocab.items(), key=lambda kv: kv[1]):
                if index != token_index:
                    logger.warning(f"Saving vocabulary to {vocab_file}: vocabulary indices are not consecutive. Please check that the vocabulary is not corrupted!")
                    index = token_index
                writer.write(token + "\n")
                index += 1
        with open(word_shape_file, "w", encoding="utf8") as writer: json.dump(self.word_shape, writer, ensure_ascii=False, indent=4, separators=(", ", ": "))
        with open(word_pronunciation_file, "w", encoding="utf8") as writer: json.dump(self.word_pronunciation, writer, ensure_ascii=False, indent=4, separators=(", ", ": "))
        return (vocab_file, word_shape_file, word_pronunciation_file)
class RoCBertBasicTokenizer:
    def __init__(self, do_lower_case=True, never_split=None, tokenize_chinese_chars=True, strip_accents=None, do_split_on_punc=True):
        if never_split is None: never_split = []
        self.do_lower_case = do_lower_case
        self.never_split = set(never_split)
        self.tokenize_chinese_chars = tokenize_chinese_chars
        self.strip_accents = strip_accents
        self.do_split_on_punc = do_split_on_punc
    def tokenize(self, text, never_split=None):
        never_split = self.never_split.union(set(never_split)) if never_split else self.never_split
        text = self._clean_text(text)
        if self.tokenize_chinese_chars: text = self._tokenize_chinese_chars(text)
        unicode_normalized_text = unicodedata.normalize("NFC", text)
        orig_tokens = whitespace_tokenize(unicode_normalized_text)
        split_tokens = []
        for token in orig_tokens:
            if token not in never_split:
                if self.do_lower_case:
                    token = token.lower()
                    if self.strip_accents is not False: token = self._run_strip_accents(token)
                elif self.strip_accents: token = self._run_strip_accents(token)
            split_tokens.extend(self._run_split_on_punc(token, never_split))
        output_tokens = whitespace_tokenize(" ".join(split_tokens))
        return output_tokens
    def _run_strip_accents(self, text):
        text = unicodedata.normalize("NFD", text)
        output = []
        for char in text:
            cat = unicodedata.category(char)
            if cat == "Mn": continue
            output.append(char)
        return "".join(output)
    def _run_split_on_punc(self, text, never_split=None):
        if not self.do_split_on_punc or (never_split is not None and text in never_split): return [text]
        chars = list(text)
        i = 0
        start_new_word = True
        output = []
        while i < len(chars):
            char = chars[i]
            if _is_punctuation(char):
                output.append([char])
                start_new_word = True
            else:
                if start_new_word: output.append([])
                start_new_word = False
                output[-1].append(char)
            i += 1
        return ["".join(x) for x in output]
    def _tokenize_chinese_chars(self, text):
        output = []
        for char in text:
            cp = ord(char)
            if self._is_chinese_char(cp):
                output.append(" ")
                output.append(char)
                output.append(" ")
            else: output.append(char)
        return "".join(output)
    def _is_chinese_char(self, cp):
        if ((cp >= 0x4E00 and cp <= 0x9FFF) or (cp >= 0x3400 and cp <= 0x4DBF) or (cp >= 0x20000 and cp <= 0x2A6DF) or (cp >= 0x2A700 and cp <= 0x2B73F)
        or (cp >= 0x2B740 and cp <= 0x2B81F) or (cp >= 0x2B820 and cp <= 0x2CEAF) or (cp >= 0xF900 and cp <= 0xFAFF) or (cp >= 0x2F800 and cp <= 0x2FA1F)): return True
        return False
    def _clean_text(self, text):
        output = []
        for char in text:
            cp = ord(char)
            if cp == 0 or cp == 0xFFFD or _is_control(char): continue
            if _is_whitespace(char): output.append(" ")
            else: output.append(char)
        return "".join(output)
class RoCBertWordpieceTokenizer:
    def __init__(self, vocab, unk_token, max_input_chars_per_word=100):
        self.vocab = vocab
        self.unk_token = unk_token
        self.max_input_chars_per_word = max_input_chars_per_word
    def tokenize(self, text):
        output_tokens = []
        for token in whitespace_tokenize(text):
            chars = list(token)
            if len(chars) > self.max_input_chars_per_word:
                output_tokens.append(self.unk_token)
                continue
            is_bad = False
            start = 0
            sub_tokens = []
            while start < len(chars):
                end = len(chars)
                cur_substr = None
                while start < end:
                    substr = "".join(chars[start:end])
                    if start > 0: substr = "##" + substr
                    if substr in self.vocab:
                        cur_substr = substr
                        break
                    end -= 1
                if cur_substr is None:
                    is_bad = True
                    break
                sub_tokens.append(cur_substr)
                start = end
            if is_bad: output_tokens.append(self.unk_token)
            else: output_tokens.extend(sub_tokens)
        return output_tokens
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
