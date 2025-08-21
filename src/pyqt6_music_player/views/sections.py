"""
UI sections for the music player.

This module contains QWidget-based section containers for different parts of the music player UI,
such as playlist controls, playback progress, playback controls, volume controls,
and audio metadata display.
"""
from enum import Enum
from typing import Tuple

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from pyqt6_music_player.config import ADD_ICON_PATH, LOAD_FOLDER_ICON_PATH, REMOVE_ICON_PATH, EDIT_BUTTON_DEFAULT_SIZE
from pyqt6_music_player.models.music_player_state import MusicPlayerState
from pyqt6_music_player.views.base_widgets import IconButton
from pyqt6_music_player.views.metadata_widgets import AlbumArtLabel, ArtistLabel, SongTitleLabel
from pyqt6_music_player.views.playback_control_buttons import (
    NextButton,
    PlayPauseButton,
    PreviousButton,
    RepeatButton,
    ReplayButton,
)
from pyqt6_music_player.views.playback_progress_widgets import (
    ElapsedTimeLabel,
    PlaybackProgressBar,
    TotalDurationLabel,
)
from pyqt6_music_player.views.playlist_widgets import PlaylistWindow
from pyqt6_music_player.views.volume_widgets import VolumeButton, VolumeLabel, VolumeSlider


class PlaylistButtons(Enum):
    """Enum for playlist control button identifiers."""
    ADD = "add_song"
    REMOVE = "remove_song"
    LOAD = "load_songs"


class PlaybackButtons(Enum):
    """Enum for playback control button identifiers."""
    REPLAY = "replay"
    PREVIOUS = "previous"
    PLAY_PAUSE = "play_pause"
    NEXT = "next"
    REPEAT = "repeat"


class PlaylistSection(QWidget):
    """A QWidget-based section containers for edit playlist buttons and playlist window."""
    def __init__(self):
        """Initializes the playlist widget container."""
        super().__init__()
        self.buttons: dict[PlaylistButtons, IconButton | QPushButton] = {
            PlaylistButtons.ADD: IconButton(
                ADD_ICON_PATH,
                EDIT_BUTTON_DEFAULT_SIZE,
                button_text="Add song"
            ),
            PlaylistButtons.REMOVE: IconButton(
                REMOVE_ICON_PATH,
                EDIT_BUTTON_DEFAULT_SIZE,
                button_text="Remove song"
            ),
            PlaylistButtons.LOAD: IconButton(
                LOAD_FOLDER_ICON_PATH,
                EDIT_BUTTON_DEFAULT_SIZE,
                button_text="Load song folder"
            )
        }
        self.playlist_window = PlaylistWindow()

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Initializes the container's internal widgets and layouts"""
        section_layout = QVBoxLayout()
        playlist_btn_layout = QHBoxLayout()

        for btn_widget in self.buttons.values():
            playlist_btn_layout.addWidget(btn_widget)

        section_layout.addLayout(playlist_btn_layout)
        section_layout.addWidget(self.playlist_window)

        self.setLayout(section_layout)

    def _connect_signals(self):
        """Connects internal widget signals to section-level signals"""
        pass


class PlaybackProgressSection(QWidget):
    """A QWidget-based section containers for playback progress bar and time labels."""

    progress_bar_slider_changed: pyqtSignal = pyqtSignal(int)

    def __init__(self, state: MusicPlayerState):
        """
        Initializes the playback progress widget container.

        Args:
            state: The music player state object.
        """
        super().__init__()
        self.state = state

        self.progress_bar = PlaybackProgressBar()
        self.elapsed_time = ElapsedTimeLabel(self.state)
        self.total_duration = TotalDurationLabel(self.state)

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Initializes the container's internal widgets and layouts"""
        section_layout = QVBoxLayout()

        progress_label_layout = QHBoxLayout()

        progress_label_layout.addWidget(self.elapsed_time)
        progress_label_layout.addWidget(self.total_duration)

        section_layout.addWidget(self.progress_bar)
        section_layout.addLayout(progress_label_layout)

        section_layout.setSpacing(0)

        self.setLayout(section_layout)

    def _connect_signals(self):
        """Connects the progress bar to the section-level signal."""
        self.progress_bar.valueChanged.connect(self.progress_bar_slider_changed)


class PlaybackControlSection(QWidget):
    """A QWidget-based section containers for playback control buttons."""

    replay_button_clicked: pyqtSignal = pyqtSignal()
    prev_button_clicked: pyqtSignal = pyqtSignal()
    play_pause_button_clicked: pyqtSignal = pyqtSignal()
    next_button_clicked: pyqtSignal = pyqtSignal()
    repeat_button_clicked: pyqtSignal = pyqtSignal()

    def __init__(self):
        """Initializes the playback control widget container."""
        super().__init__()
        self.buttons: dict[PlaybackButtons, Tuple[IconButton | QPushButton, pyqtSignal]] = {
            PlaybackButtons.REPLAY: (ReplayButton(), self.replay_button_clicked),
            PlaybackButtons.PREVIOUS: (PreviousButton(), self.prev_button_clicked),
            PlaybackButtons.PLAY_PAUSE: (PlayPauseButton(), self.play_pause_button_clicked),
            PlaybackButtons.NEXT: (NextButton(), self.next_button_clicked),
            PlaybackButtons.REPEAT: (RepeatButton(), self.repeat_button_clicked)
        }

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Initializes the container's internal widgets and layouts"""
        section_layout = QHBoxLayout()

        for btn_widget, _ in self.buttons.values():
            section_layout.addWidget(btn_widget)

        section_layout.setSpacing(10)

        self.setLayout(section_layout)

    def _connect_signals(self):
        """Connects each buttons to its section-level signal."""
        for widget, signal_obj in self.buttons.values():
            widget.clicked.connect(signal_obj)


class VolumeSection(QWidget):
    """A QWidget-based section containers for volume button, slider, and label."""
    volume_button_clicked : pyqtSignal = pyqtSignal(bool)
    volume_slider_changed: pyqtSignal = pyqtSignal(int)
    def __init__(self, state: MusicPlayerState):
        """
        Initializes the volume widget container.

        Args:
            state: The global music player state object.
        """
        super().__init__()
        self.state = state

        self.volume_button = VolumeButton()
        self.volume_slider = VolumeSlider()
        self.volume_label = VolumeLabel(self.state)

        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Initializes the container's internal widgets and layouts"""
        layout = QHBoxLayout()

        layout.addWidget(self.volume_button)
        layout.addWidget(self.volume_slider)
        layout.addWidget(self.volume_label)

        layout.setSpacing(5)

        self.setLayout(layout)

    def _connect_signals(self):
        """Connects volume widgets to its section-level signals and state updates."""
        self.volume_button.clicked.connect(self.volume_button_clicked)
        self.volume_slider.valueChanged.connect(self.volume_slider_changed)

        self.state.volume.volume_changed.connect(self._update_widgets)

    def _update_widgets(self, volume: int):
        """Updates volume button, slider, and label when volume changes.

        Args:
            volume: The new volume level.
        """
        self.volume_button.update_button_icon(volume)
        self.volume_slider.update_slider_position(volume)
        self.volume_label.setText(f"{volume}")


class AudioMetadataSection(QWidget):
    """A QWidget-based section containers for album art, song title, and performer label."""
    def __init__(self, state: MusicPlayerState):
        """
        Initializes the audio metadata widget container.

        Args:
            state: The global music player state object.
        """
        super().__init__()
        self.state = state

        self.album_art = AlbumArtLabel()
        self.song_title = SongTitleLabel(self.state)
        self.performer_label = ArtistLabel(self.state)

        self._init_ui()

    def _init_ui(self):
        """Initializes the container's internal widgets and layouts"""
        section_layout = QHBoxLayout()

        label_layout = QVBoxLayout()

        label_layout.addWidget(self.song_title)
        label_layout.addWidget(self.performer_label)

        section_layout.addWidget(self.album_art)
        section_layout.addLayout(label_layout)

        section_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        self.setLayout(section_layout)
