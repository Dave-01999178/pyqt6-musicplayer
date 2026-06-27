from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QHBoxLayout, QSlider, QWidget

from .volume_viewmodel import VolumeViewModel
from .volume_widgets import VolumeButton, VolumeLabel


class VolumeControlsPanel(QWidget):
    """A QWidget container for grouping volume widgets.

    This container also acts as the main view layer for volume controls including
    volume button, volume label and volume slider.
    """

    def __init__(self, volume_viewmodel: VolumeViewModel):
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
        #
        # PANEL LAYOUT: Horizontal box
        panel_layout = QHBoxLayout()

        # LEFT WIDGET: Volume button

        panel_layout.addWidget(self._volume_button)

        # MIDDLE WIDGET: Volume slider
        self._volume_slider.setOrientation(Qt.Orientation.Horizontal)
        self._volume_slider.setRange(
            self._viewmodel.min_volume,
            self._viewmodel.max_volume,
        )  # Fetch range from viewmodel

        panel_layout.addWidget(self._volume_slider)

        # RIGHT WIDGET: Volume label
        panel_layout.addWidget(self._volume_label)

        panel_layout.setSpacing(5)

        self.setLayout(panel_layout)

    def _connect_signals(self) -> None:
        # VolumeControlsPanel -> VolumeViewModel
        self._volume_slider.valueChanged.connect(self._viewmodel.set_volume)
        self._volume_button.toggled.connect(self._viewmodel.set_mute)

        # VolumeViewModel -> VolumeControlsPanel
        self._viewmodel.volume_changed.connect(self._on_volume_changed)

        # Initial Startup Sync: Read initial state from ViewModel
        self._on_volume_changed(self._viewmodel.current_volume)

    @pyqtSlot(int)
    def _on_volume_changed(self, new_volume: int) -> None:
        # Update volume button
        self._update_button(new_volume)

        # Update volume slider
        self._update_slider(new_volume)

        # Update volume label.
        self._volume_label.setNum(new_volume)

    def _update_button(self, new_volume: int) -> None:
        is_muted = new_volume == 0

        # Icon
        self._volume_button.update_icon(new_volume)

        # Toggle state
        self._volume_button.blockSignals(True)
        self._volume_button.setChecked(is_muted)
        self._volume_button.blockSignals(False)

    def _update_slider(self, new_volume: int) -> None:
        self._volume_slider.blockSignals(True)
        self._volume_slider.setValue(new_volume)
        self._volume_slider.blockSignals(False)
