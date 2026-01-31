"""Volume control UI components.

This module defines widgets responsible for displaying and controlling audio volume,
including a volume button, slider, and numeric label.
"""
from enum import Enum, auto
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QSlider, QWidget

from pyqt6_music_player.config import (
    HIGH_VOLUME_ICON_PATH,
    LOW_VOLUME_ICON_PATH,
    MEDIUM_VOLUME_ICON_PATH,
    MUTED_VOLUME_ICON_PATH,
)
from pyqt6_music_player.constants import MAX_VOLUME, MIN_VOLUME
from pyqt6_music_player.view_models import VolumeViewModel
from pyqt6_music_player.views import IconButton


# ================================================================================
# ENUMS
# ================================================================================
class VolumeLevel(Enum):
    """Represent discrete volume intensity levels."""

    MUTE = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()


# ================================================================================
# VOLUME CONTROLS
# ================================================================================
#
# --- WIDGETS ---
class VolumeButton(IconButton):
    """Button for controlling and displaying volume state.

    This button changes its icon based on the current volume level, and can be toggled
    to mute or unmute the audio.
    """

    HIGH_BOUNDARY = 67
    MEDIUM_BOUNDARY = 34
    LOW_BOUNDARY = 1

    def __init__(self, icon_path: Path = HIGH_VOLUME_ICON_PATH):
        """Initialize VolumeButton.

        Args:
            icon_path: Path to the icon file. Defaults to 'high-volume' icon.

        """
        super().__init__(icon_path=icon_path)
        self.volume_icons: dict[VolumeLevel, QIcon] = {}

        self._init_icons()
        self.setCheckable(True)

    def _init_icons(self):
        """Initialize volume icons."""
        self.volume_icons = {
            VolumeLevel.HIGH: self.path_to_qicon(HIGH_VOLUME_ICON_PATH),
            VolumeLevel.MEDIUM: self.path_to_qicon(MEDIUM_VOLUME_ICON_PATH),
            VolumeLevel.LOW: self.path_to_qicon(LOW_VOLUME_ICON_PATH),
            VolumeLevel.MUTE: self.path_to_qicon(MUTED_VOLUME_ICON_PATH),
        }

    def update_icon(self, new_volume: int) -> None:
        """Update instance icon based on the new volume's current level.

        Args:
            new_volume: The new volume.

        """
        if not (MIN_VOLUME <= new_volume <= MAX_VOLUME):
            raise ValueError(f"New volume: {new_volume} is out of range.")

        if new_volume >= self.HIGH_BOUNDARY:
            icon = self.volume_icons[VolumeLevel.HIGH]
        elif new_volume >= self.MEDIUM_BOUNDARY:
            icon = self.volume_icons[VolumeLevel.MEDIUM]
        elif new_volume >= self.LOW_BOUNDARY:
            icon = self.volume_icons[VolumeLevel.LOW]
        else:
            icon = self.volume_icons[VolumeLevel.MUTE]

        # Avoid unnecessary UI updates by skipping `setIcon` calls if the new,
        # and current icon are the same.
        if icon.cacheKey() == self.icon().cacheKey():
            return

        self.setIcon(icon)


class VolumeSlider(QSlider):
    """Horizontal slider for controlling the volume level.

    This slider is configured with a specific range (0-100),
    and a default value (100) for managing audio volume.
    """

    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal):
        """Initialize VolumeSlider.

        Args:
            orientation: VolumeSlider instance orientation.
                         Defaults to `Qt.Orientation.Horizontal` (horizontal).

        """
        super().__init__(orientation=orientation)
        self.setRange(MIN_VOLUME, MAX_VOLUME)


class VolumeLabel(QLabel):
    """A QLabel widget for displaying the current volume level.

    This label shows the volume as a number (0-100).
    """

    def __init__(self):
        """Initialize VolumeLabel."""
        super().__init__()

        self._configure_properties()

    def _configure_properties(self):
        """Configure instance's properties."""
        label_width = self.fontMetrics().horizontalAdvance("100") + 4

        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
        self.setFixedWidth(label_width)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)


# --- COMPONENT ---
class VolumeControls(QWidget):
    """A QWidget container for grouping volume widgets.

    This container also acts as the main view layer for volume and is responsible for:
     - Grouping and displaying volume UIs.
     - Handling volume-related input events by calling the appropriate viewmodel
       commands (View -> ViewModel).
     - Observing viewmodel layer for model updates (ViewModel -> View).
    """

    def __init__(self, volume_viewmodel: VolumeViewModel):
        """Initialize VolumeControls.

        Args:
            volume_viewmodel: The volume viewmodel.

        """
        super().__init__()
        # Volume viewmodel
        self._viewmodel = volume_viewmodel

        # Volume widgets
        self._volume_button = VolumeButton()
        self._volume_slider = VolumeSlider()
        self._volume_label = VolumeLabel()

        self._init_ui()
        self._bind_viewmodel()

    def _init_ui(self):
        """Initialize instance's internal widgets and layouts."""
        layout = QHBoxLayout()

        layout.addWidget(self._volume_button)
        layout.addWidget(self._volume_slider)
        layout.addWidget(self._volume_label)

        layout.setSpacing(5)

        self.setLayout(layout)

    def _bind_viewmodel(self) -> None:
        """Bind volume viewmodel to view."""
        # View -> ViewModel (user actions).
        self._volume_slider.valueChanged.connect(self._viewmodel.set_volume)
        self._volume_button.toggled.connect(self._viewmodel.set_mute)

        # ViewModel -> View (model updates).
        self._viewmodel.model_volume_changed.connect(self._on_model_volume_changed)
        self._viewmodel.model_mute_state_changed.connect(
            self._on_model_mute_state_changed,
        )

        # Refresh/re-emit to set UI initial state on startup.
        self._viewmodel.refresh()

    # --- Slots ---
    @pyqtSlot(int)
    def _on_model_volume_changed(self, new_volume: int) -> None:
        """Update volume widgets on model volume change."""
        # Update volume button icon.
        self._volume_button.blockSignals(True)
        self._volume_button.update_icon(new_volume)
        self._volume_button.blockSignals(False)

        # Update volume slider value.
        self._volume_slider.blockSignals(True)
        self._volume_slider.setValue(new_volume)
        self._volume_slider.blockSignals(False)

        # Update volume label display.
        self._volume_label.setNum(new_volume)

    @pyqtSlot(bool)
    def _on_model_mute_state_changed(self, is_muted: bool) -> None:
        """Update the volume button state on model mute state change."""
        self._volume_button.blockSignals(True)
        self._volume_button.setChecked(is_muted)
        self._volume_button.blockSignals(False)
