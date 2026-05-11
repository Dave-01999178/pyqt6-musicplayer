import logging

from PyQt6.QtCore import QModelIndex, Qt, pyqtSlot
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QVBoxLayout, QWidget

from pyqt6_music_player.core import (
    ADD_ICON,
    FILE_DIALOG_FILTER,
    LOAD_FOLDER_ICON,
    PLAYLIST_MANAGER_BTN_ICON_SIZE,
    PLAYLIST_MANAGER_BTN_SIZE,
    REMOVE_ICON,
)
from pyqt6_music_player.widgets import IconButton, PlaylistWidget

from .playlist_viewmodel import PlaylistViewModel

logger = logging.getLogger(__name__)


# --- Playlist manager ---
class PlaylistManagerPanel(QWidget):
    """QWidget container for grouping playlist-manager widgets.

    This container also acts as the main view layer for the playlist manager.
    """

    def __init__(self, playlist_viewmodel: PlaylistViewModel):
        """Initialize PlaylistManagerPanel and connect signals.

        Args:
            playlist_viewmodel: The playlist viewmodel.

        """
        super().__init__()
        # Viewmodel
        self._playlist_viewmodel = playlist_viewmodel

        # Widgets
        self._add_track_btn = IconButton(
            ADD_ICON,
            icon_size=PLAYLIST_MANAGER_BTN_ICON_SIZE,
            widget_size=PLAYLIST_MANAGER_BTN_SIZE,
            button_text="Add track(s)",
            object_name="addTrackBtn",
        )
        self._remove_track_btn = IconButton(
            REMOVE_ICON,
            icon_size=PLAYLIST_MANAGER_BTN_ICON_SIZE,
            widget_size=PLAYLIST_MANAGER_BTN_SIZE,
            button_text="Remove",
            object_name="removeTrackBtn",
        )
        self._load_folder_btn = IconButton(
            LOAD_FOLDER_ICON,
            icon_size=PLAYLIST_MANAGER_BTN_ICON_SIZE,
            widget_size=PLAYLIST_MANAGER_BTN_SIZE,
            button_text="Load folder",
            object_name="loadFolderBtn",
        )

        # Setup
        self._init_ui()
        self._connect_signals()

    # -- Protected/internal methods --
    def _init_ui(self) -> None:
        # Setup instance widgets and layout
        main_layout_horizontal = QHBoxLayout()

        # Left widget: Add track button
        main_layout_horizontal.addWidget(self._add_track_btn)

        # Middle widget: Remove track button
        main_layout_horizontal.addWidget(self._remove_track_btn)

        # Right widget: Load folder button
        main_layout_horizontal.addWidget(self._load_folder_btn)

        main_layout_horizontal.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter,
        )

        self.setLayout(main_layout_horizontal)

    def _connect_signals(self) -> None:
        # IconButton (add track) -> PlaylistManagerPanel
        self._add_track_btn.clicked.connect(self._on_add_track_button_clicked)

        # TODO: Implement remove track and load folder

    @pyqtSlot()
    def _on_add_track_button_clicked(self) -> None:
        file_paths, _ = QFileDialog.getOpenFileNames(
            parent=self,
            filter=FILE_DIALOG_FILTER,
        )

        # Do nothing if the file dialog is cancelled.
        if not file_paths:
            return

        # Add the selected audio files to the playlist
        logger.info("Adding audio files: %s", file_paths)

        self._playlist_viewmodel.add_tracks(file_paths)


# --- PLAYLIST ---
class PlaylistDisplayPanel(QWidget):
    """QWidget container for the main playlist widget.

    This container also acts as the main view layer for playlist widget.
    """

    def __init__(self, playlist_viewmodel: PlaylistViewModel):
        """Initialize PlaylistDisplayPanel and connect signals.

        Args:
            playlist_viewmodel: The playlist viewmodel.

        """
        super().__init__()
        # Viewmodel
        self._playlist_viewmodel = playlist_viewmodel

        # Widgets
        self._playlist_widget = PlaylistWidget()
        self._playlist_widget.setModel(self._playlist_viewmodel)

        self.selection_model = self._playlist_widget.selectionModel()

        # Setup
        self._init_ui()
        self._connect_signals()

    # -- Protected/internal methods --
    def _init_ui(self) -> None:
        # Setup instance widgets and layout
        instance_layout = QVBoxLayout()

        instance_layout.addWidget(self._playlist_widget)

        self.setLayout(instance_layout)

    def _connect_signals(self) -> None:
        # PlaylistDisplayPanel -> PlaylistViewModel
        self.selection_model.currentRowChanged.connect(self._on_row_selection_changed)

        # PlaylistViewModel -> PlaylistDisplayPanel
        self._playlist_viewmodel.playback_order_position_changed.connect(
            self._on_playback_order_position_changed,
        )
        self._playlist_viewmodel.display_order_changed.connect(
            self._on_display_order_changed,
        )

    @pyqtSlot(QModelIndex, QModelIndex)
    def _on_row_selection_changed(
            self,
            current_index: QModelIndex,
            _: QModelIndex,
    ) -> None:
        if not current_index.isValid():
            return

        # Store the index of selected row in playlist viewmodel
        self._playlist_viewmodel.set_selected_track_index(current_index.row())

    @pyqtSlot()
    def _on_display_order_changed(self) -> None:
        # Reset row selection when display order changes
        self.selection_model.clearSelection()

    @pyqtSlot(int)
    def _on_playback_order_position_changed(self, index_position: int) -> None:
        # Sync the active row to the position of active track
        self._playlist_widget.set_delegate_active_row(index_position)
