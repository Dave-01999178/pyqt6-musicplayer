from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSlider

from pyqt6_music_player.config import VOLUME_DEFAULT, VOLUME_RANGE


class PlaybackProgressBar(QSlider):
    def __init__(self):
        super().__init__(Qt.Orientation.Horizontal)


class VolumeSlider(QSlider):
    def __init__(self, orientation=Qt.Orientation.Vertical):
        super().__init__(orientation)
        self.setRange(*VOLUME_RANGE)
        self.setValue(VOLUME_DEFAULT)
