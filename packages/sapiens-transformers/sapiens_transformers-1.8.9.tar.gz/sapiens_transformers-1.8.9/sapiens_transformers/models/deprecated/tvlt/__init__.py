"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ....utils import (OptionalDependencyNotAvailable, _LazyModule, is_torch_available, is_vision_available)
_import_structure = {'configuration_tvlt': ['TvltConfig'], 'feature_extraction_tvlt': ['TvltFeatureExtractor'], 'processing_tvlt': ['TvltProcessor']}
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tvlt"] = ["TvltModel", "TvltForPreTraining", "TvltForAudioVisualClassification", "TvltPreTrainedModel"]
try:
    if not is_vision_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["image_processing_tvlt"] = ["TvltImageProcessor"]
if TYPE_CHECKING:
    from .configuration_tvlt import TvltConfig
    from .processing_tvlt import TvltProcessor
    from .feature_extraction_tvlt import TvltFeatureExtractor
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tvlt import (TvltForAudioVisualClassification, TvltForPreTraining, TvltModel, TvltPreTrainedModel)
    try:
        if not is_vision_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .image_processing_tvlt import TvltImageProcessor
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
