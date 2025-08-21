from PyQt6.QtCore import QObject, pyqtSignal

from pyqt6_music_player.config import DEFAULT_VOLUME, DEFAULT_SONG_ARTIST, DEFAULT_SONG_TITLE, DEFAULT_ELAPSED_TIME, \
    DEFAULT_TIME_DURATION, DEFAULT_PLAY_STATE


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


class SongProgressState(QObject):
    def __init__(self):
        super().__init__()
        self._is_playing = DEFAULT_PLAY_STATE
        self._elapsed_time = DEFAULT_ELAPSED_TIME
        self._total_duration = DEFAULT_TIME_DURATION

    @property
    def elapsed_time(self):
        return self._elapsed_time

    @property
    def time_remaining(self):
        return self._total_duration


class VolumeState(QObject):
    volume_changed: pyqtSignal = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        self._current_volume: int = DEFAULT_VOLUME
        self._previous_volume: int = self._current_volume

    @property
    def current_volume(self):
        return self._current_volume

    @property
    def previous_volume(self):
        return self._previous_volume

    @current_volume.setter
    def current_volume(self, new_value):
        # Reject non-integer inputs and explicitly reject `bool` since False is 0 and True is 1.
        if not isinstance(new_value, int) or isinstance(new_value, bool):
            raise TypeError("The input must be an integer between 0 and 100.")

        self._update_volume(new_value)

    def toggle_mute(self, mute: bool):
        prev_volume = self._current_volume

        self._update_volume(0 if mute else self._previous_volume)

        self._previous_volume = prev_volume

    def _update_volume(self, new_value: int):
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
            metadata: MetadataState,
            song_progress: SongProgressState,
            volume: VolumeState
    ):
        super().__init__()
        self.metadata = metadata
        self.song_progress = song_progress
        self.volume = volume
