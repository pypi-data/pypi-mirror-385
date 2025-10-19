"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import warnings
from ...processing_utils import ProcessorMixin
from ...tokenization_utils_base import BatchEncoding
class XCLIPProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = "VideoMAEImageProcessor"
    tokenizer_class = ("CLIPTokenizer", "CLIPTokenizerFast")
    def __init__(self, image_processor=None, tokenizer=None, **kwargs):
        feature_extractor = None
        if "feature_extractor" in kwargs:
            warnings.warn("The `feature_extractor` argument is deprecated and will be removed in v5, use `image_processor` instead.", FutureWarning)
            feature_extractor = kwargs.pop("feature_extractor")
        image_processor = image_processor if image_processor is not None else feature_extractor
        if image_processor is None: raise ValueError("You need to specify an `image_processor`.")
        if tokenizer is None: raise ValueError("You need to specify a `tokenizer`.")
        super().__init__(image_processor, tokenizer)
        self.current_processor = self.image_processor
    def __call__(self, text=None, videos=None, return_tensors=None, **kwargs):
        if text is None and videos is None: raise ValueError("You have to specify either text or videos. Both cannot be none.")
        if text is not None: encoding = self.tokenizer(text, return_tensors=return_tensors, **kwargs)
        if videos is not None: image_features = self.image_processor(videos, return_tensors=return_tensors, **kwargs)
        if text is not None and videos is not None:
            encoding["pixel_values"] = image_features.pixel_values
            return encoding
        elif text is not None: return encoding
        else: return BatchEncoding(data=dict(**image_features), tensor_type=return_tensors)
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    @property
    def model_input_names(self): return ["input_ids", "attention_mask", "position_ids", "pixel_values"]
    @property
    def feature_extractor_class(self):
        warnings.warn("`feature_extractor_class` is deprecated and will be removed in v5. Use `image_processor_class` instead.", FutureWarning)
        return self.image_processor_class
    @property
    def feature_extractor(self):
        warnings.warn("`feature_extractor` is deprecated and will be removed in v5. Use `image_processor` instead.", FutureWarning)
        return self.image_processor
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
