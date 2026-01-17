from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QSlider, QWidget

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
from pyqt6_music_player.helpers import format_duration
from pyqt6_music_player.view_models import PlaybackControlViewModel
from pyqt6_music_player.views import IconButton, IconButtonFactory


# ================================================================================
# PLAYBACK PROGRESS WIDGETS
# ================================================================================
class PlaybackProgressSlider(QSlider):
    """A horizontal slider widget for visualizing and controlling playback progress.

    This widget represents the current playback position of a song. Users can drag
    the slider to seek to a specific point in the music.
    """

    def __init__(self):
        """Initialize PlaybackProgressSlider instance."""
        super().__init__(orientation=Qt.Orientation.Horizontal)


class ElapsedTimeLabel(QLabel):
    """A QLabel widget for displaying the elapsed time of the current song.

    The default display is empty ('0:00:00').
    """

    def __init__(self, text=DefaultAudioInfo.elapsed_time):
        """Initialize ElapsedTimeLabel instance."""
        super().__init__(text=text)


class TotalDurationLabel(QLabel):
    """A QLabel widget for displaying the total duration of the current song.

    The default display is empty ('').
    """

    def __init__(self, text=DefaultAudioInfo.elapsed_time):
        """Initialize TotalDurationLabel instance."""
        super().__init__(text=text)


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
            object_name: str | None = "playPauseBtn",
    ):
        """Initialize PlayPauseButton instance.

        Args:
            icon_path: Path to the icon file. Defaults to 'play' icon.
            icon_size: ``(width, height)`` of the *icon* inside the button.
                       Defaults to ``(20, 20)``.
            widget_size: ``(width, height)`` of the whole button widget.
                         Defaults to ``(40, 40)``.
            object_name: Qt object name - useful for QSS selectors.
                         Defaults to ``playPauseBtn``.

        """
        super().__init__(
            icon_path=icon_path,
            icon_size=icon_size,
            widget_size=widget_size,
            object_name=object_name,
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
    """A QWidget container for widgets used to control and display playback progress.

    This includes progress bar, and time labels.
    """

    def __init__(self, playback_viewmodel: PlaybackControlViewModel):
        """Initialize PlaybackProgress instance."""
        super().__init__()
        self._viewmodel = playback_viewmodel
        self.progress_bar = PlaybackProgressSlider()
        self.elapsed_time = ElapsedTimeLabel()
        self.total_duration = TotalDurationLabel()

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Initialize the container's internal widgets and layouts."""
        layout = QHBoxLayout()

        layout.addWidget(self.elapsed_time)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.total_duration)

        layout.setSpacing(10)

        self.setLayout(layout)

    def _connect_signals(self):
        self._viewmodel.track_duration.connect(self._on_playback_start)
        self._viewmodel.position_changed.connect(self._on_playback_position_change)

    def _on_playback_start(self, duration):
        self.progress_bar.setRange(0, duration * 1000)

    def _on_playback_position_change(self, elapsed_time: int, time_remaining: int):
        # TODO: Block signals later before setting values.
        self.progress_bar.setValue(elapsed_time)
        self.elapsed_time.setText(format_duration(elapsed_time // 1000))
        self.total_duration.setText(format_duration(time_remaining // 1000))


# ================================================================================
# PLAYBACK CONTROLS
# ================================================================================
class PlaybackControls(QWidget):
    """A QWidget container for track navigation, and playback control widgets.

    This includes replay, next, previous, repeat, and play/pause button.
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
        """Initialize the instance's internal widgets and layouts."""
        layout = QHBoxLayout()

        layout.addWidget(self.replay_button)
        layout.addWidget(self.previous_button)
        layout.addWidget(self.play_pause_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.repeat_button)

        layout.setSpacing(10)

        self.setLayout(layout)

    def _bind_viewmodel(self):
        # View -> Viewmodel
        self.play_pause_button.clicked.connect(self._on_play_pause_button_clicked)
        self.next_button.clicked.connect(self._on_next_button_clicked)
        self.previous_button.clicked.connect(self._on_previous_button_clicked)
        self.replay_button.clicked.connect(self._on_replay_button_clicked)
        self.repeat_button.clicked.connect(self._on_repeat_button_clicked)

    # TODO: Switch out toggle to avoid UI and player sync issues.
    #  E.g. toggled to play and the player did not run on first playback.
    def _on_play_pause_button_clicked(self):
        self._viewmodel.play_pause()

    def _on_next_button_clicked(self):
        self._viewmodel.next_track()

    def _on_previous_button_clicked(self):
        self._viewmodel.previous_track()

    def _on_replay_button_clicked(self):
        self._viewmodel.replay()

    def _on_repeat_button_clicked(self):
        self._viewmodel.repeat()
