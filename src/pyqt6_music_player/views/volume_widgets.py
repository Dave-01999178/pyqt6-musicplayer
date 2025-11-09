"""
This module provides UI components for volume control, including a custom volume icon button
that updates its icon based on the current volume level and can be toggled to mute and unmute
the audio, a slider to adjust the volume, and a label to display the current volume value.
"""
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QSizePolicy, QSlider

from pyqt6_music_player.config import (
    HIGH_VOLUME_ICON_PATH,
    LOW_VOLUME_ICON_PATH,
    MEDIUM_VOLUME_ICON_PATH,
    MUTED_VOLUME_ICON_PATH,
    VOLUME_BUTTON_ICON_SIZE,
    VOLUME_BUTTON_SIZE,
    VOLUME_RANGE
)
from pyqt6_music_player.constant import DEFAULT_VOLUME
from pyqt6_music_player.views import IconButton


# TODO: Check if `volume_icon` and `update_button_icon` implementation could be improved
#  or simplified.
class VolumeButton(IconButton):
    """
    A custom button for controlling and displaying the current volume state.

    This button changes its icon based on the volume level and can be toggled
    to mute or unmute the audio.
    """
    def __init__(
            self,
            icon: Path = HIGH_VOLUME_ICON_PATH,
            icon_size: tuple[int, int] = VOLUME_BUTTON_ICON_SIZE,
            widget_size: tuple[int, int] = VOLUME_BUTTON_SIZE,
            object_name: str | None = None
    ):
        """
        Initializes VolumeButton instance.
        
        Args:
            icon: Icon image path. Defaults to 'high volume' icon.
            icon_size: Width and height of the icon.
                       Defaults to `VOLUME_BUTTON_ICON_SIZE` (15, 15).
            widget_size: VolumeButton instance width and height.
                         Defaults to `VOLUME_BUTTON_SIZE` (30, 30).
            object_name: VolumeButton instance object name, useful for QSS styling.
                         Defaults to None.
        """
        super().__init__(
            icon_path=icon,
            icon_size=icon_size,
            widget_size=widget_size,
            object_name=object_name
        )
        self._volume_icons = {
            "mute": self.to_qicon(MUTED_VOLUME_ICON_PATH),
            "low": self.to_qicon(LOW_VOLUME_ICON_PATH),
            "medium": self.to_qicon(MEDIUM_VOLUME_ICON_PATH),
            "high": self.to_qicon(HIGH_VOLUME_ICON_PATH)
        }

        self.setCheckable(True)

    def update_button_icon(self, new_volume: int) -> None:
        """
        The VolumeButton's public interface for updating its icon.

        This updates the button's icon based on the new volume level.

        Args:
            new_volume: The current volume level (0-100).
        """
        if new_volume == 0:
            self.setIcon(self._volume_icons["mute"])
        elif 1 <= new_volume <= 33:
            self.setIcon(self._volume_icons["low"])
        elif 34 <= new_volume <= 66:
            self.setIcon(self._volume_icons["medium"])
        else:
            self.setIcon(self._volume_icons["high"])


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
        self.setRange(*VOLUME_RANGE)
        self.setValue(DEFAULT_VOLUME)


class VolumeLabel(QLabel):
    """
    A label widget for displaying the current volume level.

    This label shows the volume as a number (0-100).
    """
    def __init__(self, display_text: str = str(DEFAULT_VOLUME)):
        """
        Initializes VolumeLabel instance.

        Args:
            display_text: VolumeLabel instance display text. Defaults to `DEFAULT_VOLUME` (100).
        """
        super().__init__(text=display_text)

        self._configure_properties()

    def _configure_properties(self):
        """Configures the instance properties"""
        label_width = self.fontMetrics().horizontalAdvance("100") + 4

        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
        self.setFixedWidth(label_width)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
