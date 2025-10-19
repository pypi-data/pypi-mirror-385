'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import dataclasses
import math
import os
from typing import Any, Callable, List, Mapping, MutableMapping, Optional, Sequence, Tuple, Union
import numpy as np
import torch
import torch.nn.functional as F
from ....utils import is_note_seq_available
from .pipeline_spectrogram_diffusion import TARGET_FEATURE_LENGTH
if is_note_seq_available(): import note_seq
else: raise ImportError('Please install note-seq via `pip install note-seq`')
INPUT_FEATURE_LENGTH = 2048
SAMPLE_RATE = 16000
HOP_SIZE = 320
FRAME_RATE = int(SAMPLE_RATE // HOP_SIZE)
DEFAULT_STEPS_PER_SECOND = 100
DEFAULT_MAX_SHIFT_SECONDS = 10
DEFAULT_NUM_VELOCITY_BINS = 1
SLAKH_CLASS_PROGRAMS = {'Acoustic Piano': 0, 'Electric Piano': 4, 'Chromatic Percussion': 8, 'Organ': 16, 'Acoustic Guitar': 24, 'Clean Electric Guitar': 26, 'Distorted Electric Guitar': 29, 'Acoustic Bass': 32, 'Electric Bass': 33, 'Violin': 40, 'Viola': 41, 'Cello': 42, 'Contrabass': 43, 'Orchestral Harp': 46, 'Timpani': 47, 'String Ensemble': 48, 'Synth Strings': 50, 'Choir and Voice': 52, 'Orchestral Hit': 55, 'Trumpet': 56, 'Trombone': 57, 'Tuba': 58, 'French Horn': 60, 'Brass Section': 61, 'Soprano/Alto Sax': 64, 'Tenor Sax': 66, 'Baritone Sax': 67, 'Oboe': 68, 'English Horn': 69, 'Bassoon': 70, 'Clarinet': 71, 'Pipe': 73, 'Synth Lead': 80, 'Synth Pad': 88}
@dataclasses.dataclass
class NoteRepresentationConfig:
    onsets_only: bool
    include_ties: bool
@dataclasses.dataclass
class NoteEventData:
    pitch: int
    velocity: Optional[int] = None
    program: Optional[int] = None
    is_drum: Optional[bool] = None
    instrument: Optional[int] = None
@dataclasses.dataclass
class NoteEncodingState:
    active_pitches: MutableMapping[Tuple[int, int], int] = dataclasses.field(default_factory=dict)
@dataclasses.dataclass
class EventRange:
    type: str
    min_value: int
    max_value: int
@dataclasses.dataclass
class Event:
    type: str
    value: int
class Tokenizer:
    def __init__(self, regular_ids: int):
        self._num_special_tokens = 3
        self._num_regular_tokens = regular_ids
    def encode(self, token_ids):
        encoded = []
        for token_id in token_ids:
            if not 0 <= token_id < self._num_regular_tokens: raise ValueError(f'token_id {token_id} does not fall within valid range of [0, {self._num_regular_tokens})')
            encoded.append(token_id + self._num_special_tokens)
        encoded.append(1)
        encoded = encoded + [0] * (INPUT_FEATURE_LENGTH - len(encoded))
        return encoded
class Codec:
    def __init__(self, max_shift_steps: int, steps_per_second: float, event_ranges: List[EventRange]):
        """Args:"""
        self.steps_per_second = steps_per_second
        self._shift_range = EventRange(type='shift', min_value=0, max_value=max_shift_steps)
        self._event_ranges = [self._shift_range] + event_ranges
        assert len(self._event_ranges) == len({er.type for er in self._event_ranges})
    @property
    def num_classes(self) -> int: return sum((er.max_value - er.min_value + 1 for er in self._event_ranges))
    def is_shift_event_index(self, index: int) -> bool: return self._shift_range.min_value <= index and index <= self._shift_range.max_value
    @property
    def max_shift_steps(self) -> int: return self._shift_range.max_value
    def encode_event(self, event: Event) -> int:
        offset = 0
        for er in self._event_ranges:
            if event.type == er.type:
                if not er.min_value <= event.value <= er.max_value: raise ValueError(f'Event value {event.value} is not within valid range [{er.min_value}, {er.max_value}] for type {event.type}')
                return offset + event.value - er.min_value
            offset += er.max_value - er.min_value + 1
        raise ValueError(f'Unknown event type: {event.type}')
    def event_type_range(self, event_type: str) -> Tuple[int, int]:
        offset = 0
        for er in self._event_ranges:
            if event_type == er.type: return (offset, offset + (er.max_value - er.min_value))
            offset += er.max_value - er.min_value + 1
        raise ValueError(f'Unknown event type: {event_type}')
    def decode_event_index(self, index: int) -> Event:
        offset = 0
        for er in self._event_ranges:
            if offset <= index <= offset + er.max_value - er.min_value: return Event(type=er.type, value=er.min_value + index - offset)
            offset += er.max_value - er.min_value + 1
        raise ValueError(f'Unknown event index: {index}')
@dataclasses.dataclass
class ProgramGranularity:
    tokens_map_fn: Callable[[Sequence[int], Codec], Sequence[int]]
    program_map_fn: Callable[[int], int]
def drop_programs(tokens, codec: Codec):
    min_program_id, max_program_id = codec.event_type_range('program')
    return tokens[(tokens < min_program_id) | (tokens > max_program_id)]
def programs_to_midi_classes(tokens, codec):
    min_program_id, max_program_id = codec.event_type_range('program')
    is_program = (tokens >= min_program_id) & (tokens <= max_program_id)
    return np.where(is_program, min_program_id + 8 * ((tokens - min_program_id) // 8), tokens)
PROGRAM_GRANULARITIES = {'flat': ProgramGranularity(tokens_map_fn=drop_programs, program_map_fn=lambda program: 0), 'midi_class': ProgramGranularity(tokens_map_fn=programs_to_midi_classes,
program_map_fn=lambda program: 8 * (program // 8)), 'full': ProgramGranularity(tokens_map_fn=lambda tokens, codec: tokens, program_map_fn=lambda program: program)}
def frame(signal, frame_length, frame_step, pad_end=False, pad_value=0, axis=-1):
    signal_length = signal.shape[axis]
    if pad_end:
        frames_overlap = frame_length - frame_step
        rest_samples = np.abs(signal_length - frames_overlap) % np.abs(frame_length - frames_overlap)
        pad_size = int(frame_length - rest_samples)
        if pad_size != 0:
            pad_axis = [0] * signal.ndim
            pad_axis[axis] = pad_size
            signal = F.pad(signal, pad_axis, 'constant', pad_value)
    frames = signal.unfold(axis, frame_length, frame_step)
    return frames
def program_to_slakh_program(program):
    for slakh_program in sorted(SLAKH_CLASS_PROGRAMS.values(), reverse=True):
        if program >= slakh_program: return slakh_program
def audio_to_frames(samples, hop_size: int, frame_rate: int) -> Tuple[Sequence[Sequence[int]], torch.Tensor]:
    frame_size = hop_size
    samples = np.pad(samples, [0, frame_size - len(samples) % frame_size], mode='constant')
    frames = frame(torch.Tensor(samples).unsqueeze(0), frame_length=frame_size, frame_step=frame_size, pad_end=False)
    num_frames = len(samples) // frame_size
    times = np.arange(num_frames) / frame_rate
    return (frames, times)
def note_sequence_to_onsets_and_offsets_and_programs(ns: note_seq.NoteSequence) -> Tuple[Sequence[float], Sequence[NoteEventData]]:
    """Returns:"""
    notes = sorted(ns.notes, key=lambda note: (note.is_drum, note.program, note.pitch))
    times = [note.end_time for note in notes if not note.is_drum] + [note.start_time for note in notes]
    values = [NoteEventData(pitch=note.pitch, velocity=0, program=note.program, is_drum=False)
    for note in notes if not note.is_drum] + [NoteEventData(pitch=note.pitch, velocity=note.velocity, program=note.program, is_drum=note.is_drum) for note in notes]
    return (times, values)
def num_velocity_bins_from_codec(codec: Codec):
    lo, hi = codec.event_type_range('velocity')
    return hi - lo
def segment(a, n): return [a[i:i + n] for i in range(0, len(a), n)]
def velocity_to_bin(velocity, num_velocity_bins):
    if velocity == 0: return 0
    else: return math.ceil(num_velocity_bins * velocity / note_seq.MAX_MIDI_VELOCITY)
def note_event_data_to_events(state: Optional[NoteEncodingState], value: NoteEventData, codec: Codec) -> Sequence[Event]:
    if value.velocity is None: return [Event('pitch', value.pitch)]
    else:
        num_velocity_bins = num_velocity_bins_from_codec(codec)
        velocity_bin = velocity_to_bin(value.velocity, num_velocity_bins)
        if value.program is None:
            if state is not None: state.active_pitches[value.pitch, 0] = velocity_bin
            return [Event('velocity', velocity_bin), Event('pitch', value.pitch)]
        elif value.is_drum: return [Event('velocity', velocity_bin), Event('drum', value.pitch)]
        else:
            if state is not None: state.active_pitches[value.pitch, value.program] = velocity_bin
            return [Event('program', value.program), Event('velocity', velocity_bin), Event('pitch', value.pitch)]
def note_encoding_state_to_events(state: NoteEncodingState) -> Sequence[Event]:
    events = []
    for pitch, program in sorted(state.active_pitches.keys(), key=lambda k: k[::-1]):
        if state.active_pitches[pitch, program]: events += [Event('program', program), Event('pitch', pitch)]
    events.append(Event('tie', 0))
    return events
def encode_and_index_events(state, event_times, event_values, codec, frame_times, encode_event_fn, encoding_state_to_events_fn=None):
    """Returns:"""
    indices = np.argsort(event_times, kind='stable')
    event_steps = [round(event_times[i] * codec.steps_per_second) for i in indices]
    event_values = [event_values[i] for i in indices]
    events = []
    state_events = []
    event_start_indices = []
    state_event_indices = []
    cur_step = 0
    cur_event_idx = 0
    cur_state_event_idx = 0
    def fill_event_start_indices_to_cur_step():
        while len(event_start_indices) < len(frame_times) and frame_times[len(event_start_indices)] < cur_step / codec.steps_per_second:
            event_start_indices.append(cur_event_idx)
            state_event_indices.append(cur_state_event_idx)
    for event_step, event_value in zip(event_steps, event_values):
        while event_step > cur_step:
            events.append(codec.encode_event(Event(type='shift', value=1)))
            cur_step += 1
            fill_event_start_indices_to_cur_step()
            cur_event_idx = len(events)
            cur_state_event_idx = len(state_events)
        if encoding_state_to_events_fn:
            for e in encoding_state_to_events_fn(state): state_events.append(codec.encode_event(e))
        for e in encode_event_fn(state, event_value, codec): events.append(codec.encode_event(e))
    while cur_step / codec.steps_per_second <= frame_times[-1]:
        events.append(codec.encode_event(Event(type='shift', value=1)))
        cur_step += 1
        fill_event_start_indices_to_cur_step()
        cur_event_idx = len(events)
    event_end_indices = event_start_indices[1:] + [len(events)]
    events = np.array(events).astype(np.int32)
    state_events = np.array(state_events).astype(np.int32)
    event_start_indices = segment(np.array(event_start_indices).astype(np.int32), TARGET_FEATURE_LENGTH)
    event_end_indices = segment(np.array(event_end_indices).astype(np.int32), TARGET_FEATURE_LENGTH)
    state_event_indices = segment(np.array(state_event_indices).astype(np.int32), TARGET_FEATURE_LENGTH)
    outputs = []
    for start_indices, end_indices, event_indices in zip(event_start_indices, event_end_indices, state_event_indices): outputs.append({'inputs': events,
    'event_start_indices': start_indices, 'event_end_indices': end_indices, 'state_events': state_events, 'state_event_indices': event_indices})
    return outputs
def extract_sequence_with_indices(features, state_events_end_token=None, feature_key='inputs'):
    features = features.copy()
    start_idx = features['event_start_indices'][0]
    end_idx = features['event_end_indices'][-1]
    features[feature_key] = features[feature_key][start_idx:end_idx]
    if state_events_end_token is not None:
        state_event_start_idx = features['state_event_indices'][0]
        state_event_end_idx = state_event_start_idx + 1
        while features['state_events'][state_event_end_idx - 1] != state_events_end_token: state_event_end_idx += 1
        features[feature_key] = np.concatenate([features['state_events'][state_event_start_idx:state_event_end_idx], features[feature_key]], axis=0)
    return features
def map_midi_programs(feature, codec: Codec, granularity_type: str='full', feature_key: str='inputs') -> Mapping[str, Any]:
    granularity = PROGRAM_GRANULARITIES[granularity_type]
    feature[feature_key] = granularity.tokens_map_fn(feature[feature_key], codec)
    return feature
def run_length_encode_shifts_fn(features, codec: Codec, feature_key: str='inputs',
state_change_event_types: Sequence[str]=()) -> Callable[[Mapping[str, Any]], Mapping[str, Any]]:
    """Returns:"""
    state_change_event_ranges = [codec.event_type_range(event_type) for event_type in state_change_event_types]
    def run_length_encode_shifts(features: MutableMapping[str, Any]) -> Mapping[str, Any]:
        """Returns:"""
        events = features[feature_key]
        shift_steps = 0
        total_shift_steps = 0
        output = np.array([], dtype=np.int32)
        current_state = np.zeros(len(state_change_event_ranges), dtype=np.int32)
        for event in events:
            if codec.is_shift_event_index(event):
                shift_steps += 1
                total_shift_steps += 1
            else:
                is_redundant = False
                for i, (min_index, max_index) in enumerate(state_change_event_ranges):
                    if min_index <= event and event <= max_index:
                        if current_state[i] == event: is_redundant = True
                        current_state[i] = event
                if is_redundant: continue
                if shift_steps > 0:
                    shift_steps = total_shift_steps
                    while shift_steps > 0:
                        output_steps = np.minimum(codec.max_shift_steps, shift_steps)
                        output = np.concatenate([output, [output_steps]], axis=0)
                        shift_steps -= output_steps
                output = np.concatenate([output, [event]], axis=0)
        features[feature_key] = output
        return features
    return run_length_encode_shifts(features)
def note_representation_processor_chain(features, codec: Codec, note_representation_config: NoteRepresentationConfig):
    tie_token = codec.encode_event(Event('tie', 0))
    state_events_end_token = tie_token if note_representation_config.include_ties else None
    features = extract_sequence_with_indices(features, state_events_end_token=state_events_end_token, feature_key='inputs')
    features = map_midi_programs(features, codec)
    features = run_length_encode_shifts_fn(features, codec, state_change_event_types=['velocity', 'program'])
    return features
class MidiProcessor:
    def __init__(self):
        self.codec = Codec(max_shift_steps=DEFAULT_MAX_SHIFT_SECONDS * DEFAULT_STEPS_PER_SECOND, steps_per_second=DEFAULT_STEPS_PER_SECOND,
        event_ranges=[EventRange('pitch', note_seq.MIN_MIDI_PITCH, note_seq.MAX_MIDI_PITCH), EventRange('velocity', 0, DEFAULT_NUM_VELOCITY_BINS),
        EventRange('tie', 0, 0), EventRange('program', note_seq.MIN_MIDI_PROGRAM,
        note_seq.MAX_MIDI_PROGRAM), EventRange('drum', note_seq.MIN_MIDI_PITCH, note_seq.MAX_MIDI_PITCH)])
        self.tokenizer = Tokenizer(self.codec.num_classes)
        self.note_representation_config = NoteRepresentationConfig(onsets_only=False, include_ties=True)
    def __call__(self, midi: Union[bytes, os.PathLike, str]):
        if not isinstance(midi, bytes):
            with open(midi, 'rb') as f: midi = f.read()
        ns = note_seq.midi_to_note_sequence(midi)
        ns_sus = note_seq.apply_sustain_control_changes(ns)
        for note in ns_sus.notes:
            if not note.is_drum: note.program = program_to_slakh_program(note.program)
        samples = np.zeros(int(ns_sus.total_time * SAMPLE_RATE))
        _, frame_times = audio_to_frames(samples, HOP_SIZE, FRAME_RATE)
        times, values = note_sequence_to_onsets_and_offsets_and_programs(ns_sus)
        events = encode_and_index_events(state=NoteEncodingState(), event_times=times, event_values=values, frame_times=frame_times, codec=self.codec,
        encode_event_fn=note_event_data_to_events, encoding_state_to_events_fn=note_encoding_state_to_events)
        events = [note_representation_processor_chain(event, self.codec, self.note_representation_config) for event in events]
        input_tokens = [self.tokenizer.encode(event['inputs']) for event in events]
        return input_tokens
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
