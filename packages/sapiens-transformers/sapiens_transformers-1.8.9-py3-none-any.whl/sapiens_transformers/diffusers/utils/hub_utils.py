'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import json
import os
import re
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Union
from uuid import uuid4
from huggingface_hub import ModelCard, ModelCardData, create_repo, hf_hub_download, model_info, snapshot_download, upload_folder
from huggingface_hub.constants import HF_HUB_CACHE, HF_HUB_DISABLE_TELEMETRY, HF_HUB_OFFLINE
from huggingface_hub.file_download import REGEX_COMMIT_HASH
from huggingface_hub.utils import EntryNotFoundError, RepositoryNotFoundError, RevisionNotFoundError, is_jinja_available, validate_hf_hub_args
from packaging import version
from requests import HTTPError
from .. import __version__
from .constants import DEPRECATED_REVISION_ARGS, HUGGINGFACE_CO_RESOLVE_ENDPOINT, SAFETENSORS_WEIGHTS_NAME, WEIGHTS_NAME
from .import_utils import ENV_VARS_TRUE_VALUES, _flax_version, _jax_version, _onnxruntime_version, _torch_version, is_flax_available, is_onnx_available, is_torch_available
MODEL_CARD_TEMPLATE_PATH = Path(__file__).parent / 'model_card_template.md'
SESSION_ID = uuid4().hex
def http_user_agent(user_agent: Union[Dict, str, None]=None) -> str:
    ua = f'sapiens_transformers.diffusers/{__version__}; python/{sys.version.split()[0]}; session_id/{SESSION_ID}'
    if HF_HUB_DISABLE_TELEMETRY or HF_HUB_OFFLINE: return ua + '; telemetry/off'
    if is_torch_available(): ua += f'; torch/{_torch_version}'
    if is_flax_available():
        ua += f'; jax/{_jax_version}'
        ua += f'; flax/{_flax_version}'
    if is_onnx_available(): ua += f'; onnxruntime/{_onnxruntime_version}'
    if os.environ.get('DIFFUSERS_IS_CI', '').upper() in ENV_VARS_TRUE_VALUES: ua += '; is_ci/true'
    if isinstance(user_agent, dict): ua += '; ' + '; '.join((f'{k}/{v}' for k, v in user_agent.items()))
    elif isinstance(user_agent, str): ua += '; ' + user_agent
    return ua
def load_or_create_model_card(repo_id_or_path: str=None, token: Optional[str]=None, is_pipeline: bool=False, from_training: bool=False, model_description: Optional[str]=None, base_model: str=None,
prompt: Optional[str]=None, license: Optional[str]=None, widget: Optional[List[dict]]=None, inference: Optional[bool]=None) -> ModelCard:
    """Args:"""
    if not is_jinja_available(): raise ValueError('Modelcard rendering is based on Jinja templates. Please make sure to have `jinja` installed before using `load_or_create_model_card`. To install it, please run `pip install Jinja2`.')
    try: model_card = ModelCard.load(repo_id_or_path, token=token)
    except (EntryNotFoundError, RepositoryNotFoundError):
        if from_training: model_card = ModelCard.from_template(card_data=ModelCardData(license=license, library_name='sapiens_transformers.diffusers', inference=inference, base_model=base_model,
        instance_prompt=prompt, widget=widget), template_path=MODEL_CARD_TEMPLATE_PATH, model_description=model_description)
        else:
            card_data = ModelCardData()
            component = 'pipeline' if is_pipeline else 'model'
            if model_description is None: model_description = f'This is the model card of a 🧨 diffusers {component} that has been pushed on the Hub. This model card has been automatically generated.'
            model_card = ModelCard.from_template(card_data, model_description=model_description)
    return model_card
def populate_model_card(model_card: ModelCard, tags: Union[str, List[str]]=None) -> ModelCard:
    if model_card.data.library_name is None: model_card.data.library_name = 'sapiens_transformers.diffusers'
    if tags is not None:
        if isinstance(tags, str): tags = [tags]
        if model_card.data.tags is None: model_card.data.tags = []
        for tag in tags: model_card.data.tags.append(tag)
    return model_card
def extract_commit_hash(resolved_file: Optional[str], commit_hash: Optional[str]=None):
    if resolved_file is None or commit_hash is not None: return commit_hash
    resolved_file = str(Path(resolved_file).as_posix())
    search = re.search('snapshots/([^/]+)/', resolved_file)
    if search is None: return None
    commit_hash = search.groups()[0]
    return commit_hash if REGEX_COMMIT_HASH.match(commit_hash) else None
hf_cache_home = os.path.expanduser(os.getenv('HF_HOME', os.path.join(os.getenv('XDG_CACHE_HOME', '~/.cache'), 'huggingface')))
old_diffusers_cache = os.path.join(hf_cache_home, 'sapiens_transformers.diffusers')
def move_cache(old_cache_dir: Optional[str]=None, new_cache_dir: Optional[str]=None) -> None:
    if new_cache_dir is None: new_cache_dir = HF_HUB_CACHE
    if old_cache_dir is None: old_cache_dir = old_diffusers_cache
    old_cache_dir = Path(old_cache_dir).expanduser()
    new_cache_dir = Path(new_cache_dir).expanduser()
    for old_blob_path in old_cache_dir.glob('**/blobs/*'):
        if old_blob_path.is_file() and (not old_blob_path.is_symlink()):
            new_blob_path = new_cache_dir / old_blob_path.relative_to(old_cache_dir)
            new_blob_path.parent.mkdir(parents=True, exist_ok=True)
            os.replace(old_blob_path, new_blob_path)
            os.symlink(new_blob_path, old_blob_path)
cache_version_file = os.path.join(HF_HUB_CACHE, 'version_diffusers_cache.txt')
if not os.path.isfile(cache_version_file): cache_version = 0
else:
    with open(cache_version_file) as f:
        try: cache_version = int(f.read())
        except ValueError: cache_version = 0
if cache_version < 1:
    old_cache_is_not_empty = os.path.isdir(old_diffusers_cache) and len(os.listdir(old_diffusers_cache)) > 0
    if old_cache_is_not_empty:
        try: move_cache()
        except Exception as e: trace = '\n'.join(traceback.format_tb(e.__traceback__))
if cache_version < 1:
    os.makedirs(HF_HUB_CACHE, exist_ok=True)
    with open(cache_version_file, 'w') as f: f.write('1')
def _add_variant(weights_name: str, variant: Optional[str]=None) -> str:
    if variant is not None:
        splits = weights_name.split('.')
        splits = splits[:-1] + [variant] + splits[-1:]
        weights_name = '.'.join(splits)
    return weights_name
@validate_hf_hub_args
def _get_model_file(pretrained_model_name_or_path: Union[str, Path], *, weights_name: str, subfolder: Optional[str]=None, cache_dir: Optional[str]=None, force_download: bool=False,
proxies: Optional[Dict]=None, local_files_only: bool=False, token: Optional[str]=None, user_agent: Optional[Union[Dict, str]]=None, revision: Optional[str]=None, commit_hash: Optional[str]=None):
    pretrained_model_name_or_path = str(pretrained_model_name_or_path)
    if os.path.isfile(pretrained_model_name_or_path): return pretrained_model_name_or_path
    elif os.path.isdir(pretrained_model_name_or_path):
        if os.path.isfile(os.path.join(pretrained_model_name_or_path, weights_name)):
            model_file = os.path.join(pretrained_model_name_or_path, weights_name)
            return model_file
        elif subfolder is not None and os.path.isfile(os.path.join(pretrained_model_name_or_path, subfolder, weights_name)):
            model_file = os.path.join(pretrained_model_name_or_path, subfolder, weights_name)
            return model_file
        else: raise EnvironmentError(f'Error no file named {weights_name} found in directory {pretrained_model_name_or_path}.')
    else:
        if revision in DEPRECATED_REVISION_ARGS and (weights_name == WEIGHTS_NAME or weights_name == SAFETENSORS_WEIGHTS_NAME) and (version.parse(version.parse(__version__).base_version) >= version.parse('0.22.0')):
            try:
                model_file = hf_hub_download(pretrained_model_name_or_path, filename=_add_variant(weights_name, revision), cache_dir=cache_dir, force_download=force_download, proxies=proxies,
                local_files_only=local_files_only, token=token, user_agent=user_agent, subfolder=subfolder, revision=revision or commit_hash)
                return model_file
            except: pass
        try:
            model_file = hf_hub_download(pretrained_model_name_or_path, filename=weights_name, cache_dir=cache_dir, force_download=force_download, proxies=proxies, local_files_only=local_files_only,
            token=token, user_agent=user_agent, subfolder=subfolder, revision=revision or commit_hash)
            return model_file
        except RepositoryNotFoundError as e: raise EnvironmentError(f"{pretrained_model_name_or_path} is not a local folder and is not a valid model identifier listed on 'https://huggingface.co/models'\nIf this is a private repository, make sure to pass a token having permission to this repo with `token` or log in with `huggingface-cli login`.") from e
        except RevisionNotFoundError as e: raise EnvironmentError(f"{revision} is not a valid git identifier (branch name, tag name or commit id) that exists for this model name. Check the model page at 'https://huggingface.co/{pretrained_model_name_or_path}' for available revisions.") from e
        except EntryNotFoundError as e: raise EnvironmentError(f'{pretrained_model_name_or_path} does not appear to have a file named {weights_name}.') from e
        except HTTPError as e: raise EnvironmentError(f'There was a specific connection error when trying to load {pretrained_model_name_or_path}:\n{e}') from e
        except ValueError as e: raise EnvironmentError(f"We couldn't connect to '{HUGGINGFACE_CO_RESOLVE_ENDPOINT}' to load this model, couldn't find it in the cached files and it looks like {pretrained_model_name_or_path} is not the path to a directory containing a file named {weights_name} or \nCheckout your internet connection or see how to run the library in offline mode at 'https://huggingface.co/docs/diffusers/installation#offline-mode'.") from e
        except EnvironmentError as e: raise EnvironmentError(f"Can't load the model for '{pretrained_model_name_or_path}'. If you were trying to load it from 'https://huggingface.co/models', make sure you don't have a local directory with the same name. Otherwise, make sure '{pretrained_model_name_or_path}' is the correct path to a directory containing a file named {weights_name}") from e
def _check_if_shards_exist_locally(local_dir, subfolder, original_shard_filenames):
    shards_path = os.path.join(local_dir, subfolder)
    shard_filenames = [os.path.join(shards_path, f) for f in original_shard_filenames]
    for shard_file in shard_filenames:
        if not os.path.exists(shard_file): raise ValueError(f'{shards_path} does not appear to have a file named {shard_file} which is required according to the checkpoint index.')
def _get_checkpoint_shard_files(pretrained_model_name_or_path, index_filename, cache_dir=None, proxies=None, local_files_only=False, token=None, user_agent=None, revision=None, subfolder=''):
    if not os.path.isfile(index_filename): raise ValueError(f"Can't find a checkpoint index ({index_filename}) in {pretrained_model_name_or_path}.")
    with open(index_filename, 'r') as f: index = json.loads(f.read())
    original_shard_filenames = sorted(set(index['weight_map'].values()))
    sharded_metadata = index['metadata']
    sharded_metadata['all_checkpoint_keys'] = list(index['weight_map'].keys())
    sharded_metadata['weight_map'] = index['weight_map'].copy()
    shards_path = os.path.join(pretrained_model_name_or_path, subfolder)
    if os.path.isdir(pretrained_model_name_or_path):
        _check_if_shards_exist_locally(pretrained_model_name_or_path, subfolder=subfolder, original_shard_filenames=original_shard_filenames)
        return (shards_path, sharded_metadata)
    allow_patterns = original_shard_filenames
    if subfolder is not None: allow_patterns = [os.path.join(subfolder, p) for p in allow_patterns]
    ignore_patterns = ['*.json', '*.md']
    model_files_info = model_info(pretrained_model_name_or_path, revision=revision, token=token)
    for shard_file in original_shard_filenames:
        shard_file_present = any((shard_file in k.rfilename for k in model_files_info.siblings))
        if not shard_file_present: raise EnvironmentError(f'{shards_path} does not appear to have a file named {shard_file} which is required according to the checkpoint index.')
    try:
        cached_folder = snapshot_download(pretrained_model_name_or_path, cache_dir=cache_dir, proxies=proxies, local_files_only=local_files_only, token=token, revision=revision,
        allow_patterns=allow_patterns, ignore_patterns=ignore_patterns, user_agent=user_agent)
        if subfolder is not None: cached_folder = os.path.join(cached_folder, subfolder)
    except HTTPError as e: raise EnvironmentError(f"We couldn't connect to '{HUGGINGFACE_CO_RESOLVE_ENDPOINT}' to load {pretrained_model_name_or_path}. You should try again after checking your internet connection.") from e
    return (cached_folder, sharded_metadata)
def _check_legacy_sharding_variant_format(folder: str=None, filenames: List[str]=None, variant: str=None):
    if filenames and folder: raise ValueError('Both `filenames` and `folder` cannot be provided.')
    if not filenames:
        filenames = []
        for _, _, files in os.walk(folder):
            for file in files: filenames.append(os.path.basename(file))
    transformers_index_format = '\\d{5}-of-\\d{5}'
    variant_file_re = re.compile(f'.*-{transformers_index_format}\\.{variant}\\.[a-z]+$')
    return any((variant_file_re.match(f) is not None for f in filenames))
class PushToHubMixin:
    def _upload_folder(self, working_dir: Union[str, os.PathLike], repo_id: str, token: Optional[str]=None, commit_message: Optional[str]=None, create_pr: bool=False):
        if commit_message is None:
            if 'Model' in self.__class__.__name__: commit_message = 'Upload model'
            elif 'Scheduler' in self.__class__.__name__: commit_message = 'Upload scheduler'
            else: commit_message = f'Upload {self.__class__.__name__}'
        return upload_folder(repo_id=repo_id, folder_path=working_dir, token=token, commit_message=commit_message, create_pr=create_pr)
    def push_to_hub(self, repo_id: str, commit_message: Optional[str]=None, private: Optional[bool]=None, token: Optional[str]=None, create_pr: bool=False,
    safe_serialization: bool=True, variant: Optional[str]=None) -> str:
        """Examples:"""
        repo_id = create_repo(repo_id, private=private, token=token, exist_ok=True).repo_id
        model_card = load_or_create_model_card(repo_id, token=token)
        model_card = populate_model_card(model_card)
        save_kwargs = {'safe_serialization': safe_serialization}
        if 'Scheduler' not in self.__class__.__name__: save_kwargs.update({'variant': variant})
        with tempfile.TemporaryDirectory() as tmpdir:
            self.save_pretrained(tmpdir, **save_kwargs)
            model_card.save(os.path.join(tmpdir, 'README.md'))
            return self._upload_folder(tmpdir, repo_id, token=token, commit_message=commit_message, create_pr=create_pr)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
