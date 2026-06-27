import logging
from collections.abc import Sequence
from pathlib import Path

from mutagen import MutagenError

from pyqt6_music_player.core import (
    SUPPORTED_AUDIO_FORMAT,
    PlaybackOrderProtocol,
    Signal,
    UnsupportedFileError,
)
from pyqt6_music_player.track import Track

from .playlist import Playlist

logger = logging.getLogger(__name__)


class PlaylistService:
    """Manage playlist operations."""

    initial_tracks_added = Signal()
    active_track_removed = Signal()
    tracks_added = Signal()
    track_removed = Signal()
    shuffle_order_changed = Signal()

    def __init__(
            self,
            playlist_model: Playlist,
            playback_order: PlaybackOrderProtocol,
    ):
        """Initialize PlaylistService.

        Args:
            playlist_model: The playlist model
            playback_order: The service managing playback order

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

    @property
    def current_track_index(self) -> int | None:
        """Return the current track's index position in the playlist."""
        return self._playback_order.current_track_index

    # -- Public methods --
    def add_tracks_from_paths(self, paths: Sequence[str]) -> None:
        """Load and add tracks from file paths.

        Args:
            paths: A sequence of file path strings.

        """
        # Normalize paths
        normalized_paths = self._normalize_paths(paths)
        if not normalized_paths:
            return  # Nothing to load

        # Load tracks from files
        tracks, errors = self._load_tracks_from_files(normalized_paths)
        if not tracks:
            return  # Nothing to add

        # Add the loaded tracks to playlist
        result = self._playlist.add_tracks(tracks)
        total_skipped = result.skipped_duplicates + errors
        logger.info(
            "Add tracks completed: "
            "%d requested, %d added, %d skipped (%d duplicates, %d errors).",
            len(paths),
            result.add_count,
            total_skipped,
            result.skipped_duplicates,
            errors,
        )

        # Update the PlaybackOrder and notify the PlaylistViewModel when
        # new tracks are added
        if result.add_count > 0:
            state = self._playback_order.add_indices_to_order(result.track_indices)

            self.tracks_added.emit(state)

            if self._playlist.track_count - result.add_count == 0:
                self.initial_tracks_added.emit()

    def remove_track_at_index(self, index: int) -> None:
        """Remove track from the playlist.

        Args:
            index: Track's position in the playlist.

        """
        self._playlist.remove_track_at_index(index)

        state = self._playback_order.remove_index_from_order(index)

        self.track_removed.emit(state)

        if state.active_track_removed:
            self.active_track_removed.emit()

    def get_track_by_index(self, index: int) -> Track:
        """Get track at the specified index.

        Args:
            index: Track's position in the playlist.

        Returns:
            The track at given index.

        """
        return self._playlist.get_track_by_index(index)

    # -- Protected/internal methods --
    def _connect_signals(self) -> None:
        # PlaylistService -> PlaylistViewModel
        self._playback_order.order_changed.connect(self.shuffle_order_changed.emit)

    @staticmethod
    def _normalize_paths(paths: Sequence[str]) -> list[Path]:
        """Validate and normalize file paths.

        Filters out non-existent files, directories, and unsupported formats.

        Args:
            paths: Sequence of file path strings.

        Returns:
            List of validated and resolved Path objects.

        """
        normalized_paths = []
        for p in paths:
            path = Path(p).expanduser()

            # Missing
            if not path.exists():
                logger.warning("Skipping non-existent file: %s.", path)
                continue

            # Not a file
            if not path.is_file():
                logger.warning("Skipping non-file: %s.", path)
                continue

            # Not supported
            if path.suffix.lower() not in SUPPORTED_AUDIO_FORMAT:
                logger.warning("Skipping non-audio or unsupported file: %s.", path)
                continue

            resolved_path = path.resolve()
            normalized_paths.append(resolved_path)

            logger.debug("Resolved path: %s", resolved_path)

        skipped = len(paths) - len(normalized_paths)
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
        for path in paths:
            try:
                track = Track.from_file(path)

                tracks.append(track)

                logger.debug("Loaded track '%s' from: %s.", track.title, path)

            # EXPECTED ERRORS
            #
            # File has correct extension but wrong content
            except UnsupportedFileError:
                logger.warning("File is not a valid audio file: %s", path)

            # File is audio but has corrupt/unreadable metadata
            except MutagenError:
                logger.warning("Failed to read metadata from: %s", path)

            # UNEXPECTED ERRORS
            except Exception:
                logger.exception("Unexpected error while loading file: %s.", path)
                continue

        error_count = len(paths) - len(tracks)
        logger.info(
            "Track loading: %d/%d loaded (%d errors).",
            len(tracks),
            len(paths),
            error_count,
        )

        return tracks, error_count
