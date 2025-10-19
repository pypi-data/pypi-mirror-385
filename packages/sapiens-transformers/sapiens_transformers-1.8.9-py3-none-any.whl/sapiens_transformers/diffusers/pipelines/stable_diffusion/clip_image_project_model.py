'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from torch import nn
from ...configuration_utils import ConfigMixin, register_to_config
from ...models.modeling_utils import ModelMixin
class CLIPImageProjection(ModelMixin, ConfigMixin):
    @register_to_config
    def __init__(self, hidden_size: int=768):
        super().__init__()
        self.hidden_size = hidden_size
        self.project = nn.Linear(self.hidden_size, self.hidden_size, bias=False)
    def forward(self, x): return self.project(x)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
