"""Main application view for the PyQt6 Music Player.

This module defines the `MusicPlayerView`, the central container widget
that holds all major UI components (playlist, player bar, controls).
"""
import logging
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor, QIcon, QPalette
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from pyqt6_music_player.core import (
    APP_DEFAULT_SIZE,
    APP_TITLE,
    MUSIC_PLAYER_ICON_PATH,
    AppContext,
)
from pyqt6_music_player.views import (
    PlayerbarView,
    PlaylistDisplayPanel,
    PlaylistManagerView,
)

logger = logging.getLogger(__name__)


# ==================== MAIN VIEW ====================
class MusicPlayerView(QWidget):
    """Main application view."""

    def __init__(self, app_context: AppContext):
        """Initialize the main view and its child views.

        Args:
            app_context: Shared application dependencies.

        """
        super().__init__()
        # App context
        self.ctx = app_context

        # Section views
        self.playlist_manager_view = PlaylistManagerView(
            app_context.playlist_viewmodel,
        )
        self.playlist_view = PlaylistDisplayPanel(app_context.playlist_viewmodel)
        self.player_bar_view = PlayerbarView(
            app_context.playback_viewmodel,
            app_context.volume_viewmodel,
        )

        # Shutdown
        self._shutdown_attempted = False
        self._timer: QTimer = QTimer()

        # Setup
        self._configure_properties()
        self._init_ui()
        self._connect_signals()

    # -- Public methods (Parent) --
    def closeEvent(self, event) -> None:
        audio_player = self.ctx.audio_player
        # Determine if we should immediately close:
        # - If shutdown was already attempted and the player is still running,
        #   let the window close on its own.
        # - If the player is not running, it's safe to close immediately.
        should_force_close = self._shutdown_attempted and audio_player.is_running()
        if should_force_close or not audio_player.is_running():
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
        self.setWindowIcon(QIcon(str(MUSIC_PLAYER_ICON_PATH)))

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#07070b"))

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
        self.ctx.audio_player.player_resources_released.connect(self.close)

    def _force_close(self) -> None:
        # Force exit: if the window is still visible, attempt to close it
        if self.isVisible():
            logger.warning("Force closing application due to shutdown timeout.")
            self.close()
