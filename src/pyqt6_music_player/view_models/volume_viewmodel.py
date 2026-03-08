from PyQt6.QtCore import QObject, pyqtSignal

from pyqt6_music_player.models import VolumeModel


class VolumeViewModel(QObject):
    """Expose volume state and commands to the view."""

    model_volume_changed = pyqtSignal(int)
    model_mute_state_changed = pyqtSignal(bool)

    def __init__(self, volume_model: VolumeModel):
        """Initialize VolumeViewModel."""
        super().__init__()
        self._model = volume_model

        # Establish Model-ViewModel connection.
        self._connect_signals()

    # --- Public methods ---
    def set_volume(self, new_volume) -> None:
        """Command for updating model volume.

        Args:
            new_volume: The new volume value to set.

        """
        self._model.set_volume(new_volume)

    def set_mute(self, mute: bool) -> None:
        """Command for toggling model mute state.

        Args:
              mute: The new mute state to set.

        """
        self._model.set_muted(mute)

    # --- Protected/internal methods ---
    def _connect_signals(self):
        self._model.volume_changed.connect(self._on_model_volume_changed)
        self._model.mute_changed.connect(self._on_model_mute_changed)

    def _on_model_volume_changed(self, new_volume: int) -> None:
        self.model_volume_changed.emit(new_volume)  # type: ignore

    def _on_model_mute_changed(self, muted: bool) -> None:
        self.model_mute_state_changed.emit(muted)  # type: ignore

    def refresh(self) -> None:
        """Re-emit the current volume to refresh any subscribed views.

        Useful when view needs initial state sync.
        """
        self.model_volume_changed.emit(self._model.current_volume)  # type: ignore
