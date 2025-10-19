"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
class Training():
	def __init__(self, base_model_path='', dataset_path='', dataset_string=None, progress=True, show_errors=True):
		try:
			self.__loaded_class = False
			model_path = base_model_path.strip() if type(base_model_path) == str else str(base_model_path).strip()
			dataset_path = dataset_path.strip() if type(dataset_path) == str else str(dataset_path).strip()
			dataset_string = rf'{dataset_string}'.strip() if type(dataset_string) == str else None
			progress = bool(progress) if type(progress) in (bool, int, float) else True
			self.__show_errors = bool(show_errors) if type(show_errors) in (bool, int, float) else True
			if not dataset_path.endswith('.json') and not dataset_path.endswith('.txt') and not dataset_string:
				if self.__show_errors: print('The training only accepts datasets in JSON or TXT formats.')
				return None
			from sapiens_transformers.utils.functions import (set_tqdm, update_tqdm, model_conversion, find_config_or_model_index, set_model_type,
			get_dataset_from_file, get_configuration_path, copy_and_overwrite_file, back_model_type)
			from logging import getLogger, WARNING, ERROR, disable, CRITICAL
			from torch import cuda, device, backends
			from sapiens_transformers.adaptations import STATE1X, STATE2X, STATE1Y, STATE2Y
			from sapiens_transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
			from sapiens_transformers import default_data_collator
			from os import environ, path
			from sapiens_transformers.adaptations import NAME068
			set_tqdm(disable=not progress)
			progress_bar = update_tqdm(total=4, description='Loading model')
			progress_bar.update(1)
			getLogger('sapiens_transformers').setLevel(WARNING)
			getLogger('sapiens_transformers').setLevel(ERROR)
			getLogger('datasets').setLevel(WARNING)
			getLogger('datasets').setLevel(ERROR)
			disable(CRITICAL)
			if cuda.is_available(): local_device = device('cuda')
			elif backends.mps.is_available():
				local_device = device('mps')
				environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'
			else: local_device = device('cpu')
			saf_model_conversion, bin_model_conversion, change_json = False, False, False
			saf_model_conversion = model_conversion(sapiens_path=model_path, to=STATE1X)
			bin_model_conversion = model_conversion(sapiens_path=model_path, to=STATE2X)
			model_path = find_config_or_model_index(model_path=model_path)
			change_json = set_model_type(model_path=model_path)
			progress_bar.update(1)
			try:
				model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype='auto').to(local_device)
				progress_bar.update(1)
				tokenizer = AutoTokenizer.from_pretrained(model_path)
				progress_bar.update(1)
				progress_bar.close()
			except:
				print('This model is not compatible for training.')
				model, tokenizer = None, None
				self.__loaded_class = None
			finally:
				progress_bar.n = 4
				progress_bar.refresh()
				progress_bar.close()
			set_tqdm(disable=True)
			if saf_model_conversion: model_conversion(sapiens_path=model_path, to=STATE1Y)
			if bin_model_conversion: model_conversion(sapiens_path=model_path, to=STATE2Y)
			dataset = get_dataset_from_file(file_path=dataset_path, string_content=dataset_string)
			configuration_path = get_configuration_path(model_path=model_path)
			self.__NAME068 = NAME068
			self.__default_epochs = len(dataset['train']) * 2
			self.__tokenizer, self.__model = tokenizer, model
			self.__set_tqdm, self.__progress = set_tqdm, progress
			self.__dataset, self.__TrainingArguments = dataset, TrainingArguments
			self.__local_device, self.__Trainer = local_device, Trainer
			self.__default_data_collator, self.__path, self.__configuration_path = default_data_collator, path, configuration_path
			self.__saf_model_conversion, self.__model_conversion = saf_model_conversion, model_conversion
			self.__STATE1Y, self.__STATE2Y = STATE1Y, STATE2Y
			self.__bin_model_conversion = bin_model_conversion
			self.__change_json, self.__back_model_type = change_json, back_model_type
			self.__model_path, self.__copy_and_overwrite_file = model_path, copy_and_overwrite_file
			if self.__loaded_class is not None: self.__loaded_class = True
			set_tqdm(disable=False)
		except Exception as error:
			if self.__show_errors: print('ERROR in Training.__init__: '+str(error))
			self.__loaded_class = False
	def train(self, precision=0.1, epochs=None, output_path='', system=''):
		try:
			if not self.__loaded_class: return 1.0
			train_loss, precision = 1.0, min((1.0, max((0.0, float(precision))))) if type(precision) in (bool, int, float) else 0.1
			epochs = max((1, int(epochs))) if type(epochs) in (bool, int, float) else None
			output_path = output_path.strip() if type(output_path) == str else ''
			system_instruction = rf'{system}'.strip() if type(system) == str else ''
			if len(system_instruction) < 1: system_instruction = self.__NAME068
			if epochs is None: epochs = self.__default_epochs
			if len(output_path) < 1: output_path = './sapiens_model'
			try: eos_token = self.__tokenizer.eos_token
			except: eos_token = self.__tokenizer.convert_ids_to_tokens([self.__tokenizer.eos_token_id])
			max_length = self.__model.config.max_position_embeddings
			self.__set_tqdm(disable=not self.__progress)
			def tokenize_function_json(dataset={}):
				formatted_texts = [f'system: {system_instruction} user: {_input} assistant: {_output}{eos_token}' for _input, _output in zip(dataset['input'], dataset['output'])]
				tokenized = self.__tokenizer(formatted_texts, truncation=True, padding='longest', max_length=max_length)
				tokenized['labels'] = tokenized['input_ids'].copy()
				tokenized['labels'] = [[-100 if token == self.__tokenizer.pad_token_id else token for token in label] for label in tokenized['labels']]
				return tokenized
			def __adjust_hyperparameters(precision=0.1):
				precision = min((1.0, max((0.0, int(precision))))) if type(precision) in (bool, int, float) else 0.1
				return {'per_device_train_batch_size': int(4 + precision * (128 - 4)), 'gradient_accumulation_steps': int(8 + precision * (64 - 8)),
				'learning_rate': 0.0001 + precision * (0.001 - 0.0001), 'weight_decay': precision * 0.1}
			hyperparameters = __adjust_hyperparameters(precision=precision)
			tokenized_datasets = self.__dataset.map(tokenize_function_json, batched=True)
			per_device_train_batch_size, gradient_accumulation_steps = hyperparameters['per_device_train_batch_size'], hyperparameters['gradient_accumulation_steps']
			learning_rate, weight_decay = hyperparameters['learning_rate'], hyperparameters['weight_decay']
			from sapiens_transformers import TrainerCallback
			class TrainLossCallback(TrainerCallback):
				def __init__(self): self.train_loss = 1.0
				def on_log(self, args=None, state=None, control=None, logs=None, **kwargs):
					if logs and 'train_loss' in logs: self.train_loss = float(logs["train_loss"])
			from tqdm.auto import tqdm
			class ProgressBarCallback(TrainerCallback):
				def __init__(self, total_epochs=1): self.total_epochs, self.progress_bar = total_epochs, None
				def on_train_begin(self, args=None, state=None, control=None, **kwargs): self.progress_bar = tqdm(total=self.total_epochs, desc='Training Progress', unit=' step')
				def on_epoch_end(self, args=None, state=None, control=None, **kwargs): self.progress_bar.update(1)
				def on_train_end(self, args=None, state=None, control=None, **kwargs):
					self.progress_bar.n = self.total_epochs
					self.progress_bar.refresh()
					self.progress_bar.close()
			train_loss_callback = TrainLossCallback()
			training_arguments = self.__TrainingArguments(output_dir=output_path, per_device_train_batch_size=per_device_train_batch_size, gradient_accumulation_steps=gradient_accumulation_steps,
			num_train_epochs=epochs, learning_rate=learning_rate, weight_decay=weight_decay, fp16=self.__local_device=='cuda', report_to='none', logging_strategy='no', save_strategy='no', disable_tqdm=True)			
			trainer = self.__Trainer(model=self.__model, args=training_arguments, train_dataset=tokenized_datasets['train'], tokenizer=self.__tokenizer, data_collator=self.__default_data_collator)
			trainer.add_callback(ProgressBarCallback(epochs))
			trainer.add_callback(train_loss_callback)
			import sys
			from io import StringIO
			old_stdout = sys.stdout
			sys.stdout = StringIO()
			trainer.train()
			sys.stdout = old_stdout
			train_loss = train_loss_callback.train_loss
			trainer.save_model(output_path)
			self.__tokenizer.save_pretrained(output_path)
			destination_path = self.__path.join(output_path, self.__path.basename(self.__configuration_path))
			if self.__saf_model_conversion: self.__model_conversion(sapiens_path=output_path, to=self.__STATE1Y)
			if self.__bin_model_conversion: self.__model_conversion(sapiens_path=output_path, to=self.__STATE2Y)
			if self.__change_json: self.__back_model_type(model_path=self.__model_path, change_json=self.__change_json)
			self.__set_tqdm(disable=False)
			return train_loss if self.__copy_and_overwrite_file(source_path=self.__configuration_path, destination_path=destination_path) else 1.0
		except Exception as error:
			if self.__show_errors: print('ERROR in Training.train: '+str(error))
			if self.__saf_model_conversion: self.__model_conversion(sapiens_path=self.__model_path, to=self.__STATE1Y)
			if self.__bin_model_conversion: self.__model_conversion(sapiens_path=self.__model_path, to=self.__STATE2Y)
			if self.__change_json: self.__back_model_type(model_path=self.__model_path, change_json=self.__change_json)
			self.__set_tqdm(disable=False)
			return 1.0
class FineTuning():
	def __init__(self, model_path='', output_path='', dataset_path='', progress=True, show_errors=True):
		try:
			self.__loaded_class = False
			model_path = model_path.strip() if type(model_path) == str else str(model_path).strip()
			output_path = output_path.strip() if type(output_path) == str else ''
			dataset_path = dataset_path.strip() if type(dataset_path) == str else str(dataset_path).strip()
			progress = bool(progress) if type(progress) in (bool, int, float) else True
			self.__show_errors = bool(show_errors) if type(show_errors) in (bool, int, float) else True
			if not output_path: output_path = './sapiens_adjusted'
			if not model_path: model_path = output_path
			from sapiens_transformers.utils.functions import (set_tqdm, update_tqdm, model_conversion, find_config_or_model_index,
			set_model_type, get_configuration_path, copy_and_overwrite_file, back_model_type)
			from logging import getLogger, WARNING, ERROR, disable, CRITICAL
			from torch import cuda, device, backends
			from os import environ
			from sapiens_transformers.adaptations import STATE1X, STATE2X, STATE1Y, STATE2Y
			from sapiens_transformers import AutoModelForCausalLM, AutoTokenizer
			set_tqdm(disable=not progress)
			progress_bar = update_tqdm(total=4, description='Loading model')
			progress_bar.update(1)
			getLogger('sapiens_transformers').setLevel(WARNING)
			getLogger('sapiens_transformers').setLevel(ERROR)
			getLogger('datasets').setLevel(WARNING)
			getLogger('datasets').setLevel(ERROR)
			disable(CRITICAL)
			if cuda.is_available(): local_device = device('cuda')
			elif backends.mps.is_available():
				local_device = device('mps')
				environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'
			else: local_device = device('cpu')
			saf_model_conversion, bin_model_conversion, change_json = False, False, False
			saf_model_conversion = model_conversion(sapiens_path=model_path, to=STATE1X)
			bin_model_conversion = model_conversion(sapiens_path=model_path, to=STATE2X)
			model_path = find_config_or_model_index(model_path=model_path)
			change_json = set_model_type(model_path=model_path)
			progress_bar.update(1)
			try:
				model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype='auto').to(local_device)
				progress_bar.update(1)
				tokenizer = AutoTokenizer.from_pretrained(model_path)
				progress_bar.update(1)
				progress_bar.close()
			except:
				print('This model is not compatible for fine-tuning.')
				model, tokenizer = None, None
				self.__loaded_class = None
			finally:
				progress_bar.n = 4
				progress_bar.refresh()
				progress_bar.close()
			set_tqdm(disable=True)
			if saf_model_conversion: model_conversion(sapiens_path=model_path, to=STATE1Y)
			if bin_model_conversion: model_conversion(sapiens_path=model_path, to=STATE2Y)
			self.__it_is_a_temporary_file = False
			if not dataset_path:
				from tempfile import NamedTemporaryFile
				with NamedTemporaryFile(suffix='.json', delete=False) as temporary_file: dataset_path = temporary_file.name
				self.__it_is_a_temporary_file = True
			configuration_path = get_configuration_path(model_path=model_path)
			self.__progress, self.__set_tqdm = progress, set_tqdm
			self.__number_of_adjustments, self.__dataset_dictionary = 0, {'data': []}
			self.__dataset_path, self.__tokenizer, self.__model = dataset_path, tokenizer, model
			self.__output_path, self.__local_device = output_path, local_device
			self.__trainer, self.__configuration_path = None, configuration_path
			self.__saf_model_conversion, self.__model_conversion = saf_model_conversion, model_conversion
			self.__STATE1Y, self.__STATE2Y = STATE1Y, STATE2Y
			self.__bin_model_conversion, self.__change_json = bin_model_conversion, change_json
			self.__back_model_type, self.__model_path = back_model_type, model_path
			self.__copy_and_overwrite_file = copy_and_overwrite_file
			if self.__loaded_class is not None: self.__loaded_class = True
			set_tqdm(disable=False)
		except Exception as error:
			if self.__show_errors: print('ERROR in FineTuning.__init__: '+str(error))
			self.__loaded_class = False
	def addFit(self, Input='', Output=''):
		try:
			if not self.__loaded_class: return False
			Input = rf'{Input}'.strip() if type(Input) == str else rf'{str(Input).strip()}'
			Output = rf'{Output}'.strip() if type(Output) == str else rf'{str(Output).strip()}'
			if not self.__progress: self.__set_tqdm(disable=True)
			self.__number_of_adjustments += 1
			from sapiens_transformers.utils.functions import update_tqdm, get_dataset_from_file
			progress_bar = update_tqdm(total=5, description='Adding adjustment '+str(self.__number_of_adjustments))
			progress_bar.update(1)
			self.__dataset_dictionary['data'].append({'input': Input, 'output': Output})
			if self.__it_is_a_temporary_file:
				from json import dump
				with open(self.__dataset_path, 'w', encoding='utf-8') as file: dump(self.__dataset_dictionary, file)
			self.__set_tqdm(disable=True)
			dataset = get_dataset_from_file(file_path=self.__dataset_path)
			try: eos_token = self.__tokenizer.eos_token
			except: eos_token = self.__tokenizer.convert_ids_to_tokens([self.__tokenizer.eos_token_id])
			max_length = self.__model.config.max_position_embeddings
			default_epochs = min(100, len(self.__dataset_dictionary['data']) + 10)
			def tokenize_function_json(dataset={}):
				formatted_texts = [f'user: {_input} assistant: {_output}{eos_token}' for _input, _output in zip(dataset['input'], dataset['output'])]
				tokenized = self.__tokenizer(formatted_texts, truncation=True, padding='longest', max_length=max_length)
				tokenized['labels'] = tokenized['input_ids'].copy()
				tokenized['labels'] = [[-100 if token == self.__tokenizer.pad_token_id else token for token in label] for label in tokenized['labels']]
				return tokenized
			def __adjust_hyperparameters(precision=0.1):
				precision = min((1, max((0, int(precision))))) if type(precision) in (bool, int, float) else 0.1
				return {'per_device_train_batch_size': int(4 + precision * (128 - 4)), 'gradient_accumulation_steps': int(8 + precision * (64 - 8)),
				'learning_rate': 0.0001 + precision * (0.001 - 0.0001), 'weight_decay': precision * 0.1}
			tokenized_datasets = dataset.map(tokenize_function_json, batched=True)
			self.__set_tqdm(disable=not self.__progress)
			progress_bar.update(1)
			hyperparameters = __adjust_hyperparameters()
			per_device_train_batch_size, gradient_accumulation_steps = hyperparameters['per_device_train_batch_size'], hyperparameters['gradient_accumulation_steps']
			learning_rate, weight_decay = hyperparameters['learning_rate'], hyperparameters['weight_decay']
			progress_bar.update(1)
			from sapiens_transformers import TrainingArguments, Trainer
			training_arguments = TrainingArguments(output_dir=self.__output_path, per_device_train_batch_size=per_device_train_batch_size, gradient_accumulation_steps=gradient_accumulation_steps,
			num_train_epochs=default_epochs, learning_rate=learning_rate, weight_decay=weight_decay, fp16=self.__local_device=='cuda', report_to='none', logging_strategy='no', save_strategy='no', disable_tqdm=False)
			progress_bar.update(1)
			from sapiens_transformers import default_data_collator
			self.__trainer = Trainer(model=self.__model, args=training_arguments, train_dataset=tokenized_datasets['train'], tokenizer=self.__tokenizer, data_collator=default_data_collator)
			progress_bar.update(1)
			progress_bar.close()
			self.__set_tqdm(disable=not self.__progress)
			return True
		except Exception as error:
			if self.__show_errors: print('ERROR in FineTuning.addFit: '+str(error))
			self.__set_tqdm(disable=not self.__progress)
			return False
	def fit(self):
		try:
			if not self.__loaded_class: return 1.0
			if self.__it_is_a_temporary_file:
				from os import path, remove
				if path.exists(self.__dataset_path): remove(self.__dataset_path)
			else:
				from sapiens_transformers.utils.functions import get_dictionary_from_json
				dataset = get_dictionary_from_json(configuration_path=self.__dataset_path)
				for data in dataset['data']: self.addFit(Input=data['input'], Output=data['output'])
			from sapiens_transformers import TrainerCallback
			class TrainLossCallback(TrainerCallback):
				def __init__(self): self.train_loss = 1.0
				def on_log(self, args=None, state=None, control=None, logs=None, **kwargs):
					if logs and 'train_loss' in logs: self.train_loss = float(logs["train_loss"])
			train_loss_callback = TrainLossCallback()
			self.__trainer.add_callback(train_loss_callback)
			import sys
			from io import StringIO
			old_stdout = sys.stdout
			sys.stdout = StringIO()
			self.__trainer.train()
			sys.stdout = old_stdout
			train_loss = train_loss_callback.train_loss
			self.__trainer.save_model(self.__output_path)
			self.__tokenizer.save_pretrained(self.__output_path)
			from os import path
			destination_path = path.join(self.__output_path, path.basename(self.__configuration_path))
			if self.__saf_model_conversion: self.__model_conversion(sapiens_path=self.__output_path, to=self.__STATE1Y)
			if self.__bin_model_conversion: self.__model_conversion(sapiens_path=self.__output_path, to=self.__STATE2Y)
			if self.__change_json: self.__back_model_type(model_path=self.__model_path, change_json=self.__change_json)
			self.__set_tqdm(disable=not self.__progress)
			return train_loss if self.__copy_and_overwrite_file(source_path=self.__configuration_path, destination_path=destination_path) else 1.0
		except Exception as error:
			if self.__show_errors: print('ERROR in FineTuning.fit: '+str(error))
			if self.__saf_model_conversion: self.__model_conversion(sapiens_path=self.__output_path, to=self.__STATE1Y)
			if self.__bin_model_conversion: self.__model_conversion(sapiens_path=self.__output_path, to=self.__STATE2Y)
			if self.__change_json: self.__back_model_type(model_path=self.__model_path, change_json=self.__change_json)
			self.__set_tqdm(disable=not self.__progress)
			return 1.0
class ManualFineTuning():
	def __init__(self, per_device_train_batch_size=4, gradient_accumulation_steps=8, num_train_epochs=10, learning_rate=3e-5, weight_decay=0.01, logging_steps=1, fp16=False, bf16=False, disable_tqdm=False, max_grad_norm=1.0, progress=True, show_errors=True):
		try:
			self.__loaded_class = False
			self.__per_device_train_batch_size = int(per_device_train_batch_size) if type(per_device_train_batch_size) in (bool, int, float) else 4
			self.__gradient_accumulation_steps = int(gradient_accumulation_steps) if type(gradient_accumulation_steps) in (bool, int, float) else 8
			self.__num_train_epochs = int(num_train_epochs) if type(num_train_epochs) in (bool, int, float) else 10
			self.__save_strategy = 'no'
			self.__evaluation_strategy = 'no'
			self.__eval_strategy = 'no'
			self.__learning_rate = max(0.0, float(learning_rate)) if type(learning_rate) == float else 3e-5
			self.__weight_decay = max(0.0, float(weight_decay)) if type(weight_decay) == float else 0.01
			self.__logging_steps = max(1, int(logging_steps)) if type(logging_steps) in (bool, int, float) else 1
			self.__fp16 = bool(fp16) if type(fp16) in (bool, int, float) else False
			self.__bf16 = bool(bf16) if type(bf16) in (bool, int, float) else False
			self.__report_to = 'none'
			self.__disable_tqdm = bool(disable_tqdm) if type(disable_tqdm) in (bool, int, float) else False
			self.__max_grad_norm = max(0.0, float(max_grad_norm)) if type(max_grad_norm) == float else 1.0
			self.__progress = bool(progress) if type(progress) in (bool, int, float) else True
			self.__show_errors = bool(show_errors) if type(show_errors) in (bool, int, float) else True
			from warnings import filterwarnings
			from logging import getLogger, ERROR, disable, CRITICAL
			from torch import cuda, device, backends
			from os import environ, path
			from sapiens_transformers.adaptations import NAME068
			from sapiens_transformers.utils.functions import (find_config_or_model_index, model_conversion, set_model_type, back_model_type,
			get_configuration_path, get_dictionary_from_json, search_model_type, copy_and_overwrite_file)
			from sapiens_transformers.adaptations import STATE1X, STATE2X, STATE1Y, STATE2Y
			from sapiens_transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
			from datasets import load_dataset
			from sapiens_transformers import default_data_collator
			filterwarnings('ignore')
			getLogger('sapiens_transformers').setLevel(ERROR)
			getLogger('datasets').setLevel(ERROR)
			disable(CRITICAL)
			if cuda.is_available(): self.__local_device = device('cuda')
			elif backends.mps.is_available():
			    self.__local_device = device('mps')
			    environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'
			else: self.__local_device = device('cpu')
			self.__NAME068 = NAME068
			self.__path = path
			self.__find_config_or_model_index = find_config_or_model_index
			self.__model_conversion = model_conversion
			self.__set_model_type = set_model_type
			self.__back_model_type = back_model_type
			self.__get_configuration_path = get_configuration_path
			self.__get_dictionary_from_json = get_dictionary_from_json
			self.__search_model_type = search_model_type
			self.__copy_and_overwrite_file = copy_and_overwrite_file
			self.__STATE1X, self.__STATE2X, self.__STATE1Y, self.__STATE2Y = STATE1X, STATE2X, STATE1Y, STATE2Y
			self.__AutoModelForCausalLM, self.__AutoTokenizer, self.__TrainingArguments, self.__Trainer = AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
			self.__load_dataset = load_dataset
			self.__default_data_collator = default_data_collator
			self.__loaded_class = True
		except Exception as error:
			if self.__show_errors: print('ERROR in ManualFineTuning.__init__: '+str(error))
			self.__loaded_class = False
	def fit(self, model_path='', dataset_path='', output_path='', system=''):
		try:
			if not self.__loaded_class: return 1.0
			model_path = str(model_path).strip()
			dataset_path = str(dataset_path).strip()
			output_path = str(output_path).strip() if output_path else './ADJUSTED_MODEL'
			system = rf'{system}'.strip() if system else self.__NAME068
			if not self.__path.exists(model_path):
				if self.__show_errors: print(f'The path to the model {model_path} does not exist.')
				return 1.0
			if not self.__path.exists(model_path):
				if self.__show_errors: print(f'The path to the dataset {dataset_path} does not exist.')
				return 1.0
			if not dataset_path.endswith('.json'):
				if self.__show_errors: print('Manual adjustment only accepts datasets in JSON format.')
				return 1.0
			saf_model_conversion, bin_model_conversion, change_json = False, False, False
			model_path = self.__find_config_or_model_index(model_path=model_path)
			saf_model_conversion = self.__model_conversion(sapiens_path=model_path, to=self.__STATE1X)
			bin_model_conversion = self.__model_conversion(sapiens_path=model_path, to=self.__STATE2X)
			change_json = self.__set_model_type(model_path=model_path)
			try:
				model = self.__AutoModelForCausalLM.from_pretrained(model_path, torch_dtype='auto').to(self.__local_device)
				tokenizer = self.__AutoTokenizer.from_pretrained(model_path)
			except:
				print('This model is not compatible for manual fine-tuning.')
				model, tokenizer = None, None
				self.__loaded_class = None
				return 1.0
			if saf_model_conversion: self.__model_conversion(sapiens_path=model_path, to=self.__STATE1Y)
			if bin_model_conversion: self.__model_conversion(sapiens_path=model_path, to=self.__STATE2Y)
			if change_json: self.__back_model_type(model_path=model_path, change_json=change_json)
			if tokenizer.pad_token is None: tokenizer.pad_token = tokenizer.eos_token
			is_url = dataset_path.startswith(('http://', 'https://', 'www.'))
			if is_url:
				from sapiens_transformers.utils.functions import download_file
				dataset_path = download_file(url_path=dataset_path)
			dataset = self.__load_dataset('json', data_files={'train': dataset_path}, field='data')
			def tokenize_function(examples={}):
			    formatted_texts = [f'system: {system} user: {question} assistant: {answer}' for question, answer in zip(examples['input'], examples['output'])]
			    tokenized = tokenizer(formatted_texts, truncation=True, padding='longest', max_length=1024)
			    tokenized['labels'] = tokenized['input_ids'].copy()
			    tokenized['labels'] = [[-100 if token == tokenizer.pad_token_id else token for token in label] for label in tokenized['labels']]
			    return tokenized
			def tokenize_function_mistral(examples={}):
			    formatted_texts = []
			    for question, answer in zip(examples['input'], examples['output']):
			        formatted_text = f"<s>[INST] <<SYS>>\n{system}\n<</SYS>>\n\n{question} [/INST] {answer}</s>"
			        formatted_texts.append(formatted_text)
			    tokenized = tokenizer(formatted_texts, truncation=True, padding='longest', max_length=1024)
			    tokenized['labels'] = tokenized['input_ids'].copy()
			    tokenized['labels'] = [[-100 if token == tokenizer.pad_token_id else token for token in label] for label in tokenized['labels']]
			    return tokenized
			configuration_path = self.__get_configuration_path(model_path=model_path)
			configuration_json = self.__get_dictionary_from_json(configuration_path=configuration_path)
			model_type = self.__search_model_type(data=configuration_json, return_key=False)
			disable_tqdm = False if self.__progress or not self.__disable_tqdm else True
			if disable_tqdm:
				from sapiens_transformers.utils.functions import set_tqdm
				set_tqdm(disable=True)
			training_arguments = self.__TrainingArguments(
			    output_dir=output_path,
			    per_device_train_batch_size=self.__per_device_train_batch_size,
			    gradient_accumulation_steps=self.__gradient_accumulation_steps,
			    num_train_epochs=self.__num_train_epochs,
			    save_strategy=self.__save_strategy,
			    evaluation_strategy=self.__evaluation_strategy,
			    eval_strategy=self.__eval_strategy,
			    learning_rate=self.__learning_rate,
			    weight_decay=self.__weight_decay,
			    logging_steps=self.__logging_steps,
			    fp16=self.__fp16,
			    bf16=self.__bf16,
			    report_to=self.__report_to,
			    disable_tqdm=disable_tqdm,
			    max_grad_norm=self.__max_grad_norm
			)
			tokenized_datasets = dataset.map(tokenize_function_mistral if model_type in ('mistral', 'mixtral', 'sastral') else tokenize_function, batched=True)
			trainer = self.__Trainer(model=model, args=training_arguments, train_dataset=tokenized_datasets['train'], tokenizer=tokenizer, data_collator=self.__default_data_collator)
			if self.__progress: print('Starting fine-tuning training......')
			train_output = trainer.train()
			if self.__progress: print(f'error rate: {train_output.training_loss:.20f}.')
			trainer.save_model(output_path)
			tokenizer.save_pretrained(output_path)
			destination_path = self.__path.join(output_path, self.__path.basename(configuration_path))
			self.__copy_and_overwrite_file(source_path=configuration_path, destination_path=destination_path)
			if saf_model_conversion: self.__model_conversion(sapiens_path=output_path, to=self.__STATE1Y)
			if bin_model_conversion: self.__model_conversion(sapiens_path=output_path, to=self.__STATE2Y)
			if is_url:
				from os import remove
				if self.__path.exists(dataset_path): remove(dataset_path)
			if self.__progress: print('Fine-tuning completed successfully.')
			return train_output.training_loss
		except Exception as error:
			if self.__show_errors: print('ERROR in ManualFineTuning.fit: '+str(error))
			try:
				if saf_model_conversion: self.__model_conversion(sapiens_path=output_path, to=self.__STATE1Y)
				if bin_model_conversion: self.__model_conversion(sapiens_path=output_path, to=self.__STATE2Y)
			except: pass
			return 1.0
class MGT():
	def __init__(self, model_path='', dataset_path='', progress=True, show_errors=True):
		try:
			self.__loaded_class = False
			self.__model_path = model_path.strip() if type(model_path) == str else str(model_path).strip()
			dataset_path = dataset_path.strip() if type(dataset_path) == str else str(dataset_path).strip()
			self.__progress = bool(progress) if type(progress) in (bool, int, float) else True
			self.__show_errors = bool(show_errors) if type(show_errors) in (bool, int, float) else True
			if dataset_path and (not dataset_path.endswith('.json') and not dataset_path.endswith('.txt')):
				if self.__show_errors: print('The MGT training only accepts datasets in JSON format.')
				return None
			self.__number_of_adjustments = 0
			self.__it_is_a_temporary_file, self.__dataset_path = False, dataset_path
			from sapiens_transformers.utils.functions import get_dictionary_from_json, set_tqdm, update_tqdm
			self.__dataset = get_dictionary_from_json(configuration_path=dataset_path) if dataset_path else dict()
			self.__get_dictionary_from_json = get_dictionary_from_json
			self.__set_tqdm, self.__update_tqdm = set_tqdm, update_tqdm
			from json import dump as json_dump
			from os import path, remove
			from pickle import dump, load
			from unicodedata import normalize
			from string import punctuation
			from random import randint
			from sapiens_generalization import SapiensGeneralization
			self.__json_dump = json_dump
			self.__path, self.__load, self.__dump, self.__remove = path, load, dump, remove
			self.__normalize, self.__punctuation, self.__randint = normalize, punctuation, randint
			self.__sapiens_generalization = SapiensGeneralization()
			self.probability = 0.0
			self.__loaded_class = True
		except Exception as error:
			if self.__show_errors: print('ERROR in MGT.__init__: '+str(error))
			self.__loaded_class = False
	def addFit(self, Input='', Output=''):
		try:
			Input = rf'{Input}'.strip() if type(Input) == str else rf'{str(Input).strip()}'
			Output = rf'{Output}'.strip() if type(Output) == str else rf'{str(Output).strip()}'
			self.__number_of_adjustments += 1
			if self.__progress:
				progress_bar = self.__update_tqdm(total=3, description='Adding adjustment '+str(self.__number_of_adjustments))
				progress_bar.update(1)
			if not self.__it_is_a_temporary_file:
				from tempfile import NamedTemporaryFile
				with NamedTemporaryFile(suffix='.json', delete=False) as temporary_file: dataset_path = temporary_file.name
				with open(dataset_path, 'w', encoding='utf-8') as file: self.__json_dump({'data': []}, file, ensure_ascii=False, indent=4)
				self.__dataset_path = dataset_path
				self.__it_is_a_temporary_file = True
			if self.__progress: progress_bar.update(1)
			dataset = self.__get_dictionary_from_json(configuration_path=self.__dataset_path)
			dataset['data'] += [{'input': Input, 'output': Output}]
			with open(self.__dataset_path, 'w', encoding='utf-8') as file: self.__json_dump(dataset, file, ensure_ascii=False, indent=4)
			if self.__progress:
				progress_bar.update(1)
				progress_bar.n = 3
				progress_bar.refresh()
				progress_bar.close()
			return True
		except Exception as error:
			if self.__show_errors: print('ERROR in MGT.addFit: '+str(error))
			return False
	def fit(self, precision=0.75):
		try:
			if not self.__loaded_class: return False
			precision = min(1.0, max(0.01, float(precision))) if type(precision) in (bool, int, float) else 0.75
			if self.__it_is_a_temporary_file: self.__dataset = self.__get_dictionary_from_json(configuration_path=self.__dataset_path)
			if not 'data' in self.__dataset:
				dataset = dict()
				dataset['data'] = self.__dataset
				self.__dataset = dataset
			if not self.__progress: self.__set_tqdm(disable=True)
			total_epochs, maximum_length = len(self.__dataset['data']), 0
			progress_bar = self.__update_tqdm(total=total_epochs, description='Adjusting with MGT')
			for data in self.__dataset['data']:
				_input = str(data.get('input', '')).strip()
				input_length = len(_input)
				if input_length > maximum_length: maximum_length = input_length
				progress_bar.update(1)
			self.__dataset['precision'] = precision
			self.__dataset['maximum_length'] = maximum_length
			file_path = self.__path.join(self.__model_path, 'adjustment.mgt')
			if self.__path.exists(file_path):
				with open(file_path, 'rb') as file: dataset = self.__load(file)
				if 'data' in dataset:
					data = list(dataset.get('data', []))
					old_precision = float(dataset.get('precision', 0.75))
					self.__dataset['data'] += data
					self.__dataset['precision'] = (old_precision+precision)/2
			with open(file_path, 'wb') as file: self.__dump(self.__dataset, file)
			progress_bar.n = total_epochs
			progress_bar.refresh()
			progress_bar.close()
			if self.__it_is_a_temporary_file and self.__path.exists(self.__dataset_path): self.__remove(self.__dataset_path)
			self.__set_tqdm(disable=not self.__progress)
			return True
		except Exception as error:
			if self.__show_errors: print('ERROR in MGT.fit: '+str(error))
			try:
				if self.__it_is_a_temporary_file and self.__path.exists(self.__dataset_path): self.__remove(self.__dataset_path)
			except: pass
			self.__set_tqdm(disable=not self.__progress)
			return False
	def predict(self, prompt=''):
		try:
			if not self.__loaded_class: return ''
			prompt = rf'{prompt}'.strip()
			file_path = self.__path.join(self.__model_path, 'adjustment.mgt')
			if not self.__path.exists(file_path): return ''
			with open(file_path, 'rb') as file: self.__dataset = self.__load(file)
			if not 'data' in self.__dataset: return ''
			data = list(self.__dataset.get('data', []))
			precision, candidates = float(self.__dataset.get('precision', 0.75)), []
			maximum_length = int(self.__dataset.get('maximum_length', 0))
			if len(prompt) > int(round(maximum_length+(maximum_length*0.1))): return ''
			def textual_comparison(text1='', text2=''):
				def normalize(text=''):
					text = ''.join(character for character in self.__normalize('NFD', str(text).lower().strip()) if not character.encode('utf-8').startswith(b'\xcc'))
					return ''.join(character for character in text if character not in self.__punctuation)
				text1, text2 = normalize(text=text1), normalize(text=text2)
				tokens1, tokens2 = text1.split(), text2.split()
				tokens1_length, tokens2_length = len(tokens1), len(tokens2)
				if text1 in text2 or text2 in text1: probability1 = 1.0
				else:
					search, target = (tokens1, tokens2) if tokens2_length > tokens1_length else (tokens2, tokens1)
					coincidences = 0
					for _search in search:
						if _search in target: coincidences += 1
					probability1 = coincidences / max(1, len(search))
				probability2 = min(tokens1_length, tokens2_length)/max(1, max(tokens1_length, tokens2_length))
				return (probability1+probability2)/2
			for index, input_output in enumerate(data):
				_input = str(input_output.get('input', '')).strip()
				probability = textual_comparison(text1=prompt, text2=_input)
				if probability > self.probability: self.probability = probability
				if probability >= precision: candidates.append((index, probability))
			if not candidates: return ''
			maximum_probability, maximum_index = 0.0, 0
			for candidate in candidates:
				if candidate[1] > maximum_probability: maximum_probability, maximum_index = candidate[1], candidate[0]
				elif candidate[1] == maximum_probability and self.__randint(0, 1) < 1: maximum_probability, maximum_index = candidate[1], candidate[0]
			_input = str(data[maximum_index].get('input', '')).strip()
			_output = str(data[maximum_index].get('output', '')).strip()
			self.probability = maximum_probability
			return self.__sapiens_generalization.generalization(prompt=prompt, original_input=_input, original_output=_output)
		except Exception as error:
			if self.__show_errors: print('ERROR in MGT.predict: '+str(error))
			return ''
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
