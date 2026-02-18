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
# Enums
# ================================================================================
# TODO: Move out later.
class PlaybackStatus(Enum):
    IDLE = auto()  # Default status, audio player initialized but no track loaded.
    PLAYING = auto()
    PAUSED = auto()
    STOPPED = auto()


class VolumeLevel(Enum):
    """Represent discrete volume intensity levels."""

    MUTE = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
