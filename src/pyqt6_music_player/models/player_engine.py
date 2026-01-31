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
from pyqt6_music_player.models import TrackAudio

logger = logging.getLogger(__name__)


# ================================================================================
# PLAYER ENGINE
# ================================================================================
#
# ---------- Audio player worker ----------
class AudioPlayerWorker(QObject):
    playback_started = pyqtSignal()
    frame_position_changed = pyqtSignal(float, float)
    playback_state_changed = pyqtSignal(PlaybackState)
    playback_ended = pyqtSignal()
    playback_error = pyqtSignal()
    resources_released = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        # Playback data
        self._audio_data: TrackAudio | None = None
        self._audio_bytes: bytes | None = None  # Audio bytes for actual playback.
        self._silence_bytes: bytes | None = None  # Silence bytes for 'pause' playback.

        # Playback info/state
        self._frames_per_buffer: int = 1024  # Buffer size.
        self._bytes_per_frame: int = 0   # Total bytes per frame.
        self._bytes_per_buffer: int = 0  # Total bytes per buffer.
        self._frame_position: int = 0  # Current frame position
        self._playback_state: PlaybackState = PlaybackState.STOPPED

        # PyAudio objects
        self._pa: PyAudio | None = None
        self._stream: PyAudio.Stream | None = None

        # Thread lock
        self._lock: threading.Lock = threading.Lock()

    # --- Private methods ---
    def _set_playback_state(self, new_playback_state: PlaybackState) -> None:
        """Set a new playback state based on the given state.

        Notifies the AudioPlayerInterface of playback state changes.

        Args:
            new_playback_state: The new playback state.

        """
        with self._lock:
            self._playback_state = new_playback_state

        self.playback_state_changed.emit(self._playback_state)

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
            in_data,
            frame_count,
            time_info,
            status_flags,
    ) -> tuple[bytes | None, int]:
        # Simple validation.
        if self._audio_data is None or self._audio_bytes is None:
            return None, paComplete

        curr_state = self._playback_state
        total_frames = len(self._audio_bytes)

        # Stopped
        if curr_state is PlaybackState.STOPPED:
            QMetaObject.invokeMethod(
                self,
                "_on_playback_ended",
                Qt.ConnectionType.QueuedConnection
            )
            return None, paComplete

        # Paused
        if curr_state is PlaybackState.PAUSED:
            return self._silence_bytes, paContinue

        # Do the actual playback
        start = self._frame_position
        end = start + self._bytes_per_buffer
        frame_chunk = self._audio_bytes[start:end]  # Or buffer.
        curr_chunk_size = len(frame_chunk)

        # If left over chunk at the end, pad with silence then feed
        # (PyAudio.Stream expects an exact buffer size).
        if curr_chunk_size < frame_count:
            frame_chunk += self._silence_bytes[:frame_count - curr_chunk_size]

        self._frame_position = min(end, total_frames)  # Update frame position.

        frame_position = self._frame_position
        frame_remaining = total_frames - self._frame_position

        QMetaObject.invokeMethod(
            self,
            "_on_frame_position_changed",
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(int, frame_position),
            Q_ARG(int, frame_remaining),
        )

        # If all frames are played, end the callback.
        if self._frame_position >= total_frames:
            QMetaObject.invokeMethod(
                self,
                "_on_playback_ended",
                Qt.ConnectionType.QueuedConnection,
            )
            return None, paComplete

        return frame_chunk, paContinue

    def _release_stream(self) -> None:
        """Release the PyAudio.Stream resource

        Stops the current stream instance if it's active before releasing.
        """
        # Ensure that the stream is not running before closing, and releasing.
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
        """Release the PyAudio resource.

        Terminates the current PyAudio instance before releasing.
        """
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
    @pyqtSlot(TrackAudio)
    def load_audio_data(self, audio_data: TrackAudio) -> None:
        """Load the given audio data.

        Args:
            audio_data: The audio data to load.

        """
        if not isinstance(audio_data, TrackAudio):
            return

        if self._playback_state is not PlaybackState.STOPPED:
            self._set_playback_state(PlaybackState.STOPPED)

        self._release_stream()  # Release stream before loading the audio data.

        self._frame_position = 0  # Reset frame position.
        self._audio_data = audio_data

    @pyqtSlot()
    def start_playback(self):
        """Load and start PyAudio."""
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

            self.playback_error.emit()
            self._set_playback_state(PlaybackState.STOPPED)

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
        """Release worker PyAudio resources."""
        logger.info("Releasing worker resources...")

        # Release PyAudio.Stream.
        self._release_stream()

        # Release PyAudio.
        self._release_pyaudio()

        # Notify
        self.resources_released.emit()

        logger.info("Worker resources released.")

    @pyqtSlot()
    def _on_playback_ended(self) -> None:
        self._release_stream()

        self.playback_ended.emit()

    @pyqtSlot(int, int)
    def _on_frame_position_changed(self, frame_pos, frames_remaining) -> None:
        sample_rate = self._audio_data.sample_rate
        elapsed_time = frame_pos / (sample_rate * self._bytes_per_frame)
        time_remaining = frames_remaining / (sample_rate * self._bytes_per_frame)

        self.frame_position_changed.emit(elapsed_time, time_remaining)

    # --- Properties ---
    @property
    def playback_state(self) -> PlaybackState:
        return self._playback_state


# ---------- Audio player service ----------
# noinspection PyUnresolvedReferences
class AudioPlayerService(QObject):
    playback_started = pyqtSignal()
    frame_position_changed = pyqtSignal(float, float)
    playback_state_changed = pyqtSignal(PlaybackState)
    playback_ended = pyqtSignal()
    worker_resources_released = pyqtSignal()

    load_audio_requested = pyqtSignal(TrackAudio)
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
        self.load_audio_requested.connect(self._worker.load_audio_data)
        self.start_playback_requested.connect(self._worker.start_playback)
        self.pause_playback_requested.connect(self._worker.pause)
        self.resume_playback_requested.connect(self._worker.resume)
        self.shutdown_requested.connect(self._worker.release_resources)

        # Establish Worker -> Service connection.
        self._worker.playback_started.connect(self._on_playback_start)
        self._worker.frame_position_changed.connect(self._on_position_change)
        self._worker.playback_state_changed.connect(
            self._on_worker_playback_state_changed
        )
        self._worker.playback_ended.connect(self._on_playback_finished)
        self._worker.resources_released.connect(self._worker_thread.quit)

        self._worker_thread.finished.connect(self._on_thread_finished)

        # Start thread.
        self._worker_thread.start()

    # --- Public methods ---
    def load_audio(self, audio_data: TrackAudio):
        self._init_thread_and_worker()

        self.load_audio_requested.emit(audio_data)

    def start_playback(self):
        self.start_playback_requested.emit()

    def resume_playback(self):
        self.resume_playback_requested.emit()

    def pause_playback(self):
        self.pause_playback_requested.emit()

    def is_running(self) -> bool:
        return self._worker_thread is not None and self._worker_thread.isRunning()

    def shutdown(self):
        if self._worker_thread is None:
            self.worker_resources_released.emit()
            return

        self._worker_thread.requestInterruption()

        self.shutdown_requested.emit()

    # --- Slots ---
    @pyqtSlot()
    def _on_playback_start(self):
        self.playback_started.emit()

    @pyqtSlot(float, float)
    def _on_position_change(self, new_position: float, remainder: float):
        self.frame_position_changed.emit(new_position, remainder)

    @pyqtSlot(PlaybackState)
    def _on_worker_playback_state_changed(self) -> None:
        self.playback_state_changed.emit(self.playback_state)

    @pyqtSlot()
    def _on_playback_finished(self):
        self.playback_ended.emit()

    @pyqtSlot()
    def _on_thread_finished(self):
        self._worker.deleteLater()
        self._worker = None

        self._worker_thread.deleteLater()
        self._worker_thread = None

        self.worker_resources_released.emit()

        logger.info("Worker and thread deleted.")

    # --- Properties ---
    @property
    def playback_state(self) -> PlaybackState | None:
        if self._worker is None:
            return None

        return self._worker.playback_state
