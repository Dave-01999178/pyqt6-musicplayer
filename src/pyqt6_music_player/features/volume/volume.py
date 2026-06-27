from pyqt6_music_player.core import Signal

MIN_VOL = 0
MAX_VOL = 100


class Volume:
    """Volume model.

    This class is responsible for managing volume, and providing volume related data.

    It notifies the viewmodel about model updates via Qt signals,
    provides methods and properties for viewmodel to interact with, and expose.
    """

    volume_changed = Signal()

    def __init__(self):
        super().__init__()
        self._current_volume: int = MAX_VOL
        self._previous_volume: int | None = None

        # Source of truth for boundaries
        self._min_volume: int = MIN_VOL
        self._max_volume: int = MAX_VOL

    # --- Properties ---
    @property
    def current_volume(self) -> int:
        return self._current_volume

    @property
    def min_volume(self) -> int:
        return self._min_volume

    @property
    def max_volume(self) -> int:
        return self._max_volume

    # --- Public methods ---
    def set_volume(self, volume: int) -> None:
        """Set the current volume to the given value.

        Args:
            volume: The value after a volume button,
                    or slider event (toggle/seek).

        """
        clamped_volume = max(self._min_volume, min(self._max_volume, volume))

        self._previous_volume = self._current_volume
        self._current_volume = clamped_volume

        self.volume_changed.emit(self._current_volume)

    def set_muted(self, muted: bool) -> None:
        """Set the current mute state to the given state.

        Args:
            muted: The mute state after a volume button toggle (mute/unmute).

        """
        volume_to_use = 0 if muted else self._previous_volume

        self.set_volume(volume_to_use)
