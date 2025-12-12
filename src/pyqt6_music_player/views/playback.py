"""
This module contains UI components playback progress such as progress bar, and labels for
displaying song's elapsed time and total duration.
"""
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QSlider, QWidget, QHBoxLayout

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
from pyqt6_music_player.view_models import PlaybackControlViewModel


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
        self.setCheckable(True)


ReplayButton = IconButtonFactory(REPLAY_ICON_PATH)
PreviousButton = IconButtonFactory(PREV_ICON_PATH)
NextButton = IconButtonFactory(NEXT_ICON_PATH)
RepeatButton = IconButtonFactory(REPEAT_ICON_PATH)


# ================================================================================
# PLAYBACK PROGRESS
# ================================================================================
class PlaybackProgress(QWidget):
    """
    A QWidget container for widgets that is used to control and display playback progress
    such as progress bar, and time labels.
    """

    def __init__(self):
        """Initializes PlaybackProgress instance."""
        super().__init__()
        self.progress_bar = PlaybackProgressSlider()
        self.elapsed_time = ElapsedTimeLabel()
        self.total_duration = TotalDurationLabel()

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Initializes the container's internal widgets and layouts."""
        layout = QHBoxLayout()

        layout.addWidget(self.elapsed_time)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.total_duration)

        layout.setSpacing(10)

        self.setLayout(layout)

    def _connect_signals(self):
        """Connects the progress bar to the section-level signal."""
        pass


# ================================================================================
# PLAYBACK CONTROLS
# ================================================================================
class PlaybackControls(QWidget):
    """
    A QWidget container for widgets that is used for track navigation and controlling playback
    such as replay, next, previous, repeat, and play/pause button.
    """

    def __init__(self, playback_viewmodel: PlaybackControlViewModel) -> None:
        """Initialize PlaybackControls instance."""
        super().__init__()
        self._viewmodel = playback_viewmodel

        self.replay_button = ReplayButton()
        self.previous_button = PreviousButton()
        self.play_pause_button = PlayPauseButton()
        self.next_button = NextButton()
        self.repeat_button = RepeatButton()

        self._init_ui()
        self._bind_viewmodel()

    def _init_ui(self):
        """Initializes the instance's internal widgets and layouts"""
        layout = QHBoxLayout()

        layout.addWidget(self.replay_button)
        layout.addWidget(self.previous_button)
        layout.addWidget(self.play_pause_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.repeat_button)

        layout.setSpacing(10)

        self.setLayout(layout)

    def _bind_viewmodel(self):
        self.play_pause_button.toggled.connect(self._on_play_pause_button_clicked)
        self.next_button.clicked.connect(self._on_next_button_clicked)
        self.previous_button.clicked.connect(self._on_previous_button_clicked)
        self.replay_button.clicked.connect(self._on_replay_button_clicked)
        self.repeat_button.clicked.connect(self._on_repeat_button_clicked)

    def _on_play_pause_button_clicked(self, play: bool):
        self._viewmodel.play_pause(play)

    def _on_next_button_clicked(self):
        self._viewmodel.next_track()

    def _on_previous_button_clicked(self):
        self._viewmodel.previous_track()

    def _on_replay_button_clicked(self):
        self._viewmodel.replay()

    def _on_repeat_button_clicked(self):
        self._viewmodel.repeat()
