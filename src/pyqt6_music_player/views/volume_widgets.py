"""
Widgets for controlling and displaying the music player's volume.

This module provides UI components for volume control, including a volume button
that updates its icon based on the volume level, a slider to adjust the volume, and a
label to display the current volume value.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSizePolicy, QSlider

from pyqt6_music_player.config import (
    PLAYBACK_BUTTON_SMALL,
    VOLUME_DEFAULT,
    VOLUME_HIGH_ICON_PATH,
    VOLUME_LOW_ICON_PATH,
    VOLUME_MEDIUM_ICON_PATH,
    VOLUME_MUTE_ICON_PATH,
    VOLUME_RANGE,
)
from pyqt6_music_player.models.music_player_state import VolumeState
from pyqt6_music_player.views.base_widgets import IconButton, BaseLabel


class VolumeButton(IconButton):
    """
    A custom button for controlling and displaying the current volume state.

    This button changes its icon based on the volume level and can be toggled
    to mute or unmute the audio.
    """
    def __init__(self, volume_state: VolumeState):
        """Initializes the volume button."""
        super().__init__(
            icon_path=VOLUME_HIGH_ICON_PATH,
            widget_size=PLAYBACK_BUTTON_SMALL,
        )
        self.icons = {
            "mute": self._to_qicon(VOLUME_MUTE_ICON_PATH),
            "low": self._to_qicon(VOLUME_LOW_ICON_PATH),
            "medium": self._to_qicon(VOLUME_MEDIUM_ICON_PATH),
            "high": self._to_qicon(VOLUME_HIGH_ICON_PATH)
        }

        self.setCheckable(True)

        # Reflect volume state changes
        volume_state.volume_changed.connect(self._update_button_icon)

    def _update_button_icon(self, volume: int):
        """
        Updates the button's icon based on the given volume level.

        Args:
            volume: The current volume level (0-100).
        """
        if volume == 0:
            self.setIcon(self.icons["mute"])
        elif 1 <= volume <= 33:
            self.setIcon(self.icons["low"])
        elif 34 <= volume <= 66:
            self.setIcon(self.icons["medium"])
        else:
            self.setIcon(self.icons["high"])


class VolumeSlider(QSlider):
    """
    A horizontal slider for controlling the volume level.

    This slider is configured with a specific range (0-100) and a default value (100) for
    managing audio volume.
    """
    def __init__(self, volume_state: VolumeState, orientation=Qt.Orientation.Horizontal):
        """Initializes the volume slider."""
        super().__init__(orientation)

        self._configure_properties()

        # Reflect volume state changes
        volume_state.volume_changed.connect(self.setValue)

    def _configure_properties(self):
        """Configures the slider's properties"""
        self.setRange(*VOLUME_RANGE)
        self.setValue(VOLUME_DEFAULT)


class VolumeLabel(BaseLabel):
    """
    A label widget for displaying the current volume level.

    This label shows the volume as a number (0-100).
    """
    def __init__(self, volume_state: VolumeState):
        """
        Initializes the volume label.

        Args:
            volume_state: The music player state object containing the current volume.
        """
        super().__init__(
            label_text=str(volume_state.current_volume),
            alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter
        )
        self.state = volume_state

        self._configure_properties()

        # Reflect volume state changes
        volume_state.volume_changed.connect(lambda new_volume: self.setText(f"{new_volume}"))

    def _configure_properties(self):
        """Configures the label's properties"""
        label_width = self.fontMetrics().horizontalAdvance("100") + 4

        self.setFixedWidth(label_width)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
