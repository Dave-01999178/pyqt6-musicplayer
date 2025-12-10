import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Self, Any

import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
from numpy.typing import NDArray
from pyaudio import PyAudio
from pydub import AudioSegment

from pyqt6_music_player.constants import SUPPORTED_BYTES


# ================================================================================
# AUDIO DECODING AND DATA PREPARATION
# ================================================================================
@dataclass(frozen=True)
class AudioData:
    channels: int
    frame_rate: int
    sample_width: int
    normalized_samples: NDArray[np.float32]

    @classmethod
    def from_file(cls, file: str | Path) -> Self | None:
        # --- Load and decode file. ---
        try:
            audio_segment = AudioSegment.from_file(file)
        except Exception as e:
            logging.error("Failed to decode file: %s, %s.", file, e)
            return None

        sample_width = audio_segment.sample_width
        if sample_width not in SUPPORTED_BYTES:
            logging.error("Invalid/Unsupported sample width: %d", sample_width)
            return None

        # Omitted 24-bit audio (sample_width == 3) because pydub automatically converts
        # 24-bit to 32-bit.
        byte_to_dtype_map: dict[int, type[np.integer[Any]]] = {
            1: np.uint8,
            2: np.int16,
            4: np.int32
        }
        orig_dtype = byte_to_dtype_map[sample_width]

        # --- Parse raw data from AudioSegment. ---
        samples = np.frombuffer(
            buffer=audio_segment.raw_data,
            dtype=orig_dtype
        ).astype(np.float32)

        # --- Normalize samples to [-1.0, 1.0]. ---
        if sample_width == 1:
            samples_normalized = (samples - 128.0) / 128.0
        else:
            # For 16-bit (i2) and 32-bit (i4) signed integers.
            # Use the maximum positive value (M_pos) for division.
            # max_value = 32767.0 for 16-bit, 2147483647.0 for 32-bit.
            max_value = float(np.iinfo(orig_dtype).max)
            samples_normalized = samples / max_value

        # --- Reshape samples array: (frames, channels). ---
        # '-1' is a numpy trick to automatically calculate that dimension size (rows in this case).
        samples_normalized = samples_normalized.reshape(-1, audio_segment.channels)

        return cls(
            channels=audio_segment.channels,
            frame_rate=audio_segment.frame_rate,
            sample_width=audio_segment.sample_width,
            normalized_samples=samples_normalized
        )


# ================================================================================
# PLAYER ENGINE
# ================================================================================
# TODO: Initial implementation (play only), refactor and extend later to include pause, repeat,
#  seeking, and volume.
class PlayerWorker(QObject):
    playback_finished = pyqtSignal(bool)
    playback_error = pyqtSignal()
    def __init__(self, audio_data: AudioData):
        super().__init__()
        self._audio_data = audio_data
        self._chunk_ms = 50
        self._chunk_frames = int(self._audio_data.frame_rate * self._chunk_ms / 1000)

        self._is_playing = False
        self._frame_position = 0

        self._pa: PyAudio | None = None
        self._stream: PyAudio.Stream | None = None

    def _playback_loop(self):
        self._is_playing = True

        samples_len = len(self._audio_data.normalized_samples)
        while self._is_playing and self._frame_position < samples_len:
            end = min(self._frame_position + self._chunk_frames, samples_len)
            chunk = self._audio_data.normalized_samples[self._frame_position:end]
            data = self._float_to_bytes(chunk)

            if data:
                self._stream.write(data)
                self._frame_position = end

            if end == samples_len:
                print("Finished playing.")
                self._is_playing = False
                self.playback_finished.emit(True)


    def _float_to_bytes(self, chunk_float: NDArray[np.float32]):
        chunk_float = np.clip(chunk_float, -1.0, 1.0)
        samples_width = self._audio_data.sample_width

        if samples_width == 1:
            uint8_max = (1 << 8 - 1) - 1
            chunk_int = ((chunk_float * uint8_max) + uint8_max).astype(np.uint8)
        elif samples_width == 2:
            int16_max = (1 << 16 - 1) - 1
            chunk_int = (chunk_float * int16_max).astype(np.int16)
        elif samples_width == 4:
            int32_max = (1 << 32 - 1) - 1
            chunk_int = (chunk_float * int32_max).astype(np.int32)
        else:
            raise ValueError(f"Unsupported sample width: {samples_width}")

        return chunk_int.tobytes()

    @pyqtSlot()
    def start_playback(self):
        self._pa = PyAudio()
        self._stream = self._pa.open(
            rate=self._audio_data.frame_rate,
            channels=self._audio_data.channels,
            format=self._pa.get_format_from_width(self._audio_data.sample_width),
            output=True,
            frames_per_buffer=self._chunk_ms,
        )

        try:
            self._playback_loop()
        except Exception as e:
            self.playback_error.emit()
            print(e)  # TODO: Replace with logging

    def cleanup(self):
        if self._is_playing:
            self._is_playing = False

        if self._stream is not None:
            try:
                self._stream.stop_stream()
                self._stream.close()
            except Exception as e:
                logging.warning(f"Error closing stream: {e}")
            finally:
                self._stream = None

        if self._pa is not None:
            try:
                self._pa.terminate()
            except Exception as e:
                logging.warning(f"Error terminating PyAudio: {e}")
            finally:
                self._pa = None

        self.playback_finished.emit(True)


class PlayerEngine(QObject):
    def __init__(self):
        super().__init__()
        self._audio_data: AudioData | None = None
        self.worker_thread: QThread | None = None
        self.worker: PlayerWorker | None = None

    def load(self, audio_data: AudioData):
        self._audio_data = audio_data

    def play(self):
        if self.worker_thread is not None and self.worker_thread.isRunning():
            return

        # Create worker and thread.
        self.worker_thread = QThread()
        self.worker = PlayerWorker(self._audio_data)

        # Move worker to thread.
        self.worker.moveToThread(self.worker_thread)

        # Connect signals.
        self.worker_thread.started.connect(self.worker.start_playback)
        self.worker.playback_error.connect(self.worker_thread.quit)
        self.worker.playback_finished.connect(self.worker_thread.quit)

        # Cleanup when finished.
        self.worker_thread.finished.connect(self.worker.cleanup)
        self.worker_thread.finished.connect(self.cleanup_resources)

        # Start the thread
        self.worker_thread.start()

    def cleanup_resources(self):
        if self.worker_thread is not None:
            self.worker_thread.deleteLater()
            self.worker_thread = None

        if self.worker is not None:
            self.worker.deleteLater()
            self.worker_thread = None

        print("Finished cleaning up resources.")
