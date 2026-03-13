from enum import Enum, auto


class PlaybackState(Enum):
    """Represents the current playback state."""

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
