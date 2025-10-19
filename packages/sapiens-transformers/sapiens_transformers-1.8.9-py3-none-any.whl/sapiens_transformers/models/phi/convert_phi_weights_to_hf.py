"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import argparse
import gc
import os
import safetensors
import torch
from huggingface_hub import hf_hub_download
from sapiens_transformers import PhiConfig, PhiForCausalLM
_MODELS = {'microsoft/phi-1': ['https://huggingface.co/microsoft/phi-1/blob/main/pytorch_model.bin'], 'microsoft/phi-1_5': ['https://huggingface.co/microsoft/phi-1_5/blob/main/pytorch_model.bin'],
'microsoft/phi-2': ['https://huggingface.co/microsoft/phi-2/blob/main/model-00001-of-00002.safetensors', 'https://huggingface.co/microsoft/phi-2/blob/main/model-00002-of-00002.safetensors']}
PHI_MAPPING = {'transformer.embd.wte.weight': 'model.embed_tokens.weight', 'lm_head.linear': 'lm_head', 'lm_head.ln': 'model.final_layernorm', 'layers': 'model.layers', 'transformer': 'model',
'.h.': '.layers.', 'ln': 'input_layernorm', 'mixer': 'self_attn', 'Wqkv': 'query_key_value', 'out_proj': 'dense'}
def convert_weights(original_weights, mapping, config):
    converted_weights = {}
    original_weights_keys = sorted(original_weights.keys())
    for original_weights_key in original_weights_keys:
        new_key = original_weights_key
        if "rotary_emb" in new_key: continue
        if "Wqkv" in new_key:
            if "weight" in new_key:
                weight = original_weights[new_key]
                weights_shape = weight.shape
                weight = (weight.view(3, config.num_attention_heads, -1, config.hidden_size).transpose(0, 1).reshape(*weights_shape))
                original_weights[new_key] = weight
            elif "bias" in new_key:
                bias = original_weights[new_key]
                bias_shape = bias.shape
                bias = bias.view(3, config.num_attention_heads, -1).transpose(0, 1).reshape(*bias_shape)
                original_weights[new_key] = bias
        for k, v in mapping.items():
            if k in new_key: new_key = new_key.replace(k, v)
        converted_weights[new_key] = original_weights.pop(original_weights_key)
    return converted_weights
def _download(url: str, root: str):
    repo_id = f"{url.split('/')[3]}/{url.split('/')[4]}"
    filename = f"{url.split('/')[-1]}"
    hf_hub_download(repo_id=repo_id, filename=filename, force_filename=root, local_dir_use_symlinks=False)
def convert_phi_weights(model_name, checkpoint_path, pytorch_dump_folder_path, use_cuda, save_weights_directly, _MODELS):
    _MODELS = _MODELS if model_name not in _MODELS.keys() else {model_name: _MODELS.get(model_name)}
    device = "cuda" if torch.cuda.is_available() and use_cuda else "cpu"
    for model_name, model_url in _MODELS.items():
        converted_checkpoint = {}
        model_checkpoint = {}
        for model_each_url in model_url:
            model_path = os.path.join(checkpoint_path, model_name + "_" + model_each_url.split("/")[-1])
            if not os.path.exists(model_path):
                print(f"\n{model_name} was not found! Downloading it to {model_path}")
                _download(url=model_each_url, root=model_path)
            if model_path.endswith("safetensors"): loaded_weights = safetensors.torch.load_file(model_path, device=device)
            else: loaded_weights = torch.load(model_path, map_location=device)
            model_checkpoint.update(**loaded_weights)
        model_type = model_name.split("/")[1]
        config = PhiConfig()
        if model_type == "phi-2":
            config.hidden_size = 2560
            config.intermediate_size = 10240
            config.num_hidden_layers = 32
            config.resid_pdrop = 0.1
            config.partial_rotary_factor = 0.4
            config.num_hidden_layers = 32
            config.torch_dtype = "float16"
        converted_checkpoint.update(**convert_weights(model_checkpoint, PHI_MAPPING, config))
        if save_weights_directly:
            save_weights_path = os.path.join(pytorch_dump_folder_path, model_type + "_pytorch_model.bin")
            torch.save(converted_checkpoint, save_weights_path)
            print(f"Model weights saved at {save_weights_path}!")
        else:
            model = PhiForCausalLM(config).to(device)
            model.load_state_dict(converted_checkpoint, strict=True)
            save_model_path = os.path.join(pytorch_dump_folder_path, model_type)
            model.save_pretrained(save_model_path)
            print(f"Model saved at {save_model_path}!")
            del config, model
        del model_checkpoint, converted_checkpoint
        if use_cuda: torch.cuda.empty_cache()
        gc.collect()
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, help="Name of the model to convert. (Please enter one of the following: phi-1, phi-1_5, phi-2). If nothing is provided, all models will be converted.", default=None)
    parser.add_argument("--checkpoint_path", type=str, help="Path to the folder of downloaded checkpoints. (Please enter full path)")
    parser.add_argument("--pytorch_dump_folder_path", default=None, type=str, help="Path to the output PyTorch model. (Please enter full path)")
    parser.add_argument("--use_cuda", default=False, type=bool, help="Whether to load the weights on GPU during conversion or not, False by default")
    parser.add_argument("--save_weights_directly", default=True, type=bool, help="Whether to save the weights directly after conversion or load the weight to the Phi model and then save the Phi model along with weights. True by default")
    args = parser.parse_args()
    convert_phi_weights(args.model_name, args.checkpoint_path, args.pytorch_dump_folder_path, args.use_cuda, args.save_weights_directly, _MODELS)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
