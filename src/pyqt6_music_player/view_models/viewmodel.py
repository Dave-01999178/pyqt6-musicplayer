# TODO: Consider splitting this monolithic module into separate individual module
#  when it grows, or became complex for easy navigation.
import logging
from collections.abc import Sequence
from typing import ClassVar

from PyQt6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QObject,
    Qt,
    pyqtSignal,
    pyqtSlot,
)

from pyqt6_music_player.constants import PlaybackState
from pyqt6_music_player.helpers import format_duration
from pyqt6_music_player.models import (
    TrackAudio,
    AudioPlayerService,
    Track,
    PlaylistModel,
    VolumeModel,
)

logger = logging.getLogger(__name__)


# ================================================================================
# PLAYBACK CONTROL VIEWMODEL
# ================================================================================
# noinspection PyUnresolvedReferences
class PlaybackViewModel(QObject):
    track_info = pyqtSignal(str, str)
    track_duration = pyqtSignal(int)
    position_changed = pyqtSignal(int, int)
    player_state_changed = pyqtSignal(PlaybackState)
    shutdown_finished = pyqtSignal()

    enable_ui = pyqtSignal()

    def __init__(self, playlist_model: PlaylistModel, player_engine: AudioPlayerService,
    ):
        super().__init__()
        self._player_engine = player_engine
        self._playlist = playlist_model

        self._current_track = None

        self._connect_signals()

    def _connect_signals(self):
        # Model -> Viewmodel
        self._playlist.playlist_changed.connect(self._on_playlist_initial_add_song)
        self._playlist.playing_index_changed.connect(self._on_playlist_index_changed)

        # AudioPlayer -> Viewmodel
        self._player_engine.playback_started.connect(
            self._on_audio_player_playback_start
        )
        self._player_engine.frame_position_changed.connect(
            self._on_audio_player_position_change
        )
        self._player_engine.playback_state_changed.connect(
            self.player_state_changed.emit
        )
        self._player_engine.playback_ended.connect(self.next_track)
        self._player_engine.worker_resources_released.connect(self.shutdown_finished)

    # --- Slots ---
    @pyqtSlot()
    def _on_audio_player_playback_start(self):
        song_title = self._current_track.title
        song_album = self._current_track.album
        song_duration = int(self._current_track.duration)

        self.track_info.emit(song_title, song_album)
        self.track_duration.emit(song_duration)

        logger.info("Now playing: %s.\n", song_title)

    @pyqtSlot(float, float)
    def _on_audio_player_position_change(
            self,
            elapsed_time: float,
            time_remaining: float,
    ):
        elapsed_time = int(elapsed_time * 1000)
        time_remaining = int(time_remaining * 1000)

        self.position_changed.emit(elapsed_time, time_remaining)

    @pyqtSlot(int)
    def _on_playlist_initial_add_song(self, new_song_count) -> None:
        if self._playlist.song_count - new_song_count != 0:
            return

        self.enable_ui.emit()

    @pyqtSlot(int)
    def _on_playlist_index_changed(self, new_index: int):
        selected_track = self._playlist.get_track(new_index)
        audio = self._get_audio(selected_track)

        if audio is not None:
            self._player_engine.load_audio(audio)

            # TODO: Extract and move to another slot, this should only trigger
            #  when audio is loaded successfully.
            self._current_track = selected_track

            self._player_engine.start_playback()

    # --- Private methods ---
    @staticmethod
    def _get_audio(track: Track) -> TrackAudio | None:
        file_path = track.path

        return TrackAudio.from_file(file_path)

    def _load_and_play(self, track: Track = None) -> None:
        track_to_use = track or self._playlist.selected_track

        if track_to_use == self._current_track:
            return

        audio = self._get_audio(track_to_use)

        if audio is None:
            return

        self._player_engine.load_audio(audio)

        # TODO: Extract and move to another slot, this should only trigger
        #  when audio is loaded successfully.
        selected_index = self._playlist.selected_index

        self._current_track = track_to_use
        self._playlist.set_playing_index(selected_index)

        self._player_engine.start_playback()

    # --- Commands ---
    def play_pause(self):
        """Start, pause and resume playback based on the current playback state."""
        if self._playlist.selected_track is None:
            return

        # Resume
        if self._player_engine.playback_state is PlaybackState.PAUSED:
            self._player_engine.resume_playback()

        # Pause
        elif self._player_engine.playback_state is PlaybackState.PLAYING:
            self._player_engine.pause_playback()

        # Start a new playback
        else:
            self._load_and_play()  # Load on demand approach.

    @pyqtSlot()
    def next_track(self):
        self._playlist.next_track()

    def previous_track(self):
        self._playlist.prev_track()

    def replay(self):
        pass

    def repeat(self):
        pass

    def seek(self):
        pass

    def shutdown(self):
        self._player_engine.shutdown()

    def service_running(self) -> bool:
        return self._player_engine.is_running()


# ================================================================================
# PLAYLIST VIEWMODEL
# ================================================================================
class PlaylistViewModel(QAbstractTableModel):
    """Playlist viewmodel.

    This class acts as an intermediary between the PlaylistModel and any
    UI components that display or modify the application's playlist state.

    It forwards model updates to the view via Qt signals and provides
    commands for modifying playlist model.
    """

    model_index_updated = pyqtSignal(int)

    DEFAULT_COLUMNS: ClassVar[tuple[tuple[str, str]]] = (
        ("title", "Title"),
        ("artist", "Artist"),
        ("album", "Album"),
        ("duration", "Duration"),
    )
    def __init__(self, playlist_model: PlaylistModel):
        """Initialize PlaylistViewModel instance."""
        super().__init__()
        self._model = playlist_model

        self._model.playlist_changed.connect(self._on_model_song_added)
        self._model.selected_index_changed.connect(self._on_model_index_updated)

    # --- QAbstractTableModel methods (overridden) ---
    def rowCount(self, parent=None):
        """Set the number of row based on the length of current playlist."""
        return len(self._model.playlist)

    def columnCount(self, parent=None):
        """Set the number of column based on the number of song metadata."""
        return len(self.DEFAULT_COLUMNS)

    def data(self, index, role=...):
        """Display the text in row cells."""
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()
        song = self._model.playlist[row]
        field_name = self.DEFAULT_COLUMNS[col][0]

        if role == Qt.ItemDataRole.DisplayRole:
            if field_name == "duration":
                return format_duration(song.duration)
            return getattr(song, field_name)

        if role == Qt.ItemDataRole.TextAlignmentRole and field_name == "duration":
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter

        return None

    def headerData(self, section, orientation, role=...):
        """Display the text in headers cells."""
        field_title = self.DEFAULT_COLUMNS[section][1]
        is_header_field = (
                role == Qt.ItemDataRole.DisplayRole
                and orientation == Qt.Orientation.Horizontal
        )
        is_duration_field = (
                role == Qt.ItemDataRole.TextAlignmentRole
                and field_title == "Duration"
        )

        if is_header_field:
            return field_title

        if is_duration_field:
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter

        return None

    # --- Slots ---
    # TODO: Initial implementation (insertion order), replace later.
    @pyqtSlot(int)
    def _on_model_song_added(self, new_song_count: int) -> None:
        """Insert and display the added song(s) to the playlist widget."""
        prev_playlist_len = self._model.song_count - new_song_count

        self.beginInsertRows(
            QModelIndex(),
            prev_playlist_len,
            self._model.song_count - 1,
        )
        self.endInsertRows()

    @pyqtSlot(int)
    def _on_model_index_updated(self, new_index: int) -> None:
        """Notify the view of model index changes.

        Args:
            new_index: The updated model index.

        """
        self.model_index_updated.emit(new_index)  # type: ignore

    # --- Commands ---
    def add_songs(self, files: Sequence[str]) -> None:
        """Command for adding new songs to playlist model.

        Args:
            files: A sequence of path-like objects.

        """
        self._model.add_songs(files)

    def set_selected_index(self, index: int) -> None:
        """Command for setting a new index in playlist model.

        Args:
            index: The selected row index in playlist widget.

        """
        self._model.set_selected_index(index)


# ================================================================================
# VOLUME VIEWMODEL
# ================================================================================
class VolumeViewModel(QObject):
    """Volume viewmodel.

    This class acts as a middleman between the VolumeModel and VolumeControls
    that display or modify the application's volume state.

    It forwards model updates to the view via Qt signals and provides
    commands for view to modify the volume model.
    """

    model_volume_changed = pyqtSignal(int)
    model_mute_state_changed = pyqtSignal(bool)

    def __init__(self, volume_model: VolumeModel, player_engine):
        """Initialize VolumeViewModel instance."""
        super().__init__()
        self._player_engine = player_engine
        self._model = volume_model

        # Establish Model-ViewModel connection.
        self._connect_signals()

    def _connect_signals(self):
        self._model.volume_changed.connect(self._on_model_volume_changed)
        self._model.mute_changed.connect(self._on_model_mute_changed)

    def _on_model_volume_changed(self, new_volume: int) -> None:
        """Notify the volume view of model volume changes.

        Args:
            new_volume: The new model volume.

        """
        self.model_volume_changed.emit(new_volume)  # type: ignore

    def _on_model_mute_changed(self, muted: bool) -> None:
        """Notify the volume view of model mute state changes.

        Args:
            muted: The new model mute state.

        """
        self.model_mute_state_changed.emit(muted)  # type: ignore

    def refresh(self) -> None:
        """Re-emit the current volume to refresh any subscribed views.

        Useful when view needs initial state sync.
        """
        self.model_volume_changed.emit(self._model.current_volume)  # type: ignore

    # --- Commands ---
    def set_volume(self, new_volume) -> None:
        """Command for updating model volume.

        Args:
            new_volume: The new volume value to set.

        """
        self._model.set_volume(new_volume)

    def set_mute(self, mute: bool) -> None:
        """Command for toggling model mute state.

        Args:
              mute: The new mute state to set.

        """
        self._model.set_muted(mute)
