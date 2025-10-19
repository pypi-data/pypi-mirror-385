"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import warnings
from ...utils import is_sklearn_available, requires_backends
if is_sklearn_available():
    from scipy.stats import pearsonr, spearmanr
    from sklearn.metrics import f1_score, matthews_corrcoef
DEPRECATION_WARNING = ("This metric will be removed from the library soon, metrics should be handled with the HF Evaluate library.")
def simple_accuracy(preds, labels):
    warnings.warn(DEPRECATION_WARNING, FutureWarning)
    requires_backends(simple_accuracy, "sklearn")
    return (preds == labels).mean()
def acc_and_f1(preds, labels):
    warnings.warn(DEPRECATION_WARNING, FutureWarning)
    requires_backends(acc_and_f1, "sklearn")
    acc = simple_accuracy(preds, labels)
    f1 = f1_score(y_true=labels, y_pred=preds)
    return {"acc": acc, "f1": f1, "acc_and_f1": (acc + f1) / 2}
def pearson_and_spearman(preds, labels):
    warnings.warn(DEPRECATION_WARNING, FutureWarning)
    requires_backends(pearson_and_spearman, "sklearn")
    pearson_corr = pearsonr(preds, labels)[0]
    spearman_corr = spearmanr(preds, labels)[0]
    return {"pearson": pearson_corr, "spearmanr": spearman_corr, "corr": (pearson_corr + spearman_corr) / 2}
def glue_compute_metrics(task_name, preds, labels):
    warnings.warn(DEPRECATION_WARNING, FutureWarning)
    requires_backends(glue_compute_metrics, "sklearn")
    assert len(preds) == len(labels), f"Predictions and labels have mismatched lengths {len(preds)} and {len(labels)}"
    if task_name == "cola": return {"mcc": matthews_corrcoef(labels, preds)}
    elif task_name == "sst-2": return {"acc": simple_accuracy(preds, labels)}
    elif task_name == "mrpc": return acc_and_f1(preds, labels)
    elif task_name == "sts-b": return pearson_and_spearman(preds, labels)
    elif task_name == "qqp": return acc_and_f1(preds, labels)
    elif task_name == "mnli": return {"mnli/acc": simple_accuracy(preds, labels)}
    elif task_name == "mnli-mm": return {"mnli-mm/acc": simple_accuracy(preds, labels)}
    elif task_name == "qnli": return {"acc": simple_accuracy(preds, labels)}
    elif task_name == "rte": return {"acc": simple_accuracy(preds, labels)}
    elif task_name == "wnli": return {"acc": simple_accuracy(preds, labels)}
    elif task_name == "hans": return {"acc": simple_accuracy(preds, labels)}
    else: raise KeyError(task_name)
def xnli_compute_metrics(task_name, preds, labels):
    warnings.warn(DEPRECATION_WARNING, FutureWarning)
    requires_backends(xnli_compute_metrics, "sklearn")
    if len(preds) != len(labels): raise ValueError(f"Predictions and labels have mismatched lengths {len(preds)} and {len(labels)}")
    if task_name == "xnli": return {"acc": simple_accuracy(preds, labels)}
    else: raise KeyError(task_name)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
