import logging
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from pyqt6_music_player.models import Track

logger = logging.getLogger(__name__)


@dataclass
class AddTracksResult:
    track_indices: list[int]
    add_count: int
    skipped_count: int


class Playlist:
    """Manages playlist tracks."""

    def __init__(self) -> None:
        """Initialize PlaylistModel."""
        super().__init__()
        self._tracks: list[Track] = []
        self._track_paths: set[Path] = set()

    # -- Properties --
    @property
    def track_count(self) -> int:
        """Return the number of tracks in the playlist."""
        return len(self._tracks)

    # -- Public methods --
    def add_tracks(self, tracks: Sequence[Track]) -> AddTracksResult:
        """Add tracks to the playlist.

        Args:
            tracks: Tracks to add.

        Returns:
            Number of tracks added.

        """
        new_tracks = []
        skipped = 0
        for track in tracks:
            track_path = track.path

            # No duplicates
            if track_path in self._track_paths:
                logger.debug("Skipping duplicate file: %s", track.path)
                skipped += 1
                continue

            new_tracks.append(track)

            self._track_paths.add(track_path)

            logger.debug("Added track '%s' to the playlist.", track.title)

        # Add and sort
        if len(new_tracks) > 0:
            self._tracks.extend(new_tracks)
            self._tracks.sort(key=lambda t: t.title)

        # Summary log
        logger.info(
            "Added tracks: %d total, %d added, %d skipped.",
            len(tracks), len(new_tracks), skipped
        )

        new_track_indices = self._get_track_index(new_tracks)

        return AddTracksResult(
            new_track_indices,
            add_count=len(new_tracks),
            skipped_count=skipped,
        )

    def get_track_by_index(self, index: int) -> Track | None:
        """Get track at the specified index.

        Args:
            index: The track index.

        Returns:
            The track at given index, or None if invalid.

        """
        if not (0 <= index < len(self._tracks)):
            return None

        return self._tracks[index]

    # -- Protected/Internal methods --
    def _get_track_index(self, tracks: list[Track]) -> list[int]:
        path_to_index = {
            track.path: track_idx for track_idx, track in enumerate(self._tracks)
        }
        return [
            path_to_index[track.path]
            for track in tracks
            if track.path in path_to_index
        ]
