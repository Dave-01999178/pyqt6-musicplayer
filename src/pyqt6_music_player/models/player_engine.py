import logging
import threading
from enum import Enum, auto

import numpy as np
from pyaudio import PyAudio, paComplete, paContinue
from PyQt6.QtCore import QObject, QThread, QTimer, pyqtSignal, pyqtSlot, QMetaObject, Qt, Q_ARG

from pyqt6_music_player.constants import CHUNK_SIZE
from pyqt6_music_player.models import AudioSamples


class PlaybackState(Enum):
    PLAYING = auto()
    PAUSED = auto()
    STOPPED = auto()  # For interrupting playback e.g. next/prev track.


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
    playback_stopped = pyqtSignal()
    playback_error = pyqtSignal()

    def __init__(self):
        super().__init__()
        # Playback data
        self._audio_data: AudioSamples | None = None

        # Playback info/state
        self._frame_position = 0
        self._state = PlaybackState.STOPPED

        # PyAudio objects
        self._pa = None
        self._stream = None

        self._lock = threading.Lock()

    # --- Private methods ---
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
        # Pause playback by feeding silence when state is set to PlaybackState.PAUSED.
        # Temporary solution until we find a way to pause the separate thread
        # that runs PyAudio stream callback.
        with self._lock:
            if self._state is PlaybackState.STOPPED:
                return None, paComplete

            if self._state is PlaybackState.PAUSED:
                dtype_to_use = self._audio_data.orig_dtype
                silence = np.zeros(
                    (frame_count, self._audio_data.channels),
                    dtype=dtype_to_use
                )

                return self._float_to_bytes(silence), paContinue

        total_frames = len(self._audio_data.samples)

        # End playback if all frames are played.
        if self._frame_position >= total_frames:
            QMetaObject.invokeMethod(
                self,
                "_playback_finished",
                Qt.ConnectionType.QueuedConnection,
            )
            return None, paComplete

        end = min(self._frame_position + frame_count, total_frames)
        frame_chunk = self._audio_data.samples[self._frame_position:end]
        current_chunk_size = len(frame_chunk)

        # If the current chunk is less-than the required frame count (left-over frames at the end),
        # pad it with silence because PyAudio expects a fixed chunk size.
        if current_chunk_size < frame_count:
            dtype_to_use = self._audio_data.orig_dtype
            shape_ = (frame_count - current_chunk_size, self._audio_data.channels)
            silence_padding  = np.zeros(shape_, dtype=dtype_to_use)
            frame_chunk = np.concatenate((frame_chunk, silence_padding))

        self._frame_position = end  # Update frame index/position.

        new_position = self._frame_position / self._audio_data.sample_rate
        frames_remaining = (total_frames - self._frame_position) / self._audio_data.sample_rate

        QMetaObject.invokeMethod(
            self,
            "_position_changed",
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(float, new_position),
            Q_ARG(float, frames_remaining),
        )

        return self._float_to_bytes(frame_chunk), paContinue

    def _cleanup_stream(self):
        # Set state to 'STOPPED' to end PyAudio callback.
        with self._lock:
            if self._state is not PlaybackState.STOPPED:
                self._state = PlaybackState.STOPPED

        # Cleanup stream.
        if self._stream is not None:
            try:
                if self._stream.is_active():
                    self._stream.stop_stream()
                self._stream.close()

                print("PyAudio stream resources released.")

            except Exception as e:
                logging.warning("Error closing stream: %s\n", e)
            finally:
                self._stream = None

    # --- Slots ---
    @pyqtSlot(AudioSamples)
    def load_audio_data(self, audio_data: AudioSamples):
        if not isinstance(audio_data, AudioSamples):
            return

        with self._lock:
            if self._state is not PlaybackState.STOPPED:
                self._state = PlaybackState.STOPPED

        self._audio_data = audio_data
        self._frame_position = 0

        self._cleanup_stream()

    @pyqtSlot()
    def start_playback(self):
        if self._pa is None:
            self._pa = PyAudio()

        self._stream = self._pa.open(
            rate=self._audio_data.sample_rate,
            channels=self._audio_data.channels,
            format=self._pa.get_format_from_width(self._audio_data.sample_width),
            output=True,
            frames_per_buffer=CHUNK_SIZE,
            stream_callback=self._audio_callback
        )

        try:
            print("Starting playback...")
            self._stream.start_stream()

            self._state = PlaybackState.PLAYING

            self.playback_started.emit()

        except Exception as e:
            logging.error("Failed to start playback, error: %s.\n", e)

            self._state = PlaybackState.STOPPED

        print("Playback started.\n")

    @pyqtSlot()
    def pause(self):
        print("Pausing...")
        with self._lock:
            self._state = PlaybackState.PAUSED
        print("Paused.\n")

    @pyqtSlot()
    def resume(self):
        print("Unpausing...")
        with self._lock:
            self._state = PlaybackState.PLAYING
        print("Unpaused.\n")

    @pyqtSlot()
    def cleanup(self):
        print("Cleaning up worker resources...\n")

        # Cleanup stream.
        self._cleanup_stream()

        # Cleanup PyAudio.
        if self._pa is not None:
            try:
                self._pa.terminate()
            except Exception as e:
                logging.warning("Error terminating PyAudio: %s\n", e)
            finally:
                self._pa = None

        print("Worker resources released.")

    @pyqtSlot()
    def _playback_finished(self):
        self.playback_finished.emit()

    @pyqtSlot(float, float)
    def _position_changed(self, frame_pos, frames_remaining):
        self.position_changed.emit(frame_pos, frames_remaining)

    # --- Properties ---
    @property
    def is_playing(self) -> bool:
        return self._state is PlaybackState.PLAYING

    @property
    def is_paused(self) -> bool:
        return self._state is PlaybackState.PAUSED


# ---------- Audio player controller ----------
# noinspection PyUnresolvedReferences
class AudioPlayerController(QObject):
    playback_started = pyqtSignal()
    position_changed = pyqtSignal(float, float)
    playback_finished = pyqtSignal()
    shutdown_finished = pyqtSignal()

    set_audio_data_requested = pyqtSignal(AudioSamples)
    start_playback_requested = pyqtSignal()
    pause_playback_requested = pyqtSignal()
    resume_playback_requested = pyqtSignal()
    shutdown_request = pyqtSignal()

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

        # Establish Controller -> Worker connection.
        self.set_audio_data_requested.connect(self._worker.load_audio_data)
        self.start_playback_requested.connect(self._worker.start_playback)
        self.pause_playback_requested.connect(self._worker.pause)
        self.resume_playback_requested.connect(self._worker.resume)

        # Establish Worker -> Controller connection.
        self._worker.playback_started.connect(self._on_playback_start)
        self._worker.position_changed.connect(self._on_position_change)

        self._worker.playback_finished.connect(self._worker.cleanup)
        # self.shutdown_request.connect(self._worker_thread.quit)

        # Start thread.
        self._worker_thread.start()

    # --- Public methods ---
    def start_playback(self, audio_data: AudioSamples):
        self._init_thread_and_worker()
        self.set_audio_data_requested.emit(audio_data)
        self.start_playback_requested.emit()

    def resume_playback(self):
        self.resume_playback_requested.emit()

    def pause_playback(self):
        self.pause_playback_requested.emit()

    def shutdown(self):
        if self._worker_thread is None:
            self.shutdown_finished.emit()
            return

        self.shutdown_request.emit()

        # self._worker_thread.wait()

        # print("Worker and thread deleted.")

    # --- Slots ---
    @pyqtSlot()
    def _on_playback_start(self):
        self.playback_started.emit()

    @pyqtSlot(float, float)
    def _on_position_change(self, new_position: float, remainder: float):
        self.position_changed.emit(new_position, remainder)

    @pyqtSlot()
    def _on_playback_finished(self):
        self.playback_finished.emit()

    def _on_thread_finished(self):
        self._worker.deleteLater()
        self._worker = None

        self._worker_thread.deleteLater()
        self._worker_thread = None

        self.shutdown_finished.emit()

        print("Worker and thread deleted.")

    # --- Properties ---
    @property
    def is_playing(self) -> bool:
        if self._worker is None:
            return False

        return self._worker.is_playing

    @property
    def is_paused(self) -> bool:
        if self._worker is None:
            return False

        return self._worker.is_paused
