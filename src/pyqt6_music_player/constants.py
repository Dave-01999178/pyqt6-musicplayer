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


# TODO: Move out later.
# ================================================================================
# Enums
# ================================================================================
class PlaybackState(Enum):
    # IDLE = auto()  # Default state, no track loaded.
    PLAYING = auto()
    PAUSED = auto()
    STOPPED = auto()  # Playback interrupted, track loaded but not playing.
