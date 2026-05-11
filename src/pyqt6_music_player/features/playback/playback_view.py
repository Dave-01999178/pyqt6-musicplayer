from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QSlider, QVBoxLayout, QWidget

from pyqt6_music_player.core import (
    DEFAULT_SLIDER_RANGE,
    NEXT_ICON,
    PAUSE_ICON,
    PLAY_ICON,
    PREV_ICON,
    PRIMARY_PLAYBACK_CONTROL_BTN_ICON_SIZE,
    PRIMARY_PLAYBACK_CONTROL_BTN_SIZE,
    SECONDARY_PLAYBACK_CONTROL_BTN_ICON_SIZE,
    SECONDARY_PLAYBACK_CONTROL_BTN_SIZE,
    PlaybackState,
    RepeatMode,
    ShuffleMode,
)
from pyqt6_music_player.track import DEFAULT_TRACK, DefaultTrackInfo
from pyqt6_music_player.widgets import (
    AlbumArtLabel,
    IconButton,
    MarqueeLabel,
    RepeatButton,
    ShuffleButton,
)

from .playback_viewmodel import PlaybackViewModel


# ==================== PANELS ====================
#
# --- PLAYBACK CONTROLS ---
class PlaybackControlsPanel(QWidget):
    """QWidget container for grouping playback control widgets.

    This container also acts as the main view layer for playback control including
    next, previous, shuffle, repeat and play/pause button.
    """

    def __init__(self, playback_viewmodel: PlaybackViewModel) -> None:
        """Initialize PlaybackControlsPanel.

        Args:
            playback_viewmodel: The playback viewmodel.

        """
        super().__init__()
        # Viewmodel
        self._viewmodel = playback_viewmodel

        # Widgets
        self.shuffle_button = ShuffleButton()
        self.previous_button = IconButton(
            PREV_ICON,
            icon_size=SECONDARY_PLAYBACK_CONTROL_BTN_ICON_SIZE,
            widget_size=SECONDARY_PLAYBACK_CONTROL_BTN_SIZE,
        )
        self.play_pause_button = IconButton(
            PLAY_ICON,
            icon_size=PRIMARY_PLAYBACK_CONTROL_BTN_ICON_SIZE,
            widget_size=PRIMARY_PLAYBACK_CONTROL_BTN_SIZE,
            object_name="playPauseBtn",
        )
        self.next_button = IconButton(
            NEXT_ICON,
            icon_size=SECONDARY_PLAYBACK_CONTROL_BTN_ICON_SIZE,
            widget_size=SECONDARY_PLAYBACK_CONTROL_BTN_SIZE,
        )
        self.repeat_button = RepeatButton()

        # Setup
        self._init_ui()
        self._connect_signals()

    # -- Protected/internal methods --
    def _init_ui(self) -> None:
        # Setup instance widgets and layout
        main_layout_horizontal = QHBoxLayout()

        # Left widgets: Shuffle, and previous button
        main_layout_horizontal.addWidget(self.shuffle_button)
        main_layout_horizontal.addWidget(self.previous_button)

        # Middle widget: Play-pause button
        main_layout_horizontal.addWidget(self.play_pause_button)

        # Right widgets: Next, and repeat buttons
        main_layout_horizontal.addWidget(self.next_button)
        main_layout_horizontal.addWidget(self.repeat_button)

        main_layout_horizontal.setSpacing(10)

        self.setLayout(main_layout_horizontal)
        self.setDisabled(True)

    def _connect_signals(self) -> None:
        # Establish PlaybackControlsPanel-PlaybackViewModel connection.
        #
        # PlaybackControlsPanel -> PlaybackViewModel
        self.shuffle_button.change_shuffle_mode_request.connect(
            self._on_shuffle_mode_change_requested,
        )
        self.previous_button.clicked.connect(self._on_previous_button_clicked)
        self.play_pause_button.clicked.connect(self._on_play_pause_button_clicked)
        self.next_button.clicked.connect(self._on_next_button_clicked)
        self.repeat_button.change_repeat_mode_request.connect(
            self._on_repeat_mode_change_request,
        )

        # PlaybackViewModel -> PlaybackControlsPanel
        self._viewmodel.initial_tracks_added.connect(self._on_initial_track_add)
        self._viewmodel.playback_state_changed.connect(self._on_player_state_changed)

    @pyqtSlot(ShuffleMode)
    def _on_shuffle_mode_change_requested(self, shuffle_mode: ShuffleMode) -> None:
        # Call viewmodel set shuffle mode command
        self._viewmodel.set_shuffle_mode(shuffle_mode)

    @pyqtSlot()
    def _on_previous_button_clicked(self) -> None:
        # Call viewmodel previous-track command
        self._viewmodel.previous_track()

    @pyqtSlot()
    def _on_play_pause_button_clicked(self) -> None:
        # Call viewmodel toggle-playback command
        self._viewmodel.toggle_playback()

    @pyqtSlot()
    def _on_next_button_clicked(self) -> None:
        # Call viewmodel next-track command
        self._viewmodel.next_track()

    @pyqtSlot(RepeatMode)
    def _on_repeat_mode_change_request(self, repeat_mode: RepeatMode) -> None:
        # Call viewmodel set repeat mode command
        self._viewmodel.set_repeat_mode(repeat_mode)

    @pyqtSlot()
    def _on_initial_track_add(self) -> None:
        # Enable the panel on initial track add to allow playback operations.
        # Note: The panel is disabled by default on app start.
        if not self.isEnabled():
            self.setEnabled(True)

    @pyqtSlot(PlaybackState)
    def _on_player_state_changed(self, player_state: PlaybackState) -> None:
        # Update play-pause button icon to reflect the current playback state.
        icon = (
            PAUSE_ICON
            if player_state == PlaybackState.PLAYING
            else PLAY_ICON
        )
        self.play_pause_button.setIcon(QIcon(str(icon)))


# --- PLAYBACK PROGRESS ---
class PlaybackProgressPanel(QWidget):
    """QWidget container for grouping playback progress widgets.

    This container also acts as the main view layer for playback progress including
    elapsed time label, duration label and progress bar.
    """

    def __init__(self, playback_viewmodel: PlaybackViewModel):
        """Initialize PlaybackProgressPanel.

        Args:
            playback_viewmodel: The playback control viewmodel.

        """
        super().__init__()
        # Viewmodel
        self._playback_viewmodel = playback_viewmodel

        # Widgets
        self.elapsed_time = QLabel(DefaultTrackInfo.duration)
        self.seek_bar = QSlider()
        self.time_remaining = QLabel(DefaultTrackInfo.duration)

        # Setup
        self._init_ui()
        self._connect_signals()

    # -- Protected/internal methods --
    def _init_ui(self) -> None:
        # Setup instance widgets and layout
        main_layout_horizontal = QHBoxLayout()

        # Left widget: Elapsed time label
        main_layout_horizontal.addWidget(self.elapsed_time)

        # Middle widget: Seek bar
        self.seek_bar.setOrientation(Qt.Orientation.Horizontal)
        self.seek_bar.setRange(*DEFAULT_SLIDER_RANGE)

        main_layout_horizontal.addWidget(self.seek_bar)

        # Right widget: Time remaining label
        main_layout_horizontal.addWidget(self.time_remaining)

        main_layout_horizontal.setSpacing(10)

        self.setLayout(main_layout_horizontal)
        self.setDisabled(True)

    def _connect_signals(self) -> None:
        # PlaybackProgressPanel -> PlaybackViewModel
        self.seek_bar.sliderPressed.connect(self._on_slider_pressed)
        self.seek_bar.sliderMoved.connect(self._on_slider_moved)
        self.seek_bar.sliderReleased.connect(self._on_slider_released)

        # PlaybackViewModel -> PlaybackProgressPanel
        self._playback_viewmodel.playback_started.connect(self._on_playback_started)
        self._playback_viewmodel.playback_position_changed.connect(
            self._on_playback_position_changed,
        )
        self._playback_viewmodel.initial_tracks_added.connect(
            self._on_initial_track_added,
        )

    @pyqtSlot()
    def _on_slider_pressed(self) -> None:
        self._playback_viewmodel.begin_seek()

    @pyqtSlot()
    def _on_slider_moved(self) -> None:
        self._playback_viewmodel.seek(self.seek_bar.value())

    @pyqtSlot()
    def _on_slider_released(self) -> None:
        self._playback_viewmodel.end_seek(self.seek_bar.value())

    @pyqtSlot(str, str, int, str)
    def _on_playback_started(
            self,
            _title,
            _artist,
            duration_in_ms: int,
            formatted_duration: str,
    ) -> None:
        # Set the progress bar range based on the total duration in milliseconds
        # to match the full track duration for smooth movement, and precise seeking.
        self.seek_bar.setRange(0, duration_in_ms)

        # Display the total duration so the user sees the full track length
        # before playback progresses.
        self.time_remaining.setText(formatted_duration)

    @pyqtSlot(int, str, str)
    def _on_playback_position_changed(
            self,
            elapsed_time_in_ms: int,
            formatted_elapsed_time: str,
            formatted_time_remaining: str,
    ) -> None:
        # Keep the slider position and time displays in sync with the
        # actual playback position so the UI accurately reflects playback progress.
        self.seek_bar.blockSignals(True)
        self.seek_bar.setValue(elapsed_time_in_ms)
        self.seek_bar.blockSignals(False)

        # Display the elapsed time and time-remaining so the user sees the
        # playback progress.
        self.elapsed_time.setText(formatted_elapsed_time)
        self.time_remaining.setText(formatted_time_remaining)

    @pyqtSlot()
    def _on_initial_track_added(self) -> None:
        # Enable the panel on initial track add to allow seek operation.
        # Note: The panel is disabled by default on app startup.
        if not self.isEnabled():
            self.setEnabled(True)


class NowPlayingPanel(QWidget):
    """QWidget container for grouping widgets that displays current track information.

    This container also acts as the main view layer for now-playing widgets including
    title label, artist label and album art.
    """

    def __init__(self, playback_viewmodel: PlaybackViewModel):
        """Initialize NowPlayingPanel.

        Args:
            playback_viewmodel: The playback viewmodel.

        """
        super().__init__()
        # Viewmodel
        self._viewmodel = playback_viewmodel

        # Widgets
        self.album_art = AlbumArtLabel()
        self.title_label = MarqueeLabel(
            DEFAULT_TRACK.title,
            object_name="trackTitleLabel",
        )
        self.artist_label = MarqueeLabel(
            DEFAULT_TRACK.artist,
            object_name="trackArtistLabel",
        )

        # Setup
        self._init_ui()

        self._viewmodel.playback_started.connect(self._on_playback_started)

    # -- Protected/internal methods --
    def _init_ui(self) -> None:
        # Setup instance widgets and layout
        main_layout_horizontal = QHBoxLayout()

        # Left widget: Album art
        main_layout_horizontal.addWidget(self.album_art)

        # Right section: Title label (top), and artist label (bottom)
        right_section_vertical = QVBoxLayout()

        right_section_vertical.addWidget(self.title_label)
        right_section_vertical.addWidget(self.artist_label)

        main_layout_horizontal.addLayout(right_section_vertical)

        self.setLayout(main_layout_horizontal)

    @pyqtSlot(str, str, int, str)
    def _on_playback_started(self, track_title: str, track_artist: str, *_) -> None:
        # Display active track metadata in UI
        self.title_label.setText(track_title)
        self.artist_label.setText(track_artist)
