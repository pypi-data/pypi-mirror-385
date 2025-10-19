"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import importlib
import json
import os
import warnings
from collections import OrderedDict
from typing import TYPE_CHECKING, Dict, Optional, Tuple, Union
from ...configuration_utils import PretrainedConfig
from ...dynamic_module_utils import get_class_from_dynamic_module, resolve_trust_remote_code
from ...image_processing_utils import BaseImageProcessor, ImageProcessingMixin
from ...image_processing_utils_fast import BaseImageProcessorFast
from ...utils import (CONFIG_NAME, IMAGE_PROCESSOR_NAME, get_file_from_repo, is_torchvision_available, is_vision_available, logging)
from .auto_factory import _LazyAutoMapping
from .configuration_auto import (CONFIG_MAPPING_NAMES, AutoConfig, model_type_to_module_name, replace_list_option_in_docstrings)
logger = logging.get_logger(__name__)
if TYPE_CHECKING: IMAGE_PROCESSOR_MAPPING_NAMES: OrderedDict[str, Tuple[Optional[str], Optional[str]]] = OrderedDict()
else:
    IMAGE_PROCESSOR_MAPPING_NAMES = OrderedDict([("align", ("EfficientNetImageProcessor",)), ("beit", ("BeitImageProcessor",)), ("bit", ("BitImageProcessor",)), ("blip", ("BlipImageProcessor",)), ("blip-2", ("BlipImageProcessor",)),
    ("bridgetower", ("BridgeTowerImageProcessor",)), ("chameleon", ("ChameleonImageProcessor",)), ("chinese_clip", ("ChineseCLIPImageProcessor",)), ("clip", ("CLIPImageProcessor",)),
    ("clipseg", ("ViTImageProcessor", "ViTImageProcessorFast")), ("conditional_detr", ("ConditionalDetrImageProcessor",)), ("convnext", ("ConvNextImageProcessor",)), ("convnextv2", ("ConvNextImageProcessor",)),
    ("cvt", ("ConvNextImageProcessor",)), ("data2vec-vision", ("BeitImageProcessor",)), ("deformable_detr", ("DeformableDetrImageProcessor",)), ("deit", ("DeiTImageProcessor",)), ("depth_anything", ("DPTImageProcessor",)),
    ("deta", ("DetaImageProcessor",)), ("detr", ("DetrImageProcessor",)), ("dinat", ("ViTImageProcessor", "ViTImageProcessorFast")), ("dinov2", ("BitImageProcessor",)), ("donut-swin", ("DonutImageProcessor",)),
    ("dpt", ("DPTImageProcessor",)), ("efficientformer", ("EfficientFormerImageProcessor",)), ("efficientnet", ("EfficientNetImageProcessor",)), ("flava", ("FlavaImageProcessor",)), ("focalnet", ("BitImageProcessor",)),
    ("fuyu", ("FuyuImageProcessor",)), ("git", ("CLIPImageProcessor",)), ("glpn", ("GLPNImageProcessor",)), ("grounding-dino", ("GroundingDinoImageProcessor",)), ("groupvit", ("CLIPImageProcessor",)),
    ("hiera", ("BitImageProcessor",)), ("hurlm", ("HurLMImageProcessor",)), ("idefics", ("IdeficsImageProcessor",)), ("idefics2", ("Idefics2ImageProcessor",)), ("imagegpt", ("ImageGPTImageProcessor",)), ("instructblip", ("BlipImageProcessor",)),
    ("instructblipvideo", ("InstructBlipVideoImageProcessor",)), ("kosmos-2", ("CLIPImageProcessor",)), ("layoutlmv2", ("LayoutLMv2ImageProcessor",)), ("layoutlmv3", ("LayoutLMv3ImageProcessor",)),
    ("levit", ("LevitImageProcessor",)), ("llava", ("CLIPImageProcessor",)), ("llava_next", ("LlavaNextImageProcessor",)), ("llava_next_video", ("LlavaNextVideoImageProcessor",)), ("llava_onevision", ("LlavaOnevisionImageProcessor",)),
    ("mask2former", ("Mask2FormerImageProcessor",)), ("maskformer", ("MaskFormerImageProcessor",)), ("mgp-str", ("ViTImageProcessor", "ViTImageProcessorFast")), ("mllama", ("MllamaImageProcessor",)), ("mobilenet_v1", ("MobileNetV1ImageProcessor",)),
    ("mobilenet_v2", ("MobileNetV2ImageProcessor",)), ("mobilevit", ("MobileViTImageProcessor",)), ("mobilevitv2", ("MobileViTImageProcessor",)), ("modular_entity", ("ModularEntityImageProcessor",)), ("nat", ("ViTImageProcessor", "ViTImageProcessorFast")),
    ("nougat", ("NougatImageProcessor",)), ("oneformer", ("OneFormerImageProcessor",)), ("owlv2", ("Owlv2ImageProcessor",)), ("owlvit", ("OwlViTImageProcessor",)), ("perceiver", ("PerceiverImageProcessor",)), ("pix2struct", ("Pix2StructImageProcessor",)),
    ("pixtral", ("PixtralImageProcessor",)), ("poolformer", ("PoolFormerImageProcessor",)), ("pvt", ("PvtImageProcessor",)), ("pvt_v2", ("PvtImageProcessor",)), ("qwen2_vl", ("Qwen2VLImageProcessor",)), ("regnet", ("ConvNextImageProcessor",)),
    ("resnet", ("ConvNextImageProcessor",)), ("rt_detr", "RTDetrImageProcessor"), ("sam", ("SamImageProcessor",)), ("sapi_image", ("SAPIImageImageProcessor",)), ("sapi_video", ("SAPIVideoImageProcessor",)), ("sapiens_vision", ("SapiensVisionImageProcessor",)),
    ("segformer", ("SegformerImageProcessor",)), ("seggpt", ("SegGptImageProcessor",)), ("siglip", ("SiglipImageProcessor",)), ("swiftformer", ("ViTImageProcessor", "ViTImageProcessorFast")), ("swin", ("ViTImageProcessor", "ViTImageProcessorFast")), ("swin2sr", ("Swin2SRImageProcessor",)),
    ("swinv2", ("ViTImageProcessor", "ViTImageProcessorFast")), ("table-transformer", ("DetrImageProcessor",)), ("timesformer", ("VideoMAEImageProcessor",)), ("tvlt", ("TvltImageProcessor",)), ("tvp", ("TvpImageProcessor",)), ("udop", ("LayoutLMv3ImageProcessor",)),
    ("upernet", ("SegformerImageProcessor",)), ("van", ("ConvNextImageProcessor",)), ("videomae", ("VideoMAEImageProcessor",)), ("vilt", ("ViltImageProcessor",)), ("vipllava", ("CLIPImageProcessor",)), ("vit", ("ViTImageProcessor", "ViTImageProcessorFast")),
    ("vit_hybrid", ("ViTHybridImageProcessor",)), ("vit_mae", ("ViTImageProcessor", "ViTImageProcessorFast")), ("vit_msn", ("ViTImageProcessor", "ViTImageProcessorFast")), ("vitmatte", ("VitMatteImageProcessor",)),
    ("xclip", ("CLIPImageProcessor",)), ("yolos", ("YolosImageProcessor",)), ("zoedepth", ("ZoeDepthImageProcessor",))])
for model_type, image_processors in IMAGE_PROCESSOR_MAPPING_NAMES.items():
    slow_image_processor_class, *fast_image_processor_class = image_processors
    if not is_vision_available(): slow_image_processor_class = None
    if not fast_image_processor_class or fast_image_processor_class[0] is None or not is_torchvision_available(): fast_image_processor_class = None
    else: fast_image_processor_class = fast_image_processor_class[0]
    IMAGE_PROCESSOR_MAPPING_NAMES[model_type] = (slow_image_processor_class, fast_image_processor_class)
IMAGE_PROCESSOR_MAPPING = _LazyAutoMapping(CONFIG_MAPPING_NAMES, IMAGE_PROCESSOR_MAPPING_NAMES)
def image_processor_class_from_name(class_name: str):
    if class_name == "BaseImageProcessorFast": return BaseImageProcessorFast
    for module_name, extractors in IMAGE_PROCESSOR_MAPPING_NAMES.items():
        if class_name in extractors:
            module_name = model_type_to_module_name(module_name)
            module = importlib.import_module(f".{module_name}", "sapiens_transformers.models")
            try: return getattr(module, class_name)
            except AttributeError: continue
    for _, extractors in IMAGE_PROCESSOR_MAPPING._extra_content.items():
        for extractor in extractors:
            if getattr(extractor, "__name__", None) == class_name: return extractor
    main_module = importlib.import_module("sapiens_transformers")
    if hasattr(main_module, class_name): return getattr(main_module, class_name)
    return None
def get_image_processor_config(pretrained_model_name_or_path: Union[str, os.PathLike], cache_dir: Optional[Union[str, os.PathLike]] = None, force_download: bool = False,
resume_download: Optional[bool] = None, proxies: Optional[Dict[str, str]] = None, token: Optional[Union[bool, str]] = None, revision: Optional[str] = None, local_files_only: bool = False, **kwargs):
    use_auth_token = kwargs.pop("use_auth_token", None)
    if use_auth_token is not None:
        warnings.warn("The `use_auth_token` argument is deprecated and will be removed in v1 of Sapiens Transformers. Please use `token` instead.", FutureWarning)
        if token is not None: raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
        token = use_auth_token
    resolved_config_file = get_file_from_repo(pretrained_model_name_or_path, IMAGE_PROCESSOR_NAME, cache_dir=cache_dir, force_download=force_download, resume_download=resume_download,
    proxies=proxies, token=token, revision=revision, local_files_only=local_files_only)
    if resolved_config_file is None:
        logger.info("Could not locate the image processor configuration file, will try to use the model config instead.")
        return {}
    with open(resolved_config_file, encoding="utf-8") as reader: return json.load(reader)
def _warning_fast_image_processor_available(fast_class): logger.warning(f"Fast image processor class {fast_class} is available for this model. Using slow image processor class. To use the fast image processor class set `use_fast=True`.")
class AutoImageProcessor:
    def __init__(self): raise EnvironmentError("AutoImageProcessor is designed to be instantiated using the `AutoImageProcessor.from_pretrained(pretrained_model_name_or_path)` method.")
    @classmethod
    @replace_list_option_in_docstrings(IMAGE_PROCESSOR_MAPPING_NAMES)
    def from_pretrained(cls, pretrained_model_name_or_path, *inputs, **kwargs):
        use_auth_token = kwargs.pop("use_auth_token", None)
        if use_auth_token is not None:
            warnings.warn("The `use_auth_token` argument is deprecated and will be removed in v1 of Sapiens Transformers. Please use `token` instead.", FutureWarning)
            if kwargs.get("token", None) is not None: raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
            kwargs["token"] = use_auth_token
        config = kwargs.pop("config", None)
        use_fast = kwargs.pop("use_fast", None)
        trust_remote_code = kwargs.pop("trust_remote_code", None)
        kwargs["_from_auto"] = True
        config_dict, _ = ImageProcessingMixin.get_image_processor_dict(pretrained_model_name_or_path, **kwargs)
        image_processor_class = config_dict.get("image_processor_type", None)
        image_processor_auto_map = None
        if "AutoImageProcessor" in config_dict.get("auto_map", {}): image_processor_auto_map = config_dict["auto_map"]["AutoImageProcessor"]
        if image_processor_class is None and image_processor_auto_map is None:
            feature_extractor_class = config_dict.pop("feature_extractor_type", None)
            if feature_extractor_class is not None: image_processor_class = feature_extractor_class.replace("FeatureExtractor", "ImageProcessor")
            if "AutoFeatureExtractor" in config_dict.get("auto_map", {}):
                feature_extractor_auto_map = config_dict["auto_map"]["AutoFeatureExtractor"]
                image_processor_auto_map = feature_extractor_auto_map.replace("FeatureExtractor", "ImageProcessor")
        if image_processor_class is None and image_processor_auto_map is None:
            if not isinstance(config, PretrainedConfig): config = AutoConfig.from_pretrained(pretrained_model_name_or_path, **kwargs)
            image_processor_class = getattr(config, "image_processor_type", None)
            if hasattr(config, "auto_map") and "AutoImageProcessor" in config.auto_map: image_processor_auto_map = config.auto_map["AutoImageProcessor"]
        if image_processor_class is not None:
            if use_fast is not None:
                if use_fast and not image_processor_class.endswith("Fast"): image_processor_class += "Fast"
                elif not use_fast and image_processor_class.endswith("Fast"): image_processor_class = image_processor_class[:-4]
            image_processor_class = image_processor_class_from_name(image_processor_class)
        has_remote_code = image_processor_auto_map is not None
        has_local_code = image_processor_class is not None or type(config) in IMAGE_PROCESSOR_MAPPING
        trust_remote_code = resolve_trust_remote_code(trust_remote_code, pretrained_model_name_or_path, has_local_code, has_remote_code)
        if image_processor_auto_map is not None and not isinstance(image_processor_auto_map, tuple): image_processor_auto_map = (image_processor_auto_map, None)
        if has_remote_code and trust_remote_code:
            if not use_fast and image_processor_auto_map[1] is not None: _warning_fast_image_processor_available(image_processor_auto_map[1])
            if use_fast and image_processor_auto_map[1] is not None: class_ref = image_processor_auto_map[1]
            else: class_ref = image_processor_auto_map[0]
            image_processor_class = get_class_from_dynamic_module(class_ref, pretrained_model_name_or_path, **kwargs)
            _ = kwargs.pop("code_revision", None)
            if os.path.isdir(pretrained_model_name_or_path): image_processor_class.register_for_auto_class()
            return image_processor_class.from_dict(config_dict, **kwargs)
        elif image_processor_class is not None: return image_processor_class.from_dict(config_dict, **kwargs)
        elif type(config) in IMAGE_PROCESSOR_MAPPING:
            image_processor_tuple = IMAGE_PROCESSOR_MAPPING[type(config)]
            image_processor_class_py, image_processor_class_fast = image_processor_tuple
            if not use_fast and image_processor_class_fast is not None: _warning_fast_image_processor_available(image_processor_class_fast)
            if image_processor_class_fast and (use_fast or image_processor_class_py is None): return image_processor_class_fast.from_pretrained(pretrained_model_name_or_path, *inputs, **kwargs)
            else:
                if image_processor_class_py is not None: return image_processor_class_py.from_pretrained(pretrained_model_name_or_path, *inputs, **kwargs)
                else: raise ValueError("This image processor cannot be instantiated. Please make sure you have `Pillow` installed.")
        raise ValueError(f"Unrecognized image processor in {pretrained_model_name_or_path}. Should have a `image_processor_type` key in its {IMAGE_PROCESSOR_NAME} of {CONFIG_NAME}, or one of the following `model_type` keys in its {CONFIG_NAME}: {', '.join(c for c in IMAGE_PROCESSOR_MAPPING_NAMES.keys())}")
    @staticmethod
    def register(config_class, image_processor_class=None, slow_image_processor_class=None, fast_image_processor_class=None, exist_ok=False):
        if image_processor_class is not None:
            if slow_image_processor_class is not None: raise ValueError("Cannot specify both image_processor_class and slow_image_processor_class")
            warnings.warn("The image_processor_class argument is deprecated and will be removed in v4.42. Please use `slow_image_processor_class`, or `fast_image_processor_class` instead", FutureWarning)
            slow_image_processor_class = image_processor_class
        if slow_image_processor_class is None and fast_image_processor_class is None: raise ValueError("You need to specify either slow_image_processor_class or fast_image_processor_class")
        if slow_image_processor_class is not None and issubclass(slow_image_processor_class, BaseImageProcessorFast): raise ValueError("You passed a fast image processor in as the `slow_image_processor_class`.")
        if fast_image_processor_class is not None and issubclass(fast_image_processor_class, BaseImageProcessor): raise ValueError("You passed a slow image processor in as the `fast_image_processor_class`.")
        if (slow_image_processor_class is not None and fast_image_processor_class is not None and issubclass(fast_image_processor_class, BaseImageProcessorFast) and fast_image_processor_class.slow_image_processor_class != slow_image_processor_class): raise ValueError(f"The fast processor class you are passing has a `slow_image_processor_class` attribute that is not consistent with the slow processor class you passed (fast tokenizer has {fast_image_processor_class.slow_image_processor_class} and you passed {slow_image_processor_class}. Fix one of those so they match!")
        if config_class in IMAGE_PROCESSOR_MAPPING._extra_content:
            existing_slow, existing_fast = IMAGE_PROCESSOR_MAPPING[config_class]
            if slow_image_processor_class is None: slow_image_processor_class = existing_slow
            if fast_image_processor_class is None: fast_image_processor_class = existing_fast
        IMAGE_PROCESSOR_MAPPING.register(config_class, (slow_image_processor_class, fast_image_processor_class), exist_ok=exist_ok)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
