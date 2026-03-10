from enum import Enum, auto


class PlaybackStatus(Enum):
    """Represents the current state of the audio player."""

    IDLE = auto()  # Default state on startup
    PLAYING = auto()
    PAUSED = auto()
    STOPPED = auto()
    ERROR = auto()


class RepeatMode(Enum):
    OFF = auto()
    ONE = auto()
    ALL = auto()


class ShuffleMode(Enum):
    ON = auto()
    OFF = auto()


class VolumeLevel(Enum):
    """Categorizes volume into discrete display levels for the volume icon."""

    MUTE = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
