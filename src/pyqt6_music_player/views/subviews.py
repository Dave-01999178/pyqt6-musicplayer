from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout

from pyqt6_music_player.view_models import (
    PlaybackControlViewModel,
    PlaylistViewModel,
    VolumeViewModel
)
from pyqt6_music_player.views import (
    NowPlayingDisplay,
    PlaybackControls,
    PlaybackProgress,
    PlaylistDisplay,
    PlaylistManager,
    VolumeControls
)


class PlaylistManagerView(QFrame):
    def __init__(self, playlist_viewmodel: PlaylistViewModel):
        super().__init__()
        self._playlist_manager = PlaylistManager(playlist_viewmodel)

        self._init_ui()

    def _init_ui(self):
        """Initializes the instance's internal widgets and layouts"""
        instance_layout = QHBoxLayout()

        instance_layout.addWidget(self._playlist_manager)

        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setObjectName("playlistManagerFrame")

        self.setLayout(instance_layout)

    @property
    def playlist_manager(self):
        return self._playlist_manager


class PlaylistView(QFrame):
    def __init__(self, playlist_viewmodel: PlaylistViewModel):
        super().__init__()
        self._playlist_display = PlaylistDisplay(playlist_viewmodel)

        self._init_ui()

    def _init_ui(self):
        """Initializes the instance's internal widgets and layouts"""
        instance_layout = QVBoxLayout()

        instance_layout.addWidget(self._playlist_display)

        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setObjectName("playlistFrame")

        self.setLayout(instance_layout)

    @property
    def playlist_display(self):
        return self._playlist_display


class PlayerbarView(QFrame):
    """
    A customizable QFrame container for grouping player-related view/components,
    including playback progress, now playing display, playback controls, and volume controls.
    """
    def __init__(
            self,
            playback_viewmodel: PlaybackControlViewModel,
            volume_viewmodel: VolumeViewModel
            ):
        super().__init__()
        self._playback_progress = PlaybackProgress()
        self._now_playing_display = NowPlayingDisplay()
        self._playback_controls = PlaybackControls(playback_viewmodel)
        self._volume_controls = VolumeControls(volume_viewmodel)

        self._init_ui()

    def _init_ui(self):
        """Initializes the instance's internal widgets and layouts"""
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
