"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Dict, Union, Optional
from ...image_utils import (VideoInput, is_valid_image, PILImageResampling, OPENAI_CLIP_MEAN, OPENAI_CLIP_STD, ChannelDimension, ImageInput, infer_channel_dimension_format,
make_list_of_images, to_numpy_array, validate_preprocess_arguments)
from ...utils import is_vision_available, TensorType
if is_vision_available(): from PIL import Image
from ...image_processing_utils import BaseImageProcessor, get_size_dict, BatchFeature
from ...image_transforms import (get_resize_output_image_size, convert_to_rgb, to_channel_dimension_format)
def make_batched_videos(videos) -> List[VideoInput]:
    if isinstance(videos, (list, tuple)) and isinstance(videos[0], (list, tuple)) and is_valid_image(videos[0][0]): return videos
    elif isinstance(videos, (list, tuple)) and is_valid_image(videos[0]):
        if isinstance(videos[0], Image.Image): return [videos]
        elif len(videos[0].shape) == 4: return [list(video) for video in videos]
    elif is_valid_image(videos) and len(videos.shape) == 4: return [list(videos)]
    raise ValueError(f"Could not make batched video from {videos}")
from numpy import ndarray as n_ndarray
class SAPIVideoImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values_videos"]
    def __init__(self, do_resize: bool = True, size: Dict[str, int] = None, image_grid_pinpoints: List = None, resample: PILImageResampling = PILImageResampling.BICUBIC,
    do_center_crop: bool = True, crop_size: Dict[str, int] = None, do_rescale: bool = True, rescale_factor: Union[int, float] = 1 / 255, do_normalize: bool = True,
    image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None, do_convert_rgb: bool = True, **kwargs) -> None:
        super().__init__(**kwargs)
        size = get_size_dict(size if size is not None else {"shortest_edge": 224}, default_to_square=False)
        crop_size = get_size_dict(crop_size if crop_size is not None else {"height": 224, "width": 224}, default_to_square=True, param_name="crop_size")
        self.do_resize, self.size, self.image_grid_pinpoints = do_resize, size, image_grid_pinpoints
        self.resample, self.do_center_crop, self.crop_size = resample, do_center_crop, crop_size
        self.do_rescale, self.rescale_factor, self.do_normalize = do_rescale, rescale_factor, do_normalize
        self.image_mean, self.image_std, self.do_convert_rgb = image_mean if image_mean is not None else OPENAI_CLIP_MEAN, image_std if image_std is not None else OPENAI_CLIP_STD, do_convert_rgb
    def resize(self, image: n_ndarray, size: Dict[str, int], resample: PILImageResampling = PILImageResampling.BICUBIC, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> n_ndarray:
        default_to_square = True
        if "shortest_edge" in size: size, default_to_square = size["shortest_edge"], False
        elif "height" in size and "width" in size: size = (size["height"], size["width"])
        else: raise ValueError("Size must contain either 'shortest_edge' or 'height' and 'width'.")
        output_size = get_resize_output_image_size(image, size=size, default_to_square=default_to_square, input_data_format=input_data_format)
        return resize(image, size=output_size, resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
    def _preprocess(self, images: ImageInput, do_resize: bool = None, size: Dict[str, int] = None, resample: PILImageResampling = None, do_center_crop: bool = None,
    crop_size: int = None, do_rescale: bool = None, rescale_factor: float = None, do_normalize: bool = None, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, do_convert_rgb: bool = None, data_format: Optional[ChannelDimension] = ChannelDimension.FIRST,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> Image.Image:
        images, all_images = make_list_of_images(images), []
        if do_convert_rgb: images = [convert_to_rgb(image) for image in images]
        images = [to_numpy_array(image) for image in images]
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images[0])
        for image in images:
            if do_resize: image = self.resize(image=image, size=size, resample=resample, input_data_format=input_data_format)
            if do_center_crop: image = self.center_crop(image=image, size=crop_size, input_data_format=input_data_format)
            if do_rescale: image = self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format)
            if do_normalize: image = self.normalize(image=image, mean=image_mean, std=image_std, input_data_format=input_data_format)
            all_images.append(image)
        return [to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format) for image in all_images]
    def preprocess(self, images: VideoInput, do_resize: bool = None, size: Dict[str, int] = None, resample: PILImageResampling = None, do_center_crop: bool = None,
    crop_size: int = None, do_rescale: bool = None, rescale_factor: float = None, do_normalize: bool = None, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, do_convert_rgb: bool = None, return_tensors: Optional[Union[str, TensorType]] = None,
    data_format: Optional[ChannelDimension] = ChannelDimension.FIRST, input_data_format: Optional[Union[str, ChannelDimension]] = None):
        do_resize = do_resize if do_resize is not None else self.do_resize
        size = get_size_dict(size if size is not None else self.size, param_name="size", default_to_square=False)
        resample, do_center_crop = resample if resample is not None else self.resample, do_center_crop if do_center_crop is not None else self.do_center_crop
        crop_size = get_size_dict(crop_size if crop_size is not None else self.crop_size, param_name="crop_size", default_to_square=True)
        do_rescale, rescale_factor = do_rescale if do_rescale is not None else self.do_rescale, rescale_factor if rescale_factor is not None else self.rescale_factor
        do_normalize, image_mean = do_normalize if do_normalize is not None else self.do_normalize, image_mean if image_mean is not None else self.image_mean
        image_std, do_convert_rgb = image_std if image_std is not None else self.image_std, do_convert_rgb if do_convert_rgb is not None else self.do_convert_rgb
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std,
        do_center_crop=do_center_crop, crop_size=crop_size, do_resize=do_resize, size=size, resample=resample)
        pixel_values = [self._preprocess(frames, do_resize=do_resize, size=size, resample=resample, do_center_crop=do_center_crop, crop_size=crop_size, do_rescale=do_rescale,
        rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std, data_format=data_format, input_data_format=input_data_format)
        for frames in make_batched_videos(images)]
        return BatchFeature(data={"pixel_values_videos": pixel_values}, tensor_type=return_tensors)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
