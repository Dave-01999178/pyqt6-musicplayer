"""Base PyQt6 widgets and widget factories used throughout the application.

This module provides reusable UI building blocks such as icon-based buttons
and scrolling text labels, along with lightweight factories for creating
preconfigured, stateless widgets with consistent sizing and styling.
"""
import logging
from pathlib import Path

from PyQt6.QtCore import QSize, Qt, QTimer
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
    HIGH_VOLUME_ICON_PATH,
    LOW_VOLUME_ICON_PATH,
    MAX_VOLUME,
    MEDIUM_VOLUME_ICON_PATH,
    METADATA_LABEL_SIZE,
    MIN_VOLUME,
    MUTED_VOLUME_ICON_PATH,
    SMALL_BUTTON,
    SMALL_ICON,
    VolumeLevel,
)


# ================================================================================
# BASE WIDGETS
# ================================================================================
#
# ----- Icon button -----
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
            icon_size: tuple[int, int] = SMALL_ICON,
            widget_size: tuple[int, int] = SMALL_BUTTON,
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
        # Icon
        self._icon_path = icon_path

        # Properties
        self._icon_size = icon_size
        self._widget_size = widget_size
        self._object_name = object_name

        # Setup
        self._configure_properties()

    # --- Public methods ---
    @staticmethod
    def path_to_qicon(icon_path: str | Path) -> QIcon:
        """Convert an icon image into QIcon instance.

        Args:
            icon_path: Path to the icon file.

        Returns:
            QIcon: A QIcon instance.

        """
        try:
            return QIcon(str(icon_path))
        except Exception as e:
            logging.error("Icon path: %s not found, %s", icon_path, e)

            return QIcon()

    # --- Protected/internal methods ---
    def _configure_properties(self):
        icon = self.path_to_qicon(self._icon_path)

        self.setIcon(icon)
        self.setIconSize(QSize(*self._icon_size))

        self.setFixedSize(*self._widget_size)

        if self._object_name:
            self.setObjectName(self._object_name)


# ================================================================================
# CUSTOM WIDGETS
# ================================================================================
#
# ----- Album art -----
class AlbumArtLabel(QLabel):
    """QLabel subclass for displaying album art.

    This label widget is configured with a fixed size, and a default image.
    """

    def __init__(self):
        """Initialize AlbumArtLabel."""
        super().__init__()
        # Setup
        self._configure_properties()
        self._init_ui()

    # --- Public methods ---
    def set_image(self, image) -> None:
        if image is None:
            return

        self._set_image(image)

    # --- Protected/internal methods ---
    def _init_ui(self):
        # Set instance default album art placeholder
        self._set_image(ALBUM_ART_PLACEHOLDER)

    def _configure_properties(self):
        self.setFixedSize(75, 75)
        self.setScaledContents(False)

    def _set_image(self, image):
        pixmap = QPixmap(str(image))
        scaled = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.setPixmap(scaled)


# ----- Marquee Label -----
class MarqueeLabel(QLabel):
    """Custom QLabel for displaying track metadata, and to handle text spills."""

    def __init__(
            self,
            text: str,
            *,
            widget_size: tuple[int, int] = METADATA_LABEL_SIZE,
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

        # Marquee configuration
        self._offset = 0  # Current horizontal offset
        self._speed = 1  # Pixels per timer tick
        self._gap = 20  # Space between repeated text instances

        # Animation timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_offset)  # type: ignore

        self._timer.start(20)

    # --- Public methods (QLabel) ---
    def paintEvent(self, event: QPaintEvent | None):
        # Custom paint event for scrolling text effect
        font_metrics = self.fontMetrics()
        text_width = font_metrics.horizontalAdvance(self.text())

        # If the current text fits, let QLabel paint itself
        # to preserve default behaviour (default painting).
        if text_width <= self.width():
            super().paintEvent(event)
            return

        # Else, draw scrolling text.
        painter = QPainter(self)
        painter.setPen(self.palette().windowText().color())

        current_text = self.text()
        x = -self._offset  # Shifts the text leftward.
        y = (self.height() + font_metrics.ascent()) // 2  # Vertically centers the text.

        # Create a seamless marquee effect when the text is wider than the widget:
        # - The first `drawText` renders the "leaving" text
        #   (shifted left from the visible area).
        # - The second `drawText` renders the "entering" text
        #  (positioned after the text, and gap).
        # Together, they produce a continuous looping scroll.
        painter.drawText(x, y, current_text)
        painter.drawText(x + text_width + self._gap, y, current_text)

    def setText(self, text: str | None):
        super().setText(text)  # Default behavior

        # Reset offset when text changes to avoid mid-word jumps
        # and weird starting positions.
        self._offset = 0

    # --- Protected/internal methods ---
    def _configure_properties(self):
        self.setFixedSize(*self._widget_size)
        self.setObjectName(self._object_name)

    def _update_offset(self):
        # Compute and update text offset based on the current text position.
        text_width = self.fontMetrics().horizontalAdvance(self.text())
        cycle_width = (text_width + self._gap)

        # If the current text fits, do nothing.
        if text_width <= self.width():
            return

        # Add '% cycle_width' to the offset formula to avoid the noticeable jump
        # when the text resets.
        self._offset = (self._offset + self._speed) % cycle_width

        # Reset offset after one full marquee cycle (text + gap) has scrolled past
        # for seamless animation.
        if self._offset > text_width + self._gap:
            self._offset = 0

        self.update()


# ----- PLAYLIST TABLE AND ROW HOVER EFFECTS -----
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

    # --- Public methods (QStyledItemDelegate) ---
    def setHoverRow(self, row: int):
        # Do work only if the hovered row actually changed
        if row != self._hover_row:
            self._hover_row = row

            # Ask the table (parent) to repaint its viewport (the display area)
            # so the hover effect is immediately visible.
            #
            # Without this, Qt wouldn't know it needs to redraw the cells
            # when the mouse moves.
            if self._parent:
                self._parent.viewport().update()

    def paint(self, painter, option, index):
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
    def __init__(self):
        """Initialize PlaylistWidget."""
        super().__init__()
        # Setup
        self._configure_properties()
        self._configure_viewport()
        self._configure_delegate()

    # --- Public method (QTableView) ---
    def leaveEvent(self, e):
        """QTableView leave event."""
        self._hover_delegate.setHoverRow(-1)  # Reset the highlighted row
        super().leaveEvent(e)

    # --- Protected/internal methods ---
    def _configure_properties(self):
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
        # Enable widget and viewport (the display area) mouse tracking
        self._viewport = self.viewport()
        if self._viewport is not None:
            self._viewport.setMouseTracking(True)

        self.setMouseTracking(True)

    def _configure_delegate(self):
        # Apply the custom row hover effect to instance
        self._hover_delegate = HoverRowDelegate(self, hover_color="#34495E")
        self.setItemDelegate(self._hover_delegate)
        self.entered.connect(lambda idx: self._hover_delegate.setHoverRow(idx.row()))


# ----- Volume button -----
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
        self.volume_icons: dict[VolumeLevel, QIcon] = {}

        self._init_icons()
        self.setCheckable(True)

    # --- Public methods ---
    def update_icon(self, new_volume: int) -> None:
        """Update instance icon based on the new volume's current level.

        Args:
            new_volume: The new volume.

        """
        if not (MIN_VOLUME <= new_volume <= MAX_VOLUME):
            raise ValueError(f"New volume: {new_volume} is out of range.")

        if new_volume >= self.HIGH_BOUNDARY:
            icon = self.volume_icons[VolumeLevel.HIGH]
        elif new_volume >= self.MEDIUM_BOUNDARY:
            icon = self.volume_icons[VolumeLevel.MEDIUM]
        elif new_volume >= self.LOW_BOUNDARY:
            icon = self.volume_icons[VolumeLevel.LOW]
        else:
            icon = self.volume_icons[VolumeLevel.MUTE]

        # Update icon only if it is new
        if icon.cacheKey() == self.icon().cacheKey():
            return

        self.setIcon(icon)

    # --- Protected/internal methods ---
    def _init_icons(self):
        # Initialize and store volume icons
        self.volume_icons = {
            VolumeLevel.HIGH: self.path_to_qicon(HIGH_VOLUME_ICON_PATH),
            VolumeLevel.MEDIUM: self.path_to_qicon(MEDIUM_VOLUME_ICON_PATH),
            VolumeLevel.LOW: self.path_to_qicon(LOW_VOLUME_ICON_PATH),
            VolumeLevel.MUTE: self.path_to_qicon(MUTED_VOLUME_ICON_PATH),
        }


# ----- Volume label -----
class VolumeLabel(QLabel):
    """QLabel widget for displaying the current volume level.

    This label shows the volume as a number (0-100).
    """

    def __init__(self):
        """Initialize VolumeLabel."""
        super().__init__()

        self._configure_properties()

    # --- Protected/internal methods ---
    def _configure_properties(self):
        # Set the instance width to the length of "100" + 4 character spaces
        # to center the text and avoid the weird behaviour when the text is "0".
        label_width = self.fontMetrics().horizontalAdvance("100") + 4

        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
        self.setFixedWidth(label_width)
