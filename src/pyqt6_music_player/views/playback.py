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
from pyqt6_music_player.constants import PlaybackStatus
from pyqt6_music_player.models import DefaultAudioInfo
from pyqt6_music_player.view_models import PlaybackViewModel
from pyqt6_music_player.views import IconButton, IconButtonFactory


# ================================================================================
# PLAYBACK PROGRESS
# ================================================================================
#
# ----- WIDGETS -----
class PlaybackProgressSlider(QSlider):
    """A horizontal slider widget for visualizing and controlling playback progress.

    This widget represents the current playback position of a track, and can be dragged
    to seek to a specific point in the playback.
    """

    def __init__(self):
        """Initialize PlaybackProgressSlider."""
        super().__init__(orientation=Qt.Orientation.Horizontal)


class ElapsedTimeLabel(QLabel):
    """A QLabel widget for displaying the elapsed time of the current track."""

    def __init__(self, elapsed_time=DefaultAudioInfo.duration):
        """Initialize ElapsedTimeLabel.

        Args:
            elapsed_time: The elapsed time in ('HH:MM:SS') format. The default
                          display is ('00:00:00').

        """
        super().__init__(text=elapsed_time)


class TimeRemainingLabel(QLabel):
    """A QLabel widget for displaying the time remaining of the current track."""

    def __init__(self, time_remaining=DefaultAudioInfo.duration):
        """Initialize TimeRemainingLabel.

        Args:
            time_remaining: The time remaining in ('HH:MM:SS') format. The default
                            display is ('00:00:00').

        """
        super().__init__(text=time_remaining)


# ----- COMPONENTS -----
class PlaybackProgress(QWidget):
    """A QWidget container for grouping playback progress widgets.

    This container also acts as the main view layer for playback progress,
    and is responsible for:
     - Displaying playback progress UIs.
     - Handling progress bar seek event by calling the appropriate viewmodel
       command (View -> ViewModel).

    """

    def __init__(self, playback_viewmodel: PlaybackViewModel):
        """Initialize PlaybackProgress.

        Args:
            playback_viewmodel: Playback control viewmodel.

        """
        super().__init__()
        # Viewmodel
        self._playback_viewmodel = playback_viewmodel

        # Widget
        self.progress_bar = PlaybackProgressSlider()
        self.elapsed_time = ElapsedTimeLabel()
        self.time_remaining = TimeRemainingLabel()

        # Setup
        self._init_ui()
        self._connect_signals()

    # --- Private methods ---
    def _init_ui(self):
        """Initialize instance internal widgets and layouts."""
        main_layout_horizontal = QHBoxLayout()

        # Left widget
        main_layout_horizontal.addWidget(self.elapsed_time)

        # Middle widget
        main_layout_horizontal.addWidget(self.progress_bar)

        # Right widget
        main_layout_horizontal.addWidget(self.time_remaining)

        main_layout_horizontal.setSpacing(10)

        self.setLayout(main_layout_horizontal)
        self.setDisabled(True)

    def _connect_signals(self):
        """Establish signal–slot connections between the viewmodel and view."""
        # ViewModel -> View (Event updates).
        self._playback_viewmodel.playback_started.connect(self._on_playback_started)
        self._playback_viewmodel.playback_position_changed.connect(
            self._on_playback_position_changed,
        )
        self._playback_viewmodel.initial_track_added.connect(self._on_initial_track_added)

    # --- Slots ---
    @pyqtSlot(int, str)
    def _on_playback_started(
            self,
            duration_in_ms: int,
            formatted_duration: str,
    ) -> None:
        """Configure UI initial display, and values.

        Args:
            duration_in_ms: The total track duration in ms.
            formatted_duration: The formatted duration in (hh:mm:ss) format.

        """
        # Set the progress bar range based on the total duration in milliseconds
        # to match the full track duration for smooth movement, and precise seeking.
        self.progress_bar.setRange(0, duration_in_ms)

        # Display the total duration so the user sees the full track length
        # before playback progresses.
        self.time_remaining.setText(formatted_duration)

    @pyqtSlot(int, str, str)
    def _on_playback_position_changed(
            self,
            elapsed_time_in_ms: int,
            formatted_elapsed_time: str,
            formatted_time_remaining: str,
    ):
        """Handle playback_position_changed by updating UI display, and position.

        Args:
            elapsed_time_in_ms: The elapsed time in ms.
            formatted_elapsed_time:  The formatted elapsed time in (hh:mm:ss) format.
            formatted_time_remaining: The formatted time remaining in (hh:mm:ss)
                                      format.

        """
        # TODO: Block progress bar setValue signal later before setting values
        #  when implementing seek functionality.
        # Keep the slider position and time displays in sync with the
        # actual playback position so the UI accurately reflects playback progress.
        self.progress_bar.setValue(elapsed_time_in_ms)
        self.elapsed_time.setText(formatted_elapsed_time)
        self.time_remaining.setText(formatted_time_remaining)

    @pyqtSlot()
    def _on_initial_track_added(self) -> None:
        """Handle initial_track_added by enabling playback component."""
        # Enable playback component on initial track add to allow playback operations.
        # Note: Playback component is disabled by default on app startup.
        if not self.isEnabled():
            self.setEnabled(True)


# ================================================================================
# PLAYBACK CONTROL
# ================================================================================
#
# --- WIDGETS ---
class PlayPauseButton(IconButton):
    """Play-Pause button for toggling current playback state.
    
    This button displays the current playback state (e.g., play or pause)
    via its icon, and allows the user to toggle between states when clicked.
    """

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
            icon_size: Size of the icon inside the button as
                       ``(width, height)`` in pixels. Defaults to ``(20, 20)``.
            widget_size: Size of the entire button widget as
                         ``(width, height)`` in pixels. Defaults to ``(40, 40)``.
            object_name: Qt object name, useful for QSS selectors.
                         Defaults to ``playPauseBtn``.

        """
        super().__init__(
            icon_path=icon_path,
            icon_size=icon_size,
            widget_size=widget_size,
            object_name=object_name,
        )

    def set_icon(self, icon_path: str | Path) -> None:
        """Set a new instance icon.

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
        """Initialize PlaybackControls.

        Args:
            playback_viewmodel: The playback control viewmodel.

        """
        super().__init__()
        # Viewmodel
        self._viewmodel = playback_viewmodel

        # Widget
        self.replay_button = ReplayButton()
        self.previous_button = PreviousButton()
        self.play_pause_button = PlayPauseButton()
        self.next_button = NextButton()
        self.repeat_button = RepeatButton()

        # Setup
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Initialize instance internal widgets and layouts."""
        main_layout_horizontal = QHBoxLayout()

        # Left widgets
        main_layout_horizontal.addWidget(self.replay_button)
        main_layout_horizontal.addWidget(self.previous_button)

        # Middle widget
        main_layout_horizontal.addWidget(self.play_pause_button)

        # Right widgets
        main_layout_horizontal.addWidget(self.next_button)
        main_layout_horizontal.addWidget(self.repeat_button)

        main_layout_horizontal.setSpacing(10)

        self.setLayout(main_layout_horizontal)
        self.setDisabled(True)

    def _connect_signals(self):
        """Establish signal–slot connections between the viewmodel and view."""
        # View -> Viewmodel (User actions).
        self.play_pause_button.clicked.connect(self._on_play_pause_button_clicked)
        self.next_button.clicked.connect(self._on_next_button_clicked)
        self.previous_button.clicked.connect(self._on_previous_button_clicked)

        # Viewmodel -> View (Event updates).
        self._viewmodel.initial_track_added.connect(self._on_initial_song_add)
        self._viewmodel.player_state_changed.connect(self._on_player_state_changed)

    # --- Slots ---
    @pyqtSlot()
    def _on_play_pause_button_clicked(self) -> None:
        self._viewmodel.play_pause()

    @pyqtSlot()
    def _on_next_button_clicked(self) -> None:
        self._viewmodel.next_track()

    @pyqtSlot()
    def _on_previous_button_clicked(self) -> None:
        self._viewmodel.previous_track()

    @pyqtSlot(PlaybackStatus)
    def _on_player_state_changed(self, player_state: PlaybackStatus):
        """Update play-pause button icon to reflect the current playback state."""
        if player_state is PlaybackStatus.PLAYING:
            self.play_pause_button.set_icon(PAUSE_ICON_PATH)
        else:
            self.play_pause_button.set_icon(PLAY_ICON_PATH)

    @pyqtSlot()
    def _on_initial_song_add(self):
        """Enable component after the first track is added."""
        self.setEnabled(True)
