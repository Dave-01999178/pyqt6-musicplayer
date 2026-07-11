import logging

import numpy as np
from pyaudio import PyAudio, paComplete, paContinue
from PyQt6.QtCore import Q_ARG, QMetaObject, QObject, Qt, pyqtSignal, pyqtSlot

from pyqt6_music_player.core import PlaybackState
from pyqt6_music_player.track import AudioPCM

logger = logging.getLogger(__name__)


class AudioPlayerWorker(QObject):
    """Handles low-level audio playback operations in a separate thread.

    Manages PyAudio stream lifecycle, audio buffer processing, and playback state.
    Must run in a worker thread, not the main thread.
    """

    FRAMES_PER_BUFFER: int = 1024

    playback_started = pyqtSignal()
    playback_finished = pyqtSignal()
    playback_position_changed = pyqtSignal(float)
    playback_state_changed = pyqtSignal(PlaybackState)
    playback_cleared = pyqtSignal()
    resources_released = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        # Not an actual track ID, used to detect stale frame position updates
        self._track_id: int = 0

        self._audio_pcm: AudioPCM | None = None  # PCM data and format parameters
        self._silence_bytes: bytes | None = None  # Silence bytes for pause
        self._current_frame_position: int = 0
        self._volume: float = 1.0
        self._state: PlaybackState = PlaybackState.IDLE

        self._pa: PyAudio | None = None
        self._stream: PyAudio.Stream | None = None

    # -- Public methods --
    @pyqtSlot(AudioPCM)
    def play_audio(self, audio_pcm: AudioPCM) -> None:
        """Play the given audio.

        Stops the current playback and releases any existing stream before loading the
        new audio.

        Args:
            audio_pcm: The track audio data to load for playback.

        """
        # PyAudio streams are session-specific and hold native audio resources.
        # They cannot be reused safely across different tracks, so we close the
        # previous stream before creating a new one.
        self._stop_playback()
        self._release_stream()

        # Load audio and start playback
        self._load_audio(audio_pcm)
        self._start_playback()

    @pyqtSlot()
    def pause_playback(self) -> None:
        self._set_playback_state(PlaybackState.PAUSED)

        logger.info("Playback paused.")

    @pyqtSlot()
    def resume_playback(self) -> None:
        self._set_playback_state(PlaybackState.PLAYING)

        logger.info("Playback resumed.")

    @pyqtSlot()
    def restart_playback(self):
        self._stream.stop_stream()

        self._set_frame_position(0, self._track_id)

        self._stream.start_stream()

    @pyqtSlot()
    def clear_playback(self) -> None:
        """Release current stream and reset the playback state to default."""
        self._release_stream()

        self._reset_worker_state()

        self.playback_cleared.emit()

        logger.info("Playback cleared.")

    @pyqtSlot(int)
    def seek(self, position_in_ms: int):
        """Seek to the given position.

        Pauses playback if currently playing to prevent audio artifacts.

        Args:
            position_in_ms: Target position in milliseconds.

        """
        if self._audio_pcm is None:
            return

        if self._state is PlaybackState.PLAYING:
            self._set_playback_state(PlaybackState.PAUSED, notify=False)

        frame_position = int((position_in_ms / 1000) * self._audio_pcm.sample_rate)

        self._set_frame_position(frame_position, self._track_id)

    @pyqtSlot(int)
    def set_volume(self, volume: int) -> None:
        clamped_volume = max(0, min(100, volume))

        self._volume = clamped_volume / 100

    @pyqtSlot()
    def release_resources(self) -> None:
        """Stop the stream before releasing PyAudio resources."""
        self._stop_playback()

        self._release_stream()
        self._release_pyaudio()

        self._reset_worker_state()

        self.resources_released.emit()

        logger.info("Worker resources released.")

    # -- Protected/internal methods --
    def _initialize_pyaudio_and_stream(self) -> None:
        if self._pa is None:
            self._pa = PyAudio()

        if self._stream is None:
            self._stream = self._pa.open(
                rate=self._audio_pcm.sample_rate,
                channels=self._audio_pcm.channels,
                format=self._pa.get_format_from_width(self._audio_pcm.sample_width),
                output=True,
                frames_per_buffer=self.FRAMES_PER_BUFFER,
                stream_callback=self._audio_callback,
            )

    def _to_pcm_bytes(self, samples: np.ndarray, volume: float) -> bytes:
        scale = self._audio_pcm.orig_scale
        dtype = self._audio_pcm.orig_dtype

        # Apply volume then clamp to valid normalized range
        samples = (samples * volume).clip(-1.0, 1.0)

        # Denormalize float samples back to original integer range
        if np.issubdtype(dtype, np.unsignedinteger):
            # Unsigned: shift from [-1.0, 1.0] back to [0, 2 * scale - 1]
            samples_int = (
                    samples * scale + scale
            ).clip(
                0,
                2 * scale - 1,
            ).astype(dtype)

        else:
            # Signed: scale from [-1.0, 1.0] back to [-scale, scale]
            samples_int = (
                    samples * scale
            ).clip(
                -scale,
                scale,
            ).astype(dtype)

        return samples_int.tobytes()

    def _prepare_silence_bytes(self) -> None:
        if self._audio_pcm is None:
            return

        # Create silence array for 'pause' playback.
        bytes_per_frame = self._audio_pcm.sample_width * self._audio_pcm.channels
        bytes_per_buffer = self.FRAMES_PER_BUFFER * bytes_per_frame

        self._silence_bytes = b"\x00" * bytes_per_buffer

    def _audio_callback(
            self,
            _in_data,
            frame_count,
            _time_info,
            _status_flags,
    ) -> tuple[bytes | None, int]:
        current_track_id = self._track_id
        audio_pcm = self._audio_pcm
        start = self._current_frame_position
        state = self._state

        # PLAYBACK STATE SET TO 'STOPPED' - end callback
        if start > 0 and state in {PlaybackState.IDLE, PlaybackState.STOPPED}:
            return None, paComplete

        # PLAYBACK STATE SET TO 'PAUSED' - feed silence bytes
        if state is PlaybackState.PAUSED:
            return self._silence_bytes, paContinue

        # PLAYBACK STATE SET TO 'PLAYING' OR WHILE STREAM IS ACTIVE - feed audio bytes
        end = start + self.FRAMES_PER_BUFFER
        buffer = audio_pcm.samples[start:end]
        buffer_size = len(buffer)
        total_frames = len(audio_pcm.samples)
        volume = self._volume

        # Pad the last chunk with silence if it is '<' the expected buffer size
        # PyAudio requires an exact frame count on every callback tick
        if buffer_size < frame_count:
            padding_size = frame_count - buffer_size
            silence_padding = np.zeros(
                (
                    padding_size,
                    audio_pcm.channels,
                ),
                dtype=np.float32,
            )
            buffer = np.concatenate((buffer, silence_padding))

        # Prepare chunk bytes before the position update
        pcm_bytes = self._to_pcm_bytes(buffer, volume)
        next_frame_pos = min(end, total_frames)

        # Update frame position
        QMetaObject.invokeMethod(
            self,
            "_set_frame_position",
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(int, next_frame_pos),
            Q_ARG(int, current_track_id),
        )

        # Feed the last chunk then signal the end of callback
        if next_frame_pos >= total_frames:
            QMetaObject.invokeMethod(
                self,
                "_on_playback_finished",
                Qt.ConnectionType.QueuedConnection,
            )
            return pcm_bytes, paComplete

        return pcm_bytes, paContinue  # Continue callback

    def _load_audio(self, audio_pcm: AudioPCM) -> None:
        self._audio_pcm = audio_pcm
        self._current_frame_position = 0  # Reset playback position

        # Increment track ID to invalidate any queued position updates from
        # the previous track's audio callback
        self._track_id += 1

        # Pre-process silence bytes for 'pause' playback.
        self._prepare_silence_bytes()

    def _start_playback(self) -> None:
        if self._audio_pcm is None:
            logger.warning("Cannot start playback: Audio PCM is not initialized.")
            return

        self._initialize_pyaudio_and_stream()

        self._set_playback_state(PlaybackState.PLAYING)

        self._stream.start_stream()

        self.playback_started.emit()

        logger.info("Playback started.")

    def _stop_playback(self) -> None:
        if self._state in {PlaybackState.PLAYING, PlaybackState.PAUSED}:
            self._set_playback_state(PlaybackState.STOPPED)

            logger.info("Playback stopped.")

    def _set_playback_state(self, state: PlaybackState, notify: bool = True) -> None:
        if self._state == state:
            return

        self._state = state

        # Optional signal notification to avoid unwanted reactions.
        if notify:
            self.playback_state_changed.emit(self._state)

    def _reset_worker_state(self) -> None:
        # Reset track ID to invalidate any queued position updates from
        # the current audio callback before resetting playback state
        self._track_id = 0

        self._audio_pcm = None
        self._silence_bytes = None
        self._current_frame_position = 0
        self._set_playback_state(PlaybackState.IDLE)

    def _release_stream(self) -> None:
        if self._stream is None:
            return

        # Stop the stream before closing for safe release
        if self._stream.is_active():
            self._stream.stop_stream()

        self._stream.close()

        self._stream = None

        logger.info("PyAudio.Stream successfully released.")

    def _release_pyaudio(self) -> None:
        if self._pa is None:
            return

        self._pa.terminate()

        self._pa = None

        logger.info("PyAudio successfully released.")

    def _on_frame_position_changed(self, frame_position: int) -> None:
        # Convert and emit frame position in seconds
        self.playback_position_changed.emit(
            frame_position / self._audio_pcm.sample_rate,
        )

    @pyqtSlot()
    def _on_playback_finished(self) -> None:
        self.playback_finished.emit()

        self._set_playback_state(PlaybackState.STOPPED)

        logger.info("Playback finished.")

    @pyqtSlot(int, int)
    def _set_frame_position(self, frame_position: int, track_id: int) -> None:
        # Update playback position with track ID validation.
        #
        # Ignore stale position updates from last track
        if self._track_id != track_id:
            return

        self._current_frame_position = frame_position
        self._on_frame_position_changed(self._current_frame_position)
