"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import argparse
import os
import pickle as pkl
import torch
from torch import nn
from sapiens_transformers import AutoTokenizer, MegaConfig, MegaForMaskedLM
try:
    from fairseq.modules.mega_layer import MegaEncoderLayer
except ImportError: raise ImportError("You need to install the version of fairseq from the Mega repo!")
class MegaLM(nn.Module):
    def __init__(self, mega_args, depth, vocab_size):
        super().__init__()
        self.mega_args = mega_args
        self.embedding_layer = nn.Embedding(vocab_size, self.mega_args.encoder_embed_dim)
        self.encoders = nn.ModuleList([MegaEncoderLayer(self.mega_args) for _ in range(depth)])
        self.depth = depth
    def forward(self, input_ids, attention_mask, batch_first=True, ignore_mask_value=0):
        if batch_first: input_ids = input_ids.T
        if ignore_mask_value == 0: attention_mask = 1 - attention_mask
        embeds = self.embedding_layer(input_ids)
        for encoder in self.encoders: embeds = encoder(embeds, attention_mask)
        if batch_first: return torch.transpose(embeds, 0, 1)
        else: return embeds
class OriginalMegaForMaskedLM(nn.Module):
    def __init__(self, mega_args, depth, vocab_size):
        super().__init__()
        self.mega = MegaLM(mega_args, depth, vocab_size)
        self.mlm_head = nn.Linear(mega_args.encoder_embed_dim, vocab_size)
        self.dropout = nn.Dropout(p=0.1)
    def forward(self, input_ids, attention_mask, batch_first=True, ignore_mask_value=0):
        encoder_output = self.mega(input_ids, attention_mask, batch_first, ignore_mask_value)
        return self.mlm_head(self.dropout(encoder_output))
def convert_checkpoint_to_huggingface(pretrained_checkpoint_path, output_path, includes_tokenizer):
    with open(os.path.join(pretrained_checkpoint_path, "model_args.pkl"), "rb") as f: mega_original_args = pkl.load(f)
    original_mlm = OriginalMegaForMaskedLM(**mega_original_args).eval()
    print("Original Mega encoder:", original_mlm.mega.load_state_dict(torch.load(os.path.join(pretrained_checkpoint_path, "encoder_weights.pt"), map_location="cpu")))
    print("Original Mega MLM layer:", original_mlm.mlm_head.load_state_dict(torch.load(os.path.join(pretrained_checkpoint_path, "mlm_head_weights.pt"), map_location="cpu")))
    hf_config = MegaConfig(num_hidden_layers=mega_original_args["depth"], vocab_size=mega_original_args["vocab_size"], hidden_size=mega_original_args["mega_args"].encoder_embed_dim,
    shared_representation_size=mega_original_args["mega_args"].encoder_z_dim, intermediate_size=mega_original_args["mega_args"].encoder_hidden_dim, ema_projection_size=mega_original_args["mega_args"].encoder_n_dim,
    dropout_prob=mega_original_args["mega_args"].dropout, attention_probs_dropout_prob=mega_original_args["mega_args"].attention_dropout, hidden_dropout_prob=mega_original_args["mega_args"].hidden_dropout,
    activation=mega_original_args["mega_args"].activation_fn, attention_activation=mega_original_args["mega_args"].attention_activation_fn, bidirectional=mega_original_args["mega_args"].bidirectional,
    use_chunking=mega_original_args["mega_args"].encoder_chunk_size > 0, chunk_size=mega_original_args["mega_args"].encoder_chunk_size, truncation=mega_original_args["mega_args"].truncation_length,
    normalization_type=mega_original_args["mega_args"].normalization_type, normalize_before_mega=True, norm_affine=True, use_feature_dropout=mega_original_args["mega_args"].feature_dropout,
    relative_positional_bias=mega_original_args["mega_args"].rel_pos_bias, max_positions=mega_original_args["mega_args"].max_source_positions, nffn_hidden_size=mega_original_args["mega_args"].encoder_ffn_embed_dim,
    normalize_before_ffn=mega_original_args["mega_args"].normalize_before, nffn_activation_dropout_prob=0.0, add_token_type_embeddings=False, add_lm_hidden_dense_layer=False)
    hf_mlm = MegaForMaskedLM(hf_config).eval()
    hf_mlm.mega.embedding_layer.word_embeddings.weight = original_mlm.mega.embedding_layer.weight
    original_state_dict = original_mlm.mega.encoders.state_dict()
    updated_keys = {}
    for module_name in original_state_dict.keys():
        new_module_name = None
        if "beta" in module_name:
            if "move.beta" in module_name: new_module_name = module_name.replace("move.beta", "ema_gate.ema_expansion_matrix")
            elif "mega_layer.beta" in module_name: new_module_name = module_name.replace("beta", "qk_bias")
            else: new_module_name = module_name.replace("beta", "b_param")
        elif "gamma" in module_name:
            if "move.gamma" in module_name: new_module_name = module_name.replace("move.gamma", "ema_gate.kernel_projection_matrix")
            elif "mega_layer.gamma" in module_name: new_module_name = module_name.replace("gamma", "qk_weight")
            else: new_module_name = module_name.replace("gamma", "g_param")
        elif "move.alpha" in module_name: new_module_name = module_name.replace("move.alpha", "ema_gate.decay_factor")
        elif "move.delta" in module_name: new_module_name = module_name.replace("move.delta", "ema_gate.damping_factor")
        elif "omega" in module_name: new_module_name = module_name.replace("move.omega", "ema_gate.residual_weight")
        if new_module_name: updated_keys[module_name] = new_module_name
    if len(updated_keys) != 0: print(f"Renaming these keys: {updated_keys.keys()}")
    else: print("No need to rename state dict entries")
    for old, new in updated_keys.items(): original_state_dict[new] = original_state_dict.pop(old)
    print("HF Mega encoder:", hf_mlm.mega.layers.load_state_dict(original_state_dict))
    print("HF Mega MLM layer:", hf_mlm.mlm_head.load_state_dict(torch.load(os.path.join(pretrained_checkpoint_path, "mlm_head_weights.pt"), map_location="cpu")))
    input_ids = torch.randint(0, hf_config.vocab_size, size=(4, 256))
    input_mask = torch.ones_like(input_ids)
    input_mask[:, -10:] = 0
    original_output = original_mlm(input_ids, input_mask, batch_first=True, ignore_mask_value=0)
    hf_output = hf_mlm(input_ids, input_mask)[0]
    print(f"original output {original_output.shape}")
    print(f"hf output {hf_output.shape}")
    print(f"max diff: {(original_output - hf_output).max()}")
    success = torch.allclose(original_output, hf_output, atol=1e-3)
    if success:
        print("Yay!")
        hf_mlm.save_pretrained(output_path)
    else: raise RuntimeError(f"Something's broken :(\nOriginal:\n{original_output}\n\nHF\n{hf_output}\n{hf_mlm}")
    if includes_tokenizer:
        print("Transferring tokenizer")
        tokenizer = AutoTokenizer.from_pretrained(pretrained_checkpoint_path)
        tokenizer.save_pretrained(output_path)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pretrained_checkpoint_path", default=None, type=str, required=True, help="Point to the directory containing your model weights using the official Mega repo")
    parser.add_argument("--output_path", default=None, type=str, required=True, help="Location to save the Sapiens version")
    parser.add_argument("--includes_tokenizer", action="store_true", help="Use this flag if there is a Sapiens tokenizer in the original checkpoint repo")
    args = parser.parse_args()
    convert_checkpoint_to_huggingface(args.pretrained_checkpoint_path, args.output_path, args.includes_tokenizer)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
