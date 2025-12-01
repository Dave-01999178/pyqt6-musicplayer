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
    def __init__(self, playlist_model: PlaylistModel):
        super().__init__()
        self._model = playlist_model
        self.header_label = Song.get_metadata_fields()

        self._model.playlist_changed.connect(self.on_song_insert)

    # --- QAbstractTableModel interface - Required methods (overridden) ---
    def rowCount(self, parent=None):
        return len(self._model.playlist)

    def columnCount(self, parent=None):
        return len(self.header_label)

    def data(self, index, role=...):
        if not index.isValid():
            return

        song = self._model.playlist[index.row()]
        col = index.column()
        field_name = self.header_label[col]

        if role == Qt.ItemDataRole.DisplayRole:
            if field_name == "duration":
                return song.formatted_duration()
            return getattr(song, field_name)

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if field_name == "duration":
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter

        return None

    def headerData(self, section, orientation, role=...):
        field_name = self.header_label[section]

        if  role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return field_name.title()

        elif role == Qt.ItemDataRole.TextAlignmentRole and field_name == "duration":
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter

        return None

    # TODO: Temporary logic, replace later.
    # Notify views if new song(s) are added.
    # Initial implementation (insertion order).
    def on_song_insert(self, song_count: int) -> None:
        if song_count != 0:
            prev_playlist_len = self._model.song_count - song_count
            self.beginInsertRows(QModelIndex(), prev_playlist_len, self._model.song_count - 1)
            self.endInsertRows()

        return None

    # --- Commands - Methods that VIEWS call to modify data ---
    def add_song(self, files: Sequence[str]) -> None:
        self._model.add_song(files)

    # --- Properties - Expose model properties if needed by views ---
    @property
    def playlist(self) -> list[Song]:
        return self._model.playlist


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

    # --- Commands - Methods that VIEWS call to modify data ---
    def set_volume(self, new_volume):
        self._model.set_volume(new_volume)

    def set_mute(self, mute: bool):
        self._model.set_mute(mute)

    # --- Properties - Expose model properties if needed by views ---
    @property
    def current_volume(self) -> int:
        return self._model.current_volume

    @property
    def is_muted(self) -> bool:
        return self._model.is_muted
