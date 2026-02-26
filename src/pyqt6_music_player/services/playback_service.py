import logging

from pyqt6_music_player.core import PlaybackStatus, Signal
from pyqt6_music_player.models import PlaybackState, Track, AudioPCM
from pyqt6_music_player.audio import AudioPlayerService
from pyqt6_music_player.services import PlaylistService

logger = logging.getLogger(__name__)


class PlaybackService:
    """Orchestrates playback operations and coordinates between audio player and playlist.

    Manages track selection, playback control, and state synchronization.

    """
    def __init__(
            self,
            audio_player: AudioPlayerService,
            playback_state: PlaybackState,
            playlist_service: PlaylistService,
    ):
        """Initialize PlaybackService."""
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

        # Setup
        self._connect_signals()

    # --- Public methods ---
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
        """Play the selected track in playlist."""
        selected_index = self._playlist.get_selected_index()

        self._play_track_at_index(selected_index)

    def pause(self) -> None:
        """Pause the current playback only if it is playing."""
        if self._state.playback_status != PlaybackStatus.PLAYING:
            return

        self._audio_player.pause_playback()

    def resume(self) -> None:
        """Resume the playback only if it is paused."""
        if self._state.playback_status != PlaybackStatus.PAUSED:
            return

        self._audio_player.resume_playback()

    def play_next_track(self) -> None:
        """Play next track."""
        next_index = self._state.track_index + 1
        new_selected_index = self._playlist.set_selected_index(next_index)

        if new_selected_index is not None:
            self._play_track_at_index(new_selected_index)

    def play_previous_track(self) -> None:
        """Play previous track."""
        prev_index = self._state.track_index - 1
        new_selected_index = self._playlist.set_selected_index(prev_index)

        if new_selected_index is not None:
            self._play_track_at_index(new_selected_index)

    def seek(self, new_position_in_ms: int) -> None:
        """Seek to a specific position.

        Args:
            new_position_in_ms: Target position in milliseconds.

        """
        self._audio_player.seek(new_position_in_ms)

    def get_playback_status(self) -> PlaybackStatus:
        """Returns the current playback status."""
        return self._state.playback_status

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
            self._selected_track = track
            self._track_index = index

            logger.info(
                "Playback requested for new selected track: '%s'",
                track.title
            )

            audio = AudioPCM.from_file(track.path)
            if audio is not None:
                # Triggers 'playback start' on successful load.
                self._audio_player.load_track_audio(audio)

    def _on_player_audio_loaded(self) -> None:
        # Emit loaded track then start playback
        self.track_loaded.emit(self._selected_track)

        self._audio_player.start_playback()

    def _on_playback_started(self) -> None:
        # Store the current track and its index
        logger.info("Now playing: %s", self._selected_track.title)

        self._state.current_track = self._selected_track
        self._state.track_index = self._track_index

        self._selected_track = None
        self._track_index = None

    def _on_playback_position_changed(self, elapsed_time: float) -> None:
        # Emit position update with elapsed and remaining time
        time_remaining = self._state.current_track.duration - elapsed_time

        self.playback_position_changed.emit(elapsed_time, time_remaining)

    def _on_player_state_changed(self, new_status: PlaybackStatus):
        # Store and emit new playback status
        self._state.playback_status = new_status

        self.player_state_changed.emit(new_status)
