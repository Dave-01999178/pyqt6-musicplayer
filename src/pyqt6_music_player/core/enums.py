from enum import Enum, auto


class OrderMode(Enum):
    """How tracks are sequenced in playback order."""

    SEQUENTIAL = auto()
    SHUFFLED = auto()


class PlaybackState(Enum):
    """Represents the current playback state."""

    IDLE = auto()  # Default state on startup
    PLAYING = auto()
    PAUSED = auto()
    STOPPED = auto()


class RepeatMode(Enum):
    """Controls how tracks are repeated when playback reaches the end."""

    OFF = auto()
    ONE = auto()
    ALL = auto()


class ShutdownStage(Enum):
    """Tracks progress through the shutdown escalation ladder."""

    NOT_STARTED = auto()
    NORMAL_PENDING = auto()
    FORCE_QUIT_PENDING = auto()
    TERMINATE_PENDING = auto()
    DONE = auto()
