from pathlib import Path
from typing import Sequence

from PyQt6.QtCore import QObject, pyqtSignal

from pyqt6_music_player.constants import (
    MIN_VOLUME,
    MAX_VOLUME,
    SUPPORTED_AUDIO_FORMAT
)
from pyqt6_music_player.models import AudioTrack


# ================================================================================
# APP MODELS
# ================================================================================
#
# ---------- Playlist model ----------
class PlaylistModel(QObject):
    playlist_changed = pyqtSignal(int)
    """
    The app's playlist model that is responsible for managing playlist,
    and providing playlist related data.
    """
    def __init__(self) -> None:
        super().__init__()
        self._playlist: list[AudioTrack] = []  # TODO: Consider replacing list.
        self._playlist_set: set[Path] = set()

        self._current_index: int | None = None

    @property
    def playlist(self) -> list[AudioTrack]:
        """Returns the current playlist"""
        return self._playlist.copy()

    @property
    def playlist_set(self) -> set[Path]:
        """Returns the set version of playlist, used for fast membership checks."""
        return self._playlist_set

    @property
    def song_count(self) -> int:
        """Returns the current number of songs in playlist."""
        return len(self._playlist)

    @property
    def selected_song(self) -> AudioTrack | None:
        """
        Returns the currently selected song based on the active playlist index.

        If no song is selected or the playlist is empty, this property returns
        ``None``. A valid selection occurs only when the internal index is set
        and falls within the bounds of the playlist.

        Returns:
            AudioTrack | None: The selected song from the model,
                         or ``None`` if the playlist is empty, or nothing is selected.
        """
        if self._current_index is not None:
            return self._playlist[self._current_index]

        return None

    @staticmethod
    def _normalize_to_paths(files: Sequence[str | Path]) -> list[Path]:
        """
        Converts valid path-like inputs into a Path object.

        Args:
            files: A sequence of path-like objects.

        Returns:
            list[Path]: The normalized input as Path objects stored in a list.

        Raises:
            TypeError: If the list contains unsupported types or if the argument type is not
                       supported.
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

    def add_song(self, files: Sequence[str | Path]) -> None:
        """
        Adds one or more audio files to the playlist.

        Supported extensions: .mp3, .wav, .flac, .ogg

        Args:
            files: A sequence of path-like objects.
        """
        if not files:
            return

        # Allow single str/Path input by wrapping into a list.
        if isinstance(files, (str, Path)):
            files = [files]

        paths = self._normalize_to_paths(files)

        from_path = AudioTrack.from_path  # Store locally to avoid repeated attribute lookups.
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
            self.playlist_changed.emit(add_count)  # type: ignore

        return None

    def set_selected_index(self, index: int) -> None:
        """
        Sets the currently selected playlist index.

        This updates the internal pointer based on the index of the selected item in playlist
        widget. The internal pointer is used for retrieving ``Song`` objects from the internal
        playlist.

        Args:
            index: The index of the selected item in the playlist widget.

        Raises:
            TypeError: If the given index is not an integer.
        """
        if not isinstance(index, int) or isinstance(index, bool):
            raise TypeError("Index must be an integer.")

        if 0 <= index < len(self._playlist):
            self._current_index = index

        return None


# ---------- Volume model ----------
class VolumeModel(QObject):
    """
    The app's volume model that is responsible for managing volume,
    and providing volume related data.
    """
    volume_changed = pyqtSignal(int)
    mute_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._current_volume = MAX_VOLUME
        self._previous_volume = self._current_volume
        self._is_muted = False

    @property
    def current_volume(self) -> int:
        """Returns the current volume."""
        return self._current_volume

    @property
    def previous_volume(self) -> int:
        """Returns the previous volume."""
        return self._previous_volume

    @property
    def is_muted(self) -> bool:
        """Returns the current mute state."""
        return self._is_muted

    def set_volume(self, new_volume: int) -> None:
        """
        Sets the current volume to a new one based on the given value.

        Args:
            new_volume: The new volume after a volume button or slider event (toggle/seek).

        Raises:
            ValueError: If the new volume is out of range.
        """
        if not (MIN_VOLUME <= new_volume <= MAX_VOLUME):
            raise ValueError(f"Volume {new_volume} is out of range [{MIN_VOLUME}-{MAX_VOLUME}].")

        # Modify the volume only if it is new.
        if new_volume != self.current_volume:
            self._previous_volume = self._current_volume
            self._current_volume = new_volume

            self.volume_changed.emit(new_volume)  # type: ignore

            new_state = (new_volume == 0)
            if new_state != self._is_muted:
                self._is_muted = new_state
                self.mute_changed.emit(new_state)  # type: ignore

        return None

    def set_mute(self, mute: bool) -> None:
        """
        Sets the current mute state based on the given new state.

        Args:
            mute: The new mute state after a volume button toggle (mute/unmute).
        """
        if not isinstance(mute, bool):
            raise TypeError(f"Invalid argument: {mute}, The argument must be a boolean")

        if self._is_muted == mute:
            return

        if mute:
            # Muting: save current volume and set to 0
            self._previous_volume = self._current_volume
            self.set_volume(0)
        else:
            # Unmuting: restore previous volume
            self.set_volume(self._previous_volume)
