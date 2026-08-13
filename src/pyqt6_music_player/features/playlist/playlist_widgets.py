from PyQt6.QtCore import QModelIndex, QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPalette,
    QPen,
)
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableView,
    QTableWidget,
)

# ==================== CONSTANTS ====================
ACTIVE_ROW_COLOR = "#2A3142"
ACTIVE_ROW_TEXT_COLOR = "#00D9FF"
HOVER_ROW_COLOR = "#1ABC9C"
PLAYLIST_WIDGET_OBJ_NAME = "playlistTableView"


# ==================== CLASSES ====================
class PlaylistItemDelegate(QStyledItemDelegate):
    """Custom delegate for playlist rows with hover and active row highlighting."""

    def __init__(self, parent: QTableView):
        super().__init__()
        self._parent = parent

        # Row state
        self._active_row = -1
        self._hover_row = -1

        # Brush
        self._active_row_brush = QBrush(QColor(ACTIVE_ROW_COLOR))
        self._active_row_text_brush = QBrush(QColor(ACTIVE_ROW_TEXT_COLOR))
        self._hover_row_brush = QBrush(QColor(HOVER_ROW_COLOR))

    # -- Public methods --
    def set_active_row(self, row: int) -> None:
        """Mark the row as the active (currently playing) row."""
        if row == self._active_row:
            return

        old_row = self._active_row
        self._active_row = row

        # Refresh both rows so the active-row effect moves off the old row and onto the
        # new one
        self._update_row(old_row)
        self._update_row(row)

    def set_hover_row(self, row: int) -> None:
        """Mark the row as hovered."""
        if row != self._hover_row:
            old_row = self._hover_row
            self._hover_row = row

            # Reset old hover row by applying Qt default because old != current row
            self._update_row(old_row)

            # Apply row effect because new row is current row
            self._update_row(row)

    # -- Overriden methods --
    def paint(self, painter, option, index) -> None:
        # Copy of `option`; stores draw parameters for items in the QTableWidget
        # (our PlaylistWidget).
        opt = QStyleOptionViewItem(option)

        # The row in playlist that we are currently drawing
        current_row = index.row()

        # Current row state is selected - highest priority (Qt default)
        selected = opt.state & QStyle.StateFlag.State_Selected
        if selected:
            # Let Qt draw selection normally; redraw active-row border if needed,
            # since default drawing strips it.
            super().paint(painter, opt, index)
            if current_row == self._active_row:
                self._draw_active_row_border(painter, option, index)

            return

        # No StateFlag for hover/active, so we use equality checks for those.
        #
        # Current row is hovered - second priority
        if current_row == self._hover_row:
            self._apply_highlight(opt, self._hover_row_brush)
            if current_row == self._active_row:
                self._apply_text_color(opt, self._active_row_text_brush)

        # Current row is active - lowest priority
        elif current_row == self._active_row:
            self._apply_text_color(opt, self._active_row_text_brush)
            self._apply_highlight(opt, self._active_row_brush)

        # Let Qt draw the rest to maintain the default behavior.
        super().paint(painter, opt, index)

        # Draw border after Qt's paint, since `super().paint()` would overwrite it
        # if done inside the elif branch above
        if current_row == self._active_row:
            self._draw_active_row_border(painter, option, index)

    # -- Protected methods --
    @staticmethod
    def _apply_highlight(opt, brush) -> None:
        opt.palette.setBrush(QPalette.ColorRole.Highlight, brush)
        opt.palette.setBrush(
            QPalette.ColorRole.HighlightedText,
            opt.palette.brush(QPalette.ColorRole.Text),
        )

        # Treat as selected to highlight the row
        opt.state |= QStyle.StateFlag.State_Selected

    @staticmethod
    def _apply_text_color(opt, brush) -> None:
        opt.palette.setBrush(
            QPalette.ColorRole.Text,
            QBrush(QColor(brush)),
        )

    def _draw_active_row_border(self, painter, option, index) -> None:
        view = self._parent
        if view is None:
            return

        model = view.model()
        if model is None:
            return

        row = index.row()

        # Get the row's full span
        left_index = model.index(row, 0)
        right_index = model.index(row, model.columnCount() - 1)

        rect = view.visualRect(left_index) | view.visualRect(right_index)

        # Adjust for crisp borders (avoid clipping)
        rect.adjust(1, 1, -1, -1)

        # Enables antialiasing so curved lines appear smooth instead of jagged
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        painter.save()

        # Create round rectangle path
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 8, 8)

        # Create gradient effect
        gradient = QLinearGradient(QPointF(rect.topLeft()), QPointF(rect.topRight()))
        gradient.setColorAt(0, QColor("#A855F7"))
        gradient.setColorAt(1, QColor("#00D9FF"))

        # Apply gradient to pen and draw border
        pen = QPen(QBrush(gradient), 2)
        painter.setPen(pen)
        painter.drawPath(path)

        painter.restore()

    def _update_row(self, row: int) -> None:
        if self._parent is None or row < 0:
            return

        model = self._parent.model()
        if model is None:
            return

        # Get the row's full span
        left = model.index(row, 0)
        right = model.index(row, model.columnCount() - 1)

        rect = self._parent.visualRect(left) | self._parent.visualRect(right)

        self._parent.viewport().update(rect)


class PlaylistWidget(QTableView):
    """Playlist table view with row hover effect and single-row selection."""

    def __init__(self):
        super().__init__()
        # Setup
        self._configure_properties()
        self._configure_viewport()
        self._init_delegate()

        self.entered.connect(self._on_table_mouse_hover)

    # -- Public methods --
    def set_active_row(self, row_index: int) -> None:
        """Set the active row in the playlist.

        Args:
            row_index: Row index to mark as active.

        """
        self._playlist_delegate.set_active_row(row_index)

    # -- Overriden methods --
    def leaveEvent(self, e) -> None:
        # Reset the hover row index when the cursor leaves the viewport
        self._playlist_delegate.set_hover_row(-1)
        super().leaveEvent(e)

    # -- Protected methods --
    def _configure_properties(self) -> None:
        # Configure instance properties and behavior
        header = self.horizontalHeader()
        if header is not None:
            header.setDefaultAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            )
            header.setSectionsClickable(False)

            # Set resize mode to QHeaderView.ResizeMode.Stretch to evenly occupy
            # available space
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        rows = self.verticalHeader()
        if rows is not None:
            rows.setDefaultSectionSize(50)
            rows.hide()

        # Disable cell edit
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Remove cell focus on click
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.setObjectName(PLAYLIST_WIDGET_OBJ_NAME)
        self.setShowGrid(False)

        # Select the entire row on click
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Disable multi row selection
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def _configure_viewport(self) -> None:
        # Enable mouse tracking inside QTableView (data/content area)
        self._viewport = self.viewport()
        if self._viewport is not None:
            self._viewport.setMouseTracking(True)

        self.setMouseTracking(True)

    def _on_table_mouse_hover(self, index: QModelIndex) -> None:
        if not index.isValid():
            return

        self._playlist_delegate.set_hover_row(index.row())

    def _init_delegate(self) -> None:
        self._playlist_delegate = PlaylistItemDelegate(self)
        self.setItemDelegate(self._playlist_delegate)
