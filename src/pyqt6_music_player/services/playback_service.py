import logging

from pyqt6_music_player.audio import AudioPlayerService
from pyqt6_music_player.core import (
    RESTART_THRESHOLD_SEC,
    PlaybackState,
    RepeatMode,
    ShuffleMode,
    Signal,
)
from pyqt6_music_player.models import AudioPCM, Track
from pyqt6_music_player.services import (
    EndBoundary,
    NoTrackLoaded,
    PlaylistService,
    RepeatCurrent,
    StartBoundary,
    TrackNavigator,
)

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
        """Initialize PlaybackService.

        Args:
            audio_player: Service managing audio playback and worker thread
                          communication.
            playlist_service: Service managing playlist state and operations.

        """
        # Service
        self._audio_player = audio_player
        self._playlist = playlist_service
        self._track_navigator = TrackNavigator(self._playlist)

        # Playback state
        self._current_track: Track | None = None
        self._current_position_sec: float = 0.0
        self._playback_state: PlaybackState = PlaybackState.IDLE

        # Signals
        self.track_loaded = Signal()
        self.playback_started = Signal()
        self.playback_position_changed = Signal()
        self.playback_state_changed = Signal()

        # Setup
        self._connect_signals()

    # -- Public methods --
    def toggle_playback(self) -> None:
        """Start new, pause, and resume playback based on the current playback state."""
        # Resume
        if self._playback_state == PlaybackState.PAUSED:
            self.resume()

        # Pause
        elif self._playback_state == PlaybackState.PLAYING:
            self.pause()

        # Start new playback
        else:
            self.play()

    def play(self) -> None:
        """Play the selected track, or the first track if none is selected.

        Has no effect if the playlist is empty.
        """
        outcome = self._track_navigator.resolve_initial_track_index()

        if isinstance(outcome, NoTrackLoaded):
            return

        # Sync playlist selection when defaulting to first track
        track_index = outcome.index
        if self._playlist.selected_row is None and track_index == 0:
            self._playlist.set_selected_row(track_index)

        self._play_track_at_index(track_index)

    def pause(self) -> None:
        """Pause playback.

        Has no effect if playback is not currently active.
        """
        if self._playback_state != PlaybackState.PLAYING:
            return

        self._audio_player.pause_playback()

    def resume(self) -> None:
        """Resume playback.

        Has no effect if playback is not paused
        (e.g. playback is in a different state or there's no track loaded).
        """
        if self._playback_state != PlaybackState.PAUSED:
            return

        self._audio_player.resume_playback()

    def next_track(self) -> None:
        """Skip to the next track in the playback order.

        Has no effect if there is no track loaded or the end of the
        playback order is reached.
        """
        outcome = self._track_navigator.resolve_next_track_index()

        if isinstance(outcome, NoTrackLoaded | EndBoundary):
            return

        new_selected_index = self._playlist.set_selected_row(outcome.index)
        if new_selected_index is not None:
            self._play_track_at_index(new_selected_index)

    def previous_track(self) -> None:
        """Skip to the previous track or restart the current one.

        Restarts the current track if the playback position exceeds the
        restart threshold, or if the start of the playback order is reached.
        Has no effect if there is no track loaded.
        """
        is_past_restart_threshold = self._current_position_sec >= RESTART_THRESHOLD_SEC
        if is_past_restart_threshold:
            self._restart_current_track()
            return

        outcome = self._track_navigator.resolve_previous_track_index()
        if isinstance(outcome, NoTrackLoaded):
            return

        if isinstance(outcome, StartBoundary):
            self._restart_current_track()
            return

        new_selected_index = self._playlist.set_selected_row(outcome.index)
        if new_selected_index is not None:
            self._play_track_at_index(new_selected_index)

    def seek(self, new_position_in_ms: int) -> None:
        """Seek to the given position.

        Args:
            new_position_in_ms: Target position in milliseconds.

        """
        self._audio_player.seek(new_position_in_ms)

    def set_shuffle_mode(self, shuffle_mode: ShuffleMode) -> None:
        """Set the shuffle mode.

        Args:
            shuffle_mode: The shuffle mode to apply (ON or OFF).

        """
        self._track_navigator.set_shuffle_mode(shuffle_mode)

    def set_repeat_mode(self, repeat_mode: RepeatMode) -> None:
        """Set the repeat mode.

        Args:
            repeat_mode: The repeat mode to apply (OFF, ONE, or ALL).

        """
        self._track_navigator.set_repeat_mode(repeat_mode)

    def get_playback_state(self) -> PlaybackState:
        """Return the current playback state."""
        return self._playback_state

    # -- Protected/internal methods --
    def _connect_signals(self) -> None:
        # Wire AudioPlayerService signals to PlaybackService slots
        self._audio_player.audio_loaded.connect(self._on_player_audio_loaded)
        self._audio_player.playback_started.connect(self._on_playback_started)
        self._audio_player.playback_position_changed.connect(
            self._on_playback_position_changed,
        )
        self._audio_player.playback_finished.connect(self._auto_advance)
        self._audio_player.playback_state_changed.connect(
            self._on_playback_state_changed,
        )

    def _play_track_at_index(self, index: int) -> None:
        # Fetch, load, and play the track at the given playlist index
        track = self._playlist.get_track_by_index(index)

        if track is not None:
            self._current_track = track

            self._track_navigator.set_playback_order_position(index)

            logger.info(
                "Playback requested for new selected track: '%s'",
                track.title,
            )

            audio = AudioPCM.from_file(track.path)
            if audio is None:
                logger.warning(
                    "Failed to load audio for track: '%s'",
                    track.title,
                )
                return

            # Triggers 'playback start' on successful load.
            self._audio_player.load_track_audio(audio)

    def _restart_current_track(self):
        # Seek to the beginning and resume playback if currently playing.
        self.seek(0)

        if self._playback_state == PlaybackState.PLAYING:
            self._audio_player.resume_playback()

    def _auto_advance(self):
        outcome = self._track_navigator.resolve_auto_advance_index()

        if isinstance(outcome, EndBoundary):
            return

        if isinstance(outcome, RepeatCurrent):
            self._audio_player.repeat_playback()
            return

        new_selected_index = self._playlist.set_selected_row(outcome.index)
        if new_selected_index is not None:
            self._play_track_at_index(new_selected_index)

    def _on_player_audio_loaded(self) -> None:
        # Emit loaded track then start playback
        self.track_loaded.emit(self._current_track)

        self._audio_player.start_playback()

    def _on_playback_started(self) -> None:
        logger.info("Now playing: %s", self._current_track.title)

    def _on_playback_position_changed(self, elapsed_time: float) -> None:
        self._current_position_sec = elapsed_time

        # Emit elapsed and remaining time
        time_remaining = self._current_track.duration - elapsed_time

        self.playback_position_changed.emit(elapsed_time, time_remaining)

    def _on_playback_state_changed(self, new_state: PlaybackState):
        # Store and emit new playback state
        self._playback_state = new_state

        self.playback_state_changed.emit(new_state)
