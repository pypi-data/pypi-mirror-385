"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from os import path as sapiens_model_path, remove as sapiens_model_remove
class SapiensModel():
    def __init__(self, model_path='', hur_context_size=None, show_errors=False):
        try:
            model_path = model_path.strip() if type(model_path) == str else str(model_path).strip()
            self.__hur_context_size = max((128, int(hur_context_size))) if type(hur_context_size) in (bool, int, float) else None
            self.__show_errors = bool(show_errors) if type(show_errors) in (bool, int, float) else False
            self.CONTEXT_SIZE, self.ARCHITECTURE = self.__hur_context_size if self.__hur_context_size else 512, 'sapiens'
            original_model_path = model_path
            from os import environ, walk, path, listdir
            from torch import cuda, device, backends
            from tqdm import tqdm
            from functools import partialmethod
            from sapiens_transformers.adaptations import (HURLM_COMPATIBILITY, SAPI_ZERO_COMPATIBILITY, SASTRAL_COMPATIBILITY, MODULAR_ENTITY_COMPATIBILITY, SAPIENS_VISION_COMPATIBILITY,
            SAPI_IMAGE_COMPATIBILITY, SAPIENS_IMAGEGEN_COMPATIBILITY, SAPI_IMAGEGEN_COMPATIBILITY, SAPI_PHOTOGEN_COMPATIBILITY, SAPI_AUDIO_COMPATIBILITY, SAPI_AUDIOGEN_COMPATIBILITY,
            SAPI_MUSICGEN_COMPATIBILITY, SAPI_VIDEO_COMPATIBILITY, SAPIENS_VIDEOGEN_COMPATIBILITY, SAPI_VIDEOGEN_COMPATIBILITY, ALLEGRO_COMPATIBILITY, SAPI_VIDEOGEN_POSSIBILITIES, NAME065, NAME066)
            try:
                from transformers import logging as sapiens_model_logging
                sapiens_model_logging.set_verbosity_error()
            except: pass
            environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'], self.__path = '0.0', path
            if cuda.is_available(): local_device = device('cuda')
            elif backends.mps.is_available(): local_device = device('mps')
            else: local_device = device('cpu')
            model, self.__tokenizer, self.__eos_token_id, self.__processor, self.__sapiens = None, None, 1, None, None
            self.__ARCHITECTURE, self.__sapiens_precision, self.__sapiens_vision_processor = None, None, None
            self.__images, self.__audios, self.__videos = [], [], []
            self.__maximum_image_pixels, self.__maximum_video_pixels = 500, 100
            self.__export_to_video, self.__model_path, self.__downloaded, self.__local_device = None, None, False, local_device
            if model_path and not path.exists(model_path):
                from sapiens_transformers.utils.functions import is_default_model
                if is_default_model(model_path=model_path):
                    from sapiens_transformers.download import DownloadHF
                    DownloadHF(model_path=model_path).snapshot_download()
                    if model_path.startswith('/'): model_path = '.'+model_path
            tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)
            def set_architecture(architecture='sapiens'):
                if architecture in HURLM_COMPATIBILITY: self.__ARCHITECTURE = HURLM_COMPATIBILITY[0]
                elif architecture in SAPI_ZERO_COMPATIBILITY: self.__ARCHITECTURE = SAPI_ZERO_COMPATIBILITY[0]
                elif architecture in SASTRAL_COMPATIBILITY: self.__ARCHITECTURE = SASTRAL_COMPATIBILITY[0]
                elif architecture in MODULAR_ENTITY_COMPATIBILITY: self.__ARCHITECTURE = MODULAR_ENTITY_COMPATIBILITY[0]
                elif architecture in SAPIENS_VISION_COMPATIBILITY: self.__ARCHITECTURE = SAPIENS_VISION_COMPATIBILITY[0]
                elif architecture in SAPI_IMAGE_COMPATIBILITY: self.__ARCHITECTURE = SAPI_IMAGE_COMPATIBILITY[0]
                elif architecture in SAPIENS_IMAGEGEN_COMPATIBILITY: self.__ARCHITECTURE = SAPIENS_IMAGEGEN_COMPATIBILITY[0]
                elif architecture in SAPI_IMAGEGEN_COMPATIBILITY: self.__ARCHITECTURE = SAPI_IMAGEGEN_COMPATIBILITY[0]
                elif architecture in SAPI_PHOTOGEN_COMPATIBILITY: self.__ARCHITECTURE = SAPI_PHOTOGEN_COMPATIBILITY[0]
                elif architecture in SAPI_AUDIO_COMPATIBILITY: self.__ARCHITECTURE = SAPI_AUDIO_COMPATIBILITY[0]
                elif architecture in SAPI_AUDIOGEN_COMPATIBILITY: self.__ARCHITECTURE = SAPI_AUDIOGEN_COMPATIBILITY[0]
                elif architecture in SAPI_MUSICGEN_COMPATIBILITY: self.__ARCHITECTURE = SAPI_MUSICGEN_COMPATIBILITY[0]
                elif architecture in SAPI_VIDEO_COMPATIBILITY: self.__ARCHITECTURE = SAPI_VIDEO_COMPATIBILITY[0]
                elif architecture in SAPIENS_VIDEOGEN_COMPATIBILITY: self.__ARCHITECTURE = SAPIENS_VIDEOGEN_COMPATIBILITY[0]
                elif architecture in SAPI_VIDEOGEN_COMPATIBILITY: self.__ARCHITECTURE = SAPI_VIDEOGEN_COMPATIBILITY[0]
                else: self.__ARCHITECTURE = architecture
            saf_model_conversion = bin_model_conversion = False
            from sapiens_transformers.adaptations import STATE1X, STATE1Y, STATE2X, STATE2Y
            from traceback import print_exc
            try:
                self.__model_path, hur_path = model_path, ''
                def get_hur_model(model_path=''):
                    for file in listdir(model_path):
                        if file.endswith('.safetensors') or file.endswith('.ben') or file.endswith('.json'): return model_path
                    for file in listdir(model_path):
                        if file.endswith('.hur'): return path.join(model_path, file)
                    return ''
                def hur_model_load(model_path=''):
                    from sapiens_transformers.sapiens_optimizer import Sapiens
                    if not self.__hur_context_size:
                        sapiens = Sapiens(model_path=model_path, n_ctx=32, verbose=False)
                        self.__hur_context_size = int(next((value for key, value in sapiens.metadata.items() if 'context_length' in key), None))
                    sapiens = Sapiens(model_path=model_path, n_ctx=self.__hur_context_size if type(self.__hur_context_size) == int else 1010000, verbose=False)
                    context_size = int(next((value for key, value in sapiens.metadata.items() if 'context_length' in key), 512))
                    architecture = str(next((value for key, value in sapiens.metadata.items() if 'architecture' in key), 'sapiens')).lower().strip()
                    set_architecture(architecture=architecture)
                    sapiens._n_ctx = context_size
                    sapiens._n_ctx_per_seq = context_size
                    self.__sapiens = sapiens
                    self.CONTEXT_SIZE, self.ARCHITECTURE = context_size, 'hur'
                if model_path and path.isdir(model_path):
                    hur_path = get_hur_model(model_path=model_path)
                    if hur_path and hur_path.endswith('.hur'): hur_model_load(model_path=hur_path)
                    else: hur_path = ''
                if not hur_path and model_path and path.isdir(model_path):
                    from sapiens_transformers.utils.functions import model_conversion, find_config_or_model_index, get_configuration_path, get_dictionary_from_json, search_model_type
                    saf_model_conversion = model_conversion(sapiens_path=original_model_path, to=STATE1X)
                    if not saf_model_conversion: bin_model_conversion = model_conversion(sapiens_path=original_model_path, to=STATE2X)
                    model_path = find_config_or_model_index(model_path=model_path)
                    configuration_path, configuration_json, architecture = get_configuration_path(model_path=model_path), {}, ''
                    if path.isfile(configuration_path): configuration_json = get_dictionary_from_json(configuration_path=configuration_path)
                    self.ARCHITECTURE = architecture = search_model_type(data=configuration_json)
                    set_architecture(architecture=architecture)
                    ARCHITECTURE = self.__ARCHITECTURE
                    sapiens_model, sapiens_processor, sapiens_tokenizer, vae = None, None, None, None
                    from sapiens_transformers.adaptations import SAPIENS_PRECISION1, SAPIENS_PRECISION2, SAPIENS_PRECISION3, SAPIENS_PRECISIONX
                    torch_dtype_x, torch_dtype_y = SAPIENS_PRECISION1, SAPIENS_PRECISIONX
                    _attn_implementation = 'flash_attention_2' if local_device == 'cuda' else 'eager'
                    if ARCHITECTURE == HURLM_COMPATIBILITY[0]:
                        from sapiens_transformers.adaptations import HurLMAutoProcessor as sapiens_processor, AutoModelForHurLM as sapiens_model
                        torch_dtype_x, torch_dtype_y = SAPIENS_PRECISION1, SAPIENS_PRECISIONX
                    elif ARCHITECTURE == MODULAR_ENTITY_COMPATIBILITY[0]:
                        from sapiens_transformers.adaptations import ModularEntityForConditionalGeneration as sapiens_model
                        from sapiens_transformers import AutoProcessor as sapiens_processor
                        torch_dtype_x, torch_dtype_y = SAPIENS_PRECISION1, SAPIENS_PRECISIONX
                    elif ARCHITECTURE == SAPIENS_VISION_COMPATIBILITY[0]:
                        from sapiens_transformers import SapiensVisionForConditionalGeneration as sapiens_model, AutoProcessor as sapiens_processor
                        from sapiens_transformers.adaptations import sapiens_vision_processor
                        torch_dtype_x, torch_dtype_y = SAPIENS_PRECISIONX, SAPIENS_PRECISION2
                        self.__sapiens_vision_processor = sapiens_vision_processor
                    elif ARCHITECTURE == SAPI_IMAGE_COMPATIBILITY[0]:
                        from sapiens_transformers import SAPIImageForConditionalGeneration as sapiens_model, SAPIImageProcessor as sapiens_processor
                        torch_dtype_x, torch_dtype_y = SAPIENS_PRECISION2, SAPIENS_PRECISIONX
                    elif ARCHITECTURE == SAPIENS_IMAGEGEN_COMPATIBILITY[0]:
                        from sapiens_transformers.diffusers import SapiensImageGenPipeline as sapiens_model
                        torch_dtype_x, torch_dtype_y = SAPIENS_PRECISION1, SAPIENS_PRECISIONX
                    elif ARCHITECTURE == SAPI_IMAGEGEN_COMPATIBILITY[0]:
                        from sapiens_transformers.diffusers import SAPIImageGenPipeline as sapiens_model
                        torch_dtype_x, torch_dtype_y = SAPIENS_PRECISION1, SAPIENS_PRECISIONX
                    elif ARCHITECTURE == SAPI_PHOTOGEN_COMPATIBILITY[0]:
                        from sapiens_transformers.adaptations import SapiensImageGenerator as sapiens_model
                        torch_dtype_x, torch_dtype_y = SAPIENS_PRECISION1, SAPIENS_PRECISIONX
                    elif ARCHITECTURE == SAPI_AUDIO_COMPATIBILITY[0]: from sapiens_transformers import SAPIAudioForConditionalGeneration as sapiens_model, SAPIAudioProcessor as sapiens_processor
                    elif ARCHITECTURE == SAPI_AUDIOGEN_COMPATIBILITY[0]: from sapiens_transformers.adaptations import SAPIAudioGen as sapiens_model
                    elif ARCHITECTURE == SAPI_MUSICGEN_COMPATIBILITY[0]: from sapiens_transformers.adaptations import SAPIMusicAutoProcessor as sapiens_processor, SAPIMusicForConditionalGeneration as sapiens_model
                    elif ARCHITECTURE == SAPI_VIDEO_COMPATIBILITY[0]:
                        from sapiens_transformers.adaptations import SAPIVideoForConditionalGeneration as sapiens_model, SAPIVideoProcessor as sapiens_processor
                        torch_dtype_x, torch_dtype_y = SAPIENS_PRECISION2, SAPIENS_PRECISIONX
                        self.__sapiens_precision = SAPIENS_PRECISION2
                    elif ARCHITECTURE == SAPIENS_VIDEOGEN_COMPATIBILITY[0]:
                        from sapiens_transformers.diffusers import SapiensVideoGenPipeline as sapiens_model
                        torch_dtype_x, torch_dtype_y = SAPIENS_PRECISION1, SAPIENS_PRECISIONX
                        from sapiens_transformers.diffusers.utils import export_to_video
                        self.__export_to_video, self.__model_path, self.__sapiens_precision = export_to_video, model_path, SAPIENS_PRECISION1
                    elif ARCHITECTURE == SAPI_VIDEOGEN_COMPATIBILITY[0]:
                        def find_safetensors_file(original_model_path=''):
                            animatediff_files, safetensors_files = [], []
                            def is_sapi_videogen(file=''):
                                for possible in SAPI_VIDEOGEN_POSSIBILITIES:
                                    if possible in path.basename(file).lower(): return True
                                return False
                            for file in listdir(original_model_path):
                                if is_sapi_videogen(file=file) and file.lower().strip().endswith('.safetensors'): return path.join(original_model_path, file)
                            for root, _, files in walk(original_model_path):
                                for file in files:
                                    if is_sapi_videogen(file=file) and file.lower().strip().endswith('.safetensors'): animatediff_files.append(path.join(root, file))
                            if animatediff_files: return animatediff_files[0]
                            for file in listdir(original_model_path):
                                if file.lower().strip().endswith('.safetensors'): return path.join(original_model_path, file)
                            for root, _, files in walk(original_model_path):
                                for file in files:
                                    if file.lower().strip().endswith('.safetensors'): safetensors_files.append(path.join(root, file))
                            if safetensors_files: return safetensors_files[0]
                            return original_model_path
                        def first_subdirectory(folder_path=''):
                            for entry in listdir(folder_path):
                                full_path = path.join(folder_path, entry)
                                if path.isdir(full_path): return full_path
                            return folder_path
                        model_path = first_subdirectory(folder_path=model_path)
                        safetensors_path, self.__model_path = find_safetensors_file(original_model_path=original_model_path), model_path
                        from logging import getLogger, ERROR
                        getLogger('moviepy').setLevel(ERROR)
                        from os import devnull
                        with open(devnull, 'w') as _devnull:
                            from contextlib import redirect_stdout
                            with redirect_stdout(_devnull):
                                from sapiens_transformers.adaptations import SapiensMotionAdapter, SapiensEulerDiscreteScheduler
                                try: adapter = SapiensMotionAdapter().to(local_device, SAPIENS_PRECISION2)
                                except: adapter = SapiensMotionAdapter().to(local_device, SAPIENS_PRECISIONX)
                                from safetensors.torch import load_file
                                try: adapter_state_dictionary = load_file(safetensors_path, device=local_device)
                                except: adapter_state_dictionary = load_file(safetensors_path, device='cpu')
                                adapter.load_state_dict(adapter_state_dictionary)
                                from sapiens_transformers.diffusers import SAPIVideoGenPipeline as sapiens_model
                                torch_dtype_x, torch_dtype_y = SAPIENS_PRECISION2, SAPIENS_PRECISIONX
                                try: model = sapiens_model.from_pretrained(model_path, motion_adapter=adapter, torch_dtype=torch_dtype_x, verbose=False).to(local_device)
                                except: model = sapiens_model.from_pretrained(model_path, motion_adapter=adapter, torch_dtype=torch_dtype_y, verbose=False).to(local_device)
                                model.scheduler = SapiensEulerDiscreteScheduler.from_config(model.scheduler.config, timestep_spacing='trailing', beta_schedule='linear')
                    elif ARCHITECTURE == ALLEGRO_COMPATIBILITY:
                        from sapiens_transformers.diffusers import AutoencoderKLAllegro, AllegroPipeline as sapiens_model
                        torch_dtype_x, torch_dtype_y = SAPIENS_PRECISION3, SAPIENS_PRECISIONX
                        from sapiens_transformers.diffusers.utils import export_to_video
                        try: vae = AutoencoderKLAllegro.from_pretrained(model_path, subfolder='vae', torch_dtype=torch_dtype_x).to(local_device)
                        except: vae = AutoencoderKLAllegro.from_pretrained(model_path, subfolder='vae', torch_dtype=torch_dtype_y).to(local_device)
                        torch_dtype_x, torch_dtype_y = SAPIENS_PRECISION1, SAPIENS_PRECISIONX
                        self.__export_to_video = export_to_video
                    else:
                        from sapiens_transformers import AutoModelForCausalLM as sapiens_model, AutoTokenizer as sapiens_tokenizer
                        torch_dtype_x, torch_dtype_y = SAPIENS_PRECISIONX, SAPIENS_PRECISION1
                    if ARCHITECTURE == HURLM_COMPATIBILITY[0]:
                        try: model = sapiens_model.from_pretrained(model_path, torch_dtype=torch_dtype_x, low_cpu_mem_usage=True, _attn_implementation=_attn_implementation).to(local_device)
                        except: model = sapiens_model.from_pretrained(model_path, torch_dtype=torch_dtype_y, low_cpu_mem_usage=True, _attn_implementation=_attn_implementation).to(local_device)
                    elif ARCHITECTURE == SAPI_AUDIO_COMPATIBILITY[0]:
                        try: model = sapiens_model.from_pretrained(model_path, low_cpu_mem_usage=True, return_dict_in_generate=True).to(local_device)
                        except: model = sapiens_model.from_pretrained(model_path, low_cpu_mem_usage=True, return_dict_in_generate=True).to(local_device)
                        model.config.forced_decoder_ids = None
                    elif ARCHITECTURE == SAPI_AUDIOGEN_COMPATIBILITY[0]: model = sapiens_model(model_path=model_path, local_device=local_device, progress_bar=False)
                    elif ARCHITECTURE == SAPI_MUSICGEN_COMPATIBILITY[0]:
                        try: model = sapiens_model.from_pretrained(model_path, low_cpu_mem_usage=True, _attn_implementation=_attn_implementation).to(local_device)
                        except: model = sapiens_model.from_pretrained(model_path, low_cpu_mem_usage=True, _attn_implementation=_attn_implementation).to(local_device)
                    elif ARCHITECTURE == SAPIENS_VIDEOGEN_COMPATIBILITY[0]:
                        try: model = sapiens_model.from_pretrained(model_path, torch_dtype=torch_dtype_x, low_cpu_mem_usage=True, verbose=False).to(local_device)
                        except: model = sapiens_model.from_pretrained(model_path, torch_dtype=torch_dtype_y, low_cpu_mem_usage=True, verbose=False).to(local_device)
                    elif ARCHITECTURE == ALLEGRO_COMPATIBILITY:
                        try: model = sapiens_model.from_pretrained(model_path, vae=vae, torch_dtype=torch_dtype_x).to(local_device)
                        except: model = sapiens_model.from_pretrained(model_path, vae=vae, torch_dtype=torch_dtype_y).to(local_device)
                        model.vae.enable_tiling()
                    elif ARCHITECTURE in (MODULAR_ENTITY_COMPATIBILITY[0], SAPIENS_VISION_COMPATIBILITY[0], SAPI_IMAGE_COMPATIBILITY[0], SAPIENS_IMAGEGEN_COMPATIBILITY[0], SAPI_IMAGEGEN_COMPATIBILITY[0], SAPI_PHOTOGEN_COMPATIBILITY[0], SAPI_VIDEO_COMPATIBILITY[0]):
                        try: model = sapiens_model.from_pretrained(model_path, torch_dtype=torch_dtype_x, low_cpu_mem_usage=True).to(local_device)
                        except: model = sapiens_model.from_pretrained(model_path, torch_dtype=torch_dtype_y, low_cpu_mem_usage=True).to(local_device)
                    elif ARCHITECTURE != SAPI_VIDEOGEN_COMPATIBILITY[0]:
                        try: model = sapiens_model.from_pretrained(model_path, torch_dtype=torch_dtype_x, trust_remote_code=True).to(local_device)
                        except: model = sapiens_model.from_pretrained(model_path, torch_dtype=torch_dtype_y, trust_remote_code=True).to(local_device)
                        self.__tokenizer = sapiens_tokenizer.from_pretrained(model_path)
                        try: self.__eos_token_id = self.__tokenizer.eos_token_id
                        except: self.__eos_token_id = 1
                        architecture = str(model.config.model_type).lower().strip()
                        set_architecture(architecture=architecture)
                    if ARCHITECTURE == MODULAR_ENTITY_COMPATIBILITY[0] and hasattr(model, 'tie_weights'): model.tie_weights()
                    if ARCHITECTURE in (HURLM_COMPATIBILITY[0], MODULAR_ENTITY_COMPATIBILITY[0], SAPIENS_VISION_COMPATIBILITY[0], SAPI_IMAGE_COMPATIBILITY[0], SAPI_AUDIO_COMPATIBILITY[0], SAPI_MUSICGEN_COMPATIBILITY[0], SAPI_VIDEO_COMPATIBILITY[0]): self.__processor = sapiens_processor.from_pretrained(model_path)
                    if ARCHITECTURE == SAPI_AUDIO_COMPATIBILITY[0] and model.config.pad_token_id == model.config.eos_token_id: model.config.pad_token_id = self.__processor.tokenizer.pad_token_id
                    if saf_model_conversion: model_conversion(sapiens_path=original_model_path, to=STATE1Y)
                    elif bin_model_conversion: model_conversion(sapiens_path=original_model_path, to=STATE2Y)
                elif not hur_path and model_path and path.isfile(model_path): hur_model_load(model_path=model_path)
                elif not hur_path and original_model_path:
                    print('Non-existent path: '+model_path)
                    print('The path to the referenced model does not exist.')
            except Exception as error:
                if self.__show_errors: print('ERROR 1 in SapiensModel.__init__: '+str(error))
                if saf_model_conversion: model_conversion(sapiens_path=original_model_path, to=STATE1Y)
                elif bin_model_conversion: model_conversion(sapiens_path=original_model_path, to=STATE2Y)
            self.__system, self.__model, self.__max_new_tokens, self.__original_model_path, self.__image_paths, self.__output_image = NAME065, model, 512, original_model_path, [], ''
            architecture_string = str(self.ARCHITECTURE).lower().strip()
            if architecture_string != 'hur':
                try: self.CONTEXT_SIZE = self.__model.config.max_position_embeddings
                except:
                    try: self.CONTEXT_SIZE = self.__model.config.text_config.max_position_embeddings
                    except: self.CONTEXT_SIZE = 512
            self.MGT_STRING = NAME066
        except Exception as error:
            if self.__show_errors: print('ERROR 2 in SapiensModel.__init__: '+str(error))
    def __del__(self):
        if self.__output_image:
            if sapiens_model_path.exists(self.__output_image): sapiens_model_remove(self.__output_image)
    def __check_template(self, text=''):
        text = text.strip() if type(text) == str else str(text).strip()
        if any(substring in text for substring in ['user:', 'Human:', 'user\n', 'User:']): return True
        if '<|' in text and '|>' in text: return True
        if '[INST]' in text and '[/INST]' in text: return True
        return False
    def __get_encoding(self):
        from tiktoken import get_encoding as _get_encoding
        return _get_encoding('cl100k_base')
    def __get_total_tokens(self, text=''): return len(self.__get_encoding().encode(str(text)))       
    def __get_maximum_new_tokens(self, maximum_length=512, input_length=512, maximum_new_tokens=512):
        length_limit = maximum_length - input_length
        if maximum_new_tokens is None: maximum_new_tokens = length_limit
        else: maximum_new_tokens = min(maximum_new_tokens, length_limit)
        return max(256, maximum_new_tokens)
    def __extract_system_subtext(self, text=''):
        text = text.strip() if type(text) == str else str(text).strip()
        from re import DOTALL, findall
        patterns = [(r'System:(.*?)\n', DOTALL), (r'system<\|end_header_id\|>(.*?)<\|eot_id\|>', DOTALL), (r'<\|system\|>(.*?)<\|end\|>', DOTALL),
        (r'<\|im_start\|>system(.*?)<\|im_end\|>', DOTALL), (r'system:(.*?)\n', DOTALL), (r'<\|system\|>(.*?)<\|system\|>', DOTALL), (r'<\|system\|>(.*?)<\|end_of_system\|>', DOTALL)]
        for pattern, flags in patterns:
            matches = findall(pattern, text, flags)
            if matches: return matches[0].strip()
        return ''
    def __extract_user_subtext(self, text=''):
        text = text.strip() if type(text) == str else str(text).strip()
        if '<|image|><|begin_of_text|>' in text: return text.split('<|image|><|begin_of_text|>')[-1]
        from re import DOTALL, findall
        patterns = [(r'<\|start_header_id\|>user<\|end_header_id\|>(.*?)<\|eot_id\|>', DOTALL), (r'\[INST\](.*?)\[/INST\]', DOTALL),
        (r'<start_of_turn>user(.*?)<end_of_turn>', DOTALL), (r'<\|user\|>(.*?)<\|end\|>', DOTALL), (r'<\|im_start\|>user(.*?)<\|im_end\|>', DOTALL),
        (r'User:(.*?)Assistant:', DOTALL), (r'User:(.*?)Falcon:', DOTALL), (r'user:(.*?)\n', DOTALL), (r'<\|prompt\|>(.*?)<\|prompt\|>', DOTALL)]
        for pattern, flags in patterns:
            matches = findall(pattern, text, flags)
            if matches: return matches[-1].strip()
        return text
    def __divide_text_in_parts(self, prompt='', tokens_limit=500):
        from math import floor
        encoding = self.__get_encoding()
        tokens = encoding.encode(prompt)
        total_tokens = len(tokens)
        parties_limit = floor(tokens_limit / 3)
        part_size = floor(total_tokens / 3)
        parts = []
        for index in range(3):
            start_index = index * part_size
            end_index = start_index + part_size if index < 2 else total_tokens
            part_tokens = tokens[start_index:end_index]
            if len(part_tokens) > parties_limit: part_tokens = part_tokens[:parties_limit]
            part_text = encoding.decode(part_tokens)
            parts.append(part_text)
        final_text = ' '.join(parts)
        return final_text
    def __truncate_text(self, text='', tokens_limit=500):
        encoding = self.__get_encoding()
        tokens = encoding.encode(text)
        if len(tokens) <= tokens_limit: return text
        truncated_tokens = tokens[:tokens_limit]
        truncated_text = encoding.decode(truncated_tokens)
        last_valid_index = max(truncated_text.rfind(char) for char in ['.', '?', '!', ';'])
        if last_valid_index != -1: return truncated_text[:last_valid_index + 1]
        return truncated_text
    def __format_output(self, text=''):
        from re import compile, IGNORECASE
        pattern = compile(r'(system:|assistant:|sapiens:)', IGNORECASE)
        matches = list(pattern.finditer(text))
        if len(matches) == 0: return text
        if len(matches) == 1: return text[matches[0].end():].strip()
        return text[matches[0].end():matches[1].start()].strip()
    def __extract_before_user(self, text=''):
        substring = 'user:'
        index = text.lower().find(substring)
        if index != -1: return text[:index].strip()
        return text.strip()
    def __cut_before_punctuation(self, text=''):
        for index, character in enumerate(str(text)):
            if character in '.;!?':
                try: return text[:index+1]
                except: return text[:index]
        return text
    def __token_generator(self, inputs=None, image_inputs=None, temperature=0.5, max_new_tokens=256):
        try:
            from sapiens_transformers import TextIteratorStreamer
            from threading import Thread
            streamer = TextIteratorStreamer(self.__processor, skip_special_tokens=True, skip_prompt=True)
            if image_inputs is not None: generation_kwargs = dict(inputs, image_inputs, max_new_tokens=max_new_tokens, streamer=streamer)
            else: generation_kwargs = dict(inputs, max_new_tokens=max_new_tokens, streamer=streamer)
            thread = Thread(target=self.__model.generate, kwargs=generation_kwargs)
            thread.start()
            stop, total_tokens = False, 0
            if self.__max_new_tokens != 512: max_new_tokens = min(self.__max_new_tokens, max_new_tokens if max_new_tokens else 256)
            for token in streamer:
                if stop: break
                if max_new_tokens and total_tokens >= max_new_tokens:
                    cut_before_punctuation = self.__cut_before_punctuation(text=token)
                    if cut_before_punctuation != token or token.strip().endswith(('.', ';', '!', '?', '\n')): token, stop = cut_before_punctuation.rstrip(), True
                total_tokens += 1
                yield token.lstrip() if total_tokens <= 1 else token
            thread.join()
        except Exception as error:
            if self.__show_errors: print('ERROR in SapiensModel.__token_generator: '+str(error))
            return ''
    def __eliminates_unnecessary_texts(self, text='', is_template=False):
        from re import match as _match
        def extract_after_assistant(text=''):
            match = _match(r'(?i)^assistant:?\s*(.*)', text)
            return match.group(1) if match else text
        def extract_after_inst(text=''):
            match = _match(r'(?i)\[/INST\]\s*(.*)', text)
            return match.group(1) if match else text
        text = str(text).strip()
        is_template = bool(is_template) if type(is_template) in (bool, int, float) else False
        if is_template and 'Human:' in text: text = text.split('Human:')[0].strip()
        if is_template and 'user:' in text: text = text.split('user:')[0].strip()
        if text.startswith(':'): text = text[1:].strip()
        text = extract_after_assistant(text=text).strip()
        text = extract_after_inst(text=text).strip()
        if not text: return ''
        characters = ['.', '?', '!', ';', '`']
        if text[-1] in characters: return text
        last_occurrence, found_character = -1, ''
        for character in characters:
            index = text.rfind(character)
            if index != -1:
                last_occurrence = index
                found_character = character
                break
        return text[:last_occurrence + 1] if last_occurrence != -1 else text
    def __is_midia_message(self, message={}):
        if 'content' in message:
            content = message['content']
            if type(content) == str: return False
            elif type(content) in (tuple, list):
                if len(content) > 0: content = content[-1]
                if 'text' in content: return True
        return False
    def __is_web_address(self, path=''): return str(path).lower().strip().startswith(('https://', 'http://', 'www.'))
    def __existing_path(self, path=''):
        if self.__is_web_address(path=path): return True
        return self.__path.exists(str(path).strip())
    def __non_existent_path(self, path=''):
        print('Non-existent path: '+path)
        print('The path to the added file does not exist.')
    def __download_media(self, url='', _type='video'):
        from os import path
        from tempfile import gettempdir
        from requests import get
        from uuid import uuid4
        from urllib.parse import urlparse, unquote
        response = get(url, stream=True)
        response.raise_for_status()
        temporary_directory = gettempdir()
        parsed_url = urlparse(url)
        file_name = path.basename(unquote(parsed_url.path))
        extension = '.mp4' if _type == 'video' else '.mp3'
        file_extension = path.splitext(file_name)[1] if '.' in file_name else extension
        media_file_name = f'downloaded_{_type}_{uuid4().hex}{file_extension}'
        media_file_path = path.join(temporary_directory, media_file_name)
        with open(media_file_path, 'wb') as video_file:
            for data_chunk in response.iter_content(chunk_size=8192): video_file.write(data_chunk)
        return media_file_path
    def __delete_media(self, media_file_path=''):
        from os import path, remove
        if media_file_path and path.exists(media_file_path): remove(media_file_path)
    def __file_to_base64(self, state=True, path=''):
        if state and len(path) > 0:
            from base64 import b64encode
            with open(path, 'rb') as file: result = b64encode(file.read()).decode('utf-8')
            from os import unlink
            unlink(path)
        return result
    def __set_tqdm(self, disable=True):
        from sapiens_transformers.utils.functions import set_tqdm
        return set_tqdm(disable=disable)
    def __get_directory_path(self, input_path=''):
        directory_path = './'
        if self.__path.isdir(input_path): directory_path = input_path
        if self.__path.isfile(input_path): directory_path = self.__path.dirname(input_path)
        if not directory_path or directory_path in ('.', '/'): directory_path = './'
        return directory_path
    def __merge_images_vertical(self, image_paths=[], maximum_pixels=500):
        if not image_paths: image_paths = self.__image_paths
        from PIL import Image
        from io import BytesIO
        from requests import get
        from tempfile import NamedTemporaryFile
        images = []
        for image_path in image_paths:
            if self.__is_web_address(path=image_path): image = Image.open(BytesIO(get(image_path, stream=True).content))
            else: image = Image.open(image_path)
            image = image.resize((maximum_pixels, maximum_pixels))
            images.append(image)
        widths, heights = zip(*(image.size for image in images))
        maximum_width, total_height = max(widths), sum(heights)
        final_image, offset = Image.new('RGB', (maximum_width, total_height)), 0
        for image in images:
            final_image.paste(image, (0, offset))
            offset += image.size[1]
        temporary_file = NamedTemporaryFile(delete=False, suffix='.png')
        final_image.save(temporary_file.name, format='PNG')
        return temporary_file.name
    def __set_merging_images(self):
        if self.__image_paths:
            output_path = self.__merge_images_vertical(image_paths=self.__image_paths, maximum_pixels=self.__maximum_image_pixels)
            self.__image_paths = []
            from os import path
            if path.exists(output_path):
                self.add_image(path=output_path, maximum_pixels=self.__maximum_image_pixels, merge_images=False)
                return output_path
        return ''
    def __get_mgt(self, prompt='', template=False):
        from sapiens_transformers.training import MGT
        model_path = self.__get_directory_path(input_path=self.__original_model_path)
        mgt = MGT(model_path=model_path, show_errors=self.__show_errors)
        inference = mgt.predict(prompt=prompt)
        if template and inference:
            from unicodedata import normalize
            from re import sub
            text = self.MGT_STRING
            text = normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
            text = sub(r'[^a-zA-Z0-9 ]', '', text)
            tag = text.replace(' ', '_').lower().strip()
            tag_start, tag_end = f'<{tag}>', f'</{tag}>'
            total_tokens = self.__get_total_tokens(text=inference)
            self.__max_new_tokens = int(round(total_tokens+(total_tokens*0.25)))
            return f'{tag_start}{inference}{tag_end}\n\n{prompt}'
        return f'{self.MGT_STRING} {inference}\n\n{prompt}' if inference else prompt
    def create_system(self, model_path='./', system='', increase=1):
        try:
            model_path = model_path.strip() if type(model_path) == str else str(model_path).strip()
            system = system.strip() if type(system) == str else str(system).strip()
            increase = int(increase) if type(increase) in (bool, int, float) else 1
            model_path = self.__get_directory_path(input_path=model_path)
            from pickle import dump
            data = {'model_path': model_path, 'system': system, 'increase': increase}
            file_path = self.__path.join(model_path, 'system.sys')
            with open(file_path, 'wb') as file: dump(data, file)
            return True
        except Exception as error:
            if self.__show_errors: print('ERROR in SapiensModel.create_system: '+str(error))
            return False
    def read_system(self, model_path='./'):
        try:
            model_path = model_path.strip() if type(model_path) == str else str(model_path).strip()
            model_path = self.__get_directory_path(input_path=model_path)
            from pickle import load
            file_path = self.__path.join(model_path, 'system.sys')
            if self.__path.exists(file_path):
                with open(file_path, 'rb') as file: return load(file)
            else: return {'model_path': '', 'system': '', 'increase': 0}
        except Exception as error:
            if self.__show_errors: print('ERROR in SapiensModel.read_system: '+str(error))
            return {'model_path': '', 'system': '', 'increase': 0}
    def add_image(self, path='', maximum_pixels=500, merge_images=True):
        try:
            path = path.strip() if type(path) == str else str(path).strip()
            maximum_pixels = max((1, int(maximum_pixels))) if type(maximum_pixels) in (int, float) else 500
            if self.__image_paths: merge_images = True
            else: merge_images = bool(merge_images) if type(merge_images) in (bool, int, float) else True
            self.__maximum_image_pixels = maximum_pixels
            if self.__existing_path(path=path):
                if merge_images: self.__image_paths.append(path)
                else:
                    modular_entity, sapi_image = self.__ARCHITECTURE == 'modular_entity', self.__ARCHITECTURE == 'sapi_image'
                    sapi_video, sapiens_vision = self.__ARCHITECTURE == 'sapi_video', self.__ARCHITECTURE == 'sapiens_vision'
                    sapiens_videogen, hurlm = self.__ARCHITECTURE == 'sapiens_videogen', self.__ARCHITECTURE == 'hurlm'
                    if sapiens_vision: self.__images.append(path)
                    else:
                        if modular_entity or sapi_image or sapi_video or sapiens_videogen or hurlm:
                            def resize_image(image=[], max_size=500):
                                width, height = image.size
                                if width > max_size or height > max_size: image.thumbnail((max_size, max_size))
                                return image
                            from PIL import Image
                            if self.__is_web_address(path=path):
                                from requests import get
                                self.__images.append(resize_image(image=Image.open(get(path, stream=True).raw), max_size=maximum_pixels))
                            else: self.__images.append(resize_image(image=Image.open(path), max_size=maximum_pixels))
                            if sapiens_videogen:
                                self.__set_tqdm(disable=True)
                                from sapiens_transformers.diffusers import SapiensVideoGenImageToVideoPipeline
                                try: self.__model = SapiensVideoGenImageToVideoPipeline.from_pretrained(self.__model_path, torch_dtype=self.__sapiens_precision, low_cpu_mem_usage=True, verbose=False).to(self.__model.device)
                                except: self.__model = SapiensVideoGenImageToVideoPipeline.from_pretrained(self.__model_path, torch_dtype='auto', low_cpu_mem_usage=True, verbose=False).to(self.__model.device)
            else: self.__non_existent_path(path=path)
            return True
        except Exception as error:
            if self.__show_errors: print('ERROR in SapiensModel.add_image: '+str(error))
            return False
    def add_audio(self, path=''):
        try:
            path = path.strip() if type(path) == str else str(path).strip()
            if not path or not self.__existing_path(path=path):
                from pathlib import Path as __Path
                get_path = __Path(path)
                file_name = get_path.name
                path = self.__original_model_path if self.__original_model_path.endswith('/') else self.__original_model_path+'/'
                path += 'samples/'+file_name
            if self.__existing_path(path=path):
                sapi_audio, sapi_audiogen = self.__ARCHITECTURE == 'sapi_audio', self.__ARCHITECTURE == 'sapi_audiogen'
                if sapi_audio or sapi_audiogen:
                    downloaded = False
                    if self.__is_web_address(path=path): path, downloaded = self.__download_media(url=path, _type='audio'), True
                    self.__downloaded = downloaded
                    if sapi_audiogen: self.__audios.append(path)
                    else:
                        from torchaudio import load, transforms
                        waveform, sampling_rate = load(path)
                        if sampling_rate != 16000: waveform, sampling_rate = transforms.Resample(orig_freq=sampling_rate, new_freq=16000)(waveform), 16000
                        waveform = waveform.mean(dim=0).squeeze()
                        container = (waveform, sampling_rate)
                        self.__audios.append(container)
                        if downloaded: self.__delete_media(media_file_path=path)
            else: self.__non_existent_path(path=path)
            return True
        except Exception as error:
            if self.__show_errors: print('ERROR in SapiensModel.add_audio: '+str(error))
            return False
    def add_video(self, path='', maximum_pixels=100):
        try:
            path = path.strip() if type(path) == str else str(path).strip()
            self.__maximum_video_pixels = max((1, int(maximum_pixels))) if type(maximum_pixels) in (int, float) else 100
            if self.__existing_path(path=path):
                sapi_video, sapiens_vision = self.__ARCHITECTURE == 'sapi_video', self.__ARCHITECTURE == 'sapiens_vision'
                if sapi_video:
                    from av import open as open_av
                    downloaded = False
                    if self.__is_web_address(path=path): path, downloaded = self.__download_media(url=path, _type='video'), True
                    container = open_av(path)
                    container.streams.video[0].thread_type = 'AUTO'
                    container.streams.video[0].thread_count = 1
                    self.__videos.append(container)
                    if downloaded: self.__delete_media(media_file_path=path)
                elif sapiens_vision: self.__videos.append(path)
            else: self.__non_existent_path(path=path)
            return True
        except Exception as error:
            if self.__show_errors: print('ERROR in SapiensModel.add_video: '+str(error))
            return False
    def generate_template_text(self, system='', prompt='', temperature=0.5, max_new_tokens=None, stream=False):
        try:
            system = system.strip() if type(system) == str else str(system).strip()
            prompt = prompt.strip() if type(prompt) == str else str(prompt).strip()
            temperature = min((1, max((0.01, float(temperature))))) if type(temperature) in (int, float) else 0.5
            maximum_new_tokens = max((1, int(round(max_new_tokens)))) if type(max_new_tokens) in (int, float) else None
            stream = bool(stream) if type(stream) in (bool, int, float) else False
            if system and not prompt:
                prompt = system
                system = ''
            def remove_template_system(template=''):
                if '<|' not in template and '|>' not in template and 'system:' not in template and 'user:' not in template: return template
                template_lines = template.split('\n')
                for index, line in enumerate(template_lines):
                    line = line.lower().strip()
                    if '|>system<|' in line or 'system:' in line:
                        row = ''
                        while '|>user<|' not in row and 'user:' not in row:
                            row = template_lines[index].lower().strip()
                            index += 1
                        try: return '\n'.join(template_lines[index-1:])
                        except: return '\n'.join(template_lines[index:])
                return template
            template_lower = prompt.lower().strip()
            if system and ('>system<' in template_lower or 'system:' in template_lower): prompt = remove_template_system(template=prompt)
            system_dictionary = self.read_system(model_path=self.__original_model_path)
            prompt = self.__get_mgt(prompt=prompt, template=True)
            system_value, increase_value = str(system_dictionary.get('system', '')).strip(), bool(float(system_dictionary.get('increase', 0)))
            if system_value and increase_value: system = str(system_value+'\n\n'+system).strip()
            elif system_value and not increase_value and not system: system = system_value
            elif system_value and not increase_value: system = system if len(system) > 3 else self.__system
            elif not system and self.__system: system = self.__system
            self.__output_image = self.__set_merging_images()
            __check_template = self.__check_template(text=prompt)
            modular_entity, sapi_image = self.__ARCHITECTURE == 'modular_entity', self.__ARCHITECTURE == 'sapi_image'
            sapi_video, sapiens_vision = self.__ARCHITECTURE == 'sapi_video', self.__ARCHITECTURE == 'sapiens_vision'
            sapi_audio, hurlm = self.__ARCHITECTURE == 'sapi_audio', self.__ARCHITECTURE == 'hurlm'
            sastral = self.__ARCHITECTURE == 'sastral'
            if sapi_audio: return self.generate_text(system=system, prompt=prompt, messages=[], temperature=temperature, max_new_tokens=maximum_new_tokens, stream=stream)
            if modular_entity:
                pre_content = '<|image|>'*len(self.__images) if type(self.__images) in (tuple, list) else '<|image|>'
                if __check_template: conversation_input = prompt
                else: conversation_input = pre_content+'<|begin_of_text|>'+prompt
                __system = system if len(system) > 0 else self.__system
                conversation_input = f'<|system|>{__system}<|end_of_system|>'+conversation_input
                inputs = self.__processor(self.__images, conversation_input, return_tensors='pt').to(self.__model.device)
                maximum_length = self.CONTEXT_SIZE
                encoding = self.__get_encoding()
                input_length = len(encoding.encode(conversation_input))
                maximum_new_tokens = self.__get_maximum_new_tokens(maximum_length=maximum_length, input_length=input_length, maximum_new_tokens=maximum_new_tokens)
                if input_length > maximum_length:
                    template_system = self.__extract_system_subtext(text=conversation_input)
                    if len(template_system) > 0: system = template_system
                    __system = system if len(system) > 0 else self.__system
                    system_length = len(encoding.encode(__system))
                    tokens_limit = int(max(0, (maximum_length - system_length) - 53) / 2)
                    prompt = self.__divide_text_in_parts(prompt=self.__extract_user_subtext(text=conversation_input), tokens_limit=tokens_limit) if tokens_limit > 0 else ''
                    conversation_input = pre_content+'<|begin_of_text|>'+prompt
                    conversation_input = f'<|system|>{__system}<|end_of_system|>'+conversation_input
                    inputs = self.__processor(self.__images, conversation_input, return_tensors='pt').to(self.__model.device)
                    maximum_new_tokens = tokens_limit
                if stream: return self.__token_generator(inputs=inputs, temperature=temperature, max_new_tokens=maximum_new_tokens)
                else:
                    output = self.__model.generate(**inputs, temperature=temperature, max_new_tokens=maximum_new_tokens, do_sample=True)
                    generated_text = self.__processor.decode(output[0], skip_special_tokens=True, skip_prompt=True)
                    if prompt in generated_text: generated_text = generated_text.split(prompt)[-1]
                    return self.__eliminates_unnecessary_texts(text=generated_text, is_template=True).strip()
            elif sapi_image or sapi_video or sapiens_vision or hurlm:
                if len(system) < 1: system = self.__extract_system_subtext(text=prompt)
                if len(system) < 1: system = self.__system
                if '<|begin_of_text|>' in prompt: prompt = prompt.split('<|begin_of_text|>')[-1].strip()
                return self.generate_text(system=system, prompt=prompt, messages=[], temperature=temperature, max_new_tokens=maximum_new_tokens, stream=stream)
            if not stream and self.__sapiens is None:
                from sapiens_transformers import pipeline
                pipe = pipeline('text-generation', model=self.__model, tokenizer=self.__tokenizer, device=self.__model.device)
            if __check_template:
                prompt_lower = prompt.lower()
                if '|>user<|' in prompt_lower and '|>system<|' not in prompt_lower: conversation_input = f'<|start_header_id|>system<|end_header_id|>\n\n{system}<|eot_id|>\n{prompt}' if system else prompt
                elif 'user:' in prompt_lower and 'system:' not in prompt_lower: conversation_input = f'system: {system}\n{prompt}' if system else prompt
                else: conversation_input = prompt
            else:
                __system = system if len(system.strip()) > 0 else self.__system
                if len(__system) > 0: conversation_input = f'system: {__system}\nuser: {prompt}\nassistant:\n'
                else: conversation_input = f'user: {prompt}\nassistant:\n'
            def endswith_any(text='', add=[]):
                suffixes = ['user:', 'Human:', '<|start_header_id|>user', '[/INST]', '<start_of_turn>user', '<|user|>', '<|im_start|>user', 'User:', '<|prompt|>', '(End of message)']+add
                return any(text.endswith(suffix) for suffix in suffixes)
            if self.__sapiens is not None:
                maximum_length = self.__sapiens._n_ctx
                encoding = self.__get_encoding()
                input_length = len(encoding.encode(conversation_input))
                maximum_new_tokens = self.__get_maximum_new_tokens(maximum_length=maximum_length, input_length=input_length, maximum_new_tokens=maximum_new_tokens)
                if input_length > maximum_length:
                    template_system = self.__extract_system_subtext(text=conversation_input)
                    if len(template_system) > 0: system = template_system
                    __system = system if len(system) > 0 else self.__system
                    system_length = len(encoding.encode(__system))
                    tokens_limit = int(max(0, (maximum_length - system_length) - 27) / 2)
                    prompt = self.__divide_text_in_parts(prompt=self.__extract_user_subtext(text=conversation_input), tokens_limit=tokens_limit) if tokens_limit > 0 else ''
                    if len(__system) > 0: conversation_input = f'system: {__system}\nuser: {prompt}\nassistant:\n'
                    else: conversation_input = f'user: {prompt}\nassistant:\n'
                    maximum_new_tokens = tokens_limit
                if stream:
                    from threading import Thread
                    def generate_template_tokens(maximum_new_tokens=512):
                        def generate_tokens(maximum_new_tokens=512):
                            try: sapiens_tokens = self.__sapiens(conversation_input, temperature=temperature, max_tokens=maximum_new_tokens*2, stop=['Q:', 'user:'], stream=True)
                            except: sapiens_tokens = self.__sapiens(conversation_input, temperature=temperature, max_tokens=self.__max_new_tokens*2, stop=['Q:', 'user:'], stream=True)
                            stop, total_tokens = False, 0
                            if self.__max_new_tokens != 512: maximum_new_tokens = min(self.__max_new_tokens, maximum_new_tokens if maximum_new_tokens else 256)
                            for token in sapiens_tokens:
                                try:
                                    if stop: break
                                    choices = token['choices'] if 'choices' in token else []
                                    choices_0 = choices[0] if len(choices) > 0 else {}
                                    token = choices_0['text'] if 'text' in choices_0 else ''
                                    if len(token) < 1 and 'delta' in choices_0:
                                        try: token = choices_0['delta'].get('content', '')
                                        except: break
                                    if maximum_new_tokens and total_tokens >= maximum_new_tokens:
                                        cut_before_punctuation = self.__cut_before_punctuation(text=token)
                                        if cut_before_punctuation != token or token.strip().endswith(('.', ';', '!', '?', '\n')): token, stop = cut_before_punctuation.rstrip(), True
                                    total_tokens += 1
                                    yield token.lstrip() if total_tokens <= 1 else token
                                except: return ''
                        thread = Thread(target=generate_tokens, args=(maximum_new_tokens,))
                        thread.start()
                        try:
                            for token in generate_tokens(maximum_new_tokens=maximum_new_tokens): yield token
                        except: return ''
                        thread.join()
                    return generate_template_tokens(maximum_new_tokens=maximum_new_tokens)
                else:
                    try: response = self.__sapiens(conversation_input, temperature=temperature, max_tokens=maximum_new_tokens, stop=['Q:', 'user:'])
                    except: response = self.__sapiens.create_chat_completion(conversation_input, temperature=temperature, max_tokens=self.__max_new_tokens, stop=['Q:', 'user:'])
                    choices = response['choices'] if 'choices' in response else []
                    choices_0 = choices[0] if len(choices) > 0 else {}
                    full_text = choices_0['text'] if 'text' in choices_0 else ''
                    if len(full_text) < 1 and 'message' in choices_0:
                        message = choices_0['message']
                        if 'content' in message: full_text = message['content'].strip()
                    return self.__eliminates_unnecessary_texts(text=full_text, is_template=True).strip()
            if self.__tokenizer is not None:
                maximum_length = self.CONTEXT_SIZE
                input_length = len(self.__tokenizer(conversation_input)['input_ids'])
                length_limit = maximum_length - input_length
                if maximum_new_tokens is None: maximum_new_tokens = length_limit
                else: maximum_new_tokens = min(maximum_new_tokens, length_limit)
                maximum_new_tokens = max(256, maximum_new_tokens)
                if input_length > maximum_length:
                    template_system = self.__extract_system_subtext(text=conversation_input)
                    if len(template_system) > 0: system = template_system
                    __system = system if len(system) > 0 else self.__system
                    system_length = len(self.__tokenizer(__system)['input_ids'])
                    tokens_limit = int(max(0, (maximum_length - system_length) - 27) / 2)
                    prompt = self.__divide_text_in_parts(prompt=self.__extract_user_subtext(text=conversation_input), tokens_limit=tokens_limit) if tokens_limit > 0 else ''
                    if system_length > 0: conversation_input = f'system: {__system}\nuser: {prompt}\n'
                    else: conversation_input = f'user: {prompt}\n'
                    maximum_new_tokens = tokens_limit
                if stream:
                    from torch import no_grad, cat
                    from torch.nn.functional import softmax
                    from torch import multinomial
                    generated_ids, all_text = self.__tokenizer(conversation_input, return_tensors='pt').input_ids.to(self.__model.device), ''
                    stop_ids = [self.__tokenizer.encode(token, add_special_tokens=False)[0] for token in ['Q:', 'user:', 'assistant:']]
                    def generate_template_tokens_x(generated_ids=[], all_text='', stop_ids=[], max_length=256):
                        all_text = self.__tokenizer.decode(generated_ids[0], skip_special_tokens=True)
                        maximum_new_tokens, stop, total_tokens = max_length, False, 0
                        if self.__max_new_tokens != 512: maximum_new_tokens = min(self.__max_new_tokens, maximum_new_tokens if maximum_new_tokens else 256)
                        for _ in range(max_length):
                            try:
                                if stop: break
                                with no_grad(): outputs = self.__model(generated_ids)
                                next_token_logits = outputs.logits[:, -1, :]
                                probs = softmax(next_token_logits / temperature, dim=-1)
                                next_token = multinomial(probs, num_samples=1)
                                generated_ids = cat([generated_ids, next_token], dim=-1)
                                current_text = self.__tokenizer.decode(generated_ids[0], skip_special_tokens=True, skip_prompt=True)
                                new_text = current_text[len(all_text):]
                                if maximum_new_tokens and total_tokens >= maximum_new_tokens:
                                    cut_before_punctuation = self.__cut_before_punctuation(text=new_text)
                                    if cut_before_punctuation != new_text or new_text.strip().endswith(('.', ';', '!', '?', '\n')): new_text, stop = cut_before_punctuation.rstrip(), True
                                total_tokens += 1
                                yield new_text.lstrip() if total_tokens <= 1 else new_text
                                all_text = current_text
                                try:
                                    if next_token.item() in stop_ids or next_token.item() == self.__tokenizer.eos_token_id: break
                                    if endswith_any(text=all_text, add=['?:']): break
                                    if endswith_any(text=all_text): break
                                except: pass
                            except: yield ''
                    def generate_template_tokens_y(generated_ids=[], all_text='', stop_ids=[], max_length=256):
                        maximum_new_tokens, stop, total_tokens = max_length, False, 0
                        if self.__max_new_tokens != 512: maximum_new_tokens = min(self.__max_new_tokens, maximum_new_tokens if maximum_new_tokens else 256)
                        for _ in range(max_length):
                            try:
                                if stop: break
                                with no_grad(): outputs = self.__model(generated_ids)
                                next_token_logits = outputs.logits[:, -1, :]
                                probs = softmax(next_token_logits / temperature, dim=-1)
                                next_token = multinomial(probs, num_samples=1)
                                generated_ids = cat([generated_ids, next_token], dim=-1)
                                tokenizer_decode = self.__tokenizer.decode(next_token[0], skip_special_tokens=True, skip_prompt=True)
                                if next_token.item() in stop_ids or next_token.item() == self.__tokenizer.eos_token_id: break
                                if endswith_any(text=all_text, add=['?:']): break
                                all_text += tokenizer_decode
                                if maximum_new_tokens and total_tokens >= maximum_new_tokens:
                                    cut_before_punctuation = self.__cut_before_punctuation(text=tokenizer_decode)
                                    if cut_before_punctuation != tokenizer_decode or tokenizer_decode.strip().endswith(('.', ';', '!', '?', '\n')): tokenizer_decode, stop = cut_before_punctuation.rstrip(), True
                                total_tokens += 1
                                yield tokenizer_decode.lstrip() if total_tokens <= 1 else tokenizer_decode
                            except: yield ''
                            try:
                                if endswith_any(text=all_text): break
                                if next_token.item() == self.__tokenizer.eos_token_id: break
                            except: pass
                    if sastral: return generate_template_tokens_x(generated_ids=generated_ids, all_text=all_text, stop_ids=stop_ids, max_length=maximum_new_tokens)
                    else: return generate_template_tokens_y(generated_ids=generated_ids, all_text=all_text, stop_ids=stop_ids, max_length=maximum_new_tokens)
                else:
                    try: response = pipe(conversation_input, temperature=temperature, max_length=maximum_new_tokens, do_sample=True, truncation=True, return_full_text=False, stop_sequence=['Q:', 'user:'])
                    except: response = pipe(conversation_input, temperature=temperature, max_length=self.__max_new_tokens, do_sample=True, truncation=True, return_full_text=False, stop_sequence=['Q:', 'user:'])
                    generated_text = response[0]['generated_text']
                    generated_text = self.__tokenizer.decode(self.__tokenizer(generated_text)['input_ids'], skip_special_tokens=True, skip_prompt=True)
                    generated_text = self.__format_output(text=generated_text)
                    generated_text = self.__extract_before_user(text=generated_text)
                    return self.__eliminates_unnecessary_texts(text=generated_text, is_template=True).strip()
            else:
                print('Non-existent path: '+self.__original_model_path)
                print('The path to the model tokenizer does not exist.')
                return ''
        except Exception as error:
            if self.__show_errors: print('ERROR in SapiensModel.generate_template_text: '+str(error))
            return ''
    def generate_text(self, system='', prompt='', messages=[], temperature=0.5, max_new_tokens=None, stream=False):
        try:
            system = system.strip() if type(system) == str else str(system).strip()
            prompt = prompt.strip() if type(prompt) == str else str(prompt).strip()
            messages = list(messages) if type(messages) in (tuple, list) else []
            temperature = min((1, max((0.01, float(temperature))))) if type(temperature) in (int, float) else 0.5
            maximum_new_tokens = max((1, int(round(max_new_tokens)))) if type(max_new_tokens) in (int, float) else None
            stream = bool(stream) if type(stream) in (bool, int, float) else False
            if system and not prompt:
                prompt = system
                system = ''
            def has_system_message(messages=[]):
                if not messages: return False
                first_message = messages[0]
                _role = str(first_message.get('role', '')).lower().strip()
                return _role == 'system'
            _system_message = has_system_message(messages=messages)
            if system and _system_message: messages = messages[1:]
            system_dictionary = self.read_system(model_path=self.__original_model_path)
            system_value, increase_value = str(system_dictionary.get('system', '')).strip(), bool(float(system_dictionary.get('increase', 0)))
            if system_value and increase_value: system = str(system_value+'\n\n'+system).strip()
            elif system_value and not increase_value and not system: system = system_value
            elif system_value and not increase_value: system = system if len(system) > 3 else self.__system
            elif not system and self.__system: system = self.__system
            if messages:
                _role = str(messages[-1].get('role', '')).lower().strip()
                if _role == 'user':
                    _prompt = str(messages[-1].get('content', '')).strip()
                    _prompt = self.__get_mgt(prompt=_prompt, template=False)
                    if _prompt: messages[-1]['content'] = _prompt
            else: prompt = self.__get_mgt(prompt=prompt, template=False)
            self.__output_image = self.__set_merging_images()
            modular_entity, sapi_image = self.__ARCHITECTURE == 'modular_entity', self.__ARCHITECTURE == 'sapi_image'
            sapi_video, sapiens_vision = self.__ARCHITECTURE == 'sapi_video', self.__ARCHITECTURE == 'sapiens_vision'
            sapi_audio, hurlm = self.__ARCHITECTURE == 'sapi_audio', self.__ARCHITECTURE == 'hurlm'
            if sapi_audio:
                if maximum_new_tokens is not None:
                    maximum_length = self.__model.config.max_length
                    maximum_new_tokens = min((maximum_new_tokens, maximum_length))
                def get_transcripts():
                    number_of_audios = len(self.__audios)
                    for index, audio in enumerate(self.__audios):
                        try:
                            waveform, sampling_rate = audio[0], audio[-1]
                            start, segment_length, position = 0, 480000, index+1
                            while start < len(waveform):
                                end = start + segment_length
                                segment = waveform[start:end]
                                processed = self.__processor(segment.numpy(), sampling_rate=sampling_rate, return_tensors='pt', return_attention_mask=True)
                                input_features = processed.input_features.to(self.__model.device)
                                attention_mask = processed.attention_mask.to(self.__model.device)
                                if maximum_new_tokens is not None: self.__model.max_new_tokens = maximum_new_tokens
                                if temperature != 0.5: self.__model.temperature = temperature
                                generated_ids = self.__model.generate(input_features, attention_mask=attention_mask, output_scores=True, return_dict_in_generate=True)
                                for token_id in generated_ids.sequences[0]: yield self.__processor.decode([token_id], skip_special_tokens=True)
                                start = end
                            if position < number_of_audios: yield '\n\n'
                        except: yield ''
                _generate_text, generated_text = get_transcripts(), ''
                if stream: return _generate_text
                else:
                    for token in _generate_text: generated_text += token
                    return generated_text.strip()
            if self.__images is None or len(self.__images) < 1: modular_entity = sapi_image = False
            def has_system_role(messages=[]): return any(message.get('role') == 'system' and 'content' in message for message in messages if isinstance(message, dict))
            has_image = type(self.__images) in (tuple, list) and len(self.__images) > 0
            if (sapi_video or sapiens_vision or hurlm) and has_image: description = 'Describe what you are seeing.'
            else: description = 'Describe what you see in the video.' if sapi_video else 'Describe what you see in the image.'
            _has_system_role = has_system_role(messages=messages)
            if len(messages) < 1:
                if not modular_entity and not sapi_image:
                    if len(system) > 0: messages.append({'role': 'system', 'content': system})
                    else: messages.append({'role': 'system', 'content': self.__system})
                if len(prompt) > 0: messages.append({'role': 'user', 'content': prompt})
                else:
                    if modular_entity or sapi_image or sapi_video or sapiens_vision or hurlm: messages.append({'role': 'user', 'content': description})
                    else: messages.append({'role': 'user', 'content': 'Hi!'})
            else:
                if not _has_system_role and not modular_entity and not sapi_image:
                    if len(system) > 0: messages, _has_system_role = [{'role': 'system', 'content': system}]+messages, True
                if not _has_system_role and not modular_entity and not sapi_image: [{'role': 'system', 'content': self.__system}]+messages
                if not 'user' in list(messages[-1].values()):
                    if len(prompt) > 0: messages.append({'role': 'user', 'content': prompt})
                    else:
                        if modular_entity or sapi_image or sapi_video or sapiens_vision or hurlm: messages.append({'role': 'user', 'content': description})
                        else: messages.append({'role': 'user', 'content': 'Hi!'})
            if modular_entity or sapi_image or hurlm:
                if _has_system_role:
                    new_messages = []
                    for message in messages:
                        role = str(message['role']).lower().strip() if 'role' in message else ''
                        if role != 'system': new_messages.append(message)
                    messages = new_messages.copy()
                if hurlm: __system = ''
                else: __system = system if len(system) > 0 else self.__system
                message, image_inputs = messages[-1], None
                pre_content = [{'type': 'image'} for _ in self.__images]
                if not self.__is_midia_message(message=message):
                    if len(messages) > 0: messages.pop()
                    if hurlm: message = {'role': 'user', 'content': pre_content+[{'type': 'text', 'text': message['content']}]}
                    else: message = {'role': 'user', 'content': pre_content+[{'type': 'text', 'text': __system+'\n\n'+message['content']}]}
                    messages.append(message)
                if hurlm: input_text = self.__processor.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
                else: input_text = self.__processor.apply_chat_template(messages, add_generation_prompt=True)
                if self.__images:
                    if hurlm:
                        inputs = self.__processor(text=input_text, return_tensors='pt').to(self.__model.device)
                        inputs = {key: value.to(self.__model.device) for key, value in inputs.items()}
                        from sapiens_transformers import CLIPFeatureExtractor
                        feature_extractor = CLIPFeatureExtractor.from_pretrained(self.__model_path, size=224)
                        image_inputs = feature_extractor(images=self.__images, return_tensors='pt')
                        image_inputs = {key: value.to(self.__model.device) for key, value in image_inputs.items()}
                    else: inputs = self.__processor(self.__images, input_text, add_special_tokens=False, return_tensors='pt').to(self.__model.device)
                else: inputs = self.__processor(input_text, add_special_tokens=False, return_tensors='pt').to(self.__model.device)
                maximum_length = self.CONTEXT_SIZE
                input_length = inputs['input_ids'].shape[1]
                maximum_new_tokens = self.__get_maximum_new_tokens(maximum_length=maximum_length, input_length=input_length, maximum_new_tokens=maximum_new_tokens)
                if input_length > maximum_length:
                    if len(prompt) < 1:
                        message, prompt = messages[-1], description
                        if self.__is_midia_message(message=message): prompt = str(message['content'][-1]['text']).strip()
                    messages, system_length = [], len(self.__get_encoding().encode(__system))
                    tokens_limit = int(max(0, (maximum_length - system_length) - 115) / 2)
                    prompt = self.__divide_text_in_parts(prompt=prompt, tokens_limit=tokens_limit) if tokens_limit > 0 else ''
                    if hurlm: message = {'role': 'user', 'content': pre_content+[{'type': 'text', 'text': prompt}]}
                    else: message = {'role': 'user', 'content': pre_content+[{'type': 'text', 'text': __system+'\n\n'+prompt}]}
                    messages.append(message)
                    if hurlm: input_text = self.__processor.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
                    else: input_text = self.__processor.apply_chat_template(messages, add_generation_prompt=True)
                    inputs = self.__processor(self.__images, input_text, add_special_tokens=False, return_tensors='pt').to(self.__model.device)
                    maximum_new_tokens = tokens_limit
                if stream: return self.__token_generator(inputs=inputs, image_inputs=image_inputs, temperature=temperature, max_new_tokens=maximum_new_tokens)
                else:
                    if image_inputs is not None: output = self.__model.generate(**inputs, **image_inputs, temperature=temperature, max_new_tokens=maximum_new_tokens, do_sample=True)
                    else: output = self.__model.generate(**inputs, temperature=temperature, max_new_tokens=maximum_new_tokens, do_sample=True)
                    generated_text = self.__processor.decode(output[0], skip_special_tokens=True, skip_prompt=True)
                    if prompt in generated_text: generated_text = generated_text.split(prompt)[-1]
                    return self.__eliminates_unnecessary_texts(text=generated_text).strip()
            elif sapi_video:
                __system = system if len(system) > 0 else self.__system
                message, outputs, generated_text = messages[-1], [], ''
                if not self.__is_midia_message(message=message):
                    if len(messages) > 0: messages.pop()
                    message = {'role': 'user', 'content': [{'type': 'video'}, {'type': 'text', 'text': message['content']}]}
                    messages.append(message)
                def messages_type_update(messages=[]):
                    for message in messages:
                        if message.get('role') == 'user' and isinstance(message.get('content'), list):
                            for content_item in message['content']:
                                if content_item.get('type') == 'video': content_item['type'] = 'image'
                    return messages
                def get_messages(maximum_length=0):
                    if len(prompt) < 1:
                        message, prompt = messages[-1], description
                        if self.__is_midia_message(message=message): prompt = str(message['content'][-1]['text']).strip()
                    messages, system_length = [], len(self.__get_encoding().encode(__system))
                    tokens_limit = int(max(0, (maximum_length - system_length) - 115) / 2)
                    prompt = self.__divide_text_in_parts(prompt=prompt, tokens_limit=tokens_limit) if tokens_limit > 0 else ''
                    messages.append({'role': 'system', 'content': __system})
                    messages.append({'role': 'user', 'content': [{'type': 'video'}, {'type': 'text', 'text': prompt}]})
                    maximum_new_tokens = tokens_limit
                    return (messages, maximum_new_tokens)
                from numpy import stack, linspace
                def read_video_pyav(container=None, indexes=[]):
                    def resize_frame(frame=[], max_size=500):
                        from cv2 import resize, INTER_AREA
                        height, width, _ = frame.shape
                        scale = min(max_size / width, max_size / height)
                        new_width, new_height = int(width * scale), int(height * scale)
                        return resize(frame, (new_width, new_height), interpolation=INTER_AREA)
                    frames = []
                    container.seek(0)
                    start_index, end_index = indexes[0], indexes[-1]
                    decoding = container.decode(video=0)
                    for index, frame in enumerate(decoding):
                        if index > end_index: break
                        if index in indexes:
                            resized_frame = resize_frame(frame=frame.to_ndarray(format='rgb24'), max_size=self.__maximum_video_pixels)
                            frames.append(resized_frame)
                    container.close()
                    return stack(frames)
                medias, maximum_length = [], self.CONTEXT_SIZE
                for video in self.__videos: medias.append({'type': 'video', 'media': video})
                for image in self.__images: medias.append({'type': 'image', 'media': image})
                number_of_medias = len(medias)
                def get_return(medias=[], messages=[], maximum_length=0, maximum_new_tokens=0, temperature=0.5, number_of_medias=0):
                    for index, media in enumerate(medias):
                        try:
                            _type, media, discrepant, inputs_media, position = media['type'], media['media'], False, {}, index+1
                            if _type == 'image': messages = messages_type_update(messages=messages)
                            else:
                                total_frames = media.streams.video[0].frames
                                indexes = linspace(0, total_frames - 1, num=8).astype(int)
                                clip = read_video_pyav(container=media, indexes=indexes)
                            formatted_prompt = self.__processor.apply_chat_template(messages, add_generation_prompt=True)
                            if _type == 'image': inputs_media = self.__processor(text=formatted_prompt, images=media, padding=True, return_tensors='pt').to(self.__model.device, self.__sapiens_precision)
                            else: inputs_media = self.__processor(text=formatted_prompt, videos=clip, padding=True, return_tensors='pt').to(self.__model.device)
                            input_length = inputs_media['input_ids'].shape[1]
                            if input_length > maximum_length: discrepant = True
                            maximum_new_tokens = self.__get_maximum_new_tokens(maximum_length=maximum_length, input_length=input_length, maximum_new_tokens=maximum_new_tokens)
                            if discrepant:
                                messages, maximum_new_tokens = get_messages(maximum_length=maximum_length)
                                formatted_prompt = self.__processor.apply_chat_template(messages, add_generation_prompt=True)
                                if _type == 'image': inputs_media = self.__processor(text=formatted_prompt, images=media, padding=True, return_tensors='pt').to(self.__model.device, self.__sapiens_precision)
                                else: inputs_media = self.__processor(text=formatted_prompt, videos=clip, padding=True, return_tensors='pt').to(self.__model.device)
                            def stream_all(number_of_medias=0):
                                for token in self.__token_generator(inputs=inputs_media, temperature=temperature, max_new_tokens=maximum_new_tokens): yield token
                                if position < number_of_medias: yield '\n\n'
                            yield from stream_all(number_of_medias=number_of_medias)
                        except: yield ''
                _generate_text = get_return(medias=medias, messages=messages, maximum_length=maximum_length, maximum_new_tokens=maximum_new_tokens, temperature=temperature, number_of_medias=number_of_medias)
                if stream: return _generate_text
                else:
                    for token in _generate_text: generated_text += token
                    return generated_text.strip()
            elif sapiens_vision:
                __system = system if len(system) > 0 else self.__system
                message, outputs, generated_text = messages[-1], [], ''
                if not self.__is_midia_message(message=message):
                    if len(messages) > 0: messages.pop()
                    message = {'role': 'user', 'content': [{'type': 'video'}, {'type': 'text', 'text': message['content']}]}
                    messages.append(message)
                def messages_update(messages=[], _type='image', path=''):
                    square_proportion = self.__maximum_image_pixels if _type == 'image' else self.__maximum_video_pixels
                    for message in messages:
                        if message.get('role') == 'user' and isinstance(message.get('content'), list):
                            for content_item in message['content']:
                                if content_item.get('type') != 'text':
                                    content_item['type'], content_item[_type] = _type, path
                                    content_item['resized_width'] = content_item['resized_height'] = square_proportion
                    return messages
                def get_messages(maximum_length=0, _type='image', path=''):
                    if len(prompt) < 1:
                        message, prompt = messages[-1], description
                        if self.__is_midia_message(message=message): prompt = str(message['content'][-1]['text']).strip()
                    messages, system_length = [], len(self.__get_encoding().encode(__system))
                    tokens_limit = int(max(0, (maximum_length - system_length) - 140) / 2)
                    prompt = self.__divide_text_in_parts(prompt=prompt, tokens_limit=tokens_limit) if tokens_limit > 0 else ''
                    messages.append({'role': 'system', 'content': __system})
                    square_proportion = self.__maximum_image_pixels if _type == 'image' else self.__maximum_video_pixels
                    if _type == 'image': messages.append({'role': 'user', 'content': [{'type': _type, _type: path,
                    'resized_width': square_proportion, 'resized_height': square_proportion}, {'type': 'text', 'text': prompt}]})
                    maximum_new_tokens = tokens_limit
                    return (messages, maximum_new_tokens)
                medias, maximum_length = [], self.CONTEXT_SIZE
                for video in self.__videos: medias.append({'type': 'video', 'media': video})
                for image in self.__images: medias.append({'type': 'image', 'media': image})
                number_of_medias = len(medias)
                def get_return(medias=[], messages=[], maximum_length=0, maximum_new_tokens=0, temperature=0.5, number_of_medias=0):
                    for index, media in enumerate(medias):
                        try:
                            _type, media, discrepant, inputs_media, position = media['type'], media['media'], False, {}, index+1
                            messages = messages_update(messages=messages, _type=_type, path=media)
                            formatted_prompt = self.__processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                            image_inputs, video_inputs = self.__sapiens_vision_processor(messages)
                            inputs_media = self.__processor(text=[formatted_prompt], images=image_inputs, videos=video_inputs, padding=True, return_tensors='pt').to(self.__model.device)
                            input_length = inputs_media['input_ids'].shape[1]
                            if input_length > maximum_length: discrepant = True
                            maximum_new_tokens = self.__get_maximum_new_tokens(maximum_length=maximum_length, input_length=input_length, maximum_new_tokens=maximum_new_tokens)
                            if discrepant:
                                messages, maximum_new_tokens = get_messages(maximum_length=maximum_length)
                                formatted_prompt = self.__processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                                image_inputs, video_inputs = self.__sapiens_vision_processor(messages)
                                inputs_media = self.__processor(text=[formatted_prompt], images=image_inputs, videos=video_inputs, padding=True, return_tensors='pt').to(self.__model.device)
                            def stream_all(number_of_medias=0):
                                for token in self.__token_generator(inputs=inputs_media, temperature=temperature, max_new_tokens=maximum_new_tokens): yield token
                                if position < number_of_medias: yield '\n\n'
                            yield from stream_all(number_of_medias=number_of_medias)
                        except: yield ''
                _generate_text = get_return(medias=medias, messages=messages, maximum_length=maximum_length, maximum_new_tokens=maximum_new_tokens, temperature=temperature, number_of_medias=number_of_medias)
                if stream: return _generate_text
                else:
                    for token in _generate_text: generated_text += token
                    return generated_text.strip()
            if self.__sapiens is not None:
                maximum_length = self.__sapiens._n_ctx
                encoding = self.__get_encoding()
                input_length = len(encoding.encode(str(messages)))
                maximum_new_tokens = self.__get_maximum_new_tokens(maximum_length=maximum_length, input_length=input_length, maximum_new_tokens=maximum_new_tokens)
                if input_length > maximum_length:
                    __system = system if len(system) > 0 else self.__system
                    if len(prompt) < 1: prompt = str(messages[-1]['content']).strip()
                    messages = [{'role': 'system', 'content': __system}] if __system else []
                    system_length = len(encoding.encode(__system))
                    tokens_limit = int(max(0, (maximum_length - system_length) - 68) / 2)
                    prompt = self.__divide_text_in_parts(prompt=prompt, tokens_limit=tokens_limit) if tokens_limit > 0 else ''
                    messages.append({'role': 'user', 'content': prompt})
                    maximum_new_tokens = tokens_limit
                if stream:
                    from threading import Thread
                    def token_generator(maximum_new_tokens=512):
                        def generate_tokens(maximum_new_tokens=512):
                            from traceback import print_exc
                            try:
                                try: create_chat_completion = self.__sapiens.create_chat_completion(messages=messages, temperature=temperature, max_tokens=maximum_new_tokens*2, stop=['Q:'], stream=True)
                                except: create_chat_completion = self.__sapiens.create_chat_completion(messages=messages, temperature=temperature, max_tokens=self.__max_new_tokens*2, stop=['Q:'], stream=True)
                                stop, total_tokens = False, 0
                                if self.__max_new_tokens != 512: maximum_new_tokens = min(self.__max_new_tokens, maximum_new_tokens if maximum_new_tokens else 256)
                                for token in create_chat_completion:
                                    if stop: break
                                    choices = token['choices'] if 'choices' in token else []
                                    choices_0 = choices[0] if len(choices) > 0 else {}
                                    token = choices_0['text'] if 'text' in choices_0 else ''
                                    if len(token) < 1 and 'delta' in choices_0:
                                        try: token = choices_0['delta'].get('content', '')
                                        except: break
                                    if maximum_new_tokens and total_tokens >= maximum_new_tokens:
                                        cut_before_punctuation = self.__cut_before_punctuation(text=token)
                                        if cut_before_punctuation != token or token.strip().endswith(('.', ';', '!', '?', '\n')): token, stop = cut_before_punctuation.rstrip(), True
                                    total_tokens += 1
                                    yield token.lstrip() if total_tokens <= 1 else token
                            except: return ''
                        thread = Thread(target=generate_tokens, args=(maximum_new_tokens,))
                        thread.start()
                        try:
                            for token in generate_tokens(maximum_new_tokens=maximum_new_tokens): yield token
                        except: return ''
                        thread.join()
                    return token_generator(maximum_new_tokens=maximum_new_tokens)
                else:
                    try: response = self.__sapiens.create_chat_completion(messages=messages, temperature=temperature, max_tokens=maximum_new_tokens, stop=['Q:'])
                    except: response = self.__sapiens.create_chat_completion(messages=messages, temperature=temperature, max_tokens=self.__max_new_tokens, stop=['Q:'])
                    choices = response['choices'] if 'choices' in response else []
                    choices_0 = choices[0] if len(choices) > 0 else {}
                    full_text = choices_0['text'] if 'text' in choices_0 else ''
                    if len(full_text) < 1 and 'message' in choices_0:
                        message = choices_0['message']
                        if 'content' in message: full_text = message['content'].strip()
                    return self.__eliminates_unnecessary_texts(text=full_text).strip()
            if self.__tokenizer is not None:
                from sapiens_transformers.adaptations import NAME014, NAME013
                if self.__ARCHITECTURE in (NAME013, NAME014):
                    if messages and 'system' in list(messages[0].values()):
                        _system_ = str(messages[0].get('content', '')).strip()
                        if len(messages) > 1 and 'user' in list(messages[-1].values()):
                            _prompt_ = str(messages[-1].get('content', '')).strip()
                            messages = messages[1:]
                            messages[-1]['content'] = _system_+'\n\n# QUESTION\n---\n'+_prompt_
                text = self.__tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                model_inputs = self.__tokenizer([text], return_tensors='pt').to(self.__model.device)
                maximum_length = self.CONTEXT_SIZE
                input_length = model_inputs.input_ids.shape[1]
                length_limit = maximum_length - input_length
                if maximum_new_tokens is None: maximum_new_tokens = length_limit
                else: maximum_new_tokens = min(maximum_new_tokens, length_limit)
                maximum_new_tokens = max(256, maximum_new_tokens)
                if input_length > maximum_length:
                    __system = system if len(system) > 0 else self.__system
                    if len(prompt) < 1: prompt = str(messages[-1]['content']).strip()
                    messages = [{'role': 'system', 'content': __system}]
                    system_text = self.__tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                    system_inputs = self.__tokenizer([system_text], return_tensors='pt').to(self.__model.device)
                    system_length = system_inputs.input_ids.shape[1]
                    tokens_limit = int(max(0, (maximum_length - system_length) - 68) / 2)
                    prompt = self.__divide_text_in_parts(prompt=prompt, tokens_limit=tokens_limit) if tokens_limit > 0 else ''
                    messages.append({'role': 'user', 'content': prompt})
                    text = self.__tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                    model_inputs = self.__tokenizer([text], return_tensors='pt').to(self.__model.device)
                    maximum_new_tokens = tokens_limit
                if stream:
                    from sapiens_transformers import TextIteratorStreamer
                    from threading import Thread
                    def token_generator(maximum_new_tokens=512):
                        try:
                            streamer = TextIteratorStreamer(self.__tokenizer, skip_special_tokens=True, skip_prompt=True)
                            def generate_tokens(maximum_new_tokens=512):
                                try: self.__model.generate(**model_inputs, temperature=temperature, max_new_tokens=maximum_new_tokens*2,
                                do_sample=True, return_dict_in_generate=True, return_legacy_cache=True, streamer=streamer, eos_token_id=self.__eos_token_id)
                                except: self.__model.generate(**model_inputs, temperature=temperature, max_new_tokens=self.__max_new_tokens*2,
                                do_sample=True, return_dict_in_generate=True, return_legacy_cache=True, streamer=streamer, eos_token_id=self.__eos_token_id)
                            thread = Thread(target=generate_tokens, args=(maximum_new_tokens,))
                            thread.start()
                            stop, total_tokens = False, 0
                            if self.__max_new_tokens != 512: maximum_new_tokens = min(self.__max_new_tokens, maximum_new_tokens if maximum_new_tokens else 256)
                            for token in streamer:
                                if stop: break
                                if maximum_new_tokens and total_tokens >= maximum_new_tokens:
                                    cut_before_punctuation = self.__cut_before_punctuation(text=token)
                                    if cut_before_punctuation != token or token.strip().endswith(('.', ';', '!', '?', '\n')): token, stop = cut_before_punctuation.rstrip(), True
                                total_tokens += 1
                                if total_tokens <= 1 and token.startswith(':'): token = ''
                                yield token.lstrip() if total_tokens <= 1 else token
                            thread.join()
                        except: yield ''
                    return token_generator(maximum_new_tokens=maximum_new_tokens)
                else:
                    try: generated_ids = self.__model.generate(**model_inputs, temperature=temperature, max_new_tokens=maximum_new_tokens, do_sample=True, eos_token_id=self.__eos_token_id)
                    except: generated_ids = self.__model.generate(**model_inputs, temperature=temperature, max_new_tokens=self.__max_new_tokens, do_sample=True, eos_token_id=self.__eos_token_id)
                    generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)]
                    response = self.__tokenizer.batch_decode(generated_ids, skip_special_tokens=True, skip_prompt=True)[0]
                    return self.__eliminates_unnecessary_texts(text=response).strip()
            else:
                print('Non-existent path: '+self.__original_model_path)
                print('The path to the model tokenizer does not exist.')
                return ''
        except Exception as error:
            if self.__show_errors: print('ERROR in SapiensModel.generate_text: '+str(error))
            return ''
    def generate_image(self, prompt='', width=512, height=512, fidelity_to_the_prompt=None, precision=None, seed=None, path=''):
        result = False
        try:
            prompt = prompt.strip() if type(prompt) == str else str(prompt).strip()
            if len(prompt) < 1: prompt = 'Create an image.'
            width = max((100, int(width))) if type(width) in (int, float) else 512
            height = max((100, int(height))) if type(height) in (int, float) else 512
            from sapiens_transformers.adaptations import SAPI_PHOTOGEN_COMPATIBILITY, SAPI_IMAGEGEN_COMPATIBILITY, SAPIENS_IMAGEGEN_COMPATIBILITY
            ARCHITECTURE = self.__ARCHITECTURE
            default_fidelity_to_the_prompt = {SAPI_PHOTOGEN_COMPATIBILITY[0]: 0.5, SAPI_IMAGEGEN_COMPATIBILITY[0]: 0.045, SAPIENS_IMAGEGEN_COMPATIBILITY[0]: 0.045}
            default_fidelity_to_the_prompt = default_fidelity_to_the_prompt[ARCHITECTURE] if ARCHITECTURE in default_fidelity_to_the_prompt else 0.5
            fidelity_to_the_prompt = min((1, max((0.01, float(fidelity_to_the_prompt))))) if type(fidelity_to_the_prompt) in (int, float) else default_fidelity_to_the_prompt
            fidelity_to_the_prompt *= 100
            default_precision = {SAPI_PHOTOGEN_COMPATIBILITY[0]: 0.5, SAPI_IMAGEGEN_COMPATIBILITY[0]: 0.4, SAPIENS_IMAGEGEN_COMPATIBILITY[0]: 0.2}
            default_precision = default_precision[ARCHITECTURE] if ARCHITECTURE in default_precision else 0.5
            precision = min((1, max((0.01, float(precision))))) if type(precision) in (int, float) else default_precision
            precision *= 100
            seed = max((0, int(seed))) if type(seed) in (int, float) else None
            path = path.strip() if type(path) == str else str(path).strip()
            if len(path) < 1: path = './IMAGE.png'
            extension = str(self.__path.splitext(path)[1]).strip()
            if len(extension) < 1: path += '.png'
            from torch import Generator
            from random import randint
            seed = Generator(self.__model.device).manual_seed(randint(0, 2**32 - 1) if seed is None else seed)
            negative_prompt = 'ugly, cropped, blurry, low-quality, mediocre average'
            image = self.__model(prompt, negative_prompt=negative_prompt, width=width, height=height, guidance_scale=fidelity_to_the_prompt, num_inference_steps=int(precision), max_sequence_length=512, generator=seed).images[0]
            image = image.convert('RGBA')
            image.save(path, format='PNG')
            result = True
        except Exception as error:
            if self.__show_errors: print('ERROR in SapiensModel.generate_image: '+str(error))
            result = False
        finally:
            self.__set_tqdm(disable=False)
            return result
    def generate_base64_image(self, prompt='', width=512, height=512, fidelity_to_the_prompt=None, precision=None, seed=None):
        result = ''
        try:
            from tempfile import NamedTemporaryFile
            with NamedTemporaryFile(suffix='.png', delete=False) as temporary_file: image_path = temporary_file.name
            _generate_image = self.generate_image(prompt=prompt, width=width, height=height, fidelity_to_the_prompt=fidelity_to_the_prompt, precision=precision, seed=seed, path=image_path)
            result = self.__file_to_base64(state=_generate_image, path=image_path)
        except Exception as error:
            if self.__show_errors: print('ERROR in SapiensModel.generate_base64_image: '+str(error))
            result = ''
        finally:
            self.__set_tqdm(disable=False)
            return result
    def generate_audio(self, prompt='', voice_file_path='', language='en', path=''):
        result = False
        try:
            prompt = prompt.strip() if type(prompt) == str else str(prompt).strip()
            voice_file_path = voice_file_path.strip() if type(voice_file_path) == str else str(voice_file_path).strip()
            if len(voice_file_path) < 1 and len(self.__audios) > 0: voice_file_path = self.__audios[0]
            language = language.lower().strip() if type(language) == str else str(language).lower().strip()
            path = path.strip() if type(path) == str else str(path).strip()
            if len(path) < 1: path = './VOICE.wav'
            extension = str(self.__path.splitext(path)[1]).strip()
            if len(extension) < 1: path += '.wav'
            self.__model.text_to_speech(text=prompt, voice_file_path=voice_file_path, output_path=path, language=language)
            if self.__downloaded: self.__delete_media(media_file_path=voice_file_path)
            result = True
        except Exception as error:
            if self.__show_errors: print('ERROR in SapiensModel.generate_audio: '+str(error))
            result = False
        finally:
            self.__set_tqdm(disable=False)
            return result
    def generate_base64_audio(self, prompt='', voice_file_path='', language='en'):
        result = ''
        try:
            from tempfile import NamedTemporaryFile
            with NamedTemporaryFile(suffix='.wav', delete=False) as temporary_file: voice_path = temporary_file.name
            _generate_voice = self.generate_audio(prompt=prompt, voice_file_path=voice_file_path, language=language, path=voice_path)
            result = self.__file_to_base64(state=_generate_voice, path=voice_path)
        except Exception as error:
            if self.__show_errors: print('ERROR in SapiensModel.generate_base64_audio: '+str(error))
            result = ''
        finally:
            self.__set_tqdm(disable=False)
            return result
    def generate_music(self, prompt='', duration_seconds=5, fidelity_to_the_prompt=None, path=''):
        result = False
        try:
            prompt = prompt.strip() if type(prompt) == str else str(prompt).strip()
            if len(prompt) < 1: prompt = 'Create an music.'
            duration_seconds = max((2, int(duration_seconds))) if type(duration_seconds) in (int, float) else 5
            fidelity_to_the_prompt = min((1, max((0.01, float(fidelity_to_the_prompt))))) if type(fidelity_to_the_prompt) in (int, float) else 0.5
            fidelity_to_the_prompt *= 100
            path = path.strip() if type(path) == str else str(path).strip()
            if len(path) < 1: path = './MUSIC.wav'
            extension = str(self.__path.splitext(path)[1]).strip()
            if len(extension) < 1: path += '.wav'
            inputs = self.__processor(text=[prompt], padding=True, return_tensors='pt').to(self.__model.device)
            sampling_rate, tokens_per_second = self.__model.config.audio_encoder.sampling_rate, 50
            max_new_tokens = duration_seconds * tokens_per_second
            audio_values = self.__model.generate(**inputs, guidance_scale=fidelity_to_the_prompt, max_new_tokens=max_new_tokens)
            from scipy import io
            io.wavfile.write(path, rate=sampling_rate, data=audio_values[0, 0].cpu().numpy())
            result = True
        except Exception as error:
            if self.__show_errors: print('ERROR in SapiensModel.generate_music: '+str(error))
            result = False
        finally:
            self.__set_tqdm(disable=False)
            return result
    def generate_base64_music(self, prompt='', duration_seconds=5, fidelity_to_the_prompt=None):
        result = ''
        try:
            from tempfile import NamedTemporaryFile
            with NamedTemporaryFile(suffix='.wav', delete=False) as temporary_file: music_path = temporary_file.name
            _generate_music = self.generate_music(prompt=prompt, duration_seconds=duration_seconds, fidelity_to_the_prompt=fidelity_to_the_prompt, path=music_path)
            result = self.__file_to_base64(state=_generate_music, path=music_path)
        except Exception as error:
            if self.__show_errors: print('ERROR in SapiensModel.generate_base64_music: '+str(error))
            result = ''
        finally:
            self.__set_tqdm(disable=False)
            return result
    def generate_video(self, prompt='', width=512, height=512, fidelity_to_the_prompt=None, precision=None, fps=None, number_of_frames=None, seed=None, path='', progress=False):
        result = False
        try:
            prompt = prompt.strip() if type(prompt) == str else str(prompt).strip()
            if len(prompt) < 1: prompt = 'Create an video.'
            width = max((128, int(width))) if type(width) in (int, float) else 512
            height = max((128, int(height))) if type(height) in (int, float) else 512
            if width != 512 or height != 512:
                def convert_to_multiple_of_128(number=128):
                    from math import ceil
                    if number < 128: return 128
                    return ceil(number / 128) * 128
                width, height = convert_to_multiple_of_128(number=width), convert_to_multiple_of_128(number=height)
            from sapiens_transformers.adaptations import SAPI_VIDEOGEN_COMPATIBILITY, SAPIENS_VIDEOGEN_COMPATIBILITY, ALLEGRO_COMPATIBILITY
            ARCHITECTURE = self.__ARCHITECTURE
            default_fidelity_to_the_prompt = {SAPI_VIDEOGEN_COMPATIBILITY[0]: 0.01, SAPIENS_VIDEOGEN_COMPATIBILITY[0]: 0.01, ALLEGRO_COMPATIBILITY: 0.075}
            default_fidelity_to_the_prompt = default_fidelity_to_the_prompt[ARCHITECTURE] if ARCHITECTURE in default_fidelity_to_the_prompt else 0.01
            fidelity_to_the_prompt = min((1, max((0.01, float(fidelity_to_the_prompt))))) if type(fidelity_to_the_prompt) in (int, float) else default_fidelity_to_the_prompt
            fidelity_to_the_prompt *= 100
            default_precision = {SAPI_VIDEOGEN_COMPATIBILITY[0]: 0.04, SAPIENS_VIDEOGEN_COMPATIBILITY[0]: 0.5, ALLEGRO_COMPATIBILITY: 1}
            default_precision = default_precision[ARCHITECTURE] if ARCHITECTURE in default_precision else 0.04
            precision = min((1, max((0.01, float(precision))))) if type(precision) in (int, float) else default_precision
            precision *= 100
            default_fps = {SAPI_VIDEOGEN_COMPATIBILITY[0]: 10, SAPIENS_VIDEOGEN_COMPATIBILITY[0]: 24, ALLEGRO_COMPATIBILITY: 15}
            default_fps = default_fps[ARCHITECTURE] if ARCHITECTURE in default_fps else 10
            fps = max((1, int(fps))) if type(fps) in (int, float) else default_fps
            number_of_frames = max((10, int(number_of_frames))) if type(number_of_frames) in (int, float) else 161
            seed = max((0, int(seed))) if type(seed) in (int, float) else None
            if seed is not None:
                from torch import Generator
                from random import randint
                seed = Generator(self.__model.device).manual_seed(randint(0, 2**32 - 1) if seed is None else seed)
            path = path.strip() if type(path) == str else str(path).strip()
            if len(path) < 1: path = './VIDEO.mp4'
            extension = str(self.__path.splitext(path)[1]).strip()
            if len(extension) < 1: path += '.mp4'
            progress = bool(progress) if type(progress) in (bool, int, float) else False
            self.__set_tqdm(disable=not progress)
            from logging import getLogger, ERROR
            getLogger('moviepy').setLevel(ERROR)
            if ARCHITECTURE == SAPIENS_VIDEOGEN_COMPATIBILITY[0]:
                negative_prompt = 'worst quality, inconsistent motion, blurry, jittery, distorted'
                if self.__images is not None and len(self.__images) > 0:
                    if seed is not None: video = self.__model(image=self.__images[0], prompt=prompt, negative_prompt=negative_prompt, width=width, height=height, num_inference_steps=int(precision), num_frames=number_of_frames, generator=seed).frames[0]
                    else: video = self.__model(image=self.__images[0], prompt=prompt, negative_prompt=negative_prompt, width=width, height=height, num_inference_steps=int(precision), num_frames=number_of_frames).frames[0]
                else:
                    if seed is not None: video = self.__model(prompt=prompt, negative_prompt=negative_prompt, width=width, height=height, num_inference_steps=int(precision), num_frames=number_of_frames, generator=seed).frames[0]
                    else: video = self.__model(prompt=prompt, negative_prompt=negative_prompt, width=width, height=height, num_inference_steps=int(precision), num_frames=number_of_frames).frames[0]                    
                self.__export_to_video(video, path, fps=fps)
                result = True
            elif ARCHITECTURE == ALLEGRO_COMPATIBILITY:
                prompt = prompt.format(prompt.lower().strip())
                negative_prompt = 'nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry'
                if seed is not None: video = self.__model(prompt, negative_prompt=negative_prompt, width=width, height=height, guidance_scale=fidelity_to_the_prompt, max_sequence_length=512, num_inference_steps=int(precision), generator=seed).frames[0]
                else: video = self.__model(prompt, negative_prompt=negative_prompt, width=width, height=height, guidance_scale=fidelity_to_the_prompt, max_sequence_length=512, num_inference_steps=int(precision)).frames[0]
                self.__export_to_video(video, path, fps=fps)
                result = True
            else:
                from os import devnull
                with open(devnull, 'w') as _devnull:
                    from contextlib import redirect_stdout
                    with redirect_stdout(_devnull):
                        if seed is not None: output = self.__model(prompt=prompt, width=width, height=height, guidance_scale=fidelity_to_the_prompt, num_inference_steps=int(precision), generator=seed)
                        else: output = self.__model(prompt=prompt, width=width, height=height, guidance_scale=fidelity_to_the_prompt, num_inference_steps=int(precision))
                        from numpy import array
                        frames = [array(frame) for frame in output.frames[0]]
                        try: from moviepy import ImageSequenceClip
                        except: from moviepy.editor import ImageSequenceClip
                        clip = ImageSequenceClip(frames, fps=fps)
                        try: clip.write_videofile(path, codec='libx264', fps=fps)
                        except: clip.write_videofile(path, codec='mpeg4', fps=fps)
                result = True
        except Exception as error:
            if self.__show_errors: print('ERROR in SapiensModel.generate_video: '+str(error))
            result = False
        finally:
            self.__set_tqdm(disable=False)
            return result
    def generate_base64_video(self, prompt='', width=512, height=512, fidelity_to_the_prompt=None, precision=None, fps=None, number_of_frames=None, seed=None, progress=False):
        result = ''
        try:
            from tempfile import NamedTemporaryFile
            with NamedTemporaryFile(suffix='.mp4', delete=False) as temporary_file: video_path = temporary_file.name
            _generate_video = self.generate_video(prompt=prompt, width=width, height=height, fidelity_to_the_prompt=fidelity_to_the_prompt, precision=precision, fps=fps, number_of_frames=number_of_frames, seed=seed, path=video_path, progress=progress)
            result = self.__file_to_base64(state=_generate_video, path=video_path)
        except Exception as error:
            if self.__show_errors: print('ERROR in SapiensModel.generate_base64_video: '+str(error))
            result = ''
        finally:
            self.__set_tqdm(disable=False)
            return result
    def print_template_text(self, system='', prompt='', temperature=0.5, max_new_tokens=None, stream=False, sleep=0):
        try:
            stream = bool(stream) if type(stream) in (bool, int, float) else False
            sleep = max((0, float(sleep))) if type(sleep) in (int, float) else 0
            _generate_text = self.generate_template_text(system=system, prompt=prompt, temperature=temperature, max_new_tokens=max_new_tokens, stream=stream)
            if stream:
                from time import sleep as _sleep
                for token in _generate_text:
                    print(token, end='', flush=True)
                    if sleep > 0: _sleep(sleep)
                print()
            else: print(_generate_text)
        except Exception as error:
            if self.__show_errors: print('ERROR in SapiensModel.print_template_text: '+str(error))
    def print_text(self, system='', prompt='', messages=[], temperature=0.5, max_new_tokens=None, stream=False, sleep=0):
        try:
            stream = bool(stream) if type(stream) in (bool, int, float) else False
            sleep = max((0, float(sleep))) if type(sleep) in (int, float) else 0
            _generate_text = self.generate_text(system=system, prompt=prompt, messages=messages, temperature=temperature, max_new_tokens=max_new_tokens, stream=stream)
            if stream:
                from time import sleep as _sleep
                for token in _generate_text:
                    print(token, end='', flush=True)
                    if sleep > 0: _sleep(sleep)
                print()
            else: print(_generate_text)
        except Exception as error:
            if self.__show_errors: print('ERROR in SapiensModel.print_text: '+str(error))
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
