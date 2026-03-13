# TODO: Add module docstring
import logging
from pathlib import Path
from typing import ClassVar

from PyQt6.QtCore import QSize, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QIcon,
    QPainter,
    QPaintEvent,
    QPalette,
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
    DEFAULT_BTN_ICON_SIZE,
    DEFAULT_BTN_SIZE,
    HIGH_VOLUME_ICON_PATH,
    LOW_VOLUME_ICON_PATH,
    MAX_VOLUME,
    MEDIUM_VOLUME_ICON_PATH,
    MIN_VOLUME,
    MUTED_VOLUME_ICON_PATH,
    REPEAT_DISABLED_ICON_PATH,
    REPEAT_ICON_PATH,
    REPEAT_ONE_ICON_PATH,
    SHUFFLE_DISABLED_ICON_PATH,
    SHUFFLE_ICON_PATH,
    TRACK_METADATA_LABEL_SIZE,
    RepeatMode,
    ShuffleMode,
)


# ==================== BASE WIDGETS ====================
class IconButton(QPushButton):
    """A customizable QPushButton with fixed size, icon, and a configurable properties.

    This class extends the QPushButton widget to provide a consistent,
    and reusable button with options for a fixed icon and widget size, button text,
    icon size, and a custom object name for styling for icon-based buttons that
    require custom behavior or state.
    """

    def __init__(
            self,
            icon_path: Path,
            *,
            icon_size: tuple[int, int] = DEFAULT_BTN_ICON_SIZE,
            widget_size: tuple[int, int] = DEFAULT_BTN_SIZE,
            button_text: str | None = None,
            object_name: str | None = None,
    ) -> None:
        """Initialize IconButton.

        Args:
            icon_path: Path to the icon file.
            icon_size: Size of the icon inside the button as
                       (width, height) in pixels. Defaults to (15, 15).
            widget_size: Size of the entire button widget as
                         (width, height) in pixels. Defaults to (30, 30).
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
    """Custom QLabel for displaying track metadata that can handle text spills."""

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


class HoverRowDelegate(QStyledItemDelegate):
    """Row hover effect delegate for QTableView."""

    def __init__(self, parent=None, hover_color: str="#3a3f4b"):
        """Set up the delegate with a configurable hover color.

        Args:
            parent: The parent QTableView.
            hover_color: Row highlight color on hover. Defaults to '#3a3f4b'.

        """
        super().__init__()
        self._parent = parent
        self._hover_row = -1  # '-1' means no row hovered
        self._hover_brush = QBrush(QColor(hover_color))

    # -- Public methods (Parent) --
    def setHoverRow(self, row: int) -> None:
        # Do work only if the hovered row actually changed
        if row != self._hover_row:
            self._hover_row = row

            # Ask the table (parent) to repaint its viewport (the display area)
            # so the hover effect is immediately visible
            #
            # Without this, Qt wouldn't know it needs to redraw the cells
            # when the mouse moves
            if self._parent:
                self._parent.viewport().update()

    def paint(self, painter, option, index) -> None:
        opt = QStyleOptionViewItem(option)
        opt.state &= ~QStyle.StateFlag.State_HasFocus

        state_flag = QStyle.StateFlag.State_Selected
        if index.row() == self._hover_row and not (opt.state & state_flag):
            opt.palette.setBrush(QPalette.ColorRole.Highlight, self._hover_brush)
            opt.palette.setBrush(
                QPalette.ColorRole.HighlightedText,
                opt.palette.brush(QPalette.ColorRole.Text),
            )

            opt.state |= QStyle.StateFlag.State_Selected

        super().paint(painter, opt, index)


class PlaylistWidget(QTableView):
    """Playlist table view with row hover effect and single-row selection."""

    def __init__(self):
        """Configure table properties, viewport tracking, and hover delegate."""
        super().__init__()
        # Setup
        self._configure_properties()
        self._configure_viewport()
        self._configure_delegate()

    # -- Public method (Parent) --
    def leaveEvent(self, e) -> None:
        self._hover_delegate.setHoverRow(-1)  # Reset the highlighted row
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

        self.setAlternatingRowColors(True)
        self.setObjectName("playlistTableView")
        self.setShowGrid(False)

        # Select the entire row on click
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Disable multi row selection
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def _configure_viewport(self) -> None:
        # Enable widget and viewport (the display area) mouse tracking
        self._viewport = self.viewport()
        if self._viewport is not None:
            self._viewport.setMouseTracking(True)

        self.setMouseTracking(True)

    def _configure_delegate(self) -> None:
        # Apply the custom row hover effect to instance
        self._hover_delegate = HoverRowDelegate(self, hover_color="#34495E")
        self.setItemDelegate(self._hover_delegate)
        self.entered.connect(lambda idx: self._hover_delegate.setHoverRow(idx.row()))


class ShuffleButton(IconButton):
    """Button for toggling shuffle mode on or off."""

    change_shuffle_mode_request  = pyqtSignal(ShuffleMode)

    def __init__(self, icon_path: Path = SHUFFLE_DISABLED_ICON_PATH):
        """Initialize ShuffleButton.

        Args:
            icon_path: Path to the shuffle icon file.
                       Defaults to 'shuffle disabled' icon.

        """
        super().__init__(icon_path=icon_path)
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
            SHUFFLE_DISABLED_ICON_PATH
            if shuffle_mode == ShuffleMode.OFF
            else SHUFFLE_ICON_PATH
        )
        self.setIcon(QIcon(str(icon)))


class RepeatButton(IconButton):
    """Button for cycling through repeat modes (off, repeat one, repeat all)."""

    change_repeat_mode_request  = pyqtSignal(RepeatMode)
    MODES: ClassVar[list[RepeatMode]] = list(RepeatMode)

    def __init__(self, icon_path: Path = REPEAT_DISABLED_ICON_PATH):
        """Initialize RepeatButton.

        Args:
            icon_path: Path to the repeat icon file.
                       Defaults to 'repeat disabled' icon.

        """
        super().__init__(icon_path=icon_path)
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
            icon = REPEAT_DISABLED_ICON_PATH
        elif repeat_mode == RepeatMode.ONE:
            icon = REPEAT_ONE_ICON_PATH
        else:
            icon = REPEAT_ICON_PATH

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

    def __init__(self, icon_path: Path = HIGH_VOLUME_ICON_PATH):
        """Initialize VolumeButton.

        Args:
            icon_path: Path to the icon file. Defaults to 'high-volume' icon.

        """
        super().__init__(icon_path=icon_path)
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
            icon = HIGH_VOLUME_ICON_PATH
        elif new_volume >= self.MEDIUM_BOUNDARY:
            icon = MEDIUM_VOLUME_ICON_PATH
        elif new_volume >= self.LOW_BOUNDARY:
            icon = LOW_VOLUME_ICON_PATH
        else:
            icon = MUTED_VOLUME_ICON_PATH

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
        label_width = self.fontMetrics().horizontalAdvance("100") + 4

        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
        self.setFixedWidth(label_width)

