import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Self

import mutagen
import numpy as np
from numpy.typing import NDArray
from pydub import AudioSegment

from pyqt6_music_player.constants import DefaultAudioInfo, SUPPORTED_BYTES
from pyqt6_music_player.metadata.metadata_extractor import get_metadata


# ================================================================================
# AUDIO MODEL
# ================================================================================
#
# ---------- Audio track (file path and metadata) ----------
@dataclass(frozen=True, eq=True)
class AudioTrack:
    """
    Represents an audio track with metadata.

    Attributes:
        path: Filesystem path to the audio file.
        title: Track title.
        artist: Track artist.
        album: Album name.
        duration: Track duration in seconds (float).
    """
    path: Path | None = None
    title: str = DefaultAudioInfo.title
    artist: str = DefaultAudioInfo.artist
    album: str = DefaultAudioInfo.album
    duration: str | float = DefaultAudioInfo.elapsed_time
    # album_art: QPixmap

    @classmethod
    def from_path(cls, path: Path) -> Self | None:
        """
        Creates an AudioTrack instance from an audio file.

        Returns:
            An AudioTrack instance containing the audio file path and its metadata,
            or None if the file cannot be read or contains invalid audio data.
        """
        # --- Load audio file. ---
        try:
            audio = mutagen.File(path)
        except (mutagen.MutagenError, OSError) as e:
            logging.warning("Invalid or unreadable audio file: %s (%s)", path, e)
            return None
        except Exception as e:
            logging.error("Unexpected error while reading %s: %s", path, e)
            return None

        # --- Extract metadata. ---
        metadata = get_metadata(audio)

        return cls(
            path=path,
            title=metadata["title"],
            artist=metadata["artist"],
            album=metadata["album"],
            duration=metadata["duration"]
        )


# ---------- Audio samples (PCM and format parameters) ----------
@dataclass(frozen=True, eq=True)
class AudioSamples:
    """
    Represents PCM audio samples normalized to [-1.0, 1.0].

    Attributes:
        channels: Number of audio channels.
        sample_rate: Samples per second (Hz).
        sample_width: Bytes per sample.
        orig_dtype: Original PCM numpy dtype.
        dtype_max_val: Maximum representable value of original dtype.
        samples: Normalized audio samples as float32.
    """
    channels: int
    sample_rate: int
    sample_width: int
    orig_dtype: type[np.uint8] | type[np.int16] | type[np.int32]
    dtype_max_val: int
    samples: NDArray[np.float32]

    def __post_init__(self) -> None:
        arr = self.samples

        if not arr.flags.writeable:
            return

        arr.setflags(write=False)  # Set to read-only.

    @classmethod
    def from_file(cls, file: Path) -> Self | None:
        # --- Load and decode file. ---
        try:
            audio_segment = AudioSegment.from_file(file)
        except Exception as e:
            logging.error("Failed to decode file: %s, %s.", file, e)
            return None

        # --- Parse raw data from AudioSegment. ---
        #
        # Omitted 24-bit audio (sample_width == 3) because pydub automatically converts
        # 24-bit to 32-bit.
        sample_width = audio_segment.sample_width
        if sample_width not in SUPPORTED_BYTES:
            logging.error("Invalid/Unsupported sample width: %d", sample_width)
            return None

        if sample_width == 1:
            orig_dtype = np.uint8
        elif sample_width == 2:
            orig_dtype = np.int16
        else:
            orig_dtype = np.int32

        samples = np.frombuffer(buffer=audio_segment.raw_data, dtype=orig_dtype).astype(np.float32)

        # --- Normalize samples to [-1.0, 1.0] range. ---
        if sample_width == 1:
            max_value = np.iinfo(orig_dtype).max
            samples_normalized = (samples - 128.0) / 128.0
        else:
            # For 16-bit (i2) and 32-bit (i4) signed integers.
            # Use the maximum positive value (M_pos) for division.
            # max_value = 32767 for 16-bit, 2147483647 for 32-bit.
            max_value = np.iinfo(orig_dtype).max
            samples_normalized = samples / float(max_value)

        # --- Reshape samples array: (frames, channels). ---
        # '-1' is a numpy trick to automatically calculate that dimension size (rows in this case).
        samples_normalized = samples_normalized.reshape(-1, audio_segment.channels)

        return cls(
            channels=audio_segment.channels,
            sample_rate=audio_segment.frame_rate,
            sample_width=sample_width,
            orig_dtype=orig_dtype,
            dtype_max_val=max_value,
            samples=samples_normalized
        )


DEFAULT_SONG: AudioTrack = AudioTrack()
