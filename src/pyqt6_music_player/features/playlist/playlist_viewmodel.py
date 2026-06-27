from collections.abc import Sequence
from typing import ClassVar

from PyQt6.QtCore import QAbstractTableModel, Qt, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

from pyqt6_music_player.core import (
    OrderChangedEvent,
    TrackRemovedEvent,
    TracksAddedEvent,
)
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
    active_track_position_changed = pyqtSignal(int)

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
        self._active_row: int | None = None
        self._selected_row: int | None = None

        # Setup
        self._connect_signals()

    # -- Public methods --
    def add_selected_tracks(self, paths: Sequence[str]) -> None:
        """Add tracks to the playlist.

        Args:
            paths: A sequence of file path strings.

        """
        self._playlist_service.add_tracks_from_paths(paths)

    def remove_selected_track(self) -> None:
        """Remove the selected track from playlist."""
        if not self._can_remove_selected_track():
            return

        self._playlist_service.remove_track_at_index(
            self._display_order[self._selected_row],
        )

        self._selected_row = None

    def sync_active_row(self) -> None:
        """Sync the playlist UI active row to the active track."""
        active_track_index = self._playlist_service.current_track_index

        self._update_active_row(self._display_order.index(active_track_index))

    def set_selected_row(self, index: int) -> None:
        """'selected_row' setter.

        Args:
            index: The index of the selected row in playlist UI.

        """
        self._selected_row = index

    def rowCount(self, parent=None):
        # Return the number of tracks in the playlist
        return self._playlist_service.track_count

    def columnCount(self, parent=None):
        # Return the number of columns (track metadata)
        return len(self.PLAYLIST_COLUMN)

    def data(self, index, role=...):
        # Provides cell data for display and alignment roles
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
        # Provides header label and alignment for horizontal headers
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
        self._playlist_service.tracks_added.connect(self._on_tracks_added)
        self._playlist_service.track_removed.connect(self._on_track_removed)
        self._playlist_service.shuffle_order_changed.connect(
            self._on_shuffle_order_changed,
        )

    def _on_tracks_added(self, state: TracksAddedEvent) -> None:
        # Update the display order
        self._update_display_order(state.order)

        self._update_active_row(state.position)

    def _on_track_removed(self, state: TrackRemovedEvent) -> None:
        # Update the display order
        self._update_display_order(state.order)

        self._update_active_row(state.position)

    def _on_shuffle_order_changed(self, result: OrderChangedEvent) -> None:
        # Update the display order
        self._update_display_order(result.order)

        # Ensure active track == active row after the display update
        self._update_active_row(result.position)

    def _update_display_order(self, display_order: list[int]) -> None:
        # Update the display order, and mode
        self.layoutAboutToBeChanged.emit()

        self._display_order = display_order

        self.layoutChanged.emit()

        # Reset selection after the display update
        self.display_order_changed.emit()

    def _update_active_row(self, position: int | None) -> None:
        # Sync playlist widget active row to the active track
        self._active_row = position

        # Translate None to -1 since the delegate uses -1 as its no-active-row sentinel
        self.active_track_position_changed.emit(-1 if position is None else position)

    def _can_remove_selected_track(self) -> bool:
        if not self._display_order:
            QMessageBox.warning(
                None,
                "Empty Playlist",
                "The playlist is empty. There are no tracks to remove.",
            )
            return False

        if self._selected_row is None:
            QMessageBox.warning(
                None,
                "No Track Selected",
                "Please select a track from the playlist to remove.",
            )
            return False

        return True
