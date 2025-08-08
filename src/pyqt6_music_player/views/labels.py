from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel

from pyqt6_music_player.config import DEFAULT_ALBUM_ART_PATH


class AlbumArtLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 300)
        self.setScaledContents(False)

        pixmap = QPixmap(str(DEFAULT_ALBUM_ART_PATH))
        scaled = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.setPixmap(scaled)


class SongTitleLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setText("Now Playing: Song Title")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class PerformerLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setText("By: Song Artist")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class ElapsedTimeLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setText("0:00")  # Placeholder
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)


class TotalDurationLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setText("2:30")  # Placeholder
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
