import os
import sys
import traceback

from PyQt6.QtWidgets import QApplication

from pyqt6_music_player.config import STYLESHEET_PATH
from pyqt6_music_player.controllers.mp_controller import MusicPlayerController
from src.pyqt6_music_player.views.main_view import MusicPlayerView


def exception_hook(exc_type, value, tb):
    """Handles uncaught exceptions."""
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
    app = QApplication(sys.argv)

    stylesheet = load_stylesheet(STYLESHEET_PATH)
    if stylesheet:
        app.setStyleSheet(stylesheet)

    # View
    view = MusicPlayerView()

    # Controller
    _controller = MusicPlayerController(view)

    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
