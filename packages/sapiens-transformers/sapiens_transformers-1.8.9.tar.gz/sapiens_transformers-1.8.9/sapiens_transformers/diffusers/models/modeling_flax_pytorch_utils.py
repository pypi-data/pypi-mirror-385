'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from flax.traverse_util import flatten_dict, unflatten_dict
from jax.random import PRNGKey
import jax.numpy as jnp
import re
def rename_key(key):
    regex = '\\w+[.]\\d+'
    pats = re.findall(regex, key)
    for pat in pats: key = key.replace(pat, '_'.join(pat.split('.')))
    return key
def rename_key_and_reshape_tensor(pt_tuple_key, pt_tensor, random_flax_state_dict):
    renamed_pt_tuple_key = pt_tuple_key[:-1] + ('scale',)
    if len(pt_tuple_key) > 1:
        for rename_from, rename_to in (('to_out_0', 'proj_attn'), ('to_k', 'key'), ('to_v', 'value'), ('to_q', 'query')):
            if pt_tuple_key[-2] == rename_from:
                weight_name = pt_tuple_key[-1]
                weight_name = 'kernel' if weight_name == 'weight' else weight_name
                renamed_pt_tuple_key = pt_tuple_key[:-2] + (rename_to, weight_name)
                if renamed_pt_tuple_key in random_flax_state_dict:
                    assert random_flax_state_dict[renamed_pt_tuple_key].shape == pt_tensor.T.shape
                    return (renamed_pt_tuple_key, pt_tensor.T)
    if any(('norm' in str_ for str_ in pt_tuple_key)) and pt_tuple_key[-1] == 'bias' and (pt_tuple_key[:-1] + ('bias',) not in random_flax_state_dict) and (pt_tuple_key[:-1] + ('scale',) in random_flax_state_dict):
        renamed_pt_tuple_key = pt_tuple_key[:-1] + ('scale',)
        return (renamed_pt_tuple_key, pt_tensor)
    elif pt_tuple_key[-1] in ['weight', 'gamma'] and pt_tuple_key[:-1] + ('scale',) in random_flax_state_dict:
        renamed_pt_tuple_key = pt_tuple_key[:-1] + ('scale',)
        return (renamed_pt_tuple_key, pt_tensor)
    if pt_tuple_key[-1] == 'weight' and pt_tuple_key[:-1] + ('embedding',) in random_flax_state_dict:
        pt_tuple_key = pt_tuple_key[:-1] + ('embedding',)
        return (renamed_pt_tuple_key, pt_tensor)
    renamed_pt_tuple_key = pt_tuple_key[:-1] + ('kernel',)
    if pt_tuple_key[-1] == 'weight' and pt_tensor.ndim == 4:
        pt_tensor = pt_tensor.transpose(2, 3, 1, 0)
        return (renamed_pt_tuple_key, pt_tensor)
    renamed_pt_tuple_key = pt_tuple_key[:-1] + ('kernel',)
    if pt_tuple_key[-1] == 'weight':
        pt_tensor = pt_tensor.T
        return (renamed_pt_tuple_key, pt_tensor)
    renamed_pt_tuple_key = pt_tuple_key[:-1] + ('weight',)
    if pt_tuple_key[-1] == 'gamma': return (renamed_pt_tuple_key, pt_tensor)
    renamed_pt_tuple_key = pt_tuple_key[:-1] + ('bias',)
    if pt_tuple_key[-1] == 'beta': return (renamed_pt_tuple_key, pt_tensor)
    return (pt_tuple_key, pt_tensor)
def convert_pytorch_state_dict_to_flax(pt_state_dict, flax_model, init_key=42):
    pt_state_dict = {k: v.numpy() for k, v in pt_state_dict.items()}
    random_flax_params = flax_model.init_weights(PRNGKey(init_key))
    random_flax_state_dict = flatten_dict(random_flax_params)
    flax_state_dict = {}
    for pt_key, pt_tensor in pt_state_dict.items():
        renamed_pt_key = rename_key(pt_key)
        pt_tuple_key = tuple(renamed_pt_key.split('.'))
        flax_key, flax_tensor = rename_key_and_reshape_tensor(pt_tuple_key, pt_tensor, random_flax_state_dict)
        if flax_key in random_flax_state_dict:
            if flax_tensor.shape != random_flax_state_dict[flax_key].shape: raise ValueError(f'PyTorch checkpoint seems to be incorrect. Weight {pt_key} was expected to be of shape {random_flax_state_dict[flax_key].shape}, but is {flax_tensor.shape}.')
        flax_state_dict[flax_key] = jnp.asarray(flax_tensor)
    return unflatten_dict(flax_state_dict)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
