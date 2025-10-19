'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import os
import shutil
from pathlib import Path
from typing import Optional, Union
import numpy as np
from huggingface_hub import hf_hub_download
from huggingface_hub.utils import validate_hf_hub_args
from ..utils import ONNX_EXTERNAL_WEIGHTS_NAME, ONNX_WEIGHTS_NAME, is_onnx_available
if is_onnx_available(): import onnxruntime as ort
ORT_TO_NP_TYPE = {'tensor(bool)': np.bool_, 'tensor(int8)': np.int8, 'tensor(uint8)': np.uint8, 'tensor(int16)': np.int16, 'tensor(uint16)': np.uint16, 'tensor(int32)': np.int32,
'tensor(uint32)': np.uint32, 'tensor(int64)': np.int64, 'tensor(uint64)': np.uint64, 'tensor(float16)': np.float16, 'tensor(float)': np.float32, 'tensor(double)': np.float64}
class OnnxRuntimeModel:
    def __init__(self, model=None, **kwargs):
        self.model = model
        self.model_save_dir = kwargs.get('model_save_dir', None)
        self.latest_model_name = kwargs.get('latest_model_name', ONNX_WEIGHTS_NAME)
    def __call__(self, **kwargs):
        inputs = {k: np.array(v) for k, v in kwargs.items()}
        return self.model.run(None, inputs)
    @staticmethod
    def load_model(path: Union[str, Path], provider=None, sess_options=None):
        if provider is None: provider = 'CPUExecutionProvider'
        return ort.InferenceSession(path, providers=[provider], sess_options=sess_options)
    def _save_pretrained(self, save_directory: Union[str, Path], file_name: Optional[str]=None, **kwargs):
        model_file_name = file_name if file_name is not None else ONNX_WEIGHTS_NAME
        src_path = self.model_save_dir.joinpath(self.latest_model_name)
        dst_path = Path(save_directory).joinpath(model_file_name)
        try: shutil.copyfile(src_path, dst_path)
        except shutil.SameFileError: pass
        src_path = self.model_save_dir.joinpath(ONNX_EXTERNAL_WEIGHTS_NAME)
        if src_path.exists():
            dst_path = Path(save_directory).joinpath(ONNX_EXTERNAL_WEIGHTS_NAME)
            try: shutil.copyfile(src_path, dst_path)
            except shutil.SameFileError: pass
    def save_pretrained(self, save_directory: Union[str, os.PathLike], **kwargs):
        if os.path.isfile(save_directory): return
        os.makedirs(save_directory, exist_ok=True)
        self._save_pretrained(save_directory, **kwargs)
    @classmethod
    @validate_hf_hub_args
    def _from_pretrained(cls, model_id: Union[str, Path], token: Optional[Union[bool, str, None]]=None, revision: Optional[Union[str, None]]=None, force_download: bool=False,
    cache_dir: Optional[str]=None, file_name: Optional[str]=None, provider: Optional[str]=None, sess_options: Optional['ort.SessionOptions']=None, **kwargs):
        model_file_name = file_name if file_name is not None else ONNX_WEIGHTS_NAME
        if os.path.isdir(model_id):
            model = OnnxRuntimeModel.load_model(Path(model_id, model_file_name).as_posix(), provider=provider, sess_options=sess_options)
            kwargs['model_save_dir'] = Path(model_id)
        else:
            model_cache_path = hf_hub_download(repo_id=model_id, filename=model_file_name, token=token, revision=revision, cache_dir=cache_dir, force_download=force_download)
            kwargs['model_save_dir'] = Path(model_cache_path).parent
            kwargs['latest_model_name'] = Path(model_cache_path).name
            model = OnnxRuntimeModel.load_model(model_cache_path, provider=provider, sess_options=sess_options)
        return cls(model=model, **kwargs)
    @classmethod
    @validate_hf_hub_args
    def from_pretrained(cls, model_id: Union[str, Path], force_download: bool=True, token: Optional[str]=None, cache_dir: Optional[str]=None, **model_kwargs):
        revision = None
        if len(str(model_id).split('@')) == 2: model_id, revision = model_id.split('@')
        return cls._from_pretrained(model_id=model_id, revision=revision, cache_dir=cache_dir, force_download=force_download, token=token, **model_kwargs)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
