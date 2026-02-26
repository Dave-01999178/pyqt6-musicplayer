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
from pyqt6_music_player.models import AudioPCM

logger = logging.getLogger(__name__)


# ================================================================================
# AUDIO PLAYER WORKER
# ================================================================================
#
# noinspection PyUnresolvedReferences
class AudioPlayerWorker(QObject):
    """Handles low-level audio playback operations in a separate thread.

    Manages PyAudio stream lifecycle, audio buffer processing, and playback state.
    Must run in a worker thread, not the main thread.

    """
    audio_loaded = pyqtSignal()
    playback_started = pyqtSignal()
    playback_finished = pyqtSignal()
    byte_position_changed = pyqtSignal(float)
    status_changed = pyqtSignal(PlaybackStatus)
    resources_released = pyqtSignal()

    def __init__(self) -> None:
        """Initialize AudioPlayerWorker."""
        super().__init__()
        # Playback data
        self._audio_pcm: AudioPCM | None = None
        self._audio_bytes: bytes | None = None  # Actual audio bytes for playback
        self._silence_bytes: bytes | None = None  # Silence bytes for 'pause' playback

        # Buffer config
        self._frames_per_buffer: int = 1024
        self._bytes_per_frame: int = 0
        self._bytes_per_buffer: int = 0

        # Playback state
        self._byte_position: int = 0
        self._status: PlaybackStatus = PlaybackStatus.IDLE

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
        self._ensure_thread()

        # PyAudio streams are session-specific and hold native audio resources.
        # They cannot be reused safely across different tracks, so we close the
        # previous stream before creating a new one.
        self._release_stream()

        self._byte_position = 0  # Reset playback position
        self._audio_pcm = audio_pcm

        self.audio_loaded.emit()

    @pyqtSlot()
    def start_playback(self) -> None:
        """Initialize PyAudio, prepare audio bytes and begin audio playback."""
        try:
            self._ensure_thread()
            self._prepare_audio_bytes()
            self._initialize_pyaudio()
            self._stream.start_stream()

        except Exception as e:
            logger.error("Failed to start playback. %s", e)

            self._set_status(PlaybackStatus.ERROR)

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
        """Seek to a specific position.

        Pauses playback if currently playing and snaps to the nearest
        frame boundary to prevent audio artifacts.

        Args:
            new_position_in_ms: Target position in milliseconds.

        """
        if self._status is PlaybackStatus.PLAYING:
            self._set_status(PlaybackStatus.PAUSED, notify=False)

        # Convert milliseconds to byte position
        bytes_per_second = self._audio_pcm.sample_rate * self._bytes_per_frame
        byte_pos = int((new_position_in_ms / 1000) * bytes_per_second)

        # Snap to the nearest frame boundary to avoid mid-frame reads
        # that causes static noise.
        byte_pos -= byte_pos % self._bytes_per_frame

        self._set_byte_position(byte_pos)

    @pyqtSlot()
    def release_resources(self) -> None:
        """Release PyAudio stream and instance, freeing audio resources."""
        self._ensure_thread()
        self._release_stream()
        self._release_pyaudio()

        self.resources_released.emit()

        logger.info("Worker resources released.")

    # --- Protected/internal methods ---
    def _ensure_thread(self) -> None:
        main_thread = QApplication.instance().thread()
        worker_thread = QThread.currentThread()

        if worker_thread == main_thread:
            raise RuntimeError(
                f"{self.__class__.__name__} must be called from a worker thread.",
            )

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

    def _prepare_audio_bytes(self) -> None:
        # Pre-process buffer sizes and audio bytes for audio callback use.
        if self._audio_pcm is None:
            return

        samples = self._audio_pcm.samples
        dtype = self._audio_pcm.orig_dtype
        scale = self._audio_pcm.orig_scale

        # Convert samples back to integers
        if np.issubdtype(dtype, np.unsignedinteger):
            # Unsigned integers: samples ∈ {0, 2 * scale - 1}
            samples_int = np.clip(
                np.round(samples * scale + scale),
                0,
                2 * scale - 1,
            ).astype(dtype)
        else:
            # Signed integers: samples ∈ {-scale, scale}
            samples_int = np.clip(
                np.round(samples * scale),
                -scale,
                scale,
            ).astype(dtype)

        # Ensure that the PCM array is contiguous
        samples_int = np.ascontiguousarray(samples_int)

        # Convert samples integer to bytes and pre-compute the buffer sizes in bytes
        self._audio_bytes = samples_int.tobytes()
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
        # Callback for playing audio bytes, used by PyAudio stream.
        if self._audio_pcm is None or self._audio_bytes is None:
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

    @pyqtSlot(int)
    def _set_byte_position(self, byte_position) -> None:
        # Set and emit new byte position.
        if self._byte_position == byte_position:
            return

        self._byte_position = byte_position

        self._on_byte_position_changed(self._byte_position)

    def _set_status(self, status: PlaybackStatus, notify=True) -> None:
        if self._status == status:
            return

        # Set and emit new playback status.
        self._status = status

        if notify:
            self.status_changed.emit(self._status)

    def _release_stream(self) -> None:
        if self._stream is None:
            return

        # Stop the current PyAudio stream callback before releasing it.
        if self._status in {PlaybackStatus.PLAYING, PlaybackStatus.PAUSED}:
            self._set_status(PlaybackStatus.STOPPED)

            logger.info("Playback stopped.")

        try:
            # Ensure that the stream is not active before closing it for safe release.
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
        """Release PyAudio instance."""
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
        """Emit playback started signal to external observers."""
        self._set_status(PlaybackStatus.PLAYING)

        self.playback_started.emit()

        logger.info("Playback started.")

    @pyqtSlot()
    def _on_playback_finished(self) -> None:
        """Release stream and emit completion signal when playback ends."""
        self.playback_finished.emit()

        self._set_status(PlaybackStatus.STOPPED)

        logger.info("Playback finished.")

    def _on_byte_position_changed(self, byte_pos: int) -> None:
        # Convert and emit byte position in seconds
        bytes_per_second = self._audio_pcm.sample_rate * self._bytes_per_frame

        byte_pos_as_sec = byte_pos / bytes_per_second

        self.byte_position_changed.emit(byte_pos_as_sec)
