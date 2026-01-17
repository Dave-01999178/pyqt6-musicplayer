from dataclasses import dataclass
from enum import Enum, auto

# ================================================================================
# CONSTANTS
# ================================================================================
#
# --- SUPPORTED AUDIO SAMPLE WIDTH ---
SUPPORTED_BYTES = {1, 2, 4}

# --- AUDIO FORMATS ---
FILE_DIALOG_FILTER = "Audio files (*.mp3 *.wav *.flac *.ogg)"
SUPPORTED_AUDIO_FORMAT = {".mp3", ".wav", ".flac", ".ogg"}

# --- VOLUME ---
MIN_VOLUME = 0
MAX_VOLUME = 100


# ================================================================================
# DATACLASSES
# ================================================================================
@dataclass(frozen=True)
class DefaultAudioInfo:
    title = "Song Title"
    artist = "Song Artist"
    album = "Song Album"
    elapsed_time = "00:00"
    total_duration = ""


@dataclass(frozen=True)
class AudioMetadataFallback:
    """Fallback values for audio metadata."""

    title: str = "Unknown Title"
    artist: str = "Unknown Artist"
    album: str = "Unknown Album"


# ================================================================================
# Enums
# ================================================================================
class PlaybackState(Enum):
    PLAYING = auto()
    PAUSED = auto()
    STOPPED = auto()
