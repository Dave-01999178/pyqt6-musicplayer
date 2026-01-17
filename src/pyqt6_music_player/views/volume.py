from enum import Enum, auto
from pathlib import Path

from PyQt6.QtCore import Qt
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


class VolumeLevel(Enum):
    MUTE = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()


# ================================================================================
# VOLUME WIDGETS
# ================================================================================
#
# --- Volume button ---
class VolumeButton(IconButton):
    """A custom button for controlling and displaying the current volume state.

    This button changes its icon based on the volume level and can be toggled
    to mute or unmute the audio.
    """

    HIGH_LOWER_BOUND = 67
    MEDIUM_LOWER_BOUND = 34
    LOW_LOWER_BOUND = 1

    def __init__(self, icon_path: Path = HIGH_VOLUME_ICON_PATH):
        """Initialize VolumeButton instance.

        Args:
            icon_path: Path to the icon file. Defaults to 'high-volume' icon.

        """
        super().__init__(icon_path=icon_path)
        self.volume_icons: dict[VolumeLevel, QIcon] = {}

        self._init_icons()

        self.setCheckable(True)

    def _init_icons(self):
        self.volume_icons = {
            VolumeLevel.HIGH: self.path_to_qicon(HIGH_VOLUME_ICON_PATH),
            VolumeLevel.MEDIUM: self.path_to_qicon(MEDIUM_VOLUME_ICON_PATH),
            VolumeLevel.LOW: self.path_to_qicon(LOW_VOLUME_ICON_PATH),
            VolumeLevel.MUTE: self.path_to_qicon(MUTED_VOLUME_ICON_PATH),
        }

    def update_button_icon(self, new_volume: int) -> None:
        """Update the button's icon based on the new volume level.

        Args:
            new_volume: The current volume level (0-100).

        """
        if not (MIN_VOLUME <= new_volume <= MAX_VOLUME):
            raise ValueError(f"New volume: {new_volume} is out of range.")

        if new_volume >= self.HIGH_LOWER_BOUND:
            icon = self.volume_icons[VolumeLevel.HIGH]
        elif new_volume >= self.MEDIUM_LOWER_BOUND:
            icon = self.volume_icons[VolumeLevel.MEDIUM]
        elif new_volume >= self.LOW_LOWER_BOUND:
            icon = self.volume_icons[VolumeLevel.LOW]
        else:
            icon = self.volume_icons[VolumeLevel.MUTE]

        # Avoid unnecessary UI updates by skipping `setIcon` calls if the new,
        # and current icon are the same.
        if icon.cacheKey() == self.icon().cacheKey():
            return

        self.setIcon(icon)


# TODO: Volume slider and display should get their default values from model
#  (default value) on app start.
# --- Volume slider ---
class VolumeSlider(QSlider):
    """A horizontal slider for controlling the volume level.

    This slider is configured with a specific range (0-100),
    and a default value (100) for managing audio volume.
    """

    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal):
        """Initialize VolumeSlider instance.

        Args:
            orientation: VolumeSlider instance orientation.
                         Defaults to `Qt.Orientation.Horizontal` (horizontal).

        """
        super().__init__(orientation=orientation)

        self._configure_properties()

    def _configure_properties(self):
        """Configure the instance's properties."""
        self.setRange(MIN_VOLUME, MAX_VOLUME)


# --- Volume display ---
class VolumeLabel(QLabel):
    """A label widget for displaying the current volume level.

    This label shows the volume as a number (0-100).
    """

    def __init__(self):
        """Initialize VolumeLabel instance."""
        super().__init__()

        self._configure_properties()

    def _configure_properties(self):
        """Configure the instance properties."""
        label_width = self.fontMetrics().horizontalAdvance("100") + 4

        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
        self.setFixedWidth(label_width)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)


# ================================================================================
# VOLUME CONTROLS
# ================================================================================
class VolumeControls(QWidget):
    """A QWidget container for grouping volume-related widgets.

    This container also acts as the main view layer for volume and is responsible for:
     - Displaying volume UIs.
     - Handling volume-related input events by calling the appropriate volume viewmodel
       commands (View -> ViewModel).
     - Observing volume viewmodel layer for data/state changes (ViewModel -> View).
    """

    def __init__(self, volume_viewmodel: VolumeViewModel):
        """Initialize VolumeControls instance."""
        super().__init__()
        self._viewmodel = volume_viewmodel

        self._volume_button = VolumeButton()
        self._volume_slider = VolumeSlider()
        self._volume_label = VolumeLabel()

        self._init_ui()
        self._setup_binding()

    def _init_ui(self):
        """Initialize the instance's internal widgets and layouts."""
        layout = QHBoxLayout()

        layout.addWidget(self._volume_button)
        layout.addWidget(self._volume_slider)
        layout.addWidget(self._volume_label)

        layout.setSpacing(5)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    def _setup_binding(self) -> None:
        # View -> ViewModel (user actions)
        self._volume_button.toggled.connect(self._viewmodel.set_mute)
        self._volume_slider.valueChanged.connect(self._viewmodel.set_volume)

        # ViewModel -> View (models updates)
        self._viewmodel.mute_changed.connect(self._volume_button.setChecked)
        self._viewmodel.volume_changed.connect(self._on_volume_changed)

        # Refresh/re-emit to set UI initial state on startup.
        self._viewmodel.refresh()

    def _on_volume_changed(self, new_volume: int) -> None:
        # Update the button icon based on the new volume's range.
        self._volume_button.blockSignals(True)
        self._volume_button.update_button_icon(new_volume)
        self._volume_button.blockSignals(False)

        # Update slider to reflect the new volume.
        self._volume_slider.blockSignals(True)
        self._volume_slider.setValue(new_volume)
        self._volume_slider.blockSignals(False)

        # Update label to display the new volume.
        self._volume_label.setNum(new_volume)

    # --- Getter method for tests ---
    @property
    def volume_button(self) -> IconButton:
        return self._volume_button

    @property
    def volume_slider(self) -> QSlider:
        return self._volume_slider

    @property
    def volume_label(self) -> QLabel:
        return self._volume_label
