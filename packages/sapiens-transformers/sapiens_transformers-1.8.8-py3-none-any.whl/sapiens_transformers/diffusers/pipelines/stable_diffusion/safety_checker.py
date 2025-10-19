'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import numpy as np
import torch
import torch.nn as nn
from sapiens_transformers import CLIPConfig, CLIPVisionModel, PreTrainedModel
def cosine_distance(image_embeds, text_embeds):
    normalized_image_embeds = nn.functional.normalize(image_embeds)
    normalized_text_embeds = nn.functional.normalize(text_embeds)
    return torch.mm(normalized_image_embeds, normalized_text_embeds.t())
class StableDiffusionSafetyChecker(PreTrainedModel):
    config_class = CLIPConfig
    main_input_name = 'clip_input'
    _no_split_modules = ['CLIPEncoderLayer']
    def __init__(self, config: CLIPConfig):
        super().__init__(config)
        self.vision_model = CLIPVisionModel(config.vision_config)
        self.visual_projection = nn.Linear(config.vision_config.hidden_size, config.projection_dim, bias=False)
        self.concept_embeds = nn.Parameter(torch.ones(17, config.projection_dim), requires_grad=False)
        self.special_care_embeds = nn.Parameter(torch.ones(3, config.projection_dim), requires_grad=False)
        self.concept_embeds_weights = nn.Parameter(torch.ones(17), requires_grad=False)
        self.special_care_embeds_weights = nn.Parameter(torch.ones(3), requires_grad=False)
    @torch.no_grad()
    def forward(self, clip_input, images):
        pooled_output = self.vision_model(clip_input)[1]
        image_embeds = self.visual_projection(pooled_output)
        special_cos_dist = cosine_distance(image_embeds, self.special_care_embeds).cpu().float().numpy()
        cos_dist = cosine_distance(image_embeds, self.concept_embeds).cpu().float().numpy()
        result = []
        batch_size = image_embeds.shape[0]
        for i in range(batch_size):
            result_img = {'special_scores': {}, 'special_care': [], 'concept_scores': {}, 'bad_concepts': []}
            adjustment = 0.0
            for concept_idx in range(len(special_cos_dist[0])):
                concept_cos = special_cos_dist[i][concept_idx]
                concept_threshold = self.special_care_embeds_weights[concept_idx].item()
                result_img['special_scores'][concept_idx] = round(concept_cos - concept_threshold + adjustment, 3)
                if result_img['special_scores'][concept_idx] > 0:
                    result_img['special_care'].append({concept_idx, result_img['special_scores'][concept_idx]})
                    adjustment = 0.01
            for concept_idx in range(len(cos_dist[0])):
                concept_cos = cos_dist[i][concept_idx]
                concept_threshold = self.concept_embeds_weights[concept_idx].item()
                result_img['concept_scores'][concept_idx] = round(concept_cos - concept_threshold + adjustment, 3)
                if result_img['concept_scores'][concept_idx] > 0: result_img['bad_concepts'].append(concept_idx)
            result.append(result_img)
        has_nsfw_concepts = [len(res['bad_concepts']) > 0 for res in result]
        for idx, has_nsfw_concept in enumerate(has_nsfw_concepts):
            if has_nsfw_concept:
                if torch.is_tensor(images) or torch.is_tensor(images[0]): images[idx] = torch.zeros_like(images[idx])
                else: images[idx] = np.zeros(images[idx].shape)
        return (images, has_nsfw_concepts)
    @torch.no_grad()
    def forward_onnx(self, clip_input: torch.Tensor, images: torch.Tensor):
        pooled_output = self.vision_model(clip_input)[1]
        image_embeds = self.visual_projection(pooled_output)
        special_cos_dist = cosine_distance(image_embeds, self.special_care_embeds)
        cos_dist = cosine_distance(image_embeds, self.concept_embeds)
        adjustment = 0.0
        special_scores = special_cos_dist - self.special_care_embeds_weights + adjustment
        special_care = torch.any(special_scores > 0, dim=1)
        special_adjustment = special_care * 0.01
        special_adjustment = special_adjustment.unsqueeze(1).expand(-1, cos_dist.shape[1])
        concept_scores = cos_dist - self.concept_embeds_weights + special_adjustment
        has_nsfw_concepts = torch.any(concept_scores > 0, dim=1)
        images[has_nsfw_concepts] = 0.0
        return (images, has_nsfw_concepts)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
