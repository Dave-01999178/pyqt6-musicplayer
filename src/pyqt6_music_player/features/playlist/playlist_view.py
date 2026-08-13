import logging

from PyQt6.QtCore import QModelIndex, Qt, pyqtSlot
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QVBoxLayout, QWidget

from pyqt6_music_player.core import ASSETS_PATH, FILE_DIALOG_FILTER, IconButton

from .playlist_viewmodel import PlaylistViewModel
from .playlist_widgets import PlaylistWidget

# ==================== CONSTANTS ====================
ADD_ICON = ASSETS_PATH / "add_icon.svg"
REMOVE_ICON = ASSETS_PATH / "remove_icon.svg"
LOAD_FOLDER_ICON = ASSETS_PATH / "load_folder_icon.svg"
PLAYLIST_MANAGER_BTN_SIZE = (120, 40)
PLAYLIST_MANAGER_BTN_ICON_SIZE = (20, 20)

logger = logging.getLogger(__name__)


# ==================== CLASSES ====================
class PlaylistManagerPanel(QWidget):
    """QWidget container for grouping playlist-manager widgets.

    This container also acts as the main view layer for the playlist manager.
    """

    def __init__(self, playlist_viewmodel: PlaylistViewModel):
        super().__init__()
        # VIEWMODEL
        self._playlist_viewmodel = playlist_viewmodel

        # WIDGETS
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

        # SETUP
        self._init_ui()
        self._connect_signals()

    # -- Protected methods --
    def _init_ui(self) -> None:
        layout = QHBoxLayout()

        layout.addWidget(self._add_track_btn)
        layout.addWidget(self._remove_track_btn)
        layout.addWidget(self._load_folder_btn)

        layout.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter,
        )

        self.setLayout(layout)

    def _connect_signals(self) -> None:
        # PlaylistManagerPanel widgets -> PlaylistViewModel
        self._add_track_btn.clicked.connect(self._on_add_track_button_clicked)
        self._remove_track_btn.clicked.connect(self._on_remove_track_button_clicked)

    @pyqtSlot()
    def _on_add_track_button_clicked(self) -> None:
        # Open QFileDialog
        file_paths, _ = QFileDialog.getOpenFileNames(
            parent=self,
            filter=FILE_DIALOG_FILTER,
        )

        # QFileDialog was closed or cancelled.
        if not file_paths:
            return

        logger.info("Adding %d selected file(s) to the playlist", len(file_paths))
        logger.debug("Selected file(s): %s", file_paths)

        self._playlist_viewmodel.add_tracks(file_paths)

    @pyqtSlot()
    def _on_remove_track_button_clicked(self) -> None:
        self._playlist_viewmodel.remove_selected_track()


class PlaylistDisplayPanel(QWidget):
    """QWidget container for the main playlist widget.

    This container also acts as the main view layer for playlist widget.
    """

    def __init__(self, playlist_viewmodel: PlaylistViewModel):
        super().__init__()
        # VIEWMODEL
        self._playlist_viewmodel = playlist_viewmodel

        # WIDGETS
        self._playlist_widget = PlaylistWidget()
        self._playlist_widget.setModel(self._playlist_viewmodel)

        # Retrieve the selection model to track and manage selected row
        self.selection_model = self._playlist_widget.selectionModel()

        # SETUP
        self._init_ui()
        self._connect_signals()

    # -- Protected methods --
    def _init_ui(self) -> None:
        panel_layout = QVBoxLayout()

        panel_layout.addWidget(self._playlist_widget)

        self.setLayout(panel_layout)

    def _connect_signals(self) -> None:
        # PlaylistDisplayPanel -> PlaylistViewModel
        self.selection_model.currentRowChanged.connect(self._on_row_selection_changed)

        # PlaylistViewModel -> PlaylistDisplayPanel
        self._playlist_viewmodel.active_row_index_changed.connect(
            self._on_active_row_index_changed,
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

        self._playlist_viewmodel.set_selected_row_index(current_index.row())

    @pyqtSlot()
    def _on_display_order_changed(self) -> None:
        # Reset row selection when display order changes
        self.selection_model.clearSelection()
        self.selection_model.clearCurrentIndex()

    @pyqtSlot(int)
    def _on_active_row_index_changed(self, index_position: int) -> None:
        self._playlist_widget.set_active_row(index_position)
