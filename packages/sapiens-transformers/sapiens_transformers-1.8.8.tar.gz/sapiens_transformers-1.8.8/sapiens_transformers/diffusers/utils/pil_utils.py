'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import List
import PIL.Image
import PIL.ImageOps
from packaging import version
from PIL import Image
if version.parse(version.parse(PIL.__version__).base_version) >= version.parse('9.1.0'): PIL_INTERPOLATION = {'linear': PIL.Image.Resampling.BILINEAR, 'bilinear': PIL.Image.Resampling.BILINEAR,
'bicubic': PIL.Image.Resampling.BICUBIC, 'lanczos': PIL.Image.Resampling.LANCZOS, 'nearest': PIL.Image.Resampling.NEAREST}
else: PIL_INTERPOLATION = {'linear': PIL.Image.LINEAR, 'bilinear': PIL.Image.BILINEAR, 'bicubic': PIL.Image.BICUBIC, 'lanczos': PIL.Image.LANCZOS, 'nearest': PIL.Image.NEAREST}
def pt_to_pil(images):
    images = (images / 2 + 0.5).clamp(0, 1)
    images = images.cpu().permute(0, 2, 3, 1).float().numpy()
    images = numpy_to_pil(images)
    return images
def numpy_to_pil(images):
    if images.ndim == 3: images = images[None, ...]
    images = (images * 255).round().astype('uint8')
    if images.shape[-1] == 1: pil_images = [Image.fromarray(image.squeeze(), mode='L') for image in images]
    else: pil_images = [Image.fromarray(image) for image in images]
    return pil_images
def make_image_grid(images: List[PIL.Image.Image], rows: int, cols: int, resize: int=None) -> PIL.Image.Image:
    assert len(images) == rows * cols
    if resize is not None: images = [img.resize((resize, resize)) for img in images]
    w, h = images[0].size
    grid = Image.new('RGB', size=(cols * w, rows * h))
    for i, img in enumerate(images): grid.paste(img, box=(i % cols * w, i // cols * h))
    return grid
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
