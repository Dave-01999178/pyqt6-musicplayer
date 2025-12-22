"""
This module provides reusable widgets for creating consistent UI components.
"""
from pathlib import Path

from PyQt6.QtCore import QSize, QTimer
from PyQt6.QtGui import QPaintEvent, QPainter
from PyQt6.QtWidgets import QPushButton, QLabel

from pyqt6_music_player.views.helpers import path_to_qicon
from pyqt6_music_player.config import SMALL_BUTTON, SMALL_ICON


# ================================================================================
# BASE ICON BUTTON
# ================================================================================
#
# --- Icon button ---
class IconButton(QPushButton):
    """
    A customizable QPushButton with fixed size and icon, and a configurable properties
    for icon-based buttons that require custom behavior or state.

    This class extends the QPushButton widget to provide a consistent and reusable button with
    options for a fixed icon and widget size, button text, icon size, and a custom object name for
    styling.
    """
    def __init__(
            self,
            icon_path: Path,
            icon_size: tuple[int, int] = SMALL_ICON,
            widget_size: tuple[int, int] = SMALL_BUTTON,
            button_text: str | None = None,
            object_name: str | None = None
    ) -> None:
        """
        Initializes IconButton instance.

        Args:
            icon_path: Path to the icon file.
            icon_size: ``(width, height)`` of the *icon* inside the button.
                       Defaults to ``(15, 15)``.
            widget_size: ``(width, height)`` of the whole button widget. Defaults to ``(30, 30)``.
            button_text: Optional text for the button. Defaults to ``None``.
            object_name: Qt object name – useful for QSS selectors. Defaults to ``None``.
        """
        super().__init__(text=button_text)
        self.icon_path = icon_path
        self.icon_size = icon_size
        self.widget_size = widget_size
        self.object_name = object_name

        self._configure_properties()

    def _configure_properties(self):
        """Configures the instance properties."""
        icon = path_to_qicon(self.icon_path)
        if icon is not None:
            self.setIcon(icon)
            self.setIconSize(QSize(*self.icon_size))

        self.setFixedSize(*self.widget_size)

        if self.object_name:
            self.setObjectName(self.object_name)


# --- Marquee Label ---
class MarqueeLabel(QLabel):
    def __init__(self, text: str | None = None):
        super().__init__(text=text)
        # Marquee settings.
        self._offset = 0  # Current horizontal offset.
        self._speed = 1  # Pixels per timer tick.
        self._gap = 20  # Space between repeated text instances.

        # Timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_offset)  # type: ignore

        self._timer.start(20)

    def _update_offset(self):
        # Compute the horizontal pixel width of the current text.
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

    def paintEvent(self, event: QPaintEvent):
        # Get the font metrics for the widget's current font and style.
        font_metrics = self.fontMetrics()

        # Compute the horizontal pixel width of the current text.
        text_width = font_metrics.horizontalAdvance(self.text())

        # If the current text fits, use default QLabel painting.
        if text_width <= self.width():
            super().paintEvent(event)  # Let QLabel paint itself to preserve default behaviour.
            return

        # Else, draw scrolling text.
        painter = QPainter(self)
        painter.setPen(self.palette().windowText().color())

        current_text = self.text()
        x = -self._offset  # Shift the text leftward.
        y = (self.height() + font_metrics.ascent()) // 2  # Vertically centers the text.

        # To create a seamless marquee effect when the text is wider than the widget:
        # - The first `drawText` renders the "leaving" instance (shifted left from the visible
        #   area).
        # - The second `drawText` renders the "entering" instance (positioned after the text, and
        #   gap).
        # Together, they produce a continuous looping scroll.
        painter.drawText(x, y, current_text)
        painter.drawText(x + text_width + self._gap, y, current_text)

    # Note: Override to reset animation when text changes.
    # This prevents mid-word jumps or weird starting positions.
    def setText(self, text: str):
        super().setText(text)
        self._offset = 0


# ================================================================================
# FACTORY
# ================================================================================
#
# Factory for creating static/stateless buttons.
class IconButtonFactory:
    """Reusable factory class for creating static IconButtons."""
    def __init__(
            self,
            icon_path: Path,
            *,
            icon_size: tuple[int, int] = SMALL_ICON,
            widget_size: tuple[int, int] = SMALL_BUTTON,
            button_text: str | None = None,
            object_name: str | None = None
    ):
        """
        A factory for creating static/stateless buttons.

        Args:
            icon_path: Path to the icon file.
            icon_size: ``(width, height)`` of the *icon* inside the button.
                       Defaults to ``(15, 15)``.
            widget_size: ``(width, height)`` of the whole button widget. Defaults to ``(30, 30)``.
            button_text: Optional text for the button. Defaults to ``None``.
            object_name: Qt object name – useful for QSS selectors. Defaults to ``None``.
        """
        self.icon_path = icon_path
        self.icon_size = icon_size
        self.widget_size = widget_size
        self.button_text = button_text
        self.object_name = object_name

    def __call__(self,) -> IconButton:
        return IconButton(
            icon_path=self.icon_path,
            icon_size=self.icon_size,
            widget_size=self.widget_size,
            button_text=self.button_text,
            object_name=self.object_name
        )
