import logging
from collections.abc import Sequence
from typing import ClassVar

from PyQt6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QObject,
    Qt,
    pyqtSignal,
)

from pyqt6_music_player.core import PlaybackStatus
from pyqt6_music_player.models import Track, VolumeModel
from pyqt6_music_player.services import PlaybackService, PlaylistService

logger = logging.getLogger(__name__)


# ================================================================================
# HELPERS
# ================================================================================
def format_duration(duration: int | float) -> str:
    """Convert seconds to (HH:MM:SS) format string.

    Args:
        duration: Duration in seconds.

    Returns:
        Formatted time string in HH:MM:SS format (e.g., "01:23:45").

    """
    duration = int(duration)
    secs_in_hr = 3600
    secs_in_min = 60

    hours, remainder = divmod(duration, secs_in_hr)
    minutes, seconds = divmod(remainder, secs_in_min)


    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


# ================================================================================
# PLAYBACK VIEWMODEL
# ================================================================================
#
# noinspection PyUnresolvedReferences
class PlaybackViewModel(QObject):
    track_loaded = pyqtSignal(str, str, int, str)
    playback_position_changed = pyqtSignal(int, str, str)
    initial_track_added = pyqtSignal()
    player_state_changed = pyqtSignal(PlaybackStatus)

    def __init__(
            self,
            playlist_service: PlaylistService,
            playback_service: PlaybackService,
    ):
        """Initialize PlaybackViewModel.

        Args:
            playlist_service: Service managing playlist state and operations.
            playback_service: Service managing track loading and audio playback.
        """
        super().__init__()
        # Service
        self._playlist_service = playlist_service
        self._playback_service = playback_service

        # Setup
        self._connect_signals()

    # --- Public methods (Commands). ---
    def toggle_playback(self) -> None:
        """Command for toggling playback state, used by play-pause button."""
        self._playback_service.toggle_playback()

    def play(self):
        """Command for starting playback."""
        self._playback_service.play()

    def pause(self):
        """Command for pausing playback"""
        self._playback_service.pause()

    def resume(self):
        """Command for resuming paused playback."""
        self._playback_service.resume()

    def next_track(self) -> None:
        """Command for playing next track."""
        self._playback_service.play_next_track()

    def previous_track(self) -> None:
        """Command for playing previous track."""
        self._playback_service.play_previous_track()

    def seek(self, new_position_in_ms: int) -> None:
        """Command for setting the playback position."""
        self._playback_service.seek(new_position_in_ms)

    def get_playback_status(self) -> PlaybackStatus:
        """Returns the current playback status."""
        return self._playback_service.get_playback_status()

    # --- Protected/internal methods ---
    def _connect_signals(self) -> None:
        # Wire service signals to PlaybackViewModel slots.
        #
        # PlaylistService -> PlaybackViewModel
        self._playlist_service.tracks_added.connect(self._on_track_added)

        # PlaybackService -> PlaybackViewModel
        self._playback_service.track_loaded.connect(self._on_track_loaded)
        self._playback_service.playback_position_changed.connect(
            self._on_playback_position_changed,
        )
        self._playback_service.player_state_changed.connect(
            self._on_player_state_changed,
        )

    def _on_track_added(self, add_count: int, new_track_count: int) -> None:
        # Emit `initial_track_added` signal on first insert
        initial_track_add = (new_track_count - add_count == 0)
        if initial_track_add:
            self.initial_track_added.emit()

    def _on_track_loaded(self, current_track: Track) -> None:
        # Emit track duration in milliseconds and formatted strings
        track_duration_in_ms = int(current_track.duration * 1000)
        formatted_duration = format_duration(int(current_track.duration))

        self.track_loaded.emit(
            current_track.title,
            current_track.album,
            track_duration_in_ms,
            formatted_duration
        )

    def _on_playback_position_changed(
            self,
            elapsed_time: float,
            time_remaining: float,
    ) -> None:
        # Convert and emit playback position in milliseconds and formatted strings
        elapsed_time_in_ms = int(elapsed_time * 1000)
        formatted_elapsed_time = format_duration(elapsed_time)
        formatted_time_remaining = format_duration(time_remaining)

        self.playback_position_changed.emit(
            elapsed_time_in_ms,
            formatted_elapsed_time,
            formatted_time_remaining,
        )

    def _on_player_state_changed(self, player_state: PlaybackStatus):
        # Forward playback status changes
        self.player_state_changed.emit(player_state)


# ================================================================================
# PLAYLIST VIEWMODEL
# ================================================================================
class PlaylistViewModel(QAbstractTableModel):
    DEFAULT_COLUMNS: ClassVar[tuple[tuple[str, str]]] = (
        ("title", "Title"),
        ("artist", "Artist"),
        ("album", "Album"),
        ("duration", "Duration"),
    )  # Field_name, Field_label

    selected_index_changed = pyqtSignal(int)

    def __init__(self, playlist_service: PlaylistService):
        """Initialize viewmodel and connect to service signals.

        Args:
            playlist_service: Service managing playlist state and operations.

        """
        super().__init__()
        # Service
        self._playlist_service = playlist_service

        # Setup
        self._connect_signals()

    # --- Public methods ---
    #
    # Commands
    def add_tracks(self, paths: Sequence[str]) -> None:
        """Command for adding tracks to the playlist.

        Args:
            paths: A sequence of path-like objects.

        """
        self._playlist_service.add_tracks(paths)

    def set_selected_index(self, index: int) -> None:
        """Model selected index setter.

        Args:
            index: The selected row index in playlist.

        """
        self._playlist_service.set_selected_index(index)

    # QAbstractTableModel
    def rowCount(self, parent=None):
        """Set the number of row based on the number of tracks in playlist."""
        return self._playlist_service.get_track_count()

    def columnCount(self, parent=None):
        """Set the number of column based on the number of track metadata."""
        return len(self.DEFAULT_COLUMNS)

    def data(self, index, role=...):
        """Render body row data."""
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()
        track = self._playlist_service.get_track_by_index(row)
        field_name = self.DEFAULT_COLUMNS[col][0]

        if role == Qt.ItemDataRole.DisplayRole:
            if field_name == "duration":
                return format_duration(track.duration)
            return getattr(track, field_name)

        if role == Qt.ItemDataRole.TextAlignmentRole and field_name == "duration":
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter

        return None

    def headerData(self, section, orientation, role=...):
        """Render header row data."""
        field_label = self.DEFAULT_COLUMNS[section][1]
        is_header_field = (
                role == Qt.ItemDataRole.DisplayRole
                and orientation == Qt.Orientation.Horizontal
        )
        is_duration_header = (
                role == Qt.ItemDataRole.TextAlignmentRole
                and field_label == "Duration"
        )

        if is_header_field:
            return field_label

        if is_duration_header:
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter

        return None

    # --- Protected/internal methods ---
    def _connect_signals(self) -> None:
        # Wire PlaylistService signals to PlaylistViewModel slots.
        self._playlist_service.tracks_added.connect(self._on_track_added)
        self._playlist_service.selection_index_changed.connect(
            self._on_selected_index_changed,
        )

    # TODO: Initial implementation (insertion order), replace later.
    def _on_track_added(self, add_count: int, new_track_count: int) -> None:
        # Displays the newly added tracks(s) in the playlist widget.
        start = new_track_count - add_count
        end = new_track_count - 1

        self.beginInsertRows(QModelIndex(), start, end)
        self.endInsertRows()

    def _on_selected_index_changed(self, new_index) -> None:
        # Forward the new selection index
        self.selected_index_changed.emit(new_index)  # type: ignore


# ================================================================================
# VOLUME VIEWMODEL
# ================================================================================
class VolumeViewModel(QObject):
    model_volume_changed = pyqtSignal(int)
    model_mute_state_changed = pyqtSignal(bool)

    def __init__(self, volume_model: VolumeModel, player_engine):
        """Initialize VolumeViewModel."""
        super().__init__()
        self._player_engine = player_engine
        self._model = volume_model

        # Establish Model-ViewModel connection.
        self._connect_signals()

    # --- Public methods ---
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

    # --- Protected/internal methods ---
    def _connect_signals(self):
        self._model.volume_changed.connect(self._on_model_volume_changed)
        self._model.mute_changed.connect(self._on_model_mute_changed)

    def _on_model_volume_changed(self, new_volume: int) -> None:
        self.model_volume_changed.emit(new_volume)  # type: ignore

    def _on_model_mute_changed(self, muted: bool) -> None:
        self.model_mute_state_changed.emit(muted)  # type: ignore

    def refresh(self) -> None:
        """Re-emit the current volume to refresh any subscribed views.

        Useful when view needs initial state sync.
        """
        self.model_volume_changed.emit(self._model.current_volume)  # type: ignore
