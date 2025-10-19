'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..utils import (is_sapiens_accelerator_available, is_sapiens_machine_available, is_flax_available, is_google_colab, is_peft_available, is_safetensors_available,
is_torch_available, is_transformers_available, is_xformers_available)
from .. import __version__ as version
from . import BaseDiffusersCLICommand
from argparse import ArgumentParser
import huggingface_hub
import subprocess
import platform
def info_command_factory(_): return EnvironmentCommand()
class EnvironmentCommand(BaseDiffusersCLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser) -> None:
        download_parser = parser.add_parser('env')
        download_parser.set_defaults(func=info_command_factory)
    def run(self) -> dict:
        hub_version = huggingface_hub.__version__
        safetensors_version = 'not installed'
        if is_safetensors_available():
            import safetensors
            safetensors_version = safetensors.__version__
        pt_version = 'not installed'
        pt_cuda_available = 'NA'
        if is_torch_available():
            import torch
            pt_version = torch.__version__
            pt_cuda_available = torch.cuda.is_available()
        flax_version = 'not installed'
        jax_version = 'not installed'
        jaxlib_version = 'not installed'
        jax_backend = 'NA'
        if is_flax_available():
            import flax
            import jax
            import jaxlib
            flax_version = flax.__version__
            jax_version = jax.__version__
            jaxlib_version = jaxlib.__version__
            jax_backend = jax.lib.xla_bridge.get_backend().platform
        sapiens_transformers_version = 'not installed'
        if is_transformers_available():
            import sapiens_transformers
            sapiens_transformers_version = sapiens_transformers.__version__
        sapiens_accelerator_version = 'not installed'
        if is_sapiens_accelerator_available():
            import sapiens_accelerator
            sapiens_accelerator_version = sapiens_accelerator.__version__
        peft_version = 'not installed'
        if is_peft_available():
            import peft
            peft_version = peft.__version__
        sapiens_machine_version = 'not installed'
        if is_sapiens_machine_available():
            import sapiens_machine
            sapiens_machine_version = sapiens_machine.__version__
        xformers_version = 'not installed'
        if is_xformers_available():
            import xformers
            xformers_version = xformers.__version__
        platform_info = platform.platform()
        is_google_colab_str = 'Yes' if is_google_colab() else 'No'
        accelerator = 'NA'
        if platform.system() in {'Linux', 'Windows'}:
            try:
                sp = subprocess.Popen(['nvidia-smi', '--query-gpu=gpu_name,memory.total', '--format=csv,noheader'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out_str, _ = sp.communicate()
                out_str = out_str.decode('utf-8')
                if len(out_str) > 0: accelerator = out_str.strip()
            except FileNotFoundError: pass
        elif platform.system() == 'Darwin':
            try:
                sp = subprocess.Popen(['system_profiler', 'SPDisplaysDataType'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out_str, _ = sp.communicate()
                out_str = out_str.decode('utf-8')
                start = out_str.find('Chipset Model:')
                if start != -1:
                    start += len('Chipset Model:')
                    end = out_str.find('\n', start)
                    accelerator = out_str[start:end].strip()
                    start = out_str.find('VRAM (Total):')
                    if start != -1:
                        start += len('VRAM (Total):')
                        end = out_str.find('\n', start)
                        accelerator += ' VRAM: ' + out_str[start:end].strip()
            except FileNotFoundError:
                pass
        info = {'HF Diffusers version': version, 'Platform': platform_info, 'Running on Google Colab?': is_google_colab_str, 'Python version': platform.python_version(),
        'PyTorch version (GPU?)': f'{pt_version} ({pt_cuda_available})', 'Flax version (CPU?/GPU?/TPU?)': f'{flax_version} ({jax_backend})', 'Jax version': jax_version,
        'JaxLib version': jaxlib_version, 'Huggingface_hub version': hub_version, 'Sapiens Transformers version': sapiens_transformers_version, 'SapiensAccelerator version': sapiens_accelerator_version,
        'PEFT version': peft_version, 'Sapiens_machine version': sapiens_machine_version, 'Safetensors version': safetensors_version, 'xFormers version': xformers_version,
        'Accelerator': accelerator, 'Using GPU in script?': '<fill in>', 'Using distributed or parallel set-up in script?': '<fill in>'}
        return info
    @staticmethod
    def format_dict(d: dict) -> str: return '\n'.join([f'- {prop}: {val}' for prop, val in d.items()]) + '\n'
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
