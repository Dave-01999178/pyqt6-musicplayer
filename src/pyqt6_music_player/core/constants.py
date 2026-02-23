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
    IDLE = auto()  # Default state on startup
    PLAYING = auto()
    PAUSED = auto()
    STOPPED = auto()  # Playback interrupted (normally or due to an error)


class VolumeLevel(Enum):
    MUTE = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
