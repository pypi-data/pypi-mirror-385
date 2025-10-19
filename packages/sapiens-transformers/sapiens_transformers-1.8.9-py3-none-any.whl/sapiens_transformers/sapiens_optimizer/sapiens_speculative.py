"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import numpy.typing as npt
from typing import Any
import numpy as np
import abc
class SapiensDraftModel(abc.ABC):
    @abc.abstractmethod
    def __call__(self, input_ids: npt.NDArray[np.intc], **kwargs: Any) -> npt.NDArray[np.intc]: raise NotImplementedError()
class SapiensPromptLookupDecoding(SapiensDraftModel):
    def __init__(self, max_ngram_size: int = 2, num_pred_tokens: int = 10):
        self.max_ngram_size = max_ngram_size
        self.num_pred_tokens = num_pred_tokens
    @staticmethod
    def find_candidate_pred_tokens(input_ids: npt.NDArray[np.intc], max_ngram_size: int, num_pred_tokens: int):
        input_length = input_ids.shape[0]
        for ngram_size in range(min(max_ngram_size, input_length - 1), 0, -1):
            windows = np.lib.stride_tricks.sliding_window_view(input_ids, (ngram_size,))
            ngram_array = input_ids[-ngram_size:]
            matches = np.all(windows == ngram_array, axis=1)
            match_indices = np.nonzero(matches)[0]
            for idx in match_indices:
                start_idx = idx + ngram_size
                end_idx = start_idx + num_pred_tokens
                end_idx = min(end_idx, input_length)
                if start_idx < end_idx: return input_ids[start_idx:end_idx]
        return np.array([], dtype=np.intc)
    def __call__(self, input_ids: npt.NDArray[np.intc], **kwargs: Any) -> npt.NDArray[np.intc]: return self.find_candidate_pred_tokens(input_ids=input_ids, max_ngram_size=self.max_ngram_size, num_pred_tokens=self.num_pred_tokens)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
