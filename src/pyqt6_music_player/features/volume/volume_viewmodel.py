import logging

from PyQt6.QtCore import QObject, pyqtSignal

from .volume import Volume

logger = logging.getLogger(__name__)


class VolumeViewModel(QObject):
    """Expose volume state and commands to the view."""

    volume_changed = pyqtSignal(int)

    def __init__(self, volume_model: Volume):
        """Initialize VolumeViewModel and connect to Volume signals."""
        super().__init__()
        self._model = volume_model

        self._model.volume_changed.connect(self._on_volume_changed)

    # -- Public methods --
    @property
    def current_volume(self) -> int:
        return self._model.current_volume

    @property
    def min_volume(self) -> int:
        return self._model.min_volume

    @property
    def max_volume(self) -> int:
        return self._model.max_volume

    def set_volume(self, new_volume) -> None:
        """Set the volume.

        Args:
            new_volume: The volume value to set.

        """
        self._model.set_volume(new_volume)

    def set_mute(self, mute: bool) -> None:
        """Set the mute state.

        Args:
            mute: The mute state to set.

        """
        self._model.set_muted(mute)

    def _on_volume_changed(self, new_volume: int) -> None:
        self.volume_changed.emit(new_volume)  # type: ignore
