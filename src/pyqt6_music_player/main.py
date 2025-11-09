import logging
import os
import sys
import traceback
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from pyqt6_music_player.config import STYLESHEET
from pyqt6_music_player.controllers import (
    PlaybackControlController,
    PlaybackProgressController,
    PlaylistManagerController,
    VolumeControlController
)
from pyqt6_music_player.models import PlaylistModel, VolumeSettings
from pyqt6_music_player.views import MusicPlayerView


def exception_hook(exc_type, value, tb):
    """Custom exception hook for handling uncaught exceptions."""
    traceback.print_exception(exc_type, value, tb)
    sys.exit(1)


sys.excepthook = exception_hook


def load_stylesheet(path: str| Path) -> str | None:
    if not os.path.isfile(path):
        logging.error("[WARNING] Stylesheet not found: %s", path)
        return None

    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except (OSError, UnicodeDecodeError) as e:
        logging.error("[ERROR] Failed to load stylesheet: %s", e)
        return None


def main():
    # App
    app = QApplication(sys.argv)

    # Stylesheet
    stylesheet = load_stylesheet(STYLESHEET)
    if stylesheet:
        app.setStyleSheet(stylesheet)

    # State, Model and Settings.
    playlist_model = PlaylistModel()
    volume_settings = VolumeSettings()

    # Main view
    main_view = MusicPlayerView(playlist_model)

    # Sub views
    playlist_sub_view = main_view.playlist_view
    player_bar_sub_view = main_view.player_bar_view
    playlist_manager_sub_view = main_view.playlist_manager_view

    # Controllers
    controllers = [
        PlaybackProgressController(player_bar_sub_view),
        PlaybackControlController(player_bar_sub_view),
        PlaylistManagerController(playlist_model, playlist_manager_sub_view),
        VolumeControlController(volume_settings, player_bar_sub_view),
    ]

    main_view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
