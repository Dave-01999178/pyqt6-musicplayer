"""Main application view for the PyQt6 Music Player.

This module defines the `MusicPlayerView`, the central container widget
that holds all major UI components (playlist, player bar, controls).
"""
import logging

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor, QIcon, QPalette
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QWidget

from pyqt6_music_player.audio import AudioPlayerService
from pyqt6_music_player.core import ASSETS_PATH
from pyqt6_music_player.features import (
    NowPlayingPanel,
    PlaybackControlsPanel,
    PlaybackProgressPanel,
    PlaybackViewModel,
    PlaylistDisplayPanel,
    PlaylistManagerPanel,
    PlaylistViewModel,
    VolumeControlsPanel,
    VolumeViewModel,
)

APP_TITLE = "Music Player"
APP_ICON = ASSETS_PATH / "mp_icon.svg"
APP_DEFAULT_SIZE = (750, 750)

logger = logging.getLogger(__name__)


# ==================== MAIN VIEW ====================
class MusicPlayerView(QWidget):
    """Main application view."""

    def __init__(
            self,
            audio_player: AudioPlayerService,
            playlist_viewmodel: PlaylistViewModel,
            playback_viewmodel: PlaybackViewModel,
            volume_viewmodel: VolumeViewModel,
    ):
        super().__init__()
        self._audio_player = audio_player

        # Section views
        self.playlist_manager_view = PlaylistManagerSection(playlist_viewmodel)
        self.playlist_view = PlaylistSection(playlist_viewmodel)
        self.player_bar_view = PlayerbarSection(playback_viewmodel, volume_viewmodel)

        # Shutdown
        self._shutdown_attempted = False

        # Setup
        self._configure_properties()
        self._init_ui()
        self._connect_signals()

    # -- Public methods (Parent) --
    def closeEvent(self, event) -> None:
        audio_player = self._audio_player
        should_force_close = self._shutdown_attempted and audio_player.is_thread_running

        # Determine if we should immediately close:
        # - If shutdown was already attempted and the player is still running,
        #   let the window close on its own.
        # - If the player is not running, it's safe to close immediately.
        if should_force_close or not audio_player.is_thread_running:
            logger.info("Application closed.")
            event.accept()  # Accept the close event to let the window close on its own
            return

        # Prevent immediate close while audio-player thread cleanup is in progress
        event.ignore()  # Ignore the close event so the app stays open

        # Start shutdown
        self._shutdown_attempted = True

        logger.info("Shutdown initiated.")

        audio_player.shutdown()

        # Fallback: force application exit if shutdown hangs
        QTimer.singleShot(5000, self._force_close)

    # -- Protected/internal methods --
    def _configure_properties(self):
        self.resize(*APP_DEFAULT_SIZE)
        self.setMinimumSize(*APP_DEFAULT_SIZE)
        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon(str(APP_ICON)))

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#0F1419"))

        self.setPalette(palette)

    def _init_ui(self) -> None:
        # Setup instance widgets and layout
        main_layout_vertical = QVBoxLayout()

        # Top widget: Playlist manager
        main_layout_vertical.addWidget(self.playlist_manager_view, 0)

        # Middle widget: Playlist display
        main_layout_vertical.addWidget(self.playlist_view, 1)

        # Bottom widget: Player bar
        main_layout_vertical.addWidget(self.player_bar_view, 0)

        main_layout_vertical.setContentsMargins(10, 10, 10, 10)
        main_layout_vertical.setSpacing(10)

        self.setLayout(main_layout_vertical)

    def _connect_signals(self) -> None:
        # Close the window once the audio player finishes releasing resources
        self._audio_player.player_resources_released.connect(self.close)

    def _force_close(self) -> None:
        # Force exit: if the window is still visible, attempt to close it
        if self.isVisible():
            logger.warning("Force closing application due to shutdown timeout.")
            self.close()


# ==================== SECTION VIEWS ====================
#
# --- PlaylistManager ---
class PlaylistManagerSection(QFrame):
    """A customizable frame container for playlist manager panel."""

    def __init__(self, playlist_viewmodel: PlaylistViewModel):
        super().__init__()
        # Panel
        self._playlist_manager_panel = PlaylistManagerPanel(playlist_viewmodel)

        # Setup
        self._configure_properties()
        self._init_ui()

    # -- Protected/internal methods --
    def _configure_properties(self) -> None:
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setObjectName("playlistManagerSection")

    def _init_ui(self) -> None:
        # Setup instance widgets and layout
        instance_layout = QVBoxLayout()

        instance_layout.addWidget(self._playlist_manager_panel)

        self.setLayout(instance_layout)


# --- Playlist ---
class PlaylistSection(QFrame):
    """A customizable frame container for playlist display panel."""

    def __init__(self, playlist_viewmodel: PlaylistViewModel):
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

        self.setObjectName("playlistSection")

        self.setLayout(instance_layout)


# --- Playerbar ---
class PlayerbarSection(QFrame):
    """A customizable frame container for grouping player-related panels.

    This includes playback progress, now-playing display, playback control,
    and volume control panels.
    """

    def __init__(
            self,
            playback_viewmodel: PlaybackViewModel,
            volume_viewmodel: VolumeViewModel,
    ):
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
        bottom_layout_horizontal.addStretch(1)  # Pushes the next layout (adds spacing)

        # Bottom section middle widget: Playback controls panel
        bottom_layout_horizontal.addWidget(self._playback_controls_panel, 1)
        bottom_layout_horizontal.addStretch(1)  # Pushes the next layout (adds spacing)

        # Bottom section right widget: Volume controls panel
        bottom_layout_horizontal.addWidget(self._volume_controls_panel, 0)

        bottom_layout_horizontal.setContentsMargins(10, 0, 10, 0)

        main_layout_vertical.addLayout(top_layout)
        main_layout_vertical.addLayout(bottom_layout_horizontal)

        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setObjectName("playerBarSection")

        self.setLayout(main_layout_vertical)
