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

from pyqt6_music_player.config import (
    ALBUM_ART_PLACEHOLDER,
    HIGH_VOLUME_ICON_PATH,
    LOW_VOLUME_ICON_PATH,
    MEDIUM_VOLUME_ICON_PATH,
    METADATA_LABEL_SIZE,
    MUTED_VOLUME_ICON_PATH,
    SMALL_BUTTON,
    SMALL_ICON,
)
from pyqt6_music_player.constants import MAX_VOLUME, MIN_VOLUME, VolumeLevel


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
        self._icon_path = icon_path
        self._icon_size = icon_size
        self._widget_size = widget_size
        self._object_name = object_name

        self._configure_properties()

    # --- Private method ---
    def _configure_properties(self):
        """Configure instance properties."""
        icon = self.path_to_qicon(self._icon_path)

        self.setIcon(icon)
        self.setIconSize(QSize(*self._icon_size))

        self.setFixedSize(*self._widget_size)

        if self._object_name:
            self.setObjectName(self._object_name)

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
        self._configure_properties()
        self._init_ui()

    # --- Private methods ---
    def _init_ui(self):
        """Initialize and set instance default album art."""
        self._set_image(ALBUM_ART_PLACEHOLDER)

    def _configure_properties(self):
        """Configure instance properties."""
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

    # --- Public methods ---
    def set_image(self, image) -> None:
        if image is None:
            return

        self._set_image(image)


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

        """
        super().__init__(text=text)
        # Instance configuration
        self._widget_size = widget_size
        self._object_name = object_name

        self._configure_properties()

        # Marquee configuration
        self._offset = 0  # Current horizontal offset.
        self._speed = 1  # Pixels per timer tick.
        self._gap = 20  # Space between repeated text instances.

        # Timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_offset)  # type: ignore

        self._timer.start(20)

    # --- Private methods ---
    def _configure_properties(self):
        self.setFixedSize(*self._widget_size)
        self.setObjectName(self._object_name)

    def _update_offset(self):
        """Compute and update text offset based on the current text position."""
        text_width = self.fontMetrics().horizontalAdvance(self.text())

        # If the current text fits, do nothing.
        if text_width <= self.width():
            return

        cycle_width = (text_width + self._gap)

        self._offset = (self._offset + self._speed) % cycle_width

        # Reset offset after one full marquee cycle (text + gap) has scrolled past
        # for seamless animation.
        if self._offset > text_width + self._gap:
            self._offset = 0

        self.update()

    # --- QLabel methods ---
    def paintEvent(self, event: QPaintEvent | None):
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
        x = -self._offset  # Shift the text leftward.
        y = (self.height() + font_metrics.ascent()) // 2  # Vertically centers the text.

        # To create a seamless marquee effect when the text is wider than the widget:
        # - The first `drawText` renders the "leaving" instance
        #   (shifted left from the visible area).
        # - The second `drawText` renders the "entering" instance
        #  (positioned after the text, and gap).
        # Together, they produce a continuous looping scroll.
        painter.drawText(x, y, current_text)
        painter.drawText(x + text_width + self._gap, y, current_text)

    # Note: Override to reset animation when text changes.
    # This prevents mid-word jumps and weird starting positions.
    def setText(self, text: str | None):
        super().setText(text)
        self._offset = 0


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

    def _init_icons(self):
        """Initialize volume icons."""
        self.volume_icons = {
            VolumeLevel.HIGH: self.path_to_qicon(HIGH_VOLUME_ICON_PATH),
            VolumeLevel.MEDIUM: self.path_to_qicon(MEDIUM_VOLUME_ICON_PATH),
            VolumeLevel.LOW: self.path_to_qicon(LOW_VOLUME_ICON_PATH),
            VolumeLevel.MUTE: self.path_to_qicon(MUTED_VOLUME_ICON_PATH),
        }

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

        # Avoid unnecessary UI updates by skipping `setIcon` calls if the new,
        # and current icon are the same.
        if icon.cacheKey() == self.icon().cacheKey():
            return

        self.setIcon(icon)


# ----- Volume label -----
class VolumeLabel(QLabel):
    """QLabel widget for displaying the current volume level.

    This label shows the volume as a number (0-100).
    """

    def __init__(self):
        """Initialize VolumeLabel."""
        super().__init__()

        self._configure_properties()

    def _configure_properties(self):
        """Configure instance's properties."""
        # This fixes the weird behaviour when the text is '0'.
        label_width = self.fontMetrics().horizontalAdvance("100") + 4

        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
        self.setFixedWidth(label_width)
