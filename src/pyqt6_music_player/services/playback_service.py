import logging
import random

from pyqt6_music_player.audio import AudioPlayerService
from pyqt6_music_player.core import (
    RESTART_THRESHOLD_SEC,
    PlaybackMode,
    PlaybackStatus,
    Signal,
)
from pyqt6_music_player.models import AudioPCM, Track
from pyqt6_music_player.services import PlaylistService

logger = logging.getLogger(__name__)


class PlaybackService:
    """Orchestrate playback operations and coordinates between player and playlist.

    Manages track selection, playback control, and state synchronization.

    """
    def __init__(
            self,
            audio_player: AudioPlayerService,
            playlist_service: PlaylistService,
    ):
        """Initialize PlaybackService."""
        # Service
        self._audio_player = audio_player

        # Model
        self._playlist = playlist_service

        # Playback state
        self._current_track: Track | None = None
        self._track_index: int | None = None
        self._current_position_sec: int = 0
        self._playback_mode: PlaybackMode = PlaybackMode.NORMAL
        self._playback_status: PlaybackStatus = PlaybackStatus.IDLE

        # Shuffle state
        self._shuffle_order: list[int] = []
        self._shuffle_pos: int | None = None

        # Signals
        self.track_loaded = Signal()
        self.playback_started = Signal()
        self.playback_position_changed = Signal()
        self.player_state_changed = Signal()

        # Setup
        self._connect_signals()

    # --- Public methods ---
    def play(self) -> None:
        """Play the selected track, or the first track if none is selected."""
        selected_index = self._playlist.get_selected_index()
        track_index = selected_index or 0  # Default to first track if none is selected

        # Set the selection index to 0 when defaulted to first track.
        if selected_index is None and track_index == 0:
            self._playlist.set_selected_index(track_index)

        self._play_track_at_index(track_index)

        # Track the shuffle position so playback follows the shuffle order
        if self._playback_mode == PlaybackMode.SHUFFLE:
            self._shuffle_pos = self._shuffle_order.index(track_index)

    def pause(self) -> None:
        """Pause the current playback only if it is playing."""
        if self._playback_status != PlaybackStatus.PLAYING:
            return

        self._audio_player.pause_playback()

    def resume(self) -> None:
        """Resume the playback only if it is paused."""
        if self._playback_status != PlaybackStatus.PAUSED:
            return

        self._audio_player.resume_playback()

    def toggle_playback(self) -> None:
        """Start new, pause, and resume playback based on the current player state."""
        # Resume
        if self._playback_status == PlaybackStatus.PAUSED:
            self.resume()

        # Pause
        elif self._playback_status == PlaybackStatus.PLAYING:
            self.pause()

        # Start new playback
        else:
            self.play()

    def play_next_track(self) -> None:
        """Play next track."""
        if self._track_index is None:
            return

        if self._playback_mode == PlaybackMode.SHUFFLE:
            if self._shuffle_pos >= len(self._shuffle_order) - 1:
                return

            self._shuffle_pos += 1

            next_track_index = self._shuffle_order[self._shuffle_pos]
        else:
            if self._track_index >= self._playlist.get_track_count():
                return

            next_track_index = self._track_index + 1

        new_selected_index = self._playlist.set_selected_index(next_track_index)

        if new_selected_index is not None:
            self._play_track_at_index(new_selected_index)

    def play_previous_track(self) -> None:
        """Play the previous track or restart the current one.

        Restarts the current track if the playback position exceeds
        the threshold, otherwise navigates to the previous track.
        Has no effect if there is no track loaded.
        """
        if self._track_index is None:
            return

        is_past_restart_threshold = self._current_position_sec >= RESTART_THRESHOLD_SEC

        if self._playback_mode == PlaybackMode.SHUFFLE:
            if self._shuffle_pos is None:
                return

            # Restart if past threshold or at the beginning of shuffle order
            if self._shuffle_pos == 0 or is_past_restart_threshold:
                self._restart_current_track()
                return

            self._shuffle_pos -= 1

            prev_track_index = self._shuffle_order[self._shuffle_pos]

        else:
            if self._track_index == 0 or is_past_restart_threshold:
                self._restart_current_track()
                return

            prev_track_index = self._track_index - 1

        new_selected_index = self._playlist.set_selected_index(prev_track_index)

        if new_selected_index is not None:
            self._play_track_at_index(new_selected_index)

    def toggle_shuffle(self, enable: bool):
        if enable:
            self._playback_mode = PlaybackMode.SHUFFLE

            self._build_shuffle_order()

            logger.info("Shuffle: On.")
        else:
            self._playback_mode = PlaybackMode.NORMAL

            logger.info("Shuffle: Off.")

    def seek(self, new_position_in_ms: int) -> None:
        """Seek to a specific position.

        Args:
            new_position_in_ms: Target position in milliseconds.

        """
        self._audio_player.seek(new_position_in_ms)

    def get_playback_status(self) -> PlaybackStatus:
        """Return the current playback status."""
        return self._playback_status

    # --- Protected/internal methods ---
    def _connect_signals(self) -> None:
        # Wire AudioPlayerService signals to PlaybackService slots
        self._audio_player.audio_loaded.connect(self._on_player_audio_loaded)
        self._audio_player.playback_started.connect(self._on_playback_started)
        self._audio_player.playback_position_changed.connect(
            self._on_playback_position_changed,
        )
        self._audio_player.playback_finished.connect(self.play_next_track)
        self._audio_player.playback_status_changed.connect(self._on_player_state_changed)

    def _play_track_at_index(self, index: int) -> None:
        # Play specific track based on the given index
        track = self._playlist.get_track_by_index(index)

        if track is not None:
            self._current_track = track
            self._track_index = index

            logger.info(
                "Playback requested for new selected track: '%s'",
                track.title,
            )

            audio = AudioPCM.from_file(track.path)
            if audio is not None:
                # Triggers 'playback start' on successful load.
                self._audio_player.load_track_audio(audio)

    def _build_shuffle_order(self):
        """Build a shuffled playback order."""
        track_count = self._playlist.get_track_count()

        if not track_count:
            return

        # Shuffle all tracks except the current one
        remaining_tracks = [x for x in range(track_count) if x != self._track_index]
        random.shuffle(remaining_tracks)

        if self._track_index is None:
            # No current track means all tracks are shuffled
            self._shuffle_order = remaining_tracks
            self._shuffle_pos = 0
        else:
            # Place the current track first, followed by the shuffled remainder
            self._shuffle_order = [self._track_index]
            self._shuffle_order.extend(remaining_tracks)

            self._shuffle_pos = self._shuffle_order.index(self._track_index)

        print(self._shuffle_order)

    def _restart_current_track(self):
        """Seek to the beginning and resume playback if currently playing."""
        self.seek(0)
        if self._playback_status == PlaybackStatus.PLAYING:
            self._audio_player.resume_playback()

    def _on_player_audio_loaded(self) -> None:
        # Emit loaded track then start playback
        self.track_loaded.emit(self._current_track)

        self._audio_player.start_playback()

    def _on_playback_started(self) -> None:
        # Store the current track and its index
        logger.info("Now playing: %s", self._current_track.title)

    def _on_playback_position_changed(self, elapsed_time: float) -> None:
        self._current_position_sec = elapsed_time

        # Emit position update with elapsed and remaining time
        time_remaining = self._current_track.duration - elapsed_time

        self.playback_position_changed.emit(elapsed_time, time_remaining)

    def _on_player_state_changed(self, new_status: PlaybackStatus):
        # Store and emit new playback status
        self._playback_status = new_status

        self.player_state_changed.emit(new_status)
