from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout

from pyqt6_music_player.view_models import (
    PlaybackViewModel,
    PlaylistViewModel,
    VolumeViewModel,
)
from pyqt6_music_player.views import (
    NowPlaying,
    PlaybackControls,
    PlaybackProgress,
    PlaylistDisplay,
    PlaylistManager,
    VolumeControls,
)


class PlaylistManagerView(QFrame):
    """A customizable frame container for playlist manager."""

    def __init__(self, playlist_viewmodel: PlaylistViewModel):
        """Initialize PlaylistManagerView.

        Args:
            playlist_viewmodel: The playlist viewmodel.

        """
        super().__init__()
        self._playlist_manager = PlaylistManager(playlist_viewmodel)

        self._init_ui()

    def _init_ui(self):
        """Initialize the instance's internal widgets and layouts."""
        instance_layout = QHBoxLayout()

        instance_layout.addWidget(self._playlist_manager)

        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setObjectName("playlistManagerFrame")

        self.setLayout(instance_layout)


class PlaylistView(QFrame):
    """A customizable frame container for playlist display."""

    def __init__(self, playlist_viewmodel: PlaylistViewModel):
        """Initialize PlaylistView.

        Args:
            playlist_viewmodel: The playlist viewmodel.

        """
        super().__init__()
        self._playlist_display = PlaylistDisplay(playlist_viewmodel)

        self._init_ui()

    def _init_ui(self):
        """Initialize the instance's internal widgets and layouts."""
        instance_layout = QVBoxLayout()

        instance_layout.addWidget(self._playlist_display)

        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setObjectName("playlistFrame")

        self.setLayout(instance_layout)


class PlayerbarView(QFrame):
    """A customizable QFrame container for grouping player-related view/components.

    This includes playback progress, now playing display, playback controls,
    and volume controls.
    """

    def __init__(
            self,
            playback_viewmodel: PlaybackViewModel,
            volume_viewmodel: VolumeViewModel,
    ):
        """Initialize PlayerbarView.

        Args:
            playback_viewmodel: The playback viewmodel.
            volume_viewmodel: The volume viewmodel.

        """
        super().__init__()
        self._playback_progress = PlaybackProgress(playback_viewmodel)
        self._now_playing_display = NowPlaying(playback_viewmodel)
        self._playback_controls = PlaybackControls(playback_viewmodel)
        self._volume_controls = VolumeControls(volume_viewmodel)

        self._init_ui()

    def _init_ui(self):
        """Initialize instance's internal widgets and layouts."""
        instance_layout = QVBoxLayout()

        # --- Top section ---
        top_layout = QHBoxLayout()

        # Playback progress widgets: progress bar, elapsed, and time remaining label.
        top_layout.addWidget(self._playback_progress)

        # --- Bottom section ---
        bottom_layout = QHBoxLayout()  # For grouping bottom sections horizontally.

        # Bottom left (Now playing display widgets): Album art, title and artist label.
        bottom_layout.addWidget(self._now_playing_display, 0)
        bottom_layout.addStretch(1)  # Pushes the next layout (add spacing).

        # Bottom middle (Playback control widgets): Play/pause and playback navigation
        # buttons.
        bottom_layout.addWidget(self._playback_controls, 1)
        bottom_layout.addStretch(1)  # Pushes the next layout (add spacing).

        # Bottom right (Volume control widgets): Volume button, slider and label.
        bottom_layout.addWidget(self._volume_controls, 0)

        bottom_layout.setContentsMargins(10, 0, 10, 0)

        instance_layout.addLayout(top_layout)
        instance_layout.addLayout(bottom_layout)

        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setObjectName("playerBarFrame")

        self.setLayout(instance_layout)
