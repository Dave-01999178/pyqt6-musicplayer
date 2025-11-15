from pathlib import Path
from typing import Sequence

from PyQt6.QtCore import QObject, pyqtSignal

from pyqt6_music_player.constants import (
    DefaultAudioInfo,
    MAX_VOLUME,
    MIN_VOLUME,
    SUPPORTED_AUDIO_FORMAT,
)
from pyqt6_music_player.models import Song


class PlaylistModel(QObject):
    playlist_changed = pyqtSignal()
    """Manages the music player's playlist state."""
    def __init__(self) -> None:
        super().__init__()
        self._playlist: list[Song] = []
        self._playlist_set: set[Path] = set()

    @property
    def playlist(self) -> list[Song]:
        """Return the current playlist."""
        return self._playlist

    @property
    def playlist_set(self) -> set[Path]:
        """Set version of playlist used for fast membership checks."""
        return self._playlist_set

    @staticmethod
    def _normalize_to_paths(file_paths: Sequence[str | Path]) -> list[Path]:
        """
        Normalize input into a list of Path objects.

        Args:
            file_paths: A list of strings and/or Paths.

        Returns:
            List of Path objects.

        Raises:
            TypeError: If the list contains unsupported types or if the argument type is not
                       supported.
        """
        normalized_paths = []
        for file_path in file_paths:
            # Ignore the strings that could point to directories/cwd.
            if file_path in {"", "."}:
                continue

            path = Path(file_path)

            # Skip cwd ('.'), empty values, or directories
            if path in {Path(""), Path(".")} or path.is_dir():
                continue
            normalized_paths.append(path)

        return normalized_paths

    def add_song(self, file_paths: str | Path | Sequence[str | Path]) -> None:
        """
        Add one or more audio files to the playlist.

        Args:
            file_paths: A single path (str or Path), or a list of paths (str and/or Path objects).

        - Normalizes inputs into Path objects and resolves them to absolute paths.
        - Ignores non-existent files and files with unsupported extensions.
        - Skips duplicates using an internal set for fast membership checks.
        - Updates the playlist and playlist_set in-place.

        Supported extensions: .mp3, .wav, .flac, .ogg
        """
        if not file_paths:
            return

        # Allow single str/Path input by wrapping into a list.
        if isinstance(file_paths, (str, Path)):
            file_paths = [file_paths]

        paths = self._normalize_to_paths(file_paths)
        from_path = Song.from_path  # Cache to avoid repeated lookups.
        for p in paths:
            try:
                resolved_path = p.resolve(strict=True)
            except FileNotFoundError:
                continue

            if resolved_path.suffix.lower() not in SUPPORTED_AUDIO_FORMAT:
                continue

            if resolved_path not in self._playlist_set:
                song = from_path(resolved_path)

                if not song:
                    continue

                self._playlist.append(song)
                self._playlist_set.add(resolved_path)

                self.playlist_changed.emit()  # type: ignore


class PlaybackProgressState(QObject):
    def __init__(self):
        super().__init__()
        self._is_playing = False
        self._elapsed_time = DefaultAudioInfo.elapsed_time
        self._total_duration = DefaultAudioInfo.total_duration

    @property
    def elapsed_time(self):
        return self._elapsed_time

    @property
    def total_duration(self):
        return self._total_duration


class VolumeSettings(QObject):
    volume_changed: pyqtSignal = pyqtSignal(int)
    """Manages the music player's volume state."""
    def __init__(self) -> None:
        super().__init__()
        self._current_volume: int = MAX_VOLUME
        self._previous_volume: int = self._current_volume

    @property
    def current_volume(self) -> int:
        return self._current_volume

    @current_volume.setter
    def current_volume(self, new_value: int) -> None:
        # Reject non-integer inputs and explicitly reject `bool` since False is 0 and True is 1.
        if not isinstance(new_value, int) or isinstance(new_value, bool):
            raise TypeError("The input must be an integer between 0 and 100.")

        self._update_volume(new_value)

    @property
    def previous_volume(self) -> int:
        return self._previous_volume

    def toggle_mute(self, mute: bool) -> None:
        """
        Toggles mute/unmute state.

        Args:
            mute: True if mute state is toggled, Otherwise, False.
        """
        prev_volume = self._current_volume

        self._update_volume(0 if mute else self._previous_volume)

        self._previous_volume = prev_volume

    def _update_volume(self, new_value: int) -> None:
        """
        Updates the current volume based on the new clamped value or volume state (mute/unmute).

        Args:
            new_value: The volume's new value.
        """
        # Ensure that the new value is within the 0-100 bounds.
        clamped_value = max(MIN_VOLUME, min(MAX_VOLUME, new_value))

        # Only update if the value has changed.
        if clamped_value == self.current_volume:
            return

        self._current_volume = clamped_value

        self.volume_changed.emit(self._current_volume)
