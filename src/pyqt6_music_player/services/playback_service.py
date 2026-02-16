from pyqt6_music_player.constants import PlaybackStatus
from pyqt6_music_player.models import (
    AudioPlayerService,
    PlaybackState,
    Track,
    TrackAudio
)
from pyqt6_music_player.services import PlaylistService
from pyqt6_music_player.signals import Signal


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
        # self._current_track = None
        # self._track_index = None

        # Signals
        self.track_loaded = Signal()
        self.playback_started = Signal()
        self.playback_position_changed = Signal()
        self.player_state_changed = Signal()

        self._connect_signals()

    # --- Private methods ---
    def _connect_signals(self) -> None:
        """Establish signal-handler connections between the service and viewmodel."""
        self._audio_player.audio_loaded.connect(self._on_audio_loaded)
        self._audio_player.playback_started.connect(self._on_playback_started)
        self._audio_player.playback_position_changed.connect(
            self._on_playback_position_changed,
        )
        self._audio_player.playback_finished.connect(self.next_track)
        self._audio_player.playback_status_changed.connect(self._on_player_state_changed)

    @staticmethod
    def _get_audio_from_track(track: Track) -> TrackAudio | None:
        """Decode audio from the given track.

        Args:
            track: The given track.

        Returns:
            ``TrackAudio`` instance or ``None`` if the given track is invalid.
        """
        return TrackAudio.from_file(track.path)

    def _play_track_at_index(self, index: int) -> None:
        """Play specific track based on the given index.

        Args:
            index: The playlist index of the track.

        """
        track = self._playlist.get_track_by_index(index)
        if track is not None:
            audio = self._get_audio_from_track(track)
            if audio is not None:
                self._audio_player.load_track_audio(audio)

    # --- Custom signal event handler ---
    def _on_audio_loaded(self) -> None:
        """Update state and start playback when audio finishes loading."""
        selected_index = self._playlist.get_selected_index()
        selected_track = self._playlist.get_track_by_index(selected_index)

        self._state.current_track = selected_track
        self._state.track_index = selected_index

        self.track_loaded.emit(selected_track)

        self._audio_player.start_playback()

    def _on_playback_started(self) -> None:
        """Emit playback started signal with track duration."""
        track_duration = self._state.current_track.duration

        self.playback_started.emit(track_duration)

    def _on_playback_position_changed(self, elapsed_time: float) -> None:
        """Emit position update with elapsed and remaining time.

        Args:
            elapsed_time: Seconds elapsed since playback start.

        """
        time_remaining = self._state.current_track.duration - elapsed_time

        self.playback_position_changed.emit(elapsed_time, time_remaining)

    def _on_player_state_changed(self, playback_status: PlaybackStatus):
        self._state.playback_status = playback_status

        self.player_state_changed.emit(playback_status)

    # --- Public methods (Commands) ---
    def play_pause(self) -> None:
        """Start new, pause, and resume playback based on the current player state."""
        curr_playback_status = self._state.playback_status

        # Resume
        if curr_playback_status is PlaybackStatus.PAUSED:
            self._audio_player.resume_playback()

        # Pause
        elif curr_playback_status is PlaybackStatus.PLAYING:
            self._audio_player.pause_playback()

        # Start new playback
        else:
            selected_index = self._playlist.get_selected_index()

            self._play_track_at_index(selected_index)

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
