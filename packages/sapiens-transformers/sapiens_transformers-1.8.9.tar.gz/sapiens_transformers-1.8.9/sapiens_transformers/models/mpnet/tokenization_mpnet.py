"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import collections
import os
import unicodedata
from typing import List, Optional, Tuple
from ...tokenization_utils import AddedToken, PreTrainedTokenizer, _is_control, _is_punctuation, _is_whitespace
from ...utils import logging
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "vocab.txt"}
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
class MPNetTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, vocab_file, do_lower_case=True, do_basic_tokenize=True, never_split=None, bos_token="<s>", eos_token="</s>", sep_token="</s>", cls_token="<s>",
    unk_token="[UNK]", pad_token="<pad>", mask_token="<mask>", tokenize_chinese_chars=True, strip_accents=None, clean_up_tokenization_spaces=True, **kwargs):
        bos_token = AddedToken(bos_token, special=True) if isinstance(bos_token, str) else bos_token
        eos_token = AddedToken(eos_token, special=True) if isinstance(eos_token, str) else eos_token
        sep_token = AddedToken(sep_token, special=True) if isinstance(sep_token, str) else sep_token
        cls_token = AddedToken(cls_token, special=True) if isinstance(cls_token, str) else cls_token
        unk_token = AddedToken(unk_token, special=True) if isinstance(unk_token, str) else unk_token
        pad_token = AddedToken(pad_token, special=True) if isinstance(pad_token, str) else pad_token
        mask_token = AddedToken(mask_token, lstrip=True, special=True) if isinstance(mask_token, str) else mask_token
        if not os.path.isfile(vocab_file): raise ValueError(f"Can't find a vocabulary file at path '{vocab_file}'. To load the vocabulary from a Google pretrained model use `tokenizer = AutoTokenizer.from_pretrained(PRETRAINED_MODEL_NAME)`")
        self.vocab = load_vocab(vocab_file)
        self.ids_to_tokens = collections.OrderedDict([(ids, tok) for tok, ids in self.vocab.items()])
        self.do_basic_tokenize = do_basic_tokenize
        if do_basic_tokenize: self.basic_tokenizer = BasicTokenizer(do_lower_case=do_lower_case, never_split=never_split, tokenize_chinese_chars=tokenize_chinese_chars, strip_accents=strip_accents)
        self.wordpiece_tokenizer = WordpieceTokenizer(vocab=self.vocab, unk_token=str(unk_token))
        super().__init__(do_lower_case=do_lower_case, do_basic_tokenize=do_basic_tokenize, never_split=never_split, bos_token=bos_token, eos_token=eos_token, unk_token=unk_token,
        sep_token=sep_token, cls_token=cls_token, pad_token=pad_token, mask_token=mask_token, tokenize_chinese_chars=tokenize_chinese_chars, strip_accents=strip_accents,
        clean_up_tokenization_spaces=clean_up_tokenization_spaces, **kwargs)
    @property
    def do_lower_case(self): return self.basic_tokenizer.do_lower_case
    @property
    def vocab_size(self): return len(self.vocab)
    def get_vocab(self):
        vocab = self.added_tokens_encoder.copy()
        vocab.update(self.vocab)
        return vocab
    def _tokenize(self, text):
        split_tokens = []
        if self.do_basic_tokenize:
            for token in self.basic_tokenizer.tokenize(text, never_split=self.all_special_tokens):
                if token in self.basic_tokenizer.never_split: split_tokens.append(token)
                else: split_tokens += self.wordpiece_tokenizer.tokenize(token)
        else: split_tokens = self.wordpiece_tokenizer.tokenize(text)
        return split_tokens
    def _convert_token_to_id(self, token): return self.vocab.get(token, self.vocab.get(self.unk_token))
    def _convert_id_to_token(self, index): return self.ids_to_tokens.get(index, self.unk_token)
    def convert_tokens_to_string(self, tokens):
        out_string = " ".join(tokens).replace(" ##", "").strip()
        return out_string
    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        if token_ids_1 is None: return [self.cls_token_id] + token_ids_0 + [self.sep_token_id]
        cls = [self.cls_token_id]
        sep = [self.sep_token_id]
        return cls + token_ids_0 + sep + sep + token_ids_1 + sep
    def get_special_tokens_mask(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens: return super().get_special_tokens_mask(token_ids_0=token_ids_0, token_ids_1=token_ids_1, already_has_special_tokens=True)
        if token_ids_1 is None: return [1] + ([0] * len(token_ids_0)) + [1]
        return [1] + ([0] * len(token_ids_0)) + [1, 1] + ([0] * len(token_ids_1)) + [1]
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        sep = [self.sep_token_id]
        cls = [self.cls_token_id]
        if token_ids_1 is None: return len(cls + token_ids_0 + sep) * [0]
        return len(cls + token_ids_0 + sep + sep + token_ids_1 + sep) * [0]
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        index = 0
        if os.path.isdir(save_directory): vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab_file"])
        else: vocab_file = (filename_prefix + "-" if filename_prefix else "") + save_directory
        with open(vocab_file, "w", encoding="utf-8") as writer:
            for token, token_index in sorted(self.vocab.items(), key=lambda kv: kv[1]):
                if index != token_index:
                    logger.warning(f"Saving vocabulary to {vocab_file}: vocabulary indices are not consecutive. Please check that the vocabulary is not corrupted!")
                    index = token_index
                writer.write(token + "\n")
                index += 1
        return (vocab_file,)
class BasicTokenizer:
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
class WordpieceTokenizer:
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
