import logging
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal

from pyqt6_music_player.core import (
    MAX_VOLUME,
    MIN_VOLUME,
)
from pyqt6_music_player.models import Track

logger = logging.getLogger(__name__)

# ================================================================================
# APP STATE/MODELS
# ================================================================================
#
# --- Playback state ---
@dataclass
class PlaybackState:
    current_track: Track | None = None
    track_index: int | None = None
    playback_status = None  # TODO: Sync value to audio player on startup


# --- Playlist model ---
class Playlist:
    """Manages playlist tracks and selection state."""

    def __init__(self) -> None:
        """Initialize PlaylistModel."""
        super().__init__()
        self._tracks: list[Track] = []  # TODO: Consider replacing list.
        self._track_paths: set[Path] = set()
        self._selected_index: int = -1  # -1 means no selection

    def set_selected_index(self, index: int) -> int | None:
        """Set the selected track index.

        Args:
            index: The row index to select.

        Returns:
            The updated index, or None if invalid or unchanged.

        """
        if index < -1 or index >= len(self._tracks):
            return None

        if self._selected_index == index:
            return None

        self._selected_index = index

        return self._selected_index

    def get_track_by_index(self, index: int) -> Track | None:
        """Get track at the specified index.

        Args:
            index: The track index.

        Returns:
            The track at index, or None if invalid.

        """
        if not (0 <= index < len(self._tracks)):
            return None

        return self._tracks[index]

    def has_track(self, track_path: Path) -> bool:
        """Check if playlist contains a track with the given path.

        Args:
            track_path: Path to check.

        Returns:
            True if track exists in playlist; Otherwise, False.

        """
        return Path(track_path) in self._track_paths

    def is_valid_index(self, index: int) -> bool:
        """Check if index is within playlist bounds.

        Args:
            index: Index to validate.

        Returns:
            True if index is valid; Otherwise, False

        """
        return 0 <= index < len(self._tracks)

    def add_tracks(self, tracks: Sequence[Track]) -> int:
        """Add tracks to the playlist.

        Args:
            tracks: Tracks to add.

        Returns:
            Number of tracks added.

        """
        add_count = 0

        for track in tracks:
            track_path = track.path

            # No duplicates
            if track_path in self._track_paths:
                continue

            self._tracks.append(track)
            self._track_paths.add(track_path)

            add_count += 1

        if add_count == 1:
            logger.info("Added track '%s' to the playlist.", tracks[0].title)
        else:
            logger.info("Added %d tracks to playlist.", add_count)

        return add_count

    # --- Properties ---
    @property
    def get_all_tracks(self) -> list[Track]:
        """Return all tracks in the playlist.

        Returns:
            A list of tracks.

        """
        return self._tracks.copy()

    @property
    def track_count(self) -> int:
        """Return the number of tracks in the playlist.

        Returns:
            The number of tracks in playlist.

        """
        return len(self._tracks)

    @property
    def selected_index(self) -> int:
        """Return the currently selected track index.

        Returns:
            The selected track index or -1 if none.

        """
        return self._selected_index


# --- Volume model ---
class VolumeModel(QObject):
    """Volume model.

    This class is responsible for managing volume, and providing volume related data.

    It notifies the viewmodel about model updates via Qt signals,
    provides methods and properties for viewmodel to interact with, and expose.
    """

    volume_changed = pyqtSignal(int)
    mute_changed = pyqtSignal(bool)

    def __init__(self):
        """Initialize VolumeModel instance."""
        super().__init__()
        self._current_volume: int = 100
        self._previous_volume: int | None = None
        self._is_muted: bool = False

    # --- Private methods ---
    def _update_mute_state(self, new_volume: int) -> None:
        """Update the model mute state based on the new volume.

        Set the mute state to True if the new volume is 0; otherwise, False.

        Args:
            new_volume: The new volume.

        """
        curr_mute_state = (new_volume == 0)

        if curr_mute_state != self._is_muted:
            self.mute_changed.emit(curr_mute_state)  # type: ignore

            self._is_muted = curr_mute_state

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
        self._update_mute_state(new_volume)

    def set_muted(self, muted: bool) -> None:
        """Set the current mute state based on the given new state.

        Args:
            muted: The new mute state after a volume button toggle (mute/unmute).

        """
        volume_to_use = 0 if muted else self._previous_volume

        self.set_volume(volume_to_use)

    # --- Properties ---
    @property
    def current_volume(self) -> int:
        """Return the current volume."""
        return self._current_volume
