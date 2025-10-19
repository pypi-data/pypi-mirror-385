"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from shutil import copyfile
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple
import sentencepiece as spm
from ...convert_slow_tokenizer import import_protobuf
from ...tokenization_utils import AddedToken, PreTrainedTokenizer
from ...utils import logging
if TYPE_CHECKING: from ...tokenization_utils_base import TextInput
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "tokenizer.model"}
SPIECE_UNDERLINE = "▁"
B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
DEFAULT_SYSTEM_PROMPT = """You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your \
answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure\
 that your responses are socially unbiased and positive in nature.
If a question does not make any sense, or is not factually coherent, explain why instead of answering something not \
correct. If you don't know the answer to a question, please don't share false information."""
class LlamaTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, vocab_file, unk_token="<unk>", bos_token="<s>", eos_token="</s>", pad_token=None, sp_model_kwargs: Optional[Dict[str, Any]] = None,
    add_bos_token=True, add_eos_token=False, clean_up_tokenization_spaces=False, use_default_system_prompt=False, spaces_between_special_tokens=False,
    legacy=None, add_prefix_space=True, **kwargs):
        self.sp_model_kwargs = {} if sp_model_kwargs is None else sp_model_kwargs
        bos_token = AddedToken(bos_token, normalized=False, special=True) if isinstance(bos_token, str) else bos_token
        eos_token = AddedToken(eos_token, normalized=False, special=True) if isinstance(eos_token, str) else eos_token
        unk_token = AddedToken(unk_token, normalized=False, special=True) if isinstance(unk_token, str) else unk_token
        pad_token = AddedToken(pad_token, normalized=False, special=True) if isinstance(pad_token, str) else pad_token
        if legacy is None:
            logger.warning_once(f"You are using the default legacy behaviour of the {self.__class__}. This is expected, and simply means that the `legacy` (previous) behavior will be used so nothing changes for you. If you want to use the new behaviour, set `legacy=False`. This should only be set if you understand what it means - if you loaded a llama tokenizer from a GGUF file you can ignore this message")
            legacy = True
        self.legacy = legacy
        self.vocab_file = vocab_file
        self.add_bos_token = add_bos_token
        self.add_eos_token = add_eos_token
        self.use_default_system_prompt = use_default_system_prompt
        self.sp_model = self.get_spm_processor(kwargs.pop("from_slow", False))
        self.add_prefix_space = add_prefix_space
        super().__init__(bos_token=bos_token, eos_token=eos_token, unk_token=unk_token, pad_token=pad_token, add_bos_token=add_bos_token, add_eos_token=add_eos_token,
        sp_model_kwargs=self.sp_model_kwargs, clean_up_tokenization_spaces=clean_up_tokenization_spaces, use_default_system_prompt=use_default_system_prompt,
        spaces_between_special_tokens=spaces_between_special_tokens, legacy=legacy, add_prefix_space=add_prefix_space, **kwargs)
    @property
    def unk_token_length(self): return len(self.sp_model.encode(str(self.unk_token)))
    def get_spm_processor(self, from_slow=False):
        tokenizer = spm.SentencePieceProcessor(**self.sp_model_kwargs)
        if self.legacy or from_slow:
            tokenizer.Load(self.vocab_file)
            return tokenizer
        with open(self.vocab_file, "rb") as f:
            sp_model = f.read()
            model_pb2 = import_protobuf(f"The new behaviour of {self.__class__.__name__} (with `self.legacy = False`)")
            model = model_pb2.ModelProto.FromString(sp_model)
            normalizer_spec = model_pb2.NormalizerSpec()
            normalizer_spec.add_dummy_prefix = False
            model.normalizer_spec.MergeFrom(normalizer_spec)
            sp_model = model.SerializeToString()
            tokenizer.LoadFromSerializedProto(sp_model)
        return tokenizer
    def __getstate__(self):
        state = self.__dict__.copy()
        state["sp_model"] = None
        state["sp_model_proto"] = self.sp_model.serialized_model_proto()
        return state
    def __setstate__(self, d):
        self.__dict__ = d
        self.sp_model = spm.SentencePieceProcessor(**self.sp_model_kwargs)
        self.sp_model.LoadFromSerializedProto(self.sp_model_proto)
    @property
    def vocab_size(self): return self.sp_model.get_piece_size()
    def get_vocab(self):
        vocab = {self.convert_ids_to_tokens(i): i for i in range(self.vocab_size)}
        vocab.update(self.added_tokens_encoder)
        return vocab
    def tokenize(self, text: "TextInput", **kwargs) -> List[str]:
        if self.legacy or len(text) == 0: return super().tokenize(text, **kwargs)
        text = text.replace(SPIECE_UNDERLINE, " ")
        if self.add_prefix_space: text = SPIECE_UNDERLINE + text
        tokens = super().tokenize(text, **kwargs)
        if len(tokens) > 1 and tokens[0] == SPIECE_UNDERLINE and tokens[1] in self.all_special_tokens: tokens = tokens[1:]
        return tokens
    def _tokenize(self, text, **kwargs):
        if self.legacy or not text.startswith((SPIECE_UNDERLINE, " ")): return self.sp_model.encode(text, out_type=str)
        tokens = self.sp_model.encode(self.unk_token + text, out_type=str)
        return tokens[self.unk_token_length :] if len(tokens) >= self.unk_token_length else tokens
    def _convert_token_to_id(self, token): return self.sp_model.piece_to_id(token)
    def _convert_id_to_token(self, index):
        token = self.sp_model.IdToPiece(index)
        return token
    def convert_tokens_to_string(self, tokens):
        if tokens[0].startswith(SPIECE_UNDERLINE) and self.add_prefix_space: tokens[0] = tokens[0][1:]
        current_sub_tokens = []
        out_string = ""
        prev_is_special = False
        for i, token in enumerate(tokens):
            if token in self.all_special_tokens:
                if not prev_is_special and i != 0 and self.legacy: out_string += " "
                out_string += self.sp_model.decode(current_sub_tokens) + token
                prev_is_special = True
                current_sub_tokens = []
            else:
                if prev_is_special and i == 1 and self.add_prefix_space and not token.startswith(SPIECE_UNDERLINE): out_string += " "
                current_sub_tokens.append(token)
                prev_is_special = False
        out_string += self.sp_model.decode(current_sub_tokens)
        return out_string
    def save_vocabulary(self, save_directory, filename_prefix: Optional[str] = None) -> Tuple[str]:
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
    def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None):
        bos_token_id = [self.bos_token_id] if self.add_bos_token else []
        eos_token_id = [self.eos_token_id] if self.add_eos_token else []
        output = bos_token_id + token_ids_0 + eos_token_id
        if token_ids_1 is not None: output = output + bos_token_id + token_ids_1 + eos_token_id
        return output
    def get_special_tokens_mask(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens: return super().get_special_tokens_mask(token_ids_0=token_ids_0, token_ids_1=token_ids_1, already_has_special_tokens=True)
        bos_token_id = [1] if self.add_bos_token else []
        eos_token_id = [1] if self.add_eos_token else []
        if token_ids_1 is None: return bos_token_id + ([0] * len(token_ids_0)) + eos_token_id
        return (bos_token_id + ([0] * len(token_ids_0)) + eos_token_id + bos_token_id + ([0] * len(token_ids_1)) + eos_token_id)
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        bos_token_id = [self.bos_token_id] if self.add_bos_token else []
        eos_token_id = [self.eos_token_id] if self.add_eos_token else []
        output = [0] * len(bos_token_id + token_ids_0 + eos_token_id)
        if token_ids_1 is not None: output += [1] * len(bos_token_id + token_ids_1 + eos_token_id)
        return output
class SAPITokenizer(LlamaTokenizer): pass
class SAPIGPTModel():
    def __init__(self):
        from nemo.collections.nlp.models.language_modeling.megatron_gpt_model import MegatronGPTModel
        self.SAPIGPTModel = MegatronGPTModel
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
