"""
UI sections for the music player.

This module contains QWidget-based section containers for different parts of the music player UI,
such as playlist controls, playback progress, playback controls, volume controls,
and audio metadata display.
"""
# --- Standard library ---
from enum import Enum
from typing import TypeAlias

# --- Third-party library ---
from PyQt6.QtCore import Qt, pyqtSignal, pyqtBoundSignal
from PyQt6.QtWidgets import QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget

# --- Local imports ---
from pyqt6_music_player.models.music_player_state import (
    MetadataState,
    VolumeState,
    PlaybackProgressState,
)
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
from pyqt6_music_player.views.playlist_widgets import (
    AddSongButton,
    LoadSongFolderButton,
    PlaylistWindow,
    RemoveSongButton,
)
from pyqt6_music_player.views.volume_widgets import VolumeButton, VolumeLabel, VolumeSlider


# --- Enums ---
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


# --- Type Alias ---
PlaylistButtonType: TypeAlias = AddSongButton | RemoveSongButton | LoadSongFolderButton
PlaylistButtonDict: TypeAlias = dict[
    PlaylistButtons, tuple[PlaylistButtonType, pyqtBoundSignal | pyqtSignal]
]

PlaybackButtonType: TypeAlias = (
        ReplayButton | PreviousButton | PlayPauseButton | NextButton | RepeatButton
)
PlaybackButtonDict: TypeAlias = dict[
    PlaybackButtons, tuple[PlaybackButtonType, pyqtBoundSignal | pyqtSignal]
]


# --- UI Sections ---
class PlaylistSection(QWidget):
    """A QWidget-based section containers for edit playlist buttons and playlist window."""
    add_song_button_clicked = pyqtSignal()
    remove_song_button_clicked = pyqtSignal()
    load_song_button_clicked = pyqtSignal()
    def __init__(self) -> None:
        """Initializes the playlist widget container."""
        super().__init__()
        self.buttons: PlaylistButtonDict = {
            PlaylistButtons.ADD: (AddSongButton(), self.add_song_button_clicked),
            PlaylistButtons.REMOVE: (RemoveSongButton(), self.remove_song_button_clicked),
            PlaylistButtons.LOAD: (LoadSongFolderButton(), self.load_song_button_clicked)
        }
        self.playlist_window = PlaylistWindow()

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Initializes the container's internal widgets and layouts"""
        section_layout = QVBoxLayout()
        playlist_btn_layout = QHBoxLayout()

        for btn_widget, _ in self.buttons.values():
            playlist_btn_layout.addWidget(btn_widget)

        section_layout.addLayout(playlist_btn_layout)
        section_layout.addWidget(self.playlist_window)

        self.setLayout(section_layout)

    def _connect_signals(self):
        """Connects internal widget signals to section-level signals"""
        for btn_widget, signal_obj in self.buttons.values():
            btn_widget.clicked.connect(signal_obj)


class PlaybackProgressSection(QWidget):
    """A QWidget-based section containers for playback progress bar and time labels."""

    progress_bar_slider_changed: pyqtSignal = pyqtSignal(int)

    def __init__(self, playback_progress_state: PlaybackProgressState):
        """
        Initializes the playback progress widget container.

        Args:
            playback_progress_state: The music player state object.
        """
        super().__init__()
        self.playback_progress_state = playback_progress_state

        self.progress_bar = PlaybackProgressBar()
        self.elapsed_time = ElapsedTimeLabel(self.playback_progress_state)
        self.total_duration = TotalDurationLabel(self.playback_progress_state)

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

    def __init__(self) -> None:
        """Initializes the playback control widget container."""
        super().__init__()
        self.buttons: PlaybackButtonDict = {
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
    def __init__(self, volume_state: VolumeState):
        """
        Initializes the volume widget container.

        Args:
            volume_state: The global music player state object.
        """
        super().__init__()
        self.volume_state = volume_state

        self.volume_button = VolumeButton(self.volume_state)
        self.volume_slider = VolumeSlider(self.volume_state)
        self.volume_label = VolumeLabel(self.volume_state)

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


class AudioMetadataSection(QWidget):
    """A QWidget-based section containers for album art, song title, and performer label."""
    def __init__(self, metadata_state: MetadataState):
        """
        Initializes the audio metadata widget container.

        Args:
            metadata_state: The global music player state object.
        """
        super().__init__()
        self.metadata_state = metadata_state

        self.album_art = AlbumArtLabel()
        self.song_title = SongTitleLabel(self.metadata_state)
        self.performer_label = ArtistLabel(self.metadata_state)

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
