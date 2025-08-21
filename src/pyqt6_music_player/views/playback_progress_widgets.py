"""
Widgets for visualizing and controlling music playback.

This module contains UI components such as a progress bar, and labels for
displaying elapsed and total song durations.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSlider

from pyqt6_music_player.models.music_player_state import MusicPlayerState
from pyqt6_music_player.views.base_widgets import BaseLabel


class PlaybackProgressBar(QSlider):
    """
    A horizontal slider for visualizing and controlling music playback progress.

    This widget represents the current playback position of a song. Users can drag
    the slider to seek to a specific point in the music.
    """
    def __init__(self):
        """Initializes the playback progress bar."""
        super().__init__(orientation=Qt.Orientation.Horizontal)


class ElapsedTimeLabel(BaseLabel):
    """A label widget for displaying the elapsed time of the current song."""
    def __init__(self, state: MusicPlayerState):
        """
        Initializes the elapsed time label.

        Args:
            state: The music player state object containing.
        """
        super().__init__(
            label_text=f"{state.song_progress.elapsed_time}"
        )


class TotalDurationLabel(BaseLabel):
    """A label widget for displaying the total duration of the current song."""
    def __init__(self, state: MusicPlayerState):
        """
        Initializes the total duration label.

        Args:
            state: The music player state object containing.
        """
        super().__init__(
            label_text=f"{state.song_progress.time_remaining}",
            alignment=Qt.AlignmentFlag.AlignRight
        )
