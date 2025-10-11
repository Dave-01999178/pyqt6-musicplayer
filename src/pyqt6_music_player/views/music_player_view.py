"""
Main application view for the PyQt6 Music Player.

This module defines the `MusicPlayerView`, the central container widget
that holds all major UI components (playlist, player bar, controls).
"""
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from src.pyqt6_music_player.views import PlayerBarFrame, PlaylistSectionFrame

from src.pyqt6_music_player.config import APP_DEFAULT_SIZE, APP_TITLE


class MusicPlayerSignals(QObject):
    """
    Container for all high-level signals of the music player view.

    Signals are grouped into nested classes by feature domain
    (volume, playback progress, playback controls).
    """
    class PlaylistManager(QObject):
        add_song_button_clicked = pyqtSignal()
        remove_song_button_clicked = pyqtSignal()
        load_song_button_clicked = pyqtSignal()

    class Volume(QObject):
        """Signals related to volume control (mute button and slider)."""
        button_clicked = pyqtSignal(bool)
        slider_changed = pyqtSignal(int)

    class PlaybackProgress(QObject):
        """Signals related to playback progress (timeline slider)."""
        slider_changed = pyqtSignal(int)

    class PlaybackControls(QObject):
        """Signals related to playback control buttons."""
        previous_clicked = pyqtSignal()
        play_pause_clicked = pyqtSignal()
        next_clicked = pyqtSignal()

    def __init__(self):
        """Initialize grouped signal containers."""
        super().__init__()
        self.playlist_manager = self.PlaylistManager()
        self.volume = self.Volume()
        self.playback_progress = self.PlaybackProgress()
        self.playback_control = self.PlaybackControls()


# ------------------------------ Main view ------------------------------

class MusicPlayerView(QWidget):
    """
    The main application view for the music player.

    This widget arranges and manages the primary UI components:

    - `PlaylistSectionFrame` for the playlist view.
    - `PlayerBarFrame` for playback controls, progress, and volume.

    It also forwards all widget-level signals into a higher-level
    `MusicPlayerSignals` object.
    """
    def __init__(self, state):
        """
        Initialize the main music player view.

        Args:
            state: Application state object (MusicPlayerState).
        """
        super().__init__()
        self.state = state
        self.playlist_frame = PlaylistSectionFrame(state)
        self.player_bar_frame = PlayerBarFrame(state)
        self.signals = MusicPlayerSignals()

        self._init_ui()
        self._connect_signals()

    @property
    def playlist_manager_signals(self):
        return self.signals.playlist_manager

    @property
    def playback_progress_signals(self):
        """Return the signal group for playback progress."""
        return self.signals.playback_progress

    @property
    def playback_control_signals(self):
        """Return the signal group for playback controls."""
        return self.signals.playback_control

    @property
    def volume_signals(self):
        """Return the signal group for volume control."""
        return self.signals.volume

    def _init_ui(self):
        """Configure window properties and initialize layouts."""
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(*APP_DEFAULT_SIZE)
        self.resize(*APP_DEFAULT_SIZE)

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#07070b"))  # Old color #000213

        self.setPalette(palette)

        main_layout = QVBoxLayout()

        main_layout.addWidget(self.playlist_frame, 1)
        main_layout.addWidget(self.player_bar_frame, 0)

        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        self.setLayout(main_layout)

    def _connect_signals(self):
        """Connect low-level widget signals to higher-level grouped signals."""
        # Playlist manager
        self.playlist_frame.add_song_button_clicked.connect(
            self.playlist_manager_signals.add_song_button_clicked
        )

        # Playback progress widget signals
        self.player_bar_frame.progress_bar_slider_changed.connect(
            self.playback_progress_signals.slider_changed
        )

        # Playback control widget signals
        self.player_bar_frame.previous_button_clicked.connect(
            self.playback_control_signals.previous_clicked
        )
        self.player_bar_frame.play_pause_button_clicked.connect(
            self.playback_control_signals.play_pause_clicked
        )
        self.player_bar_frame.next_button_clicked.connect(
            self.playback_control_signals.next_clicked
        )

        # Volume widget signals
        self.player_bar_frame.volume_button_clicked.connect(self.volume_signals.button_clicked)
        self.player_bar_frame.volume_slider_changed.connect(self.volume_signals.slider_changed)
