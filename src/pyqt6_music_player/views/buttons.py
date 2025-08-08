from pathlib import Path
from typing import Tuple

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton

from pyqt6_music_player.config import (
    BUTTON_SIZE_LARGE,
    PLAY_ICON_PATH,
    PLAY_ICON_SIZE,
)


class IconButton(QPushButton):
    def __init__(
            self,
            icon_path_normal: Path,
            size: Tuple[int, int],
            icon_path_pressed: Path = None
    ):
        super().__init__()
        self.icon_normal = QIcon(str(icon_path_normal))
        self.icon_pressed = QIcon(str(icon_path_pressed)) if icon_path_pressed else None

        self.setFixedSize(*size)
        self.setIcon(self.icon_normal)

        if icon_path_pressed:
            self.pressed.connect(self.on_pressed)
            self.released.connect(self.on_released)

    def on_pressed(self):
        if self.icon_pressed:
            self.setIcon(self.icon_pressed)

    def on_released(self):
        if self.icon_pressed:
            self.setIcon(self.icon_normal)


class PlayPauseButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.setFixedSize(*BUTTON_SIZE_LARGE)
        self.setIconSize(QSize(*PLAY_ICON_SIZE))
        self.setObjectName("playBtn")
        self.setIcon(QIcon(str(PLAY_ICON_PATH)))
