import logging

import numpy as np
from pyaudio import PyAudio, paComplete, paContinue
from PyQt6.QtCore import (
    Q_ARG,
    QMetaObject,
    QObject,
    Qt,
    pyqtSignal,
    pyqtSlot,
)

from pyqt6_music_player.core import PlaybackState
from pyqt6_music_player.models import AudioPCM

logger = logging.getLogger(__name__)


# noinspection PyUnresolvedReferences
class AudioPlayerWorker(QObject):
    """Handles low-level audio playback operations in a separate thread.

    Manages PyAudio stream lifecycle, audio buffer processing, and playback state.
    Must run in a worker thread, not the main thread.
    """

    audio_loaded = pyqtSignal()
    playback_started = pyqtSignal()
    playback_finished = pyqtSignal()
    playback_position_changed = pyqtSignal(float)
    status_changed = pyqtSignal(PlaybackState)
    resources_released = pyqtSignal()

    def __init__(self) -> None:
        """Initialize AudioPlayerWorker."""
        super().__init__()
        self._audio_pcm: AudioPCM | None = None  # PCM data and format parameters
        self._frames_per_buffer: int = 1024
        self._silence_bytes: bytes | None = None  # Silence bytes for 'pause' playback
        self._frame_position: int = 0  # Playback position in frames
        self._volume: float = 1.0
        self._status: PlaybackState = PlaybackState.IDLE

        # Not an actual track ID, used to detect stale frame position updates
        self._track_id = 0

        # PyAudio objects
        self._pa: PyAudio | None = None
        self._stream: PyAudio.Stream | None = None

    # --- Public methods ---
    @pyqtSlot(AudioPCM)
    def load_track_audio(self, audio_pcm: AudioPCM) -> None:
        """Load new track audio and reset playback state.

        Releases any existing stream before loading new audio data.

        Args:
            audio_pcm: Track audio data to load for playback.

        """
        # PyAudio streams are session-specific and hold native audio resources.
        # They cannot be reused safely across different tracks, so we close the
        # previous stream before creating a new one.
        self._release_stream()

        self._audio_pcm = audio_pcm
        self._frame_position = 0  # Reset playback position

        # Increment track ID to invalidate any queued position updates from
        # the previous track's audio callback
        self._track_id += 1

        self._prepare_silence_bytes()

        self.audio_loaded.emit()

    @pyqtSlot()
    def start_playback(self) -> None:
        """Initialize PyAudio, and begin audio playback."""

        if self._audio_pcm is None:
            logger.warning("Cannot start playback: Audio PCM is not initialized.")
            return

        try:
            self._initialize_pyaudio()
            self._stream.start_stream()

        except Exception as e:
            logger.error("Failed to start playback. %s", e)

            self._set_status(PlaybackState.ERROR)

    @pyqtSlot()
    def repeat_playback(self):
        try:
            self._stream.stop_stream()

            self._set_frame_position(0, self._track_id)

            self._stream.start_stream()

        except Exception as e:
            logger.error("Failed to start playback. %s", e)

            self._set_status(PlaybackState.ERROR)

    @pyqtSlot()
    def pause_playback(self) -> None:
        """Pause current playback."""
        self._set_status(PlaybackState.PAUSED)

        logger.info("Playback paused.")

    @pyqtSlot()
    def resume_playback(self) -> None:
        """Resume paused playback from current position."""
        self._set_status(PlaybackState.PLAYING)

        logger.info("Playback unpaused.")

    @pyqtSlot(int)
    def seek(self, position_in_ms: int):
        """Seek to the given position.

        Pauses playback if currently playing to prevent audio artifacts.

        Args:
            position_in_ms: Target position in milliseconds.

        """
        # Guard against seek attempt when no track is loaded
        if self._audio_pcm is None:
            return

        # Guard against audio artifacts when seeking to a specific position
        # while playback is active
        if self._status is PlaybackState.PLAYING:
            self._set_status(PlaybackState.PAUSED, notify=False)

        frame_position = int((position_in_ms / 1000) * self._audio_pcm.sample_rate)

        self._set_frame_position(frame_position, self._track_id)

    @pyqtSlot(float)
    def set_volume(self, volume: float) -> None:
        """Set the playback volume.

        Args:
            volume: Volume level in range [0.0, 1.0].

        """
        self._volume = volume

    @pyqtSlot()
    def release_resources(self) -> None:
        """Release PyAudio stream and instance, freeing audio resources."""
        self._release_stream()
        self._release_pyaudio()

        self.resources_released.emit()

        logger.info("Worker resources released.")

    # --- Protected/internal methods ---
    def _initialize_pyaudio(self) -> None:
        """Initialize PyAudio instance and stream."""
        if self._pa is None:
            self._pa = PyAudio()

        if self._stream is None:
            self._stream = self._pa.open(
                rate=self._audio_pcm.sample_rate,
                channels=self._audio_pcm.channels,
                format=self._pa.get_format_from_width(self._audio_pcm.sample_width),
                output=True,
                frames_per_buffer=self._frames_per_buffer,
                stream_callback=self._audio_callback,
            )

    def _chunk_to_pcm_bytes(self, samples_chunk: np.ndarray, volume: float) -> bytes:
        """Convert a normalized float sample chunk to PCM bytes with volume applied.

        Args:
            samples_chunk: Normalized float32 samples of shape (frames, channels).
            volume: Volume multiplier in range [0.0, 1.0].

        Returns:
            PCM bytes ready for PyAudio output.

        """
        scale = self._audio_pcm.orig_scale
        dtype = self._audio_pcm.orig_dtype

        # Apply volume then clamp to valid normalized range
        samples_chunk = (samples_chunk * volume).clip(-1.0, 1.0)

        # Denormalize float samples back to original integer range
        if np.issubdtype(dtype, np.unsignedinteger):
            # Unsigned: shift from [-1.0, 1.0] back to [0, 2 * scale - 1]
            samples_int = (
                    samples_chunk * scale + scale
            ).clip(
                0, 2 * scale - 1,
            ).astype(dtype)

        else:
            # Signed: scale from [-1.0, 1.0] back to [-scale, scale]
            samples_int = (
                    samples_chunk * scale
            ).clip(
                -scale,
                scale,
            ).astype(dtype)

        return samples_int.tobytes()

    def _prepare_silence_bytes(self) -> None:
        if self._audio_pcm is None:
            return

        # Create 'silence' array for 'pause' playback.
        bytes_per_frame = self._audio_pcm.sample_width * self._audio_pcm.channels
        bytes_per_buffer = self._frames_per_buffer * bytes_per_frame

        self._silence_bytes = b"\x00" * bytes_per_buffer

    def _audio_callback(
            self,
            _in_data,
            frame_count,
            _time_info,
            _status_flags,
    ) -> tuple[bytes | None, int]:
        # Callback for playing pcm bytes, used by PyAudio stream.
        current_track_id = self._track_id
        start = self._frame_position
        status = self._status

        # Handle playback start
        if start == 0 and status in {PlaybackState.IDLE, PlaybackState.STOPPED}:
            QMetaObject.invokeMethod(
                self,
                "_on_playback_started",
                Qt.ConnectionType.QueuedConnection,
            )

        # Exit callback when stopped mid-playback or a stale position update occurred.
        #
        # This prevents:
        # - Continuing to read from old track's buffer after stream closure
        # - Position updates from wrong track causing UI jumps
        # - Static noise from reading audio at incorrect byte positions
        if start > 0 and status in {PlaybackState.ERROR, PlaybackState.STOPPED}:
            return None, paComplete

        # Handle pause by outputting silence.
        if status is PlaybackState.PAUSED:
            return self._silence_bytes, paContinue

        # Actual playback
        end = start + self._frames_per_buffer
        buffer = self._audio_pcm.samples[start:end]
        buffer_size = len(buffer)
        total_frames = len(self._audio_pcm.samples)
        volume = self._volume

        # Pad the last chunk with silence if it's smaller than the expected buffer size
        # PyAudio requires an exact frame count on every callback tick
        if buffer_size < frame_count:
            padding_size = frame_count - buffer_size
            silence_padding = np.zeros((padding_size, self._audio_pcm.channels), dtype=np.float32)
            buffer = np.concatenate((buffer, silence_padding))

        # Prepare chunk before position update so the last chunk is still returned
        pcm_bytes = self._chunk_to_pcm_bytes(buffer, volume)

        # Update frame position for next buffer
        next_frame_pos = min(end, total_frames)

        # Queue position update with track ID for validation and to keep the UI in sync
        QMetaObject.invokeMethod(
            self,
            "_set_frame_position",
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(int, next_frame_pos),
            Q_ARG(int, current_track_id),
        )

        # Return last audio chunk so PyAudio plays it fully
        if next_frame_pos >= total_frames:
            QMetaObject.invokeMethod(
                self,
                "_on_playback_finished",
                Qt.ConnectionType.QueuedConnection,
            )
            return pcm_bytes, paComplete

        return pcm_bytes, paContinue

    @pyqtSlot(int, int)
    def _set_frame_position(self, frame_position: int, track_id: int) -> None:
        """Update playback position with track ID validation.

        Discards position updates from previous tracks to prevent race conditions
        during rapid track switching. This is the final guard against stale updates
        that were queued before the stream was released.

        Args:
            frame_position: New frame position in the audio buffer.
            track_id: Track ID when this update was queued.

        """
        # Reject stale position updates from previous tracks
        if self._track_id != track_id:
            return

        if self._frame_position == frame_position:
            return

        # Set and emit new frame position.
        self._frame_position = frame_position

        self._on_frame_position_changed(self._frame_position)

    def _on_frame_position_changed(self, frame_position: int) -> None:
        # Convert and emit frame position in seconds
        self.playback_position_changed.emit(
            frame_position / self._audio_pcm.sample_rate,
        )

    def _set_status(self, status: PlaybackState, notify=True) -> None:
        if self._status == status:
            return

        # Update and emit new playback state with optional notification.
        self._status = status

        if notify:
            self.status_changed.emit(self._status)

    def _release_stream(self) -> None:
        if self._stream is None:
            return

        # Release PyAudio stream safely.
        #
        # Stop the audio callback before releasing the stream
        # This prevents the callback from accessing the stream during closure
        if self._status in {PlaybackState.PLAYING, PlaybackState.PAUSED}:
            self._set_status(PlaybackState.STOPPED)

            logger.info("Playback stopped.")

        try:
            # Ensure that the stream is not active before closing it for safe release
            if self._stream.is_active():
                self._stream.stop_stream()

            self._stream.close()
            logger.info("PyAudio stream successfully released.")

        except Exception as e:
            logger.warning(
                "PyAudio stream forced release due to an error: %s\n",
                e,
            )

        finally:
            self._stream = None

    def _release_pyaudio(self) -> None:
        if self._pa is not None:
            try:
                self._pa.terminate()
                logger.info("PyAudio instance successfully released.")

            except Exception as e:
                logger.warning(
                    "PyAudio instance forced release due to an error: %s\n",
                    e,
                )
            finally:
                self._pa = None

    @pyqtSlot()
    def _on_playback_started(self) -> None:
        self._set_status(PlaybackState.PLAYING)

        self.playback_started.emit()

        logger.info("Playback started.")

    @pyqtSlot()
    def _on_playback_finished(self) -> None:
        self.playback_finished.emit()

        self._set_status(PlaybackState.STOPPED)

        logger.info("Playback finished.")
