import logging

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

from pyqt6_music_player.core import PlaybackState
from pyqt6_music_player.track import AudioPCM

from .audio_player_worker import AudioPlayerWorker

logger = logging.getLogger(__name__)


class AudioPlayerService(QObject):
    """Manages audio playback worker thread and coordinates signal communication.

    Acts as a thread-safe interface to the audio player worker, handling thread
    lifecycle and signal routing between the main thread and worker thread.
    """

    # AudioPlayerService signals
    play_audio_requested = pyqtSignal(AudioPCM)
    pause_playback_requested = pyqtSignal()
    resume_playback_requested = pyqtSignal()
    repeat_playback_requested = pyqtSignal()
    seek_requested = pyqtSignal(int)
    set_volume_requested = pyqtSignal(int)
    clear_playback_requested = pyqtSignal()
    shutdown_requested = pyqtSignal()

    # AudioPlayerWorker signals
    playback_started = pyqtSignal()
    playback_finished = pyqtSignal()
    playback_position_changed = pyqtSignal(float)
    playback_state_changed = pyqtSignal(PlaybackState)
    playback_cleared = pyqtSignal()
    thread_deleted = pyqtSignal()

    def __init__(self):
        super().__init__()
        # Thread and worker
        self._worker_thread: QThread | None = None
        self._worker = None

        # Setup
        self._init_thread_and_worker()

    # --- Public methods ---
    @property
    def has_thread(self) -> bool:
        return self._worker_thread is not None

    def play_audio(self, audio_pcm: AudioPCM) -> None:
        """Request track audio load to the audio worker.

        Args:
            audio_pcm: PCM audio data to load. Must be a valid AudioPCM instance.

        """
        self.play_audio_requested.emit(audio_pcm)

    def repeat_playback(self):
        """Request playback repeat to the audio worker."""
        self.repeat_playback_requested.emit()

    def pause_playback(self) -> None:
        """Request playback pause to the audio worker."""
        self.pause_playback_requested.emit()

    def resume_playback(self) -> None:
        """Request playback resume to the audio worker."""
        self.resume_playback_requested.emit()

    def seek(self, new_position_in_ms: int) -> None:
        """Request playback position update to the audio worker.

        Args:
            new_position_in_ms: Target position in milliseconds.

        """
        self.seek_requested.emit(new_position_in_ms)

    def set_volume(self, volume: int) -> None:
        """Request volume update to the audio worker.

        Args:
            volume: Volume level in range [0, 100].

        """
        self.set_volume_requested.emit(volume)

    def clear_playback(self) -> None:
        """Request playback stop and audio data release to the audio worker."""
        self.clear_playback_requested.emit()

    def shutdown(self):
        """Request a graceful shutdown of the audio worker."""
        self.shutdown_requested.emit()

    def quit_thread(self) -> None:
        """Ask the worker thread's event loop to quit directly.

        Does not wait for the worker's own graceful shutdown to complete
        first, so the thread may exit before the worker has released its
        resources.
        """
        if self._worker_thread is None:
            return

        self._worker_thread.quit()

    def terminate_thread(self):
        """Forcibly and immediately kill the worker thread.

        Last resort. The worker gets no chance to release its resources,
        and completion is not guaranteed to be signaled afterward.
        """
        if self._worker_thread is None:
            return

        self._worker_thread.terminate()

    # --- Protected/internal methods ---
    def _connect_signals(self) -> None:
        if self._worker is None:
            self._worker_thread.wait()

        # AudioPlayerService -> AudioPlayerWorker
        self.play_audio_requested.connect(self._worker.play_audio)
        self.pause_playback_requested.connect(self._worker.pause_playback)
        self.resume_playback_requested.connect(self._worker.resume_playback)
        self.repeat_playback_requested.connect(self._worker.restart_playback)
        self.seek_requested.connect(self._worker.seek)
        self.set_volume_requested.connect(self._worker.set_volume)
        self.clear_playback_requested.connect(self._worker.clear_playback)
        self.shutdown_requested.connect(self._worker.shutdown)

        # AudioPlayerWorker -> AudioPlayerService
        self._worker.playback_started.connect(self.playback_started.emit)
        self._worker.playback_finished.connect(self.playback_finished.emit)
        self._worker.playback_position_changed.connect(
            self.playback_position_changed.emit,
        )
        self._worker.playback_state_changed.connect(self.playback_state_changed.emit)
        self._worker.playback_cleared.connect(self.playback_cleared.emit)
        self._worker.shutdown_completed.connect(self._worker_thread.quit)
        self._worker_thread.finished.connect(self._on_thread_finished)

    def _init_thread_and_worker(self) -> None:
        # Create thread and worker
        self._worker_thread = QThread()
        self._worker = AudioPlayerWorker()

        # Move the worker to thread first before connecting the signals and starting
        # the thread (important)
        self._worker.moveToThread(self._worker_thread)
        self._connect_signals()
        self._worker_thread.start()

    @pyqtSlot()
    def _on_thread_finished(self):
        self._worker.deleteLater()
        self._worker = None

        self._worker_thread.deleteLater()
        self._worker_thread = None

        logger.info("Worker and thread deleted.")

        self.thread_deleted.emit()
