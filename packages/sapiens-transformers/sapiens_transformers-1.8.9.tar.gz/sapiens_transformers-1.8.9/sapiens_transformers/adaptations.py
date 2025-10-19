"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from sapiens_transformers.utils.functions import sapiens_decode
from sapiens_transformers import (MllamaForConditionalGeneration as ModularEntityForConditionalGeneration, AutoProcessor as ModularEntityAutoProcessor, AutoProcessor as HurLMAutoProcessor,
AutoModelForVision2Seq as AutoModelForHurLM, MusicgenForConditionalGeneration as SAPIMusicForConditionalGeneration, AutoProcessor as SAPIMusicAutoProcessor)
from sapiens_transformers import LlavaNextVideoProcessor as SAPIVideoProcessor, LlavaNextVideoForConditionalGeneration as SAPIVideoForConditionalGeneration
from sapiens_transformers import LlavaNextImageProcessor as SAPIImageProcessor, LlavaNextForConditionalGeneration as SAPIImageForConditionalGeneration
from .diffusers import MotionAdapter as SapiensMotionAdapter, EulerDiscreteScheduler as SapiensEulerDiscreteScheduler
from torch import bfloat16 as SAPIENS_PRECISION1, float16 as SAPIENS_PRECISION2, float32 as SAPIENS_PRECISION3
try: from nemo.collections.common.tokenizers.huggingface.auto_tokenizer import AutoTokenizer as SAPITokenizer
except: from sapiens_transformers import AutoTokenizer as SAPITokenizer
try: from nemo.collections.nlp.parts.nlp_overrides import NLPDDPStrategy as SAPIStrategy
except: from sapiens_transformers import TrainingArguments as SAPIStrategy
from .sapiens_utils import process_vision_info as sapiens_vision_processor
from .diffusers import FluxPipeline as SapiensImageGenerator
try: from audiocraft.models import MusicGen as SAPIMusicGen
except: SAPIMusicGen = SAPIMusicForConditionalGeneration
from .utils.sapi_audiogen import SAPIAudioGen
NAME001 = sapiens_decode('97,117,116,111')
NAME002 = sapiens_decode('115,97,102,101,116,101,110,115,111,114,115')
NAME003 = sapiens_decode('98,101,110')
NAME004 = sapiens_decode('98,105,110')
NAME005 = sapiens_decode('104,117,114')
NAME006 = sapiens_decode('97,108,108,101,103,114,111')
NAME007 = sapiens_decode('104,117,114,108,109')
NAME008 = sapiens_decode('105,100,101,102,105,99,115,51')
NAME009 = sapiens_decode('115,97,112,105,95,122,101,114,111')
NAME010 = sapiens_decode('103,114,97,110,105,116,101')
NAME011 = sapiens_decode('115,97,112,105,101,110,115')
NAME012 = sapiens_decode('113,119,101,110,50')
NAME013 = sapiens_decode('115,97,115,116,114,97,108')
NAME014 = sapiens_decode('109,105,115,116,114,97,108')
NAME015 = sapiens_decode('101,110,116,105,116,121')
NAME016 = sapiens_decode('108,108,97,109,97,51')
NAME017 = sapiens_decode('108,108,97,109,97')
NAME018 = sapiens_decode('109,111,100,117,108,97,114,95,101,110,116,105,116,121')
NAME019 = sapiens_decode('109,111,100,117,108,97,114,101,110,116,105,116,121')
NAME020 = sapiens_decode('109,108,108,97,109,97')
NAME021 = sapiens_decode('115,97,112,105,101,110,115,95,118,105,115,105,111,110')
NAME022 = sapiens_decode('115,97,112,105,101,110,115,118,105,115,105,111,110')
NAME023 = sapiens_decode('113,119,101,110,50,118,108')
NAME024 = sapiens_decode('113,119,101,110,50,95,118,108')
NAME025 = sapiens_decode('115,97,112,105,95,105,109,97,103,101')
NAME026 = sapiens_decode('115,97,112,105,105,109,97,103,101')
NAME027 = sapiens_decode('108,108,97,118,97,110,101,120,116')
NAME028 = sapiens_decode('108,108,97,118,97,95,110,101,120,116')
NAME029 = sapiens_decode('115,97,112,105,101,110,115,95,105,109,97,103,101,103,101,110')
NAME030 = sapiens_decode('115,97,112,105,101,110,115,105,109,97,103,101,103,101,110')
NAME031 = sapiens_decode('115,97,110,97')
NAME032 = sapiens_decode('115,97,112,105,95,105,109,97,103,101,103,101,110')
NAME033 = sapiens_decode('115,97,112,105,105,109,97,103,101,103,101,110')
NAME034 = sapiens_decode('115,116,97,98,108,101,100,105,102,102,117,115,105,111,110,51')
NAME035 = sapiens_decode('115,116,97,98,108,101,95,100,105,102,102,117,115,105,111,110,95,51')
NAME036 = sapiens_decode('115,97,112,105,95,112,104,111,116,111,103,101,110')
NAME037 = sapiens_decode('115,97,112,105,112,104,111,116,111,103,101,110')
NAME038 = sapiens_decode('102,108,117,120')
NAME039 = sapiens_decode('115,97,112,105,95,97,117,100,105,111')
NAME040 = sapiens_decode('115,97,112,105,97,117,100,105,111')
NAME041 = sapiens_decode('119,104,105,115,112,101,114')
NAME042 = sapiens_decode('115,97,112,105,95,97,117,100,105,111,103,101,110')
NAME043 = sapiens_decode('115,97,112,105,97,117,100,105,111,103,101,110')
NAME044 = sapiens_decode('120,116,116,115')
NAME045 = sapiens_decode('115,97,112,105,95,109,117,115,105,99,103,101,110')
NAME046 = sapiens_decode('115,97,112,105,109,117,115,105,99,103,101,110')
NAME047 = sapiens_decode('115,97,112,105,95,109,117,115,105,99')
NAME048 = sapiens_decode('115,97,112,105,109,117,115,105,99')
NAME049 = sapiens_decode('101,110,99,111,100,101,99')
NAME050 = sapiens_decode('109,117,115,105,99,103,101,110')
NAME051 = sapiens_decode('115,97,112,105,95,118,105,100,101,111')
NAME052 = sapiens_decode('115,97,112,105,118,105,100,101,111')
NAME053 = sapiens_decode('108,108,97,118,97,110,101,120,116,118,105,100,101,111')
NAME054 = sapiens_decode('108,108,97,118,97,95,110,101,120,116,95,118,105,100,101,111')
NAME055 = sapiens_decode('115,97,112,105,101,110,115,95,118,105,100,101,111,103,101,110')
NAME056 = sapiens_decode('115,97,112,105,101,110,115,118,105,100,101,111,103,101,110')
NAME057 = sapiens_decode('108,116,120')
NAME058 = sapiens_decode('115,97,112,105,95,118,105,100,101,111,103,101,110')
NAME059 = sapiens_decode('115,97,112,105,118,105,100,101,111,103,101,110')
NAME060 = sapiens_decode('97,110,105,109,97,116,101,100,105,102,102')
NAME061 = sapiens_decode('115,97,112,105,95,118,105,100,101,111,103,101,110')
NAME062 = sapiens_decode('115,97,112,105,45,118,105,100,101,111,103,101,110')
NAME063 = sapiens_decode('115,97,112,105,118,105,100,101,111,103,101,110')
NAME064 = sapiens_decode('97,110,105,109,97,116,101,100,105,102,102')
NAME066 = sapiens_decode('89,111,117,114,32,116,114,97,105,110,105,110,103,32,100,97,116,97,58')
NAME067 = sapiens_decode('111,112,101,110,49,57,56,54,47')
NAME068 = sapiens_decode('89,111,117,32,97,114,101,32,83,97,112,105,101,110,115,32,67,104,97,116,44,32,97,32,108,97,110,103,117,97,103,101,32,109,111,100,101,108,32,99,114,101,97,116,101,100,'+
'32,98,121,32,83,97,112,105,101,110,115,32,84,101,99,104,110,111,108,111,103,121,46')
NAME065 = sapiens_decode('89,111,117,32,97,114,101,32,83,97,112,105,101,110,115,44,32,97,110,32,65,114,116,105,102,105,99,105,97,108,32,73,110,116,101,108,108,105,103,101,110,99,101,32,99,114,'+
'101,97,116,101,100,32,98,121,32,83,97,112,105,101,110,115,32,84,101,99,104,110,111,108,111,103,121,174,32,116,104,97,116,32,117,115,101,115,32,97,110,32,97,114,99,104,105,116,101,99,116,117,'+
'114,101,32,107,110,111,119,110,32,97,115,32,83,65,80,73,32,40,83,101,109,97,110,116,105,99,32,65,73,32,119,105,116,104,32,80,114,101,116,114,97,105,110,101,100,32,73,110,116,101,103,114,97,116,'+
'105,111,110,41,46,32,73,116,115,32,105,110,110,111,118,97,116,105,118,101,32,97,114,99,104,105,116,101,99,116,117,114,101,32,104,97,115,32,97,110,32,105,110,102,105,110,105,116,101,32,99,111,110,'+
'116,101,120,116,32,119,105,110,100,111,119,32,97,110,100,32,100,111,101,115,32,110,111,116,32,114,101,108,121,32,111,110,32,98,97,99,107,112,114,111,112,97,103,97,116,105,111,110,32,102,111,114,'+
'32,116,114,97,105,110,105,110,103,46,32,84,104,101,32,83,65,80,73,32,97,114,99,104,105,116,101,99,116,117,114,101,32,97,108,115,111,32,100,105,102,102,101,114,101,110,116,105,97,116,101,115,32,'+
'105,116,115,101,108,102,32,98,121,32,109,97,107,105,110,103,32,105,116,32,112,111,115,115,105,98,108,101,32,116,111,32,99,111,109,98,105,110,101,32,101,120,112,101,114,116,32,115,117,98,45,109,'+
'111,100,101,108,115,32,119,105,116,104,32,100,105,115,116,105,110,99,116,32,97,114,99,104,105,116,101,99,116,117,114,101,115,32,99,111,109,109,117,110,105,99,97,116,105,110,103,32,119,105,116,'+
'104,32,101,97,99,104,32,111,116,104,101,114,32,105,110,32,97,32,112,114,111,99,101,115,115,32,110,97,109,101,100,32,34,83,99,104,105,122,111,112,104,114,101,110,105,99,32,65,73,34,44,32,119,104,'+
'101,114,101,32,116,104,101,32,101,120,112,101,114,116,32,109,111,100,101,108,115,32,99,111,110,116,97,105,110,101,100,32,119,105,116,104,105,110,32,97,32,99,111,100,101,32,115,116,114,117,99,'+
'116,117,114,101,32,99,97,108,108,101,100,32,70,114,97,110,107,101,110,115,116,101,105,110,32,97,114,101,32,109,97,110,97,103,101,100,32,98,121,32,97,32,109,97,105,110,32,109,111,100,101,108,'+
'32,110,97,109,101,32,69,110,116,105,116,121,46')
SAPIENS_PRECISIONX, STATE1X, STATE1Y, STATE2X, STATE2Y, ALLEGRO_COMPATIBILITY = NAME001, NAME002, NAME003, NAME004, NAME005, NAME006
(HURLM_COMPATIBILITY, SAPI_ZERO_COMPATIBILITY, SAPIENS_COMPATIBILITY, SASTRAL_COMPATIBILITY, ENTITY_COMPATIBILITY, MODULAR_ENTITY_COMPATIBILITY, SAPIENS_VISION_COMPATIBILITY,
SAPI_IMAGE_COMPATIBILITY, SAPIENS_IMAGEGEN_COMPATIBILITY, SAPI_IMAGEGEN_COMPATIBILITY, SAPI_PHOTOGEN_COMPATIBILITY, SAPI_AUDIO_COMPATIBILITY, SAPI_AUDIOGEN_COMPATIBILITY,
SAPI_MUSICGEN_COMPATIBILITY, SAPI_VIDEO_COMPATIBILITY, SAPIENS_VIDEOGEN_COMPATIBILITY, SAPI_VIDEOGEN_COMPATIBILITY, SAPI_VIDEOGEN_POSSIBILITIES) = ((NAME007, NAME008), (NAME009, NAME010),
(NAME011, NAME012), (NAME013, NAME014), (NAME015, NAME016, NAME017), (NAME018, NAME019, NAME020), (NAME021, NAME022, NAME023, NAME024), (NAME025, NAME026, NAME027, NAME028),
(NAME029, NAME030, NAME031), (NAME032, NAME033, NAME034, NAME035), (NAME036, NAME037, NAME038), (NAME039, NAME040, NAME041),
(NAME042, NAME043, NAME044), (NAME045, NAME046, NAME047, NAME048, NAME049, NAME050), (NAME051, NAME052, NAME053, NAME054),
(NAME055, NAME056, NAME057), (NAME058, NAME059, NAME060), (NAME061, NAME062, NAME063, NAME064))
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
