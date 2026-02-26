import logging

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread

from pyqt6_music_player.audio import AudioPlayerWorker
from pyqt6_music_player.core import PlaybackStatus
from pyqt6_music_player.models import AudioPCM

logger = logging.getLogger(__name__)


# ================================================================================
# AUDIO PLAYER SERVICE
# ================================================================================
#
# noinspection PyUnresolvedReferences
class AudioPlayerService(QObject):
    """Manages audio playback worker thread and coordinates signal communication.

    Acts as a thread-safe interface to the audio player worker, handling thread
    lifecycle and signal routing between the main thread and worker thread.

    """

    # AudioPlayerService signals
    load_audio_requested = pyqtSignal(AudioPCM)
    start_playback_requested = pyqtSignal()
    pause_playback_requested = pyqtSignal()
    resume_playback_requested = pyqtSignal()
    seek_requested = pyqtSignal(int)
    shutdown_requested = pyqtSignal()

    # AudioPlayerWorker signals
    audio_loaded = pyqtSignal()
    playback_started = pyqtSignal()
    playback_finished = pyqtSignal()
    playback_position_changed = pyqtSignal(float)
    playback_status_changed = pyqtSignal(PlaybackStatus)
    player_resources_released = pyqtSignal()

    def __init__(self):
        """Initialize AudioPlayerService and its worker thread."""
        super().__init__()
        # Thread and worker
        self._worker_thread = None
        self._worker = None

        # Setup
        self._init_thread_and_worker()

    # --- Public methods ---
    def load_track_audio(self, audio_pcm: AudioPCM):
        """Request track audio load to the worker."""
        if not isinstance(audio_pcm, AudioPCM):
            return

        self.load_audio_requested.emit(audio_pcm)

    def start_playback(self) -> None:
        """Request playback start."""
        self.start_playback_requested.emit()

    def pause_playback(self) -> None:
        """Request playback pause."""
        self.pause_playback_requested.emit()

    def resume_playback(self) -> None:
        """Request playback resume"""
        self.resume_playback_requested.emit()

    def seek(self, new_position_in_ms: int) -> None:
        """Request playback position update."""
        self.seek_requested.emit(new_position_in_ms)

    def shutdown(self):
        """Request thread shutdown."""
        if self._worker_thread is None:
            self.player_resources_released.emit()
            return

        self.shutdown_requested.emit()

    def is_running(self) -> bool:
        """Check if there's a current running thread.

        Returns:
            True if there is a running thread; Else, False.
        """
        return self._worker_thread is not None and self._worker_thread.isRunning()

    # --- Protected/internal methods ---
    def _connect_signals(self) -> None:
        """Establish signal–slot connections between the service and worker."""
        if self._worker is None:
            return

        # Connect service signals to worker.
        self.load_audio_requested.connect(self._worker.load_track_audio)
        self.start_playback_requested.connect(self._worker.start_playback)
        self.pause_playback_requested.connect(self._worker.pause_playback)
        self.resume_playback_requested.connect(self._worker.resume_playback)
        self.seek_requested.connect(self._worker.seek)
        self.shutdown_requested.connect(self._worker.release_resources)

        # Connect worker signals to service.
        self._worker.audio_loaded.connect(self._on_audio_load)
        self._worker.playback_started.connect(self._on_playback_started)
        self._worker.byte_position_changed.connect(self._on_byte_position_changed)
        self._worker.status_changed.connect(self._on_playback_status_changed)
        self._worker.playback_finished.connect(self._on_playback_finished)
        self._worker.resources_released.connect(self._worker_thread.quit)
        self._worker_thread.finished.connect(self._on_thread_finished)

    def _init_thread_and_worker(self) -> None:
        """Initialize thread and worker then connect signals."""
        if self._worker_thread is not None:
            return

        # Create thread and worker
        self._worker_thread = QThread()
        self._worker = AudioPlayerWorker()

        # IMPORTANT!!!
        # Move the worker to thread first before connecting signals and starting thread
        self._worker.moveToThread(self._worker_thread)

        # Connect service and worker signals
        self._connect_signals()

        # Start thread
        self._worker_thread.start()

    @pyqtSlot()
    def _on_audio_load(self) -> None:
        self.audio_loaded.emit()

    @pyqtSlot()
    def _on_playback_started(self) -> None:
        self.playback_started.emit()

    @pyqtSlot(float)
    def _on_byte_position_changed(self, byte_pos_as_sec: float) -> None:
        self.playback_position_changed.emit(byte_pos_as_sec)

    @pyqtSlot()
    def _on_playback_finished(self):
        self.playback_finished.emit()

    @pyqtSlot(PlaybackStatus)
    def _on_playback_status_changed(self, playback_status: PlaybackStatus) -> None:
        self.playback_status_changed.emit(playback_status)

    @pyqtSlot()
    def _on_thread_finished(self):
        self._worker.deleteLater()
        self._worker = None

        self._worker_thread.deleteLater()
        self._worker_thread = None

        logger.info("Worker and thread deleted.")

        self.player_resources_released.emit()
