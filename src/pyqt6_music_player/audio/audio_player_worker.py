import logging

import numpy as np
from pyaudio import PyAudio, paComplete, paContinue
from PyQt6.QtCore import (
    Q_ARG,
    QMetaObject,
    QObject,
    Qt,
    QThread,
    pyqtSignal,
    pyqtSlot,
)
from PyQt6.QtWidgets import QApplication

from pyqt6_music_player.core import PlaybackStatus
from pyqt6_music_player.models import TrackAudio

logger = logging.getLogger(__name__)


# ================================================================================
# AUDIO PLAYER WORKER
# ================================================================================
#
# noinspection PyUnresolvedReferences
class AudioPlayerWorker(QObject):
    audio_loaded = pyqtSignal()
    playback_started = pyqtSignal()
    byte_position_changed = pyqtSignal(float)
    status_changed = pyqtSignal(PlaybackStatus)
    playback_finished = pyqtSignal()
    playback_error = pyqtSignal()
    resources_released = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        # Playback data
        self._audio_data: TrackAudio | None = None  # Track audio
        self._audio_bytes: bytes | None = None  # Audio bytes for actual playback
        self._silence_bytes: bytes | None = None  # Silence bytes for 'pause' playback

        # Playback info/state
        self._frames_per_buffer: int = 1024  # Buffer size
        self._bytes_per_frame: int = 0   # Total bytes per frame
        self._bytes_per_buffer: int = 0  # Total bytes per buffer
        self._byte_position: int = 0  # Current byte position
        self._status: PlaybackStatus = PlaybackStatus.IDLE

        # PyAudio objects
        self._pa: PyAudio | None = None
        self._stream: PyAudio.Stream | None = None

    # --- Private methods ---
    def _ensure_thread(self) -> None:
        main_thread = QApplication.instance().thread()
        current_thread = QThread.currentThread()

        if current_thread == main_thread:
            raise RuntimeError(
                f"{self.__class__.__name__} must be called from a worker thread.",
            )

    def _initialize_pyaudio(self) -> None:
        """Initialize PyAudio and stream."""
        if self._pa is None:
            self._pa = PyAudio()

        if self._stream is None:
            self._stream = self._pa.open(
                rate=self._audio_data.sample_rate,
                channels=self._audio_data.channels,
                format=self._pa.get_format_from_width(self._audio_data.sample_width),
                output=True,
                frames_per_buffer=self._frames_per_buffer,
                stream_callback=self._audio_callback,
            )

    def _set_status(self, status: PlaybackStatus, notify=True) -> None:
        """Playback status private setter.

        Notifies the external observers of playback status changes.

        Args:
            status: The new playback status.

        """
        if self._status == status:
            return

        self._status = status

        if notify:
            self.status_changed.emit(self._status)

    def _prepare_audio_bytes(self) -> None:
        """Pre-process buffer sizes and audio bytes for audio callback use."""
        samples = self._audio_data.samples
        sample_width = self._audio_data.sample_width
        dtype = self._audio_data.orig_dtype
        dtype_max = self._audio_data.orig_dtype_max

        # Convert float PCM back to its original dtype (np.integer).
        if sample_width == 1:
            samples_int = ((samples * dtype_max) + dtype_max).astype(dtype)
        else:
            samples_int = (samples * dtype_max).astype(dtype)

        # Ensure that the PCM array is contiguous.
        samples_int = np.ascontiguousarray(samples_int)

        # Convert PCM array (np.integer) to bytes.
        self._audio_bytes = samples_int.tobytes()

        # Precompute frame and buffer byte sizes.
        self._bytes_per_frame = samples_int.strides[0]
        self._bytes_per_buffer = self._frames_per_buffer * self._bytes_per_frame

        # Create 'silence' array for 'pause' playback.
        self._silence_bytes = b"\x00" * self._bytes_per_buffer

    def _audio_callback(
            self,
            _in_data,
            frame_count,
            _time_info,
            _status_flags,
    ) -> tuple[bytes | None, int]:
        """Callback for playing audio bytes, used by PyAudio stream.

        Returns:
            Audio bytes or ``None``, and PortAudio callback return code in tuple
            (bytes | None, return code).

        """
        if self._audio_data is None or self._audio_bytes is None:
            return None, paComplete

        status = self._status
        start = self._byte_position

        # Start
        if start == 0 and status in {PlaybackStatus.STOPPED, PlaybackStatus.IDLE}:
            QMetaObject.invokeMethod(
                self,
                "_on_playback_started",
                Qt.ConnectionType.QueuedConnection,
            )

        # Stop
        if start > 0 and status is PlaybackStatus.STOPPED:
            QMetaObject.invokeMethod(
                self,
                "_on_playback_finished",
                Qt.ConnectionType.QueuedConnection,
            )
            return None, paComplete

        # Pause
        if status is PlaybackStatus.PAUSED:
            return self._silence_bytes, paContinue

        # Actual playback
        end = start + self._bytes_per_buffer
        buffer = self._audio_bytes[start:end]
        curr_buffer_size = len(buffer)
        total_bytes = len(self._audio_bytes)

        # If the current buffer size is less than the expected buffer size
        # (left over), fill up the missing buffer by padding with silence bytes.
        # PyAudio.Stream expects an exact buffer size.
        if curr_buffer_size < frame_count:
            buffer += self._silence_bytes[:frame_count - curr_buffer_size]

        # Update byte position for next buffer.
        next_byte_pos = min(end, total_bytes)

        # Emit updated byte position to keep the UI in sync.
        QMetaObject.invokeMethod(
            self,
            "_set_byte_position",
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(int, next_byte_pos),
        )

        # If all bytes are played, end the callback.
        if next_byte_pos >= total_bytes:
            QMetaObject.invokeMethod(
                self,
                "_on_playback_finished",
                Qt.ConnectionType.QueuedConnection,
            )
            return None, paComplete

        return buffer, paContinue

    def _release_stream(self) -> None:
        """Release PyAudio stream."""
        if self._stream is None:
            return

        # Stop the current PyAudio stream before releasing it.
        if self._status not in {PlaybackStatus.STOPPED, PlaybackStatus.IDLE}:
            self._set_status(PlaybackStatus.STOPPED)
            logger.info("Playback stopped.")

        try:
            # Ensure that the stream is not active before closing it for safe release.
            if self._stream.is_active():
                self._stream.stop_stream()

            self._stream.close()
            logger.info("Stream successfully released.")

        except Exception as e:
            logger.warning(
                "PyAudio stream forced release due to an error: %s\n",
                e,
            )

        finally:
            self._stream = None

    def _release_pyaudio(self) -> None:
        """Release PyAudio instance."""
        if self._pa is not None:
            try:
                self._pa.terminate()
                logger.info("PyAudio successfully released.")

            except Exception as e:
                logger.warning(
                    "PyAudio instance forced release due to an error: %s\n",
                    e,
                )
            finally:
                self._pa = None

    # --- Slots ---
    @pyqtSlot(TrackAudio)
    def load_track_audio(self, track_audio: TrackAudio) -> None:
        """Load new track audio.

        Releases previous stream, and resets playback position before loading
        the new audio.

        Args:
            track_audio: Track audio data to load for playback.

        """
        self._ensure_thread()

        # Release the previous stream for a clean start since we can't reuse them.
        self._release_stream()

        self._audio_data = track_audio
        self._byte_position = 0

        self.audio_loaded.emit()

    @pyqtSlot()
    def start_playback(self) -> None:
        """Initialize PyAudio stream and begin audio playback."""
        try:
            self._ensure_thread()
            self._initialize_pyaudio()
            self._prepare_audio_bytes()
            self._stream.start_stream()

        except Exception as e:
            logger.error("Failed to start playback. %s", e)

            self._set_status(PlaybackStatus.STOPPED)

            self.playback_error.emit()

    @pyqtSlot()
    def pause_playback(self) -> None:
        """Pause current playback."""
        self._ensure_thread()

        self._set_status(PlaybackStatus.PAUSED)

        logger.info("Playback paused.")

    @pyqtSlot()
    def resume_playback(self) -> None:
        """Resume paused playback from current position."""
        self._ensure_thread()

        self._set_status(PlaybackStatus.PLAYING)

        logger.info("Playback unpaused.")

    @pyqtSlot(int)
    def seek(self, new_position_in_ms: int):
        self._set_status(PlaybackStatus.PAUSED, notify=False)

        bytes_per_second = self._audio_data.sample_rate * self._bytes_per_frame
        byte_pos = int((new_position_in_ms / 1000) * bytes_per_second)

        # Snap to the nearest frame boundary to avoid mid-frame reads
        # that causes static noise.
        byte_pos -= byte_pos % self._bytes_per_frame

        self._set_byte_position(byte_pos)

    @pyqtSlot(int)
    def _set_byte_position(self, byte_position):
        if self._byte_position == byte_position:
            return

        self._byte_position = byte_position

        self._on_byte_position_changed(self._byte_position)

    @pyqtSlot()
    def release_resources(self) -> None:
        """Release PyAudio stream and instance, freeing audio resources."""
        self._ensure_thread()
        self._release_stream()
        self._release_pyaudio()

        self.resources_released.emit()

        logger.info("Worker resources released.")

    @pyqtSlot()
    def _on_playback_started(self) -> None:
        """Emit playback started signal to external observers."""
        self._set_status(PlaybackStatus.PLAYING)

        self.playback_started.emit()

        logger.info("Playback started.")

    @pyqtSlot()
    def _on_playback_finished(self) -> None:
        """Release stream and emit completion signal when playback ends."""
        logger.info("Playback finished.")

        self._release_stream()

        self.playback_finished.emit()

    # TODO: Add playback ended signal and slot.

    def _on_byte_position_changed(self, byte_pos: int) -> None:
        """Convert byte position to seconds and emit byte position update signal.

        Args:
            byte_pos: Current byte position in audio stream.

        """
        bytes_per_second = self._audio_data.sample_rate * self._bytes_per_frame

        byte_pos_as_sec = byte_pos / bytes_per_second

        self.byte_position_changed.emit(byte_pos_as_sec)
