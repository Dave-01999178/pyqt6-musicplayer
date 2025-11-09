"""
UI sections for the music player.

This module contains QWidget-based section containers for different parts of the music player UI,
such as playlist controls, playback progress, playback controls, volume controls,
and audio metadata display.
"""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget

from pyqt6_music_player.models import PlaylistModel, Song
from pyqt6_music_player.views import (
    AddSongButton,
    AlbumArtLabel,
    AudioArtistLabel,
    AudioTitleLabel,
    ElapsedTimeLabel,
    LoadSongFolderButton,
    NextButton,
    PlaybackProgressSlider,
    PlaylistTableWidget,
    PlayPauseButton,
    PreviousButton,
    RemoveSongButton,
    RepeatButton,
    ReplayButton,
    TotalDurationLabel,
    VolumeButton,
    VolumeLabel,
    VolumeSlider
)


class PlaylistManager(QWidget):
    """
    A QWidget container for widgets that is used to manage the playlist
    such as add/remove song button, and load folder button.
    """
    add_song_button_clicked = pyqtSignal()
    remove_song_button_clicked = pyqtSignal()
    load_song_button_clicked = pyqtSignal()
    def __init__(self):
        """Initializes PlaylistManager instance."""
        super().__init__()
        self._add_button = AddSongButton()
        self._remove_button = RemoveSongButton()
        self._load_button = LoadSongFolderButton()

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Initializes the container's internal widgets and layouts"""
        section_layout = QHBoxLayout()

        section_layout.addWidget(self._add_button)
        section_layout.addWidget(self._remove_button)
        section_layout.addWidget(self._load_button)

        section_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)

        self.setLayout(section_layout)

    def _connect_signals(self):
        self._add_button.clicked.connect(self.add_song_button_clicked)
        self._remove_button.clicked.connect(self.remove_song_button_clicked)
        self._load_button.clicked.connect(self.load_song_button_clicked)

    @property
    def add_button(self):
        return self._add_button

    @property
    def remove_button(self):
        return self._remove_button

    @property
    def load_button(self):
        return self._load_button


class PlaylistDisplay(QWidget):
    """A QWidget container for the main playlist widget."""
    def __init__(self, playlist_state: PlaylistModel):
        """Initializes PlaylistDisplay instance."""
        super().__init__()
        self.playlist_window = PlaylistTableWidget(playlist_state)

        self._init_ui()

    def _init_ui(self):
        """Initializes the container's internal widgets and layouts"""
        section_layout = QVBoxLayout()

        section_layout.addWidget(self.playlist_window)

        self.setLayout(section_layout)


class PlaybackProgress(QWidget):
    """
    A QWidget container for widgets that is used to control and display playback progress
    such as progress bar, and time labels.
    """
    playback_slider_moved = pyqtSignal(int)

    def __init__(self):
        """Initializes PlaybackProgress instance."""
        super().__init__()
        self.progress_bar = PlaybackProgressSlider()
        self.elapsed_time = ElapsedTimeLabel()
        self.total_duration = TotalDurationLabel()

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Initializes the container's internal widgets and layouts."""
        section_layout = QHBoxLayout()

        section_layout.addWidget(self.elapsed_time)
        section_layout.addWidget(self.progress_bar)
        section_layout.addWidget(self.total_duration)

        section_layout.setSpacing(10)

        self.setLayout(section_layout)

    def _connect_signals(self):
        """Connects the progress bar to the section-level signal."""
        self.progress_bar.valueChanged.connect(self.playback_slider_moved)


class PlaybackControls(QWidget):
    """
    A QWidget container for widgets that is used for track navigation and controlling playback
    such as replay, next, previous, repeat, and play/pause button.
    """
    replay_button_clicked: pyqtSignal = pyqtSignal()
    previous_button_clicked: pyqtSignal = pyqtSignal()
    play_pause_button_clicked: pyqtSignal = pyqtSignal()
    next_button_clicked: pyqtSignal = pyqtSignal()
    repeat_button_clicked: pyqtSignal = pyqtSignal()

    def __init__(self) -> None:
        """Initialize PlaybackControls instance."""
        super().__init__()
        self._replay_button = ReplayButton()
        self._previous_button = PreviousButton()
        self._play_pause_button = PlayPauseButton()
        self._next_button = NextButton()
        self._repeat_button = RepeatButton()

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Initializes the instance's internal widgets and layouts"""
        section_layout = QHBoxLayout()

        section_layout.addWidget(self._replay_button)
        section_layout.addWidget(self._previous_button)
        section_layout.addWidget(self._play_pause_button)
        section_layout.addWidget(self._next_button)
        section_layout.addWidget(self._repeat_button)

        section_layout.setSpacing(10)

        self.setLayout(section_layout)

    def _connect_signals(self):
        """Connects playback control widgets to container-level signals."""
        self._replay_button.clicked.connect(self.replay_button_clicked)
        self._previous_button.clicked.connect(self.previous_button_clicked)
        self._play_pause_button.clicked.connect(self.play_pause_button_clicked)
        self._next_button.clicked.connect(self.next_button_clicked)
        self._repeat_button.clicked.connect(self.repeat_button_clicked)


class VolumeControls(QWidget):
    """
    A QWidget container for widgets that is used to control and display volume
    such as volume button, slider and label.
    """
    volume_button_toggled = pyqtSignal(bool)
    volume_slider_moved = pyqtSignal(int)
    def __init__(self):
        """Initialize VolumeControls instance."""
        super().__init__()
        self._volume_button = VolumeButton()
        self._volume_slider = VolumeSlider()
        self._volume_label = VolumeLabel()

        self._init_ui()
        self._connect_signals()

        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    def _init_ui(self):
        """Initializes the instance's internal widgets and layouts"""
        layout = QHBoxLayout()

        layout.addWidget(self._volume_button)
        layout.addWidget(self._volume_slider)
        layout.addWidget(self._volume_label)

        layout.setSpacing(5)

        self.setLayout(layout)

    def _connect_signals(self):
        """Connects volume widgets to container-level signals."""
        self._volume_button.toggled.connect(self.volume_button_toggled)
        self._volume_slider.valueChanged.connect(self.volume_slider_moved)

    @property
    def volume_button(self):
        return self._volume_button

    @property
    def volume_slider(self):
        return self._volume_slider

    @property
    def volume_label(self):
        return self._volume_label


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
        section_layout = QHBoxLayout()
        section_layout.addWidget(self.album_art)

        label_layout = QVBoxLayout()

        label_layout.addWidget(self.song_title)
        label_layout.addWidget(self.artist_label)

        section_layout.addLayout(label_layout)

        self.setLayout(section_layout)
