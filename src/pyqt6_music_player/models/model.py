import logging
from collections.abc import Sequence
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal

from pyqt6_music_player.constants import (
    MAX_VOLUME,
    MIN_VOLUME,
    SUPPORTED_AUDIO_FORMAT,
)
from pyqt6_music_player.models import Track

logger = logging.getLogger(__name__)

# ================================================================================
# APP MODELS
# ================================================================================
#
# --- Playlist model ---
class PlaylistModel(QObject):
    """The playlist model.

    This class is responsible for managing playlist, and providing playlist
    related data.
    """

    playlist_changed = pyqtSignal(int)  # TODO: Rename to song_added.
    selected_index_changed = pyqtSignal(int)
    playing_index_changed = pyqtSignal(int)

    def __init__(self) -> None:
        """Initialize PlaylistModel instance."""
        super().__init__()
        self._playlist: list[Track] = []  # TODO: Consider replacing list.
        self._playlist_set: set[Path] = set()

        self._selected_index: int | None = None
        self._playing_index: int | None = None

    # --- Private methods ---
    @staticmethod
    def _normalize_to_paths(files: Sequence[str | Path]) -> list[Path]:
        """Convert valid path-like inputs into a Path object.

        Args:
            files: A sequence of path-like objects.

        Returns:
            list[Path]: The normalized input as Path objects stored in a list.

        Raises:
            TypeError: If the list contains unsupported types,
                       or if the argument type is not supported.

        """
        normalized_paths = []
        for file_path in files:
            # Ignore the strings that could point to directories/cwd.
            if file_path in {"", "."}:
                continue

            path = Path(file_path)

            # Skip cwd ('.'), empty values, or directories
            if path in {Path(""), Path(".")} or path.is_dir():
                continue

            normalized_paths.append(path)

        return normalized_paths

    # --- Public methods ---
    def add_songs(self, files: Sequence[str | Path]) -> None:
        """Add one or more audio files to the playlist.

        Supported extensions: .mp3, .wav, .flac, .ogg

        Args:
            files: A sequence of path-like objects.

        """
        if not files or files is None:
            return

        # Allow single str/Path input by wrapping into a list.
        if isinstance(files, (str | Path)):
            files = [files]

        paths = self._normalize_to_paths(files)
        from_path = Track.from_path  # Store locally to avoid repeated lookups.
        add_count = 0
        for p in paths:
            try:
                resolved_path = p.resolve(strict=True)
            except FileNotFoundError:
                continue

            is_new = resolved_path not in self._playlist_set
            is_supported = resolved_path.suffix.lower() in SUPPORTED_AUDIO_FORMAT
            if is_new and is_supported:
                song = from_path(resolved_path)

                if song is not None:
                    self._playlist.append(song)
                    self._playlist_set.add(resolved_path)
                    add_count += 1

        if add_count != 0:
            self.playlist_changed.emit(add_count)

            logger.info("%s song(s) was added to the playlist.", add_count)

    def set_selected_index(self, index: int) -> None:
        """Set the currently selected playlist index.

        This updates the internal pointer based on the index of the selected item
        in playlist widget.

        The internal pointer is used for retrieving ``Song`` objects from the internal
        playlist.

        Args:
            index: The index of the selected item in the playlist widget.

        Raises:
            TypeError: If the given index is not an integer.

        """

        if 0 <= index < len(self._playlist):
            self._selected_index = index

            self.selected_index_changed.emit(self._selected_index)

    def set_playing_index(self, index: int):
        if 0 <= index < len(self._playlist):
            self._playing_index = index

    def next_track(self):
        if self._playing_index is None:
            return

        next_index = self._playing_index + 1
        if 0 <= next_index < len(self._playlist):
            self.set_selected_index(next_index)

            self.set_playing_index(next_index)
            self.playing_index_changed.emit(next_index)

    def prev_track(self):
        if self._playing_index is None:
            return

        prev_index = self._playing_index - 1
        if 0 <= prev_index < len(self._playlist):
            self.set_selected_index(prev_index)

            self.set_playing_index(prev_index)
            self.playing_index_changed.emit(prev_index)

    def get_track(self, index) -> Track | None:
        if self._playlist is None or not (0 <= index < len(self._playlist)):
            return None

        return self._playlist[index]

    # --- Properties ---
    @property
    def playlist(self) -> list[Track]:
        """Return the current playlist."""
        return self._playlist.copy()

    @property
    def playlist_set(self) -> set[Path]:
        """Return the set version of playlist, used for membership checks."""
        return self._playlist_set

    @property
    def selected_index(self) -> int | None:
        """Return the active playlist index, or None if the playlist is empty."""
        if not self._playlist:
            return None

        return self._selected_index

    @property
    def selected_track(self) -> Track | None:
        """Return the currently selected track based on the active playlist index.

        If no track is selected or the playlist is empty, this property returns
        ``None``. A valid selection occurs only when the internal index is set
        and falls within the bounds of the playlist.

        Returns:
            Track | None: The selected track from the model,
                         or ``None`` if the playlist is empty, or nothing is selected.

        """
        if self._selected_index is not None:
            return self._playlist[self._selected_index]

        return None

    @property
    def track_playing(self) -> Track | None:
        if self._playing_index is not None:
            return self._playlist[self._playing_index]

        return None

    @property
    def song_count(self) -> int:
        """Return the current number of songs in playlist."""
        return len(self._playlist)


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
