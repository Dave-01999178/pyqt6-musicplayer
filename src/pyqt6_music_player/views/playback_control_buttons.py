"""
Custom PyQt6 button widgets for consistent UI components.

This module provides button widgets for managing music playback, such as play/pause,
next/previous track, and repeat functionality.
"""
from pyqt6_music_player.config import (
    PLAYBACK_BUTTON_LARGE,
    PLAYBACK_BUTTON_SMALL,
    NEXT_ICON_PATH,
    PLAY_ICON_PATH,
    PLAY_ICON_SIZE,
    PREV_ICON_PATH,
    REPEAT_ICON_PATH,
    REPLAY_ICON_PATH,
)
from pyqt6_music_player.views import IconButton


class ReplayButton(IconButton):
    """Replay button widget with a small icon size."""
    def __init__(self):
        """Initializes replay button."""
        super().__init__(
            icon_path=REPLAY_ICON_PATH,
            widget_size=PLAYBACK_BUTTON_SMALL
        )


class PreviousButton(IconButton):
    """Previous track button widget with a small icon size."""
    def __init__(self):
        """Initializes previous track button."""
        super().__init__(
            icon_path=PREV_ICON_PATH,
            widget_size=PLAYBACK_BUTTON_SMALL,
            object_name="navigationBtn"
        )


class PlayPauseButton(IconButton):
    """Play/Pause button with custom size, icon, and stylesheet name."""
    def __init__(self):
        """Initializes play/pause button."""
        super().__init__(
            icon_path=PLAY_ICON_PATH,
            widget_size=PLAYBACK_BUTTON_LARGE,
            icon_size=PLAY_ICON_SIZE,
            object_name="playPauseBtn"
        )


class NextButton(IconButton):
    """Next track button widget with a small icon size."""
    def __init__(self):
        """Initializes next track button."""
        super().__init__(
            icon_path=NEXT_ICON_PATH,
            widget_size=PLAYBACK_BUTTON_SMALL,
            object_name="navigationBtn"
        )


class RepeatButton(IconButton):
    """Repeat button widget with a small icon size."""
    def __init__(self):
        """Initializes repeat button."""
        super().__init__(
            icon_path=REPEAT_ICON_PATH,
            widget_size=PLAYBACK_BUTTON_SMALL
        )
