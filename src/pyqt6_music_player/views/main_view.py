"""Main application view for the PyQt6 Music Player.

This module defines the `MusicPlayerView`, the central container widget
that holds all major UI components (playlist, player bar, controls).
"""
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QColor, QIcon, QPalette
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from pyqt6_music_player.config import (
    APP_DEFAULT_SIZE,
    APP_TITLE,
    MUSIC_PLAYER_ICON_PATH,
)
from pyqt6_music_player.context import AppContext
from pyqt6_music_player.views import PlayerbarView, PlaylistManagerView, PlaylistView


# ================================================================================
# MAIN VIEW
# ================================================================================
class MusicPlayerView(QWidget):
    """App's main view."""

    def __init__(self, ctx: AppContext):
        super().__init__()
        self.ctx = ctx
        self.playlist_manager_view = PlaylistManagerView(ctx.playlist_viewmodel)
        self.playlist_view = PlaylistView(ctx.playlist_viewmodel)
        self.player_bar_view = PlayerbarView(
            ctx.playback_viewmodel,
            ctx.volume_viewmodel,
        )

        self._should_close = False

        self._configure_properties()
        self._init_ui()

    def _configure_properties(self):
        """Configure the instance's properties."""
        self.resize(*APP_DEFAULT_SIZE)
        self.setMinimumSize(*APP_DEFAULT_SIZE)
        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon(str(MUSIC_PLAYER_ICON_PATH)))

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#07070b"))

        self.setPalette(palette)

    def _init_ui(self):
        """Initialize the instance's internal widgets and layouts."""
        main_layout = QVBoxLayout()

        # Top (Playlist manager): add, remove, and load song buttons.
        main_layout.addWidget(self.playlist_manager_view, 0)

        # Middle (Playlist window): QTableView.
        main_layout.addWidget(self.playlist_view, 1)

        # Bottom (Player bar): playback controls, volume controls,
        # and current song display.
        main_layout.addWidget(self.player_bar_view, 0)

        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        self.setLayout(main_layout)

    def closeEvent(self, a0):
        # TODO: Should close quickly when audio player is not running (fix).
        if self._should_close:
            a0.accept()
            return

        a0.ignore()

        self.ctx.playback_viewmodel.shutdown()
        self.ctx.playback_viewmodel.shutdown_finished.connect(
            self._on_shutdown_finished,
        )

    @pyqtSlot()
    def _on_shutdown_finished(self):
        self._should_close = True

        self.close()
