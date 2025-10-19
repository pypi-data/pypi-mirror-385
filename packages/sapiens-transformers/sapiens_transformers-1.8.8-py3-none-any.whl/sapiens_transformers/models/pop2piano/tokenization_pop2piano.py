"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import json
import os
from typing import List, Optional, Tuple, Union
import numpy as np
from ...feature_extraction_utils import BatchFeature
from ...tokenization_utils import AddedToken, BatchEncoding, PaddingStrategy, PreTrainedTokenizer, TruncationStrategy
from ...utils import TensorType, is_pretty_midi_available, logging, requires_backends, to_numpy
if is_pretty_midi_available(): import pretty_midi
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {'vocab': 'vocab.json'}
def token_time_to_note(number, cutoff_time_idx, current_idx):
    current_idx += number
    if cutoff_time_idx is not None: current_idx = min(current_idx, cutoff_time_idx)
    return current_idx
def token_note_to_note(number, current_velocity, default_velocity, note_onsets_ready, current_idx, notes):
    if note_onsets_ready[number] is not None:
        onset_idx = note_onsets_ready[number]
        if onset_idx < current_idx:
            offset_idx = current_idx
            notes.append([onset_idx, offset_idx, number, default_velocity])
            onsets_ready = None if current_velocity == 0 else current_idx
            note_onsets_ready[number] = onsets_ready
    else: note_onsets_ready[number] = current_idx
    return notes
class Pop2PianoTokenizer(PreTrainedTokenizer):
    model_input_names = ["token_ids", "attention_mask"]
    vocab_files_names = VOCAB_FILES_NAMES
    def __init__(self, vocab, default_velocity=77, num_bars=2, unk_token="-1", eos_token="1", pad_token="0", bos_token="2", **kwargs):
        unk_token = AddedToken(unk_token, lstrip=False, rstrip=False) if isinstance(unk_token, str) else unk_token
        eos_token = AddedToken(eos_token, lstrip=False, rstrip=False) if isinstance(eos_token, str) else eos_token
        pad_token = AddedToken(pad_token, lstrip=False, rstrip=False) if isinstance(pad_token, str) else pad_token
        bos_token = AddedToken(bos_token, lstrip=False, rstrip=False) if isinstance(bos_token, str) else bos_token
        self.default_velocity = default_velocity
        self.num_bars = num_bars
        with open(vocab, "rb") as file: self.encoder = json.load(file)
        self.decoder = {v: k for k, v in self.encoder.items()}
        super().__init__(unk_token=unk_token, eos_token=eos_token, pad_token=pad_token, bos_token=bos_token, **kwargs)
    @property
    def vocab_size(self): return len(self.encoder)
    def get_vocab(self): return dict(self.encoder, **self.added_tokens_encoder)
    def _convert_id_to_token(self, token_id: int) -> list:
        token_type_value = self.decoder.get(token_id, f"{self.unk_token}_TOKEN_TIME")
        token_type_value = token_type_value.split("_")
        token_type, value = "_".join(token_type_value[1:]), int(token_type_value[0])
        return [token_type, value]
    def _convert_token_to_id(self, token, token_type="TOKEN_TIME") -> int: return self.encoder.get(f"{token}_{token_type}", int(self.unk_token))
    def relative_batch_tokens_ids_to_notes(self, tokens: np.ndarray, beat_offset_idx: int, bars_per_batch: int, cutoff_time_idx: int):
        notes = None
        for index in range(len(tokens)):
            _tokens = tokens[index]
            _start_idx = beat_offset_idx + index * bars_per_batch * 4
            _cutoff_time_idx = cutoff_time_idx + _start_idx
            _notes = self.relative_tokens_ids_to_notes(_tokens, start_idx=_start_idx, cutoff_time_idx=_cutoff_time_idx)
            if len(_notes) == 0: pass
            elif notes is None: notes = _notes
            else: notes = np.concatenate((notes, _notes), axis=0)
        if notes is None: return []
        return notes
    def relative_batch_tokens_ids_to_midi(self, tokens: np.ndarray, beatstep: np.ndarray, beat_offset_idx: int = 0, bars_per_batch: int = 2, cutoff_time_idx: int = 12):
        beat_offset_idx = 0 if beat_offset_idx is None else beat_offset_idx
        notes = self.relative_batch_tokens_ids_to_notes(tokens=tokens, beat_offset_idx=beat_offset_idx, bars_per_batch=bars_per_batch, cutoff_time_idx=cutoff_time_idx)
        midi = self.notes_to_midi(notes, beatstep, offset_sec=beatstep[beat_offset_idx])
        return midi
    def relative_tokens_ids_to_notes(self, tokens: np.ndarray, start_idx: float, cutoff_time_idx: float = None):
        words = [self._convert_id_to_token(token) for token in tokens]
        current_idx = start_idx
        current_velocity = 0
        note_onsets_ready = [None for i in range(sum([k.endswith("NOTE") for k in self.encoder.keys()]) + 1)]
        notes = []
        for token_type, number in words:
            if token_type == "TOKEN_SPECIAL":
                if number == 1: break
            elif token_type == "TOKEN_TIME": current_idx = token_time_to_note(number=number, cutoff_time_idx=cutoff_time_idx, current_idx=current_idx)
            elif token_type == "TOKEN_VELOCITY": current_velocity = number
            elif token_type == "TOKEN_NOTE": notes = token_note_to_note(number=number, current_velocity=current_velocity, default_velocity=self.default_velocity,
            note_onsets_ready=note_onsets_ready, current_idx=current_idx, notes=notes)
            else: raise ValueError("Token type not understood!")
        for pitch, note_onset in enumerate(note_onsets_ready):
            if note_onset is not None:
                if cutoff_time_idx is None: cutoff = note_onset + 1
                else: cutoff = max(cutoff_time_idx, note_onset + 1)
                offset_idx = max(current_idx, cutoff)
                notes.append([note_onset, offset_idx, pitch, self.default_velocity])
        if len(notes) == 0: return []
        else:
            notes = np.array(notes)
            note_order = notes[:, 0] * 128 + notes[:, 1]
            notes = notes[note_order.argsort()]
            return notes
    def notes_to_midi(self, notes: np.ndarray, beatstep: np.ndarray, offset_sec: int = 0.0):
        requires_backends(self, ["pretty_midi"])
        new_pm = pretty_midi.PrettyMIDI(resolution=384, initial_tempo=120.0)
        new_inst = pretty_midi.Instrument(program=0)
        new_notes = []
        for onset_idx, offset_idx, pitch, velocity in notes:
            new_note = pretty_midi.Note(velocity=velocity, pitch=pitch, start=beatstep[onset_idx] - offset_sec, end=beatstep[offset_idx] - offset_sec)
            new_notes.append(new_note)
        new_inst.notes = new_notes
        new_pm.instruments.append(new_inst)
        new_pm.remove_invalid_notes()
        return new_pm
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        if not os.path.isdir(save_directory):
            logger.error(f"Vocabulary path ({save_directory}) should be a directory")
            return
        out_vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab"])
        with open(out_vocab_file, "w") as file: file.write(json.dumps(self.encoder))
        return (out_vocab_file,)
    def encode_plus(self, notes: Union[np.ndarray, List[pretty_midi.Note]], truncation_strategy: Optional[TruncationStrategy] = None, max_length: Optional[int] = None, **kwargs) -> BatchEncoding:
        requires_backends(self, ["pretty_midi"])
        if isinstance(notes[0], pretty_midi.Note): notes = np.array([[each_note.start, each_note.end, each_note.pitch, each_note.velocity] for each_note in notes]).reshape(-1, 4)
        notes = np.round(notes).astype(np.int32)
        max_time_idx = notes[:, :2].max()
        times = [[] for i in range((max_time_idx + 1))]
        for onset, offset, pitch, velocity in notes:
            times[onset].append([pitch, velocity])
            times[offset].append([pitch, 0])
        tokens = []
        current_velocity = 0
        for i, time in enumerate(times):
            if len(time) == 0: continue
            tokens.append(self._convert_token_to_id(i, "TOKEN_TIME"))
            for pitch, velocity in time:
                velocity = int(velocity > 0)
                if current_velocity != velocity:
                    current_velocity = velocity
                    tokens.append(self._convert_token_to_id(velocity, "TOKEN_VELOCITY"))
                tokens.append(self._convert_token_to_id(pitch, "TOKEN_NOTE"))
        total_len = len(tokens)
        if truncation_strategy != TruncationStrategy.DO_NOT_TRUNCATE and max_length and total_len > max_length: tokens, _, _ = self.truncate_sequences(ids=tokens,
        num_tokens_to_remove=total_len - max_length, truncation_strategy=truncation_strategy, **kwargs)
        return BatchEncoding({"token_ids": tokens})
    def batch_encode_plus(self, notes: Union[np.ndarray, List[pretty_midi.Note]], truncation_strategy: Optional[TruncationStrategy] = None, max_length: Optional[int] = None, **kwargs) -> BatchEncoding:
        encoded_batch_token_ids = []
        for i in range(len(notes)): encoded_batch_token_ids.append(self.encode_plus(notes[i], truncation_strategy=truncation_strategy, max_length=max_length, **kwargs)["token_ids"])
        return BatchEncoding({"token_ids": encoded_batch_token_ids})
    def __call__(self, notes: Union[np.ndarray, List[pretty_midi.Note], List[List[pretty_midi.Note]]], padding: Union[bool, str, PaddingStrategy] = False,
    truncation: Union[bool, str, TruncationStrategy] = None, max_length: Optional[int] = None, pad_to_multiple_of: Optional[int] = None, return_attention_mask: Optional[bool] = None,
    return_tensors: Optional[Union[str, TensorType]] = None, verbose: bool = True, **kwargs) -> BatchEncoding:
        is_batched = notes.ndim == 3 if isinstance(notes, np.ndarray) else isinstance(notes[0], list)
        padding_strategy, truncation_strategy, max_length, kwargs = self._get_padding_truncation_strategies(padding=padding, truncation=truncation, max_length=max_length,
        pad_to_multiple_of=pad_to_multiple_of, verbose=verbose, **kwargs)
        if is_batched:
            return_attention_mask = True if return_attention_mask is None else return_attention_mask
            token_ids = self.batch_encode_plus(notes=notes, truncation_strategy=truncation_strategy, max_length=max_length, **kwargs)
        else: token_ids = self.encode_plus(notes=notes, truncation_strategy=truncation_strategy, max_length=max_length, **kwargs)
        token_ids = self.pad(token_ids, padding=padding_strategy, max_length=max_length, pad_to_multiple_of=pad_to_multiple_of, return_attention_mask=return_attention_mask,
        return_tensors=return_tensors, verbose=verbose)
        return token_ids
    def batch_decode(self, token_ids, feature_extractor_output: BatchFeature, return_midi: bool = True):
        attention_masks_present = bool(hasattr(feature_extractor_output, "attention_mask") and hasattr(feature_extractor_output, "attention_mask_beatsteps") and hasattr(feature_extractor_output, "attention_mask_extrapolated_beatstep"))
        if not attention_masks_present and feature_extractor_output["beatsteps"].shape[0] > 1: raise ValueError("attention_mask, attention_mask_beatsteps and attention_mask_extrapolated_beatstep must be present for batched inputs! But one of them were not present.")
        if attention_masks_present:
            if (sum(feature_extractor_output["attention_mask"][:, 0] == 0) != feature_extractor_output["beatsteps"].shape[0] or feature_extractor_output["beatsteps"].shape[0] != feature_extractor_output["extrapolated_beatstep"].shape[0]): raise ValueError(f"Length mistamtch between token_ids, beatsteps and extrapolated_beatstep! Found token_ids length - {token_ids.shape[0]}, beatsteps shape - {feature_extractor_output['beatsteps'].shape[0]} and extrapolated_beatsteps shape - {feature_extractor_output['extrapolated_beatstep'].shape[0]}")
            if feature_extractor_output["attention_mask"].shape[0] != token_ids.shape[0]: raise ValueError(f"Found attention_mask of length - {feature_extractor_output['attention_mask'].shape[0]} but token_ids of length - {token_ids.shape[0]}")
        else:
            if (feature_extractor_output["beatsteps"].shape[0] != 1 or feature_extractor_output["extrapolated_beatstep"].shape[0] != 1): raise ValueError(f"Length mistamtch of beatsteps and extrapolated_beatstep! Since attention_mask is not present the number of examples must be 1, But found beatsteps length - {feature_extractor_output['beatsteps'].shape[0]}, extrapolated_beatsteps length - {feature_extractor_output['extrapolated_beatstep'].shape[0]}.")
        if attention_masks_present: batch_idx = np.where(feature_extractor_output["attention_mask"][:, 0] == 0)[0]
        else: batch_idx = [token_ids.shape[0]]
        notes_list = []
        pretty_midi_objects_list = []
        start_idx = 0
        for index, end_idx in enumerate(batch_idx):
            each_tokens_ids = token_ids[start_idx:end_idx]
            each_tokens_ids = each_tokens_ids[:, : np.max(np.where(each_tokens_ids == int(self.eos_token))[1]) + 1]
            beatsteps = feature_extractor_output["beatsteps"][index]
            extrapolated_beatstep = feature_extractor_output["extrapolated_beatstep"][index]
            if attention_masks_present:
                attention_mask_beatsteps = feature_extractor_output["attention_mask_beatsteps"][index]
                attention_mask_extrapolated_beatstep = feature_extractor_output["attention_mask_extrapolated_beatstep"][index]
                beatsteps = beatsteps[: np.max(np.where(attention_mask_beatsteps == 1)[0]) + 1]
                extrapolated_beatstep = extrapolated_beatstep[: np.max(np.where(attention_mask_extrapolated_beatstep == 1)[0]) + 1]
            each_tokens_ids = to_numpy(each_tokens_ids)
            beatsteps = to_numpy(beatsteps)
            extrapolated_beatstep = to_numpy(extrapolated_beatstep)
            pretty_midi_object = self.relative_batch_tokens_ids_to_midi(tokens=each_tokens_ids, beatstep=extrapolated_beatstep, bars_per_batch=self.num_bars, cutoff_time_idx=(self.num_bars + 1) * 4)
            for note in pretty_midi_object.instruments[0].notes:
                note.start += beatsteps[0]
                note.end += beatsteps[0]
                notes_list.append(note)
            pretty_midi_objects_list.append(pretty_midi_object)
            start_idx += end_idx + 1
        if return_midi: return BatchEncoding({"notes": notes_list, "pretty_midi_objects": pretty_midi_objects_list})
        return BatchEncoding({"notes": notes_list})
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
