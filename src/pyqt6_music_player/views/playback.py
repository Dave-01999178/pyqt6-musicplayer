"""Playback UI components.

This module defines widgets responsible for track navigation, playback control,
and displaying playback progress including progress bar, elapsed,
and time remaining labels, play/pause, next/prev, repeat, and replay button.
"""
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QSlider, QWidget

from pyqt6_music_player.config import (
    MEDIUM_BUTTON,
    MEDIUM_ICON,
    NEXT_ICON_PATH,
    PAUSE_ICON_PATH,
    PLAY_ICON_PATH,
    PREV_ICON_PATH,
    REPEAT_ICON_PATH,
    REPLAY_ICON_PATH,
)
from pyqt6_music_player.constants import PlaybackState
from pyqt6_music_player.helpers import format_duration
from pyqt6_music_player.models import DefaultAudioInfo
from pyqt6_music_player.view_models import PlaybackViewModel
from pyqt6_music_player.views import IconButton, IconButtonFactory


# ================================================================================
# PLAYBACK PROGRESS
# ================================================================================
#
# --- WIDGETS ---
class PlaybackProgressSlider(QSlider):
    """A horizontal slider widget for visualizing and controlling playback progress.

    This widget represents the current playback position of a song. Users can drag
    the slider to seek to a specific point in the music.
    """

    def __init__(self):
        """Initialize PlaybackProgressSlider."""
        super().__init__(orientation=Qt.Orientation.Horizontal)


class ElapsedTimeLabel(QLabel):
    """A QLabel widget for displaying the elapsed time of the current song."""

    def __init__(self, text=DefaultAudioInfo.elapsed_time):
        """Initialize ElapsedTimeLabel.

        Args:
            text: The elapsed time. The default display is ('0:00:00')

        """
        super().__init__(text=text)


class TimeRemainingLabel(QLabel):
    """A QLabel widget for displaying the time remaining of the current song."""

    def __init__(self, text=DefaultAudioInfo.elapsed_time):
        """Initialize TimeRemainingLabel.

        Args:
            text: The time remaining. The default display is ('0:00:00')

        """
        super().__init__(text=text)


# --- COMPONENTS ---
class PlaybackProgress(QWidget):
    """A QWidget container for grouping playback progress widgets.

    This container also acts as the main view layer for playback progress,
    and is responsible for:
     - Displaying playback progress UIs.
     - Handling progress bar seek event by calling the appropriate viewmodel
       command (View -> ViewModel).
     - Observing viewmodel for audio player service for playback updates
       (ViewModel -> View).
    """

    def __init__(self, playback_viewmodel: PlaybackViewModel):
        """Initialize PlaybackProgress.

        Args:
            playback_viewmodel: The playback control viewmodel.

        """
        super().__init__()
        # Playback viewmodel
        self._viewmodel = playback_viewmodel

        # Playback progress widgets
        self.progress_bar = PlaybackProgressSlider()
        self.elapsed_time = ElapsedTimeLabel()
        self.total_duration = TimeRemainingLabel()

        # Setup
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Initialize instance's internal widgets and layouts."""
        layout = QHBoxLayout()

        layout.addWidget(self.elapsed_time)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.total_duration)

        layout.setSpacing(10)

        self.setLayout(layout)
        self.setDisabled(True)

    def _connect_signals(self):
        self._viewmodel.track_duration.connect(self._on_playback_start)
        self._viewmodel.position_changed.connect(self._on_playback_position_change)
        self._viewmodel.enable_ui.connect(self._on_initial_song_add)

    # --- Slots ---
    @pyqtSlot(int)
    def _on_playback_start(self, duration):
        duration_in_ms = duration * 1000

        self.progress_bar.setRange(0, duration_in_ms)

    @pyqtSlot(int, int)
    def _on_playback_position_change(self, elapsed_time: int, time_remaining: int):
        # TODO: Block signals later before setting values.
        self.progress_bar.setValue(elapsed_time)
        self.elapsed_time.setText(format_duration(elapsed_time // 1000))
        self.total_duration.setText(format_duration(time_remaining // 1000))

    @pyqtSlot()
    def _on_initial_song_add(self):
        self.setEnabled(True)


# ================================================================================
# PLAYBACK CONTROL
# ================================================================================
#
# --- WIDGETS ---
class PlayPauseButton(IconButton):
    """Play/Pause button."""

    def __init__(
            self,
            icon_path: Path = PLAY_ICON_PATH,
            icon_size: tuple[int, int] = MEDIUM_ICON,
            widget_size: tuple[int, int] = MEDIUM_BUTTON,
            object_name: str | None = "playPauseBtn",
    ):
        """Initialize PlayPauseButton.

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

    def update_icon(self, icon_path: str | Path) -> None:
        """Update the button's icon using the given icon.

        Args:
            icon_path: Icon image's file path.

        """
        icon = self.path_to_qicon(icon_path)

        self.setIcon(icon)


ReplayButton = IconButtonFactory(REPLAY_ICON_PATH)
PreviousButton = IconButtonFactory(PREV_ICON_PATH)
NextButton = IconButtonFactory(NEXT_ICON_PATH)
RepeatButton = IconButtonFactory(REPEAT_ICON_PATH)


# --- VIEW ---
class PlaybackControls(QWidget):
    """A QWidget container for grouping playback control, and track navigation widgets.

    This container also acts as the main view layer for playback control,
    and is responsible for:
     - Displaying playback control UIs.
     - Handling playback control input events by calling the appropriate viewmodel
       command (View -> ViewModel).
    """

    def __init__(self, playback_viewmodel: PlaybackViewModel) -> None:
        """Initialize PlaybackControls

        Args:
            playback_viewmodel: The playback control viewmodel.

        """
        super().__init__()
        # Viewmodel
        self._viewmodel = playback_viewmodel

        # Widgets
        self.replay_button = ReplayButton()
        self.previous_button = PreviousButton()
        self.play_pause_button = PlayPauseButton()
        self.next_button = NextButton()
        self.repeat_button = RepeatButton()

        # Setup
        self._init_ui()
        self._setup_binding()

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
        self.setDisabled(True)

    def _setup_binding(self):
        """Set up volume viewmodel and view binding."""
        # View -> Viewmodel
        self.play_pause_button.clicked.connect(self._on_play_pause_button_clicked)
        self.next_button.clicked.connect(self._on_next_button_clicked)
        self.previous_button.clicked.connect(self._on_previous_button_clicked)
        self.replay_button.clicked.connect(self._on_replay_button_clicked)
        self.repeat_button.clicked.connect(self._on_repeat_button_clicked)

        # Viewmodel -> View
        self._viewmodel.enable_ui.connect(self._on_initial_song_add)
        self._viewmodel.player_state_changed.connect(self._on_playback_state_changed)

    # --- Slots ---
    @pyqtSlot()
    def _on_play_pause_button_clicked(self):
        self._viewmodel.play_pause()

    @pyqtSlot()
    def _on_next_button_clicked(self):
        self._viewmodel.next_track()

    @pyqtSlot()
    def _on_previous_button_clicked(self):
        self._viewmodel.previous_track()

    @pyqtSlot()
    def _on_replay_button_clicked(self):
        self._viewmodel.replay()

    @pyqtSlot()
    def _on_repeat_button_clicked(self):
        self._viewmodel.repeat()

    @pyqtSlot(PlaybackState)
    def _on_playback_state_changed(self, playback_state):
        if playback_state in {PlaybackState.PAUSED, PlaybackState.STOPPED}:
            self.play_pause_button.update_icon(PLAY_ICON_PATH)
        else:
            self.play_pause_button.update_icon(PAUSE_ICON_PATH)

    @pyqtSlot()
    def _on_initial_song_add(self):
        self.setEnabled(True)
