import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Self

import numpy as np
from numpy.typing import NDArray
from pydub import AudioSegment

from pyqt6_music_player.config import SUPPORTED_BYTES


# ================================================================================
# AUDIO DECODING AND DATA PREPARATION
# ================================================================================
@dataclass(frozen=True)
class AudioData:
    segment: AudioSegment
    samples: NDArray[np.float32]

    @classmethod
    def from_file(cls, file: Path) -> Self | None:
        # --- Load and decode file. ---
        try:
            audio_segment = AudioSegment.from_file(file)
        except Exception as e:
            logging.error("Failed to decode file: %s, %s.", file, e)
            return None

        # Omitted 24-bit audio (sample_width == 3) as pydub converts 24-bit to 32-bit
        # automatically.
        byte_to_dtype_map = {1: "<u1", 2: "<i2", 4: "<i4"}

        sample_width = audio_segment.sample_width
        if sample_width not in SUPPORTED_BYTES:
            logging.error("Invalid/Unsupported sample width: %d", sample_width)
            return None

        orig_dtype = byte_to_dtype_map.get(sample_width)

        # --- Parse raw data from AudioSegment. ---
        samples = np.frombuffer(
            buffer=audio_segment.raw_data,
            dtype=orig_dtype
        )

        # --- Normalize samples to [-1.0, 1.0]. ---
        samples.astype(np.float32)
        if sample_width == 1:
            samples_normalized = (samples - 128) / 128
        else:
            max_value = np.iinfo(orig_dtype).max if np.issubdtype(orig_dtype, np.integer) else 1.0
            samples_normalized = samples / max_value

        # --- Reshape samples array: (frames, channels). ---
        # '-1' is a numpy trick to automatically calculate that dimension size (rows in this case).
        samples_normalized = samples_normalized.reshape(-1, audio_segment.channels)

        return cls(segment=audio_segment, samples=samples_normalized)
