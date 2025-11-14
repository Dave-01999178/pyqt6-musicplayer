from PyQt6.QtCore import QAbstractTableModel, Qt
from PyQt6.QtGui import QBrush, QColor, QPalette
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableView,
    QTableWidget
)

from pyqt6_music_player.config import (
    ADD_ICON_PATH,
    LOAD_FOLDER_ICON_PATH,
    RECTANGLE_MEDIUM,
    REMOVE_ICON_PATH,
)
from pyqt6_music_player.models import PlaylistModel, Song
from pyqt6_music_player.views import IconButtonFactory

# ================================================================================
# PLAYLIST MANAGER BUTTON WIDGETS
# ================================================================================
AddSongButton = IconButtonFactory(
    ADD_ICON_PATH,
    widget_size=RECTANGLE_MEDIUM,
    button_text="Add song(s)",
    object_name="addSongBtn"
)
RemoveSongButton = IconButtonFactory(
    REMOVE_ICON_PATH,
    widget_size=RECTANGLE_MEDIUM,
    button_text="Remove",
    object_name="removeSongBtn"
)
LoadSongFolderButton = IconButtonFactory(
    LOAD_FOLDER_ICON_PATH,
    widget_size=RECTANGLE_MEDIUM,
    button_text="Load folder",
    object_name="loadFolderBtn"
)


# ================================================================================
# PLAYLIST TABLE CUSTOM STYLE AND EFFECTS
# ================================================================================
class HoverRowDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, hover_color: str="#3a3f4b"):
        super().__init__()
        self._parent = parent
        self._hover_row = -1  # '-1' means no row hovered
        self._hover_brush = QBrush(QColor(hover_color))

    def setHoverRow(self, row: int):
        # Only do work if the hovered row actually changed
        if row != self._hover_row:
            self._hover_row = row

            # Ask the table (parent) to repaint its viewport so the hover effect
            # is immediately visible. Without this, Qt wouldn’t know it needs
            # to redraw the cells when the mouse moves.
            #
            # Note: self.parent() is the QTableView that owns this delegate.
            # Its .viewport() is the widget that actually paints all the cells.
            if self._parent:
                self._parent.viewport().update()

    def paint(self, painter, option, index):
        # 'QStyleOptionViewItem(option).state or opt.state' is a set of bit flags that describe how
        # the cell should be drawn.
        opt = QStyleOptionViewItem(option)

        # QStyle.StateFlag.State_HasFocus is a single bitmask.
        # So '~QStyle.StateFlag.State_HasFocus' means everything except the HasFocus bit.
        opt.state &= ~QStyle.StateFlag.State_HasFocus

        # When hovering an unselected row, paint it as selected with our color
        if index.row() == self._hover_row and not (opt.state & QStyle.StateFlag.State_Selected):
            opt.palette.setBrush(QPalette.ColorRole.Highlight, self._hover_brush)

            # Keep normal text color
            opt.palette.setBrush(
                QPalette.ColorRole.HighlightedText,
                opt.palette.brush(QPalette.ColorRole.Text)
            )

            opt.state |= QStyle.StateFlag.State_Selected

        # Call the base class paint method.
        # Qt does all normal painting, but now with modified options.
        super().paint(painter, opt, index)


# ================================================================================
# PLAYLIST MODEL AND WIDGET
# ================================================================================
class PlaylistTableModel(QAbstractTableModel):
    def __init__(self, playlist_model: PlaylistModel):
        super().__init__()
        self.playlist_model = playlist_model
        self.header_label = Song.get_metadata_fields()

        playlist_model.playlist_changed.connect(self._update_playlist_table)

    def rowCount(self, parent=None):
        return len(self.playlist_model.playlist)

    def columnCount(self, parent=None):
        return len(self.header_label)

    def data(self, index, role=...):
        if not index.isValid():
            return

        song = self.playlist_model.playlist[index.row()]
        col = index.column()
        field_name = self.header_label[col]

        if role == Qt.ItemDataRole.DisplayRole:
            if field_name == "duration":
                return song.formatted_duration()
            return getattr(song, field_name)

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if field_name == "duration":
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter

        return None

    def headerData(self, section, orientation, role=...):
        field_name = self.header_label[section]

        if  role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return field_name.title()

        elif role == Qt.ItemDataRole.TextAlignmentRole and field_name == "duration":
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter

        return None

    def _update_playlist_table(self):
        self.beginResetModel()
        self.endResetModel()


class PlaylistTableWidget(QTableView):
    def __init__(self, playlist_state: PlaylistModel):
        super().__init__()
        self._model = PlaylistTableModel(playlist_state)
        self.setModel(self._model)

        self._configure_properties()
        self._configure_viewport()
        self._configure_delegate()

    def leaveEvent(self, e):
        self._hover_delegate.setHoverRow(-1)
        super().leaveEvent(e)

    def _configure_properties(self):
        # Add`is not None` check to resolve mypy no attribute [union-attr] errors (optional).
        header = self.horizontalHeader()
        if header is not None:
            header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            header.setSectionsClickable(False)
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Add `is not None` check to resolve mypy no attribute [union-attr] errors (optional).
        rows = self.verticalHeader()
        if rows is not None:
            rows.setDefaultSectionSize(50)
            rows.hide()

        self.setAlternatingRowColors(True)  # Alternating row colors
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Disable cell edit
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Remove cell focus on click
        self.setObjectName("playlistTableView")  # Set object name for qss.
        self.setShowGrid(False)  # Remove grid inside table

        # Select the entire row on click
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Disable multi row selection (temporary).
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def _configure_viewport(self):
        # `is not None` check to resolve mypy no attribute [union-attr] errors.
        self._viewport = self.viewport()
        if self._viewport is not None:
            self._viewport.setMouseTracking(True)
        self.setMouseTracking(True)

    def _configure_delegate(self):
        self._hover_delegate = HoverRowDelegate(self, hover_color="#34495E")
        self.setItemDelegate(self._hover_delegate)
        self.entered.connect(lambda idx: self._hover_delegate.setHoverRow(idx.row()))
