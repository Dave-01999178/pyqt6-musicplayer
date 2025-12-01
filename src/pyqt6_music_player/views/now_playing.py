"""
This module provides UI components for displaying the current audio/song information such as title,
artist, and an album art.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout, QVBoxLayout

from pyqt6_music_player.config import ALBUM_ART_PLACEHOLDER
from pyqt6_music_player.models import DEFAULT_SONG, Song


# ================================================================================
# NOW PLAYING WIDGETS
# ================================================================================
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


# TODO: Consider using factory if label widgets remained static.
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


class NowPlayingDisplay(QWidget):
    """
    A QWidget container for widgets that displays current song information
    such as album art, song title, and artist label.
    """
    def __init__(self):
        """Initialize NowPlayingDisplay instance."""
        super().__init__()
        self.current_song = Song()  # Placeholder until 'select song' feature is implemented.

        self.album_art = AlbumArtLabel()
        self.song_title = AudioTitleLabel()
        self.artist_label = AudioArtistLabel()

        self._init_ui()

    def _init_ui(self):
        """Initializes the instance's internal widgets and layouts"""
        layout = QHBoxLayout()
        layout.addWidget(self.album_art)

        label_layout = QVBoxLayout()

        label_layout.addWidget(self.song_title)
        label_layout.addWidget(self.artist_label)

        layout.addLayout(label_layout)

        self.setLayout(layout)
