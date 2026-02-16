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
    HORIZONTAL_MEDIUM_BUTTON,
    LOAD_FOLDER_ICON_PATH,
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
AddTrackButton = IconButtonFactory(
    ADD_ICON_PATH,
    widget_size=HORIZONTAL_MEDIUM_BUTTON,
    button_text="Add song(s)",
    object_name="addSongBtn",
)
RemoveTrackButton = IconButtonFactory(
    REMOVE_ICON_PATH,
    widget_size=HORIZONTAL_MEDIUM_BUTTON,
    button_text="Remove",
    object_name="removeSongBtn",
)
LoadFolderButton = IconButtonFactory(
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
        # Viewmodel
        self._playlist_viewmodel = playlist_viewmodel

        # Widgets
        self._add_track_btn = AddTrackButton()
        self._remove_track_btn = RemoveTrackButton()
        self._load_folder_btn = LoadFolderButton()

        # Setup
        self._init_ui()
        self._connect_signals()

    # --- Private methods ---
    def _init_ui(self):
        """Initialize instance's internal widgets and layouts."""
        layout = QHBoxLayout()

        layout.addWidget(self._add_track_btn)
        layout.addWidget(self._remove_track_btn)
        layout.addWidget(self._load_folder_btn)

        layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def _connect_signals(self):
        """Connect button widget signals to their respective slots."""
        # View -> ViewModel (user actions).
        self._add_track_btn.clicked.connect(self._on_add_track_btn_clicked)

    # --- Slots ---
    @pyqtSlot()
    def _on_add_track_btn_clicked(self) -> None:
        """Add track button click event signal handler."""
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

        self._playlist_viewmodel.add_tracks(file_paths)


# ================================================================================
# PLAYLIST TABLE
# ================================================================================
#
# --- PLAYLIST WIDGET ROW HOVER EFFECTS ---
class HoverRowDelegate(QStyledItemDelegate):
    """Custom QTableView row hover effect."""

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
class PlaylistWidget(QTableView):
    """Playlist widget."""

    def __init__(self):
        """Initialize PlaylistWidget."""
        super().__init__()
        # Setup
        self._configure_properties()
        self._configure_viewport()
        self._configure_delegate()

    def _configure_properties(self):
        """Configure instance's properties."""
        header = self.horizontalHeader()
        if header is not None:
            header.setDefaultAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            )
            header.setSectionsClickable(False)
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

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
    """

    def __init__(self, playlist_viewmodel: PlaylistViewModel):
        """Initialize PlaylistDisplay.

        Args:
            playlist_viewmodel: The playlist viewmodel.

        """
        super().__init__()
        # Viewmodel
        self._playlist_viewmodel = playlist_viewmodel

        # Widget
        self._playlist_widget = PlaylistWidget()
        self._playlist_widget.setModel(self._playlist_viewmodel)

        self.selection_model = self._playlist_widget.selectionModel()

        # Setup
        self._init_ui()
        self._connect_signals()

    # --- UI and Widgets ---
    def _init_ui(self):
        """Initialize instance's internal widgets and layouts."""
        section_layout = QVBoxLayout()

        section_layout.addWidget(self._playlist_widget)

        self.setLayout(section_layout)

    def _connect_signals(self):
        """Connect playlist widget, and viewmodel signals to their respective slots."""
        # View -> ViewModel (User actions).
        self.selection_model.currentRowChanged.connect(self._on_row_changed)

        # ViewModel -> View (Event updates).
        self._playlist_viewmodel.selected_index_changed.connect(self._on_model_index_changed)

    # --- Slots ---
    @pyqtSlot(QModelIndex, QModelIndex)
    def _on_row_changed(self, current_index: QModelIndex, previous_index: QModelIndex):
        """Playlist row selection change signal handler.

        Args:
            current_index: The selected row index.
            previous_index: The previous selected row index.

        """
        if not current_index.isValid():
            return

        row_index = current_index.row()

        self._playlist_viewmodel.set_selected_index(row_index)

    @pyqtSlot(int)
    def _on_model_index_changed(self, new_index: int) -> None:
        """Model selected index update signal handler.

        Updates the playlist widget's highlighted row (track) if it's new.

        Args:
            new_index: The updated index from model.

        """
        if new_index != self._playlist_widget.currentIndex().row():
            self._playlist_widget.selectRow(new_index)
