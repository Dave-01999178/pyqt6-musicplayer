import logging

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread

from pyqt6_music_player.audio import AudioPlayerWorker
from pyqt6_music_player.core import PlaybackStatus
from pyqt6_music_player.models import TrackAudio

logger = logging.getLogger(__name__)


# ================================================================================
# AUDIO PLAYER INTERFACE
# ================================================================================
#
# noinspection PyUnresolvedReferences
class AudioPlayerService(QObject):
    # Service signals
    load_audio_requested = pyqtSignal(TrackAudio)
    start_playback_requested = pyqtSignal()
    pause_playback_requested = pyqtSignal()
    resume_playback_requested = pyqtSignal()
    seek_requested = pyqtSignal(int)
    shutdown_requested = pyqtSignal()

    # Worker signals
    audio_loaded = pyqtSignal()
    playback_started = pyqtSignal()
    playback_position_changed = pyqtSignal(float)
    playback_status_changed = pyqtSignal(PlaybackStatus)
    playback_finished = pyqtSignal()
    player_resources_released = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._worker_thread = None
        self._worker = None

        self._init_thread_and_worker()

    # --- Slots ---
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

        self.player_resources_released.emit()

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

    # --- Public methods (Commands) ---
    def load_track_audio(self, track_audio: TrackAudio):
        if not isinstance(track_audio, TrackAudio):
            return

        self.load_audio_requested.emit(track_audio)

    def start_playback(self) -> None:
        self.start_playback_requested.emit()

    def pause_playback(self) -> None:
        self.pause_playback_requested.emit()

    def resume_playback(self) -> None:
        self.resume_playback_requested.emit()

    def seek(self, new_position_in_ms: int) -> None:
        self.seek_requested.emit(new_position_in_ms)

    def is_running(self) -> bool:
        return self._worker_thread is not None and self._worker_thread.isRunning()

    def shutdown(self):
        if self._worker_thread is None:
            self.player_resources_released.emit()
            return

        self.shutdown_requested.emit()