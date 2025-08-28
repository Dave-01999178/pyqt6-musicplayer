"""
Main frame widgets for the music player application.

This module provides the core container widgets that structure the application's
UI, including the main player bar and the playlist display area.
"""
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout

from pyqt6_music_player.models.music_player_state import MusicPlayerState
from pyqt6_music_player.views.sections import (
    AudioMetadataSection,
    PlaybackControlSection,
    PlaybackProgressSection,
    PlaylistSection,
    VolumeSection,
)


class PlaylistSectionFrame(QFrame):
    """
    A customizable frame container for the playlist section.

    This class provides a styled frame to hold the playlist view,
    giving it a distinct visual appearance within the application.
    """
    add_song_button_clicked = pyqtSignal()
    remove_song_button_clicked = pyqtSignal()
    load_song_button_clicked = pyqtSignal()
    def __init__(self):
        """Initializes the playlist section frame."""
        super().__init__()

        self.playlist_section = PlaylistSection()

        self._configure_properties()
        self._init_ui()
        self._connect_signals()

    def _configure_properties(self):
        """Configures the frame's properties"""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setObjectName("playlistFrame")

    def _init_ui(self):
        """Initializes the frame's internal widgets and layouts"""
        layout = QVBoxLayout()

        layout.addWidget(self.playlist_section)

        self.setLayout(layout)

    def _connect_signals(self):
        self.playlist_section.add_song_button_clicked.connect(self.add_song_button_clicked)
        self.playlist_section.remove_song_button_clicked.connect(self.remove_song_button_clicked)
        self.playlist_section.load_song_button_clicked.connect(self.load_song_button_clicked)


class PlayerBarFrame(QFrame):
    """
    A customizable frame container for the playlist section.

    This frame serves as the main container for the music player controls,
    including playback buttons, a progress bar and its time labels, and volume controls.
    """
    # Progress bar signal
    progress_bar_slider_changed: pyqtSignal = pyqtSignal(int)

    # Playback control signals
    prev_button_clicked: pyqtSignal = pyqtSignal()
    play_pause_button_clicked: pyqtSignal = pyqtSignal()
    next_button_clicked: pyqtSignal = pyqtSignal()

    # Volume control signals
    volume_button_clicked: pyqtSignal = pyqtSignal(bool)
    volume_slider_changed: pyqtSignal = pyqtSignal(int)
    def __init__(self, state: MusicPlayerState):
        """
        Initializes the player bar frame.

        Args:
            state: The music player state object
        """
        super().__init__()
        self.audio_metadata_section = AudioMetadataSection(state.metadata)
        self.playback_progress_section = PlaybackProgressSection(state.playback_progress)
        self.playback_control_section = PlaybackControlSection()
        self.volume_section = VolumeSection(state.volume)

        self._configure_properties()
        self._init_ui()
        self._connect_signals()

    def _configure_properties(self):
        """Configures the frame's properties"""
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setObjectName("playerBarFrame")

    def _init_ui(self):
        """Initializes the frame's internal widgets and layouts"""
        layout = QHBoxLayout()

        # Left section: Audio metadata (album art, title, performer).
        layout.addWidget(self.audio_metadata_section, 1)
        layout.addStretch(1)  # Pushes the next layout (spacing).

        # Middle section: Container for playback controls and progress bar.
        playback_container = QVBoxLayout()

        playback_container.addWidget(self.playback_progress_section, 0)
        playback_container.addWidget(self.playback_control_section, 0)
        playback_container.setContentsMargins(0, 0, 0, 0)
        playback_container.setSpacing(0)

        layout.addLayout(playback_container, 6)
        layout.addStretch(1)

        # Right section: Volume controls
        layout.addWidget(self.volume_section, 1)

        layout.setSpacing(0)

        self.setLayout(layout)

    def _connect_signals(self):
        """Connects child widget signals to frame-level signals"""
        self.playback_progress_section.progress_bar_slider_changed.connect(
            self.progress_bar_slider_changed
        )

        self.playback_control_section.prev_button_clicked.connect(self.prev_button_clicked)
        self.playback_control_section.play_pause_button_clicked.connect(self.play_pause_button_clicked)
        self.playback_control_section.next_button_clicked.connect(self.next_button_clicked)

        self.volume_section.volume_button_clicked.connect(self.volume_button_clicked)
        self.volume_section.volume_slider_changed.connect(self.volume_slider_changed)
