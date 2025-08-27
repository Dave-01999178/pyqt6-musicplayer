from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal

from pyqt6_music_player.config import DEFAULT_VOLUME, DEFAULT_SONG_ARTIST, DEFAULT_SONG_TITLE, DEFAULT_ELAPSED_TIME, \
    DEFAULT_TIME_DURATION, DEFAULT_PLAY_STATE, DEFAULT_CURRENT_SONG


class PlaylistState(QObject):
    """
    Manages the playlist of the music player, including loaded songs and
    current playback state.
    """
    SUPPORTED_AUDIO_SUFFIXES: set[str] = {".mp3", ".wav", ".flac", ".ogg"}
    def __init__(self):
        super().__init__()
        self._current_song = DEFAULT_CURRENT_SONG
        self._playlist: list[Path] = []
        self._playlist_set: set[Path] = set()

    @property
    def current_song(self):
        return self._current_song

    @property
    def playlist(self) -> list[Path]:
        return self._playlist

    @property
    def playlist_set(self) -> set[Path]:
        """Set version of playlist used for fast membership checks."""
        return self._playlist_set

    @property
    def song_count(self) -> int:
        return len(self._playlist)

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
        if not isinstance(file_paths, list):
            raise TypeError(f"Expected list[str | Path], got {type(file_paths)}.")

        # Ensure every item is str or Path
        if any(not isinstance(p, (str, Path)) for p in file_paths):
            raise TypeError(f"Unsupported type in list.")

        return [Path(p) for p in file_paths]

    def add_song(self, file_paths: list[str | Path]) -> None:
        """
        Add one or more audio files to the playlist.

        Args:
            file_paths: List of file paths as str or Path objects.

        Behavior:
        - Normalizes inputs into Path objects and resolves them to absolute paths.
        - Ignores non-existent files and files with unsupported extensions.
        - Skips duplicates using an internal set for fast membership checks.
        - Updates the playlist and playlist_set in-place.

        Supported extensions: .mp3, .wav, .flac, .ogg
        """
        if not file_paths:
            return

        paths = self._normalize_to_paths(file_paths)

        for p in paths:
            try:
                resolved_path = p.resolve(strict=True)
            except FileNotFoundError:
                continue

            if resolved_path.suffix.lower() not in self.SUPPORTED_AUDIO_SUFFIXES:
                continue

            if resolved_path not in self._playlist_set:
                self._playlist.append(resolved_path)
                self._playlist_set.add(resolved_path)


class MetadataState(QObject):
    def __init__(self):
        super().__init__()
        self.album_art = None
        self._song_title = DEFAULT_SONG_TITLE
        self._artist = DEFAULT_SONG_ARTIST

    @property
    def song_title(self):
        return self._song_title

    @property
    def song_artist(self):
        return self._artist


class PlaybackProgressState(QObject):
    def __init__(self):
        super().__init__()
        self._is_playing = DEFAULT_PLAY_STATE
        self._elapsed_time = DEFAULT_ELAPSED_TIME
        self._total_duration = DEFAULT_TIME_DURATION

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
            metadata: MetadataState,
            playback_progress: PlaybackProgressState,
            volume: VolumeState
    ):
        super().__init__()
        self.playlist = playlist
        self.metadata = metadata
        self.playback_progress = playback_progress
        self.volume = volume
