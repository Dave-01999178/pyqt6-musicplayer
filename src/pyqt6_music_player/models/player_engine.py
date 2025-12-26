import logging
import threading

import numpy as np
from pyaudio import PyAudio, paComplete, paContinue
from PyQt6.QtCore import QObject, QThread, QTimer, pyqtSignal, pyqtSlot

from pyqt6_music_player.models import AudioSamples


# ================================================================================
# PLAYER ENGINE
# ================================================================================
#
# ---------- Audio player worker ----------
# noinspection PyUnresolvedReferences
class AudioPlayerWorker(QObject):
    playback_started = pyqtSignal()
    position_changed = pyqtSignal(float, float)
    playback_finished = pyqtSignal()
    playback_error = pyqtSignal()

    def __init__(self, audio_data: AudioSamples):
        super().__init__()
        # Playback data
        self._audio_data = audio_data
        self._chunk_size = 1024

        # Playback info/state
        self._frame_position = 0
        self._paused = False
        self._running = False

        # PyAudio objects
        self._pa = None
        self._stream = None

        self._timer = None
        self._lock = threading.Lock()

    # --- Internal helper methods ---
    def _float_to_bytes(self, chunk_float):
        chunk_float = np.clip(chunk_float, -1.0, 1.0)
        samples_width = self._audio_data.sample_width
        max_value = self._audio_data.dtype_max_val
        dtype_to_use = self._audio_data.orig_dtype

        if samples_width == 1:
            samples_int = ((chunk_float * max_value) + max_value).astype(dtype_to_use)
        elif samples_width == 2:
            samples_int = (chunk_float * max_value).astype(dtype_to_use)
        elif samples_width == 4:
            samples_int = (chunk_float * max_value).astype(dtype_to_use)
        else:
            raise ValueError(f"Unsupported sample width: {samples_width}")

        return samples_int.tobytes()

    def _audio_callback(self, in_data, frame_count, time_info, status):
        # When paused (`_paused` flag is set to True), feed silence.
        # Temporary solution for now until we find a way to pause the separate thread
        # that runs PyAudio stream callback.
        with self._lock:
            if self._paused:
                dtype_to_use = self._audio_data.orig_dtype
                silence = np.zeros(
                    (frame_count, self._audio_data.channels),
                    dtype=dtype_to_use
                )

                return self._float_to_bytes(silence), paContinue

        total_frames = len(self._audio_data.samples)

        # When all frames are played, end PyAudio callback.
        if self._frame_position >= total_frames:
            self._running = False
            print("Playback finished.")

            return None, paComplete

        end = min(self._frame_position + frame_count, total_frames)
        frame_chunk = self._audio_data.samples[self._frame_position:end]
        current_chunk_size = len(frame_chunk)

        # If the current chunk is leftover (frames at the end), pad with silence
        # because PyAudio expects a fixed chunk size.
        if current_chunk_size < frame_count:
            dtype_to_use = self._audio_data.orig_dtype
            shape_ = (frame_count - current_chunk_size, self._audio_data.channels)
            silence_padding  = np.zeros(shape_, dtype=dtype_to_use)
            frame_chunk = np.concatenate((frame_chunk, silence_padding))

        self._frame_position = end  # Update frame index/position.

        new_position = self._frame_position / self._audio_data.sample_rate
        remaining = (total_frames - self._frame_position) / self._audio_data.sample_rate

        self.position_changed.emit(new_position, remaining)

        return self._float_to_bytes(frame_chunk), paContinue

    def _check_status(self):
        with self._lock:
            is_running = self._running

        if not is_running:
            self.playback_finished.emit()

    # --- Slots ---
    @pyqtSlot()
    def start_playback(self):
        self._timer = QTimer()
        self._timer.timeout.connect(self._check_status)

        self._pa = PyAudio()
        self._stream = self._pa.open(
            rate=self._audio_data.sample_rate,
            channels=self._audio_data.channels,
            format=self._pa.get_format_from_width(self._audio_data.sample_width),
            output=True,
            frames_per_buffer=self._chunk_size,
            stream_callback=self._audio_callback
        )

        try:
            print("Starting playback...")
            self._running = True

            self._stream.start_stream()
            self.playback_started.emit()
        except Exception as e:
            logging.error("Failed to start playback, error: %s.\n", e)
            self._running = False
            self.playback_error.emit()

        print("Playback started.\n")

        self._timer.start(100)

    @pyqtSlot()
    def pause(self):
        print("Pausing...")
        with self._lock:
            self._paused = True
        print("Paused.\n")

    @pyqtSlot()
    def resume(self):
        print("Unpausing...")
        with self._lock:
            self._paused = False
        print("Unpaused.\n")

    @pyqtSlot()
    def cleanup(self):
        print("Cleaning up worker resources...\n")

        # Cleanup timer.
        if self._timer is not None:
            self._timer.stop()
            self._timer = None

        # Stop the running flag to end PyAudio callback.
        with self._lock:
            self._running = False

        # Cleanup stream.
        if self._stream is not None:
            try:
                if self._stream.is_active():
                    self._stream.stop_stream()
                self._stream.close()
            except Exception as e:
                logging.warning("Error closing stream: %s\n", e)
            finally:
                self._stream = None

        # Cleanup PyAudio.
        if self._pa is not None:
            try:
                self._pa.terminate()
            except Exception as e:
                logging.warning("Error terminating PyAudio: %s\n", e)
            finally:
                self._pa = None

        print("Worker resources released.")

    # --- Properties ---
    @property
    def is_paused(self) -> bool:
        if not self._running:
            return False  # Worker cannot be in a pause state if it's not running.

        return self._paused


# ---------- Audio player controller ----------
# noinspection PyUnresolvedReferences
class AudioPlayerController(QObject):
    playback_started = pyqtSignal()
    position_changed = pyqtSignal(float, float)
    start_playback_requested = pyqtSignal(AudioSamples)
    pause_playback_requested = pyqtSignal()
    resume_playback_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._worker_thread = None
        self._worker = None

        self.start_playback_requested.connect(self.start)

    # --- Public methods ---
    def start_playback(self, audio_data: AudioSamples):
        self.start_playback_requested.emit(audio_data)

    def resume_playback(self):
        self.resume_playback_requested.emit()

    def pause_playback(self):
        self.pause_playback_requested.emit()

    # --- Slots ---
    @pyqtSlot(AudioSamples)
    def start(self, audio_data: AudioSamples):
        if self._worker_thread is not None and self._worker_thread.isRunning():
            return

        # Create thread and worker.
        self._worker_thread = QThread()
        self._worker = AudioPlayerWorker(audio_data)

        # Move worker to thread.
        self._worker.moveToThread(self._worker_thread)

        # Connect signals.
        self._worker_thread.started.connect(self._worker.start_playback)

        self._worker.playback_started.connect(self._on_playback_start)
        self._worker.position_changed.connect(self._on_position_change)

        self.pause_playback_requested.connect(self._worker.pause)
        self.resume_playback_requested.connect(self._worker.resume)

        self._worker.playback_error.connect(self._worker.cleanup)  # Cleanup on error
        self._worker.playback_finished.connect(self._worker.cleanup)  # Cleanup on finish

        # Quit thread after worker cleanup
        self._worker.playback_error.connect(self._worker_thread.quit)
        self._worker.playback_finished.connect(self._worker_thread.quit)

        # Thread cleanup.
        self._worker_thread.finished.connect(self._cleanup_thread)

        # Start thread.
        self._worker_thread.start()

    @pyqtSlot()
    def _on_playback_start(self):
        self.playback_started.emit()

    @pyqtSlot(float, float)
    def _on_position_change(self, new_position: float, remainder: float):
        self.position_changed.emit(new_position, remainder)

    @pyqtSlot()
    def _cleanup_thread(self):
        if self._worker is not None:
            self._worker.deleteLater()
            self._worker = None

        if self._worker_thread is not None:
            self._worker_thread.deleteLater()
            self._worker_thread = None

        print("Worker and thread deleted.")

    # --- Properties ---
    @property
    def is_paused(self) -> bool:
        if self._worker is None:
            return False

        return self._worker.is_paused
