from PyQt6.QtCore import Qt, QAbstractTableModel
from PyQt6.QtGui import QBrush, QColor, QPalette
from PyQt6.QtWidgets import QTableWidget, QHeaderView, QTableView, QStyledItemDelegate, QStyle, QStyleOptionViewItem, \
    QAbstractItemView


class PlayPauseDelegate(QStyledItemDelegate):
    def __init__(self):
        super().__init__()


class HoverRowDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, hover_color="#3a3f4b"):
        super().__init__()
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
            if self.parent():
                self.parent().viewport().update()

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


class PlaylistModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()

        self.header_label = ["Title", "Performer", "Album", "Duration"]
        self.row_data = [
            {"Title": "Song 1", "Performer" :"Performer 1", "Album": "Album 1", "Duration": "2:30"},
            {"Title": "Song 2", "Performer" :"Performer 2", "Album": "Album 2", "Duration": "1:30"},
            {"Title": "Song 3", "Performer" :"Performer 3", "Album": "Album 3", "Duration": "2:15"},
            {"Title": "Song 4", "Performer" :"Performer 4", "Album": "Album 4", "Duration": "1:45"},
        ]

    def rowCount(self, parent=None):
        return len(self.row_data)

    def columnCount(self, parent=None):
        return len(self.header_label)

    def data(self, index, role=...):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            row_idx, col_idx = index.row(), index.column()
            row = self.row_data[row_idx]
            header = self.header_label[col_idx]

            return row.get(header)
        return None

    def headerData(self, section, orientation, role=...):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header_label[section]
        return None


class PlaylistWindow(QTableView):
    def __init__(self):
        super().__init__()
        self.model = PlaylistModel()
        self.setModel(self.model)

        self._configure_properties()

        self.viewport().setMouseTracking(True)
        self.setMouseTracking(True)

        self._hover_delegate = HoverRowDelegate(self, hover_color="#48484b")
        self.setItemDelegate(self._hover_delegate)

        self.entered.connect(lambda idx: self._hover_delegate.setHoverRow(idx.row()))

    def leaveEvent(self, e):
        self._hover_delegate.setHoverRow(-1)
        super().leaveEvent(e)

    def _configure_properties(self):
        # Make column headers take available space equally
        header = self.horizontalHeader()

        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header.setSectionsClickable(False)

        self.verticalHeader().setDefaultSectionSize(50)

        self.setAlternatingRowColors(True)  # Alternating row colors
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Disable cell edit
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Remove cell focus on click
        self.setObjectName("playlistTableView")  # Set object name for qss.
        self.setShowGrid(False)  # Remove grid inside table

        # Select the entire row on click
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.verticalHeader().hide()
