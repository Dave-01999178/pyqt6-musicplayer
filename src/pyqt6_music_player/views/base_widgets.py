"""
This module provides reusable widgets for creating consistent UI components.
"""
from pathlib import Path

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QPushButton

from pyqt6_music_player.views.helpers import path_to_qicon
from pyqt6_music_player.config import SMALL_BUTTON, SMALL_ICON


# ================================================================================
# BASE ICON BUTTON
# ================================================================================
# TODO: Consider using dataclass or other containers if `__init__` arguments exceed 5
#  e.g. the class became complex or when extending class to include custom behaviour/logic etc.
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
