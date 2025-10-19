"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import json
import os
import warnings
from functools import lru_cache
from typing import List, Optional, Tuple, Union
import numpy as np
import regex as re
from ...tokenization_utils import AddedToken, PreTrainedTokenizer
from ...utils import logging
from .english_normalizer import BasicTextNormalizer, EnglishTextNormalizer
VOCAB_FILES_NAMES = {'vocab_file': 'vocab.json', 'tokenizer_file': 'tokenizer.json', 'merges_file': 'merges.txt', 'normalizer_file': 'normalizer.json'}
MAX_MODEL_INPUT_SIZES = {'openai/whisper-base': 448}
def bytes_to_unicode():
    bs = (list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1)))
    cs = bs[:]
    n = 0
    for b in range(2**8):
        if b not in bs:
            bs.append(b)
            cs.append(2**8 + n)
            n += 1
    cs = [chr(n) for n in cs]
    return dict(zip(bs, cs))
logger = logging.get_logger(__name__)
def get_pairs(word):
    pairs = set()
    prev_char = word[0]
    for char in word[1:]:
        pairs.add((prev_char, char))
        prev_char = char
    return pairs
LANGUAGES = {'en': 'english', 'zh': 'chinese', 'de': 'german', 'es': 'spanish', 'ru': 'russian', 'ko': 'korean', 'fr': 'french', 'ja': 'japanese', 'pt': 'portuguese',
'tr': 'turkish', 'pl': 'polish', 'ca': 'catalan', 'nl': 'dutch', 'ar': 'arabic', 'sv': 'swedish', 'it': 'italian', 'id': 'indonesian', 'hi': 'hindi', 'fi': 'finnish',
'vi': 'vietnamese', 'he': 'hebrew', 'uk': 'ukrainian', 'el': 'greek', 'ms': 'malay', 'cs': 'czech', 'ro': 'romanian', 'da': 'danish', 'hu': 'hungarian', 'ta': 'tamil',
'no': 'norwegian', 'th': 'thai', 'ur': 'urdu', 'hr': 'croatian', 'bg': 'bulgarian', 'lt': 'lithuanian', 'la': 'latin', 'mi': 'maori', 'ml': 'malayalam', 'cy': 'welsh',
'sk': 'slovak', 'te': 'telugu', 'fa': 'persian', 'lv': 'latvian', 'bn': 'bengali', 'sr': 'serbian', 'az': 'azerbaijani', 'sl': 'slovenian', 'kn': 'kannada', 'et': 'estonian',
'mk': 'macedonian', 'br': 'breton', 'eu': 'basque', 'is': 'icelandic', 'hy': 'armenian', 'ne': 'nepali', 'mn': 'mongolian', 'bs': 'bosnian', 'kk': 'kazakh', 'sq': 'albanian',
'sw': 'swahili', 'gl': 'galician', 'mr': 'marathi', 'pa': 'punjabi', 'si': 'sinhala', 'km': 'khmer', 'sn': 'shona', 'yo': 'yoruba', 'so': 'somali', 'af': 'afrikaans',
'oc': 'occitan', 'ka': 'georgian', 'be': 'belarusian', 'tg': 'tajik', 'sd': 'sindhi', 'gu': 'gujarati', 'am': 'amharic', 'yi': 'yiddish', 'lo': 'lao', 'uz': 'uzbek',
'fo': 'faroese', 'ht': 'haitian creole', 'ps': 'pashto', 'tk': 'turkmen', 'nn': 'nynorsk', 'mt': 'maltese', 'sa': 'sanskrit', 'lb': 'luxembourgish', 'my': 'myanmar',
'bo': 'tibetan', 'tl': 'tagalog', 'mg': 'malagasy', 'as': 'assamese', 'tt': 'tatar', 'haw': 'hawaiian', 'ln': 'lingala', 'ha': 'hausa', 'ba': 'bashkir',
'jw': 'javanese', 'su': 'sundanese', 'yue': 'cantonese'}
TO_LANGUAGE_CODE = {**{language: code for code, language in LANGUAGES.items()}, "burmese": "my", "valencian": "ca", "flemish": "nl", "haitian": "ht", "letzeburgesch": "lb",
"pushto": "ps", "panjabi": "pa", "moldavian": "ro", "moldovan": "ro", "sinhalese": "si", "castilian": "es", "mandarin": "zh"}
TASK_IDS = ["translate", "transcribe"]
class WhisperTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, vocab_file, merges_file, normalizer_file=None, errors="replace", unk_token="<|endoftext|>", bos_token="<|endoftext|>", eos_token="<|endoftext|>",
    pad_token=None, add_prefix_space=False, language=None, task=None, predict_timestamps=False, **kwargs):
        bos_token = (AddedToken(bos_token, lstrip=False, rstrip=False, normalized=False, special=True) if isinstance(bos_token, str) else bos_token)
        eos_token = (AddedToken(eos_token, lstrip=False, rstrip=False, normalized=False, special=True) if isinstance(eos_token, str) else eos_token)
        unk_token = (AddedToken(unk_token, lstrip=False, rstrip=False, normalized=False, special=True) if isinstance(unk_token, str) else unk_token)
        pad_token = (AddedToken(pad_token, lstrip=False, rstrip=False, normalized=False, special=True) if isinstance(pad_token, str) else pad_token)
        with open(vocab_file, encoding="utf-8") as vocab_handle: self.encoder = json.load(vocab_handle)
        self.decoder = {v: k for k, v in self.encoder.items()}
        self.errors = errors
        self.byte_encoder = bytes_to_unicode()
        self.byte_decoder = {v: k for k, v in self.byte_encoder.items()}
        with open(merges_file, encoding="utf-8") as merges_handle: bpe_merges = merges_handle.read().split("\n")[1:-1]
        bpe_merges = [tuple(merge.split()) for merge in bpe_merges]
        self.bpe_ranks = dict(zip(bpe_merges, range(len(bpe_merges))))
        self.cache = {}
        self.add_prefix_space = add_prefix_space
        if normalizer_file is not None:
            with open(normalizer_file, encoding="utf-8") as vocab_handle: self.english_spelling_normalizer = json.load(vocab_handle)
        else: self.english_spelling_normalizer = None
        self.pat = re.compile(r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+""")
        self.timestamp_pat = re.compile(r"<\|(\d+\.\d+)\|>")
        self.language = language
        super().__init__(errors=errors, unk_token=unk_token, bos_token=bos_token, eos_token=eos_token, pad_token=pad_token, add_prefix_space=add_prefix_space, **kwargs)
        self.task = task
        self.predict_timestamps = predict_timestamps
    @property
    def vocab_size(self) -> int: return len(self.encoder)
    def get_vocab(self):
        vocab = {self.convert_ids_to_tokens(i): i for i in range(self.vocab_size)}
        vocab.update(self.added_tokens_encoder)
        return vocab
    def bpe(self, token):
        if token in self.cache: return self.cache[token]
        word = tuple(token)
        pairs = get_pairs(word)
        if not pairs: return token
        while True:
            bigram = min(pairs, key=lambda pair: self.bpe_ranks.get(pair, float("inf")))
            if bigram not in self.bpe_ranks: break
            first, second = bigram
            new_word = []
            i = 0
            while i < len(word):
                try: j = word.index(first, i)
                except ValueError:
                    new_word.extend(word[i:])
                    break
                else:
                    new_word.extend(word[i:j])
                    i = j
                if word[i] == first and i < len(word) - 1 and word[i + 1] == second:
                    new_word.append(first + second)
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1
            new_word = tuple(new_word)
            word = new_word
            if len(word) == 1: break
            else: pairs = get_pairs(word)
        word = " ".join(word)
        self.cache[token] = word
        return word
    def set_prefix_tokens(self, language: str = None, task: str = None, predict_timestamps: bool = None):
        self.language = language if language is not None else self.language
        self.task = task if task is not None else self.task
        self.predict_timestamps = predict_timestamps if predict_timestamps is not None else self.predict_timestamps
    @property
    def prefix_tokens(self) -> List[int]:
        bos_token_id = self.convert_tokens_to_ids("<|startoftranscript|>")
        translate_token_id = self.convert_tokens_to_ids("<|translate|>")
        transcribe_token_id = self.convert_tokens_to_ids("<|transcribe|>")
        notimestamps_token_id = self.convert_tokens_to_ids("<|notimestamps|>")
        langs = tuple(LANGUAGES.keys())
        if self.language is not None:
            self.language = self.language.lower()
            if self.language in TO_LANGUAGE_CODE: language_id = TO_LANGUAGE_CODE[self.language]
            elif self.language in TO_LANGUAGE_CODE.values(): language_id = self.language
            else:
                is_language_code = len(self.language) == 2
                raise ValueError(f"Unsupported language: {self.language}. Language should be one of: {list(TO_LANGUAGE_CODE.values()) if is_language_code else list(TO_LANGUAGE_CODE.keys())}.")
        if self.task is not None:
            if self.task not in TASK_IDS: raise ValueError(f"Unsupported task: {self.task}. Task should be in: {TASK_IDS}")
        bos_sequence = [bos_token_id]
        if self.language is not None: bos_sequence.append(bos_token_id + 1 + langs.index(language_id))
        if self.task is not None: bos_sequence.append(transcribe_token_id if self.task == "transcribe" else translate_token_id)
        if not self.predict_timestamps: bos_sequence.append(notimestamps_token_id)
        return bos_sequence
    def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None) -> List[int]:
        if token_ids_1 is None: return self.prefix_tokens + token_ids_0 + [self.eos_token_id]
        return self.prefix_tokens + token_ids_0 + token_ids_1 + [self.eos_token_id]
    def get_special_tokens_mask(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens: return super().get_special_tokens_mask(token_ids_0=token_ids_0, token_ids_1=token_ids_1, already_has_special_tokens=True)
        prefix_ones = [1] * len(self.prefix_tokens)
        suffix_ones = [1]
        if token_ids_1 is None: return prefix_ones + ([0] * len(token_ids_0)) + suffix_ones
        return prefix_ones + ([0] * len(token_ids_0)) + ([0] * len(token_ids_1)) + suffix_ones
    def _tokenize(self, text):
        bpe_tokens = []
        for token in re.findall(self.pat, text):
            token = "".join(self.byte_encoder[b] for b in token.encode("utf-8"))
            bpe_tokens.extend(bpe_token for bpe_token in self.bpe(token).split(" "))
        return bpe_tokens
    def _convert_token_to_id(self, token): return self.encoder.get(token, self.encoder.get(self.unk_token))
    def _convert_id_to_token(self, index): return self.decoder.get(index, "")
    def _normalize(self, text):
        warnings.warn("The private method `_normalize` is deprecated and will be removed in v1 of Sapiens Transformers. You can normalize an input string using the Whisper English normalizer using the `normalize` method.")
        return self.normalize(text)
    def _basic_normalize(self, text, remove_diacritics=False):
        warnings.warn("The private method `_basic_normalize` is deprecated and will be removed in v1 of Sapiens Transformers. You can normalize an input string using the Whisper basic normalizer using the `basic_normalize` method.")
        return self.basic_normalize(text, remove_diacritics=remove_diacritics)
    def normalize(self, text):
        normalizer = EnglishTextNormalizer(self.english_spelling_normalizer)
        return normalizer(text)
    @staticmethod
    def basic_normalize(text, remove_diacritics=False):
        normalizer = BasicTextNormalizer(remove_diacritics=remove_diacritics)
        return normalizer(text)
    def _decode_with_timestamps(self, token_ids, skip_special_tokens=False, time_precision=0.02) -> str:
        timestamp_begin = self.all_special_ids[-1] + 1
        outputs = [[]]
        cur_max_timestamp = 0.0
        prev_segments_len = 0.0
        for token in token_ids:
            if token >= timestamp_begin:
                timestamp = float((token - timestamp_begin) * time_precision)
                if timestamp < cur_max_timestamp: prev_segments_len += cur_max_timestamp
                cur_max_timestamp = timestamp
                outputs.append(f"<|{(timestamp + prev_segments_len):.2f}|>")
                outputs.append([])
            else: outputs[-1].append(token)
        outputs = [s if isinstance(s, str) else self.decode(s, skip_special_tokens=skip_special_tokens) for s in outputs]
        return "".join(outputs)
    def _compute_offsets(self, token_ids, time_precision=0.02):
        offsets = []
        if "torch" in str(type(token_ids)) and (hasattr(token_ids, "cpu") and callable(token_ids.cpu)): token_ids = token_ids.cpu()
        token_ids = np.array(token_ids)
        if token_ids.shape[0] > 1 and len(token_ids.shape) > 1: raise ValueError("Can only process a single input at a time")
        timestamp_begin = self.all_special_ids[-1] + 1
        timestamp_tokens = token_ids >= timestamp_begin
        consecutive = np.where(timestamp_tokens[:-1] & timestamp_tokens[1:])[0] + 1
        if consecutive.shape[0] == 0 and timestamp_tokens.sum() <= 1: return []
        elif np.where(timestamp_tokens)[0][-1] + 1 not in consecutive: consecutive = np.append(consecutive, np.where(timestamp_tokens)[0][-1] + 1)
        last_slice = np.where(timestamp_tokens)[0][0]
        cur_max_timestamp = 0
        prev_segments_len = 0
        for current_slice in consecutive:
            sliced_tokens = token_ids[last_slice:current_slice]
            if len(sliced_tokens) > 1:
                start_timestamp_position = sliced_tokens[0].item() - timestamp_begin
                end_timestamp_position = sliced_tokens[-1].item() - timestamp_begin
                if start_timestamp_position < cur_max_timestamp: prev_segments_len += cur_max_timestamp
                cur_max_timestamp = end_timestamp_position
                sliced_tokens = self._preprocess_token_ids(sliced_tokens)
                text = self._decode(sliced_tokens)
                text = self._filter_timestamp_ids(text)
                offsets.append({"text": text, "timestamp": ((start_timestamp_position + prev_segments_len) * time_precision, (end_timestamp_position + prev_segments_len) * time_precision)})
            last_slice = current_slice
        return offsets
    @lru_cache
    def timestamp_ids(self, time_precision=0.02): return self.convert_tokens_to_ids([("<|%.2f|>" % (i * time_precision)) for i in range(1500 + 1)])
    def _preprocess_token_ids(self, token_ids, skip_special_tokens: bool = False):
        if skip_special_tokens:
            prompt_token_id = self.convert_tokens_to_ids("<|startofprev|>")
            decoder_start_token_id = self.convert_tokens_to_ids("<|startoftranscript|>")
            token_ids = self._strip_prompt(token_ids, prompt_token_id, decoder_start_token_id)
        return token_ids
    def _filter_timestamp_ids(self, token_ids): return re.sub(self.timestamp_pat, "", token_ids)
    def decode(self, token_ids, skip_special_tokens: bool = False, clean_up_tokenization_spaces: bool = None, output_offsets: bool = False, time_precision: float = 0.02,
    decode_with_timestamps: bool = False, normalize: bool = False, basic_normalize: bool = False, remove_diacritics: bool = False, **kwargs) -> str:
        filtered_ids = self._preprocess_token_ids(token_ids, skip_special_tokens=skip_special_tokens)
        text = super().decode(filtered_ids, skip_special_tokens=skip_special_tokens, clean_up_tokenization_spaces=clean_up_tokenization_spaces, normalize=normalize,
        basic_normalize=basic_normalize, remove_diacritics=remove_diacritics, **kwargs)
        if decode_with_timestamps: text = self._decode_with_timestamps(filtered_ids, time_precision=time_precision, skip_special_tokens=skip_special_tokens)
        else: text = self._filter_timestamp_ids(text)
        if output_offsets:
            offsets = self._compute_offsets(token_ids, time_precision=time_precision)
            return {"text": text, "offsets": offsets}
        return text
    def _decode(self, token_ids: Union[int, List[int]], skip_special_tokens: bool = False, normalize: bool = False, basic_normalize: bool = False, remove_diacritics: bool = False, **kwargs) -> str:
        self._decode_use_source_tokenizer = kwargs.pop("use_source_tokenizer", False)
        filtered_tokens = self.convert_ids_to_tokens(token_ids, skip_special_tokens=skip_special_tokens)
        sub_texts = []
        current_sub_text = []
        for token in filtered_tokens:
            if skip_special_tokens and token in self.all_special_ids: continue
            if token in self.added_tokens_encoder:
                if current_sub_text:
                    sub_texts.append(self.convert_tokens_to_string(current_sub_text))
                    current_sub_text = []
                sub_texts.append(token)
            else: current_sub_text.append(token)
        if current_sub_text: sub_texts.append(self.convert_tokens_to_string(current_sub_text))
        text = "".join(sub_texts)
        if normalize:
            clean_text = self.normalize(text)
            return clean_text
        elif basic_normalize:
            clean_text = self.basic_normalize(text, remove_diacritics=remove_diacritics)
            return clean_text
        else: return text
    def convert_tokens_to_string(self, tokens):
        text = "".join(tokens)
        text = bytearray([self.byte_decoder[c] for c in text]).decode("utf-8", errors=self.errors)
        return text
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        if not os.path.isdir(save_directory):
            logger.error(f"Vocabulary path ({save_directory}) should be a directory")
            return
        vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab_file"])
        merge_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["merges_file"])
        normalizer_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["normalizer_file"])
        with open(vocab_file, "w", encoding="utf-8") as f: f.write(json.dumps(self.encoder, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
        index = 0
        with open(merge_file, "w", encoding="utf-8") as writer:
            writer.write("#version: 0.2\n")
            for bpe_tokens, token_index in sorted(self.bpe_ranks.items(), key=lambda kv: kv[1]):
                if index != token_index:
                    logger.warning(f"Saving vocabulary to {merge_file}: BPE merge indices are not consecutive. Please check that the tokenizer is not corrupted!")
                    index = token_index
                writer.write(" ".join(bpe_tokens) + "\n")
                index += 1
        if self.english_spelling_normalizer is not None:
            with open(normalizer_file, "w", encoding="utf-8") as f: f.write(json.dumps(self.english_spelling_normalizer, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
        return vocab_file, merge_file, normalizer_file
    def prepare_for_tokenization(self, text, is_split_into_words=False, **kwargs):
        add_prefix_space = kwargs.pop("add_prefix_space", self.add_prefix_space)
        if is_split_into_words or add_prefix_space: text = " " + text
        return (text, kwargs)
    def get_decoder_prompt_ids(self, task=None, language=None, no_timestamps=True):
        self.set_prefix_tokens(task=task, language=language, predict_timestamps=not no_timestamps)
        forced_tokens = self.prefix_tokens[1:]
        forced_decoder_ids = [(rank + 1, token) for rank, token in enumerate(forced_tokens)]
        return forced_decoder_ids
    def _decode_asr(self, model_outputs, *, return_timestamps, return_language, time_precision): return _decode_asr(self, model_outputs, return_timestamps=return_timestamps, return_language=return_language, time_precision=time_precision)
    def get_prompt_ids(self, text: str, return_tensors="np"):
        batch_encoding = self("<|startofprev|>", " " + text.strip(), add_special_tokens=False)
        prompt_text_ids = batch_encoding["input_ids"][1:]
        special_token_id = next((x for x in prompt_text_ids if x >= self.all_special_ids[0]), None)
        if special_token_id is not None:
            token = self.convert_ids_to_tokens(special_token_id)
            raise ValueError(f"Encountered text in the prompt corresponding to disallowed special token: {token}.")
        batch_encoding.convert_to_tensors(tensor_type=return_tensors)
        return batch_encoding["input_ids"]
    def _strip_prompt(self, token_ids: List[int], prompt_token_id: int, decoder_start_token_id: int):
        if not isinstance(token_ids, list): token_ids = self._convert_to_list(token_ids)
        if not token_ids: return token_ids
        has_prompt = token_ids[0] == prompt_token_id
        if has_prompt:
            if decoder_start_token_id in token_ids: return token_ids[token_ids.index(decoder_start_token_id) :]
            else: return []
        return token_ids
    @staticmethod
    def _convert_to_list(token_ids):
        if hasattr(token_ids, "numpy"):
            if "torch" in str(type(token_ids)): token_ids = token_ids.cpu().numpy()
            elif "tensorflow" in str(type(token_ids)): token_ids = token_ids.numpy()
        elif "jaxlib" in str(type(token_ids)): token_ids = token_ids.tolist()
        if isinstance(token_ids, np.ndarray): token_ids = token_ids.tolist()
        return token_ids
def _decode_asr(tokenizer, model_outputs, *, return_timestamps, return_language, time_precision):
    last_language = None
    def new_chunk(): return {"language": last_language, "timestamp": [None, None], "text": ""}
    chunks = []
    chunk = new_chunk()
    time_offset = 0.0
    timestamp_begin = tokenizer.convert_tokens_to_ids("<|notimestamps|>") + 1
    previous_tokens = []
    previous_token_timestamps = []
    skip = False
    right_stride_start = None
    all_special_ids = set(tokenizer.all_special_ids)
    prompt_token_id = tokenizer.convert_tokens_to_ids("<|startofprev|>")
    decoder_start_token_id = tokenizer.convert_tokens_to_ids("<|startoftranscript|>")
    for chunk_id, output in enumerate(model_outputs):
        token_ids = output["tokens"][0].tolist()
        token_ids = tokenizer._strip_prompt(token_ids, prompt_token_id, decoder_start_token_id)
        if return_timestamps == "word": token_timestamps = output["token_timestamps"][0].tolist()
        last_timestamp = None
        first_timestamp = timestamp_begin
        if "stride" in output:
            chunk_len, stride_left, stride_right = output["stride"]
            time_offset -= stride_left
            right_stride_start = chunk_len - stride_right
            if stride_left: first_timestamp = stride_left / time_precision + timestamp_begin
            if stride_right:
                for token in reversed(token_ids):
                    if token >= timestamp_begin:
                        if (last_timestamp is not None and (token - timestamp_begin) * time_precision < right_stride_start): break
                        last_timestamp = token
        current_tokens = []
        current_token_timestamps = []
        for i, token in enumerate(token_ids):
            if token in all_special_ids:
                text = tokenizer.decode([token])
                text = text[2:-2]
                language = LANGUAGES.get(text, None)
                if language is not None:
                    if last_language and language != last_language and not return_timestamps:
                        previous_tokens.append(current_tokens)
                        resolved_tokens = _find_longest_common_sequence(previous_tokens)
                        resolved_text = tokenizer.decode(resolved_tokens)
                        chunk["text"] = resolved_text
                        chunks.append(chunk)
                        previous_tokens = []
                        current_tokens = []
                        chunk = new_chunk()
                    chunk["language"] = language
                    last_language = language
                else: pass
            elif token >= timestamp_begin:
                time = (token - timestamp_begin) * time_precision + time_offset
                time = round(time, 2)
                if last_timestamp and token >= last_timestamp: skip = True
                elif skip or (previous_tokens and token < first_timestamp): skip = False
                elif chunk["timestamp"][0] is None: chunk["timestamp"][0] = time
                else:
                    if time == chunk["timestamp"][0]: pass
                    else:
                        chunk["timestamp"][1] = time
                        previous_tokens.append(current_tokens)
                        if return_timestamps == "word": previous_token_timestamps.append(current_token_timestamps)
                        resolved_tokens, resolved_token_timestamps = _find_longest_common_sequence(previous_tokens, previous_token_timestamps)
                        resolved_text = tokenizer.decode(resolved_tokens)
                        chunk["text"] = resolved_text
                        if return_timestamps == "word": chunk["words"] = _collate_word_timestamps(tokenizer, resolved_tokens, resolved_token_timestamps, last_language, return_language)
                        chunks.append(chunk)
                        previous_tokens = []
                        current_tokens = []
                        previous_token_timestamps = []
                        current_token_timestamps = []
                        chunk = new_chunk()
            else:
                current_tokens.append(token)
                if return_timestamps == "word":
                    start_time = round(token_timestamps[i] + time_offset, 2)
                    if i + 1 < len(token_timestamps): end_time = round(token_timestamps[i + 1] + time_offset, 2)
                    else: end_time = None
                    current_token_timestamps.append((start_time, end_time))
        if "stride" in output: time_offset += chunk_len - stride_right
        if current_tokens:
            previous_tokens.append(current_tokens)
            if return_timestamps == "word": previous_token_timestamps.append(current_token_timestamps)
        elif not (any(p for p in previous_tokens)):
            chunk = new_chunk()
            previous_tokens = []
            current_tokens = []
            previous_token_timestamps = []
            current_token_timestamps = []
    if previous_tokens:
        if return_timestamps: logger.warning("Whisper did not predict an ending timestamp, which can happen if audio is cut off in the middle of a word. Also make sure WhisperTimeStampLogitsProcessor was used during generation.")
        resolved_tokens, resolved_token_timestamps = _find_longest_common_sequence(previous_tokens, previous_token_timestamps)
        resolved_text = tokenizer.decode(resolved_tokens)
        chunk["text"] = resolved_text
        if return_timestamps == "word": chunk["words"] = _collate_word_timestamps(tokenizer, resolved_tokens, resolved_token_timestamps, last_language, return_language)
        chunks.append(chunk)
    full_text = "".join(chunk["text"] for chunk in chunks)
    if return_timestamps or return_language:
        for chunk in chunks:
            if not return_timestamps: chunk.pop("timestamp")
            else: chunk["timestamp"] = tuple(chunk["timestamp"])
            if not return_language: chunk.pop("language")
        if return_timestamps == "word":
            new_chunks = []
            for chunk in chunks: new_chunks.extend(chunk["words"])
            optional = {"chunks": new_chunks}
        else: optional = {"chunks": chunks}
    else: optional = {}
    return full_text, optional
def _find_longest_common_sequence(sequences, token_timestamp_sequences=None):
    left_sequence = sequences[0]
    left_length = len(left_sequence)
    total_sequence = []
    if token_timestamp_sequences:
        left_token_timestamp_sequence = token_timestamp_sequences[0]
        total_token_timestamp_sequence = []
    for seq_idx, right_sequence in enumerate(sequences[1:]):
        max_ = 0.0
        max_indices = (left_length, left_length, 0, 0)
        right_length = len(right_sequence)
        for i in range(1, left_length + right_length):
            eps = i / 10000.0
            left_start = max(0, left_length - i)
            left_stop = min(left_length, left_length + right_length - i)
            left = np.array(left_sequence[left_start:left_stop])
            right_start = max(0, i - left_length)
            right_stop = min(right_length, i)
            right = np.array(right_sequence[right_start:right_stop])
            if len(left) != len(right): raise RuntimeError("There is a bug within whisper `decode_asr` function, please report it. Dropping to prevent bad inference.")
            if token_timestamp_sequences: matches = sum(1 for idx, elem in enumerate(left) if (elem == right[idx] and left_token_timestamp_sequence[left_start + idx] <= token_timestamp_sequences[seq_idx + 1][right_start + idx]))
            else: matches = np.sum(left == right)
            matching = matches / i + eps
            if matches > 1 and matching > max_:
                max_ = matching
                max_indices = (left_start, left_stop, right_start, right_stop)
        (left_start, left_stop, right_start, right_stop) = max_indices
        left_mid = (left_stop + left_start) // 2
        right_mid = (right_stop + right_start) // 2
        total_sequence.extend(left_sequence[:left_mid])
        left_sequence = right_sequence[right_mid:]
        left_length = len(left_sequence)
        if token_timestamp_sequences:
            total_token_timestamp_sequence.extend(left_token_timestamp_sequence[:left_mid])
            left_token_timestamp_sequence = token_timestamp_sequences[seq_idx + 1][right_mid:]
    total_sequence.extend(left_sequence)
    if token_timestamp_sequences is None: return total_sequence
    if len(token_timestamp_sequences) > 0:
        total_token_timestamp_sequence.extend(left_token_timestamp_sequence)
        return total_sequence, total_token_timestamp_sequence
    else: return total_sequence, []
def _collate_word_timestamps(tokenizer, tokens, token_timestamps, language, return_language):
    words, _, token_indices = _combine_tokens_into_words(tokenizer, tokens, language)
    optional_language_field = {"language": language} if return_language else {}
    timings = [{"text": word, "timestamp": (token_timestamps[indices[0]][0], token_timestamps[indices[-1]][1]), **optional_language_field} for word, indices in zip(words, token_indices)]
    return timings
def _combine_tokens_into_words(tokenizer, tokens: List[int], language: str = None, prepend_punctuations: str = "\"'“¡¿([{-", append_punctuations: str = "\"'.。,，!！?？:：”)]}、"):
    if language is None: language = tokenizer.language
    if language is None: language = "english"
    if language in {"chinese", "japanese", "thai", "lao", "myanmar", "cantonese"}: words, word_tokens, token_indices = _split_tokens_on_unicode(tokenizer, tokens)
    else: words, word_tokens, token_indices = _split_tokens_on_spaces(tokenizer, tokens)
    _merge_punctuations(words, word_tokens, token_indices, prepend_punctuations, append_punctuations)
    return words, word_tokens, token_indices
def _split_tokens_on_unicode(tokenizer, tokens: List[int]):
    decoded_full = tokenizer.decode(tokens, decode_with_timestamps=True)
    replacement_char = "\ufffd"
    words = []
    word_tokens = []
    token_indices = []
    current_tokens = []
    current_indices = []
    unicode_offset = 0
    for token_idx, token in enumerate(tokens):
        current_tokens.append(token)
        current_indices.append(token_idx)
        decoded = tokenizer.decode(current_tokens, decode_with_timestamps=True)
        if (replacement_char not in decoded or decoded_full[unicode_offset + decoded.index(replacement_char)] == replacement_char):
            words.append(decoded)
            word_tokens.append(current_tokens)
            token_indices.append(current_indices)
            current_tokens = []
            current_indices = []
            unicode_offset += len(decoded)
    return words, word_tokens, token_indices
def _split_tokens_on_spaces(tokenizer, tokens: List[int]):
    subwords, subword_tokens_list, subword_indices_list = _split_tokens_on_unicode(tokenizer, tokens)
    words = []
    word_tokens = []
    token_indices = []
    for subword, subword_tokens, subword_indices in zip(subwords, subword_tokens_list, subword_indices_list):
        special = subword_tokens[0] >= tokenizer.eos_token_id
        with_space = subword.startswith(" ")
        punctuation = subword.strip() in "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
        if special or with_space or punctuation or len(words) == 0:
            words.append(subword)
            word_tokens.append(subword_tokens)
            token_indices.append(subword_indices)
        else:
            words[-1] = words[-1] + subword
            word_tokens[-1].extend(subword_tokens)
            token_indices[-1].extend(subword_indices)
    return words, word_tokens, token_indices
def _merge_punctuations(words, tokens, indices, prepended, appended):
    i = len(words) - 2
    j = len(words) - 1
    while i >= 0:
        if words[i].startswith(" ") and words[i].strip() in prepended:
            words[j] = words[i] + words[j]
            tokens[j] = tokens[i] + tokens[j]
            indices[j] = indices[i] + indices[j]
            words[i] = ""
            tokens[i] = []
            indices[i] = []
        else: j = i
        i -= 1
    i = 0
    j = 1
    while j < len(words):
        if not words[i].endswith(" ") and words[j] in appended:
            words[i] += words[j]
            tokens[i] += tokens[j]
            indices[i] += indices[j]
            words[j] = ""
            tokens[j] = []
            indices[j] = []
        else: i = j
        j += 1
    words[:] = [word for word in words if word]
    tokens[:] = [token for token in tokens if token]
    indices[:] = [idx for idx in indices if idx]
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
