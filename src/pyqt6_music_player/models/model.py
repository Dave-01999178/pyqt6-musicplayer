from pathlib import Path
from typing import Sequence

from PyQt6.QtCore import QObject, pyqtSignal

from pyqt6_music_player.constants import (
    MIN_VOLUME,
    MAX_VOLUME,
    SUPPORTED_AUDIO_FORMAT
)
from pyqt6_music_player.models import Song


# TODO: Consider replacing list.
class PlaylistModel(QObject):
    playlist_changed = pyqtSignal(int)
    """Manages the music player's playlist state."""
    def __init__(self) -> None:
        super().__init__()
        self._playlist: list[Song] = []
        self._playlist_set: set[Path] = set()

    @property
    def playlist(self) -> list[Song]:
        """Return the current playlist."""
        return self._playlist.copy()

    @property
    def playlist_set(self) -> set[Path]:
        """Set version of playlist used for fast membership checks."""
        return self._playlist_set

    @property
    def song_count(self) -> int:
        return len(self._playlist)

    @staticmethod
    def _normalize_to_paths(files: Sequence[str | Path]) -> list[Path]:
        """
        Converts valid path-like inputs into a Path object.

        Args:
            files: A sequence of path-like objects.

        Returns:
            List of Path objects.

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

        Args:
            files: A sequence of path-like objects.

        Supported extensions: .mp3, .wav, .flac, .ogg
        """
        if not files:
            return None

        # Allow single str/Path input by wrapping into a list.
        if isinstance(files, (str, Path)):
            files = [files]

        paths = self._normalize_to_paths(files)

        add_count = 0
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
                add_count += 1

        if add_count != 0:
            self.playlist_changed.emit(add_count)  # type: ignore

        return None


class VolumeModel(QObject):
    volume_changed = pyqtSignal(int)
    mute_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._current_volume = MAX_VOLUME
        self._previous_volume = self._current_volume
        self._is_muted = False

    @property
    def current_volume(self) -> int:
        return self._current_volume

    @property
    def previous_volume(self) -> int:
        return self._previous_volume

    @property
    def is_muted(self) -> bool:
        return self._is_muted

    def set_volume(self, new_volume: int) -> None:
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
