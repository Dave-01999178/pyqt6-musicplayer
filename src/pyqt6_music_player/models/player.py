import logging
import threading

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

from pyqt6_music_player.constants import PlaybackStatus
from pyqt6_music_player.models import TrackAudio

logger = logging.getLogger(__name__)


# ================================================================================
# AUDIO PLAYER
# ================================================================================
#
# ----- Worker -----
# noinspection PyUnresolvedReferences
class AudioPlayerWorker(QObject):
    audio_loaded = pyqtSignal()
    playback_started = pyqtSignal()
    byte_position_changed = pyqtSignal(float)  # elapsed time, time remaining
    playback_status_changed = pyqtSignal(PlaybackStatus)
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
        self._playback_status: PlaybackStatus = PlaybackStatus.IDLE

        # PyAudio objects
        self._pa: PyAudio | None = None
        self._stream: PyAudio.Stream | None = None

        # Thread lock
        self._lock: threading.Lock = threading.Lock()

    # --- Private methods ---
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

    def _set_status(self, status: PlaybackStatus) -> None:
        """Playback status private setter.

        Notifies the external observers of playback status changes.

        Args:
            status: The new playback status.

        """
        with self._lock:
            self._playback_status = status

        self.playback_status_changed.emit(self._playback_status)

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

        curr_playback_status = self._playback_status
        total_bytes = len(self._audio_bytes)

        # Stop
        if curr_playback_status is PlaybackStatus.STOPPED:
            QMetaObject.invokeMethod(
                self,
                "_on_playback_ended",
                Qt.ConnectionType.QueuedConnection,
            )
            return None, paComplete

        # Pause
        if curr_playback_status is PlaybackStatus.PAUSED:
            return self._silence_bytes, paContinue

        # Actual playback
        start = self._byte_position
        end = start + self._bytes_per_buffer
        buffer = self._audio_bytes[start:end]
        curr_buffer_size = len(buffer)

        # Emit initial time on playback start.
        if start == 0:
            QMetaObject.invokeMethod(
                self,
                "_on_playback_started",
                Qt.ConnectionType.QueuedConnection,
            )

        # If the current buffer size is less than the expected buffer size
        # (left over), fill up the missing buffer by padding with silence bytes.
        # PyAudio.Stream expects an exact buffer size.
        if curr_buffer_size < frame_count:
            buffer += self._silence_bytes[:frame_count - curr_buffer_size]

        # Update byte position for next buffer.
        self._byte_position = min(end, total_bytes)

        # Emit updated byte position to keep UI in sync.
        QMetaObject.invokeMethod(
            self,
            "_on_byte_position_changed",
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(int, self._byte_position),
        )

        # If all bytes are played, end the callback.
        if self._byte_position >= total_bytes:
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

        # Set the playback status to 'stopped' to stop any stream callback
        # before releasing.
        if self._playback_status not in {PlaybackStatus.STOPPED, PlaybackStatus.IDLE}:
            self._set_status(PlaybackStatus.STOPPED)

        try:
            # Ensure that the stream is not active before closing.
            if self._stream.is_active():
                self._stream.stop_stream()

            self._stream.close()
            logger.info("Stream successfully released.")

        except Exception as e:
            logger.warning(
                "Force released PyAudio stream due to an error: %s\n",
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
                    "Force released PyAudio instance due to an error: %s\n",
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
        self._release_stream()  # Release PyAudio stream before loading the audio.

        self._byte_position = 0  # Reset byte position.
        self._audio_data = track_audio

        self.audio_loaded.emit()

    @pyqtSlot()
    def start_playback(self) -> None:
        """Initialize PyAudio stream and begin audio playback."""
        logger.info("Starting playback...")
        try:
            self._initialize_pyaudio()
            self._prepare_audio_bytes()
            self._stream.start_stream()

        except Exception as e:
            logger.error("Failed to start playback, error: %s.\n", e)

            self._set_status(PlaybackStatus.STOPPED)

            self.playback_error.emit()

    @pyqtSlot()
    def pause_playback(self) -> None:
        """Pause current playback."""
        self._set_status(PlaybackStatus.PAUSED)

        logger.info("Playback paused.\n")

    @pyqtSlot()
    def resume_playback(self) -> None:
        """Resume paused playback from current position."""
        self._set_status(PlaybackStatus.PLAYING)

        logger.info("Playback unpaused.\n")

    @pyqtSlot()
    def release_resources(self) -> None:
        """Release PyAudio stream and instance, freeing audio resources."""
        logger.info("Releasing worker resources...")

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
        self._release_stream()

        self.playback_finished.emit()

    @pyqtSlot(int)
    def _on_byte_position_changed(self, byte_pos: int) -> None:
        """Convert byte position to seconds and emit byte position update signal.

        Args:
            byte_pos: Current byte position in audio stream.

        """
        bytes_per_second = self._audio_data.sample_rate * self._bytes_per_frame

        byte_pos_as_sec = byte_pos / bytes_per_second

        self.byte_position_changed.emit(byte_pos_as_sec)

    # --- Properties ---
    @property
    def playback_status(self) -> PlaybackStatus:
        return self._playback_status


# ----- Service -----
# noinspection PyUnresolvedReferences
class AudioPlayerService(QObject):
    # Worker signals
    audio_loaded = pyqtSignal()
    playback_started = pyqtSignal()
    playback_position_changed = pyqtSignal(float)
    playback_status_changed = pyqtSignal(PlaybackStatus)
    playback_finished = pyqtSignal()
    worker_resources_released = pyqtSignal()

    # Service signals
    load_audio_requested = pyqtSignal(TrackAudio)
    start_playback_requested = pyqtSignal()
    pause_playback_requested = pyqtSignal()
    resume_playback_requested = pyqtSignal()
    shutdown_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._worker_thread = None
        self._worker = None

        self._init_thread_and_worker()

    # --- Slots (PyQt) ---
    @pyqtSlot()
    def _on_audio_load(self) -> None:
        """Emit audio loaded signal to external observers."""
        self.audio_loaded.emit()

    @pyqtSlot()
    def _on_playback_started(self) -> None:
        """Emit playback started signal to external observers."""
        self.playback_started.emit()

    @pyqtSlot(float)
    def _on_byte_position_changed(self, byte_pos_as_sec: float) -> None:
        """Emit playback position in seconds.

        Args:
            byte_pos_as_sec: Byte position in seconds.

        """
        self.playback_position_changed.emit(byte_pos_as_sec)

    @pyqtSlot()
    def _on_playback_finished(self):
        """Emit playback finished signal to external observers."""
        self.playback_finished.emit()

    @pyqtSlot(PlaybackStatus)
    def _on_playback_status_changed(self, playback_status: PlaybackStatus) -> None:
        self.playback_status_changed.emit(playback_status)

    @pyqtSlot()
    def _on_thread_finished(self):
        """Cleanup thread, and worker."""
        self._worker.deleteLater()
        self._worker = None

        self._worker_thread.deleteLater()
        self._worker_thread = None

        self.worker_resources_released.emit()

        logger.info("Worker and thread deleted.")

    # --- Private methods ---
    def _connect_signals(self) -> None:
        """Establish signal–slot connections between the service and worker."""
        if self._worker is None:
            return

        # Connect service signals to worker.
        self.load_audio_requested.connect(self._worker.load_track_audio)
        self.start_playback_requested.connect(self._worker.start_playback)
        self.pause_playback_requested.connect(self._worker.pause_playback)
        self.resume_playback_requested.connect(self._worker.resume_playback)
        self.shutdown_requested.connect(self._worker.release_resources)

        # Connect worker signals to service.
        self._worker.audio_loaded.connect(self._on_audio_load)
        self._worker.playback_started.connect(self._on_playback_started)
        self._worker.byte_position_changed.connect(self._on_byte_position_changed)
        self._worker.playback_status_changed.connect(self._on_playback_status_changed)
        self._worker.playback_finished.connect(self._on_playback_finished)
        self._worker.resources_released.connect(self._worker_thread.quit)
        self._worker_thread.finished.connect(self._on_thread_finished)

    def _init_thread_and_worker(self) -> None:
        """Initialize thread, and worker then connect signals."""
        if self._worker_thread is not None:
            return

        # Create thread and worker
        self._worker_thread = QThread()
        self._worker = AudioPlayerWorker()

        # Move worker to thread
        self._worker.moveToThread(self._worker_thread)

        # Connect service and worker signals
        self._connect_signals()

        # Start thread
        self._worker_thread.start()

        self.playback_status_changed.emit(self.playback_status)

    # --- Public methods (Commands) ---
    def load_track_audio(self, track_audio: TrackAudio):
        """Load track audio."""
        if not isinstance(track_audio, TrackAudio):
            return

        self.load_audio_requested.emit(track_audio)

    def start_playback(self) -> None:
        """Start new playback."""
        self.start_playback_requested.emit()

    def pause_playback(self) -> None:
        """Pause current playback."""
        self.pause_playback_requested.emit()

    def resume_playback(self) -> None:
        """Resume paused playback from current position."""
        self.resume_playback_requested.emit()

    def is_running(self) -> bool:
        """Check if there's an active thread."""
        return self._worker_thread is not None and self._worker_thread.isRunning()

    def shutdown(self):
        """Shutdown current thread."""
        if self._worker_thread is None:
            self.worker_resources_released.emit()
            return

        self.shutdown_requested.emit()

    # --- Properties ---
    @property
    def playback_status(self) -> PlaybackStatus | None:
        if self._worker is None:
            return None

        return self._worker.playback_status
