"""
Custom PyQt6 reusable widgets for creating consistent UI components.

This module provides a collection of base widgets, including a customizable icon button,
a base label, and a base slider, designed for reuse across various UI projects.
"""
from pathlib import Path
from typing import Tuple

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton, QLabel, QSlider


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
            widget_size: Tuple[int, int],
            button_text: str | None = None,
            icon_size: Tuple[int, int] | None = None,
            object_name: str | None = None
    ):
        """Initializes a new IconButton instance.

        Args:
            icon_path: File system path to the icon image.
            widget_size: Width and height of the widget.
            button_text Text displayed on the button. Defaults to None.
            icon_size: Width and height of the button icon. Defaults to None.
            object_name: Widget object name, useful for QSS styling. Defaults to None.
        """
        super().__init__(text=button_text)
        self._icon = self._to_qicon(icon_path)
        self._widget_size = widget_size
        self._icon_size = icon_size
        self._object_name = object_name

        self._configure_properties()

    def _configure_properties(self):
        """Configures the icon button's properties."""
        self.setFixedSize(*self._widget_size)
        self.setIcon(self._icon)

        if self._icon_size:
            self.setIconSize(QSize(*self._icon_size))

        if self._object_name:
            self.setObjectName(self._object_name)

    @staticmethod
    def _to_qicon(path: Path | str | QIcon) -> QIcon:
        """
        Convert a file path or QIcon into a QIcon instance.

        Args:
            path: The file path to the icon image or an existing QIcon instance.

        Returns:
            QIcon: A QIcon object created from the given path or returned directly if
            the input is already a QIcon.
        """
        # If the `path` is already a QIcon, return it.
        if isinstance(path, QIcon):
            return path

        return QIcon(str(path))


class BaseLabel(QLabel):
    """
    A customizable QLabel with fixed text and configurable properties.

    This class extends the QLabel widget to provide a consistent and reusable label with options
    for a fixed text string, a custom object name for styling, and text alignment.
    """
    def __init__(
            self,
            label_text: str,
            object_name: str | None = None,
            alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft
    ):
        """
        Initializes a new BaseLabel instance.

        Args:
            label_text: The text to display on the label.
            object_name: An optional name for the widget. This is useful for applying specific
            styles using QSS (Qt Style Sheets).
            alignment: An optional flag to specify the text alignment within the label.
            Defaults to Qt.AlignmentFlag.AlignLeft.
        """
        super().__init__(text=label_text)
        self.object_name = object_name
        self.widget_alignment = alignment

        self._configure_properties()

    def _configure_properties(self):
        """Configures the label's properties"""
        if self.object_name:
            self.setObjectName(self.object_name)

        self.setAlignment(self.widget_alignment)


class BaseSlider(QSlider):
    def __init__(self):
        super().__init__()
