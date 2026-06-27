import logging
from pathlib import Path

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton

logger = logging.getLogger(__name__)


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
        super().__init__(text=button_text)
        self._icon_path = icon_path

        # Instance properties
        self._icon_size = icon_size
        self._widget_size = widget_size
        self._object_name = object_name

        # Setup
        self._configure_properties()

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
