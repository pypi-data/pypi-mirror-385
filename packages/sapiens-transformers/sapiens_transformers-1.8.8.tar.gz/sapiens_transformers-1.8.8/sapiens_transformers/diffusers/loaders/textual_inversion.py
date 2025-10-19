'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..utils import _get_model_file, is_sapiens_accelerator_available, is_transformers_available
from huggingface_hub.utils import validate_hf_hub_args
from ..models.modeling_utils import load_state_dict
from typing import Dict, List, Optional, Union
from torch import nn
import safetensors
import torch
if is_sapiens_accelerator_available(): from sapiens_accelerator.hooks import AlignDevicesHook, CpuOffload, remove_hook_from_module
if is_transformers_available(): from sapiens_transformers import PreTrainedModel, PreTrainedTokenizer
TEXT_INVERSION_NAME = 'learned_embeds.bin'
TEXT_INVERSION_NAME_SAFE = 'learned_embeds.safetensors'
@validate_hf_hub_args
def load_textual_inversion_state_dicts(pretrained_model_name_or_paths, **kwargs):
    cache_dir = kwargs.pop('cache_dir', None)
    force_download = kwargs.pop('force_download', False)
    proxies = kwargs.pop('proxies', None)
    local_files_only = kwargs.pop('local_files_only', None)
    token = kwargs.pop('token', None)
    revision = kwargs.pop('revision', None)
    subfolder = kwargs.pop('subfolder', None)
    weight_name = kwargs.pop('weight_name', None)
    use_safetensors = kwargs.pop('use_safetensors', None)
    allow_pickle = False
    if use_safetensors is None:
        use_safetensors = True
        allow_pickle = True
    user_agent = {'file_type': 'text_inversion', 'framework': 'pytorch'}
    state_dicts = []
    for pretrained_model_name_or_path in pretrained_model_name_or_paths:
        if not isinstance(pretrained_model_name_or_path, (dict, torch.Tensor)):
            model_file = None
            if use_safetensors and weight_name is None or (weight_name is not None and weight_name.endswith('.safetensors')):
                try:
                    model_file = _get_model_file(pretrained_model_name_or_path, weights_name=weight_name or TEXT_INVERSION_NAME_SAFE, cache_dir=cache_dir, force_download=force_download,
                    proxies=proxies, local_files_only=local_files_only, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent)
                    state_dict = safetensors.torch.load_file(model_file, device='cpu')
                except Exception as e:
                    if not allow_pickle: raise e
                    model_file = None
            if model_file is None:
                model_file = _get_model_file(pretrained_model_name_or_path, weights_name=weight_name or TEXT_INVERSION_NAME, cache_dir=cache_dir, force_download=force_download, proxies=proxies,
                local_files_only=local_files_only, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent)
                state_dict = load_state_dict(model_file)
        else: state_dict = pretrained_model_name_or_path
        state_dicts.append(state_dict)
    return state_dicts
class TextualInversionLoaderMixin:
    def maybe_convert_prompt(self, prompt: Union[str, List[str]], tokenizer: 'PreTrainedTokenizer'):
        """Returns:"""
        if not isinstance(prompt, List): prompts = [prompt]
        else: prompts = prompt
        prompts = [self._maybe_convert_prompt(p, tokenizer) for p in prompts]
        if not isinstance(prompt, List): return prompts[0]
        return prompts
    def _maybe_convert_prompt(self, prompt: str, tokenizer: 'PreTrainedTokenizer'):
        """Returns:"""
        tokens = tokenizer.tokenize(prompt)
        unique_tokens = set(tokens)
        for token in unique_tokens:
            if token in tokenizer.added_tokens_encoder:
                replacement = token
                i = 1
                while f'{token}_{i}' in tokenizer.added_tokens_encoder:
                    replacement += f' {token}_{i}'
                    i += 1
                prompt = prompt.replace(token, replacement)
        return prompt
    def _check_text_inv_inputs(self, tokenizer, text_encoder, pretrained_model_name_or_paths, tokens):
        if tokenizer is None: raise ValueError(f'{self.__class__.__name__} requires `self.tokenizer` or passing a `tokenizer` of type `PreTrainedTokenizer` for calling `{self.load_textual_inversion.__name__}`')
        if text_encoder is None: raise ValueError(f'{self.__class__.__name__} requires `self.text_encoder` or passing a `text_encoder` of type `PreTrainedModel` for calling `{self.load_textual_inversion.__name__}`')
        if len(pretrained_model_name_or_paths) > 1 and len(pretrained_model_name_or_paths) != len(tokens): raise ValueError(f'You have passed a list of models of length {len(pretrained_model_name_or_paths)}, and list of tokens of length {len(tokens)} Make sure both lists have the same length.')
        valid_tokens = [t for t in tokens if t is not None]
        if len(set(valid_tokens)) < len(valid_tokens): raise ValueError(f'You have passed a list of tokens that contains duplicates: {tokens}')
    @staticmethod
    def _retrieve_tokens_and_embeddings(tokens, state_dicts, tokenizer):
        all_tokens = []
        all_embeddings = []
        for state_dict, token in zip(state_dicts, tokens):
            if isinstance(state_dict, torch.Tensor):
                if token is None: raise ValueError('You are trying to load a textual inversion embedding that has been saved as a PyTorch tensor. Make sure to pass the name of the corresponding token in this case: `token=...`.')
                loaded_token = token
                embedding = state_dict
            elif len(state_dict) == 1: loaded_token, embedding = next(iter(state_dict.items()))
            elif 'string_to_param' in state_dict:
                loaded_token = state_dict['name']
                embedding = state_dict['string_to_param']['*']
            else: raise ValueError(f'Loaded state dictionary is incorrect: {state_dict}. \n\nPlease verify that the loaded state dictionary of the textual embedding either only has a single key or includes the `string_to_param` input key.')
            if not (token is not None and loaded_token != token): token = loaded_token
            if token in tokenizer.get_vocab(): raise ValueError(f'Token {token} already in tokenizer vocabulary. Please choose a different token name or remove {token} and embedding from the tokenizer and text encoder.')
            all_tokens.append(token)
            all_embeddings.append(embedding)
        return (all_tokens, all_embeddings)
    @staticmethod
    def _extend_tokens_and_embeddings(tokens, embeddings, tokenizer):
        all_tokens = []
        all_embeddings = []
        for embedding, token in zip(embeddings, tokens):
            if f'{token}_1' in tokenizer.get_vocab():
                multi_vector_tokens = [token]
                i = 1
                while f'{token}_{i}' in tokenizer.added_tokens_encoder:
                    multi_vector_tokens.append(f'{token}_{i}')
                    i += 1
                raise ValueError(f'Multi-vector Token {multi_vector_tokens} already in tokenizer vocabulary. Please choose a different token name or remove the {multi_vector_tokens} and embedding from the tokenizer and text encoder.')
            is_multi_vector = len(embedding.shape) > 1 and embedding.shape[0] > 1
            if is_multi_vector:
                all_tokens += [token] + [f'{token}_{i}' for i in range(1, embedding.shape[0])]
                all_embeddings += [e for e in embedding]
            else:
                all_tokens += [token]
                all_embeddings += [embedding[0]] if len(embedding.shape) > 1 else [embedding]
        return (all_tokens, all_embeddings)
    @validate_hf_hub_args
    def load_textual_inversion(self, pretrained_model_name_or_path: Union[str, List[str], Dict[str, torch.Tensor], List[Dict[str, torch.Tensor]]], token: Optional[Union[str, List[str]]]=None,
    tokenizer: Optional['PreTrainedTokenizer']=None, text_encoder: Optional['PreTrainedModel']=None, **kwargs):
        tokenizer = tokenizer or getattr(self, 'tokenizer', None)
        text_encoder = text_encoder or getattr(self, 'text_encoder', None)
        pretrained_model_name_or_paths = [pretrained_model_name_or_path] if not isinstance(pretrained_model_name_or_path, list) else pretrained_model_name_or_path
        tokens = [token] if not isinstance(token, list) else token
        if tokens[0] is None: tokens = tokens * len(pretrained_model_name_or_paths)
        self._check_text_inv_inputs(tokenizer, text_encoder, pretrained_model_name_or_paths, tokens)
        state_dicts = load_textual_inversion_state_dicts(pretrained_model_name_or_paths, **kwargs)
        if len(tokens) > 1 and len(state_dicts) == 1:
            if isinstance(state_dicts[0], torch.Tensor):
                state_dicts = list(state_dicts[0])
                if len(tokens) != len(state_dicts): raise ValueError(f'You have passed a state_dict contains {len(state_dicts)} embeddings, and list of tokens of length {len(tokens)} Make sure both have the same length.')
        tokens, embeddings = self._retrieve_tokens_and_embeddings(tokens, state_dicts, tokenizer)
        tokens, embeddings = self._extend_tokens_and_embeddings(tokens, embeddings, tokenizer)
        expected_emb_dim = text_encoder.get_input_embeddings().weight.shape[-1]
        if any((expected_emb_dim != emb.shape[-1] for emb in embeddings)): raise ValueError('Loaded embeddings are of incorrect shape. Expected each textual inversion embedding to be of shape {input_embeddings.shape[-1]}, but are {embeddings.shape[-1]} ')
        is_model_cpu_offload = False
        is_sequential_cpu_offload = False
        if self.hf_device_map is None:
            for _, component in self.components.items():
                if isinstance(component, nn.Module):
                    if hasattr(component, '_hf_hook'):
                        is_model_cpu_offload = isinstance(getattr(component, '_hf_hook'), CpuOffload)
                        is_sequential_cpu_offload = isinstance(getattr(component, '_hf_hook'), AlignDevicesHook) or (hasattr(component._hf_hook, 'hooks') and isinstance(component._hf_hook.hooks[0], AlignDevicesHook))
                        remove_hook_from_module(component, recurse=is_sequential_cpu_offload)
        device = text_encoder.device
        dtype = text_encoder.dtype
        text_encoder.resize_token_embeddings(len(tokenizer) + len(tokens))
        input_embeddings = text_encoder.get_input_embeddings().weight
        for token, embedding in zip(tokens, embeddings):
            tokenizer.add_tokens(token)
            token_id = tokenizer.convert_tokens_to_ids(token)
            input_embeddings.data[token_id] = embedding
        input_embeddings.to(dtype=dtype, device=device)
        if is_model_cpu_offload: self.enable_model_cpu_offload()
        elif is_sequential_cpu_offload: self.enable_sequential_cpu_offload()
    def unload_textual_inversion(self, tokens: Optional[Union[str, List[str]]]=None, tokenizer: Optional['PreTrainedTokenizer']=None, text_encoder: Optional['PreTrainedModel']=None):
        tokenizer = tokenizer or getattr(self, 'tokenizer', None)
        text_encoder = text_encoder or getattr(self, 'text_encoder', None)
        token_ids = []
        last_special_token_id = None
        if tokens:
            if isinstance(tokens, str): tokens = [tokens]
            for added_token_id, added_token in tokenizer.added_tokens_decoder.items():
                if not added_token.special:
                    if added_token.content in tokens: token_ids.append(added_token_id)
                else: last_special_token_id = added_token_id
            if len(token_ids) == 0: raise ValueError('No tokens to remove found')
        else:
            tokens = []
            for added_token_id, added_token in tokenizer.added_tokens_decoder.items():
                if not added_token.special:
                    token_ids.append(added_token_id)
                    tokens.append(added_token.content)
                else: last_special_token_id = added_token_id
        for token_id, token_to_remove in zip(token_ids, tokens):
            del tokenizer._added_tokens_decoder[token_id]
            del tokenizer._added_tokens_encoder[token_to_remove]
        key_id = 1
        for token_id in tokenizer.added_tokens_decoder:
            if token_id > last_special_token_id and token_id > last_special_token_id + key_id:
                token = tokenizer._added_tokens_decoder[token_id]
                tokenizer._added_tokens_decoder[last_special_token_id + key_id] = token
                del tokenizer._added_tokens_decoder[token_id]
                tokenizer._added_tokens_encoder[token.content] = last_special_token_id + key_id
                key_id += 1
        tokenizer._update_trie()
        tokenizer._update_total_vocab_size()
        text_embedding_dim = text_encoder.get_input_embeddings().embedding_dim
        temp_text_embedding_weights = text_encoder.get_input_embeddings().weight
        text_embedding_weights = temp_text_embedding_weights[:last_special_token_id + 1]
        to_append = []
        for i in range(last_special_token_id + 1, temp_text_embedding_weights.shape[0]):
            if i not in token_ids: to_append.append(temp_text_embedding_weights[i].unsqueeze(0))
        if len(to_append) > 0:
            to_append = torch.cat(to_append, dim=0)
            text_embedding_weights = torch.cat([text_embedding_weights, to_append], dim=0)
        text_embeddings_filtered = nn.Embedding(text_embedding_weights.shape[0], text_embedding_dim)
        text_embeddings_filtered.weight.data = text_embedding_weights
        text_encoder.set_input_embeddings(text_embeddings_filtered)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
