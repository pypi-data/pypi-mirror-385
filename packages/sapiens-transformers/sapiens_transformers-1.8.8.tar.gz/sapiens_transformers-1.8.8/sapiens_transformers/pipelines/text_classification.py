"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import inspect
import warnings
from typing import Dict
import numpy as np
from ..utils import ExplicitEnum, add_end_docstrings, is_tf_available, is_torch_available
from .base import GenericTensor, Pipeline, build_pipeline_init_args
if is_tf_available(): from ..models.auto.modeling_tf_auto import TF_MODEL_FOR_SEQUENCE_CLASSIFICATION_MAPPING_NAMES
if is_torch_available(): from ..models.auto.modeling_auto import MODEL_FOR_SEQUENCE_CLASSIFICATION_MAPPING_NAMES
def sigmoid(_outputs): return 1.0 / (1.0 + np.exp(-_outputs))
def softmax(_outputs):
    maxes = np.max(_outputs, axis=-1, keepdims=True)
    shifted_exp = np.exp(_outputs - maxes)
    return shifted_exp / shifted_exp.sum(axis=-1, keepdims=True)
class ClassificationFunction(ExplicitEnum):
    SIGMOID = "sigmoid"
    SOFTMAX = "softmax"
    NONE = "none"
@add_end_docstrings(build_pipeline_init_args(has_tokenizer=True),
    r"""
        return_all_scores (`bool`, *optional*, defaults to `False`):
            Whether to return all prediction scores or just the one of the predicted class.
        function_to_apply (`str`, *optional*, defaults to `"default"`):
            The function to apply to the model outputs in order to retrieve the scores. Accepts four different values:
            - `"default"`: if the model has a single label, will apply the sigmoid function on the output. If the model
              has several labels, will apply the softmax function on the output.
            - `"sigmoid"`: Applies the sigmoid function on the output.
            - `"softmax"`: Applies the softmax function on the output.
            - `"none"`: Does not apply any function on the output.""")
class TextClassificationPipeline(Pipeline):
    return_all_scores = False
    function_to_apply = ClassificationFunction.NONE
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.check_model_type(TF_MODEL_FOR_SEQUENCE_CLASSIFICATION_MAPPING_NAMES if self.framework == "tf" else MODEL_FOR_SEQUENCE_CLASSIFICATION_MAPPING_NAMES)
    def _sanitize_parameters(self, return_all_scores=None, function_to_apply=None, top_k="", **tokenizer_kwargs):
        preprocess_params = tokenizer_kwargs
        postprocess_params = {}
        if hasattr(self.model.config, "return_all_scores") and return_all_scores is None: return_all_scores = self.model.config.return_all_scores
        if isinstance(top_k, int) or top_k is None:
            postprocess_params["top_k"] = top_k
            postprocess_params["_legacy"] = False
        elif return_all_scores is not None:
            warnings.warn("`return_all_scores` is now deprecated,  if want a similar functionality use `top_k=None` instead of `return_all_scores=True` or `top_k=1` instead of `return_all_scores=False`.", UserWarning)
            if return_all_scores: postprocess_params["top_k"] = None
            else: postprocess_params["top_k"] = 1
        if isinstance(function_to_apply, str): function_to_apply = ClassificationFunction[function_to_apply.upper()]
        if function_to_apply is not None: postprocess_params["function_to_apply"] = function_to_apply
        return preprocess_params, {}, postprocess_params
    def __call__(self, inputs, **kwargs):
        inputs = (inputs,)
        result = super().__call__(*inputs, **kwargs)
        _legacy = "top_k" not in kwargs
        if isinstance(inputs[0], str) and _legacy: return [result]
        else: return result
    def preprocess(self, inputs, **tokenizer_kwargs) -> Dict[str, GenericTensor]:
        return_tensors = self.framework
        if isinstance(inputs, dict): return self.tokenizer(**inputs, return_tensors=return_tensors, **tokenizer_kwargs)
        elif isinstance(inputs, list) and len(inputs) == 1 and isinstance(inputs[0], list) and len(inputs[0]) == 2: return self.tokenizer(text=inputs[0][0], text_pair=inputs[0][1], return_tensors=return_tensors, **tokenizer_kwargs)
        elif isinstance(inputs, list): raise ValueError("The pipeline received invalid inputs, if you are trying to send text pairs, you can try to send a"+' dictionary `{"text": "My text", "text_pair": "My pair"}` in order to send a text pair.')
        return self.tokenizer(inputs, return_tensors=return_tensors, **tokenizer_kwargs)
    def _forward(self, model_inputs):
        model_forward = self.model.forward if self.framework == "pt" else self.model.call
        if "use_cache" in inspect.signature(model_forward).parameters.keys(): model_inputs["use_cache"] = False
        return self.model(**model_inputs)
    def postprocess(self, model_outputs, function_to_apply=None, top_k=1, _legacy=True):
        if function_to_apply is None:
            if self.model.config.problem_type == "multi_label_classification" or self.model.config.num_labels == 1: function_to_apply = ClassificationFunction.SIGMOID
            elif self.model.config.problem_type == "single_label_classification" or self.model.config.num_labels > 1: function_to_apply = ClassificationFunction.SOFTMAX
            elif hasattr(self.model.config, "function_to_apply") and function_to_apply is None: function_to_apply = self.model.config.function_to_apply
            else: function_to_apply = ClassificationFunction.NONE
        outputs = model_outputs["logits"][0]
        if self.framework == "pt": outputs = outputs.float().numpy()
        else: outputs = outputs.numpy()
        if function_to_apply == ClassificationFunction.SIGMOID: scores = sigmoid(outputs)
        elif function_to_apply == ClassificationFunction.SOFTMAX: scores = softmax(outputs)
        elif function_to_apply == ClassificationFunction.NONE: scores = outputs
        else: raise ValueError(f"Unrecognized `function_to_apply` argument: {function_to_apply}")
        if top_k == 1 and _legacy: return {"label": self.model.config.id2label[scores.argmax().item()], "score": scores.max().item()}
        dict_scores = [{"label": self.model.config.id2label[i], "score": score.item()} for i, score in enumerate(scores)]
        if not _legacy:
            dict_scores.sort(key=lambda x: x["score"], reverse=True)
            if top_k is not None: dict_scores = dict_scores[:top_k]
        return dict_scores
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
