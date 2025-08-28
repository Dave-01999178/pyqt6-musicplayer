"""
Widgets for displaying song metadata.

This module provides UI components for displaying a song's title, artist,
and album art within the music player application.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel

from pyqt6_music_player.config import DEFAULT_ALBUM_ART_PATH
from pyqt6_music_player.models.music_player_state import MetadataState
from pyqt6_music_player.views.base_widgets import BaseLabel


class AlbumArtLabel(QLabel):
    """
    A label widget for displaying album art.

    This label is configured with a fixed size and displays a scaled QPixmap
    of the album art, with a default image.
    """
    def __init__(self):
        """Initializes the album art label."""
        super().__init__()

        self._configure_properties()
        self._init_ui()

    def _init_ui(self):
        """Sets the initial album art pixmap and scales it to fit."""
        pixmap = QPixmap(str(DEFAULT_ALBUM_ART_PATH))
        scaled = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.setPixmap(scaled)

    def _configure_properties(self):
        """Configures the label's properties"""
        self.setFixedSize(60, 60)
        self.setScaledContents(False)


class SongTitleLabel(BaseLabel):
    """
    A label widget for displaying the current song's title.
    """
    def __init__(self, metadata_state: MetadataState):
        """
        Initializes the song title label.

        Args:
            metadata_state: The music player metadata state.
        """
        super().__init__(
            label_text=f"Now Playing: {metadata_state.song_title}",
            object_name="songTitleLabel"
        )


class ArtistLabel(BaseLabel):
    """A label widget for displaying the current song's artist."""
    def __init__(self, metadata_state: MetadataState):
        """
        Initializes the artist label.

        Args:
            metadata_state: The music player metadata state.
        """
        super().__init__(
            label_text=f"By: {metadata_state.song_artist}",
            object_name="artistLabel"
        )
