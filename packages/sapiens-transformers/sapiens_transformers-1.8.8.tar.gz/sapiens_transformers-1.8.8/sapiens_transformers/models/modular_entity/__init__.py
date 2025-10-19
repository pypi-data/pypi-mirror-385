"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...utils import (SAPIENS_TECHNOLOGY_CHECKING, SapiensTechnologyNotAvailable, SapiensTechnologyModule, sapiens_technology_torch, sapiens_technology_for_vision)
_import_structure = {'configuration_modular_entity': ['ModularEntityConfig'], 'processing_modular_entity': ['ModularEntityProcessor']}
try:
    if not sapiens_technology_torch(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else: _import_structure["modeling_modular_entity"] = ["ModularEntityForConditionalGeneration", "ModularEntityForCausalLM", "ModularEntityTextModel", "ModularEntityVisionModel", "ModularEntityPreTrainedModel"]
try:
    if not sapiens_technology_for_vision(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else: _import_structure["image_processing_modular_entity"] = ["ModularEntityImageProcessor"]
if SAPIENS_TECHNOLOGY_CHECKING:
    from .configuration_modular_entity import ModularEntityConfig
    from .processing_modular_entity import ModularEntityProcessor
    try:
        if not sapiens_technology_torch(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .modeling_modular_entity import (ModularEntityForCausalLM, ModularEntityForConditionalGeneration, ModularEntityPreTrainedModel, ModularEntityTextModel, ModularEntityVisionModel)
    try:
        if not sapiens_technology_for_vision(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .image_processing_modular_entity import (ModularEntityImageProcessor)
else:
    import sys
    sys.modules[__name__] = SapiensTechnologyModule(__name__, globals()["__file__"], _import_structure)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
