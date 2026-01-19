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

from pyqt6_music_player.constants import PlaybackState
from pyqt6_music_player.models import AudioData

logger = logging.getLogger(__name__)


# ================================================================================
# PLAYER ENGINE
# ================================================================================
#
# ---------- Audio player worker ----------
class AudioPlayerWorker(QObject):
    audio_data_loaded = pyqtSignal()
    playback_started = pyqtSignal()
    position_changed = pyqtSignal(float, float)
    playback_state_changed = pyqtSignal(PlaybackState)
    playback_finished = pyqtSignal()
    playback_error = pyqtSignal()
    resources_released = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        # Playback data
        self._audio_data: AudioData | None = None
        self._audio_bytes: bytes | None = None  # Audio bytes for actual playback.
        self._silence_bytes: bytes | None = None  # Silence bytes for 'pause' playback.

        # Playback info/state
        self._frames_per_buffer: int = 1024  # Buffer size.
        self._bytes_per_frame: int = 0   # Total bytes per frame.
        self._bytes_per_buffer: int = 0  # Total bytes per buffer.
        self._byte_position: int = 0  # Current position
        self._playback_state: PlaybackState = PlaybackState.STOPPED

        # PyAudio objects
        self._pa: PyAudio | None = None
        self._stream: PyAudio.Stream | None = None

        # Thread lock
        self._lock: threading.Lock = threading.Lock()

    # --- Private methods ---
    def _set_playback_state(self, new_playback_state: PlaybackState) -> None:
        with self._lock:
            self._playback_state = new_playback_state

        self.playback_state_changed.emit(self._playback_state)

    def _prepare_audio_bytes(self) -> None:
        samples = self._audio_data.samples
        sample_width = self._audio_data.sample_width
        dtype = self._audio_data.orig_dtype
        dtype_max = self._audio_data.orig_dtype_max

        # Convert float PCM back to its original dtype (np.integer).
        if sample_width == 1:
            samples_int = ((samples * dtype_max) + dtype_max).astype(dtype)
        else:
            samples_int = (samples * dtype_max).astype(dtype)

        # Ensure that the PCM is contiguous.
        samples_int = np.ascontiguousarray(samples_int)

        # Convert PCM (np.integer) to bytes.
        self._audio_bytes = samples_int.tobytes()

        # Precompute sizes.
        self._bytes_per_frame = samples_int.strides[0]
        self._bytes_per_buffer = self._frames_per_buffer * self._bytes_per_frame

        # Create 'silence' array for pause.
        self._silence_bytes = b"\x00" * self._bytes_per_buffer

    def _audio_callback(
            self,
            in_data,
            frame_count,
            time_info,
            status_flags,
    ) -> tuple[bytes | None, int]:
        # Validation.
        if self._audio_data is None or self._audio_bytes is None:
            return None, paComplete

        curr_state = self._playback_state
        total_frames = len(self._audio_bytes)

        # If stopped, end callback.
        if curr_state is PlaybackState.STOPPED:
            QMetaObject.invokeMethod(
                self,
                "_playback_finished",
                Qt.ConnectionType.QueuedConnection
            )
            return None, paComplete

        # If paused, feed silence.
        if curr_state is PlaybackState.PAUSED:
            return self._silence_bytes, paContinue

        # Do the actual playback.
        start = self._byte_position
        end = start + self._bytes_per_buffer
        frame_chunk = self._audio_bytes[start:end]
        curr_chunk_size = len(frame_chunk)

        # If left over chunk at the end, pad with silence then feed.
        if curr_chunk_size < frame_count:
            frame_chunk += self._silence_bytes[:frame_count - curr_chunk_size]

        self._byte_position = min(end, total_frames)  # Update position.

        frame_position = self._byte_position
        frame_remaining = total_frames - self._byte_position

        QMetaObject.invokeMethod(
            self,
            "_frame_position_changed",
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(int, frame_position),
            Q_ARG(int, frame_remaining),
        )

        # If all frames are played, end callback.
        if self._byte_position >= total_frames:
            QMetaObject.invokeMethod(
                self,
                "_playback_finished",
                Qt.ConnectionType.QueuedConnection,
            )
            return None, paComplete

        return frame_chunk, paContinue

    def _release_stream(self) -> None:
        """Stop the current PyAudio.Stream instance before releasing."""
        # Ensure that the stream is stopped before closing and releasing.
        if self._playback_state is not PlaybackState.STOPPED:
            self._set_playback_state(PlaybackState.STOPPED)

        if self._stream is not None:
            try:
                # Ensure that the stream is not active before closing.
                if self._stream.is_active():
                    self._stream.stop_stream()

                self._stream.close()  # Close PyAudio.Stream.
                logger.info("Stream successfully released.")

            except Exception as e:
                logger.warning(
                    "Force releasing stream due to an error: %s\n",
                    e,
                )

            finally:
                self._stream = None  # Release PyAudio.Stream instance.

    def _release_pyaudio(self) -> None:
        """Terminate the current PyAudio instance before releasing."""
        if self._pa is not None:
            try:
                self._pa.terminate()
                logger.info("PyAudio successfully released.")

            except Exception as e:
                logger.warning(
                    "Force releasing PyAudio due to an error: %s\n",
                    e,
                )
            finally:
                self._pa = None  # Release PyAudio instance.

    # --- Slots ---
    @pyqtSlot(AudioData)
    def load_audio_data(self, audio_data: AudioData) -> None:
        if not isinstance(audio_data, AudioData):
            return

        with self._lock:
            if self._playback_state is not PlaybackState.STOPPED:
                self._playback_state = PlaybackState.STOPPED

        self._release_pyaudio()

        self._audio_data = audio_data
        self._byte_position = 0  # Reset frame position.

        self.audio_data_loaded.emit()

    @pyqtSlot()
    def start_playback(self):
        if self._pa is None:
            self._pa = PyAudio()

        self._stream = self._pa.open(
            rate=self._audio_data.sample_rate,
            channels=self._audio_data.channels,
            format=self._pa.get_format_from_width(self._audio_data.sample_width),
            output=True,
            frames_per_buffer=self._frames_per_buffer,
            stream_callback=self._audio_callback,
        )

        try:
            self._prepare_audio_bytes()

            logger.info("Starting playback...")
            self._set_playback_state(PlaybackState.PLAYING)
            self._stream.start_stream()
            self.playback_started.emit()
            logger.info("Playback started.")

        except Exception as e:
            logger.error("Failed to start playback, error: %s.\n", e)

            with self._lock:
                self._playback_state = PlaybackState.STOPPED

    @pyqtSlot()
    def pause(self) -> None:
        self._set_playback_state(PlaybackState.PAUSED)

        logger.info("Playback paused.\n")

    @pyqtSlot()
    def resume(self) -> None:
        self._set_playback_state(PlaybackState.PLAYING)

        logger.info("Playback unpaused.\n")

    @pyqtSlot()
    def release_resources(self) -> None:
        """Release instance's PyAudio resources."""
        logger.info("Releasing worker resources...")

        # Release PyAudio.Stream.
        self._release_stream()

        # Release PyAudio.
        self._release_pyaudio()

        self.resources_released.emit()

        logger.info("Worker resources released.")

    @pyqtSlot()
    def _playback_finished(self) -> None:
        self._release_stream()

        self.playback_finished.emit()

    @pyqtSlot()
    def _playback_stopped(self) -> None:
        self._release_stream()

    @pyqtSlot(int, int)
    def _frame_position_changed(self, frame_pos, frames_remaining) -> None:
        sample_rate = self._audio_data.sample_rate
        elapsed_time = frame_pos / (sample_rate * self._bytes_per_frame)
        time_remaining = frames_remaining / (sample_rate * self._bytes_per_frame)

        self.position_changed.emit(elapsed_time, time_remaining)

    # --- Properties ---
    @property
    def playback_state(self) -> PlaybackState:
        return self._playback_state


# ---------- Audio player service ----------
# noinspection PyUnresolvedReferences
class AudioPlayerService(QObject):
    audio_data_loaded = pyqtSignal()
    playback_started = pyqtSignal()
    position_changed = pyqtSignal(float, float)
    player_playback_state_changed = pyqtSignal(PlaybackState)
    playback_finished = pyqtSignal()
    shutdown_finished = pyqtSignal()

    set_audio_data_requested = pyqtSignal(AudioData)
    start_playback_requested = pyqtSignal()
    pause_playback_requested = pyqtSignal()
    resume_playback_requested = pyqtSignal()
    shutdown_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._worker_thread = None
        self._worker = None

    def _init_thread_and_worker(self):
        if self._worker_thread is not None:
            return

        # Create thread and worker.
        self._worker_thread = QThread()
        self._worker = AudioPlayerWorker()

        # Move worker to thread.
        self._worker.moveToThread(self._worker_thread)

        # Establish Service -> Worker connection.
        self.set_audio_data_requested.connect(self._worker.load_audio_data)
        self.start_playback_requested.connect(self._worker.start_playback)
        self.pause_playback_requested.connect(self._worker.pause)
        self.resume_playback_requested.connect(self._worker.resume)
        self.shutdown_requested.connect(self._worker.release_resources)

        # Establish Worker -> Service connection.
        self._worker.audio_data_loaded.connect(self._on_audio_data_load)
        self._worker.playback_started.connect(self._on_playback_start)
        self._worker.position_changed.connect(self._on_position_change)
        self._worker.playback_state_changed.connect(
            self._on_worker_playback_state_changed
        )
        self._worker.playback_finished.connect(self._on_playback_finished)
        self._worker.resources_released.connect(self._worker_thread.quit)

        self._worker_thread.finished.connect(self._on_thread_finished)

        # Start thread.
        self._worker_thread.start()

    # --- Public methods ---
    def load_audio(self, audio_data: AudioData):
        self._init_thread_and_worker()

        self.set_audio_data_requested.emit(audio_data)

    def start_playback(self):
        self.start_playback_requested.emit()

    def resume_playback(self):
        self.resume_playback_requested.emit()

    def pause_playback(self):
        self.pause_playback_requested.emit()

    def shutdown(self):
        if self._worker_thread is None:
            self.shutdown_finished.emit()
            return

        self._worker_thread.requestInterruption()

        self.shutdown_requested.emit()

    # --- Slots ---
    @pyqtSlot()
    def _on_audio_data_load(self):
        self.audio_data_loaded.emit()

    @pyqtSlot()
    def _on_playback_start(self):
        self.playback_started.emit()

    @pyqtSlot(float, float)
    def _on_position_change(self, new_position: float, remainder: float):
        self.position_changed.emit(new_position, remainder)

    @pyqtSlot(PlaybackState)
    def _on_worker_playback_state_changed(
            self,
    ) -> None:
        self.player_playback_state_changed.emit(self.playback_state)

    @pyqtSlot()
    def _on_playback_finished(self):
        self.playback_finished.emit()

    @pyqtSlot()
    def _on_thread_finished(self):
        self._worker.deleteLater()
        self._worker = None

        self._worker_thread.deleteLater()
        self._worker_thread = None

        self.shutdown_finished.emit()

        logger.info("Worker and thread deleted.")

    # --- Properties ---
    @property
    def playback_state(self) -> PlaybackState | None:
        if self._worker is None:
            return None

        return self._worker.playback_state
