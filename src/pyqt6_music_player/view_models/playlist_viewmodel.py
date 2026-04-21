# TODO: Add module docstring
from collections.abc import Sequence
from typing import ClassVar

from PyQt6.QtCore import QAbstractTableModel, Qt, pyqtSignal

from pyqt6_music_player.core import OrderMode
from pyqt6_music_player.services import PlaylistService
from pyqt6_music_player.services.playback_order import ChangeOrderResult
from pyqt6_music_player.utils import format_duration


class PlaylistViewModel(QAbstractTableModel):
    """Expose playlist tracks as a table model for the playlist view."""

    PLAYLIST_COLUMN: ClassVar[tuple[tuple[str, str]]] = (
        ("title", "Title"),
        ("artist", "Artist"),
        ("album", "Album"),
        ("duration", "Duration"),
    )  # Column, Column name

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

        self._track_display_order: list[int] | None = []
        self._display_mode: OrderMode = OrderMode.SEQUENTIAL
        self._selected_index: int | None = None

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

    def remove_track(self) -> None:
        if self._selected_index is None:
            return  # TODO: Show dialog

        # self._playlist_service.remove_tracks(self._selected_index)

    def set_selection_index(self, index: int) -> None:
        self._selected_index = (
            self._track_display_order[index]
            if self._display_mode == OrderMode.SHUFFLED  # TODO: Implement later
            else index
        )

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
        col = self.PLAYLIST_COLUMN[index.column()][0]
        track_index = self._track_display_order[row]
        track = self._playlist_service.get_track_by_index(track_index)

        if role == Qt.ItemDataRole.DisplayRole:
            if col == "duration":
                return format_duration(track.duration)
            return getattr(track, col)

        if role == Qt.ItemDataRole.TextAlignmentRole and col == "duration":
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter

        return None

    def headerData(self, section, orientation, role=...):
        # Provides header label and alignment for horizontal headers.
        column_name = self.PLAYLIST_COLUMN[section][1]
        is_column_field = (
                role == Qt.ItemDataRole.DisplayRole
                and orientation == Qt.Orientation.Horizontal
        )
        is_duration_column = (
                role == Qt.ItemDataRole.TextAlignmentRole
                and column_name == "Duration"
        )

        if is_column_field:
            return column_name

        if is_duration_column:
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter

        return None

    # -- Protected/Internal methods --
    def _connect_signals(self):
        self._playlist_service.playback_order_changed.connect(
            self._on_playback_order_changed,
        )
        self._playlist_service.playback_order_position_changed.connect(
            self._on_playback_order_position_changed,
        )

    def _on_playback_order_changed(self, result: ChangeOrderResult) -> None:
        self.layoutAboutToBeChanged.emit()

        self._track_display_order = result.new_order
        self._display_mode = result.order_mode

        self.layoutChanged.emit()

        self.display_order_changed.emit()  # Reset any selection

    def _on_playback_order_position_changed(self, position: int) -> None:
        # Sync active row
        self.playback_order_position_changed.emit(position)
