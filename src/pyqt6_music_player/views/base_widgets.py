"""
This module provides reusable widgets for creating consistent UI components.
"""
from pathlib import Path

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton

from pyqt6_music_player.config import (
    DEFAULT_ICON_BUTTON_SIZE,
    DEFAULT_ICON_SIZE
)


class IconButton(QPushButton):
    """
    A customizable QPushButton with fixed size and icon, and a configurable properties.

    This class extends the QPushButton widget to provide a consistent and reusable button with
    options for a fixed icon and widget size, button text, icon size, and a custom object name for
    styling.
    """
    def __init__(
            self,
            icon_path: Path,
            icon_size: tuple[int, int] = DEFAULT_ICON_SIZE,
            widget_size: tuple[int, int] = DEFAULT_ICON_BUTTON_SIZE,
            button_text: str | None = None,
            object_name: str | None = None
    ) -> None:
        """
        Initializes IconButton instance.

        Args:
            icon_path: Icon image path.
            icon_size: Width and height of the icon.
                       Defaults to `DEFAULT_ICON_SIZE` (15, 15).
            widget_size: Width and height of the widget.
                         Defaults to `DEFAULT_ICON_BUTTON_SIZE` (30, 30).
            button_text: Text displayed on the button. Defaults to None.
            object_name: Widget object name, useful for QSS styling. Defaults to None.
        """
        super().__init__(text=button_text)
        self.icon_path = icon_path
        self.icon_size = icon_size
        self.widget_size = widget_size
        self.object_name = object_name

        self._configure_properties()

    def _configure_properties(self):
        """Configures the instance properties."""
        self.setIcon(QIcon(str(self.icon_path)))
        self.setIconSize(QSize(*self.icon_size))

        self.setFixedSize(*self.widget_size)

        if self.object_name:
            self.setObjectName(self.object_name)

    @staticmethod
    def to_qicon(icon_path: Path) -> QIcon:
        """
        Converts icon's path into a QIcon instance.

        Args:
            icon_path: Icon image path.

        Returns:
            A QICon instance.
        """
        return QIcon(str(icon_path))
