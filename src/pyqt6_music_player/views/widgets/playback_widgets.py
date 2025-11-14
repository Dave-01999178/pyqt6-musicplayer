"""
This module contains UI components playback progress such as progress bar, and labels for
displaying song's elapsed time and total duration.
"""
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QSlider

from pyqt6_music_player.config import (
    MEDIUM_BUTTON,
    MEDIUM_ICON,
    NEXT_ICON_PATH,
    PLAY_ICON_PATH,
    PREV_ICON_PATH,
    REPEAT_ICON_PATH,
    REPLAY_ICON_PATH,
)
from pyqt6_music_player.constants import DefaultAudioInfo
from pyqt6_music_player.views import IconButton, IconButtonFactory


# ================================================================================
# PLAYBACK PROGRESS WIDGETS
# ================================================================================
class PlaybackProgressSlider(QSlider):
    """
    A horizontal slider widget (QSlider) for visualizing and controlling music playback progress.

    This widget represents the current playback position of a song. Users can drag
    the slider to seek to a specific point in the music.
    """
    def __init__(self):
        """Initializes PlaybackProgressSlider instance."""
        super().__init__(orientation=Qt.Orientation.Horizontal)


# TODO: Consider using factory if QLabels remain static.
class ElapsedTimeLabel(QLabel):
    """
    A QLabel widget for displaying the elapsed time of the current song.

    The default display is empty ('0:00:00').
    """
    def __init__(self):
        """Initializes ElapsedTimeLabel instance."""
        super().__init__(
            text=DefaultAudioInfo.elapsed_time
        )


class TotalDurationLabel(QLabel):
    """
    A QLabel widget for displaying the total duration of the current song.

    The default display is empty ('').
    """
    def __init__(self):
        """Initializes TotalDurationLabel instance."""
        super().__init__(
            text=DefaultAudioInfo.total_duration
        )


# ================================================================================
# PLAYBACK CONTROL WIDGETS
# ================================================================================
class PlayPauseButton(IconButton):
    """A custom play/pause button."""
    def __init__(
            self,
            icon_path: Path = PLAY_ICON_PATH,
            icon_size: tuple[int, int] = MEDIUM_ICON,
            widget_size: tuple[int, int] = MEDIUM_BUTTON,
            object_name: str | None = "playPauseBtn"
    ):
        """
        Initializes PlayPauseButton instance.

        Args:
            icon_path: Path to the icon file. Defaults to 'play' icon.
            icon_size: ``(width, height)`` of the *icon* inside the button.
                       Defaults to ``(20, 20)``.
            widget_size: ``(width, height)`` of the whole button widget. Defaults to ``(40, 40)``.
            object_name: Qt object name – useful for QSS selectors. Defaults to ``playPauseBtn``.
        """
        super().__init__(
            icon_path=icon_path,
            icon_size=icon_size,
            widget_size=widget_size,
            object_name=object_name
        )


ReplayButton = IconButtonFactory(REPLAY_ICON_PATH)
PreviousButton = IconButtonFactory(PREV_ICON_PATH)
NextButton = IconButtonFactory(NEXT_ICON_PATH)
RepeatButton = IconButtonFactory(REPEAT_ICON_PATH)
