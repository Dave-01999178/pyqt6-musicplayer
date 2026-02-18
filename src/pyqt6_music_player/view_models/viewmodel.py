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
)

from pyqt6_music_player.constants import PlaybackStatus
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
    track_loaded = pyqtSignal(str, str, int, str)  # Title, Album, Duration
    playback_started = pyqtSignal(int, str)  # Display duration, duration in ms
    playback_position_changed = pyqtSignal(int, str, str)
    initial_track_added = pyqtSignal()
    player_state_changed = pyqtSignal(PlaybackStatus)

    def __init__(
            self,
            playlist_service: PlaylistService,
            playback_service: PlaybackService,
    ):
        """Initialize viewmodel and connect to service signals.

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

    # --- Private methods ---
    def _connect_signals(self) -> None:
        """Establish signal–slot connections between the viewmodel and service."""
        # Playlist service signals
        self._playlist_service.tracks_added.connect(self._on_track_added)

        # Playback service signals
        self._playback_service.track_loaded.connect(self._on_track_loaded)
        self._playback_service.playback_position_changed.connect(
            self._on_playback_position_changed,
        )
        self._playback_service.player_state_changed.connect(self._on_player_state_changed)

    # --- Custom signal slots ---
    def _on_track_added(self, add_count: int, new_track_count: int) -> None:
        """Enable playback UI when the first track is added to an empty playlist.

        Args:
            add_count: Number of tracks just added.
            new_track_count: Total tracks in playlist after addition.

        """
        initial_track_add = (new_track_count - add_count == 0)
        if initial_track_add:
            self.initial_track_added.emit()

    def _on_track_loaded(self, current_track: Track) -> None:
        """Emit track metadata when a new track is loaded.

        Args:
            current_track: The newly loaded track.

        """
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
        """Convert and emit playback position in milliseconds and formatted strings.

        Args:
            elapsed_time: Seconds elapsed since playback start.
            time_remaining: Seconds remaining until track end.

        """
        # Elapsed time in ms (for smooth slider movement)
        elapsed_time_in_ms = int(elapsed_time * 1000)

        # Formatted playback position
        formatted_elapsed_time = format_duration(elapsed_time)
        formatted_time_remaining = format_duration(time_remaining)

        self.playback_position_changed.emit(
            elapsed_time_in_ms,
            formatted_elapsed_time,
            formatted_time_remaining,
        )

    def _on_player_state_changed(self, player_state: PlaybackStatus):
        self.player_state_changed.emit(player_state)

    # --- Public methods (Commands). ---
    def play_pause(self) -> None:
        """Command for starting, pausing, and resuming playback."""
        self._playback_service.play_pause()

    def next_track(self) -> None:
        """Command for playing next track."""
        self._playback_service.next_track()

    def previous_track(self) -> None:
        """Command for playing previous track."""
        self._playback_service.previous_track()


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

    # --- Private methods ---
    def _connect_signals(self) -> None:
        """Connect service signals."""
        self._playlist_service.tracks_added.connect(self._on_track_added)
        self._playlist_service.selection_index_changed.connect(
            self._on_selected_index_changed,
        )

    # --- QAbstractTableModel methods ---
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

    # --- Slots ---
    # TODO: Initial implementation (insertion order), replace later.
    def _on_track_added(self, add_count: int, new_track_count: int) -> None:
        """Playlist add track event signal handler.

        Displays the newly added tracks(s) in the playlist widget.

        Args:
            add_count: The number of added track(s).
            new_track_count: The new playlist track count.

        """
        start = new_track_count - add_count
        end = new_track_count - 1

        self.beginInsertRows(QModelIndex(), start, end)
        self.endInsertRows()

        logger.info("%s tracks(s) was added to the playlist.", add_count)

    def _on_selected_index_changed(self, new_index) -> None:
        """Model selected index update signal handler.

        Args:
            new_index: The updated index from model.

        """
        self.selected_index_changed.emit(new_index)  # type: ignore

    # --- Public methods (Commands) ---
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


# ================================================================================
# VOLUME VIEWMODEL
# ================================================================================
class VolumeViewModel(QObject):
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
