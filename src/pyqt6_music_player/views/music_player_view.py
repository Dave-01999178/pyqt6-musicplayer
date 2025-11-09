"""
Main application view for the PyQt6 Music Player.

This module defines the `MusicPlayerView`, the central container widget
that holds all major UI components (playlist, player bar, controls).
"""
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPalette
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QWidget

from pyqt6_music_player.config import (
    APP_DEFAULT_SIZE,
    APP_TITLE,
    MUSIC_PLAYER_ICON_PATH
)
from pyqt6_music_player.models import PlaylistModel
from pyqt6_music_player.views import (
    NowPlayingDisplay,
    PlaybackControls,
    PlaybackProgress,
    PlaylistDisplay,
    PlaylistManager,
    VolumeControls,
)


# ================================================================================
# MAIN VIEW
# ================================================================================
class MusicPlayerView(QWidget):
    def __init__(self, state):
        """
        Initialize the main music player view.
        """
        super().__init__()
        self.state = state
        self.playlist_manager_view = PlaylistManagerView()
        self.playlist_view = PlaylistView(state)
        self.player_bar_view = PlayerbarView()

        self._configure_properties()
        self._init_ui()

    def _configure_properties(self):
        """Configures the instance's properties"""
        self.resize(*APP_DEFAULT_SIZE)
        self.setMinimumSize(*APP_DEFAULT_SIZE)
        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon(str(MUSIC_PLAYER_ICON_PATH)))

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#07070b"))

        self.setPalette(palette)

    def _init_ui(self):
        """Initializes the instance's internal widgets and layouts"""
        main_layout = QVBoxLayout()

        # Top (Playlist manager): add, remove, and load song buttons.
        main_layout.addWidget(self.playlist_manager_view, 0)

        # Middle (Playlist window): QTableView.
        main_layout.addWidget(self.playlist_view, 1)

        # Bottom (Player bar): playback controls, volume controls, and current song display.
        main_layout.addWidget(self.player_bar_view, 0)

        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        self.setLayout(main_layout)


# ================================================================================
# SUBVIEWS
# ================================================================================
class PlaylistManagerView(QFrame):
    add_song_button_clicked = pyqtSignal()
    remove_song_button_clicked = pyqtSignal()
    load_song_button_clicked = pyqtSignal()
    def __init__(self):
        super().__init__()
        self._playlist_manager = PlaylistManager()

        self._connect_signals()
        self._init_ui()

    def _init_ui(self):
        instance_layout = QHBoxLayout()

        instance_layout.addWidget(self._playlist_manager)

        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setObjectName("playlistManagerFrame")

        self.setLayout(instance_layout)

    def _connect_signals(self):
        self._playlist_manager.add_song_button_clicked.connect(self.add_song_button_clicked)
        self._playlist_manager.remove_song_button_clicked.connect(self.remove_song_button_clicked)
        self._playlist_manager.load_song_button_clicked.connect(self.load_song_button_clicked)

    @property
    def playlist_manager(self):
        return self._playlist_manager


class PlaylistView(QFrame):
    def __init__(self, playlist_state: PlaylistModel):
        super().__init__()
        self._playlist_display = PlaylistDisplay(playlist_state)

        self._init_ui()

    def _init_ui(self):
        instance_layout = QVBoxLayout()

        instance_layout.addWidget(self._playlist_display)

        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setObjectName("playlistFrame")

        self.setLayout(instance_layout)

    @property
    def playlist_display(self):
        return self._playlist_display


class PlayerbarView(QFrame):
    # Playback progress signal
    playback_slider_moved = pyqtSignal(int)

    # Playback control signals
    replay_button_clicked = pyqtSignal()
    previous_button_clicked = pyqtSignal()
    play_pause_button_clicked = pyqtSignal()
    next_button_clicked = pyqtSignal()
    repeat_button_clicked = pyqtSignal()

    # Volume control signals
    volume_button_toggled = pyqtSignal(bool)
    volume_slider_moved = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self._playback_progress = PlaybackProgress()
        self._now_playing_display = NowPlayingDisplay()
        self._playback_controls = PlaybackControls()
        self._volume_controls = VolumeControls()

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        instance_layout = QVBoxLayout()

        # --- Top section ---
        top_layout = QHBoxLayout()

        # Top (Playback progress widgets): Progress bar, elapsed time and total duration label.
        top_layout.addWidget(self._playback_progress)

        # --- Bottom section ---
        bottom_layout = QHBoxLayout()  # For grouping bottom sections horizontally.

        # Bottom left (Now playing display widgets): Album art, title and artist label.
        bottom_layout.addWidget(self._now_playing_display, 0)
        bottom_layout.addStretch(1)  # Pushes the next layout (add spacing).

        # Bottom middle (Playback control widgets): Play/pause and playback navigation buttons.
        bottom_layout.addWidget(self._playback_controls, 1)
        bottom_layout.addStretch(1)  # Pushes the next layout (add spacing).

        # Bottom right (Volume control widgets): Volume button, slider and label.
        bottom_layout.addWidget(self._volume_controls, 0)

        instance_layout.addLayout(top_layout)
        instance_layout.addLayout(bottom_layout)

        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setObjectName("playerBarFrame")

        self.setLayout(instance_layout)

    def _connect_signals(self):
        # Playback progress signal
        self._playback_progress.playback_slider_moved.connect(self.playback_slider_moved)

        # Playback control signals
        self._playback_controls.replay_button_clicked.connect(self.replay_button_clicked)
        self._playback_controls.previous_button_clicked.connect(self.previous_button_clicked)
        self._playback_controls.play_pause_button_clicked.connect(self.play_pause_button_clicked)
        self._playback_controls.next_button_clicked.connect(self.next_button_clicked)
        self._playback_controls.repeat_button_clicked.connect(self.repeat_button_clicked)

        # Volume control signals
        self._volume_controls.volume_button_toggled.connect(self.volume_button_toggled)
        self._volume_controls.volume_slider_moved.connect(self.volume_slider_moved)

    @property
    def playback_progress(self):
        return self._playback_progress

    @property
    def now_playing_display(self):
        return self._now_playing_display

    @property
    def playback_controls(self):
        return self._playback_controls

    @property
    def volume_controls(self):
        return self._volume_controls
