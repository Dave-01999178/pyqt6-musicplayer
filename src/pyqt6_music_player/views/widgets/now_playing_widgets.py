"""
This module provides UI components for displaying the current audio/song information such as title,
artist, and an album art.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel

from pyqt6_music_player.config import ALBUM_ART_PLACEHOLDER
from pyqt6_music_player.models import DEFAULT_SONG


class AlbumArtLabel(QLabel):
    """
    A QLabel widget for displaying album art.

    This label is configured with a fixed size and displays a scaled QPixmap
    of the album art, with a default image.
    """
    def __init__(self):
        """Initializes AlbumArtLabel instance."""
        super().__init__()

        self._configure_properties()
        self._init_ui()

    def _set_image(self, image):
        pixmap = QPixmap(str(image))
        scaled = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.setPixmap(scaled)

    def _configure_properties(self):
        """Configures the instance's properties"""
        self.setFixedSize(70, 70)
        self.setScaledContents(False)

    def _init_ui(self):
        """Initializes album art pixmap and scales it to fit."""
        self._set_image(ALBUM_ART_PLACEHOLDER)

    def update_image(self, image):
        if image is None:
            return None

        self._set_image(image)


# TODO: Consider using factory if QLabels remain static.
class AudioTitleLabel(QLabel):
    """
    A QLabel widget for displaying the current audio title. The default text is 'Song Title'.
    """
    def __init__(self):
        """Initializes AudioTitleLabel instance."""
        super().__init__(
            text=DEFAULT_SONG.title,
        )

        self.setObjectName("audioTitleLabel")


class AudioArtistLabel(QLabel):
    """
    A QLabel widget for displaying the current audio artist. The default text is 'Song Artist'.
    """
    def __init__(self):
        """Initializes AudioArtistLabel instance."""
        super().__init__(
            text=DEFAULT_SONG.artist,
        )

        self.setObjectName("audioArtistLabel")
