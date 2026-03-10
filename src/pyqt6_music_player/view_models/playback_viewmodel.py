from PyQt6.QtCore import QObject, pyqtSignal

from pyqt6_music_player.core import PlaybackStatus, RepeatMode, ShuffleMode
from pyqt6_music_player.models import Track
from pyqt6_music_player.services import PlaybackService, PlaylistService
from pyqt6_music_player.utils import format_duration


# noinspection PyUnresolvedReferences
class PlaybackViewModel(QObject):
    """Expose playback state and commands to the view."""

    track_loaded = pyqtSignal(str, str, int, str)
    playback_position_changed = pyqtSignal(int, str, str)
    initial_track_added = pyqtSignal()
    player_state_changed = pyqtSignal(PlaybackStatus)

    def __init__(
            self,
            playlist_service: PlaylistService,
            playback_service: PlaybackService,
    ):
        """Initialize PlaybackViewModel.

        Args:
            playlist_service: Service managing playlist state and operations.
            playback_service: Service managing track loading and audio playback.

        """
        super().__init__()
        # Service
        self._playlist_service = playlist_service
        self._playback_service = playback_service

        # Setup
        self._connect_signals()

    # --- Public methods (Commands). ---
    def toggle_playback(self) -> None:
        """Command for toggling playback state, used by play-pause button."""
        self._playback_service.toggle_playback()

    def play(self):
        """Command for starting playback."""
        self._playback_service.play()

    def pause(self):
        """Command for pausing playback."""
        self._playback_service.pause()

    def resume(self):
        """Command for resuming paused playback."""
        self._playback_service.resume()

    def next_track(self) -> None:
        """Command for playing next track."""
        self._playback_service.play_next_track()

    def previous_track(self) -> None:
        """Command for playing previous track."""
        self._playback_service.play_previous_track()

    def seek(self, new_position_in_ms: int) -> None:
        """Command for setting the playback position."""
        self._playback_service.seek(new_position_in_ms)

    def set_repeat_mode(self, repeat_mode: RepeatMode) -> None:
        self._playback_service.set_repeat_mode(repeat_mode)

    def set_shuffle_mode(self, shuffle_mode: ShuffleMode) -> None:
        self._playback_service.set_shuffle_mode(shuffle_mode)

    def get_playback_status(self) -> PlaybackStatus:
        """Return the current playback status."""
        return self._playback_service.get_playback_status()

    # --- Protected/internal methods ---
    def _connect_signals(self) -> None:
        # Wire service signals to PlaybackViewModel slots.
        #
        # PlaylistService -> PlaybackViewModel
        self._playlist_service.tracks_added.connect(self._on_track_added)

        # PlaybackService -> PlaybackViewModel
        self._playback_service.track_loaded.connect(self._on_track_loaded)
        self._playback_service.playback_position_changed.connect(
            self._on_playback_position_changed,
        )
        self._playback_service.player_state_changed.connect(
            self._on_player_state_changed,
        )

    def _on_track_added(self, new_track_idx: list[int]) -> None:
        # Emit `initial_track_added` signal on first insert
        initial_track_add = (new_track_idx[0] == 0)
        if initial_track_add:
            self.initial_track_added.emit()

    def _on_track_loaded(self, current_track: Track) -> None:
        # Emit track duration in milliseconds and formatted strings
        track_duration_in_ms = int(current_track.duration * 1000)
        formatted_duration = format_duration(int(current_track.duration))

        self.track_loaded.emit(
            current_track.title,
            current_track.album,
            track_duration_in_ms,
            formatted_duration,
        )

    def _on_playback_position_changed(
            self,
            elapsed_time: float,
            time_remaining: float,
    ) -> None:
        # Convert and emit playback position in milliseconds and formatted strings
        elapsed_time_in_ms = int(elapsed_time * 1000)
        formatted_elapsed_time = format_duration(elapsed_time)
        formatted_time_remaining = format_duration(time_remaining)

        self.playback_position_changed.emit(
            elapsed_time_in_ms,
            formatted_elapsed_time,
            formatted_time_remaining,
        )

    def _on_player_state_changed(self, player_state: PlaybackStatus):
        # Forward playback status changes
        self.player_state_changed.emit(player_state)
