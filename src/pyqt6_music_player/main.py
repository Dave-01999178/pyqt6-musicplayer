import logging
import os
import sys
import traceback
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from pyqt6_music_player.core import STYLESHEET, build_context
from pyqt6_music_player.utils import setup_logging
from pyqt6_music_player.views import MusicPlayerView

logger = logging.getLogger(__name__)


def exception_hook(exc_type, value, tb):
    """Custom exception hook for handling uncaught exceptions."""
    traceback.print_exception(exc_type, value, tb)
    sys.exit(1)


sys.excepthook = exception_hook


def load_stylesheet(path: str | Path) -> str | None:
    if not os.path.isfile(path):
        logger.warning("Stylesheet not found: %s", path)
        return None

    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except (OSError, UnicodeDecodeError) as e:
        logger.error("Failed to load stylesheet: %s", e)
        return None


# ================================================================================
# MAIN
# ================================================================================
def main() -> None:
    """Application entry point.

    Configures logging,loads styles, builds the application context,
    initializes the Qt application creates the main view, and starts the event loop.
    """
    # --- Setup ---
    setup_logging()

    ctx = build_context()
    stylesheet = load_stylesheet(STYLESHEET)

    # --- App ---
    app = QApplication(sys.argv)

    if stylesheet:
        app.setStyleSheet(stylesheet)

    main_view = MusicPlayerView(ctx)
    main_view.show()

    logger.info("Application started.")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
