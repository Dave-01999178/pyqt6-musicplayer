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
from pyqt6_music_player.models import DEFAULT_TRACK, DefaultAudioInfo
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
class PlaylistManager(QWidget):
    """A QWidget container for grouping playlist manager widgets.

    This container also acts as the main view layer for the playlist manager,
    and is responsible for:
     - Grouping and displaying playlist manager buttons.
     - Handling playlist manager events by calling the appropriate viewmodel commands
       (View -> ViewModel).
    """

    def __init__(self, playlist_viewmodel: PlaylistViewModel):
        """Initialize PlaylistManager.

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

    # --- Private methods ---
    def _init_ui(self):
        """Initialize instance's internal widgets and layouts."""
        layout = QHBoxLayout()

        layout.addWidget(self._add_track_btn)
        layout.addWidget(self._remove_track_btn)
        layout.addWidget(self._load_folder_btn)

        layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def _connect_signals(self):
        """Connect button widget signals to their respective slots."""
        # View -> ViewModel (user actions).
        self._add_track_btn.clicked.connect(self._on_add_track_btn_clicked)

    # --- Slots ---
    @pyqtSlot()
    def _on_add_track_btn_clicked(self) -> None:
        """Add track button click event signal handler."""
        # The `getOpenFileNames()` returns a tuple containing the list of selected
        # filenames, and the name of the selected filter so we use `_` to discard
        # the filter name.
        file_paths, _ = QFileDialog.getOpenFileNames(
            parent=self,
            filter=FILE_DIALOG_FILTER,
        )

        # Do nothing if the file dialog is cancelled.
        if not file_paths:
            return

        self._playlist_viewmodel.add_tracks(file_paths)


# ================================================================================
# PLAYLIST
# ================================================================================
class PlaylistDisplay(QWidget):
    """A QWidget container for the main playlist widget.

    This container also acts as the main view layer for playlist,
    and is responsible for:
     - Displaying main playlist widget.
     - Handling playlist-related input events by calling the appropriate viewmodel
       commands (View -> ViewModel).
    """

    def __init__(self, playlist_viewmodel: PlaylistViewModel):
        """Initialize PlaylistDisplay.

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

    # --- UI and Widgets ---
    def _init_ui(self):
        """Initialize instance's internal widgets and layouts."""
        section_layout = QVBoxLayout()

        section_layout.addWidget(self._playlist_widget)

        self.setLayout(section_layout)

    def _connect_signals(self):
        """Connect playlist widget, and viewmodel signals to their respective slots."""
        # View -> ViewModel (User actions).
        self.selection_model.currentRowChanged.connect(self._on_row_changed)

        # ViewModel -> View (Event updates).
        self._playlist_viewmodel.selected_index_changed.connect(self._on_model_index_changed)

    # --- Slots ---
    @pyqtSlot(QModelIndex, QModelIndex)
    def _on_row_changed(self, current_index: QModelIndex, previous_index: QModelIndex):
        """Playlist row selection change signal handler.

        Args:
            current_index: The selected row index.
            previous_index: The previous selected row index.

        """
        if not current_index.isValid():
            return

        row_index = current_index.row()

        self._playlist_viewmodel.set_selected_index(row_index)

    @pyqtSlot(int)
    def _on_model_index_changed(self, new_index: int) -> None:
        """Model selected index update signal handler.

        Updates the playlist widget's highlighted row (track) if it's new.

        Args:
            new_index: The updated index from model.

        """
        if new_index != self._playlist_widget.currentIndex().row():
            self._playlist_widget.selectRow(new_index)


# ================================================================================
# NOW PLAYING
# ================================================================================
class NowPlaying(QWidget):
    """QWidget container for widgets that displays current song information.

    This includes album art, song title, and artist label.
    """

    def __init__(self, playback_viewmodel: PlaybackViewModel):
        """Initialize NowPlaying."""
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

        self._init_ui()

        self._viewmodel.track_loaded.connect(self._on_track_loaded)

    # --- Private methods ---
    def _init_ui(self):
        """Initialize instance internal widgets and layouts."""
        main_layout_horizontal = QHBoxLayout()

        # Left: Album art widget
        main_layout_horizontal.addWidget(self.album_art)

        # Right: Metadata label section
        right_section_vertical = QVBoxLayout()

        right_section_vertical.addWidget(self.title_label)
        right_section_vertical.addWidget(self.artist_label)

        main_layout_horizontal.addLayout(right_section_vertical)

        self.setLayout(main_layout_horizontal)

    @pyqtSlot(str, str, int, str)
    def _on_track_loaded(self, track_title: str, track_artist: str, *_) -> None:
        """Display loaded track metadata in UI.

        Args:
            track_title: The track title.
            track_artist: The track artist.

        """
        self.title_label.setText(track_title)
        self.artist_label.setText(track_artist)


# ================================================================================
# PLAYBACK CONTROLS
# ================================================================================
class PlaybackControls(QWidget):
    """QWidget container for grouping playback control, and track navigation widgets.

    This container also acts as the main view layer for playback control,
    and is responsible for:
     - Displaying playback control UIs.
     - Handling playback control input by calling the appropriate viewmodel
       commands (View -> ViewModel).
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
        self.replay_button = IconButton(REPLAY_ICON_PATH)
        self.previous_button = IconButton(PREV_ICON_PATH)
        self.play_pause_button = IconButton(
            PLAY_ICON_PATH,
            icon_size=MEDIUM_ICON,
            widget_size=MEDIUM_BUTTON,
            object_name="playPauseBtn"
        )
        self.next_button = IconButton(NEXT_ICON_PATH)
        self.repeat_button = IconButton(REPEAT_ICON_PATH)

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
        self._viewmodel.toggle_playback()

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
            self.play_pause_button.setIcon(QIcon(str(PAUSE_ICON_PATH)))
        else:
            self.play_pause_button.setIcon(QIcon(str(PLAY_ICON_PATH)))

    @pyqtSlot()
    def _on_initial_song_add(self):
        """Enable component after the first track is added."""
        self.setEnabled(True)


# ================================================================================
# PLAYBACK PROGRESS
# ================================================================================
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
        self.elapsed_time = QLabel(DefaultAudioInfo.duration)
        self.seek_bar = QSlider()
        self.time_remaining = QLabel(DefaultAudioInfo.duration)

        # Setup
        self._init_ui()
        self._connect_signals()

    # --- Private methods ---
    def _init_ui(self):
        """Initialize instance internal widgets and layouts."""
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
        """Establish signal–slot connections between the viewmodel and view."""
        # ViewModel -> View (Event updates).
        self._playback_viewmodel.track_loaded.connect(self._on_track_loaded)
        self._playback_viewmodel.playback_position_changed.connect(
            self._on_playback_position_changed,
        )
        self._playback_viewmodel.initial_track_added.connect(self._on_initial_track_added)

        self.seek_bar.sliderPressed.connect(self._on_slider_pressed)
        self.seek_bar.sliderMoved.connect(self._on_slider_moved)
        self.seek_bar.sliderReleased.connect(self._on_slider_released)

    @pyqtSlot()
    def _on_slider_pressed(self):
        playback_status = self._playback_viewmodel.get_playback_status()
        if playback_status == PlaybackStatus.PLAYING:
            self._playback_viewmodel.pause()

    @pyqtSlot()
    def _on_slider_moved(self):
        self._playback_viewmodel.seek(self.seek_bar.value())

    @pyqtSlot()
    def _on_slider_released(self):
        self._playback_viewmodel.seek(self.seek_bar.value())

        playback_status = self._playback_viewmodel.get_playback_status()
        if playback_status == PlaybackStatus.PAUSED:
            self._playback_viewmodel.resume()

    # --- Slots ---
    @pyqtSlot(str, str, int, str)
    def _on_track_loaded(
            self,
            _title,
            _artist,
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
        """Handle playback_position_changed by updating UI display, and position.

        Args:
            elapsed_time_in_ms: The elapsed time in ms.
            formatted_elapsed_time:  The formatted elapsed time in (hh:mm:ss) format.
            formatted_time_remaining: The formatted time remaining in (hh:mm:ss)
                                      format.

        """
        # Keep the slider position and time displays in sync with the
        # actual playback position so the UI accurately reflects playback progress.
        self.seek_bar.blockSignals(True)
        self.seek_bar.setValue(elapsed_time_in_ms)
        self.seek_bar.blockSignals(False)

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
# VOLUME CONTROLS
# ================================================================================
class VolumeControls(QWidget):
    """A QWidget container for grouping volume widgets.

    This container also acts as the main view layer for volume and is responsible for:
     - Grouping and displaying volume UIs.
     - Handling volume-related input events by calling the appropriate viewmodel
       commands (View -> ViewModel).
     - Observing viewmodel layer for model updates (ViewModel -> View).
    """

    def __init__(self, volume_viewmodel: VolumeViewModel):
        """Initialize VolumeControls.

        Args:
            volume_viewmodel: The volume viewmodel.

        """
        super().__init__()
        # Volume viewmodel
        self._viewmodel = volume_viewmodel

        # Volume widgets
        self._volume_button = VolumeButton()
        self._volume_slider = QSlider()
        self._volume_label = VolumeLabel()

        self._init_ui()
        self._bind_viewmodel()

    def _init_ui(self):
        """Initialize instance's internal widgets and layouts."""
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

    def _bind_viewmodel(self) -> None:
        """Bind volume viewmodel to view."""
        # View -> ViewModel (user actions).
        self._volume_slider.valueChanged.connect(self._viewmodel.set_volume)
        self._volume_button.toggled.connect(self._viewmodel.set_mute)

        # ViewModel -> View (model updates).
        self._viewmodel.model_volume_changed.connect(self._on_model_volume_changed)
        self._viewmodel.model_mute_state_changed.connect(
            self._on_model_mute_state_changed,
        )

        # Refresh/re-emit to set UI initial state on startup.
        self._viewmodel.refresh()

    # --- Slots ---
    @pyqtSlot(int)
    def _on_model_volume_changed(self, new_volume: int) -> None:
        """Update volume widgets on model volume change."""
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
        """Update the volume button state on model mute state change."""
        self._volume_button.blockSignals(True)
        self._volume_button.setChecked(is_muted)
        self._volume_button.blockSignals(False)
