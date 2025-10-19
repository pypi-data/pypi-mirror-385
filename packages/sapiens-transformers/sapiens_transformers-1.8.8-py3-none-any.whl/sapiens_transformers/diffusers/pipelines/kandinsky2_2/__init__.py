'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import TYPE_CHECKING
from ...utils import DIFFUSERS_SLOW_IMPORT, OptionalDependencyNotAvailable, _LazyModule, get_objects_from_module, is_torch_available, is_transformers_available
_dummy_objects = {}
_import_structure = {}
try:
    if not (is_transformers_available() and is_torch_available()): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable:
    from ...utils import dummy_torch_and_transformers_objects
    _dummy_objects.update(get_objects_from_module(dummy_torch_and_transformers_objects))
else:
    _import_structure['pipeline_kandinsky2_2'] = ['KandinskyV22Pipeline']
    _import_structure['pipeline_kandinsky2_2_combined'] = ['KandinskyV22CombinedPipeline', 'KandinskyV22Img2ImgCombinedPipeline', 'KandinskyV22InpaintCombinedPipeline']
    _import_structure['pipeline_kandinsky2_2_controlnet'] = ['KandinskyV22ControlnetPipeline']
    _import_structure['pipeline_kandinsky2_2_controlnet_img2img'] = ['KandinskyV22ControlnetImg2ImgPipeline']
    _import_structure['pipeline_kandinsky2_2_img2img'] = ['KandinskyV22Img2ImgPipeline']
    _import_structure['pipeline_kandinsky2_2_inpainting'] = ['KandinskyV22InpaintPipeline']
    _import_structure['pipeline_kandinsky2_2_prior'] = ['KandinskyV22PriorPipeline']
    _import_structure['pipeline_kandinsky2_2_prior_emb2emb'] = ['KandinskyV22PriorEmb2EmbPipeline']
if TYPE_CHECKING or DIFFUSERS_SLOW_IMPORT:
    try:
        if not (is_transformers_available() and is_torch_available()): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: from ...utils.dummy_torch_and_transformers_objects import *
    else:
        from .pipeline_kandinsky2_2 import KandinskyV22Pipeline
        from .pipeline_kandinsky2_2_combined import KandinskyV22CombinedPipeline, KandinskyV22Img2ImgCombinedPipeline, KandinskyV22InpaintCombinedPipeline
        from .pipeline_kandinsky2_2_controlnet import KandinskyV22ControlnetPipeline
        from .pipeline_kandinsky2_2_controlnet_img2img import KandinskyV22ControlnetImg2ImgPipeline
        from .pipeline_kandinsky2_2_img2img import KandinskyV22Img2ImgPipeline
        from .pipeline_kandinsky2_2_inpainting import KandinskyV22InpaintPipeline
        from .pipeline_kandinsky2_2_prior import KandinskyV22PriorPipeline
        from .pipeline_kandinsky2_2_prior_emb2emb import KandinskyV22PriorEmb2EmbPipeline
else:
    import sys
    sys.modules[__name__] = _LazyModule(__name__, globals()['__file__'], _import_structure, module_spec=__spec__)
    for name, value in _dummy_objects.items(): setattr(sys.modules[__name__], name, value)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
