# TODO: Consider splitting this monolithic module into separate individual modules when it grows,
#  or became complex for easy navigation.
import logging
from typing import Sequence

from PyQt6.QtCore import (QAbstractTableModel, QModelIndex, QObject, Qt, pyqtSignal, pyqtSlot)

from pyqt6_music_player.models import (
    AudioData,
    AudioPlayerController,
    PlaylistModel,
    Song,
    VolumeModel
)


# ================================================================================
# PLAYBACK CONTROL VIEWMODEL
# ================================================================================
class PlaybackControlViewModel(QObject):
    playback_started = pyqtSignal(str, str)

    def __init__(self, playlist_model: PlaylistModel, player_engine: AudioPlayerController):
        super().__init__()
        self._player_engine = player_engine
        self._playlist = playlist_model

        self._current_song = None

        self._player_engine.playback_started.connect(self._on_playback_start)

    @pyqtSlot()
    def _on_playback_start(self):
        song_title = self._current_song.title
        song_album = self._current_song.album

        self.playback_started.emit(song_title, song_album)  # type: ignore

    # TODO: Separate loading from play/pause later for better Separation of Concerns (SoC).
    def _load_song(self, song: Song):
        if song == self._current_song:
            return

        file_path = song.path
        audio_data = AudioData.from_file(file_path)

        if audio_data is not None:
            logging.info("New song: %s successfully loaded", file_path)
            self._current_song = song

            return audio_data

        return None

    # --- Commands ---
    def play_pause(self, play: bool):
        if self._playlist.selected_song is None:
            return

        # Resume
        if play and self._player_engine.is_paused:
            self._player_engine.resume_playback()
        # Pause
        elif not play:
            self._player_engine.pause_playback()
        # Start playback
        else:
            selected_song = self._playlist.selected_song
            audio_data = self._load_song(selected_song)

            if audio_data is None:
                return

            self._player_engine.start_playback(audio_data)
            self._on_playback_start()

    def next_track(self):
        print("Next button has been clicked.")

    def previous_track(self):
        print("Previous button has been clicked.")

    def replay(self):
        print("Replay button has been clicked.")

    def repeat(self):
        print("Repeat button has been clicked.")

    def seek(self):
        pass


# ================================================================================
# PLAYLIST VIEWMODEL
# ================================================================================
class PlaylistViewModel(QAbstractTableModel):
    """
    Viewmodel responsible for exposing playlist-related data and commands
    to the View layer in an MVVM architecture.

    This class acts as an intermediary between the PlaylistModel and any
    UI components that display or modify the application's playlist state.

    It forwards model updates to the view via Qt signals and provides
    commands for modifying playlist model.
    """
    DEFAULT_COLUMNS = [
        ("title", "Title"),
        ("artist", "Artist"),
        ("album", "Album"),
        ("duration", "Duration")
    ]
    def __init__(self, playlist_model: PlaylistModel):
        super().__init__()
        self._model = playlist_model

        self._model.playlist_changed.connect(self._on_model_song_insert)

    # --- QAbstractTableModel interface - Required methods (overridden) ---
    def rowCount(self, parent=None):
        return len(self._model.playlist)

    def columnCount(self, parent=None):
        return len(self.DEFAULT_COLUMNS)

    def data(self, index, role=...):
        if not index.isValid():
            return

        row = index.row()
        col = index.column()
        song = self._model.playlist[row]
        field_name = self.DEFAULT_COLUMNS[col][0]

        if role == Qt.ItemDataRole.DisplayRole:
            if field_name == "duration":
                return self.format_duration(song.duration)
            return getattr(song, field_name)

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if field_name == "duration":
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter

        return None

    def headerData(self, section, orientation, role=...):
        field_title = self.DEFAULT_COLUMNS[section][1]
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return field_title

        elif role == Qt.ItemDataRole.TextAlignmentRole and field_title == "Duration":
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter

        return None

    @staticmethod
    def format_duration(seconds: int | float):
        """
        Returns audio duration in format (mm:ss) if it's less than hour else (hh:mm:ss).
        """
        int_total_duration = int(seconds)
        secs_in_hr = 3600
        secs_in_min = 60

        hours, remainder = divmod(int_total_duration, secs_in_hr)
        minutes, seconds = divmod(remainder, secs_in_min)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        return f"{minutes:02d}:{seconds:02d}"

    # TODO: Temporary logic, replace later.
    # Notify views if new song(s) are added.
    # Initial implementation (insertion order).
    def _on_model_song_insert(self, new_song_count: int) -> None:
        prev_playlist_len = self._model.song_count - new_song_count

        self.beginInsertRows(QModelIndex(), prev_playlist_len, self._model.song_count - 1)
        self.endInsertRows()

    # --- Commands ---
    def add_song(self, files: Sequence[str]) -> None:
        """
        Command for adding new songs to the playlist.

        Args:
            files: A sequence of path-like objects.
        """
        self._model.add_song(files)

    def set_selected_index(self, index: int):
        """
        Command for setting currently selected playlist index.

        Args:
            index: The index of the selected item in the playlist widget.
        """
        self._model.set_selected_index(index)

    # --- Properties ---
    @property
    def playlist(self) -> list[Song]:
        """
        Exposes the model's current playlist.

        Returns:
            list[Song]: The current playlist.
        """
        return self._model.playlist

    @property
    def selected_song(self):
        """
        Exposes the model's currently selected song.

        Returns:
            Song | None: The selected song from the model,
                         or ``None`` if the playlist is empty, or nothing is selected.
        """
        return self._model.selected_song


# ================================================================================
# VOLUME VIEWMODEL
# ================================================================================
class VolumeViewModel(QObject):
    """
    Viewmodel responsible for exposing volume-related data and commands
    to the View layer in an MVVM architecture.

    This class acts as an intermediary between the VolumeModel and any
    UI components that display or modify the application's volume state.

    It forwards model updates to the view via Qt signals and provides
    commands for modifying volume model.
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
        """
        Forward volume changes from the model to the view layer.

        Args:
            new_volume: The updated volume from the model.
        """
        self.volume_changed.emit(new_volume)  # type: ignore

    def _on_model_mute_changed(self, muted: bool) -> None:
        """
        Forward mute state changes from the model to the view layer.

        Args:
            muted: Updated mute state from the model.
        """
        self.mute_changed.emit(muted)  # type: ignore

    def refresh(self) -> None:
        """
        Re-emit the current volume to refresh any subscribed views.

        Useful when view needs initial state sync.
        """
        self.volume_changed.emit(self._model.current_volume)  # type: ignore

    # --- Commands ---
    def set_volume(self, new_volume) -> None:
        """
        Command for updating volume.

        Args:
            new_volume: The new volume value to set.
        """
        self._model.set_volume(new_volume)

    def set_mute(self, mute: bool) -> None:
        """
        Command for toggling mute state.

        Args:
              mute: The new mute state to set.
        """
        self._model.set_mute(mute)

    # --- Properties ---
    @property
    def current_volume(self) -> int:
        """
        Exposes the model's current volume.

        Returns:
            int: The model's current volume.
        """
        return self._model.current_volume

    @property
    def is_muted(self) -> bool:
        """
        Exposes the model's current mute state.

        Returns:
            bool: The model's current mute state.
        """
        return self._model.is_muted
