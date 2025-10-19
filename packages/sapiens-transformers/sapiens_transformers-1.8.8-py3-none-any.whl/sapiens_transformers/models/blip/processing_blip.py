"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Optional, Union
from ...image_utils import ImageInput
from ...processing_utils import ProcessorMixin
from ...tokenization_utils_base import BatchEncoding, PaddingStrategy, PreTokenizedInput, TextInput, TruncationStrategy
from ...utils import TensorType
class BlipProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    valid_kwargs = []
    image_processor_class = "BlipImageProcessor"
    tokenizer_class = ("BertTokenizer", "BertTokenizerFast")
    def __init__(self, image_processor, tokenizer, **kwargs):
        tokenizer.return_token_type_ids = False
        super().__init__(image_processor, tokenizer)
        self.current_processor = self.image_processor
    def __call__(self, images: ImageInput = None, text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None, add_special_tokens: bool = True,
    padding: Union[bool, str, PaddingStrategy] = False, truncation: Union[bool, str, TruncationStrategy] = None, max_length: Optional[int] = None, stride: int = 0,
    pad_to_multiple_of: Optional[int] = None, return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False,
    return_offsets_mapping: bool = False, return_token_type_ids: bool = False, return_length: bool = False, verbose: bool = True, return_tensors: Optional[Union[str, TensorType]] = None, **kwargs) -> BatchEncoding:
        if images is None and text is None: raise ValueError("You have to specify either images or text.")
        if images is None:
            self.current_processor = self.tokenizer
            text_encoding = self.tokenizer(text=text, add_special_tokens=add_special_tokens, padding=padding, truncation=truncation, max_length=max_length, stride=stride,
            pad_to_multiple_of=pad_to_multiple_of, return_attention_mask=return_attention_mask, return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask,
            return_offsets_mapping=return_offsets_mapping, return_token_type_ids=return_token_type_ids, return_length=return_length, verbose=verbose, return_tensors=return_tensors, **kwargs)
            return text_encoding
        encoding_image_processor = self.image_processor(images, return_tensors=return_tensors)
        if text is not None:
            text_encoding = self.tokenizer(text=text, add_special_tokens=add_special_tokens, padding=padding, truncation=truncation, max_length=max_length, stride=stride,
            pad_to_multiple_of=pad_to_multiple_of, return_attention_mask=return_attention_mask, return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask,
            return_offsets_mapping=return_offsets_mapping, return_token_type_ids=return_token_type_ids, return_length=return_length, verbose=verbose, return_tensors=return_tensors, **kwargs)
        else: text_encoding = None
        if text_encoding is not None: encoding_image_processor.update(text_encoding)
        return encoding_image_processor
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    @property
    def model_input_names(self):
        tokenizer_input_names = self.tokenizer.model_input_names
        image_processor_input_names = self.image_processor.model_input_names
        return list(dict.fromkeys(tokenizer_input_names + image_processor_input_names))
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
