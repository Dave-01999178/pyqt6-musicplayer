import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Self, Any

import numpy as np
from PyQt6.QtCore import QObject
from numpy.typing import NDArray
from pyaudio import PyAudio
from pydub import AudioSegment

from pyqt6_music_player.constants import SUPPORTED_BYTES

temp_file_to_use = r"C:\Users\dave_\Music\Factory Background.mp3"


# ================================================================================
# AUDIO DECODING AND DATA PREPARATION
# ================================================================================
@dataclass(frozen=True)
class AudioData:
    channels: int
    frame_rate: int
    sample_width: int
    normalized_samples: NDArray[np.float32]

    @classmethod
    def from_file(cls, file: str | Path) -> Self | None:
        # --- Load and decode file. ---
        try:
            audio_segment = AudioSegment.from_file(file)
        except Exception as e:
            logging.error("Failed to decode file: %s, %s.", file, e)
            return None

        sample_width = audio_segment.sample_width
        if sample_width not in SUPPORTED_BYTES:
            logging.error("Invalid/Unsupported sample width: %d", sample_width)
            return None

        # Omitted 24-bit audio (sample_width == 3) as pydub converts 24-bit to 32-bit
        # automatically.
        byte_to_dtype_map: dict[int, type[np.integer[Any]]] = {
            1: np.uint8,
            2: np.int16,
            4: np.int32
        }
        orig_dtype = byte_to_dtype_map[sample_width]

        # --- Parse raw data from AudioSegment. ---
        samples = np.frombuffer(
            buffer=audio_segment.raw_data,
            dtype=orig_dtype
        ).astype(np.float32)

        # --- Normalize samples to [-1.0, 1.0]. ---
        if sample_width == 1:
            samples_normalized = (samples - 128.0) / 128.0
        else:
            # For 16-bit (i2) and 32-bit (i4) signed integers.
            # Use the maximum positive value (M_pos) for division.
            # max_value = 32767.0 for 16-bit, 2147483647.0 for 32-bit.
            max_value = float(np.iinfo(orig_dtype).max)
            samples_normalized = samples / max_value

        # --- Reshape samples array: (frames, channels). ---
        # '-1' is a numpy trick to automatically calculate that dimension size (rows in this case).
        samples_normalized = samples_normalized.reshape(-1, audio_segment.channels)

        return cls(
            channels=audio_segment.channels,
            frame_rate=audio_segment.frame_rate,
            sample_width=audio_segment.sample_width,
            normalized_samples=samples_normalized
        )


# ================================================================================
# PLAYER ENGINE
# ================================================================================
# TODO: Initial implementation (play only), refactor and extend later to include pause, repeat,
#  seeking, and volume.
class PlayerEngine(QObject):
    def __init__(self, audio_data: AudioData):
        super().__init__()
        self.audio_data = audio_data
        self.chunk_ms = 50
        self.chunk_frames = int(self.audio_data.frame_rate * self.chunk_ms / 1000)
        self.frame_index = 0

        self.pa = PyAudio()
        self.stream = self.pa.open(
            rate=self.audio_data.frame_rate,
            channels=self.audio_data.channels,
            format=self.pa.get_format_from_width(self.audio_data.sample_width, True),
            output=True,
            frames_per_buffer=self.chunk_frames
        )

    def playback_loop(self):
        samples_len = len(self.audio_data.normalized_samples)

        while self.frame_index < samples_len:
            end = min(self.frame_index + self.chunk_frames, samples_len)
            chunk = self.audio_data.normalized_samples[self.frame_index:end]

            data = self._float_to_bytes(chunk)

            self.stream.write(data)
            self.frame_index = end

        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

    def _float_to_bytes(self, chunk_float):
        chunk_float = np.clip(chunk_float, -1.0, 1.0)
        sample_width = self.audio_data.sample_width

        if sample_width == 1:
            chunk_int = (chunk_float * 127 + 128).astype(np.uint8)
        elif sample_width == 2:
            chunk_int = (chunk_float * 32767).astype(np.int16)
        elif sample_width == 4:
            chunk_int = (chunk_float * 2147483647).astype(np.int32)
        else:
            raise ValueError("Unsupported sample width")

        return chunk_int.tobytes()  # Already interleaved
