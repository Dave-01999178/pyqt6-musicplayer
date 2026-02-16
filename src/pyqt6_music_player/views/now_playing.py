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
# ----- WIDGETS -----
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

    # --- Private methods ---
    def _init_ui(self):
        """Initialize and set default album art."""
        self._set_image(ALBUM_ART_PLACEHOLDER)

    def _configure_properties(self):
        """Configure instance properties."""
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

    # --- Public methods ---
    def set_image(self, image) -> None:
        if image is None:
            return

        self._set_image(image)


class AudioTitleLabel(MarqueeLabel):
    """A QLabel widget for displaying the current audio title."""

    def __init__(self, text: str = DEFAULT_TRACK.title):
        """Initialize AudioTitleLabel.

        Args:
            text: The text to display. The default text is "Song Title".

        """
        super().__init__(text)
        self._configure_properties()

    def _configure_properties(self):
        """Configure instance properties."""
        self.setFixedWidth(100)
        self.setObjectName("audioTitleLabel")


class AudioArtistLabel(MarqueeLabel):
    """A QLabel widget for displaying the current audio artist."""

    def __init__(self, text: str = DEFAULT_TRACK.artist):
        """Initialize AudioArtistLabel.

        Args:
            text: The text to display. The default text is "Song Artist".

        """
        super().__init__(text=text)
        self._configure_properties()

    def _configure_properties(self):
        """Configure instance properties."""
        self.setFixedWidth(100)
        self.setObjectName("audioArtistLabel")


# ----- COMPONENT -----
class NowPlayingDisplay(QWidget):
    """A QWidget container for widgets that displays current song information.

    This includes album art, song title, and artist label.
    """

    def __init__(self, playback_viewmodel: PlaybackViewModel):
        """Initialize NowPlayingDisplay."""
        super().__init__()
        # Viewmodel
        self._viewmodel = playback_viewmodel

        # Widget
        self.album_art = AlbumArtLabel()
        self.title_label = AudioTitleLabel()
        self.artist_label = AudioArtistLabel()

        self._init_ui()

        self._viewmodel.track_loaded.connect(self._on_track_loaded)

    # --- Private methods ---
    def _init_ui(self):
        """Initialize instance internal widgets and layouts."""
        main_layout_horizontal = QHBoxLayout()

        # Left: Album art widget
        main_layout_horizontal.addWidget(self.album_art)

        # Right: Metadata label section
        right_section_vertical = QVBoxLayout()

        right_section_vertical.addWidget(self.title_label)
        right_section_vertical.addWidget(self.artist_label)

        main_layout_horizontal.addLayout(right_section_vertical)

        self.setLayout(main_layout_horizontal)

    @pyqtSlot(str, str)
    def _on_track_loaded(self, track_title: str, track_artist: str) -> None:
        """Display loaded track metadata in UI.

        Args:
            track_title: The track title.
            track_artist: The track artist.

        """
        # Update the UI so users can see the loaded track information.
        self.title_label.setText(track_title)
        self.artist_label.setText(track_artist)
