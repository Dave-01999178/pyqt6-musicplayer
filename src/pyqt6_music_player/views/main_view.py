"""
Main application view for the PyQt6 Music Player.

This module defines the `MusicPlayerView`, the central container widget
that holds all major UI components (playlist, player bar, controls).
"""
from dataclasses import dataclass

from PyQt6.QtGui import QColor, QIcon, QPalette
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from pyqt6_music_player.config import (
    APP_DEFAULT_SIZE,
    APP_TITLE,
    MUSIC_PLAYER_ICON_PATH
)
from pyqt6_music_player.models import PlaylistModel, VolumeModel
from pyqt6_music_player.view_models import (
    PlaybackControlViewModel,
    PlaylistViewModel,
    VolumeViewModel
)
from pyqt6_music_player.views import PlaylistManagerView, PlaylistView, PlayerbarView


# TODO: Single source of truth, created once in main(). Move outside of main view module later.
@dataclass
class AppContext:
    # Models
    playlist_model: PlaylistModel
    volume_model: VolumeModel

    # ViewModels
    playback_viewmodel: PlaybackControlViewModel
    playlist_viewmodel: PlaylistViewModel
    volume_viewmodel: VolumeViewModel


# ================================================================================
# MAIN VIEW
# ================================================================================
class MusicPlayerView(QWidget):
    def __init__(self, ctx: AppContext):
        """
        Initialize the main music player view.
        """
        super().__init__()
        self.ctx = ctx
        self.playlist_manager_view = PlaylistManagerView(ctx.playlist_viewmodel)
        self.playlist_view = PlaylistView(ctx.playlist_viewmodel)
        self.player_bar_view = PlayerbarView(ctx.playback_viewmodel, ctx.volume_viewmodel)

        self._configure_properties()
        self._init_ui()

    def _configure_properties(self):
        """Configures the instance's properties"""
        self.resize(*APP_DEFAULT_SIZE)
        self.setMinimumSize(*APP_DEFAULT_SIZE)
        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon(str(MUSIC_PLAYER_ICON_PATH)))

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#07070b"))

        self.setPalette(palette)

    def _init_ui(self):
        """Initializes the instance's internal widgets and layouts"""
        main_layout = QVBoxLayout()

        # Top (Playlist manager): add, remove, and load song buttons.
        main_layout.addWidget(self.playlist_manager_view, 0)

        # Middle (Playlist window): QTableView.
        main_layout.addWidget(self.playlist_view, 1)

        # Bottom (Player bar): playback controls, volume controls, and current song display.
        main_layout.addWidget(self.player_bar_view, 0)

        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        self.setLayout(main_layout)
