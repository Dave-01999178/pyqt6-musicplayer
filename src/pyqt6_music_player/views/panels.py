from PyQt6.QtCore import QModelIndex, Qt, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from pyqt6_music_player.core import (
    ADD_ICON_PATH,
    DEFAULT_SLIDER_RANGE,
    FILE_DIALOG_FILTER,
    LOAD_FOLDER_ICON_PATH,
    MEDIUM_BUTTON,
    MEDIUM_ICON,
    NEXT_ICON_PATH,
    PAUSE_ICON_PATH,
    PLAY_ICON_PATH,
    PLAYLIST_MANAGER_BTN_SIZE,
    PREV_ICON_PATH,
    REMOVE_ICON_PATH,
    REPEAT_ICON_PATH,
    REPLAY_ICON_PATH,
    PlaybackStatus,
)
from pyqt6_music_player.models import DEFAULT_TRACK, DefaultTrackInfo
from pyqt6_music_player.view_models import (
    PlaybackViewModel,
    PlaylistViewModel,
    VolumeViewModel,
)
from pyqt6_music_player.views import (
    AlbumArtLabel,
    IconButton,
    MarqueeLabel,
    PlaylistWidget,
    VolumeButton,
    VolumeLabel,
)


# ================================================================================
# PLAYLIST MANAGER
# ================================================================================
class PlaylistManagerPanel(QWidget):
    """QWidget container for grouping playlist manager widgets.

    This container also acts as the main view layer for the playlist manager,
    and is responsible for:
     - Organizing and displaying playlist manager widgets.
     - Handling playlist manager widget events by calling the appropriate viewmodel
       commands (View -> ViewModel).
    """

    def __init__(self, playlist_viewmodel: PlaylistViewModel):
        """Initialize PlaylistManagerPanel.

        Args:
            playlist_viewmodel: The playlist viewmodel.

        """
        super().__init__()
        # Viewmodel
        self._playlist_viewmodel = playlist_viewmodel

        # Widgets
        self._add_track_btn = IconButton(
            ADD_ICON_PATH,
            widget_size=PLAYLIST_MANAGER_BTN_SIZE,
            button_text="Add song(s)",
            object_name="addSongBtn",
        )
        self._remove_track_btn = IconButton(
            REMOVE_ICON_PATH,
            widget_size=PLAYLIST_MANAGER_BTN_SIZE,
            button_text="Remove",
            object_name="removeSongBtn",
        )
        self._load_folder_btn = IconButton(
            LOAD_FOLDER_ICON_PATH,
            widget_size=PLAYLIST_MANAGER_BTN_SIZE,
            button_text="Load folder",
            object_name="loadFolderBtn",
        )

        # Setup
        self._init_ui()
        self._connect_signals()

    # --- Protected/internal methods ---
    def _init_ui(self):
        main_layout_horizontal = QHBoxLayout()

        # Left widget: Add track button
        main_layout_horizontal.addWidget(self._add_track_btn)

        # Middle widget: Remove track button
        main_layout_horizontal.addWidget(self._remove_track_btn)

        # Right widget: Load folder button
        main_layout_horizontal.addWidget(self._load_folder_btn)

        main_layout_horizontal.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter
        )

        self.setLayout(main_layout_horizontal)

    def _connect_signals(self):
        # Wire PlaylistManagerPanel signals to slots.
        self._add_track_btn.clicked.connect(self._on_add_track_button_clicked)

    @pyqtSlot()
    def _on_add_track_button_clicked(self) -> None:
        file_paths, _ = QFileDialog.getOpenFileNames(
            parent=self,
            filter=FILE_DIALOG_FILTER,
        )

        # Do nothing if the file dialog is cancelled.
        if not file_paths:
            return

        # Add the selected audio files to the playlist.
        self._playlist_viewmodel.add_tracks(file_paths)


# ================================================================================
# PLAYLIST
# ================================================================================
class PlaylistDisplayPanel(QWidget):
    """QWidget container for the main playlist widget.

    This container also acts as the main view layer for playlist widget,
    and is responsible for:
     - Organizing and displaying playlist widgets.
     - Handling playlist widget events by calling the appropriate viewmodel
       commands (View -> ViewModel).

    """

    def __init__(self, playlist_viewmodel: PlaylistViewModel):
        """Initialize PlaylistDisplayPanel.

        Args:
            playlist_viewmodel: The playlist viewmodel.

        """
        super().__init__()
        # Viewmodel
        self._playlist_viewmodel = playlist_viewmodel

        # Widget
        self._playlist_widget = PlaylistWidget()
        self._playlist_widget.setModel(self._playlist_viewmodel)

        self.selection_model = self._playlist_widget.selectionModel()

        # Setup
        self._init_ui()
        self._connect_signals()

    # --- Protected/internal methods ---
    def _init_ui(self):
        instance_layout = QVBoxLayout()

        instance_layout.addWidget(self._playlist_widget)

        self.setLayout(instance_layout)

    def _connect_signals(self):
        # Establish PlaylistDisplayPanel-PlaylistViewModel connection.
        #
        # PlaylistDisplayPanel -> PlaylistViewModel
        self.selection_model.currentRowChanged.connect(self._on_row_changed)

        # PlaylistViewModel -> PlaylistDisplayPanel
        self._playlist_viewmodel.selected_index_changed.connect(
            self._on_model_index_changed
        )

    @pyqtSlot(QModelIndex, QModelIndex)
    def _on_row_changed(self, current_index: QModelIndex, previous_index: QModelIndex):
        # Store the index of the selected row in playlist widget.
        if not current_index.isValid():
            return

        row_index = current_index.row()

        self._playlist_viewmodel.set_selected_index(row_index)

    @pyqtSlot(int)
    def _on_model_index_changed(self, new_index: int) -> None:
        # Set the selected row in playlist to the new index.
        if new_index != self._playlist_widget.currentIndex().row():
            self._playlist_widget.selectRow(new_index)


# ================================================================================
# NOW PLAYING
# ================================================================================
class NowPlayingPanel(QWidget):
    """QWidget container for grouping widgets that displays current song information.

    This container also acts as the main view layer for 'now playing' widgets,
    and is responsible for:
     - Organizing and displaying 'now playing' widgets.
     - Displaying current track information.

    """

    def __init__(self, playback_viewmodel: PlaybackViewModel):
        """Initialize NowPlayingPanel."""
        super().__init__()
        # Viewmodel
        self._viewmodel = playback_viewmodel

        # Widget
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

        self._connect_signals()

    # --- Protected/internal methods ---
    def _init_ui(self):
        main_layout_horizontal = QHBoxLayout()

        # Left widget: Album art
        main_layout_horizontal.addWidget(self.album_art)

        # Right section: Title label (top), and artist label (bottom)
        right_section_vertical = QVBoxLayout()

        right_section_vertical.addWidget(self.title_label)
        right_section_vertical.addWidget(self.artist_label)

        main_layout_horizontal.addLayout(right_section_vertical)

        self.setLayout(main_layout_horizontal)

    def _connect_signals(self):
        # Wire ViewModel signals to NowPlayingPanel slots.
        self._viewmodel.track_loaded.connect(self._on_track_loaded)

    @pyqtSlot(str, str, int, str)
    def _on_track_loaded(self, track_title: str, track_artist: str, *_) -> None:
        # Display loaded track metadata in UI.
        self.title_label.setText(track_title)
        self.artist_label.setText(track_artist)


# ================================================================================
# PLAYBACK CONTROLS
# ================================================================================
class PlaybackControlsPanel(QWidget):
    """QWidget container for grouping playback control, and track navigation widgets.

    This container also acts as the main view layer for playback control,
    and is responsible for:
     - Organizing and displaying playback control widgets.
     - Handling playback control widget events by calling the appropriate viewmodel
       commands (View -> ViewModel).

    """

    def __init__(self, playback_viewmodel: PlaybackViewModel) -> None:
        """Initialize PlaybackControlsPanel.

        Args:
            playback_viewmodel: The playback control viewmodel.

        """
        super().__init__()
        # Viewmodel
        self._viewmodel = playback_viewmodel

        # Widget
        self.replay_button = IconButton(REPLAY_ICON_PATH)
        self.previous_button = IconButton(PREV_ICON_PATH)
        self.play_pause_button = IconButton(
            PLAY_ICON_PATH,
            icon_size=MEDIUM_ICON,
            widget_size=MEDIUM_BUTTON,
            object_name="playPauseBtn",
        )
        self.next_button = IconButton(NEXT_ICON_PATH)
        self.repeat_button = IconButton(REPEAT_ICON_PATH)

        # Setup
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        main_layout_horizontal = QHBoxLayout()

        # Left widgets: Replay, and previous button
        main_layout_horizontal.addWidget(self.replay_button)
        main_layout_horizontal.addWidget(self.previous_button)

        # Middle widget: Play-pause button
        main_layout_horizontal.addWidget(self.play_pause_button)

        # Right widgets: Next, and repeat buttons
        main_layout_horizontal.addWidget(self.next_button)
        main_layout_horizontal.addWidget(self.repeat_button)

        main_layout_horizontal.setSpacing(10)

        self.setLayout(main_layout_horizontal)
        self.setDisabled(True)

    def _connect_signals(self):
        # Establish PlaybackControlsPanel-PlaybackViewModel connection.
        #
        # PlaybackControlsPanel -> PlaybackViewModel
        self.play_pause_button.clicked.connect(self._on_play_pause_button_clicked)
        self.next_button.clicked.connect(self._on_next_button_clicked)
        self.previous_button.clicked.connect(self._on_previous_button_clicked)

        # PlaybackViewModel -> PlaybackControlsPanel
        self._viewmodel.initial_track_added.connect(self._on_initial_track_add)
        self._viewmodel.player_state_changed.connect(self._on_player_state_changed)

    @pyqtSlot()
    def _on_initial_track_add(self):
        # Enable the panel on initial track add to allow playback operations.
        # Note: The panel is disabled by default on app start.
        self.setEnabled(True)

    @pyqtSlot()
    def _on_play_pause_button_clicked(self) -> None:
        # Call viewmodel toggle-playback command.
        self._viewmodel.toggle_playback()

    @pyqtSlot()
    def _on_next_button_clicked(self) -> None:
        # Call viewmodel next-track command.
        self._viewmodel.next_track()

    @pyqtSlot()
    def _on_previous_button_clicked(self) -> None:
        # Call viewmodel previous-track command.
        self._viewmodel.previous_track()

    @pyqtSlot(PlaybackStatus)
    def _on_player_state_changed(self, player_state: PlaybackStatus):
        # Update play-pause button icon to reflect the current playback state.
        if player_state is PlaybackStatus.PLAYING:
            self.play_pause_button.setIcon(QIcon(str(PAUSE_ICON_PATH)))
        else:
            self.play_pause_button.setIcon(QIcon(str(PLAY_ICON_PATH)))


# ================================================================================
# PLAYBACK PROGRESS
# ================================================================================
class PlaybackProgressPanel(QWidget):
    """QWidget container for grouping playback progress widgets.

    This container also acts as the main view layer for playback progress,
    and is responsible for:
     - Organizing and displaying playback progress widgets.
     - Handling progress bar seek event by calling the appropriate viewmodel
       command (View -> ViewModel).
     - Displaying playback progress.

    """

    def __init__(self, playback_viewmodel: PlaybackViewModel):
        """Initialize PlaybackProgressPanel.

        Args:
            playback_viewmodel: Playback control viewmodel.

        """
        super().__init__()
        # Viewmodel
        self._playback_viewmodel = playback_viewmodel

        # Widget
        self.elapsed_time = QLabel(DefaultTrackInfo.duration)
        self.seek_bar = QSlider()
        self.time_remaining = QLabel(DefaultTrackInfo.duration)

        # Pre-seek playback state tracker.
        self._pre_seek_playback_state: PlaybackStatus | None = None

        # Setup
        self._init_ui()
        self._connect_signals()

    # --- Private methods ---
    def _init_ui(self):
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

    def _connect_signals(self):
        # Establish PlaybackProgressPanel-PlaybackViewModel connection.
        #
        # PlaybackProgressPanel -> PlaybackViewModel
        self.seek_bar.sliderPressed.connect(self._on_slider_pressed)
        self.seek_bar.sliderMoved.connect(self._on_slider_moved)
        self.seek_bar.sliderReleased.connect(self._on_slider_released)

        # PlaybackViewModel -> PlaybackProgressPanel
        self._playback_viewmodel.track_loaded.connect(self._on_track_loaded)
        self._playback_viewmodel.playback_position_changed.connect(
            self._on_playback_position_changed,
        )
        self._playback_viewmodel.initial_track_added.connect(self._on_initial_track_added)

    @pyqtSlot()
    def _on_slider_pressed(self):
        curr_playback_status = self._playback_viewmodel.get_playback_status()

        self._pre_seek_playback_state = curr_playback_status

        if curr_playback_status == PlaybackStatus.PLAYING:
            self._playback_viewmodel.pause()

    @pyqtSlot()
    def _on_slider_moved(self):
        self._playback_viewmodel.seek(self.seek_bar.value())

    @pyqtSlot()
    def _on_slider_released(self):
        self._playback_viewmodel.seek(self.seek_bar.value())

        if self._pre_seek_playback_state == PlaybackStatus.PLAYING:
            self._playback_viewmodel.resume()

            self._pre_seek_playback_state = None

    @pyqtSlot(str, str, int, str)
    def _on_track_loaded(
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
    ):
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


# ================================================================================
# VOLUME CONTROLS
# ================================================================================
class VolumeControlsPanel(QWidget):
    """A QWidget container for grouping volume widgets.

    This container also acts as the main view layer for volume and is responsible for:
     - Organizing and displaying volume widgets.
     - Handling volume widgets input events by calling the appropriate viewmodel
       commands (View -> ViewModel).
     - Displaying current volume state and information.

    """

    def __init__(self, volume_viewmodel: VolumeViewModel):
        """Initialize VolumeControlsPanel.

        Args:
            volume_viewmodel: The volume viewmodel.

        """
        super().__init__()
        # Viewmodel
        self._viewmodel = volume_viewmodel

        # Widgets
        self._volume_button = VolumeButton()
        self._volume_slider = QSlider()
        self._volume_label = VolumeLabel()

        # Setup
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        main_layout_horizontal = QHBoxLayout()

        # Left widget: Volume button
        main_layout_horizontal.addWidget(self._volume_button)

        # Middle widget: Volume slider
        self._volume_slider.setOrientation(Qt.Orientation.Horizontal)
        self._volume_slider.setRange(*DEFAULT_SLIDER_RANGE)

        main_layout_horizontal.addWidget(self._volume_slider)

        # Right widget: Volume label
        main_layout_horizontal.addWidget(self._volume_label)

        main_layout_horizontal.setSpacing(5)

        self.setLayout(main_layout_horizontal)

    def _connect_signals(self) -> None:
        # Establish VolumeControlsPanel-VolumeViewModel connection.
        #
        # VolumeControlsPanel -> VolumeViewModel
        self._volume_slider.valueChanged.connect(self._viewmodel.set_volume)
        self._volume_button.toggled.connect(self._viewmodel.set_mute)

        # VolumeViewModel -> VolumeControlsPanel
        self._viewmodel.model_volume_changed.connect(self._on_model_volume_changed)
        self._viewmodel.model_mute_state_changed.connect(
            self._on_model_mute_state_changed,
        )

        # Refresh/re-emit to set UI initial state on startup.
        self._viewmodel.refresh()

    # --- Slots ---
    @pyqtSlot(int)
    def _on_model_volume_changed(self, new_volume: int) -> None:
        # Update volume button icon.
        self._volume_button.blockSignals(True)
        self._volume_button.update_icon(new_volume)
        self._volume_button.blockSignals(False)

        # Update volume slider value.
        self._volume_slider.blockSignals(True)
        self._volume_slider.setValue(new_volume)
        self._volume_slider.blockSignals(False)

        # Update volume label display.
        self._volume_label.setNum(new_volume)

    @pyqtSlot(bool)
    def _on_model_mute_state_changed(self, is_muted: bool) -> None:
        self._volume_button.blockSignals(True)
        self._volume_button.setChecked(is_muted)
        self._volume_button.blockSignals(False)
