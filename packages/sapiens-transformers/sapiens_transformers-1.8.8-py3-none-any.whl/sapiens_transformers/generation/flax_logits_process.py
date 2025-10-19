"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import inspect
import jax
import jax.lax as lax
import jax.numpy as jnp
from jax.experimental import sparse
from ..utils import add_start_docstrings
from ..utils.logging import get_logger
logger = get_logger(__name__)
LOGITS_PROCESSOR_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`jnp.ndarray` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary.
            Indices can be obtained using [`PreTrainedTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        scores (`jnp.ndarray` of shape `(batch_size, config.vocab_size)`):
            Prediction scores of a language modeling head. These can be logits for each vocabulary when not using beam
            search or log softmax for each vocabulary token when using beam search
        kwargs (`Dict[str, Any]`, *optional*):
            Additional logits processor specific kwargs.
    Return:
        `jnp.ndarray` of shape `(batch_size, config.vocab_size)`: The processed prediction scores.
"""
class FlaxLogitsProcessor:
    @add_start_docstrings(LOGITS_PROCESSOR_INPUTS_DOCSTRING)
    def __call__(self, input_ids: jnp.ndarray, scores: jnp.ndarray) -> jnp.ndarray: raise NotImplementedError(f"{self.__class__} is an abstract class. Only classes inheriting this class can be called.")
class FlaxLogitsWarper:
    @add_start_docstrings(LOGITS_PROCESSOR_INPUTS_DOCSTRING)
    def __call__(self, input_ids: jnp.ndarray, scores: jnp.ndarray) -> jnp.ndarray: raise NotImplementedError(f"{self.__class__} is an abstract class. Only classes inheriting this class can be called.")
class FlaxLogitsProcessorList(list):
    @add_start_docstrings(LOGITS_PROCESSOR_INPUTS_DOCSTRING)
    def __call__(self, input_ids: jnp.ndarray, scores: jnp.ndarray, cur_len: int, **kwargs) -> jnp.ndarray:
        for processor in self:
            function_args = inspect.signature(processor.__call__).parameters
            if len(function_args) > 3:
                if not all(arg in kwargs for arg in list(function_args.keys())[2:]): raise ValueError(f"Make sure that all the required parameters: {list(function_args.keys())} for {processor.__class__} are passed to the logits processor.")
                scores = processor(input_ids, scores, cur_len, **kwargs)
            else: scores = processor(input_ids, scores, cur_len)
        return scores
class FlaxTemperatureLogitsWarper(FlaxLogitsWarper):
    def __init__(self, temperature: float):
        if not isinstance(temperature, float) or not (temperature > 0): raise ValueError(f"`temperature` has to be a strictly positive float, but is {temperature}")
        self.temperature = temperature
    def __call__(self, input_ids: jnp.ndarray, scores: jnp.ndarray, cur_len: int) -> jnp.ndarray:
        scores = scores / self.temperature
        return scores
class FlaxTopPLogitsWarper(FlaxLogitsWarper):
    def __init__(self, top_p: float, filter_value: float = -float("Inf"), min_tokens_to_keep: int = 1):
        if not isinstance(top_p, float) or (top_p < 0 or top_p > 1.0): raise ValueError(f"`top_p` has to be a float > 0 and < 1, but is {top_p}")
        if not isinstance(min_tokens_to_keep, int) or (min_tokens_to_keep < 1): raise ValueError(f"`min_tokens_to_keep` has to be a positive integer, but is {min_tokens_to_keep}")
        self.top_p = top_p
        self.filter_value = filter_value
        self.min_tokens_to_keep = min_tokens_to_keep
    def __call__(self, input_ids: jnp.ndarray, scores: jnp.ndarray, cur_len: int) -> jnp.ndarray:
        topk_scores, topk_indices = lax.top_k(scores, scores.shape[-1])
        mask_scores = jnp.full_like(scores, self.filter_value)
        cumulative_probs = jax.nn.softmax(topk_scores, axis=-1).cumsum(axis=-1)
        score_mask = cumulative_probs < self.top_p
        score_mask = jnp.roll(score_mask, 1)
        score_mask |= score_mask.at[:, 0].set(True)
        score_mask = score_mask.at[:, : self.min_tokens_to_keep].set(True)
        topk_next_scores = jnp.where(score_mask, topk_scores, mask_scores)
        next_scores = jax.lax.sort_key_val(topk_indices, topk_next_scores)[-1]
        return next_scores
class FlaxTopKLogitsWarper(FlaxLogitsWarper):
    def __init__(self, top_k: int, filter_value: float = -float("Inf"), min_tokens_to_keep: int = 1):
        if not isinstance(top_k, int) or top_k <= 0: raise ValueError(f"`top_k` has to be a strictly positive integer, but is {top_k}")
        self.top_k = max(top_k, min_tokens_to_keep)
        self.filter_value = filter_value
    def __call__(self, input_ids: jnp.ndarray, scores: jnp.ndarray, cur_len: int) -> jnp.ndarray:
        batch_size, vocab_size = scores.shape
        next_scores_flat = jnp.full(batch_size * vocab_size, self.filter_value)
        topk = min(self.top_k, scores.shape[-1])
        topk_scores, topk_indices = lax.top_k(scores, topk)
        shift = jnp.broadcast_to((jnp.arange(batch_size) * vocab_size)[:, None], (batch_size, topk)).flatten()
        topk_scores_flat = topk_scores.flatten()
        topk_indices_flat = topk_indices.flatten() + shift
        next_scores_flat = next_scores_flat.at[topk_indices_flat].set(topk_scores_flat)
        next_scores = next_scores_flat.reshape(batch_size, vocab_size)
        return next_scores
class FlaxForcedBOSTokenLogitsProcessor(FlaxLogitsProcessor):
    def __init__(self, bos_token_id: int): self.bos_token_id = bos_token_id
    def __call__(self, input_ids: jnp.ndarray, scores: jnp.ndarray, cur_len: int) -> jnp.ndarray:
        new_scores = jnp.full(scores.shape, -float("inf"))
        apply_penalty = 1 - jnp.bool_(cur_len - 1)
        scores = jnp.where(apply_penalty, new_scores.at[:, self.bos_token_id].set(0), scores)
        return scores
class FlaxForcedEOSTokenLogitsProcessor(FlaxLogitsProcessor):
    def __init__(self, max_length: int, eos_token_id: int):
        self.max_length = max_length
        self.eos_token_id = eos_token_id
    def __call__(self, input_ids: jnp.ndarray, scores: jnp.ndarray, cur_len: int) -> jnp.ndarray:
        new_scores = jnp.full(scores.shape, -float("inf"))
        apply_penalty = 1 - jnp.bool_(cur_len - self.max_length + 1)
        scores = jnp.where(apply_penalty, new_scores.at[:, self.eos_token_id].set(0), scores)
        return scores
class FlaxMinLengthLogitsProcessor(FlaxLogitsProcessor):
    def __init__(self, min_length: int, eos_token_id: int):
        if not isinstance(min_length, int) or min_length < 0: raise ValueError(f"`min_length` has to be a positive integer, but is {min_length}")
        if not isinstance(eos_token_id, int) or eos_token_id < 0: raise ValueError(f"`eos_token_id` has to be a positive integer, but is {eos_token_id}")
        self.min_length = min_length
        self.eos_token_id = eos_token_id
    def __call__(self, input_ids: jnp.ndarray, scores: jnp.ndarray, cur_len: int) -> jnp.ndarray:
        apply_penalty = 1 - jnp.clip(cur_len - self.min_length, 0, 1)
        scores = jnp.where(apply_penalty, scores.at[:, self.eos_token_id].set(-float("inf")), scores)
        return scores
class FlaxSAPIAudioTimeStampLogitsProcessor(FlaxLogitsProcessor):
    def __init__(self, generate_config, model_config, decoder_input_length):
        self.eos_token_id = generate_config.eos_token_id
        self.no_timestamps_token_id = generate_config.no_timestamps_token_id
        self.timestamp_begin = generate_config.no_timestamps_token_id + 1
        self.begin_index = decoder_input_length + 1
        if generate_config.is_multilingual: self.begin_index += 2
        if hasattr(generate_config, "max_initial_timestamp_index"): self.max_initial_timestamp_index = generate_config.max_initial_timestamp_index
        else: self.max_initial_timestamp_index = model_config.vocab_size
        if self.max_initial_timestamp_index is None: self.max_initial_timestamp_index = model_config.vocab_size
    def __call__(self, input_ids, scores, cur_len):
        scores = scores.at[:, self.no_timestamps_token_id].set(-float("inf"))
        def handle_pairs(input_ids_k, scores_k):
            last_was_timestamp = jnp.where((cur_len - self.begin_index) >= 1, True, False)
            last_was_timestamp = jnp.where(input_ids_k[cur_len - 1] >= self.timestamp_begin, True and last_was_timestamp, False)
            penultimate_was_timestamp = jnp.where((cur_len - self.begin_index) < 2, True, False)
            penultimate_was_timestamp = jnp.where(input_ids_k[cur_len - 2] >= self.timestamp_begin, True, penultimate_was_timestamp)
            return jnp.where(last_was_timestamp, jnp.where(penultimate_was_timestamp > 0, scores_k.at[self.timestamp_begin :].set(-float("inf")), scores_k.at[: self.eos_token_id].set(-float("inf"))), scores_k)
        scores = jax.vmap(handle_pairs)(input_ids, scores)
        apply_max_initial_timestamp = jnp.where(cur_len == self.begin_index, True, False)
        apply_max_initial_timestamp = jnp.where(self.max_initial_timestamp_index is not None, True and apply_max_initial_timestamp, False)
        last_allowed = self.timestamp_begin + self.max_initial_timestamp_index
        scores = jnp.where(apply_max_initial_timestamp, scores.at[:, last_allowed + 1 :].set(-float("inf")), scores)
        logprobs = jax.nn.log_softmax(scores, axis=-1)
        def handle_cumulative_probs(logprobs_k, scores_k):
            timestamp_logprob = jax.nn.logsumexp(logprobs_k[self.timestamp_begin :], axis=-1)
            max_text_token_logprob = jnp.max(logprobs_k[: self.timestamp_begin])
            return jnp.where(timestamp_logprob > max_text_token_logprob, scores_k.at[: self.timestamp_begin].set(-float("inf")), scores_k)
        scores = jax.vmap(handle_cumulative_probs)(logprobs, scores)
        return scores
class FlaxSuppressTokensAtBeginLogitsProcessor(FlaxLogitsProcessor):
    def __init__(self, begin_suppress_tokens, begin_index):
        self.begin_suppress_tokens = list(begin_suppress_tokens)
        self.begin_index = begin_index
    def __call__(self, input_ids, scores, cur_len: int):
        apply_penalty = 1 - jnp.bool_(cur_len - self.begin_index)
        scores = jnp.where(apply_penalty, scores.at[:, self.begin_suppress_tokens].set(-float("inf")), scores)
        return scores
class FlaxSuppressTokensLogitsProcessor(FlaxLogitsProcessor):
    def __init__(self, suppress_tokens: list): self.suppress_tokens = list(suppress_tokens)
    def __call__(self, input_ids: jnp.ndarray, scores: jnp.ndarray, cur_len: int) -> jnp.ndarray:
        scores = scores.at[..., self.suppress_tokens].set(-float("inf"))
        return scores
class FlaxForceTokensLogitsProcessor(FlaxLogitsProcessor):
    def __init__(self, force_token_map):
        force_token_map = dict(force_token_map)
        force_token_array = jnp.ones((max(force_token_map.keys()) + 1), dtype=jnp.int32) * -1
        for index, token in force_token_map.items():
            if token is not None: force_token_array = force_token_array.at[index].set(token)
        self.force_token_array = jnp.int32(force_token_array)
    def __call__(self, input_ids: jnp.ndarray, scores: jnp.ndarray, cur_len: int) -> jnp.ndarray:
        def _force_token(generation_idx):
            batch_size = scores.shape[0]
            current_token = self.force_token_array[generation_idx]
            new_scores = jnp.ones_like(scores, dtype=scores.dtype) * -float("inf")
            updates = jnp.zeros((batch_size, 1), dtype=scores.dtype)
            new_scores = lax.dynamic_update_slice(new_scores, updates, (0, current_token))
            return new_scores
        scores = lax.cond(cur_len >= self.force_token_array.shape[0], lambda: scores, lambda: lax.cond(self.force_token_array[cur_len] >= 0, lambda: _force_token(cur_len), lambda: scores))
        return scores
class FlaxWhisperTimeStampLogitsProcessor(FlaxLogitsProcessor):
    def __init__(self, generate_config, model_config, decoder_input_length):
        self.eos_token_id = generate_config.eos_token_id
        self.no_timestamps_token_id = generate_config.no_timestamps_token_id
        self.timestamp_begin = generate_config.no_timestamps_token_id + 1
        self.begin_index = decoder_input_length + 1
        if generate_config.is_multilingual: self.begin_index += 2
        if hasattr(generate_config, "max_initial_timestamp_index"): self.max_initial_timestamp_index = generate_config.max_initial_timestamp_index
        else: self.max_initial_timestamp_index = model_config.vocab_size
        if self.max_initial_timestamp_index is None: self.max_initial_timestamp_index = model_config.vocab_size
    def __call__(self, input_ids, scores, cur_len):
        scores = scores.at[:, self.no_timestamps_token_id].set(-float("inf"))
        def handle_pairs(input_ids_k, scores_k):
            last_was_timestamp = jnp.where((cur_len - self.begin_index) >= 1, True, False)
            last_was_timestamp = jnp.where(input_ids_k[cur_len - 1] >= self.timestamp_begin, True and last_was_timestamp, False)
            penultimate_was_timestamp = jnp.where((cur_len - self.begin_index) < 2, True, False)
            penultimate_was_timestamp = jnp.where(input_ids_k[cur_len - 2] >= self.timestamp_begin, True, penultimate_was_timestamp)
            return jnp.where(last_was_timestamp, jnp.where(penultimate_was_timestamp > 0, scores_k.at[self.timestamp_begin :].set(-float("inf")), scores_k.at[: self.eos_token_id].set(-float("inf"))), scores_k)
        scores = jax.vmap(handle_pairs)(input_ids, scores)
        apply_max_initial_timestamp = jnp.where(cur_len == self.begin_index, True, False)
        apply_max_initial_timestamp = jnp.where(self.max_initial_timestamp_index is not None, True and apply_max_initial_timestamp, False)
        last_allowed = self.timestamp_begin + self.max_initial_timestamp_index
        scores = jnp.where(apply_max_initial_timestamp, scores.at[:, last_allowed + 1 :].set(-float("inf")), scores)
        logprobs = jax.nn.log_softmax(scores, axis=-1)
        def handle_cumulative_probs(logprobs_k, scores_k):
            timestamp_logprob = jax.nn.logsumexp(logprobs_k[self.timestamp_begin :], axis=-1)
            max_text_token_logprob = jnp.max(logprobs_k[: self.timestamp_begin])
            return jnp.where(timestamp_logprob > max_text_token_logprob, scores_k.at[: self.timestamp_begin].set(-float("inf")), scores_k)
        scores = jax.vmap(handle_cumulative_probs)(logprobs, scores)
        return scores
class FlaxNoRepeatNGramLogitsProcessor(FlaxLogitsProcessor):
    def __init__(self, ngram_size: int):
        if not isinstance(ngram_size, int) or ngram_size <= 0: raise ValueError(f"`ngram_size` has to be a strictly positive integer, but is {ngram_size}")
        self.ngram_size = ngram_size
    def get_previous_ngrams(self, input_ids: jnp.ndarray, vocab_size: int, cur_len: int):
        batch_size, seq_len = input_ids.shape
        seq_ngrams = seq_len - (self.ngram_size - 1)
        cur_ngrams = cur_len - (self.ngram_size - 1)
        def body_fun(i, val):
            b = i % batch_size
            pos = i // batch_size
            return val.at[i].set(jnp.array([b,] + [jnp.array(input_ids)[b, pos + j] for j in range(self.ngram_size)]))
        shape = (batch_size * seq_ngrams, self.ngram_size + 1)
        all_update_indices = jax.lax.fori_loop(0, batch_size * cur_ngrams, body_fun, jnp.zeros(shape, dtype=input_ids.dtype))
        data = (jnp.arange(batch_size * seq_ngrams) < batch_size * cur_ngrams).astype("float32")
        return sparse.BCOO((data, all_update_indices), shape=(batch_size,) + (vocab_size,) * self.ngram_size)
    def get_banned_tokens_mask(self, latest_tokens: jnp.ndarray, previous_ngrams) -> jnp.ndarray:
        @sparse.sparsify
        @jax.vmap
        def inner_fn(latest_tokens, previous_ngrams): return previous_ngrams[tuple(latest_tokens)]
        return sparse.bcoo_todense(inner_fn(latest_tokens, previous_ngrams))
    def __call__(self, input_ids: jnp.ndarray, scores: jnp.ndarray, cur_len: int) -> jnp.ndarray:
        def true_fn():
            _, vocab_size = scores.shape
            previous_ngrams = self.get_previous_ngrams(input_ids, vocab_size, cur_len)
            latest_tokens = jnp.zeros((input_ids.shape[0], self.ngram_size - 1), dtype=input_ids.dtype)
            latest_tokens = jax.lax.dynamic_update_slice(latest_tokens, jax.lax.dynamic_slice(input_ids, (0, cur_len - (self.ngram_size - 1)), (input_ids.shape[0], (self.ngram_size - 1))), (0, 0))
            banned_tokens_indices_mask = self.get_banned_tokens_mask(latest_tokens, previous_ngrams).astype("bool")
            return jnp.where(banned_tokens_indices_mask, -float("inf"), scores)
        output = jax.lax.cond((cur_len >= self.ngram_size - 1), true_fn, lambda: scores)
        return output
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
