import os
import sys
import traceback

from PyQt6.QtWidgets import QApplication

from pyqt6_music_player.config import STYLESHEET
from pyqt6_music_player.controllers import (
    PlaybackControlsController,
    PlaybackProgressController,
    PlaylistController,
    VolumeController,
    NowPlayingMetadataController,
)
from pyqt6_music_player.models import (
    MusicPlayerState,
    PlaylistState,
    PlaybackProgressState,
    VolumeState,
)
from pyqt6_music_player.views import MusicPlayerView
    

def exception_hook(exc_type, value, tb):
    """Custom exception hook for handling uncaught exceptions."""
    traceback.print_exception(exc_type, value, tb)
    sys.exit(1)


sys.excepthook = exception_hook


def load_stylesheet(path: str) -> str | None:
    if not os.path.isfile(path):
        print(f"[WARNING] Stylesheet not found: {path}")
        return None

    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except (OSError, UnicodeDecodeError) as e:
        print(f"[ERROR] Failed to load stylesheet: {e}")
        return None


def main():
    # App
    app = QApplication(sys.argv)

    # Stylesheet
    stylesheet = load_stylesheet(STYLESHEET)
    if stylesheet:
        app.setStyleSheet(stylesheet)

    # States
    playlist_state = PlaylistState()
    volume_state = VolumeState()
    playback_progress = PlaybackProgressState()

    state = MusicPlayerState(
        playlist=playlist_state,
        volume=volume_state,
        playback_progress=playback_progress
    )

    # Views
    view = MusicPlayerView(state)

    # Controllers
    controllers = [
        PlaybackProgressController(state, view),
        PlaybackControlsController(state, view),
        VolumeController(state, view),
        NowPlayingMetadataController(state, view),
        PlaylistController(state, view),
    ]

    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
