"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import argparse
import torch
from sapiens_transformers import LxmertConfig, LxmertForPreTraining, load_tf_weights_in_lxmert
from sapiens_transformers.utils import logging
logging.set_verbosity_info()
def convert_tf_checkpoint_to_pytorch(tf_checkpoint_path, config_file, pytorch_dump_path):
    config = LxmertConfig.from_json_file(config_file)
    print(f"Building PyTorch model from configuration: {config}")
    model = LxmertForPreTraining(config)
    load_tf_weights_in_lxmert(model, config, tf_checkpoint_path)
    print(f"Save PyTorch model to {pytorch_dump_path}")
    torch.save(model.state_dict(), pytorch_dump_path)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tf_checkpoint_path", default=None, type=str, required=True, help="Path to the TensorFlow checkpoint path.")
    parser.add_argument("--config_file", default=None, type=str, required=True, help="The config json file corresponding to the pre-trained model. \nThis specifies the model architecture.")
    parser.add_argument("--pytorch_dump_path", default=None, type=str, required=True, help="Path to the output PyTorch model.")
    args = parser.parse_args()
    convert_tf_checkpoint_to_pytorch(args.tf_checkpoint_path, args.config_file, args.pytorch_dump_path)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
