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
    AudioData,
    AudioPlayerService,
    AudioTrack,
    PlaylistModel,
    VolumeModel,
)

logger = logging.getLogger(__name__)


# ================================================================================
# PLAYBACK CONTROL VIEWMODEL
# ================================================================================
# noinspection PyUnresolvedReferences
class PlaybackControlViewModel(QObject):
    track_info = pyqtSignal(str, str)
    track_duration = pyqtSignal(int)
    position_changed = pyqtSignal(int, int)
    player_playback_state_changed = pyqtSignal(PlaybackState)
    shutdown_finished = pyqtSignal()

    enable_ui = pyqtSignal()

    def __init__(
            self,
            playlist_model: PlaylistModel,
            player_engine: AudioPlayerService,
    ):
        super().__init__()
        self._player_engine = player_engine
        self._playlist = playlist_model

        self._current_song = None

        self._connect_signals()

    def _connect_signals(self):
        # Model -> Viewmodel
        self._playlist.playlist_changed.connect(self._on_playlist_add_song)

        # AudioPlayer -> Viewmodel
        self._player_engine.audio_data_loaded.connect(self._play)
        self._player_engine.playback_started.connect(self._on_audio_player_playback_start)
        self._player_engine.position_changed.connect(self._on_audio_player_position_change)
        self._player_engine.player_playback_state_changed.connect(
            self._on_player_playback_state_changed
        )
        self._player_engine.playback_finished.connect(self.next_track)
        self._player_engine.shutdown_finished.connect(self.shutdown_finished)

    # --- Slots ---
    @pyqtSlot()
    def _on_audio_player_playback_start(self):
        song_title = self._current_song.title
        song_album = self._current_song.album
        song_duration = int(self._current_song.duration)

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

    @pyqtSlot(PlaybackState)
    def _on_player_playback_state_changed(self, new_playback_state: PlaybackState) -> None:
        self.player_playback_state_changed.emit(new_playback_state)

    @pyqtSlot(int)
    def _on_playlist_add_song(self, new_song_count):
        if self._playlist.song_count - new_song_count == 0:
            self.enable_ui.emit()

    # --- Private methods ---
    # TODO: Separate loading later for better Separation of Concerns (SoC).
    def _load_song(self, song: AudioTrack) -> None:
        if song == self._current_song:
            return

        file_path = song.path
        audio_data = AudioData.from_file(file_path)

        if audio_data is not None:
            self._player_engine.load_audio(audio_data)

            self._current_song = song

            return

        logging.info("Failed to load song: %s.", file_path)

    def _play(self):
        self._player_engine.start_playback()

    # --- Commands ---
    def play_pause(self):
        """Start, pause and resume playback based on the current playback state."""
        # Do nothing if there's no song playing or selected.
        if self._playlist.selected_song is None:
            return

        # Resume
        if self._player_engine.playback_state is PlaybackState.PAUSED:
            self._player_engine.resume_playback()

        # Pause
        elif self._player_engine.playback_state is PlaybackState.PLAYING:
            self._player_engine.pause_playback()

        # Start playback
        else:
            selected_song = self._playlist.selected_song

            self._load_song(selected_song)


    @pyqtSlot()
    def next_track(self):
        current_index = self._playlist.current_index

        # Can't move on to the next track if there's no song selected or playing.
        if current_index is None and self._current_song is None:
            return

        self._playlist.set_selected_index(current_index + 1)

        next_song = self._playlist.selected_song

        self._load_song(next_song)

    def previous_track(self):
        current_index = self._playlist.current_index

        # Can't move on to the previous track if there's no song selected or playing.
        if current_index is None and self._current_song is None:
            return

        self._playlist.set_selected_index(current_index - 1)

        prev_song = self._playlist.selected_song

        self._load_song(prev_song)

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
    index_updated = pyqtSignal(int)
    """
    Viewmodel responsible for exposing playlist-related data and commands
    to the View layer in an MVVM architecture.

    This class acts as an intermediary between the PlaylistModel and any
    UI components that display or modify the application's playlist state.

    It forwards model updates to the view via Qt signals and provides
    commands for modifying playlist model.
    """
    DEFAULT_COLUMNS: ClassVar[tuple[tuple[str, str]]] = (
        ("title", "Title"),
        ("artist", "Artist"),
        ("album", "Album"),
        ("duration", "Duration"),
    )
    def __init__(self, playlist_model: PlaylistModel):
        super().__init__()
        self._model = playlist_model

        self._model.playlist_changed.connect(self._on_model_song_insert)
        self._model.index_updated.connect(self._on_index_update)

    # --- QAbstractTableModel interface - Required methods (overridden) ---
    def rowCount(self, parent=None):
        return len(self._model.playlist)

    def columnCount(self, parent=None):
        return len(self.DEFAULT_COLUMNS)

    def data(self, index, role=...):
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

    # TODO: Temporary logic, replace later.
    # Notify views if new song(s) are added.
    # Initial implementation (insertion order).
    @pyqtSlot(int)
    def _on_model_song_insert(self, new_song_count: int) -> None:
        prev_playlist_len = self._model.song_count - new_song_count

        self.beginInsertRows(
            QModelIndex(),
            prev_playlist_len,
            self._model.song_count - 1,
        )
        self.endInsertRows()

    def _on_index_update(self, new_index):
        self.index_updated.emit(new_index)

    # --- Commands ---
    def add_song(self, files: Sequence[str]) -> None:
        """Command for adding new songs to the playlist.

        Args:
            files: A sequence of path-like objects.

        """
        self._model.add_song(files)

    def set_selected_index(self, index: int):
        """Command for setting currently selected playlist index.

        Args:
            index: The index of the selected item in the playlist widget.

        """
        self._model.set_selected_index(index)

    # --- Properties ---
    @property
    def playlist(self) -> list[AudioTrack]:
        """Expose the model's current playlist.

        Returns:
            list[AudioTrack]: The current playlist.

        """
        return self._model.playlist

    @property
    def selected_song(self):
        """Expose the model's currently selected song.

        Returns:
            AudioTrack | None: The selected song from the model,
                         or ``None`` if the playlist is empty, or nothing is selected.

        """
        return self._model.selected_song


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

    volume_changed = pyqtSignal(int)
    mute_changed = pyqtSignal(bool)

    def __init__(self, volume_model: VolumeModel, player_engine):
        super().__init__()
        self._player_engine = player_engine
        self._model = volume_model

        # Establish Model-ViewModel connection.
        self._model.volume_changed.connect(self._on_model_volume_changed)
        self._model.mute_changed.connect(self._on_model_mute_changed)

    def _on_model_volume_changed(self, new_volume: int) -> None:
        """Forward volume changes from the model to the view layer.

        Args:
            new_volume: The updated volume from the model.

        """
        self.volume_changed.emit(new_volume)  # type: ignore

    def _on_model_mute_changed(self, muted: bool) -> None:
        """Forward mute state changes from the model to the view layer.

        Args:
            muted: Updated mute state from the model.

        """
        self.mute_changed.emit(muted)  # type: ignore

    def refresh(self) -> None:
        """Re-emit the current volume to refresh any subscribed views.

        Useful when view needs initial state sync.
        """
        self.volume_changed.emit(self._model.current_volume)  # type: ignore

    # --- Commands ---
    def set_volume(self, new_volume) -> None:
        """Command for updating volume.

        Args:
            new_volume: The new volume value to set.

        """
        self._model.set_volume(new_volume)

    def set_mute(self, mute: bool) -> None:
        """Command for toggling mute state.

        Args:
              mute: The new mute state to set.

        """
        self._model.set_mute(mute)

    # --- Properties ---
    @property
    def current_volume(self) -> int:
        """Expose the model's current volume.

        Returns:
            int: The model's current volume.

        """
        return self._model.current_volume

    @property
    def is_muted(self) -> bool:
        """Expose the model's current mute state.

        Returns:
            bool: The model's current mute state.

        """
        return self._model.is_muted
