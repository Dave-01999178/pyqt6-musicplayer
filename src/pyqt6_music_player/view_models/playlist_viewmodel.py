# TODO: Add module docstring
from collections.abc import Sequence
from typing import ClassVar

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, pyqtSignal

from pyqt6_music_player.services import PlaylistService
from pyqt6_music_player.utils import format_duration


class PlaylistViewModel(QAbstractTableModel):
    """Expose playlist tracks as a table model for the playlist view."""

    playlist_model_position_changed = pyqtSignal(int)
    playlist_display_order_changed = pyqtSignal(int)
    DEFAULT_COLUMNS: ClassVar[tuple[tuple[str, str]]] = (
        ("title", "Title"),
        ("artist", "Artist"),
        ("album", "Album"),
        ("duration", "Duration"),
    )  # Field_name, Field_label

    def __init__(self, playlist_service: PlaylistService):
        """Initialize PlaylistViewModel and connect to PlaylistService signals.

        Args:
            playlist_service: Service managing playlist state and operations.

        """
        super().__init__()
        # Service
        self._playlist_service = playlist_service

        self._track_display_order: list[int] | None = []
        self._is_shuffled_display: bool = False
        self._track_index: int | None = None
        self._active_row: int | None = None


        # Setup
        self._connect_signals()

    # -- Public methods --
    #
    # Instance methods
    def add_tracks(self, paths: Sequence[str]) -> None:
        """Add tracks to the playlist.

        Args:
            paths: A sequence of path-like objects.

        """
        self._playlist_service.add_tracks(paths)

    def sync_playlist_model_position(self, index: int) -> None:
        index = (
            self._track_display_order[index]
            if self._track_display_order
            else index
        )

        self._playlist_service.sync_playlist_model_position(index)

    def update_display_order(self, playback_order: list[int]) -> None:
        self.layoutAboutToBeChanged.emit()

        self._track_display_order = playback_order

        self.layoutChanged.emit()

        self._is_shuffled_display = any(
            a > b
            for a, b in zip(playback_order, playback_order[1:])
        )

        self._sync_active_row()

    # QAbstractTableModel methods
    def rowCount(self, parent=None):
        # Returns the number of tracks in the playlist.
        return self._playlist_service.track_count

    def columnCount(self, parent=None):
        # Returns the number of track metadata columns.
        return len(self.DEFAULT_COLUMNS)

    def data(self, index, role=...):
        # Provides cell data for display and alignment roles.
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        track_index = (
            self._track_display_order[row]
            if self._track_display_order
            else row
        )

        track = self._playlist_service.get_track_by_index(track_index)
        field_name = self.DEFAULT_COLUMNS[col][0]

        if role == Qt.ItemDataRole.DisplayRole:
            if field_name == "duration":
                return format_duration(track.duration)
            return getattr(track, field_name)

        if role == Qt.ItemDataRole.TextAlignmentRole and field_name == "duration":
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter

        return None

    def headerData(self, section, orientation, role=...):
        # Provides header label and alignment for horizontal headers.
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

    # -- Protected/internal methods --
    def _connect_signals(self) -> None:
        # Wire PlaylistService signals to PlaylistViewModel slots.
        self._playlist_service.playlist_changed.connect(self._on_playlist_changed)
        self._playlist_service.playlist_model_position_changed.connect(
            self._on_playlist_model_position_changed,
        )

    def _sync_active_row(self) -> None:
        # Active row sync guide
        #
        # [0, 1, 2, 3, 4]  # Original playback order from playlist model
        # [3, 0, 1, 4, 2]  # Shuffled playback order from track navigator
        # [0, 1, 2, 3, 4]  # Row index
        self._active_row = (
            0
            if self._is_shuffled_display
            else self._track_index
        )

        self.playlist_display_order_changed.emit(self._active_row)

    def _on_playlist_changed(self) -> None:
        track_count = self._playlist_service.track_count
        first_row = 0
        last_row = track_count - 1

        self._track_display_order = list(range(track_count))

        self.beginInsertRows(QModelIndex(), first_row, last_row)
        self.endInsertRows()

    def _on_playlist_model_position_changed(self, index) -> None:
        # - SYNC PLAYLIST WIDGET ACTIVE ROW POSITION -
        #
        # Use the new index position from model for syncing playlist widget
        # (playlist model index == playlist widget row index) when not shuffled
        if not self._is_shuffled_display:
            self._track_index = index

            self.playlist_model_position_changed.emit(index)

            return

        # TODO: Initial logic/implementation, recheck later.
        # Convert the current track index from shuffled playback order back to its
        # original position in playlist model (playlist model index == row index)
        #
        # Example:
        # [0, 1, 2, 3, 4]  # Original playback order from playlist model
        # [3, 0, 1, 4, 2]  # Shuffled playback order from track navigator
        # [0, 1, 2, 3, 4]  # Row index
        if not (0 <= self._active_row < len(self._track_display_order)):
            return

        next_row_idx = (self._active_row + 1) % len(self._track_display_order)
        prev_row_idx = (self._active_row - 1) % len(self._track_display_order)
        if self._track_display_order[next_row_idx] == index:
            self._active_row = next_row_idx

        elif self._track_display_order[prev_row_idx] == index:
            self._active_row = prev_row_idx

        self._track_index = index

        self.playlist_model_position_changed.emit(self._active_row)
