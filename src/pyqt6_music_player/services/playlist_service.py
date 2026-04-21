import logging
from collections.abc import Sequence
from pathlib import Path

from mutagen import MutagenError

from pyqt6_music_player.core import SUPPORTED_AUDIO_FORMAT
from pyqt6_music_player.core.signals import Signal
from pyqt6_music_player.exceptions import UnsupportedFileError
from pyqt6_music_player.models import Playlist, Track
from pyqt6_music_player.services import PlaybackOrder

logger = logging.getLogger(__name__)


class PlaylistService:
    """Manage playlist operations."""

    initial_tracks_added = Signal()
    playback_order_changed = Signal()
    playback_order_position_changed = Signal()

    def __init__(self, playlist_model: Playlist, playback_order: PlaybackOrder):
        """Initialize PlaylistService.

        Args:
            playlist_model: The playlist model.
            playback_order: The playback order

        """
        # Model
        self._playlist = playlist_model
        self._playback_order = playback_order

        self._connect_signals()

    # -- Properties --
    @property
    def track_count(self) -> int:
        """Return the number of tracks in the playlist."""
        return self._playlist.track_count

    def get_playback_order_snapshot(self) -> list[int]:
        return self._playback_order.order

    # -- Public methods --
    def add_tracks_from_paths(self, paths: Sequence[str]) -> None:
        """Load and add tracks from file paths.

        Args:
            paths: A sequence of file path strings.

        """
        # Normalize paths
        normalized_paths = self._normalize_paths(paths)
        if not normalized_paths:
            return

        # Load tracks from files
        tracks, errors = self._load_tracks_from_files(normalized_paths)
        if not tracks:
            return

        # Add tracks
        result = self._playlist.add_tracks(tracks)

        total_skipped = result.skipped_count + errors
        logger.info(
            "Add tracks completed: %d requested, %d added, %d skipped (%d errors).",
            len(paths),
            result.add_count,
            total_skipped,
            errors,
        )

        if result.add_count > 0:
            self._playback_order.add_to_playback_order(result.track_indices)
            if self.track_count - result.add_count == 0:
                self.initial_tracks_added.emit()

    def get_track_by_index(self, index: int) -> Track | None:
        """Get track at the specified index.

        Args:
            index: The track index.

        Returns:
            The track at given index, or None if invalid.

        """
        return self._playlist.get_track_by_index(index)

    # -- Protected/internal methods --
    def _connect_signals(self):
        self._playback_order.order_changed.connect(self.playback_order_changed.emit)
        self._playback_order.position_changed.connect(
            self.playback_order_position_changed.emit,
        )

    @staticmethod
    def _normalize_paths(paths: Sequence[str]) -> list[Path]:
        """Validate and normalize file paths.

        Filters out non-existent files, directories, and unsupported formats.

        Args:
            paths: Sequence of file path strings.

        Returns:
            List of validated, resolved Path objects.

        """
        normalized_paths = []
        skipped = 0
        for p in paths:
            path = Path(p).expanduser()

            # Missing
            if not path.exists():
                logger.warning("Skipping non-existent file: %s.", path)
                skipped += 1
                continue

            # Not a file
            if not path.is_file():
                logger.warning("Skipping non-file: %s.", path)
                skipped += 1
                continue

            # Not supported
            if path.suffix.lower() not in SUPPORTED_AUDIO_FORMAT:
                logger.warning("Skipping non-audio or unsupported file: %s.", path)
                skipped += 1
                continue

            resolved_path = path.resolve()
            normalized_paths.append(resolved_path)

            logger.debug("Resolved path: %s", resolved_path)

        logger.info(
            "Path validation: %d/%d valid (%d skipped).",
            len(normalized_paths),
            len(paths),
            skipped,
        )

        return normalized_paths

    @staticmethod
    def _load_tracks_from_files(paths: Sequence[Path]) -> tuple[list[Track], int]:
        """Load Track objects from validated file paths.

        Args:
            paths: Sequence of validated audio file paths.

        Returns:
            Tuple of (loaded tracks, error count).

        """
        tracks = []
        error_count = 0
        for path in paths:
            try:
                track = Track.from_file(path)

                tracks.append(track)

                logger.debug("Loaded track '%s' from: %s.", track.title, path)

            # Expected error
            except UnsupportedFileError:
                # File has correct extension but wrong content
                logger.warning("File is not a valid audio file: %s", path)
                error_count += 1

            except MutagenError:
                # File is audio but has corrupt/unreadable metadata
                logger.warning("Failed to read metadata from: %s", path)
                error_count += 1

            # Unexpected errors
            except Exception:
                logger.exception("Unexpected error while loading file: %s.", path)
                error_count += 1
                continue

        logger.info(
            "Track loading: %d total, %d loaded, %d errors.",
            len(paths), len(tracks), error_count
        )

        return tracks, error_count
