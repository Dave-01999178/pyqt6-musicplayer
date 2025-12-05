# TODO: Consider splitting this monolithic module into separate individual modules when it grows,
#  or became complex for easy navigation.
from typing import Sequence

from PyQt6.QtCore import pyqtSignal, QObject, QAbstractTableModel, Qt, QModelIndex

from pyqt6_music_player.models import PlaylistModel, Song, VolumeModel
from pyqt6_music_player.models.player_engine import PlayerEngine


# ================================================================================
# PLAYBACK CONTROL VIEWMODEL
# ================================================================================
class PlaybackControlViewModel(QObject):
    def __init__(self, playlist_model: PlaylistModel, player_engine: PlayerEngine):
        super().__init__()
        self._player_engine = player_engine
        self._model = playlist_model

    def play_selected(self):
        print("Play button has been clicked.")

    def next_track(self):
        print("Next button has been clicked.")

    def previous_track(self):
        print("Previous button has been clicked.")

    def replay(self):
        print("Replay button has been clicked.")

    def repeat(self):
        print("Repeat button has been clicked.")

    # Properties
    @property
    def playlist(self):
        return self._model.playlist


# ================================================================================
# PLAYLIST VIEWMODEL
# ================================================================================
class PlaylistViewModel(QAbstractTableModel):
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
        if new_song_count != 0:
            prev_playlist_len = self._model.song_count - new_song_count
            self.beginInsertRows(QModelIndex(), prev_playlist_len, self._model.song_count - 1)
            self.endInsertRows()

        return None

    # --- Commands ---
    def add_song(self, files: Sequence[str]) -> None:
        self._model.add_song(files)

    def set_selected_index(self, index: int):
        self._model.set_selected_index(index)

    # --- Properties ---
    @property
    def playlist(self) -> list[Song]:
        return self._model.playlist

    @property
    def selected_song(self):
        return self._model.selected_song


# ================================================================================
# VOLUME VIEWMODEL
# ================================================================================
class VolumeViewModel(QObject):
    volume_changed = pyqtSignal(int)
    mute_changed = pyqtSignal(bool)

    def __init__(self, volume_model: VolumeModel, player_engine):
        super().__init__()
        self._player_engine = player_engine
        self._model = volume_model

        # Establish Model-ViewModel connection.
        self._model.volume_changed.connect(self._on_model_volume_changed)
        self._model.mute_changed.connect(self._on_model_mute_changed)

    def _on_model_volume_changed(self, new_volume: int):
        self.volume_changed.emit(new_volume)  # type: ignore

    def _on_model_mute_changed(self, muted: bool):
        self.mute_changed.emit(muted)  # type: ignore

    def refresh(self):
        self.volume_changed.emit(self._model.current_volume)  # type: ignore

    # --- Commands ---
    def set_volume(self, new_volume):
        self._model.set_volume(new_volume)

    def set_mute(self, mute: bool):
        self._model.set_mute(mute)

    # --- Properties ---
    @property
    def current_volume(self) -> int:
        return self._model.current_volume

    @property
    def is_muted(self) -> bool:
        return self._model.is_muted
