import logging

from pyqt6_music_player.core import PlaybackStatus, Signal
from pyqt6_music_player.models import PlaybackState, Track, TrackAudio
from pyqt6_music_player.audio import AudioPlayerService
from pyqt6_music_player.services import PlaylistService

logger = logging.getLogger(__name__)


class PlaybackService:
    def __init__(
            self,
            audio_player: AudioPlayerService,
            playback_state: PlaybackState,
            playlist_service: PlaylistService,
    ):
        # Service
        self._audio_player = audio_player

        # Model
        self._playlist = playlist_service

        # State
        self._state = playback_state

        # Cache
        self._selected_track: Track | None = None
        self._track_index: int | None = None

        # Signals
        self.track_loaded = Signal()
        self.playback_started = Signal()
        self.playback_position_changed = Signal()
        self.player_state_changed = Signal()

        self._connect_signals()

    # --- Private methods ---
    def _connect_signals(self) -> None:
        """Establish signal-handler connections between the service and viewmodel."""
        self._audio_player.audio_loaded.connect(self._on_player_audio_loaded)
        self._audio_player.playback_started.connect(self._on_playback_started)
        self._audio_player.playback_position_changed.connect(
            self._on_playback_position_changed,
        )
        self._audio_player.playback_finished.connect(self.next_track)
        self._audio_player.playback_status_changed.connect(self._on_player_state_changed)

    def _play_track_at_index(self, index: int) -> None:
        """Play specific track based on the given index.

        Args:
            index: The playlist index of the track.

        """
        track = self._playlist.get_track_by_index(index)

        logger.info(
            "Playback requested for new selected track: '%s'",
            track.title
        )

        if track is not None:
            self._selected_track = track
            self._track_index = index

            audio = TrackAudio.from_file(track.path)
            if audio is not None:
                # Triggers 'playback start' on successful load.
                self._audio_player.load_track_audio(audio)

    # --- Custom signal event handler ---
    def _on_player_audio_loaded(self) -> None:
        """Update state and start playback when audio finishes loading."""
        self.track_loaded.emit(self._selected_track)

        self._audio_player.start_playback()

    def _on_playback_started(self) -> None:
        """Emit playback started signal with track duration."""
        logger.info("Now playing: %s", self._selected_track.title)

        self._state.current_track = self._selected_track
        self._state.track_index = self._track_index

        self._selected_track = None
        self._track_index = None

    def _on_playback_position_changed(self, elapsed_time: float) -> None:
        """Emit position update with elapsed and remaining time.

        Args:
            elapsed_time: Seconds elapsed since playback start.

        """
        time_remaining = self._state.current_track.duration - elapsed_time

        self.playback_position_changed.emit(elapsed_time, time_remaining)

    def _on_player_state_changed(self, new_status: PlaybackStatus):
        self._state.playback_status = new_status

        self.player_state_changed.emit(new_status)

    # --- Public methods (Commands) ---
    def toggle_playback(self) -> None:
        """Start new, pause, and resume playback based on the current player state."""
        playback_status = self._state.playback_status

        # Resume
        if playback_status == PlaybackStatus.PAUSED:
            self.resume()

        # Pause
        elif playback_status == PlaybackStatus.PLAYING:
            self.pause()

        # Start new playback
        else:
            self.play()

    def play(self) -> None:
        selected_index = self._playlist.get_selected_index()

        self._play_track_at_index(selected_index)

    def pause(self) -> None:
        if self._state.playback_status != PlaybackStatus.PLAYING:
            return

        self._audio_player.pause_playback()

    def resume(self) -> None:
        if self._state.playback_status != PlaybackStatus.PAUSED:
            return

        self._audio_player.resume_playback()

    def next_track(self) -> None:
        """Play next track."""
        next_index = self._state.track_index + 1
        new_selected_index = self._playlist.set_selected_index(next_index)

        if new_selected_index is not None:
            self._play_track_at_index(new_selected_index)

    def previous_track(self) -> None:
        """Play previous track."""
        prev_index = self._state.track_index - 1
        new_selected_index = self._playlist.set_selected_index(prev_index)

        if new_selected_index is not None:
            self._play_track_at_index(new_selected_index)

    def seek(self, new_position_in_ms: int) -> None:
        self._audio_player.seek(new_position_in_ms)

    # --- Queries ---
    # Note: Expose only what is needed
    def get_playback_status(self) -> PlaybackStatus:
        return self._state.playback_status
