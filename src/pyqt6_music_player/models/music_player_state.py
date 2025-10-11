from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal

from src.pyqt6_music_player.config import (
    DEFAULT_ELAPSED_TIME,
    DEFAULT_PLAY_STATE,
    DEFAULT_SONG_DURATION,
    DEFAULT_VOLUME,
    SUPPORTED_AUDIO_FORMAT,
)
from src.pyqt6_music_player.models import Song, DEFAULT_SONG


class PlaylistState(QObject):
    playlist_changed = pyqtSignal(list)
    """
    Manages the playlist of the music player, including loaded songs and
    current playback state.
    """
    def __init__(self) -> None:
        super().__init__()
        self._playlist: list[Song] = []
        self._playlist_set: set[Path] = set()

    @property
    def playlist(self) -> list[Song]:
        """Return the current playlist as a list of Songs."""
        return self._playlist

    @property
    def playlist_set(self) -> set[Path]:
        """Set version of playlist used for fast membership checks."""
        return self._playlist_set

    @property
    def song_count(self) -> int:
        """Return the number of songs currently in the playlist."""
        return len(self._playlist)

    @property
    def current_song(self):
        return DEFAULT_SONG

    @staticmethod
    def _normalize_to_paths(file_paths: list[str | Path]) -> list[Path]:
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

    def add_song(self, file_paths: str | Path | list[str | Path]) -> None:
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

                self.playlist_changed.emit(self.playlist)  # type: ignore


class PlaybackProgressState(QObject):
    def __init__(self):
        super().__init__()
        self._is_playing = DEFAULT_PLAY_STATE
        self._elapsed_time = DEFAULT_ELAPSED_TIME
        self._total_duration = DEFAULT_SONG_DURATION

    @property
    def elapsed_time(self):
        return self._elapsed_time

    @property
    def total_duration(self):
        return self._total_duration


class VolumeState(QObject):
    volume_changed: pyqtSignal = pyqtSignal(int)
    def __init__(self) -> None:
        super().__init__()
        self._current_volume: int = DEFAULT_VOLUME
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
        prev_volume = self._current_volume

        self._update_volume(0 if mute else self._previous_volume)

        self._previous_volume = prev_volume

    def _update_volume(self, new_value: int) -> None:
        # Ensure that the new value is within the 0-100 bounds.
        clamped_value = max(0, min(100, new_value))

        # Only update if the value has changed.
        if clamped_value == self.current_volume:
            return

        self._current_volume = clamped_value

        self.volume_changed.emit(self._current_volume)


class MusicPlayerState(QObject):
    def __init__(
            self,
            playlist: PlaylistState,
            playback_progress: PlaybackProgressState,
            volume: VolumeState
    ):
        super().__init__()
        self.playlist = playlist
        self.playback_progress = playback_progress
        self.volume = volume
