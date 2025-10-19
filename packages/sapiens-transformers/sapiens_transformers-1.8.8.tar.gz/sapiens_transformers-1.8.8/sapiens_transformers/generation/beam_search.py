"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from abc import ABC, abstractmethod
from collections import UserDict
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import torch
from ..utils import add_start_docstrings
from .beam_constraints import Constraint, ConstraintListState
PROCESS_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size * num_beams, sequence_length)`):
            Indices of input sequence tokens in the vocabulary.
            Indices can be obtained using any class inheriting from [`PreTrainedTokenizer`]. See
            [`PreTrainedTokenizer.encode`] and [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        next_scores (`torch.FloatTensor` of shape `(batch_size, 2 * num_beams)`):
            Current scores of the top `2 * num_beams` non-finished beam hypotheses.
        next_tokens (`torch.LongTensor` of shape `(batch_size, 2 * num_beams)`):
            `input_ids` of the tokens corresponding to the top `2 * num_beams` non-finished beam hypotheses.
        next_indices (`torch.LongTensor` of shape `(batch_size, 2 * num_beams)`):
            Beam indices indicating to which beam hypothesis the `next_tokens` correspond.
        pad_token_id (`int`, *optional*):
            The id of the *padding* token.
        eos_token_id (`Union[int, List[int]]`, *optional*):
            The id of the *end-of-sequence* token. Optionally, use a list to set multiple *end-of-sequence* tokens.
        beam_indices (`torch.LongTensor`, *optional*):
            Beam indices indicating to which beam hypothesis each token correspond.
        group_index (`int`, *optional*):
            The index of the group of beams. Used with [`~PreTrainedModel.group_beam_search`].
    Return:
        `UserDict`: A dictionary composed of the fields as defined above:
            - *next_beam_scores* (`torch.FloatTensor` of shape `(batch_size * num_beams)`) -- Updated scores of all
              non-finished beams.
            - *next_beam_tokens* (`torch.FloatTensor` of shape `(batch_size * num_beams)`) -- Next tokens to be added
              to the non-finished beam_hypotheses.
            - *next_beam_indices* (`torch.FloatTensor` of shape `(batch_size * num_beams)`) -- Beam indices
              indicating to which beam the next tokens shall be added.
"""
FINALIZE_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size * num_beams, sequence_length)`):
            Indices of input sequence tokens in the vocabulary.
            Indices can be obtained using any class inheriting from [`PreTrainedTokenizer`]. See
            [`PreTrainedTokenizer.encode`] and [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        final_beam_scores (`torch.FloatTensor` of shape `(batch_size * num_beams)`):
            The final scores of all non-finished beams.
        final_beam_tokens (`torch.FloatTensor` of shape `(batch_size * num_beams)`):
            The last tokens to be added to the non-finished beam_hypotheses.
        final_beam_indices (`torch.FloatTensor` of shape `(batch_size * num_beams)`):
            The beam indices indicating to which beam the `final_beam_tokens` shall be added.
        pad_token_id (`int`, *optional*):
            The id of the *padding* token.
        eos_token_id (`Union[int, List[int]]`, *optional*):
            The id of the *end-of-sequence* token. Optionally, use a list to set multiple *end-of-sequence* tokens.
    Return:
        `torch.LongTensor` of shape `(batch_size * num_return_sequences, sequence_length)`: The generated sequences.
        The second dimension (sequence_length) is either equal to `max_length` or shorter if all batches finished early
        due to the `eos_token_id`.
"""
class BeamScorer(ABC):
    @abstractmethod
    @add_start_docstrings(PROCESS_INPUTS_DOCSTRING)
    def process(self, input_ids: torch.LongTensor, next_scores: torch.FloatTensor, next_tokens: torch.LongTensor, next_indices: torch.LongTensor, **kwargs) -> Tuple[torch.Tensor]: raise NotImplementedError("This is an abstract method.")
    @abstractmethod
    @add_start_docstrings(FINALIZE_INPUTS_DOCSTRING)
    def finalize(self, input_ids: torch.LongTensor, next_scores: torch.FloatTensor, next_tokens: torch.LongTensor, next_indices: torch.LongTensor, max_length: int, **kwargs) -> torch.LongTensor: raise NotImplementedError("This is an abstract method.")
class BeamSearchScorer(BeamScorer):
    def __init__(self, batch_size: int, num_beams: int, device: torch.device, length_penalty: Optional[float] = 1.0, do_early_stopping: Optional[Union[bool, str]] = False,
    num_beam_hyps_to_keep: Optional[int] = 1, num_beam_groups: Optional[int] = 1, max_length: Optional[int] = None):
        self.num_beams = num_beams
        self.device = device
        self.length_penalty = length_penalty
        self.do_early_stopping = do_early_stopping
        self.num_beam_hyps_to_keep = num_beam_hyps_to_keep
        self.num_beam_groups = num_beam_groups
        self.group_size = self.num_beams // self.num_beam_groups
        self._is_init = False
        self._beam_hyps = [BeamHypotheses(num_beams=self.group_size, length_penalty=self.length_penalty, early_stopping=self.do_early_stopping, max_length=max_length) for _ in range(batch_size * self.num_beam_groups)]
        self._done = torch.tensor([False for _ in range(batch_size * self.num_beam_groups)], dtype=torch.bool, device=self.device)
        if not isinstance(num_beams, int) or num_beams <= 1: raise ValueError(f"`num_beams` has to be an integer strictly greater than 1, but is {num_beams}. For `num_beams` == 1, one should make use of `greedy_search` instead.")
        if not isinstance(num_beam_groups, int) or (num_beam_groups > num_beams) or (num_beams % num_beam_groups != 0): raise ValueError(f"`num_beam_groups` has to be an integer smaller or equal than `num_beams` and `num_beams` has to be divisible by `num_beam_groups`, but is {num_beam_groups} with `num_beams` being {num_beams}.")
    @property
    def is_done(self) -> bool: return self._done.all()
    def process(self, input_ids: torch.LongTensor, next_scores: torch.FloatTensor, next_tokens: torch.LongTensor, next_indices: torch.LongTensor, pad_token_id: Optional[Union[int, torch.Tensor]] = None,
    eos_token_id: Optional[Union[int, List[int], torch.Tensor]] = None, beam_indices: Optional[torch.LongTensor] = None, group_index: Optional[int] = 0, decoder_prompt_len: Optional[int] = 0) -> Dict[str, torch.Tensor]:
        cur_len = input_ids.shape[-1] + 1
        batch_size = len(self._beam_hyps) // self.num_beam_groups
        if not (batch_size == (input_ids.shape[0] // self.group_size)):
            if self.num_beam_groups > 1: raise ValueError(f"A group beam size of {input_ids.shape[0]} is used as the input, but a group beam size of {self.group_size} is expected by the beam scorer.")
            else: raise ValueError(f"A beam size of {input_ids.shape[0]} is used as the input, but a beam size of {self.group_size} is expected by the beam scorer.")
        device = input_ids.device
        next_beam_scores = torch.zeros((batch_size, self.group_size), dtype=next_scores.dtype, device=device)
        next_beam_tokens = torch.zeros((batch_size, self.group_size), dtype=next_tokens.dtype, device=device)
        next_beam_indices = torch.zeros((batch_size, self.group_size), dtype=next_indices.dtype, device=device)
        if eos_token_id is not None and not isinstance(eos_token_id, torch.Tensor):
            if isinstance(eos_token_id, int): eos_token_id = [eos_token_id]
            eos_token_id = torch.tensor(eos_token_id)
        for batch_idx in range(batch_size):
            batch_group_idx = batch_idx * self.num_beam_groups + group_index
            if self._done[batch_group_idx]:
                if self.num_beams < len(self._beam_hyps[batch_group_idx]): raise ValueError(f"Batch can only be done if at least {self.num_beams} beams have been generated")
                if eos_token_id is None or pad_token_id is None: raise ValueError("Generated beams >= num_beams -> eos_token_id and pad_token have to be defined")
                next_beam_scores[batch_idx, :] = 0
                next_beam_tokens[batch_idx, :] = pad_token_id
                next_beam_indices[batch_idx, :] = 0
                continue
            beam_idx = 0
            for beam_token_rank, (next_token, next_score, next_index) in enumerate(zip(next_tokens[batch_idx], next_scores[batch_idx], next_indices[batch_idx])):
                batch_beam_idx = batch_idx * self.group_size + next_index
                if (eos_token_id is not None) and (next_token.item() in eos_token_id):
                    is_beam_token_worse_than_top_num_beams = beam_token_rank >= self.group_size
                    if is_beam_token_worse_than_top_num_beams: continue
                    if beam_indices is not None:
                        beam_index = beam_indices[batch_beam_idx]
                        beam_index = beam_index + (batch_beam_idx,)
                    else: beam_index = None
                    self._beam_hyps[batch_group_idx].add(input_ids[batch_beam_idx].clone(), next_score.item(), beam_indices=beam_index, generated_len=cur_len - decoder_prompt_len)
                else:
                    next_beam_scores[batch_idx, beam_idx] = next_score
                    next_beam_tokens[batch_idx, beam_idx] = next_token
                    next_beam_indices[batch_idx, beam_idx] = batch_beam_idx
                    beam_idx += 1
                if beam_idx == self.group_size: break
            if beam_idx < self.group_size: raise ValueError(f"At most {self.group_size} tokens in {next_tokens[batch_idx]} can be equal to `eos_token_id: {eos_token_id}`. Make sure {next_tokens[batch_idx]} are corrected.")
            self._done[batch_group_idx] = self._done[batch_group_idx] or self._beam_hyps[batch_group_idx].is_done(next_scores[batch_idx].max().item(), cur_len, decoder_prompt_len)
        return UserDict({"next_beam_scores": next_beam_scores.view(-1), "next_beam_tokens": next_beam_tokens.view(-1), "next_beam_indices": next_beam_indices.view(-1)})
    def finalize(self, input_ids: torch.LongTensor, final_beam_scores: torch.FloatTensor, final_beam_tokens: torch.LongTensor, final_beam_indices: torch.LongTensor, max_length: int, pad_token_id: Optional[Union[int, torch.Tensor]] = None,
    eos_token_id: Optional[Union[int, List[int], torch.Tensor]] = None, beam_indices: Optional[torch.LongTensor] = None, decoder_prompt_len: Optional[int] = 0) -> Tuple[torch.LongTensor]:
        batch_size = len(self._beam_hyps) // self.num_beam_groups
        if eos_token_id is not None and not isinstance(eos_token_id, torch.Tensor):
            if isinstance(eos_token_id, int): eos_token_id = [eos_token_id]
            eos_token_id = torch.tensor(eos_token_id)
        for batch_group_idx, beam_hyp in enumerate(self._beam_hyps):
            if self._done[batch_group_idx]: continue
            for index_per_group in range(self.group_size):
                batch_beam_idx = batch_group_idx * self.group_size + index_per_group
                final_score = final_beam_scores[batch_beam_idx].item()
                final_tokens = input_ids[batch_beam_idx]
                beam_index = beam_indices[batch_beam_idx] if beam_indices is not None else None
                generated_len = final_tokens.shape[-1] - decoder_prompt_len
                beam_hyp.add(final_tokens, final_score, beam_indices=beam_index, generated_len=generated_len)
        sent_lengths = input_ids.new(batch_size * self.num_beam_hyps_to_keep)
        best = []
        best_indices = []
        best_scores = torch.zeros(batch_size * self.num_beam_hyps_to_keep, device=self.device, dtype=torch.float32)
        for i in range(batch_size):
            beam_hyps_in_batch = self._beam_hyps[i * self.num_beam_groups : (i + 1) * self.num_beam_groups]
            candidate_beams = [beam for beam_hyp in beam_hyps_in_batch for beam in beam_hyp.beams]
            sorted_hyps = sorted(candidate_beams, key=lambda x: x[0])
            for j in range(self.num_beam_hyps_to_keep):
                best_hyp_tuple = sorted_hyps.pop()
                best_score = best_hyp_tuple[0]
                best_hyp = best_hyp_tuple[1]
                best_index = best_hyp_tuple[2]
                sent_lengths[self.num_beam_hyps_to_keep * i + j] = len(best_hyp)
                best.append(best_hyp)
                best_indices.append(best_index)
                best_scores[i * self.num_beam_hyps_to_keep + j] = best_score
        sent_lengths_max = sent_lengths.max().item() + 1
        sent_max_len = min(sent_lengths_max, max_length) if max_length is not None else sent_lengths_max
        decoded: torch.LongTensor = input_ids.new(batch_size * self.num_beam_hyps_to_keep, sent_max_len)
        if len(best_indices) > 0 and best_indices[0] is not None: indices: torch.LongTensor = input_ids.new(batch_size * self.num_beam_hyps_to_keep, sent_max_len)
        else: indices = None
        if sent_lengths.min().item() != sent_lengths.max().item():
            if pad_token_id is None: raise ValueError("`pad_token_id` has to be defined")
            decoded.fill_(pad_token_id)
        if indices is not None: indices.fill_(-1)
        for i, (hypo, best_idx) in enumerate(zip(best, best_indices)):
            decoded[i, : sent_lengths[i]] = hypo
            if indices is not None: indices[i, : len(best_idx)] = torch.tensor(best_idx)
            if sent_lengths[i] < sent_max_len: decoded[i, sent_lengths[i]] = eos_token_id[0]
        return UserDict({"sequences": decoded, "sequence_scores": best_scores, "beam_indices": indices})
class ConstrainedBeamSearchScorer(BeamScorer):
    def __init__(self, batch_size: int, num_beams: int, constraints: List[Constraint], device: torch.device, length_penalty: Optional[float] = 1.0, do_early_stopping: Optional[Union[bool, str]] = False, num_beam_hyps_to_keep: Optional[int] = 1, num_beam_groups: Optional[int] = 1, max_length: Optional[int] = None):
        self.num_beams = num_beams
        self.device = device
        self.length_penalty = length_penalty
        self.do_early_stopping = do_early_stopping
        self.num_beam_hyps_to_keep = num_beam_hyps_to_keep
        self.num_beam_groups = num_beam_groups
        self.group_size = self.num_beams // self.num_beam_groups
        self.constraints = constraints
        self._is_init = False
        self._beam_hyps = [BeamHypotheses(num_beams=self.num_beams, length_penalty=self.length_penalty, early_stopping=self.do_early_stopping, max_length=max_length) for _ in range(batch_size)]
        self._done = torch.tensor([False for _ in range(batch_size)], dtype=torch.bool, device=self.device)
        if not isinstance(num_beams, int) or num_beams <= 1: raise ValueError(f"`num_beams` has to be an integer strictly greater than 1, but is {num_beams}. For `num_beams` == 1, one should make use of `greedy_search` instead.")
        if not isinstance(num_beam_groups, int) or (num_beam_groups > num_beams) or (num_beams % num_beam_groups != 0): raise ValueError(f"`num_beam_groups` has to be an integer smaller or equal than `num_beams` and `num_beams` has to be divisible by `num_beam_groups`, but is {num_beam_groups} with `num_beams` being {num_beams}.")
    @property
    def is_done(self) -> bool: return self._done.all()
    def make_constraint_states(self, n): return [ConstraintListState([constraint.copy() for constraint in self.constraints]) for _ in range(n)]
    def check_completes_constraints(self, sequence):
        new_state = self.make_constraint_states(1)[0]
        new_state.reset(sequence)
        return new_state.completed
    def process(self, input_ids: torch.LongTensor, next_scores: torch.FloatTensor, next_tokens: torch.LongTensor, next_indices: torch.LongTensor, scores_for_all_vocab: torch.FloatTensor, pad_token_id: Optional[Union[int, torch.Tensor]] = None, eos_token_id: Optional[Union[int, List[int],
    torch.Tensor]] = None, beam_indices: Optional[torch.LongTensor] = None, decoder_prompt_len: Optional[int] = 0) -> Tuple[torch.Tensor]:
        cur_len = input_ids.shape[-1] + 1
        batch_size = len(self._beam_hyps)
        if not (batch_size == (input_ids.shape[0] // self.group_size)):
            if self.num_beam_groups > 1: raise ValueError(f"A group beam size of {input_ids.shape[0]} is used as the input, but a group beam size of {self.group_size} is expected by the beam scorer.")
            else: raise ValueError(f"A beam size of {input_ids.shape[0]} is used as the input, but a beam size of {self.group_size} is expected by the beam scorer.")
        device = input_ids.device
        next_beam_scores = torch.zeros((batch_size, self.group_size), dtype=next_scores.dtype, device=device)
        next_beam_tokens = torch.zeros((batch_size, self.group_size), dtype=next_tokens.dtype, device=device)
        next_beam_indices = torch.zeros((batch_size, self.group_size), dtype=next_indices.dtype, device=device)
        if eos_token_id is not None and not isinstance(eos_token_id, torch.Tensor):
            if isinstance(eos_token_id, int): eos_token_id = [eos_token_id]
            eos_token_id = torch.tensor(eos_token_id)
        for batch_idx, beam_hyp in enumerate(self._beam_hyps):
            if self._done[batch_idx]:
                if self.num_beams < len(beam_hyp): raise ValueError(f"Batch can only be done if at least {self.num_beams} beams have been generated")
                if eos_token_id is None or pad_token_id is None: raise ValueError("Generated beams >= num_beams -> eos_token_id and pad_token have to be defined")
                next_beam_scores[batch_idx, :] = 0
                next_beam_tokens[batch_idx, :] = pad_token_id
                next_beam_indices[batch_idx, :] = 0
                continue
            beam_idx = 0
            for beam_token_rank, (next_token, next_score, next_index) in enumerate(zip(next_tokens[batch_idx], next_scores[batch_idx], next_indices[batch_idx])):
                batch_beam_idx = batch_idx * self.group_size + next_index
                if (eos_token_id is not None) and (next_token.item() in eos_token_id):
                    is_beam_token_worse_than_top_num_beams = beam_token_rank >= self.group_size
                    if is_beam_token_worse_than_top_num_beams: continue
                    completes_constraint = self.check_completes_constraints(input_ids[batch_beam_idx].cpu().tolist())
                    if completes_constraint:
                        if beam_indices is not None:
                            beam_index = beam_indices[batch_beam_idx]
                            beam_index = beam_index + (batch_beam_idx,)
                        else: beam_index = None
                        beam_hyp.add(input_ids[batch_beam_idx].clone(), next_score.item(), beam_indices=beam_index, generated_len=cur_len - decoder_prompt_len)
                else:
                    next_beam_scores[batch_idx, beam_idx] = next_score
                    next_beam_tokens[batch_idx, beam_idx] = next_token
                    next_beam_indices[batch_idx, beam_idx] = batch_beam_idx
                    beam_idx += 1
                if beam_idx == self.group_size: break
            new_scores, new_tokens, new_indices = self.step_sentence_constraint(batch_idx, input_ids, scores_for_all_vocab, next_beam_scores[batch_idx], next_beam_tokens[batch_idx], next_beam_indices[batch_idx])
            next_beam_scores[batch_idx] = new_scores
            next_beam_tokens[batch_idx] = new_tokens
            next_beam_indices[batch_idx] = new_indices
            if beam_idx < self.group_size: raise ValueError(f"At most {self.group_size} tokens in {next_tokens[batch_idx]} can be equal to `eos_token_id: {eos_token_id}`. Make sure {next_tokens[batch_idx]} are corrected.")
            self._done[batch_idx] = self._done[batch_idx] or beam_hyp.is_done(next_scores[batch_idx].max().item(), cur_len, decoder_prompt_len)
        return UserDict({"next_beam_scores": next_beam_scores.view(-1), "next_beam_tokens": next_beam_tokens.view(-1), "next_beam_indices": next_beam_indices.view(-1)})
    def step_sentence_constraint(self, batch_idx: int, input_ids: torch.LongTensor, vocab_scores: torch.FloatTensor, sent_beam_scores: torch.FloatTensor, sent_beam_tokens: torch.LongTensor, sent_beam_indices: torch.LongTensor, push_progress: bool = False):
        orig_len = sent_beam_indices.size(0)
        device = sent_beam_indices.device
        topk_contraint_states = self.make_constraint_states(orig_len)
        advance_constraint_states = self.make_constraint_states(orig_len)
        sidx, eidx = batch_idx * orig_len, (batch_idx + 1) * orig_len
        this_batch_input_ids = input_ids[sidx:eidx]
        this_batch_token_scores = vocab_scores[sidx:eidx]
        full_hypotheses = torch.cat((input_ids[sent_beam_indices], sent_beam_tokens.unsqueeze(-1)), dim=-1)
        track_new = {"new_seqs": full_hypotheses.tolist(), "new_states": [], "new_indices": [], "new_tokens": [], "new_scores": []}
        for seq_idx, pre_seq in enumerate(this_batch_input_ids):
            topk_state = topk_contraint_states[seq_idx]
            topk_state.reset(full_hypotheses[seq_idx].cpu().tolist())
            advance_state = advance_constraint_states[seq_idx]
            advance_state.reset(pre_seq.cpu().tolist())
            if not advance_state.completed:
                advance_tokens = torch.LongTensor(advance_state.advance()).to(device)
                for advance_token in advance_tokens:
                    new_state = advance_state.copy(stateful=True)
                    new_state.add(advance_token.cpu().tolist())
                    advance_seq = torch.cat((pre_seq, advance_token.unsqueeze(0)), -1).cpu().tolist()
                    if advance_seq not in track_new["new_seqs"]:
                        track_new["new_seqs"].append(advance_seq)
                        track_new["new_indices"].append(sidx + seq_idx)
                        track_new["new_tokens"].append(advance_token)
                        track_new["new_scores"].append(this_batch_token_scores[seq_idx].take(advance_token))
                        track_new["new_states"].append(new_state)
            elif push_progress:
                new_score, new_token = torch.max(this_batch_token_scores[seq_idx], 0)
                advance_seq = torch.cat((pre_seq, new_token.unsqueeze(0)), -1)
                advance_state = advance_constraint_states[seq_idx]
                advance_seq = advance_seq.cpu().tolist()
                advance_state.reset(advance_seq)
                if advance_seq not in track_new["new_seqs"]:
                    track_new["new_seqs"].append(advance_seq)
                    track_new["new_indices"].append(seq_idx)
                    track_new["new_tokens"].append(new_token)
                    track_new["new_scores"].append(new_score)
                    track_new["new_states"].append(advance_state)
        if len(track_new["new_indices"]) > 0:
            new_indices = torch.tensor(track_new["new_indices"]).to(device)
            new_tokens = torch.stack(track_new["new_tokens"]).to(device)
            new_scores = torch.stack(track_new["new_scores"]).to(device)
            all_states = topk_contraint_states + track_new["new_states"]
            all_tokens = torch.cat((sent_beam_tokens, new_tokens), -1)
            all_scores = torch.cat((sent_beam_scores, new_scores), -1)
            all_banks = torch.tensor([one.get_bank() for one in all_states]).to(device)
            zipped = all_banks * 100 + all_scores
            indices = zipped.sort(descending=True).indices
            sorted_banks = all_banks[indices]
            counter = -1
            cur_bank = sorted_banks[0]
            increments = []
            for bank in sorted_banks:
                if bank == cur_bank: counter += 1
                else:
                    counter = 0
                    cur_bank = bank
                increments.append(counter)
            rearrangers = torch.tensor(np.argsort(increments, kind="mergesort"))
            indices = indices[rearrangers][:orig_len]
            sent_beam_scores = all_scores[indices]
            sent_beam_tokens = all_tokens[indices]
            sent_beam_indices = torch.cat((sent_beam_indices, new_indices))[indices]
        return sent_beam_scores, sent_beam_tokens, sent_beam_indices
    def finalize(self, input_ids: torch.LongTensor, final_beam_scores: torch.FloatTensor, final_beam_tokens: torch.LongTensor, final_beam_indices: torch.LongTensor, max_length: int,
    pad_token_id: Optional[Union[int, torch.Tensor]] = None, eos_token_id: Optional[Union[int, List[int], torch.Tensor]] = None, beam_indices: Optional[torch.LongTensor] = None, decoder_prompt_len: Optional[int] = 0) -> Tuple[torch.LongTensor]:
        batch_size = len(self._beam_hyps)
        if eos_token_id is not None and not isinstance(eos_token_id, torch.Tensor):
            if isinstance(eos_token_id, int): eos_token_id = [eos_token_id]
            eos_token_id = torch.tensor(eos_token_id)
        for batch_idx, beam_hyp in enumerate(self._beam_hyps):
            if self._done[batch_idx]: continue
            ids_collect = []
            for beam_id in range(self.num_beams):
                batch_beam_idx = batch_idx * self.num_beams + beam_id
                final_score = final_beam_scores[batch_beam_idx].item()
                final_tokens = input_ids[batch_beam_idx]
                completes_constraint = self.check_completes_constraints(final_tokens.cpu().tolist())
                if completes_constraint:
                    beam_index = beam_indices[batch_beam_idx] if beam_indices is not None else None
                    generated_len = final_tokens.shape[-1] - decoder_prompt_len
                    beam_hyp.add(final_tokens, final_score, beam_indices=beam_index, generated_len=generated_len)
                    ids_collect.append(beam_id)
            if len(ids_collect) < self.num_beam_hyps_to_keep:
                for beam_id in range(self.num_beams):
                    if beam_id not in ids_collect:
                        batch_beam_idx = batch_idx * self.num_beams + beam_id
                        final_score = final_beam_scores[batch_beam_idx].item()
                        final_tokens = input_ids[batch_beam_idx]
                        generated_len = final_tokens.shape[-1] - decoder_prompt_len
                        beam_hyp.add(final_tokens, final_score, generated_len=generated_len)
                    if len(ids_collect) >= self.num_beam_hyps_to_keep: break
        sent_lengths = input_ids.new(batch_size * self.num_beam_hyps_to_keep)
        best = []
        best_indices = []
        best_scores = torch.zeros(batch_size * self.num_beam_hyps_to_keep, device=self.device, dtype=torch.float32)
        for i, beam_hyp in enumerate(self._beam_hyps):
            sorted_hyps = sorted(beam_hyp.beams, key=lambda x: x[0])
            for j in range(self.num_beam_hyps_to_keep):
                best_hyp_tuple = sorted_hyps.pop()
                best_score = best_hyp_tuple[0]
                best_hyp = best_hyp_tuple[1]
                best_index = best_hyp_tuple[2]
                sent_lengths[self.num_beam_hyps_to_keep * i + j] = len(best_hyp)
                best.append(best_hyp)
                best_indices.append(best_index)
                best_scores[i * self.num_beam_hyps_to_keep + j] = best_score
        sent_lengths_max = sent_lengths.max().item() + 1
        sent_max_len = min(sent_lengths_max, max_length) if max_length is not None else sent_lengths_max
        decoded: torch.LongTensor = input_ids.new(batch_size * self.num_beam_hyps_to_keep, sent_max_len)
        if len(best_indices) > 0 and best_indices[0] is not None: indices: torch.LongTensor = input_ids.new(batch_size * self.num_beam_hyps_to_keep, sent_max_len)
        else: indices = None
        if sent_lengths.min().item() != sent_lengths.max().item():
            if pad_token_id is None: raise ValueError("`pad_token_id` has to be defined")
            decoded.fill_(pad_token_id)
        if indices is not None: indices.fill_(-1)
        for i, (hypo, best_idx) in enumerate(zip(best, best_indices)):
            decoded[i, : sent_lengths[i]] = hypo
            if indices is not None: indices[i, : len(best_idx)] = torch.tensor(best_idx)
            if sent_lengths[i] < sent_max_len: decoded[i, sent_lengths[i]] = eos_token_id[0]
        return UserDict({"sequences": decoded, "sequence_scores": best_scores, "beam_indices": indices})
class BeamHypotheses:
    def __init__(self, num_beams: int, length_penalty: float, early_stopping: bool, max_length: Optional[int] = None):
        self.length_penalty = length_penalty
        self.early_stopping = early_stopping
        self.max_length = max_length
        self.num_beams = num_beams
        self.beams = []
        self.worst_score = 1e9
        if not isinstance(self.early_stopping, bool) and self.max_length is None: raise ValueError("When `do_early_stopping` is set to a string, `max_length` must be defined. Ensure it is passed to the BeamScorer class instance at initialization time.")
    def __len__(self): return len(self.beams)
    def add(self, hyp: torch.LongTensor, sum_logprobs: float, beam_indices: Optional[torch.LongTensor] = None, generated_len: Optional[int] = None):
        if generated_len is not None: score = sum_logprobs / (generated_len**self.length_penalty)
        else: score = sum_logprobs / (hyp.shape[-1] ** self.length_penalty)
        if len(self) < self.num_beams or score > self.worst_score:
            self.beams.append((score, hyp, beam_indices))
            if len(self) > self.num_beams:
                sorted_next_scores = sorted([(s, idx) for idx, (s, _, _) in enumerate(self.beams)])
                del self.beams[sorted_next_scores[0][1]]
                self.worst_score = sorted_next_scores[1][0]
            else: self.worst_score = min(score, self.worst_score)
    def is_done(self, best_sum_logprobs: float, cur_len: int, decoder_prompt_len: Optional[int] = 0) -> bool:
        if len(self) < self.num_beams: return False
        if self.early_stopping is True: return True
        elif self.early_stopping is False:
            highest_attainable_score = best_sum_logprobs / (cur_len - decoder_prompt_len) ** self.length_penalty
            ret = self.worst_score >= highest_attainable_score
            return ret
        else:
            if self.length_penalty > 0.0:
                if self.max_length <= decoder_prompt_len: raise ValueError("max_length is not larger than decoder prompt length")
                highest_attainable_score = (best_sum_logprobs / (self.max_length - decoder_prompt_len) ** self.length_penalty)
            else: highest_attainable_score = best_sum_logprobs / (cur_len - decoder_prompt_len) ** self.length_penalty
            ret = self.worst_score >= highest_attainable_score
            return ret
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
