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


# ==================== SECTION VIEWS ====================
#
# --- PlaylistManager ---
class PlaylistManagerView(QFrame):
    """A customizable frame container for playlist manager panel."""

    def __init__(self, playlist_viewmodel: PlaylistViewModel):
        """Initialize PlaylistManagerView.

        Args:
            playlist_viewmodel: The playlist viewmodel.

        """
        super().__init__()
        # Panel
        self._playlist_manager_panel = PlaylistManagerPanel(playlist_viewmodel)

        # Setup
        self._configure_properties()
        self._init_ui()

    # -- Protected/internal methods --
    def _configure_properties(self) -> None:
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setObjectName("playlistManagerFrame")

    def _init_ui(self) -> None:
        # Setup instance widgets and layout
        instance_layout = QVBoxLayout()

        instance_layout.addWidget(self._playlist_manager_panel)

        self.setLayout(instance_layout)


# --- Playlist ---
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

    # -- Protected/internal methods --
    def _init_ui(self) -> None:
        # Setup instance widgets and layout
        instance_layout = QVBoxLayout()

        instance_layout.addWidget(self._playlist_display)

        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setObjectName("playlistFrame")

        self.setLayout(instance_layout)


# --- Player bar ---
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
        self._playback_progress_panel = PlaybackProgressPanel(playback_viewmodel)
        self._now_playing_panel = NowPlayingPanel(playback_viewmodel)
        self._playback_controls_panel = PlaybackControlsPanel(playback_viewmodel)
        self._volume_controls_panel = VolumeControlsPanel(volume_viewmodel)

        # Setup
        self._init_ui()

    # -- Protected/internal methods --
    def _init_ui(self):
        # Setup instance widgets and layout
        main_layout_vertical = QVBoxLayout()

        # Top section: Playback progress panel
        top_layout = QVBoxLayout()

        top_layout.addWidget(self._playback_progress_panel)

        # Bottom section: Now playing, playback control, and volume control panels
        bottom_layout_horizontal = QHBoxLayout()

        # Bottom section left widget: Now playing panel
        bottom_layout_horizontal.addWidget(self._now_playing_panel, 0)
        bottom_layout_horizontal.addStretch(1)  # Pushes the next layout (add spacing).

        # Bottom section middle widget: Playback controls panel
        bottom_layout_horizontal.addWidget(self._playback_controls_panel, 1)
        bottom_layout_horizontal.addStretch(1)  # Pushes the next layout (add spacing).

        # Bottom section right widget: Volume controls panel
        bottom_layout_horizontal.addWidget(self._volume_controls_panel, 0)

        bottom_layout_horizontal.setContentsMargins(10, 0, 10, 0)

        main_layout_vertical.addLayout(top_layout)
        main_layout_vertical.addLayout(bottom_layout_horizontal)

        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setObjectName("playerBarFrame")

        self.setLayout(main_layout_vertical)
