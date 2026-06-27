from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QLabel

from pyqt6_music_player.core import ASSETS_PATH, IconButton

# ==================== CONSTANTS ====================
HIGH_VOLUME_ICON = ASSETS_PATH / "volume_high.svg"
MEDIUM_VOLUME_ICON = ASSETS_PATH / "volume_medium.svg"
LOW_VOLUME_ICON = ASSETS_PATH / "volume_low.svg"
MUTED_VOLUME_ICON = ASSETS_PATH / "volume_muted.svg"
VOLUME_BTN_SIZE = (30, 30)
VOLUME_BTN_ICON_SIZE = (15, 15)


# ==================== WIDGETS ====================
class VolumeButton(IconButton):
    """Button for controlling and displaying volume state.

    This button changes its icon based on the current volume level, and can be toggled
    to mute or unmute the audio.
    """

    def __init__(
            self,
            icon_path: Path = HIGH_VOLUME_ICON,
            icon_size: tuple[int, int] = VOLUME_BTN_ICON_SIZE,
            widget_size: tuple[int, int] = VOLUME_BTN_SIZE,
    ):
        """Initialize VolumeButton.

        Args:
            icon_path: Path to the icon file. Defaults to 'high-volume' icon.
            icon_size: Size of the icon inside the button as
                       (width, height) in pixels. Defaults to (15, 15).
            widget_size: Size of the entire button widget as (width, height) in pixels.
                         Defaults to (30, 30).

        """
        super().__init__(
            icon_path=icon_path,
            icon_size=icon_size,
            widget_size=widget_size,
        )
        self._current_icon = icon_path

        self.setCheckable(True)

    # -- Public methods --
    def update_icon(self, new_volume: int) -> None:
        """Update instance icon based on the new volume's current level.

        Args:
            new_volume: The new volume.

        """
        high_threshold = 67
        medium_threshold = 34
        low_threshold = 1

        if new_volume >= high_threshold:
            icon = HIGH_VOLUME_ICON
        elif new_volume >= medium_threshold:
            icon = MEDIUM_VOLUME_ICON
        elif new_volume >= low_threshold:
            icon = LOW_VOLUME_ICON
        else:
            icon = MUTED_VOLUME_ICON

        # Update icon only if it is new
        if icon == self._current_icon:
            return

        self.setIcon(QIcon(str(icon)))

        self._current_icon = icon


class VolumeLabel(QLabel):
    """QLabel widget for displaying the current volume level.

    This label shows the volume as a number (0-100).
    """

    def __init__(self):
        """Initialize VolumeLabel."""
        super().__init__()

        self._configure_properties()

    # -- Protected/internal methods --
    def _configure_properties(self):
        # Set the instance width to the length of "100" + 4 character spaces
        # to center the text and avoid the weird behaviour when the text is "0"
        label_width = self.fontMetrics().horizontalAdvance("100")

        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
        self.setFixedWidth(label_width)
