# Base widgets
from .base_widgets import BaseLabel, BaseSlider, IconButton

# Metadata widgets
from .metadata_widgets import AlbumArtLabel, ArtistLabel, SongTitleLabel

# Playback control widgets
from .playback_control_buttons import (
    NextButton,
    PlayPauseButton,
    PreviousButton,
    RepeatButton,
    ReplayButton
)

# Playback progress widgets
from .playback_progress_widgets import ElapsedTimeLabel, PlaybackProgressBar, TotalDurationLabel

# Playlist widgets
from .playlist_widgets import (
    PlaylistWindow,
    AddSongButton,
    LoadSongFolderButton,
    RemoveSongButton
)

# Volume widgets
from .volume_widgets import VolumeButton, VolumeLabel, VolumeSlider

# Sections (grouped widgets)
from .sections import (
    AudioMetadataSection,
    PlaybackControlSection,
    PlaybackProgressSection,
    PlaylistToolbarSection,
    PlaylistWindowSection,
    VolumeSection
)

# Frames (section customizable container)
from .frames import PlayerBarFrame, PlaylistSectionFrame, PlaylistToolbarSectionFrame

# Music player view (main view)
from .music_player_view import MusicPlayerView


__all__ = [
    # Base widgets
    "BaseLabel",
    "BaseSlider",
    "IconButton",

    # Metadata widgets
    "AlbumArtLabel",
    "ArtistLabel",
    "SongTitleLabel",

    # Playback control widgets
    "NextButton",
    "PlayPauseButton",
    "PreviousButton",
    "RepeatButton",
    "ReplayButton",

    # Playback progress widgets
    "ElapsedTimeLabel",
    "PlaybackProgressBar",
    "TotalDurationLabel",

    # Playlist widgets
    "PlaylistWindow",
    "AddSongButton",
    "LoadSongFolderButton",
    "RemoveSongButton",

    # Volume widgets
    "VolumeButton",
    "VolumeLabel",
    "VolumeSlider",

    # Sections
    "AudioMetadataSection",
    "PlaybackControlSection",
    "PlaybackProgressSection",
    "PlaylistToolbarSection",
    "PlaylistWindowSection",
    "VolumeSection",

    # Frames
    "PlaylistToolbarSectionFrame",
    "PlayerBarFrame",
    "PlaylistSectionFrame",

    # Music player view
    "MusicPlayerView",
]
