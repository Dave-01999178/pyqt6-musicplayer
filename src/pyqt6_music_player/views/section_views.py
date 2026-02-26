from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout

from pyqt6_music_player.view_models import (
    PlaybackViewModel,
    PlaylistViewModel,
    VolumeViewModel,
)
from pyqt6_music_player.views import (
    NowPlayingPanel,
    PlaybackControlsPanel,
    PlaybackProgressPanel,
    PlaylistDisplayPanel,
    PlaylistManagerPanel,
    VolumeControlsPanel,
)


class PlaylistManagerView(QFrame):
    """A customizable frame container for playlist manager panel."""

    def __init__(self, playlist_viewmodel: PlaylistViewModel):
        """Initialize PlaylistManagerView.

        Args:
            playlist_viewmodel: The playlist viewmodel.

        """
        super().__init__()
        # Panel
        self._playlist_manager = PlaylistManagerPanel(playlist_viewmodel)

        # Setup
        self._configure_properties()
        self._init_ui()

    # --- Protected/internal methods ---
    def _configure_properties(self):
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setObjectName("playlistManagerFrame")

    def _init_ui(self):
        instance_layout = QVBoxLayout()

        instance_layout.addWidget(self._playlist_manager)

        self.setLayout(instance_layout)


class PlaylistView(QFrame):
    """A customizable frame container for playlist display panel."""

    def __init__(self, playlist_viewmodel: PlaylistViewModel):
        """Initialize PlaylistView.

        Args:
            playlist_viewmodel: The playlist viewmodel.

        """
        super().__init__()
        # Panel
        self._playlist_display = PlaylistDisplayPanel(playlist_viewmodel)

        # Setup
        self._init_ui()

    # --- Protected/internal methods ---
    def _init_ui(self):
        instance_layout = QVBoxLayout()

        instance_layout.addWidget(self._playlist_display)

        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setObjectName("playlistFrame")

        self.setLayout(instance_layout)


class PlayerbarView(QFrame):
    """A customizable frame container for grouping player-related panels.

    This includes playback progress, now playing display, playback control,
    and volume control panels.
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
        # Panels
        self._playback_progress = PlaybackProgressPanel(playback_viewmodel)
        self._now_playing_display = NowPlayingPanel(playback_viewmodel)
        self._playback_controls = PlaybackControlsPanel(playback_viewmodel)
        self._volume_controls = VolumeControlsPanel(volume_viewmodel)

        # Setup
        self._init_ui()

    # --- Protected/internal methods ---
    def _init_ui(self):
        main_layout_vertical = QVBoxLayout()

        # Top section: Playback progress panel
        top_layout = QVBoxLayout()

        top_layout.addWidget(self._playback_progress)

        # Bottom section: Now playing, playback control, and volume control panels
        bottom_layout_horizontal = QHBoxLayout()

        # Bottom section left widget: Now playing panel
        bottom_layout_horizontal.addWidget(self._now_playing_display, 0)
        bottom_layout_horizontal.addStretch(1)  # Pushes the next layout (add spacing).

        # Bottom section middle widget: Playback controls panel
        bottom_layout_horizontal.addWidget(self._playback_controls, 1)
        bottom_layout_horizontal.addStretch(1)  # Pushes the next layout (add spacing).

        # Bottom section right widget: Volume controls panel
        bottom_layout_horizontal.addWidget(self._volume_controls, 0)

        bottom_layout_horizontal.setContentsMargins(10, 0, 10, 0)

        main_layout_vertical.addLayout(top_layout)
        main_layout_vertical.addLayout(bottom_layout_horizontal)

        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setObjectName("playerBarFrame")

        self.setLayout(main_layout_vertical)
