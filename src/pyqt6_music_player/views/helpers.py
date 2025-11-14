import logging
from pathlib import Path

from PyQt6.QtGui import QIcon


def path_to_qicon(icon_path: Path) -> QIcon:
    try:
        return QIcon(str(icon_path))
    except Exception as e:
        logging.error("Icon path: %s not found, %s", icon_path, e)
        return QIcon()  # Empty QIcon() fallback instead of None for mypy incompatible type error.
