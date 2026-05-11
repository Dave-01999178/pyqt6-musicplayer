from pyqt6_music_player.core.signals import Signal


class Volume:
    """Volume model.

    This class is responsible for managing volume, and providing volume related data.

    It notifies the viewmodel about model updates via Qt signals,
    provides methods and properties for viewmodel to interact with, and expose.
    """

    volume_changed = Signal()

    def __init__(self):
        """Initialize VolumeModel."""
        super().__init__()
        self._current_volume: int = 100
        self._previous_volume: int | None = None

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
        clamped_volume = max(0, min(100, new_volume))

        self._previous_volume = self._current_volume
        self._current_volume = clamped_volume

        self.volume_changed.emit(self._current_volume)

    def set_muted(self, muted: bool) -> int:
        """Set the current mute state based on the given new state.

        Args:
            muted: The new mute state after a volume button toggle (mute/unmute).

        """
        volume_to_use = 0 if muted else self._previous_volume

        self.set_volume(volume_to_use)

        return volume_to_use
