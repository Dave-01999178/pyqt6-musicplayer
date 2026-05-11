from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QHBoxLayout, QSlider, QWidget

from pyqt6_music_player.core import DEFAULT_SLIDER_RANGE
from pyqt6_music_player.widgets import VolumeButton, VolumeLabel

from .volume_viewmodel import VolumeViewModel


class VolumeControlsPanel(QWidget):
    """A QWidget container for grouping volume widgets.

    This container also acts as the main view layer for volume and is responsible for:
     - Organizing and displaying volume widgets.
     - Handling volume widgets input events by calling the appropriate viewmodel
       commands (View -> ViewModel).
     - Displaying current volume state and information.

    """

    def __init__(self, volume_viewmodel: VolumeViewModel):
        """Initialize VolumeControlsPanel.

        Args:
            volume_viewmodel: The volume viewmodel.

        """
        super().__init__()
        # Viewmodel
        self._viewmodel = volume_viewmodel

        # Widgets
        self._volume_button = VolumeButton()
        self._volume_slider = QSlider()
        self._volume_label = VolumeLabel()

        # Setup
        self._init_ui()
        self._connect_signals()

    # -- Protected/internal methods --
    def _init_ui(self) -> None:
        # Setup instance widgets and layout
        main_layout_horizontal = QHBoxLayout()

        # Left widget: Volume button
        main_layout_horizontal.addWidget(self._volume_button)

        # Middle widget: Volume slider
        self._volume_slider.setOrientation(Qt.Orientation.Horizontal)
        self._volume_slider.setRange(*DEFAULT_SLIDER_RANGE)

        main_layout_horizontal.addWidget(self._volume_slider)

        # Right widget: Volume label
        main_layout_horizontal.addWidget(self._volume_label)

        main_layout_horizontal.setSpacing(5)

        self.setLayout(main_layout_horizontal)

    def _connect_signals(self) -> None:
        # Establish VolumeControlsPanel-VolumeViewModel connection.
        #
        # VolumeControlsPanel -> VolumeViewModel
        self._volume_slider.valueChanged.connect(self._viewmodel.set_volume)
        self._volume_button.toggled.connect(self._viewmodel.set_mute)

        # VolumeViewModel -> VolumeControlsPanel
        self._viewmodel.model_volume_changed.connect(self._on_model_volume_changed)
        self._viewmodel.model_mute_state_changed.connect(
            self._on_model_mute_state_changed,
        )

        # Refresh/re-emit to set UI initial state on startup.
        self._viewmodel.refresh()

    @pyqtSlot(int)
    def _on_model_volume_changed(self, new_volume: int) -> None:
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
        self._volume_button.blockSignals(True)
        self._volume_button.setChecked(is_muted)
        self._volume_button.blockSignals(False)
