from PyQt6.QtCore import QObject, pyqtSignal

from pyqt6_music_player.core import PlaybackState, RepeatMode
from pyqt6_music_player.utils import format_duration

from .playback_service import PlaybackService

# ==================== CONSTANTS ====================
DEFAULT_TITLE = "Track Title"
DEFAULT_ARTIST = "Track Artist"
DEFAULT_DURATION = 0.0


# ==================== VIEWMODEL ====================
class PlaybackViewModel(QObject):
    """Expose playback state and commands to the view."""

    playback_started = pyqtSignal(str, str, int, str)
    playback_position_changed = pyqtSignal(int, str, str)
    initial_tracks_added = pyqtSignal()
    playback_state_changed = pyqtSignal(PlaybackState)
    playback_cleared = pyqtSignal(str, str, str)

    def __init__(self, playback_service: PlaybackService):
        """Initialize PlaybackViewModel and connect to PlaybackService signals.

        Args:
            playback_service: Service managing track loading and audio playback.

        """
        super().__init__()
        # Service
        self._service = playback_service

        # State
        self._active_track_title: str = DEFAULT_TITLE
        self._active_track_artist: str = DEFAULT_ARTIST
        self._active_track_duration: float = DEFAULT_DURATION
        self._pre_seek_playback_state: PlaybackState | None = None

        # Setup
        self._connect_signals()

    # -- Public methods --
    @property
    def active_track_title(self) -> str:
        """The active track's title."""
        return self._active_track_title

    @property
    def active_track_artist(self) -> str:
        """The active track's artist."""
        return self._active_track_artist

    @property
    def active_track_formatted_duration(self) -> str:
        """The active track's duration in 'hh:mm:ss' format."""
        return format_duration(self._active_track_duration)

    def toggle_playback(self) -> None:
        """Toggle between playing and paused state."""
        self._service.toggle_playback()

    def next_track(self) -> None:
        """Skip to the next track."""
        self._service.next_track()

    def previous_track(self) -> None:
        """Skip to the previous track."""
        self._service.previous_track()

    def begin_seek(self) -> None:
        """Begin seek operation, pausing playback if currently playing."""
        status = self._service.playback_state

        self._pre_seek_playback_state = status

        if status == PlaybackState.PLAYING:
            self._service.pause()

    def seek(self, current_position: int) -> None:
        """Seek to the given position during an active seek operation.

        Args:
            current_position: The current playback position in milliseconds.

        """
        self._service.seek(current_position)

    def end_seek(self, final_pos: int) -> None:
        """End seek operation, resuming playback if it was playing before seeking.

        Args:
            final_pos: The final playback position in milliseconds after seeking.

        """
        self._service.seek(final_pos)

        if self._pre_seek_playback_state == PlaybackState.PLAYING:
            self._service.resume()

        self._pre_seek_playback_state = None

    def set_shuffle_enabled(self, enabled: bool) -> None:
        """Enable or disable shuffle mode.

        Args:
            enabled: If True, enables shuffle; if False, disables it.

        """
        self._service.set_shuffle_enabled(enabled)

    def set_repeat_mode(self, repeat_mode: RepeatMode) -> None:
        """Set the repeat mode.

        Args:
            repeat_mode: The repeat mode to apply (OFF, ONE, or ALL).

        """
        self._service.set_repeat_mode(repeat_mode)

    def enable_controls(self) -> None:
        """Enable playback controls."""
        self.initial_tracks_added.emit()

    # -- Protected/internal methods --
    def _connect_signals(self):
        # PlaybackService -> PlaybackViewModel
        self._service.playback_started.connect(self._on_playback_started)
        self._service.playback_state_changed.connect(self._on_playback_state_changed)
        self._service.playback_position_changed.connect(
            self._on_playback_position_changed,
        )
        self._service.playback_cleared.connect(self._on_playback_cleared)

    def _reset_state(self) -> None:
        self._active_track_title= DEFAULT_TITLE
        self._active_track_artist = DEFAULT_ARTIST
        self._active_track_duration = DEFAULT_DURATION

    def _on_playback_started(self) -> None:
        current_track = self._service.current_track

        # Avoid redundant UI updates if the active track did not change e.g. replay or
        # repeat playback
        if self._active_track_title == current_track.title:
            return

        duration_in_ms = int(current_track.duration * 1000)
        formatted_duration = format_duration(current_track.duration)

        self.playback_started.emit(
            current_track.title,
            current_track.artist,
            duration_in_ms,
            formatted_duration,
        )

        # Cache title and duration for later use.
        # This avoids frequent `self._service.current_track` lookup inside
        # `_on_playback_position_changed` method when calculating the
        # 'time remaining' every position update
        self._active_track_title = current_track.title
        self._active_track_duration = current_track.duration

    def _on_playback_position_changed(self, elapsed_time_in_seconds: float) -> None:
        # Convert and emit elapsed time into milliseconds and formatted duration
        elapsed_time_in_ms = int(elapsed_time_in_seconds * 1000)
        time_remaining = int(self._active_track_duration - elapsed_time_in_seconds)
        formatted_elapsed_time = format_duration(elapsed_time_in_seconds)
        formatted_time_remaining = format_duration(time_remaining)

        self.playback_position_changed.emit(
            elapsed_time_in_ms,
            formatted_elapsed_time,
            formatted_time_remaining,
        )

    def _on_playback_cleared(self) -> None:
        self._reset_state()

        self.playback_cleared.emit(
            self._active_track_title,
            self._active_track_artist,
            format_duration(self._active_track_duration),
        )

    def _on_playback_state_changed(self, playback_state: PlaybackState) -> None:
        self.playback_state_changed.emit(playback_state)
