import logging
import os
import sys
import traceback
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from pyqt6_music_player.config import STYLESHEET
from pyqt6_music_player.context import build_context
from pyqt6_music_player.logging_config import setup_logging
from pyqt6_music_player.views import MusicPlayerView

logger = logging.getLogger(__name__)


def exception_hook(exc_type, value, tb):
    """Custom exception hook for handling uncaught exceptions."""
    traceback.print_exception(exc_type, value, tb)
    sys.exit(1)


sys.excepthook = exception_hook


def load_stylesheet(path: str | Path) -> str | None:
    if not os.path.isfile(path):
        logger.warning("[WARNING] Stylesheet not found: %s", path)
        return None

    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except (OSError, UnicodeDecodeError) as e:
        logger.error("[ERROR] Failed to load stylesheet: %s", e)
        return None


def main():
    # --- Log ---
    setup_logging()

    logger.info("Application started.")

    # --- App ---
    app = QApplication(sys.argv)

    # --- Stylesheet ---
    stylesheet = load_stylesheet(STYLESHEET)
    if stylesheet:
        app.setStyleSheet(stylesheet)

    # --- App context ---
    ctx = build_context()

    # --- View ---
    main_view = MusicPlayerView(ctx)
    main_view.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
