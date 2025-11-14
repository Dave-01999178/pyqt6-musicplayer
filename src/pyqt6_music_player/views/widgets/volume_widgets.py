"""
This module provides UI components for volume control, including a custom volume icon button
that updates its icon based on the current volume level and can be toggled to mute and unmute
the audio, a slider to adjust the volume, and a label to display the current volume value.
"""
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QLabel, QSizePolicy, QSlider

from pyqt6_music_player.config import (
    HIGH_VOLUME_ICON_PATH,
    LOW_VOLUME_ICON_PATH,
    MEDIUM_VOLUME_ICON_PATH,
    MUTED_VOLUME_ICON_PATH,
)
from pyqt6_music_player.constants import MAX_VOLUME, MIN_VOLUME
from pyqt6_music_player.views import IconButton, path_to_qicon


class VolumeButton(IconButton):
    """
    A custom button for controlling and displaying the current volume state.

    This button changes its icon based on the volume level and can be toggled
    to mute or unmute the audio.
    """
    # TODO: Consider moving class constants to a dataclass or similar containers for reusability.
    _LOW_LOWER_BOUND = 1
    _MEDIUM_LOWER_BOUND = 34
    _HIGH_LOWER_BOUND = 67

    # TODO: Consider using Enum + Mapping.
    _VOLUME_ICONS = {
        "mute": path_to_qicon(MUTED_VOLUME_ICON_PATH),
        "low": path_to_qicon(LOW_VOLUME_ICON_PATH),
        "medium": path_to_qicon(MEDIUM_VOLUME_ICON_PATH),
        "high": path_to_qicon(HIGH_VOLUME_ICON_PATH)
    }

    def __init__(self, icon_path: Path = HIGH_VOLUME_ICON_PATH):
        """
        Initializes VolumeButton instance.

        Args:
            icon_path: Path to the icon file. Defaults to 'high-volume' icon.
        """
        super().__init__(icon_path=icon_path)
        self.current_icon: QIcon = self._VOLUME_ICONS["high"]  # Default

        self.setCheckable(True)

    def update_button_icon(self, new_volume: int) -> None:
        """
        The VolumeButton's public interface for updating its icon.

        This updates the button's icon based on the new volume level.

        Args:
            new_volume: The current volume level (0-100).
        """
        if not (MIN_VOLUME <= new_volume <= MAX_VOLUME):
            raise ValueError(f"New volume: {new_volume} is out of range.")

        if new_volume >= self._HIGH_LOWER_BOUND:
            icon = self._VOLUME_ICONS["high"]
        elif new_volume >= self._MEDIUM_LOWER_BOUND:
            icon = self._VOLUME_ICONS["medium"]
        elif new_volume >= self._LOW_LOWER_BOUND:
            icon = self._VOLUME_ICONS["low"]
        else:
            icon = self._VOLUME_ICONS["mute"]

        # Avoid unnecessary UI updates by skipping `setIcon` calls if the new, and current icon
        # are the same.
        if icon.cacheKey() == self.current_icon.cacheKey():
            return None

        self.setIcon(icon)
        self.current_icon = icon


class VolumeSlider(QSlider):
    """
    A horizontal slider for controlling the volume level.

    This slider is configured with a specific range (0-100) and a default value (100) for
    managing audio volume.
    """
    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal):
        """
        Initializes VolumeSlider instance.

        Args:
            orientation: VolumeSlider instance orientation.
                         Defaults to `Qt.Orientation.Horizontal` (horizontal).
        """
        super().__init__(orientation=orientation)

        self._configure_properties()

    def _configure_properties(self):
        """Configures the instance's properties"""
        self.setRange(MIN_VOLUME, MAX_VOLUME)
        self.setValue(MAX_VOLUME)


class VolumeLabel(QLabel):
    """
    A label widget for displaying the current volume level.

    This label shows the volume as a number (0-100).
    """
    def __init__(self, display_text: str = str(MAX_VOLUME)):
        """
        Initializes VolumeLabel instance.

        Args:
            display_text: VolumeLabel instance display text. Defaults to `MAX_VOLUME` (100).
        """
        super().__init__(text=display_text)

        self._configure_properties()

    def _configure_properties(self):
        """Configures the instance properties"""
        label_width = self.fontMetrics().horizontalAdvance("100") + 4

        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
        self.setFixedWidth(label_width)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
