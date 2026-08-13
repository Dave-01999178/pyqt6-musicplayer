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
            playlist: Playlist,
            playback_order: PlaybackOrderProtocol,
    ):
        # Model
        self._playlist = playlist
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
        # FUTURE IMPROVEMENT: Duplicate tracks are still resolved and loaded
        # before being filtered out in playlist. If bulk/repeated adds become common
        # (e.g. watch-folder or re-scan features), consider pre-checking paths against
        # the playlist earlier to avoid processing duplicates.
        validated_paths = self._validate_paths(paths)
        if not validated_paths:
            logger.warning(
                "Add tracks aborted: no valid paths from %d selected.",
                len(paths),
            )
            return

        tracks = self._load_tracks_from_paths(validated_paths)
        if not tracks:
            logger.warning(
                "Add tracks aborted: no tracks loaded from %d valid path(s).",
                len(validated_paths),
            )
            return

        result = self._playlist.add_tracks(tracks)
        logger.info(
            "Add tracks completed: %d requested, %d added "
            "(%d invalid paths, %d load errors, %d duplicates).",
            len(paths),
            result.add_count,
            len(paths) - len(validated_paths),
            len(validated_paths) - len(tracks),
            result.skipped_duplicates,
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

    # -- Protected methods --
    def _connect_signals(self) -> None:
        # PlaylistService -> PlaylistViewModel
        self._playback_order.order_changed.connect(self.shuffle_order_changed.emit)

    @staticmethod
    def _validate_paths(paths: Sequence[str]) -> list[Path]:
        """Validate paths and resolve them to absolute paths.

        Filters out non-existent paths, directories, and unsupported audio formats.

        Args:
            paths: Sequence of file path strings.

        Returns:
            List of validated and resolved Path objects.

        """
        logger.debug("Path validation: starting for %d path(s).", len(paths))

        validated_paths = []
        seen_resolved_paths = set()
        for p in paths:
            path = Path(p).expanduser()

            # Fast-fail on unsupported formats: check extension first before disk I/O.
            # This avoids expensive filesystem operations on files we'll reject anyway.
            if path.suffix.lower() not in SUPPORTED_AUDIO_FORMAT:
                logger.warning(
                    "Skipping non-audio or unsupported audio format: %s.",
                    path,
                )
                continue

            if not path.is_file():
                logger.warning("Skipping non-existent file or directory: %s.", path)
                continue

            resolved_path = path.resolve()

            if resolved_path in seen_resolved_paths:
                logger.debug("Skipping batch duplicate: %s", resolved_path)
                continue

            validated_paths.append(resolved_path)
            seen_resolved_paths.add(resolved_path)

            logger.debug("Validated path: %s", resolved_path)

        logger.debug(
            "Path validation: %d/%d valid (%d skipped).",
            len(validated_paths),
            len(paths),
            len(paths) - len(validated_paths),
        )

        return validated_paths

    @staticmethod
    def _load_tracks_from_paths(paths: Sequence[Path]) -> list[Track]:
        """Load Track objects from validated paths.

        Args:
            paths: Sequence of validated audio file paths.

        Returns:
            List of Track objects.

        """
        logger.debug("Track loading: starting for %d path(s).", len(paths))

        tracks = []
        for path in paths:
            try:
                track = Track.from_file(path)

                tracks.append(track)

                logger.debug("Loaded track '%s' from: %s.", track.title, path)

            # EXPECTED ERRORS
            #
            # File has audio extension but content is invalid or unsupported.
            except UnsupportedFileError:
                logger.warning("File is not a valid audio file: %s", path)

            # Failed to parse metadata (corruption, unsupported format, etc.).
            except MutagenError:
                logger.warning("Failed to read metadata from: %s", path)

            # UNEXPECTED ERRORS
            except Exception:
                logger.exception("Unexpected error while loading file: %s.", path)
                continue

        logger.debug(
            "Track loading: %d/%d loaded (%d errors).",
            len(tracks),
            len(paths),
            len(paths) - len(tracks),
        )

        return tracks
