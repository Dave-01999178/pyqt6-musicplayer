from enum import Enum
from typing import TypeAlias

from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal

from pyqt6_music_player.views import (
    NextButton,
    PlayPauseButton,
    PreviousButton,
    RepeatButton,
    ReplayButton,
    AddSongButton,
    LoadSongFolderButton,
    RemoveSongButton,
)


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


PLAYBACK_BUTTON_MAP = {
    PlaybackButtons.REPLAY: (ReplayButton, "replay_button_clicked"),
    PlaybackButtons.PREVIOUS: (PreviousButton, "previous_button_clicked"),
    PlaybackButtons.PLAY_PAUSE: (PlayPauseButton, "play_pause_button_clicked"),
    PlaybackButtons.NEXT: (NextButton, "next_button_clicked"),
    PlaybackButtons.REPEAT: (RepeatButton, "repeat_button_clicked")
}

PLAYLIST_BUTTON_MAP = {
    PlaylistButtons.ADD: (AddSongButton, "add_song_button_clicked"),
    PlaylistButtons.REMOVE: (RemoveSongButton, "remove_song_button_clicked"),
    PlaylistButtons.LOAD: (LoadSongFolderButton, "load_song_button_clicked")
}

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
