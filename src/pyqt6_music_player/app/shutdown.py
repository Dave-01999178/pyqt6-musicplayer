import logging

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QApplication

from pyqt6_music_player.core import Shutdownable, ShutdownStage

TIMEOUT_DURATION_IN_MS = 1000

logger = logging.getLogger(__name__)


class ShutdownHandler(QObject):
    """Coordinates a multi-stage, non-blocking shutdown of audio-player worker thread.

    Escalates through increasingly forceful stages (normal -> force quit -> terminate)
    if the previous stage doesn't complete within `TIMEOUT_DURATION_IN_MS`, and
    guarantees the application will close even if the worker thread never confirms
    its own termination.
    """

    shutdown_completed = pyqtSignal()

    def __init__(self, audio_player: Shutdownable):
        super().__init__()
        self._audio_player = audio_player
        self._stage = ShutdownStage.NOT_STARTED

        self._audio_player.thread_deleted.connect(self._on_thread_deleted)

    @property
    def can_close(self) -> bool:
        """Whether shutdown has finished and the application is safe to close."""
        return self._stage == ShutdownStage.DONE

    def begin_shutdown(self):
        # No worker thread exists at all (e.g. it failed to initialize at startup) -
        # there's nothing to shut down, so skip straight to completion.
        if not self._audio_player.has_thread:
            self._on_thread_deleted()  # Re-use `thread_deleted` handler
            return

        # Guard against re-entry: only the first call may start the ladder.
        if self._stage != ShutdownStage.NOT_STARTED:
            return

        self._stage = ShutdownStage.NORMAL_PENDING

        logger.info("Shutdown requested; starting normal shutdown.")

        self._audio_player.shutdown()

        # If normal shutdown hasn't completed in time, escalate to force quit.
        QTimer.singleShot(TIMEOUT_DURATION_IN_MS, self._escalate_to_force_quit)

    def _escalate_to_force_quit(self):
        # Normal shutdown already completed (thread deleted) - nothing to escalate.
        if not self._audio_player.has_thread:
            return

        # Only escalate once, and only if we're still waiting on normal shutdown
        if self._stage != ShutdownStage.NORMAL_PENDING:
            return

        self._stage = ShutdownStage.FORCE_QUIT_PENDING

        logger.warning(
            "Normal shutdown did not complete within %dms; escalating to force quit.",
            TIMEOUT_DURATION_IN_MS,
        )

        self._audio_player.quit_thread()

        # If force quit hasn't completed in time, escalate to a forced terminate.
        QTimer.singleShot(TIMEOUT_DURATION_IN_MS, self._escalate_to_terminate)

    def _escalate_to_terminate(self):
        # Force quit already completed (thread deleted) - nothing to escalate.
        if not self._audio_player.has_thread:
            return

        # Only escalate once, and only if we're still waiting on force quit.
        if self._stage != ShutdownStage.FORCE_QUIT_PENDING:
            return

        self._stage = ShutdownStage.TERMINATE_PENDING

        logger.warning(
            "Force quit did not complete within %dms; escalating to forced terminate.",
            TIMEOUT_DURATION_IN_MS,
        )

        # Last resort: abruptly kill the thread. `finished` signal is not guaranteed to
        # fire after this, so we don't rely on it.
        self._audio_player.terminate_thread()

        QTimer.singleShot(TIMEOUT_DURATION_IN_MS, self._force_close_application)

    def _force_close_application(self):
        # Guarantees the app will exit even if terminating audio-player thread never
        # produced a `finished` signal (and thus `_on_thread_deleted` never fired).
        #
        # Runs regardless of stage/thread state - only skipped if shutdown already
        # completed.
        if self._stage == ShutdownStage.DONE:
            return

        self._stage = ShutdownStage.DONE

        logger.warning(
            "Forcing application exit after terminate timeout; "
            "worker thread state unconfirmed.",
        )

        self.shutdown_completed.emit()

        # Explicit close
        app = QApplication.instance()
        if app is not None:
            app.quit()

    def _on_thread_deleted(self) -> None:
        if self._stage == ShutdownStage.DONE:
            return

        self._stage = ShutdownStage.DONE

        self.shutdown_completed.emit()
