"""Now playing UI components.

This module defines widgets responsible for showing current track information
including an album art, track title, and artist label.
"""
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from pyqt6_music_player.config import ALBUM_ART_PLACEHOLDER
from pyqt6_music_player.models import DEFAULT_TRACK
from pyqt6_music_player.view_models import PlaybackViewModel
from pyqt6_music_player.views import MarqueeLabel


# ================================================================================
# NOW PLAYING
# ================================================================================
#
# --- WIDGETS ---
class AlbumArtLabel(QLabel):
    """A QLabel widget for displaying album art.

    This label is configured with a fixed size and displays a scaled QPixmap
    of the album art, with a default image.
    """

    def __init__(self):
        """Initialize AlbumArtLabel."""
        super().__init__()

        self._configure_properties()
        self._init_ui()

    def _init_ui(self):
        """Initialize album art pixmap."""
        self._set_image(ALBUM_ART_PLACEHOLDER)

    def _configure_properties(self):
        self.setFixedSize(75, 75)
        self.setScaledContents(False)

    def _set_image(self, image):
        pixmap = QPixmap(str(image))
        scaled = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.setPixmap(scaled)

    def set_image(self, image) -> None:
        """Set instance image."""
        if image is None:
            return

        self._set_image(image)


class AudioTitleLabel(MarqueeLabel):
    """A QLabel widget for displaying the current audio title.

    The default text is 'Song Title'.
    """

    def __init__(self, text: str = DEFAULT_TRACK.title):
        """Initialize AudioTitleLabel."""
        super().__init__(text)

        self.setFixedWidth(100)
        self.setObjectName("audioTitleLabel")


class AudioArtistLabel(MarqueeLabel):
    """A QLabel widget for displaying the current audio artist.

    The default text is 'Song Artist'.
    """

    def __init__(self, text: str = DEFAULT_TRACK.artist):
        """Initialize AudioArtistLabel."""
        super().__init__(text=text)

        self.setFixedWidth(100)
        self.setObjectName("audioArtistLabel")


# --- COMPONENT ---
class NowPlayingDisplay(QWidget):
    """A QWidget container for widgets that displays current song information.

    This includes album art, song title, and artist label.
    """

    def __init__(self, playback_viewmodel: PlaybackViewModel):
        """Initialize NowPlayingDisplay."""
        super().__init__()
        # Playback viewmodel
        self._viewmodel = playback_viewmodel

        # Now playing widgets
        self.album_art = AlbumArtLabel()
        self.title_label = AudioTitleLabel()
        self.artist_label = AudioArtistLabel()

        self._init_ui()
        self._viewmodel.track_info.connect(self._on_playback_start)

    def _init_ui(self):
        """Initialize the instance's internal widgets and layouts."""
        # --- Left section: Album art ---
        layout = QHBoxLayout()

        layout.addWidget(self.album_art)

        # --- Right section: Song title and artist label ---
        label_layout = QVBoxLayout()

        label_layout.addWidget(self.title_label)
        label_layout.addWidget(self.artist_label)

        layout.addLayout(label_layout)

        self.setLayout(layout)

    @pyqtSlot(str, str)
    def _on_playback_start(self, song_title: str, song_artist: str):
        self.title_label.setText(song_title)
        self.artist_label.setText(song_artist)
