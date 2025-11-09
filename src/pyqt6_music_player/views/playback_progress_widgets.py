"""
This module contains UI components playback progress such as progress bar, and labels for
displaying song's elapsed time and total duration.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QSlider

from pyqt6_music_player.constant import DefaultAudioInfo


class PlaybackProgressSlider(QSlider):
    """
    A horizontal slider widget (QSlider) for visualizing and controlling music playback progress.

    This widget represents the current playback position of a song. Users can drag
    the slider to seek to a specific point in the music.
    """
    def __init__(self):
        """Initializes PlaybackProgressSlider instance."""
        super().__init__(orientation=Qt.Orientation.Horizontal)


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
