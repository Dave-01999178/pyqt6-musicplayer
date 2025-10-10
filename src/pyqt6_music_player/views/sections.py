"""
UI sections for the music player.

This module contains QWidget-based section containers for different parts of the music player UI,
such as playlist controls, playback progress, playback controls, volume controls,
and audio metadata display.
"""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget

from pyqt6_music_player.models.music_player_state import PlaylistState
from src.pyqt6_music_player.button_mappings import (
    PLAYBACK_BUTTON_MAP,
    PLAYLIST_BUTTON_MAP,
    PlaybackButtonDict,
    PlaylistButtonDict,
)
from src.pyqt6_music_player.models.music_player_state import (
    PlaybackProgressState,
    Song,
    VolumeState,
)
from src.pyqt6_music_player.views.metadata_widgets import (
    AlbumArtLabel,
    ArtistLabel,
    SongTitleLabel
)
from src.pyqt6_music_player.views.playback_progress_widgets import (
    ElapsedTimeLabel,
    PlaybackProgressBar,
    TotalDurationLabel,
)
from src.pyqt6_music_player.views.playlist_widgets import PlaylistWindow
from src.pyqt6_music_player.views.volume_widgets import VolumeButton, VolumeLabel, VolumeSlider


# --- Helper function ---
def build_button_dict(mapping: dict, parent: QWidget):
    buttons = {}
    for btn_name, (btn_cls, signal_name) in mapping.items():
        btn_widget = btn_cls()
        signal_obj = getattr(parent, signal_name)
        buttons[btn_name] = (btn_widget, signal_obj)
    return buttons


# --- UI Sections ---
class PlaylistSection(QWidget):
    """A QWidget-based section containers for edit playlist buttons and playlist window."""
    add_song_button_clicked = pyqtSignal()
    remove_song_button_clicked = pyqtSignal()
    load_song_button_clicked = pyqtSignal()
    def __init__(self, playlist_state: PlaylistState) -> None:
        """Initializes the playlist widget container."""
        super().__init__()
        self.buttons: PlaylistButtonDict = build_button_dict(PLAYLIST_BUTTON_MAP, self)
        self.playlist_window = PlaylistWindow(playlist_state)

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
    previous_button_clicked: pyqtSignal = pyqtSignal()
    play_pause_button_clicked: pyqtSignal = pyqtSignal()
    next_button_clicked: pyqtSignal = pyqtSignal()
    repeat_button_clicked: pyqtSignal = pyqtSignal()

    def __init__(self) -> None:
        """Initializes the playback control widget container."""
        super().__init__()
        self.buttons: PlaybackButtonDict = build_button_dict(PLAYBACK_BUTTON_MAP, self)

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
    def __init__(self, current_song: Song):
        """
        Initializes the audio metadata widget container.

        Args:
            current_song: The current Song object.
        """
        super().__init__()
        self.current_song = current_song

        self.album_art = AlbumArtLabel()
        self.song_title = SongTitleLabel(self.current_song)
        self.performer_label = ArtistLabel(self.current_song)

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
