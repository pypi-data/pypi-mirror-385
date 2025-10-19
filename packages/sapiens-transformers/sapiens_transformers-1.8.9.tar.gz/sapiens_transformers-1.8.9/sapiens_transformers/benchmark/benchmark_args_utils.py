"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import dataclasses
import json
import warnings
from dataclasses import dataclass, field
from time import time
from typing import List
from ..utils import logging
logger = logging.get_logger(__name__)
def list_field(default=None, metadata=None): return field(default_factory=lambda: default, metadata=metadata)
@dataclass
class BenchmarkArguments:
    models: List[str] = list_field(default=[], metadata={'help': 'Model checkpoints to be provided to the AutoModel classes. Leave blank to benchmark the base version of all available models'})
    batch_sizes: List[int] = list_field(default=[8], metadata={"help": "List of batch sizes for which memory and time performance will be evaluated"})
    sequence_lengths: List[int] = list_field(default=[8, 32, 128, 512], metadata={"help": "List of sequence lengths for which memory and time performance will be evaluated"})
    inference: bool = field(default=True, metadata={"help": "Whether to benchmark inference of model. Inference can be disabled via --no-inference."})
    cuda: bool = field(default=True, metadata={"help": "Whether to run on available cuda devices. Cuda can be disabled via --no-cuda."})
    tpu: bool = field(default=True, metadata={"help": "Whether to run on available tpu devices. TPU can be disabled via --no-tpu."})
    fp16: bool = field(default=False, metadata={"help": "Use FP16 to sapiens_accelerator inference."})
    training: bool = field(default=False, metadata={"help": "Benchmark training of model"})
    verbose: bool = field(default=False, metadata={"help": "Verbose memory tracing"})
    speed: bool = field(default=True, metadata={"help": "Whether to perform speed measurements. Speed measurements can be disabled via --no-speed."})
    memory: bool = field(default=True, metadata={'help': 'Whether to perform memory measurements. Memory measurements can be disabled via --no-memory'})
    trace_memory_line_by_line: bool = field(default=False, metadata={"help": "Trace memory line by line"})
    save_to_csv: bool = field(default=False, metadata={"help": "Save result to a CSV file"})
    log_print: bool = field(default=False, metadata={"help": "Save all print statements in a log file"})
    env_print: bool = field(default=False, metadata={"help": "Whether to print environment information"})
    multi_process: bool = field(default=True, metadata={'help': 'Whether to use multiprocessing for memory and speed measurement. It is highly recommended to use multiprocessing for accurate CPU and GPU memory measurements. This option should only be disabled for debugging / testing and on TPU.'})
    inference_time_csv_file: str = field(default=f"inference_time_{round(time())}.csv", metadata={"help": "CSV filename used if saving time results to csv."})
    inference_memory_csv_file: str = field(default=f"inference_memory_{round(time())}.csv", metadata={"help": "CSV filename used if saving memory results to csv."})
    train_time_csv_file: str = field(default=f"train_time_{round(time())}.csv", metadata={"help": "CSV filename used if saving time results to csv for training."})
    train_memory_csv_file: str = field(default=f"train_memory_{round(time())}.csv", metadata={"help": "CSV filename used if saving memory results to csv for training."})
    env_info_csv_file: str = field(default=f"env_info_{round(time())}.csv", metadata={"help": "CSV filename used if saving environment information."})
    log_filename: str = field(default=f"log_{round(time())}.csv", metadata={"help": "Log filename used if print statements are saved in log."})
    repeat: int = field(default=3, metadata={"help": "Times an experiment will be run."})
    only_pretrain_model: bool = field(default=False, metadata={'help': 'Instead of loading the model as defined in `config.architectures` if exists, just load the pretrain model weights.'})
    def __post_init__(self): warnings.warn(f"The class {self.__class__} is deprecated. Sapiens Benchmarking utils are deprecated in general and it is advised to use external Benchmarking libraries to benchmark Transformer models.", FutureWarning)
    def to_json_string(self): return json.dumps(dataclasses.asdict(self), indent=2)
    @property
    def model_names(self) -> List[str]:
        if len(self.models) <= 0: raise ValueError("Please make sure you provide at least one model name / model identifier, *e.g.* `--models google-bert/bert-base-cased` or `args.models = ['google-bert/bert-base-cased'].")
        return self.models
    @property
    def do_multi_processing(self):
        if not self.multi_process: return False
        elif self.is_tpu:
            logger.info("Multiprocessing is currently not possible on TPU.")
            return False
        else: return True
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
