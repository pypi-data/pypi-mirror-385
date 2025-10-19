"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import argparse
import json
import os
import torch
from sapiens_transformers import (MixtralConfig, MixtralForCausalLM)
def compute_intermediate_size(n, ffn_dim_multiplier=1, multiple_of=256): return multiple_of * ((int(ffn_dim_multiplier * int(8 * n / 3)) + multiple_of - 1) // multiple_of)
def read_json(path):
    with open(path, "r") as f: return json.load(f)
def write_json(text, path):
    with open(path, "w") as f: json.dump(text, f)
def write_model(model_path, input_base_path, model_size, safe_serialization=True):
    os.makedirs(model_path, exist_ok=True)
    params = read_json(os.path.join(input_base_path, "params.json"))
    num_shards = 1
    sliding_window = int(params["sliding_window"]) if "sliding_window" in params else None
    n_layers = params["num_hidden_layers"]
    n_heads = params["num_attention_heads"]
    n_heads_per_shard = n_heads // num_shards
    dim = params["hidden_size"]
    dims_per_head = dim // n_heads
    base = params.get("rope_theta", 10000.0)
    max_position_embeddings = 4096 * 8
    num_local_experts = params["num_local_experts"]
    ffn_dim = params["intermediate_size"]
    vocab_size = params["vocab_size"]
    if "num_key_value_heads" in params:
        num_key_value_heads = params["num_key_value_heads"]
        num_local_key_value_heads = num_key_value_heads // num_shards
        key_value_dim = dims_per_head * num_local_key_value_heads
    else:
        num_key_value_heads = n_heads
        num_local_key_value_heads = n_heads_per_shard
        key_value_dim = dim
    def permute(w, n_heads=n_heads, dim1=dim, dim2=dim): return w.view(n_heads, dim1 // n_heads // 2, 2, dim2).transpose(1, 2).reshape(dim1, dim2)
    print(f"Fetching all parameters from the checkpoint at {input_base_path}.")
    loaded = [torch.load(os.path.join(input_base_path, f"consolidated.{i:02d}.pt"), map_location="cpu") for i in range(8)]
    merged_state_dict = {}
    for state_dict in loaded: merged_state_dict.update(state_dict)
    state_dict = {}
    for layer_i in range(n_layers):
        state_dict.update({f"model.layers.{layer_i}.input_layernorm.weight": merged_state_dict[f"layers.{layer_i}.attention_norm.weight"].clone(), f"model.layers.{layer_i}.post_attention_layernorm.weight": merged_state_dict[f"layers.{layer_i}.ffn_norm.weight"].clone()})
        state_dict[f"model.layers.{layer_i}.self_attn.q_proj.weight"] = permute(merged_state_dict[f"layers.{layer_i}.attention.wq.weight"].view(n_heads_per_shard, dims_per_head, dim).reshape(dim, dim))
        state_dict[f"model.layers.{layer_i}.self_attn.k_proj.weight"] = permute(merged_state_dict[f"layers.{layer_i}.attention.wk.weight"].view(num_local_key_value_heads, dims_per_head, dim).reshape(key_value_dim, dim), num_key_value_heads, key_value_dim, dim)
        state_dict[f"model.layers.{layer_i}.self_attn.v_proj.weight"] = (merged_state_dict[f"layers.{layer_i}.attention.wv.weight"].view(num_local_key_value_heads, dims_per_head, dim).reshape(key_value_dim, dim))
        state_dict[f"model.layers.{layer_i}.self_attn.o_proj.weight"] = merged_state_dict[f"layers.{layer_i}.attention.wo.weight"]
        w1 = merged_state_dict[f"layers.{layer_i}.block_sparse_moe.w1"]
        w2 = merged_state_dict[f"layers.{layer_i}.block_sparse_moe.w2"]
        w3 = merged_state_dict[f"layers.{layer_i}.block_sparse_moe.w3"]
        experts_w1 = [w1[ffn_dim * expert_idx : ffn_dim * (expert_idx + 1), :].contiguous().clone() for expert_idx in range(num_local_experts)]
        for idx, expert_block in enumerate(experts_w1):
            expert_key = f"model.layers.{layer_i}.block_sparse_moe.experts.{idx}.w1"
            state_dict[expert_key + ".weight"] = expert_block.clone()
        experts_w2 = [w2[ffn_dim * expert_idx : ffn_dim * (expert_idx + 1), :].contiguous().clone() for expert_idx in range(num_local_experts)]
        for idx, expert_block in enumerate(experts_w2):
            expert_key = f"model.layers.{layer_i}.block_sparse_moe.experts.{idx}.w2"
            state_dict[expert_key + ".weight"] = expert_block.T.clone().contiguous()
        experts_w3 = [w3[ffn_dim * expert_idx : ffn_dim * (expert_idx + 1), :].contiguous().clone() for expert_idx in range(num_local_experts)]
        for idx, expert_block in enumerate(experts_w3):
            expert_key = f"model.layers.{layer_i}.block_sparse_moe.experts.{idx}.w3"
            state_dict[expert_key + ".weight"] = expert_block.clone()
        state_dict[f"model.layers.{layer_i}.block_sparse_moe.gate.weight"] = merged_state_dict[f"layers.{layer_i}.block_sparse_moe.gate.weight"]
    state_dict.update({"model.norm.weight": merged_state_dict["norm.weight"], "model.embed_tokens.weight": merged_state_dict["tok_embeddings.weight"], "lm_head.weight": merged_state_dict["output.weight"]})
    config = MixtralConfig(hidden_size=dim, intermediate_size=ffn_dim, num_attention_heads=params["num_attention_heads"], num_hidden_layers=params["num_hidden_layers"], rms_norm_eps=params["rms_norm_eps"],
    num_key_value_heads=num_key_value_heads, vocab_size=vocab_size, rope_theta=base, max_position_embeddings=max_position_embeddings, sliding_window=sliding_window, num_local_experts=num_local_experts)
    print("Loading the checkpoint in a Mixtral model.")
    with torch.device("meta"): model = MixtralForCausalLM(config)
    del model.config._name_or_path
    model.config.torch_dtype = torch.float16
    print("Saving in the Transformers format.")
    model.load_state_dict(state_dict, strict=True, assign=True)
    for n, p in model.named_parameters(): assert p.device.type != "meta", f"{n} has not been loaded!"
    model.save_pretrained(model_path, safe_serialization=safe_serialization)
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", help="Location of Mixtral weights, which contains tokenizer.model and model folders", required=True)
    parser.add_argument("--model_size", choices=["7B"], help="'f' models correspond to the finetuned versions, and are specific to the Mixtral official release. For more details on Mixtral, checkout the original repo: https://huggingface.co/mistral-ai", default="7B")
    parser.add_argument("--output_dir", help="Location to write HF model", required=True)
    parser.add_argument("--safe_serialization", type=bool, help="Whether or not to save using `safetensors`.")
    args = parser.parse_args()
    write_model(model_path=args.output_dir, input_base_path=args.input_dir, model_size=args.model_size, safe_serialization=args.safe_serialization)
if __name__ == "__main__": main()
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
