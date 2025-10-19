'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...models.modeling_utils import ModelMixin
from ...configuration_utils import ConfigMixin
from ...utils import PIL_INTERPOLATION
from typing import List
from PIL import Image
import PIL.Image
import torch
class IFWatermarker(ModelMixin, ConfigMixin):
    def __init__(self):
        super().__init__()
        self.register_buffer('watermark_image', torch.zeros((62, 62, 4)))
        self.watermark_image_as_pil = None
    def apply_watermark(self, images: List[PIL.Image.Image], sample_size=None):
        h = images[0].height
        w = images[0].width
        sample_size = sample_size or h
        coef = min(h / sample_size, w / sample_size)
        img_h, img_w = (int(h / coef), int(w / coef)) if coef < 1 else (h, w)
        S1, S2 = (1024 ** 2, img_w * img_h)
        K = (S2 / S1) ** 0.5
        wm_size, wm_x, wm_y = (int(K * 62), img_w - int(14 * K), img_h - int(14 * K))
        if self.watermark_image_as_pil is None:
            watermark_image = self.watermark_image.to(torch.uint8).cpu().numpy()
            watermark_image = Image.fromarray(watermark_image, mode='RGBA')
            self.watermark_image_as_pil = watermark_image
        wm_img = self.watermark_image_as_pil.resize((wm_size, wm_size), PIL_INTERPOLATION['bicubic'], reducing_gap=None)
        for pil_img in images: pil_img.paste(wm_img, box=(wm_x - wm_size, wm_y - wm_size, wm_x, wm_y), mask=wm_img.split()[-1])
        return images
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
