"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from ...utils import logging
from .utils import DataProcessor, InputExample
logger = logging.get_logger(__name__)
class XnliProcessor(DataProcessor):
    def __init__(self, language, train_language=None):
        self.language = language
        self.train_language = train_language
    def get_train_examples(self, data_dir):
        lg = self.language if self.train_language is None else self.train_language
        lines = self._read_tsv(os.path.join(data_dir, f"XNLI-MT-1.0/multinli/multinli.train.{lg}.tsv"))
        examples = []
        for i, line in enumerate(lines):
            if i == 0: continue
            guid = f"train-{i}"
            text_a = line[0]
            text_b = line[1]
            label = "contradiction" if line[2] == "contradictory" else line[2]
            if not isinstance(text_a, str): raise TypeError(f"Training input {text_a} is not a string")
            if not isinstance(text_b, str): raise TypeError(f"Training input {text_b} is not a string")
            if not isinstance(label, str): raise TypeError(f"Training label {label} is not a string")
            examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label=label))
        return examples
    def get_test_examples(self, data_dir):
        lines = self._read_tsv(os.path.join(data_dir, "XNLI-1.0/xnli.test.tsv"))
        examples = []
        for i, line in enumerate(lines):
            if i == 0: continue
            language = line[0]
            if language != self.language: continue
            guid = f"test-{i}"
            text_a = line[6]
            text_b = line[7]
            label = line[1]
            if not isinstance(text_a, str): raise TypeError(f"Training input {text_a} is not a string")
            if not isinstance(text_b, str): raise TypeError(f"Training input {text_b} is not a string")
            if not isinstance(label, str): raise TypeError(f"Training label {label} is not a string")
            examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label=label))
        return examples
    def get_labels(self): return ["contradiction", "entailment", "neutral"]
xnli_processors = {"xnli": XnliProcessor}
xnli_output_modes = {"xnli": "classification"}
xnli_tasks_num_labels = {"xnli": 3}
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
