"""Playlist UI components.

This module defines widgets responsible for displaying and managing playlist,
including add, remove and load song button; and a playlist table.
"""
from PyQt6.QtCore import QModelIndex, Qt, pyqtSlot
from PyQt6.QtGui import QBrush, QColor, QPalette
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableView,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from pyqt6_music_player.config import (
    ADD_ICON_PATH,
    LOAD_FOLDER_ICON_PATH,
    HORIZONTAL_MEDIUM_BUTTON,
    REMOVE_ICON_PATH,
)
from pyqt6_music_player.constants import FILE_DIALOG_FILTER
from pyqt6_music_player.view_models import PlaylistViewModel
from pyqt6_music_player.views import IconButtonFactory

# ================================================================================
# PLAYLIST MANAGER
# ================================================================================
#
# --- WIDGETS ---
AddSongButton = IconButtonFactory(
    ADD_ICON_PATH,
    widget_size=HORIZONTAL_MEDIUM_BUTTON,
    button_text="Add song(s)",
    object_name="addSongBtn",
)
RemoveSongButton = IconButtonFactory(
    REMOVE_ICON_PATH,
    widget_size=HORIZONTAL_MEDIUM_BUTTON,
    button_text="Remove",
    object_name="removeSongBtn",
)
LoadSongFolderButton = IconButtonFactory(
    LOAD_FOLDER_ICON_PATH,
    widget_size=HORIZONTAL_MEDIUM_BUTTON,
    button_text="Load folder",
    object_name="loadFolderBtn",
)


# --- COMPONENT ---
class PlaylistManager(QWidget):
    """A QWidget container for grouping playlist manager widgets.

    This container also acts as the main view layer for the playlist manager,
    and is responsible for:
     - Grouping and displaying playlist manager buttons.
     - Handling playlist manager events by calling the appropriate viewmodel commands
       (View -> ViewModel).
    """

    def __init__(self, playlist_viewmodel: PlaylistViewModel):
        """Initialize PlaylistManager.

        Args:
            playlist_viewmodel: The playlist viewmodel.

        """
        super().__init__()
        # Playlist viewmodel
        self._viewmodel = playlist_viewmodel

        # Playlist manager widgets
        self._add_button = AddSongButton()
        self._remove_button = RemoveSongButton()
        self._load_button = LoadSongFolderButton()

        self._init_ui()
        self._bind_viewmodel()

    def _init_ui(self):
        """Initialize instance's internal widgets and layouts."""
        layout = QHBoxLayout()

        layout.addWidget(self._add_button)
        layout.addWidget(self._remove_button)
        layout.addWidget(self._load_button)

        layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def _bind_viewmodel(self):
        """Bind playlist viewmodel to playlist manager view."""
        # View -> ViewModel (user actions)
        self._add_button.clicked.connect(self._on_add_song_clicked)

    def _on_add_song_clicked(self):
        """Add the selected song(s) to playlist."""
        # The `getOpenFileNames()` returns a tuple containing the list of selected
        # filenames, and the name of the selected filter so we use `_` to discard
        # the filter name.
        file_paths, _ = QFileDialog.getOpenFileNames(
            parent=self,
            filter=FILE_DIALOG_FILTER,
        )

        # Do nothing if the file dialog is cancelled.
        if not file_paths:
            return

        self._viewmodel.add_songs(file_paths)


# ================================================================================
# PLAYLIST TABLE
# ================================================================================
#
# --- PLAYLIST WIDGET ROW HOVER EFFECTS ---
class HoverRowDelegate(QStyledItemDelegate):
    """Custom class for QTableView row hover effect."""

    def __init__(self, parent=None, hover_color: str="#3a3f4b"):
        """Initialize HoverRowDelegate.

        Args:
            parent: The parent object.
            hover_color: The desired row hover color. Defaults to #3a3f4b.
        """
        super().__init__()
        self._parent = parent
        self._hover_row = -1  # '-1' means no row hovered
        self._hover_brush = QBrush(QColor(hover_color))

    def setHoverRow(self, row: int):
        # Only do work if the hovered row actually changed
        if row != self._hover_row:
            self._hover_row = row

            # Ask the table (parent) to repaint its viewport so the hover effect
            # is immediately visible. Without this, Qt wouldn't know it needs
            # to redraw the cells when the mouse moves.
            #
            # Note: self.parent() is the QTableView that owns this delegate.
            # Its .viewport() is the widget that actually paints all the cells.
            if self._parent:
                self._parent.viewport().update()

    def paint(self, painter, option, index):
        # 'QStyleOptionViewItem(option) is a set of bit flags that describes
        # how the cell should be drawn.
        opt = QStyleOptionViewItem(option)

        # QStyle.StateFlag.State_HasFocus is a single bitmask.
        # So '~QStyle.StateFlag.State_HasFocus' means everything except HasFocus bit.
        opt.state &= ~QStyle.StateFlag.State_HasFocus

        # When hovering an unselected row, paint it as selected with our color
        state_flag = QStyle.StateFlag.State_Selected
        if index.row() == self._hover_row and not (opt.state & state_flag):
            opt.palette.setBrush(QPalette.ColorRole.Highlight, self._hover_brush)

            # Keep normal text color
            opt.palette.setBrush(
                QPalette.ColorRole.HighlightedText,
                opt.palette.brush(QPalette.ColorRole.Text),
            )

            opt.state |= QStyle.StateFlag.State_Selected

        # Call the base class paint method.
        # Qt does all normal painting, but now with modified options.
        super().paint(painter, opt, index)


# --- WIDGETS ---
class PlaylistTableWidget(QTableView):
    """Playlist table."""

    def __init__(self):
        """Initialize PlaylistTableWidget."""
        super().__init__()
        self._configure_properties()
        self._configure_viewport()
        self._configure_delegate()

    def _configure_properties(self):
        """Configure instance's properties."""
        # Add`is not None` check to resolve mypy no attribute [union-attr] errors
        # (optional).
        header = self.horizontalHeader()
        if header is not None:
            header.setDefaultAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            )
            header.setSectionsClickable(False)
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Add `is not None` check to resolve mypy no attribute [union-attr] errors
        # (optional).
        rows = self.verticalHeader()
        if rows is not None:
            rows.setDefaultSectionSize(50)
            rows.hide()

        # Disable cell edit.
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Remove cell focus on click.
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.setAlternatingRowColors(True)
        self.setObjectName("playlistTableView")
        self.setShowGrid(False)

        # Select the entire row on click
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Disable multi row selection.
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def _configure_viewport(self):
        """Configure instance's viewport."""
        # Add `is not None` check to resolve mypy no attribute [union-attr] errors.
        self._viewport = self.viewport()
        if self._viewport is not None:
            self._viewport.setMouseTracking(True)

        self.setMouseTracking(True)

    def _configure_delegate(self):
        """Configure instance's hover row delegate (for custom row hover effect)."""
        self._hover_delegate = HoverRowDelegate(self, hover_color="#34495E")
        self.setItemDelegate(self._hover_delegate)
        self.entered.connect(lambda idx: self._hover_delegate.setHoverRow(idx.row()))

    def leaveEvent(self, e):
        """QTableView leave event."""
        self._hover_delegate.setHoverRow(-1)
        super().leaveEvent(e)


# --- COMPONENTS ---
class PlaylistDisplay(QWidget):
    """A QWidget container for the main playlist widget.

    This container also acts as the main view layer for playlist,
    and is responsible for:
     - Displaying main playlist widget.
     - Handling playlist-related input events by calling the appropriate viewmodel
       commands (View -> ViewModel).
     - Observing viewmodel layer for model updates (ViewModel -> View).
    """

    def __init__(self, playlist_viewmodel: PlaylistViewModel):
        """Initialize PlaylistDisplay.

        Args:
            playlist_viewmodel: The playlist viewmodel.

        """
        super().__init__()
        self._viewmodel = playlist_viewmodel
        self._playlist_window = PlaylistTableWidget()
        self._playlist_window.setModel(self._viewmodel)
        self.selection_model = self.playlist_window.selectionModel()

        self._init_ui()
        self._bind_viewmodel()

    # --- UI and Widgets ---
    def _init_ui(self):
        """Initialize instance's internal widgets and layouts."""
        section_layout = QVBoxLayout()

        section_layout.addWidget(self.playlist_window)

        self.setLayout(section_layout)

    def _bind_viewmodel(self):
        """Bind playlist viewmodel to view."""
        # View -> ViewModel (user actions).
        self.selection_model.currentRowChanged.connect(self._on_row_changed)

        # ViewModel -> View (model updates).
        self._viewmodel.model_index_updated.connect(self._on_model_index_changed)

    # --- Slots ---
    @pyqtSlot(QModelIndex, QModelIndex)
    def _on_row_changed(self, current_index: QModelIndex, previous_index: QModelIndex):
        """Update the model index.

        Set the model index to the index of the selected row in playlist widget.

        Args:
            current_index: The current row index.
            previous_index: The previous row index.

        """
        if not current_index.isValid():
            return

        row_index = current_index.row()

        self._viewmodel.set_selected_index(row_index)

    @pyqtSlot(int)
    def _on_model_index_changed(self, new_index: int) -> None:
        """Update the playlist widget's current index.

        Args:
            new_index: The new row index.

        """
        if new_index != self._playlist_window.currentIndex().row():
            self._playlist_window.selectRow(new_index)

    # --- Properties ---
    @property
    def playlist_window(self) -> QTableView:
        """Return playlist widget instance."""
        return self._playlist_window
