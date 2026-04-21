import logging

from PyQt6.QtCore import QObject, pyqtSignal

from pyqt6_music_player.models import Volume

logger = logging.getLogger(__name__)


class VolumeViewModel(QObject):
    """Expose volume state and commands to the view."""

    model_volume_changed = pyqtSignal(int)
    model_mute_state_changed = pyqtSignal(bool)

    def __init__(self, volume_model: Volume):
        """Initialize VolumeViewModel and connect to model signals."""
        super().__init__()
        self._model = volume_model

    # -- Public methods --
    def set_volume(self, new_volume) -> None:
        """Set the volume.

        Args:
            new_volume: The new volume value to set.

        """
        try:
            self._model.set_volume(new_volume)
            self._on_model_volume_changed(new_volume)
        except Exception:
            logger.exception("Unexpected error while changing volume.")

    def set_mute(self, mute: bool) -> None:
        """Set the mute state.

        Args:
              mute: The new mute state to set.

        """
        try:
            new_volume = self._model.set_muted(mute)

            self._on_model_volume_changed(new_volume)
            self._on_model_mute_changed(mute)
        except Exception:
            logger.exception("Unexpected error while changing mute state.")

    def refresh(self) -> None:
        """Re-emit the current volume for initial state sync."""
        self.model_volume_changed.emit(self._model.current_volume)  # type: ignore

    def _on_model_volume_changed(self, new_volume: int) -> None:
        self.model_volume_changed.emit(new_volume)  # type: ignore

    def _on_model_mute_changed(self, muted: bool) -> None:
        self.model_mute_state_changed.emit(muted)  # type: ignore
