from pathlib import Path
from typing import ClassVar

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QPainter, QPaintEvent, QPixmap, QImage
from PyQt6.QtWidgets import QLabel

from pyqt6_music_player.core import ASSETS_PATH, IconButton, RepeatMode

# ==================== CONSTANTS ====================
ALBUM_ART_PLACEHOLDER = ASSETS_PATH / "default_art.png"
REPEAT_DISABLED_ICON = ASSETS_PATH / "repeat_icon_disabled.svg"
REPEAT_ICON = ASSETS_PATH / "repeat_icon.svg"
REPEAT_ONE_ICON = ASSETS_PATH / "repeat_one_icon.svg"
SHUFFLE_DISABLED_ICON = ASSETS_PATH / "shuffle_icon_disabled.svg"
SHUFFLE_ICON = ASSETS_PATH / "shuffle_icon.svg"
TRACK_METADATA_LABEL_SIZE = (100, 25)
SECONDARY_PLAYBACK_CONTROL_BTN_SIZE = (30, 30)
SECONDARY_PLAYBACK_CONTROL_BTN_ICON_SIZE = (15, 15)
SECONDARY_PLAYBACK_CONTROL_BTN_OBJ_NAME = "secondaryPlaybackControlBtn"


# ==================== WIDGETS ====================
class AlbumArtLabel(QLabel):
    """Custom QLabel for displaying track album art."""

    def __init__(self):
        super().__init__()
        # Setup
        self._configure_properties()
        self._init_ui()

    # -- Public methods --
    def update_image_display(self, image: QImage) -> None:
        """Display the given album art image, or the placeholder if null.

        Args:
            image: The album art to display. A null QImage (or one that
                failed to load) is treated as "no art" and renders the
                placeholder instead.

        """
        self._render_image(image)

    def reset_display(self) -> None:
        """Reset the display back to the placeholder image."""
        self._render_image(QImage())

    # -- Protected/internal methods --
    def _init_ui(self) -> None:
        # Set instance default album art placeholder
        self._render_image(QImage())

    def _configure_properties(self) -> None:
        # Configure instance properties
        self.setFixedSize(50, 50)
        self.setScaledContents(False)

    def _render_image(self, image: QImage) -> None:
        # Render placeholder image when the given QImage is null
        # (no art, or corrupted/unparseable art)
        pixmap = (
            QPixmap(str(ALBUM_ART_PLACEHOLDER))
            if image.isNull()
            else QPixmap.fromImage(image)
        )

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
            text: str = "",
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


class ShuffleButton(IconButton):
    """Button for toggling shuffle mode on or off."""

    change_shuffle_mode_request  = pyqtSignal(bool)

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
        self.change_shuffle_mode_request.emit(checked)

        self._update_icon(checked)

    def _update_icon(self, checked: bool) -> None:
        # Update icon based on the current shuffle mode
        icon = (SHUFFLE_DISABLED_ICON if checked else SHUFFLE_ICON)

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
