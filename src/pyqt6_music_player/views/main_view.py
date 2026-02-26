"""Main application view for the PyQt6 Music Player.

This module defines the `MusicPlayerView`, the central container widget
that holds all major UI components (playlist, player bar, controls).
"""
import logging

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


# ================================================================================
# MAIN VIEW
# ================================================================================
class MusicPlayerView(QWidget):
    """Application main view."""

    def __init__(self, ctx: AppContext):
        """Initialize MusicPlayerView."""
        super().__init__()
        # App context
        self.ctx = ctx

        # Section views
        self.playlist_manager_view = PlaylistManagerView(ctx.playlist_viewmodel)
        self.playlist_view = PlaylistDisplayPanel(ctx.playlist_viewmodel)
        self.player_bar_view = PlayerbarView(
            ctx.playback_viewmodel,
            ctx.volume_viewmodel,
        )

        # Setup
        self._configure_properties()
        self._init_ui()

    # --- Public methods (QWidget) ---
    def closeEvent(self, a0):
        audio_player = self.ctx.audio_player

        if not audio_player.is_running():
            logger.info("Application closed.")
            a0.accept()

            return

        a0.ignore()

        audio_player.shutdown()
        audio_player.player_resources_released.connect(self.close)

    # --- Protected/internal methods ---
    def _configure_properties(self):
        self.resize(*APP_DEFAULT_SIZE)
        self.setMinimumSize(*APP_DEFAULT_SIZE)
        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon(str(MUSIC_PLAYER_ICON_PATH)))

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#07070b"))

        self.setPalette(palette)

    def _init_ui(self):
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
