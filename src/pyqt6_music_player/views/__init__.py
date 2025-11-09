# Base widgets
from .base_widgets import IconButton

# Metadata widgets
from .now_playing_widgets import AlbumArtLabel, AudioArtistLabel, AudioTitleLabel

# Playback control widgets
from .playback_control_widgets import (
    NextButton,
    PlayPauseButton,
    PreviousButton,
    RepeatButton,
    ReplayButton
)

# Playback progress widgets
from .playback_progress_widgets import (
    ElapsedTimeLabel,
    PlaybackProgressSlider,
    TotalDurationLabel
)

# Playlist widgets
from .playlist_widgets import (
    AddSongButton,
    LoadSongFolderButton,
    PlaylistTableWidget,
    RemoveSongButton
)

# Volume widgets
from .volume_widgets import VolumeButton, VolumeLabel, VolumeSlider

# Sections (grouped widgets)
from .sections import (
    NowPlayingDisplay,
    PlaybackControls,
    PlaybackProgress,
    PlaylistDisplay,
    PlaylistManager,
    VolumeControls
)

# Music player view (main view)
from .music_player_view import MusicPlayerView, PlayerbarView, PlaylistView, PlaylistManagerView

__all__ = [
    # Base widgets
    "IconButton",

    # Metadata widgets
    "AlbumArtLabel",
    "AudioArtistLabel",
    "AudioTitleLabel",

    # Playback control widgets
    "NextButton",
    "PlayPauseButton",
    "PreviousButton",
    "RepeatButton",
    "ReplayButton",

    # Playback progress widgets
    "ElapsedTimeLabel",
    "PlaybackProgressSlider",
    "TotalDurationLabel",

    # Playlist widgets
    "AddSongButton",
    "LoadSongFolderButton",
    "PlaylistTableWidget",
    "RemoveSongButton",

    # Volume widgets
    "VolumeButton",
    "VolumeLabel",
    "VolumeSlider",

    # Sections
    "NowPlayingDisplay",
    "PlaybackControls",
    "PlaybackProgress",
    "PlaylistDisplay",
    "PlaylistManager",
    "VolumeControls",

    # Music player view
    "MusicPlayerView",
    "PlayerbarView",
    "PlaylistView",
    "PlaylistManagerView"
]
