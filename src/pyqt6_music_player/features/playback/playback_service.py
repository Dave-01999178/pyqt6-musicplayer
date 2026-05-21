import logging

from pyqt6_music_player.audio import AudioPlayerService
from pyqt6_music_player.core import (
    RESTART_THRESHOLD_SEC,
    PlaybackState,
    RepeatMode,
    ShuffleMode,
    Signal,
)
from pyqt6_music_player.features.playlist import PlaylistService
from pyqt6_music_player.track import AudioPCM, Track

from .track_navigator import (
    EndBoundary,
    NoTrackLoaded,
    RepeatCurrent,
    StartBoundary,
    TrackNavigator, NoActiveTrack,
)

logger = logging.getLogger(__name__)


class PlaybackService:
    """Orchestrate playback operations and coordinates between player and playlist.

    Manages track selection, playback control, and state synchronization.
    """

    playback_started = Signal()
    playback_changed = Signal()
    playback_state_changed = Signal()
    playback_position_changed = Signal()
    playback_ended = Signal()

    def __init__(
            self,
            audio_player: AudioPlayerService,
            playlist_service: PlaylistService,
            track_navigator: TrackNavigator,
    ):
        """Initialize PlaybackService.

        Args:
            audio_player: Service managing audio playback and worker thread
                          communication.
            playlist_service: Service managing playlist state and operations.
            track_navigator: Domain service resolving next, previous, and auto-advance
                             track indices based on repeat and shuffle rules.

        """
        # Dependencies
        self._audio_player = audio_player
        self._playlist = playlist_service
        self._track_navigator = track_navigator

        # State
        self._current_track: Track | None = None
        self._curr_pos_in_sec: float = 0.0
        self._playback_state: PlaybackState = PlaybackState.IDLE

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
        outcome = self._track_navigator.resolve_track_index()
        if isinstance(outcome, NoTrackLoaded):
            return

        track_index = outcome.index

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
        if isinstance(outcome, EndBoundary | NoTrackLoaded | NoActiveTrack):
            return

        self._play_track_at_index(outcome.index)

    def previous_track(self) -> None:
        """Skip to the previous track or restart the current one.

        Restarts the current track if the playback position exceeds the
        restart threshold, or if the start of the playback order is reached.
        Has no effect if there is no track loaded.
        """
        is_past_restart_threshold = self._curr_pos_in_sec >= RESTART_THRESHOLD_SEC
        if is_past_restart_threshold:
            self._restart_current_track()
            return

        outcome = self._track_navigator.resolve_previous_track_index()
        if isinstance(outcome, NoTrackLoaded | NoActiveTrack):
            return

        if isinstance(outcome, StartBoundary):
            self._restart_current_track()
            return

        self._play_track_at_index(outcome.index)

    def seek(self, position_in_ms: int) -> None:
        """Seek to the given position.

        Args:
            position_in_ms: Target position in milliseconds.

        """
        self._audio_player.seek(position_in_ms)

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

    def set_volume(self, volume: int) -> None:
        """Set the playback volume.

        Args:
            volume: The volume level in range (0, 100).

        """
        self._audio_player.set_volume(volume / 100)

    def get_playback_state(self) -> PlaybackState:
        """Return the current playback state."""
        return self._playback_state

    # -- Protected/internal methods --
    def _connect_signals(self) -> None:
        # AudioPlayerService -> PlaybackService
        self._audio_player.playback_started.connect(self._on_playback_started)
        self._audio_player.playback_position_changed.connect(
            self._on_playback_position_changed,
        )
        self._audio_player.playback_finished.connect(self._auto_advance)
        self._audio_player.playback_state_changed.connect(self._on_playback_state_changed)

        # PlaylistService -> PlaybackService
        self._playlist.active_track_removed.connect(self._on_active_track_removed)

    def _play_track_at_index(self, index: int) -> None:
        # Fetch, load, and play the track at the given playlist index
        track = self._playlist.get_track_by_index(index)
        if track is None:
            return  # TODO: Add log

        audio = AudioPCM.from_file(track.path)
        if audio is None:
            return  # TODO: Add log

        self._current_track = track
        self._track_index = index

        self._audio_player.play_audio(audio)

    def _on_playback_started(self) -> None:
        track_duration_in_ms = int(self._current_track.duration * 1000)
        self.playback_started.emit(
            self._current_track.title,
            self._current_track.artist,
            track_duration_in_ms,
        )

        logger.info("Now playing: %s", self._current_track.title)

        self.playback_changed.emit(self._track_navigator.current_position)

    def _auto_advance(self) -> None:
        outcome = self._track_navigator.resolve_auto_advance_index()

        if isinstance(outcome, EndBoundary | NoTrackLoaded):
            return

        if isinstance(outcome, RepeatCurrent):
            self._audio_player.repeat_playback()
            return

        self._play_track_at_index(outcome.index)

    def _restart_current_track(self) -> None:
        # Seek to the beginning and resume playback if currently playing.
        self.seek(0)

        if self._playback_state == PlaybackState.PLAYING:
            self._audio_player.resume_playback()

    def _on_playback_position_changed(self, elapsed_time: float) -> None:
        # Emit elapsed and remaining time
        self._curr_pos_in_sec = elapsed_time

        elapsed_time_in_ms = int(elapsed_time * 1000)
        time_remaining = self._current_track.duration - elapsed_time

        self.playback_position_changed.emit(
            elapsed_time,
            elapsed_time_in_ms,
            time_remaining,
        )

    def _on_playback_state_changed(self, new_state: PlaybackState) -> None:
        # Store and emit new playback state
        self._playback_state = new_state

        self.playback_state_changed.emit(new_state)

    def _on_active_track_removed(self) -> None:
        outcome = self._track_navigator.resolve_track_index()
        if isinstance(outcome, NoTrackLoaded):
            self._audio_player.end_playback()

            self.playback_ended.emit()
            return

        track_index = outcome.index

        self._play_track_at_index(track_index)
