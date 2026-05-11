# TODO: Add module docstring
from collections.abc import Sequence
from typing import ClassVar

from PyQt6.QtCore import QAbstractTableModel, Qt, pyqtSignal

from pyqt6_music_player.core import OrderMode
from pyqt6_music_player.features.playback import PlaybackOrderState
from pyqt6_music_player.utils import format_duration

from .playlist_service import PlaylistService


class PlaylistViewModel(QAbstractTableModel):
    """Expose playlist tracks as a table model for the playlist view."""

    PLAYLIST_COLUMN: ClassVar[tuple[tuple[str, str]]] = (
        ("title", "Title"),
        ("artist", "Artist"),
        ("album", "Album"),
        ("duration", "Duration"),
    )  # Column name, Actual column

    display_order_changed = pyqtSignal()
    playback_order_position_changed = pyqtSignal(int)

    def __init__(self, playlist_service: PlaylistService):
        """Initialize PlaylistViewModel and connect to PlaylistService signals.

        Args:
            playlist_service: Service managing playlist state and operations.

        """
        super().__init__()
        # Service
        self._playlist_service = playlist_service

        # Playlist UI state
        self._display_order: list[int] | None = []
        self._display_mode: OrderMode = OrderMode.SEQUENTIAL
        self._active_row: int | None = None
        self._selected_row: int | None = None

        # Setup
        self._connect_signals()

    # -- Public methods --
    #
    # Instance methods
    def add_tracks(self, paths: Sequence[str]) -> None:
        """Add tracks to the playlist.

        Args:
            paths: A sequence of file path strings.

        """
        self._playlist_service.add_tracks_from_paths(paths)

    def set_active_row(self, index: int) -> None:
        self._on_playback_order_position_changed(index)

    def set_selected_track_index(self, index: int) -> None:
        """Map a display row to its playlist index and store it.

        Args:
            index: The selected row in playlist widget.

        """
        self._selected_row = (
            self._display_order[index]
            if self._display_mode == OrderMode.SHUFFLED
            else index
        )

        # Only forward to PlaybackOrder if no track is actively playing.
        # Once playback starts, position is owned by the playback domain.
        if self._active_row is None:
            self._playlist_service.set_position(index)

    # QAbstractTableModel methods
    def rowCount(self, parent=None):
        # Return the number of tracks in the playlist.
        return self._playlist_service.track_count

    def columnCount(self, parent=None):
        # Return the number of columns (track metadata).
        return len(self.PLAYLIST_COLUMN)

    def data(self, index, role=...):
        # Provides cell data for display and alignment roles.
        if not index.isValid():
            return None

        row = index.row()
        column_name = self.PLAYLIST_COLUMN[index.column()][0]
        track_index = self._display_order[row]

        if role == Qt.ItemDataRole.DisplayRole:
            track = self._playlist_service.get_track_by_index(track_index)
            if column_name == "duration":
                return format_duration(track.duration)
            return getattr(track, column_name)

        if role == Qt.ItemDataRole.TextAlignmentRole and column_name == "duration":
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter

        return None

    def headerData(self, section, orientation, role=...):
        # Provides header label and alignment for horizontal headers.
        column = self.PLAYLIST_COLUMN[section][1]
        is_column_field = (
                role == Qt.ItemDataRole.DisplayRole
                and orientation == Qt.Orientation.Horizontal
        )
        is_duration_column = (
                role == Qt.ItemDataRole.TextAlignmentRole
                and column == "Duration"
        )

        if is_column_field:
            return column

        if is_duration_column:
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter

        return None

    # -- Protected/Internal methods --
    def _connect_signals(self) -> None:
        # PlaylistService -> PlaylistViewModel
        self._playlist_service.playback_order_changed.connect(
            self._on_playback_order_changed,
        )

    def _on_playback_order_changed(self, result: PlaybackOrderState) -> None:
        # Update the display order
        self.layoutAboutToBeChanged.emit()

        self._display_order = result.order
        self._display_mode = result.mode

        self.layoutChanged.emit()

        # Reset selection after the display update
        self.display_order_changed.emit()

        # Ensure active track == active row after the display update
        if self._active_row != result.position:
            self._on_playback_order_position_changed(result.position)

    def _on_playback_order_position_changed(self, position: int) -> None:
        # Sync playlist widget active row to the active track
        self._active_row = position

        self.playback_order_position_changed.emit(position)
