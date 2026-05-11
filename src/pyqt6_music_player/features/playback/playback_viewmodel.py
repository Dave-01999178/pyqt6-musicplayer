# TODO: Add module docstring
from PyQt6.QtCore import QObject, pyqtSignal

from pyqt6_music_player.core import PlaybackState, RepeatMode, ShuffleMode
from pyqt6_music_player.utils import format_duration

from .playback_service import PlaybackService


class PlaybackViewModel(QObject):
    """Expose playback state and commands to the view."""

    playback_started = pyqtSignal(str, str, int, str)
    playback_position_changed = pyqtSignal(int, str, str)
    initial_tracks_added = pyqtSignal()
    playback_state_changed = pyqtSignal(PlaybackState)

    def __init__(self, playback_service: PlaybackService):
        """Initialize PlaybackViewModel.

        Args:
            playback_service: Service managing track loading and audio playback.

        """
        super().__init__()
        # Service
        self._playback_service = playback_service

        # Pre-seek playback state tracker.
        self._pre_seek_playback_state: PlaybackState | None = None

        self._connect_signals()

    # -- Public methods --
    def toggle_playback(self) -> None:
        """Toggle between playing and paused state."""
        self._playback_service.toggle_playback()

    def next_track(self) -> None:
        """Skip to the next track."""
        self._playback_service.next_track()

    def previous_track(self) -> None:
        """Skip to the previous track."""
        self._playback_service.previous_track()

    def begin_seek(self) -> None:
        """Begin seek operation, pausing playback if currently playing."""
        status = self._playback_service.get_playback_state()

        self._pre_seek_playback_state = status

        if status == PlaybackState.PLAYING:
            self._playback_service.pause()

    def seek(self, current_position: int) -> None:
        """Seek to the given position during an active seek operation.

        Args:
            current_position: The current playback position in milliseconds.

        """
        self._playback_service.seek(current_position)

    def end_seek(self, final_pos: int) -> None:
        """End seek operation, resuming playback if it was playing before seeking.

        Args:
            final_pos: The final playback position in milliseconds after seeking.

        """
        self._playback_service.seek(final_pos)

        if self._pre_seek_playback_state == PlaybackState.PLAYING:
            self._playback_service.resume()

        self._pre_seek_playback_state = None

    def set_shuffle_mode(self, shuffle_mode: ShuffleMode) -> None:
        """Set the shuffle mode.

        Args:
            shuffle_mode: The shuffle mode to apply (ON or OFF).

        """
        self._playback_service.set_shuffle_mode(shuffle_mode)

    def set_repeat_mode(self, repeat_mode: RepeatMode) -> None:
        """Set the repeat mode.

        Args:
            repeat_mode: The repeat mode to apply (OFF, ONE, or ALL).

        """
        self._playback_service.set_repeat_mode(repeat_mode)

    def enable_controls(self) -> None:
        """Enable playback controls."""
        self.initial_tracks_added.emit()

    # -- Protected/internal methods --
    def _connect_signals(self):
        # PlaybackService -> PlaybackViewModel
        self._playback_service.playback_started.connect(
            self._on_playback_started,
        )
        self._playback_service.playback_state_changed.connect(
            self._on_playback_state_changed,
        )
        self._playback_service.playback_position_changed.connect(
            self._on_playback_position_changed,
        )

    def _on_playback_started(
            self,
            track_title: str,
            track_artist: str,
            track_duration_in_ms: int,
    ) -> None:
        formatted_duration = format_duration(track_duration_in_ms // 1000)

        self.playback_started.emit(
            track_title,
            track_artist,
            track_duration_in_ms,
            formatted_duration,
        )

    def _on_playback_position_changed(
            self,
            elapsed_time: float,
            elapsed_time_in_ms: int,
            time_remaining: float,
    ) -> None:
        formatted_elapsed_time = format_duration(elapsed_time)
        formatted_time_remaining = format_duration(time_remaining)

        self.playback_position_changed.emit(
            elapsed_time_in_ms,
            formatted_elapsed_time,
            formatted_time_remaining,
        )

    def _on_playback_state_changed(self, playback_state: PlaybackState) -> None:
        self.playback_state_changed.emit(playback_state)
