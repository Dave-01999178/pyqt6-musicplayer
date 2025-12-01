import logging
import os
import sys
import traceback
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from pyqt6_music_player.config import STYLESHEET
from pyqt6_music_player.models import PlaylistModel, VolumeModel
from pyqt6_music_player.models.player_engine import PlayerEngine
from pyqt6_music_player.view_models import PlaylistViewModel, PlaybackControlViewModel, VolumeViewModel
from pyqt6_music_player.views import MusicPlayerView
from pyqt6_music_player.views.main_view import AppContext


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
    # --- App ---
    app = QApplication(sys.argv)

    # --- Stylesheet ---
    stylesheet = load_stylesheet(STYLESHEET)
    if stylesheet:
        app.setStyleSheet(stylesheet)

    # --- Player engine ---
    player_engine = PlayerEngine()

    # --- Models ---
    playlist_model = PlaylistModel()
    volume_model = VolumeModel()

    # --- ViewModels ---
    playback_viewmodel = PlaybackControlViewModel(playlist_model, player_engine)
    playlist_viewmodel = PlaylistViewModel(playlist_model)
    volume_viewmodel = VolumeViewModel(volume_model, player_engine)

    ctx = AppContext(
        playlist_model=playlist_model,
        volume_model=volume_model,
        playback_viewmodel=playback_viewmodel,
        playlist_viewmodel=playlist_viewmodel,
        volume_viewmodel=volume_viewmodel
    )

    # --- View ---
    main_view = MusicPlayerView(ctx)
    main_view.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
