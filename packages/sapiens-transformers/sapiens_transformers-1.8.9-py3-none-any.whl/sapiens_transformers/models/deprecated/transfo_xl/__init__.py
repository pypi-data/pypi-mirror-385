"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ....utils import OptionalDependencyNotAvailable, _LazyModule, is_tf_available, is_torch_available
_import_structure = {'configuration_transfo_xl': ['TransfoXLConfig'], 'tokenization_transfo_xl': ['TransfoXLCorpus', 'TransfoXLTokenizer']}
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_transfo_xl"] = ["AdaptiveEmbedding", "TransfoXLForSequenceClassification", "TransfoXLLMHeadModel", "TransfoXLModel", "TransfoXLPreTrainedModel", "load_tf_weights_in_transfo_xl"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_transfo_xl"] = ["TFAdaptiveEmbedding", "TFTransfoXLForSequenceClassification", "TFTransfoXLLMHeadModel", "TFTransfoXLMainLayer", "TFTransfoXLModel", "TFTransfoXLPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_transfo_xl import TransfoXLConfig
    from .tokenization_transfo_xl import TransfoXLCorpus, TransfoXLTokenizer
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_transfo_xl import (AdaptiveEmbedding, TransfoXLForSequenceClassification, TransfoXLLMHeadModel, TransfoXLModel, TransfoXLPreTrainedModel, load_tf_weights_in_transfo_xl)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_transfo_xl import (TFAdaptiveEmbedding, TFTransfoXLForSequenceClassification, TFTransfoXLLMHeadModel, TFTransfoXLMainLayer, TFTransfoXLModel, TFTransfoXLPreTrainedModel)
else:
    import sys
    sys.modules[__name__] = _LazyModule(__name__, globals()["__file__"], _import_structure, module_spec=__spec__)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
