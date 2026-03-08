from PyQt6.QtCore import QObject, pyqtSignal

from pyqt6_music_player.core import MAX_VOLUME, MIN_VOLUME


class VolumeModel(QObject):
    """Volume model.

    This class is responsible for managing volume, and providing volume related data.

    It notifies the viewmodel about model updates via Qt signals,
    provides methods and properties for viewmodel to interact with, and expose.
    """

    volume_changed = pyqtSignal(int)
    mute_changed = pyqtSignal(bool)

    def __init__(self):
        """Initialize VolumeModel."""
        super().__init__()
        self._current_volume: int = 100
        self._previous_volume: int | None = None
        self._is_muted: bool = False

    # --- Properties ---
    @property
    def current_volume(self) -> int:
        """Return the current volume."""
        return self._current_volume

    # --- Public methods ---
    def set_volume(self, new_volume: int) -> None:
        """Set the current volume to a new one based on the given value.

        Args:
            new_volume: The new volume after volume button,
                        or slider event (toggle/seek).

        Raises:
            ValueError: If the new volume is out of range.

        """
        if not (MIN_VOLUME <= new_volume <= MAX_VOLUME):
            raise ValueError(
                f"Volume {new_volume} is out of range [{MIN_VOLUME}-{MAX_VOLUME}].",
            )

        self._previous_volume = self._current_volume
        self._current_volume = new_volume

        self.volume_changed.emit(new_volume)  # type: ignore

        curr_mute_state = (new_volume == 0)

        if curr_mute_state != self._is_muted:
            self.mute_changed.emit(curr_mute_state)  # type: ignore

            self._is_muted = curr_mute_state

    def set_muted(self, muted: bool) -> None:
        """Set the current mute state based on the given new state.

        Args:
            muted: The new mute state after a volume button toggle (mute/unmute).

        """
        volume_to_use = 0 if muted else self._previous_volume

        self.set_volume(volume_to_use)
