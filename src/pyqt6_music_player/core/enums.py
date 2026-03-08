from enum import Enum, auto


class PlaybackMode(Enum):
    """Defines how the next track is selected during playback."""

    NORMAL = auto()
    REPEAT_ONE = auto()
    REPEAT_ALL = auto()
    SHUFFLE = auto()


class PlaybackStatus(Enum):
    """Represents the current state of the audio player."""

    IDLE = auto()  # Default state on startup
    PLAYING = auto()
    PAUSED = auto()
    STOPPED = auto()
    ERROR = auto()


class VolumeLevel(Enum):
    """Categorizes volume into discrete display levels for the volume icon."""

    MUTE = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
