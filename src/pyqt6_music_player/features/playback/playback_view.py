from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon, QImage
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QSlider, QVBoxLayout, QWidget

from pyqt6_music_player.core import ASSETS_PATH, IconButton, PlaybackState, RepeatMode

from .playback_viewmodel import PlaybackViewModel
from .playback_widgets import AlbumArtLabel, MarqueeLabel, RepeatButton, ShuffleButton

# ==================== CONSTANTS ====================
NEXT_ICON = ASSETS_PATH / "next_icon.svg"
PAUSE_ICON = ASSETS_PATH / "pause_icon.svg"
PLAY_ICON = ASSETS_PATH / "play_icon.svg"
PREV_ICON = ASSETS_PATH / "prev_icon.svg"
PRIMARY_PLAYBACK_CONTROL_BTN_SIZE = (40, 40)
PRIMARY_PLAYBACK_CONTROL_BTN_ICON_SIZE = (20, 20)
SECONDARY_PLAYBACK_CONTROL_BTN_SIZE = (30, 30)
SECONDARY_PLAYBACK_CONTROL_BTN_ICON_SIZE = (15, 15)


# ==================== PANELS ====================
#
# --- PLAYBACK CONTROLS ---
class PlaybackControlsPanel(QWidget):
    """QWidget container for grouping playback control widgets.

    This container also acts as the main view layer for playback controls including
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
        #
        # PANEL LAYOUT: Horizontal box
        main_layout_horizontal = QHBoxLayout()

        # LEFT WIDGETS: Shuffle and previous buttons
        main_layout_horizontal.addWidget(self.shuffle_button)
        main_layout_horizontal.addWidget(self.previous_button)

        # MIDDLE WIDGET: Play-pause button
        main_layout_horizontal.addWidget(self.play_pause_button)

        # RIGHT WIDGETS: Next and repeat buttons
        main_layout_horizontal.addWidget(self.next_button)
        main_layout_horizontal.addWidget(self.repeat_button)

        main_layout_horizontal.setSpacing(10)

        self.setLayout(main_layout_horizontal)
        self.setDisabled(True)

    def _connect_signals(self) -> None:
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

    @pyqtSlot(bool)
    def _on_shuffle_mode_change_requested(self, enabled: bool) -> None:
        self._viewmodel.set_shuffle_enabled(enabled)

    @pyqtSlot()
    def _on_previous_button_clicked(self) -> None:
        self._viewmodel.previous_track()

    @pyqtSlot()
    def _on_play_pause_button_clicked(self) -> None:
        self._viewmodel.toggle_playback()

    @pyqtSlot()
    def _on_next_button_clicked(self) -> None:
        self._viewmodel.next_track()

    @pyqtSlot(RepeatMode)
    def _on_repeat_mode_change_request(self, repeat_mode: RepeatMode) -> None:
        self._viewmodel.set_repeat_mode(repeat_mode)

    @pyqtSlot()
    def _on_initial_track_add(self) -> None:
        # Enable the panel on initial track add to allow playback operations because
        # the panel is disabled by default on app start.
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
            playback_viewmodel: The playback viewmodel.

        """
        super().__init__()
        # Viewmodel
        self._viewmodel = playback_viewmodel

        # Widgets
        self.elapsed_time_label = QLabel()
        self.seek_bar = QSlider()
        self.time_remaining_label = QLabel()

        # Setup
        self._init_ui()
        self._connect_signals()

    # -- Protected/internal methods --
    def _init_ui(self) -> None:
        # Setup instance widgets and layout
        #
        # WIDGET INITIAL STATE
        default_duration = self._viewmodel.active_track_formatted_duration

        # PANEL LAYOUT: Horizontal box
        main_layout_horizontal = QHBoxLayout()

        # LEFT WIDGET: Elapsed time label
        self.elapsed_time_label.setText(default_duration)

        main_layout_horizontal.addWidget(self.elapsed_time_label)

        # MIDDLE WIDGET: Seek bar
        self.seek_bar.setOrientation(Qt.Orientation.Horizontal)

        main_layout_horizontal.addWidget(self.seek_bar)

        # RIGHT WIDGET: Time remaining label
        self.time_remaining_label.setText(default_duration)

        main_layout_horizontal.addWidget(self.time_remaining_label)

        main_layout_horizontal.setSpacing(10)

        self.setLayout(main_layout_horizontal)
        self.setDisabled(True)

    def _connect_signals(self) -> None:
        # PlaybackProgressPanel -> PlaybackViewModel
        self.seek_bar.sliderPressed.connect(self._on_slider_pressed)
        self.seek_bar.sliderMoved.connect(self._on_slider_moved)
        self.seek_bar.sliderReleased.connect(self._on_slider_released)

        # PlaybackViewModel -> PlaybackProgressPanel
        self._viewmodel.playback_started.connect(self._on_playback_started)
        self._viewmodel.playback_position_changed.connect(
            self._on_playback_position_changed,
        )
        self._viewmodel.initial_tracks_added.connect(
            self._on_initial_track_added,
        )
        self._viewmodel.playback_cleared.connect(self._on_playback_cleared)

    @pyqtSlot()
    def _on_slider_pressed(self) -> None:
        self._viewmodel.begin_seek()

    @pyqtSlot()
    def _on_slider_moved(self) -> None:
        self._viewmodel.seek(self.seek_bar.value())

    @pyqtSlot()
    def _on_slider_released(self) -> None:
        self._viewmodel.end_seek(self.seek_bar.value())

    @pyqtSlot(str, str, QImage, int, str)
    def _on_playback_started(
            self,
            _title,
            _artist,
            _album_art,
            duration_in_ms: int,
            formatted_duration: str,
    ) -> None:
        # Set the progress bar range based on the total duration in milliseconds
        # to match the full track duration and for smooth, and precise seeking.
        self.seek_bar.setRange(0, duration_in_ms)
        self.time_remaining_label.setText(formatted_duration)

    @pyqtSlot(int, str, str)
    def _on_playback_position_changed(
            self,
            elapsed_time_in_ms: int,
            formatted_elapsed_time: str,
            formatted_time_remaining: str,
    ) -> None:
        # Keep the slider and time labels in sync with the actual playback progress
        self.seek_bar.blockSignals(True)
        self.seek_bar.setValue(elapsed_time_in_ms)
        self.seek_bar.blockSignals(False)

        self.elapsed_time_label.setText(formatted_elapsed_time)
        self.time_remaining_label.setText(formatted_time_remaining)

    @pyqtSlot()
    def _on_initial_track_added(self) -> None:
        # Enable the panel on initial track add to allow seek operation.
        # Note: The panel is disabled by default on app startup.
        if not self.isEnabled():
            self.setEnabled(True)

    @pyqtSlot(str, str, str)
    def _on_playback_cleared(self, _title, _artist, formatted_duration: str):
        self.seek_bar.setValue(0)

        self.elapsed_time_label.setText(formatted_duration)
        self.time_remaining_label.setText(formatted_duration)


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
        self.title_label = MarqueeLabel(object_name="trackTitleLabel")
        self.artist_label = MarqueeLabel(object_name="trackArtistLabel")

        # Setup
        self._init_ui()
        self._connect_signals()

    # -- Protected/internal methods --
    def _init_ui(self) -> None:
        # Setup instance widgets and layout
        #
        # WIDGET INITIAL STATE
        default_title = self._viewmodel.active_track_title
        default_artist = self._viewmodel.active_track_artist

        # PANEL LAYOUT: Horizontal box
        panel_layout = QHBoxLayout()

        # LEFT WIDGET: Album art
        panel_layout.addWidget(self.album_art)

        # RIGHT WIDGET: Vertical box container
        right_section_vertical = QVBoxLayout()

        # RIGHT CONTAINER WIDGETS: Title label (top), and artist label (bottom)
        self.title_label.setText(default_title)
        right_section_vertical.addWidget(self.title_label)

        self.artist_label.setText(default_artist)
        right_section_vertical.addWidget(self.artist_label)

        panel_layout.addLayout(right_section_vertical)

        self.setLayout(panel_layout)

    def _connect_signals(self) -> None:
        self._viewmodel.playback_started.connect(self._on_playback_started)
        self._viewmodel.playback_cleared.connect(self._on_playback_cleared)

    @pyqtSlot(str, str, QImage,  int, str)
    def _on_playback_started(
            self,
            track_title: str,
            track_artist: str,
            track_image: QImage,
            *_,
    ) -> None:
        # Display the active track's album art and metadata.
        self.album_art.update_image_display(track_image)
        self.title_label.setText(track_title)
        self.artist_label.setText(track_artist)

    @pyqtSlot(str, str, str)
    def _on_playback_cleared(self, track_title: str, track_artist: str, *_) -> None:
        self.album_art.reset_display()
        self.title_label.setText(track_title)
        self.artist_label.setText(track_artist)
