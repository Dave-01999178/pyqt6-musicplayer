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


# ==================== PANELS ====================
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
        #
        # PANEL LAYOUT: Horizontal box
        panel_layout = QHBoxLayout()

        # LEFT WIDGET: Add track button
        panel_layout.addWidget(self._add_track_btn)

        # MIDDLE WIDGET: Remove track button
        panel_layout.addWidget(self._remove_track_btn)

        # RIGHT WIDGET: Load folder button
        panel_layout.addWidget(self._load_folder_btn)

        panel_layout.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter,
        )

        self.setLayout(panel_layout)

    def _connect_signals(self) -> None:
        # PlaylistManagerPanel widgets -> PlaylistViewModel
        self._add_track_btn.clicked.connect(self._on_add_track_button_clicked)
        self._remove_track_btn.clicked.connect(self._on_remove_track_button_clicked)

        # TODO: Implement load folder

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

        self._playlist_viewmodel.add_selected_tracks(file_paths)

    @pyqtSlot()
    def _on_remove_track_button_clicked(self) -> None:
        self._playlist_viewmodel.remove_selected_track()


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
        #
        # PANEL LAYOUT: Vertical box
        panel_layout = QVBoxLayout()

        # WIDGET: Playlist table (QTableView)
        panel_layout.addWidget(self._playlist_widget)

        self.setLayout(panel_layout)

    def _connect_signals(self) -> None:
        # PlaylistDisplayPanel -> PlaylistViewModel
        self.selection_model.currentRowChanged.connect(self._on_row_selection_changed)

        # PlaylistViewModel -> PlaylistDisplayPanel
        self._playlist_viewmodel.active_track_position_changed.connect(
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
        self._playlist_viewmodel.set_selected_row(current_index.row())

    @pyqtSlot()
    def _on_display_order_changed(self) -> None:
        # Reset row selection when display order changes
        self.selection_model.clearSelection()
        self.selection_model.clearCurrentIndex()

    @pyqtSlot(int)
    def _on_playback_order_position_changed(self, index_position: int) -> None:
        # Sync the active row to the position of active track
        self._playlist_widget.set_delegate_active_row(index_position)
