# TODO: Add module docstring
from collections.abc import Sequence
from typing import ClassVar

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, pyqtSignal

from pyqt6_music_player.services import PlaylistService
from pyqt6_music_player.utils import format_duration


class PlaylistViewModel(QAbstractTableModel):
    """Expose playlist tracks as a table model for the playlist view."""

    selected_index_changed = pyqtSignal(int)
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

    def set_selected_row(self, index: int) -> None:
        """Store the row index from playlist.

        Args:
            index: The selected row index in playlist.

        """
        self._playlist_service.set_selected_row(index)

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
        self._playlist_service.tracks_added.connect(self._on_track_added)
        self._playlist_service.selection_index_changed.connect(
            self._on_selected_index_changed,
        )

    # TODO: Initial implementation (insertion order), replace later.
    def _on_track_added(self, new_track_idx: list[int]) -> None:
        # Displays the newly added tracks(s) in the playlist widget.
        start, end = new_track_idx[0], new_track_idx[-1]

        self.beginInsertRows(QModelIndex(), start, end)
        self.endInsertRows()

    def _on_selected_index_changed(self, new_index) -> None:
        self.selected_index_changed.emit(new_index)  # type: ignore
