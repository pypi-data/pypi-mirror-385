"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import OptionalDependencyNotAvailable, _LazyModule, is_torch_available
_import_structure = {'configuration_xlm_roberta_xl': ['XLMRobertaXLConfig', 'XLMRobertaXLOnnxConfig']}
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_xlm_roberta_xl"] = ["XLMRobertaXLForCausalLM", "XLMRobertaXLForMaskedLM", "XLMRobertaXLForMultipleChoice", "XLMRobertaXLForQuestionAnswering",
"XLMRobertaXLForSequenceClassification", "XLMRobertaXLForTokenClassification", "XLMRobertaXLModel", "XLMRobertaXLPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_xlm_roberta_xl import (XLMRobertaXLConfig, XLMRobertaXLOnnxConfig)
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_xlm_roberta_xl import (XLMRobertaXLForCausalLM, XLMRobertaXLForMaskedLM, XLMRobertaXLForMultipleChoice, XLMRobertaXLForQuestionAnswering,
    XLMRobertaXLForSequenceClassification, XLMRobertaXLForTokenClassification, XLMRobertaXLModel, XLMRobertaXLPreTrainedModel)
else:
    import sys
    sys.modules[__name__] = _LazyModule(__name__, globals()["__file__"], _import_structure)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
