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
class DefaultTrackInfo:
    """Placeholder for missing track metadata."""

    title = "Track Title"
    artist = "Track Artist"
    album = "Track Album"
    duration = "00:00:00"


# ================================================================================
# TRACK
# ================================================================================
#
# ----- Track file path, and metadata -----
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
    title: str = DefaultTrackInfo.title
    artist: str = DefaultTrackInfo.artist
    album: str = DefaultTrackInfo.album
    duration: str | float = DefaultTrackInfo.duration

    @classmethod
    def from_file(cls, path: Path) -> Self | None:
        """Create a Track instance from an audio file.

        Args:
            path: The filesystem path to the audio file.

        Returns:
            A Track instance containing the audio file path and its metadata,
            or None if the file cannot be read or contains invalid audio data.

        """
        # Load the audio file
        try:
            audio = mutagen.File(path)

        except (mutagen.MutagenError, OSError) as e:
            logging.warning("Invalid or unreadable audio file: %s (%s)", path, e)
            return None

        except Exception as e:
            logging.error("Unexpected error while reading %s: %s", path, e)
            return None

        else:
            # Extract the metadata from audio file
            metadata = get_metadata(audio)

        return cls(
            path=path,
            title=metadata["title"],
            artist=metadata["artist"],
            album=metadata["album"],
            duration=metadata["duration"],
        )


# ----- Audio PCM -----
@dataclass(frozen=True, eq=True)
class AudioPCM:
    """Represents PCM audio samples normalized to [-1.0, 1.0].

    Attributes:
        channels: Number of audio channels.
        sample_rate: Samples per second (Hz).
        sample_width: Bytes per sample.
        samples: Normalized audio samples as float32.
        orig_dtype: Original PCM numpy dtype.
        orig_scale: Value used to adjust, or transform data to a common scale or range.

    """
    # Format parameters
    channels: int
    sample_rate: int
    sample_width: int

    # PCM data
    samples: NDArray[np.float32]
    orig_dtype: type[np.uint8] | type[np.int16] | type[np.int32]
    orig_scale: float

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
        # --- Load and decode audio file. ---
        try:
            audio_segment = AudioSegment.from_file(path)
        except Exception as e:
            logging.error("Failed to decode file: %s, %s.", path, e)
            return None

        # --- Parse raw data from AudioSegment. ---
        sample_width = audio_segment.sample_width
        if sample_width not in SUPPORTED_BYTES:
            logging.error("Invalid/Unsupported sample width: %d", sample_width)
            return None

        # 'sample_width = 3' or '24-bit' is not included since PyDub automatically
        # converts it into 32-bit due to limitations.
        if sample_width == 1:
            orig_dtype = np.uint8
        elif sample_width == 2:
            orig_dtype = np.int16
        else:
            orig_dtype = np.int32

        samples = np.frombuffer(
            buffer=audio_segment.raw_data,
            dtype=orig_dtype,
        ).astype(np.float32)

        info = np.iinfo(orig_dtype)

        # --- Normalize samples to [-1.0, 1.0] range. ---
        if np.issubdtype(orig_dtype, np.unsignedinteger):
            # For unsigned: subtract mid-point, then divide by float mid-point.
            mid_point = (1 << (info.bits - 1))
            scale = float(mid_point)
            samples_normalized = (samples - mid_point) / scale
        else:
            # For signed: divide by max positive value
            scale = float(info.max)
            samples_normalized = samples / scale

        # --- Reshape samples array: (frames, channels). ---
        # '-1' is a numpy trick to automatically calculate a row, or column size
        samples_normalized = samples_normalized.reshape(-1, audio_segment.channels)

        return cls(
            channels=audio_segment.channels,
            sample_rate=audio_segment.frame_rate,
            sample_width=sample_width,
            samples=samples_normalized,
            orig_dtype=orig_dtype,
            orig_scale=scale,
        )


DEFAULT_TRACK: Track = Track()
