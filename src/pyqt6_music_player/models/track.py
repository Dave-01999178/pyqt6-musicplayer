import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Self

import mutagen
import numpy as np
from numpy.typing import NDArray
from pydub import AudioSegment

from pyqt6_music_player.core import SUPPORTED_BYTES
from pyqt6_music_player.utils import get_metadata


@dataclass(frozen=True)
class DefaultAudioInfo:
    title = "Track Title"
    artist = "Track Artist"
    album = "Track Album"
    duration = "00:00:00"


# ================================================================================
# TRACK
# ================================================================================
#
# --- Track file path, and metadata ---
@dataclass(frozen=True, eq=True)
class Track:
    """Represent an audio track with metadata.

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
    duration: str | float = DefaultAudioInfo.duration

    @classmethod
    def from_path(cls, path: Path) -> Self | None:
        """Create a Track instance from an audio file.

        Returns:
            A Track instance containing the audio file path and its metadata,
            or None if the file cannot be read or contains invalid audio data.

        """
        # Load audio file.
        try:
            audio = mutagen.File(path)
        except (mutagen.MutagenError, OSError) as e:
            logging.warning("Invalid or unreadable audio file: %s (%s)", path, e)
            return None
        except Exception as e:
            logging.error("Unexpected error while reading %s: %s", path, e)
            return None

        # Extract metadata.
        metadata = get_metadata(audio)

        return cls(
            path=path,
            title=metadata["title"],
            artist=metadata["artist"],
            album=metadata["album"],
            duration=metadata["duration"],
        )


# --- Track PCM and format parameters ---
@dataclass(frozen=True, eq=True)
class TrackAudio:
    """Represents PCM audio samples normalized to [-1.0, 1.0].

    Attributes:
        channels: Number of audio channels.
        sample_rate: Samples per second (Hz).
        sample_width: Bytes per sample.
        orig_dtype: Original PCM numpy dtype.
        orig_dtype_max: Maximum representable value of original dtype.
        samples: Normalized audio samples as float32.

    """

    channels: int
    sample_rate: int
    sample_width: int
    orig_dtype: type[np.uint8] | type[np.int16] | type[np.int32]
    orig_dtype_max: int
    samples: NDArray[np.float32]

    def __post_init__(self) -> None:
        """Set PCM samples to read-only after initializing."""
        arr = self.samples

        if not arr.flags.writeable:
            return

        arr.setflags(write=False)  # Set to read-only.

    @classmethod
    def from_file(cls, path: Path) -> Self | None:
        """Decode and parse AudioSegment.

        Args:
            path: The filesystem path to the audio file.

        """
        # --- Load and decode file. ---
        try:
            audio_segment = AudioSegment.from_file(path)
        except Exception as e:
            logging.error("Failed to decode file: %s, %s.", path, e)
            return None

        # --- Parse raw data from AudioSegment. ---
        #
        # Omitted 24-bit audio (sample_width == 3) because pydub automatically converts
        # 24-bit to 32-bit.
        sample_width = audio_segment.sample_width
        if sample_width not in SUPPORTED_BYTES:
            logging.error("Invalid/Unsupported sample width: %d", sample_width)
            return None

        one_byte = 1
        two_bytes = 2

        if sample_width == one_byte:
            orig_dtype = np.uint8
        elif sample_width == two_bytes:
            orig_dtype = np.int16
        else:
            orig_dtype = np.int32

        samples = np.frombuffer(
            buffer=audio_segment.raw_data,
            dtype=orig_dtype,
        ).astype(np.float32)

        # --- Normalize samples to [-1.0, 1.0] range. ---
        if sample_width == one_byte:
            max_value = np.iinfo(orig_dtype).max
            samples_normalized = (samples - 128.0) / 128.0
        else:
            # For 16-bit (i2) and 32-bit (i4) signed integers.
            # Use the maximum positive value (M_pos) for division.
            # max_value = 32767 for 16-bit, 2147483647 for 32-bit.
            max_value = np.iinfo(orig_dtype).max
            samples_normalized = samples / float(max_value)

        # --- Reshape samples array: (frames, channels). ---
        # '-1' is a numpy trick to automatically calculate a dimension size
        # (rows in this case).
        samples_normalized = samples_normalized.reshape(-1, audio_segment.channels)

        return cls(
            channels=audio_segment.channels,
            sample_rate=audio_segment.frame_rate,
            sample_width=sample_width,
            orig_dtype=orig_dtype,
            orig_dtype_max=max_value,
            samples=samples_normalized,
        )


DEFAULT_TRACK: Track = Track()
