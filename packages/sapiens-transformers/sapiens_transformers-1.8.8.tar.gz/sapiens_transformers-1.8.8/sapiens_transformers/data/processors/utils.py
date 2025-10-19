"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import csv
import dataclasses
import json
from dataclasses import dataclass
from typing import List, Optional, Union
from ...utils import is_tf_available, is_torch_available, logging
logger = logging.get_logger(__name__)
@dataclass
class InputExample:
    guid: str
    text_a: str
    text_b: Optional[str] = None
    label: Optional[str] = None
    def to_json_string(self): return json.dumps(dataclasses.asdict(self), indent=2) + "\n"
@dataclass(frozen=True)
class InputFeatures:
    input_ids: List[int]
    attention_mask: Optional[List[int]] = None
    token_type_ids: Optional[List[int]] = None
    label: Optional[Union[int, float]] = None
    def to_json_string(self): return json.dumps(dataclasses.asdict(self)) + "\n"
class DataProcessor:
    def get_example_from_tensor_dict(self, tensor_dict): raise NotImplementedError()
    def get_train_examples(self, data_dir): raise NotImplementedError()
    def get_dev_examples(self, data_dir): raise NotImplementedError()
    def get_test_examples(self, data_dir): raise NotImplementedError()
    def get_labels(self): raise NotImplementedError()
    def tfds_map(self, example):
        if len(self.get_labels()) > 1: example.label = self.get_labels()[int(example.label)]
        return example
    @classmethod
    def _read_tsv(cls, input_file, quotechar=None):
        with open(input_file, "r", encoding="utf-8-sig") as f: return list(csv.reader(f, delimiter="\t", quotechar=quotechar))
class SingleSentenceClassificationProcessor(DataProcessor):
    def __init__(self, labels=None, examples=None, mode="classification", verbose=False):
        self.labels = [] if labels is None else labels
        self.examples = [] if examples is None else examples
        self.mode = mode
        self.verbose = verbose
    def __len__(self): return len(self.examples)
    def __getitem__(self, idx):
        if isinstance(idx, slice): return SingleSentenceClassificationProcessor(labels=self.labels, examples=self.examples[idx])
        return self.examples[idx]
    @classmethod
    def create_from_csv(cls, file_name, split_name="", column_label=0, column_text=1, column_id=None, skip_first_row=False, **kwargs):
        processor = cls(**kwargs)
        processor.add_examples_from_csv(file_name, split_name=split_name, column_label=column_label, column_text=column_text, column_id=column_id, skip_first_row=skip_first_row, overwrite_labels=True, overwrite_examples=True)
        return processor
    @classmethod
    def create_from_examples(cls, texts_or_text_and_labels, labels=None, **kwargs):
        processor = cls(**kwargs)
        processor.add_examples(texts_or_text_and_labels, labels=labels)
        return processor
    def add_examples_from_csv(self, file_name, split_name="", column_label=0, column_text=1, column_id=None, skip_first_row=False, overwrite_labels=False, overwrite_examples=False):
        lines = self._read_tsv(file_name)
        if skip_first_row: lines = lines[1:]
        texts = []
        labels = []
        ids = []
        for i, line in enumerate(lines):
            texts.append(line[column_text])
            labels.append(line[column_label])
            if column_id is not None: ids.append(line[column_id])
            else:
                guid = f"{split_name}-{i}" if split_name else str(i)
                ids.append(guid)
        return self.add_examples(texts, labels, ids, overwrite_labels=overwrite_labels, overwrite_examples=overwrite_examples)
    def add_examples(self, texts_or_text_and_labels, labels=None, ids=None, overwrite_labels=False, overwrite_examples=False):
        if labels is not None and len(texts_or_text_and_labels) != len(labels): raise ValueError(f"Text and labels have mismatched lengths {len(texts_or_text_and_labels)} and {len(labels)}")
        if ids is not None and len(texts_or_text_and_labels) != len(ids): raise ValueError(f"Text and ids have mismatched lengths {len(texts_or_text_and_labels)} and {len(ids)}")
        if ids is None: ids = [None] * len(texts_or_text_and_labels)
        if labels is None: labels = [None] * len(texts_or_text_and_labels)
        examples = []
        added_labels = set()
        for text_or_text_and_label, label, guid in zip(texts_or_text_and_labels, labels, ids):
            if isinstance(text_or_text_and_label, (tuple, list)) and label is None: text, label = text_or_text_and_label
            else: text = text_or_text_and_label
            added_labels.add(label)
            examples.append(InputExample(guid=guid, text_a=text, text_b=None, label=label))
        if overwrite_examples: self.examples = examples
        else: self.examples.extend(examples)
        if overwrite_labels: self.labels = list(added_labels)
        else: self.labels = list(set(self.labels).union(added_labels))
        return self.examples
    def get_features(self, tokenizer, max_length=None, pad_on_left=False, pad_token=0, mask_padding_with_zero=True, return_tensors=None):
        if max_length is None: max_length = tokenizer.max_len
        label_map = {label: i for i, label in enumerate(self.labels)}
        all_input_ids = []
        for ex_index, example in enumerate(self.examples):
            if ex_index % 10000 == 0: logger.info(f"Tokenizing example {ex_index}")
            input_ids = tokenizer.encode(example.text_a, add_special_tokens=True, max_length=min(max_length, tokenizer.max_len))
            all_input_ids.append(input_ids)
        batch_length = max(len(input_ids) for input_ids in all_input_ids)
        features = []
        for ex_index, (input_ids, example) in enumerate(zip(all_input_ids, self.examples)):
            if ex_index % 10000 == 0: logger.info(f"Writing example {ex_index}/{len(self.examples)}")
            attention_mask = [1 if mask_padding_with_zero else 0] * len(input_ids)
            padding_length = batch_length - len(input_ids)
            if pad_on_left:
                input_ids = ([pad_token] * padding_length) + input_ids
                attention_mask = ([0 if mask_padding_with_zero else 1] * padding_length) + attention_mask
            else:
                input_ids = input_ids + ([pad_token] * padding_length)
                attention_mask = attention_mask + ([0 if mask_padding_with_zero else 1] * padding_length)
            if len(input_ids) != batch_length: raise ValueError(f"Error with input length {len(input_ids)} vs {batch_length}")
            if len(attention_mask) != batch_length: raise ValueError(f"Error with input length {len(attention_mask)} vs {batch_length}")
            if self.mode == "classification": label = label_map[example.label]
            elif self.mode == "regression": label = float(example.label)
            else: raise ValueError(self.mode)
            if ex_index < 5 and self.verbose:
                logger.info("*** Example ***")
                logger.info(f"guid: {example.guid}")
                logger.info(f"input_ids: {' '.join([str(x) for x in input_ids])}")
                logger.info(f"attention_mask: {' '.join([str(x) for x in attention_mask])}")
                logger.info(f"label: {example.label} (id = {label})")
            features.append(InputFeatures(input_ids=input_ids, attention_mask=attention_mask, label=label))
        if return_tensors is None: return features
        elif return_tensors == "tf":
            if not is_tf_available(): raise RuntimeError("return_tensors set to 'tf' but TensorFlow 2.0 can't be imported")
            import tensorflow as tf
            def gen():
                for ex in features: yield ({"input_ids": ex.input_ids, "attention_mask": ex.attention_mask}, ex.label)
            dataset = tf.data.Dataset.from_generator(gen, ({"input_ids": tf.int32, "attention_mask": tf.int32}, tf.int64), ({"input_ids": tf.TensorShape([None]), "attention_mask": tf.TensorShape([None])}, tf.TensorShape([])))
            return dataset
        elif return_tensors == "pt":
            if not is_torch_available(): raise RuntimeError("return_tensors set to 'pt' but PyTorch can't be imported")
            import torch
            from torch.utils.data import TensorDataset
            all_input_ids = torch.tensor([f.input_ids for f in features], dtype=torch.long)
            all_attention_mask = torch.tensor([f.attention_mask for f in features], dtype=torch.long)
            if self.mode == "classification": all_labels = torch.tensor([f.label for f in features], dtype=torch.long)
            elif self.mode == "regression": all_labels = torch.tensor([f.label for f in features], dtype=torch.float)
            dataset = TensorDataset(all_input_ids, all_attention_mask, all_labels)
            return dataset
        else: raise ValueError("return_tensors should be one of 'tf' or 'pt'")
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
