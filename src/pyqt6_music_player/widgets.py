# TODO: Add module docstring
import logging
from pathlib import Path
from typing import ClassVar

from PyQt6.QtCore import (
    QModelIndex,
    QPointF,
    QRectF,
    QSize,
    Qt,
    QTimer,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPalette,
    QPen,
    QPixmap,
)
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QPushButton,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableView,
    QTableWidget,
)

from pyqt6_music_player.core import (
    ALBUM_ART_PLACEHOLDER,
    HIGH_VOLUME_ICON,
    LOW_VOLUME_ICON,
    MAX_VOLUME,
    MEDIUM_VOLUME_ICON,
    MIN_VOLUME,
    MUTED_VOLUME_ICON,
    REPEAT_DISABLED_ICON,
    REPEAT_ICON,
    REPEAT_ONE_ICON,
    SECONDARY_PLAYBACK_CONTROL_BTN_ICON_SIZE,
    SECONDARY_PLAYBACK_CONTROL_BTN_OBJ_NAME,
    SECONDARY_PLAYBACK_CONTROL_BTN_SIZE,
    SHUFFLE_DISABLED_ICON,
    SHUFFLE_ICON,
    TRACK_METADATA_LABEL_SIZE,
    VOLUME_BTN_ICON_SIZE,
    VOLUME_BTN_SIZE,
    RepeatMode,
    ShuffleMode,
)


# ==================== BASE WIDGETS ====================
class IconButton(QPushButton):
    """A reusable QPushButton with a custom icon and fixed dimensions."""

    def __init__(
            self,
            icon_path: Path,
            icon_size: tuple[int, int],
            widget_size: tuple[int, int],
            *,
            button_text: str | None = None,
            object_name: str | None = None,
    ) -> None:
        """Initialize IconButton.

        Args:
            icon_path: Path to the icon file.
            icon_size: Size of the icon inside the button as (width, height) in pixels.
            widget_size: Size of the entire button widget as (width, height) in pixels.
            button_text: Optional text for the button. Defaults to ``None``.
            object_name: Qt object name useful for QSS selectors.
                         Defaults to ``None``.

        """
        super().__init__(text=button_text)
        self._icon_path = icon_path

        # Instance properties
        self._icon_size = icon_size
        self._widget_size = widget_size
        self._object_name = object_name

        # Setup
        self._configure_properties()

    # -- Public methods --
    def _configure_properties(self) -> None:
        # Configure instance properties
        if not self._icon_path.exists():
            logging.warning("Icon path not found: %s", self._icon_path)

        qicon = QIcon(str(self._icon_path))

        self.setIcon(qicon)
        self.setIconSize(QSize(*self._icon_size))
        self.setFixedSize(*self._widget_size)

        if self._object_name:
            self.setObjectName(self._object_name)


# ==================== CUSTOM WIDGETS ====================
class AlbumArtLabel(QLabel):
    """Custom QLabel for displaying track album art."""

    def __init__(self):
        """Initialize AlbumArtLabel."""
        super().__init__()
        # Setup
        self._configure_properties()
        self._init_ui()

    # -- Public methods --
    def set_image(self, image) -> None:
        if image is None:
            return

        self._set_image(image)

    # -- Protected/internal methods --
    def _init_ui(self) -> None:
        # Set instance default album art placeholder
        self._set_image(ALBUM_ART_PLACEHOLDER)

    def _configure_properties(self) -> None:
        # Configure instance properties
        self.setFixedSize(75, 75)
        self.setScaledContents(False)

    def _set_image(self, image) -> None:
        pixmap = QPixmap(str(image))
        scaled = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.setPixmap(scaled)


class MarqueeLabel(QLabel):
    """Custom QLabel for displaying track metadata."""

    def __init__(
            self,
            text: str,
            *,
            widget_size: tuple[int, int] = TRACK_METADATA_LABEL_SIZE,
            object_name: str | None = None,
    ):
        """Initialize MarqueeLabel.

        Args:
            text: The text to display.
            widget_size: Size of the marquee label as (width, height) in pixels.
                         Defaults to (100, 25).
            object_name: Qt object name useful for QSS selectors.
                         Defaults to ``None``.

        """
        super().__init__(text=text)
        # Instance properties
        self._widget_size = widget_size
        self._object_name = object_name

        self._configure_properties()

        # Text animation configuration
        self._offset = 0  # Current horizontal offset
        self._speed = 1  # Pixels per timer tick
        self._gap = 20  # Space between repeated text instances

        # Animation timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_offset)  # type: ignore

        self._timer.start(20)

    # -- Public methods (Parent) --
    def paintEvent(self, event: QPaintEvent | None) -> None:
        # Custom paint event for scrolling text effect
        font_metrics = self.fontMetrics()
        text_width = font_metrics.horizontalAdvance(self.text())

        # If the current text fits, let QLabel paint itself to preserve default
        # behaviour (default painting)
        if text_width <= self.width():
            super().paintEvent(event)
            return

        # Else, draw scrolling text.
        painter = QPainter(self)
        painter.setPen(self.palette().windowText().color())

        current_text = self.text()
        x = -self._offset  # Shifts the text leftward
        y = (self.height() + font_metrics.ascent()) // 2  # Vertically centers the text

        # Create a seamless marquee effect when the text is wider than the widget:
        # - The first `drawText` renders the "leaving" text
        #   (shifted left from the visible area)
        # - The second `drawText` renders the "entering" text
        #  (positioned after the text, and gap)
        # Together, they produce a continuous looping scroll
        painter.drawText(x, y, current_text)
        painter.drawText(x + text_width + self._gap, y, current_text)

    def setText(self, text: str | None) -> None:
        super().setText(text)  # Default behavior

        # Reset offset when text changes to avoid mid-word jumps
        # and weird starting positions
        self._offset = 0

    # -- Protected/internal methods --
    def _configure_properties(self) -> None:
        # Configure instance properties
        self.setFixedSize(*self._widget_size)
        self.setObjectName(self._object_name)

    def _update_offset(self) -> None:
        # Compute and update text offset based on the current text position
        text_width = self.fontMetrics().horizontalAdvance(self.text())
        cycle_width = (text_width + self._gap)

        # If the current text fits, do nothing
        if text_width <= self.width():
            return

        # Add '% cycle_width' to the offset formula to avoid the noticeable jump
        # when the text resets
        self._offset = (self._offset + self._speed) % cycle_width

        # Reset offset after one full marquee cycle (text + gap) has scrolled past
        # for seamless animation
        if self._offset > text_width + self._gap:
            self._offset = 0

        self.update()


class PlaylistItemDelegate(QStyledItemDelegate):
    """Custom delegate for playlist rows with hover and active row highlighting."""

    def __init__(self, parent: QTableView):
        """Initialize PlaylistItemDelegate.

        Args:
            parent: The parent QTableView.

        """
        super().__init__()
        self._parent = parent

        # Row state
        self._active_row = -1
        self._hover_row = -1

        # Brush
        self._active_row_brush = QBrush(QColor("#2A3142"))
        self._active_row_text_brush = QBrush(QColor("#00D9FF"))
        self._hover_row_brush = QBrush(QColor("#1ABC9C"))

    # -- Public methods --
    #
    # Instance methods
    def set_active_row(self, row: int) -> None:
        if row == self._active_row:
            return

        old_row = self._active_row
        self._active_row = row

        # Reset old active row by applying Qt default because current != new row
        self._update_row(old_row)

        # Apply row effect because new row is current row
        self._update_row(row)

    def set_hover_row(self, row: int) -> None:
        if row != self._hover_row:
            old_row = self._hover_row
            self._hover_row = row

            # Reset old hover row by applying Qt default because old != current row
            self._update_row(old_row)

            # Apply row effect because new row is current row
            self._update_row(row)

    # Parent methods
    def paint(self, painter, option, index) -> None:
        opt = QStyleOptionViewItem(option)  # Stores a copy of `option`

        # Remove focus visuals (dotted outline or highlights)
        opt.state &= ~QStyle.StateFlag.State_HasFocus
        row_index = index.row()
        selected = opt.state & QStyle.StateFlag.State_Selected

        # Row selected - highest priority (Qt default)
        if selected:
            super().paint(painter, opt, index)
            # Draw border if selected row == active row
            if row_index == self._active_row:
                self._draw_active_row_border(painter, option, index)
            return

        # Hover - second priority
        if row_index == self._hover_row:
            self._apply_highlight(opt, self._hover_row_brush)
            # Apply text color if hover row == active row
            if row_index == self._active_row:
                opt.palette.setBrush(
                    QPalette.ColorRole.Text,
                    QBrush(QColor(self._active_row_text_brush)),
                )

        # Active row - lower priority
        elif row_index == self._active_row:
            opt.palette.setBrush(
                QPalette.ColorRole.Text,
                QBrush(QColor(self._active_row_text_brush)),
            )
            self._apply_highlight(opt, self._active_row_brush)

        # Use the default behavior for the rest
        super().paint(painter, opt, index)

        # Draw border to the active row after painting
        if row_index == self._active_row:
            self._draw_active_row_border(painter, option, index)

    # -- Protected/Internal methods --
    def _apply_highlight(self, opt, brush):
        opt.palette.setBrush(QPalette.ColorRole.Highlight, brush)
        opt.palette.setBrush(
            QPalette.ColorRole.HighlightedText,
            opt.palette.brush(QPalette.ColorRole.Text),
        )

        # Treat as selected to highlight the row
        opt.state |= QStyle.StateFlag.State_Selected

    def _draw_active_row_border(self, painter, option, index):
        view = self._parent
        if view is None:
            return

        model = view.model()
        if model is None:
            return

        row = index.row()

        # Determine row's full span
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

        # Get first and last index of the row (entire row)
        left = model.index(row, 0)
        right = model.index(row, model.columnCount() - 1)

        rect = self._parent.visualRect(left) | self._parent.visualRect(right)

        self._parent.viewport().update(rect)


class PlaylistWidget(QTableView):
    """Playlist table view with row hover effect and single-row selection."""

    def __init__(self):
        """Configure table properties, viewport tracking, and hover delegate."""
        super().__init__()
        # Setup
        self._configure_properties()
        self._connect_signals()
        self._configure_viewport()
        self._init_delegate()

    # -- Public methods --
    #
    # Instance method
    def set_delegate_active_row(self, row_index: int) -> None:
        """Set the active row in the playlist.

        Args:
            row_index: Row index to mark as active.

        """
        self._playlist_delegate.set_active_row(row_index)

    # Parent method
    def leaveEvent(self, e) -> None:
        # Reset the hover row index when the cursor leaves the viewport
        self._playlist_delegate.set_hover_row(-1)
        super().leaveEvent(e)

    # -- Protected/internal methods --
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

        self.setObjectName("playlistTableView")
        self.setShowGrid(False)

        # Select the entire row on click
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Disable multi row selection
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def _configure_viewport(self) -> None:
        # Enable mouse tracking inside QTableView (data/content area e.g. cells)
        self._viewport = self.viewport()
        if self._viewport is not None:
            self._viewport.setMouseTracking(True)

        self.setMouseTracking(True)

    def _connect_signals(self):
        self.entered.connect(self._on_table_mouse_hover)

    def _on_table_mouse_hover(self, index: QModelIndex) -> None:
        """Update hover row when mouse enters a new row.

        Args:
            index: The model index of the hovered row.

        """
        if not index.isValid():
            return

        self._playlist_delegate.set_hover_row(index.row())

    def _init_delegate(self) -> None:
        self._playlist_delegate = PlaylistItemDelegate(self)
        self.setItemDelegate(self._playlist_delegate)


class ShuffleButton(IconButton):
    """Button for toggling shuffle mode on or off."""

    change_shuffle_mode_request  = pyqtSignal(ShuffleMode)

    def __init__(
            self,
            icon_path: Path = SHUFFLE_DISABLED_ICON,
            icon_size: tuple[int, int] = SECONDARY_PLAYBACK_CONTROL_BTN_ICON_SIZE,
            widget_size: tuple[int, int] = SECONDARY_PLAYBACK_CONTROL_BTN_SIZE,
            object_name: str | None = SECONDARY_PLAYBACK_CONTROL_BTN_OBJ_NAME,
    ):
        """Initialize ShuffleButton.

        Args:
            icon_path: Path to the icon file. Defaults to 'shuffle disabled' icon.
            icon_size: Size of the icon inside the button as
                       (width, height) in pixels. Defaults to (15, 15).
            widget_size: Size of the entire button widget as (width, height) in pixels.
                         Defaults to (30, 30).
            object_name: Qt object name useful for QSS selectors.
                         Defaults to 'secondaryPlaybackControlBtn'.

        """
        super().__init__(
            icon_path=icon_path,
            icon_size=icon_size,
            widget_size=widget_size,
            object_name=object_name,
        )
        self.setCheckable(True)

        self.toggled.connect(self._on_toggle)

    # -- Protected/Internal methods --
    def _on_toggle(self, checked: bool) -> None:
        # Toggle and emit shuffle mode
        shuffle_mode = ShuffleMode.ON if checked else ShuffleMode.OFF

        self.change_shuffle_mode_request.emit(shuffle_mode)

        self._update_icon(shuffle_mode)

    def _update_icon(self, shuffle_mode: ShuffleMode) -> None:
        # Update icon based on the current shuffle mode
        icon = (
            SHUFFLE_DISABLED_ICON
            if shuffle_mode == ShuffleMode.OFF
            else SHUFFLE_ICON
        )
        self.setIcon(QIcon(str(icon)))


class RepeatButton(IconButton):
    """Button for cycling through repeat modes (off, repeat one, repeat all)."""

    MODES: ClassVar[list[RepeatMode]] = list(RepeatMode)
    change_repeat_mode_request  = pyqtSignal(RepeatMode)

    def __init__(
            self,
            icon_path: Path = REPEAT_DISABLED_ICON,
            icon_size: tuple[int, int] = SECONDARY_PLAYBACK_CONTROL_BTN_ICON_SIZE,
            widget_size: tuple[int, int] = SECONDARY_PLAYBACK_CONTROL_BTN_SIZE,
            object_name: str | None = SECONDARY_PLAYBACK_CONTROL_BTN_OBJ_NAME,
    ):
        """Initialize RepeatButton.

        Args:
            icon_path: Path to the icon file. Defaults to 'repeat disabled' icon.
            icon_size: Size of the icon inside the button as
                       (width, height) in pixels. Defaults to (15, 15).
            widget_size: Size of the entire button widget as (width, height) in pixels.
                         Defaults to (30, 30).
            object_name: Qt object name useful for QSS selectors.
                         Defaults to 'secondaryPlaybackControlBtn'.

        """
        super().__init__(
            icon_path=icon_path,
            icon_size=icon_size,
            widget_size=widget_size,
            object_name=object_name,
        )
        self._mode_idx = 0

        self.setCheckable(True)

        self.clicked.connect(self._on_clicked)

    # -- Protected/Internal methods --
    def _on_clicked(self) -> None:
        # Cycle and emit shuffle mode
        self._mode_idx = (self._mode_idx + 1) % len(self.MODES)

        repeat_mode = self.MODES[self._mode_idx]

        self.change_repeat_mode_request.emit(repeat_mode)

        self._update_icon(repeat_mode)

    def _update_icon(self, repeat_mode: RepeatMode) -> None:
        # Update button based on the repeat mode
        if repeat_mode == RepeatMode.OFF:
            icon = REPEAT_DISABLED_ICON
        elif repeat_mode == RepeatMode.ONE:
            icon = REPEAT_ONE_ICON
        else:
            icon = REPEAT_ICON

        self.setIcon(QIcon(str(icon)))

        # Change the toggle state only if current state != new state
        toggle_state = repeat_mode in {RepeatMode.ONE, RepeatMode.ALL}
        if self.isChecked() != toggle_state:
            self.setChecked(toggle_state)


class VolumeButton(IconButton):
    """Button for controlling and displaying volume state.

    This button changes its icon based on the current volume level, and can be toggled
    to mute or unmute the audio.
    """

    HIGH_BOUNDARY = 67
    MEDIUM_BOUNDARY = 34
    LOW_BOUNDARY = 1

    def __init__(
            self,
            icon_path: Path = HIGH_VOLUME_ICON,
            icon_size: tuple[int, int] = VOLUME_BTN_ICON_SIZE,
            widget_size: tuple[int, int] = VOLUME_BTN_SIZE,
    ):
        """Initialize VolumeButton.

        Args:
            icon_path: Path to the icon file. Defaults to 'high-volume' icon.
            icon_size: Size of the icon inside the button as
                       (width, height) in pixels. Defaults to (15, 15).
            widget_size: Size of the entire button widget as (width, height) in pixels.
                         Defaults to (30, 30).

        """
        super().__init__(
            icon_path=icon_path,
            icon_size=icon_size,
            widget_size=widget_size,
        )
        self._current_icon = icon_path

        self.setCheckable(True)

    # -- Public methods --
    def update_icon(self, new_volume: int) -> None:
        """Update instance icon based on the new volume's current level.

        Args:
            new_volume: The new volume.

        """
        if not (MIN_VOLUME <= new_volume <= MAX_VOLUME):
            raise ValueError(f"New volume: {new_volume} is out of range.")

        if new_volume >= self.HIGH_BOUNDARY:
            icon = HIGH_VOLUME_ICON
        elif new_volume >= self.MEDIUM_BOUNDARY:
            icon = MEDIUM_VOLUME_ICON
        elif new_volume >= self.LOW_BOUNDARY:
            icon = LOW_VOLUME_ICON
        else:
            icon = MUTED_VOLUME_ICON

        # Update icon only if it is new
        if icon == self._current_icon:
            return

        self.setIcon(QIcon(str(icon)))

        self._current_icon = icon


class VolumeLabel(QLabel):
    """QLabel widget for displaying the current volume level.

    This label shows the volume as a number (0-100).
    """

    def __init__(self):
        """Initialize VolumeLabel."""
        super().__init__()

        self._configure_properties()

    # -- Protected/internal methods --
    def _configure_properties(self):
        # Set the instance width to the length of "100" + 4 character spaces
        # to center the text and avoid the weird behaviour when the text is "0"
        label_width = self.fontMetrics().horizontalAdvance("100")

        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
        self.setFixedWidth(label_width)

