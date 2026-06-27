import logging
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from pyqt6_music_player.track.track import Track

logger = logging.getLogger(__name__)


@dataclass
class AddTracksResult:
    track_indices: list[int]
    add_count: int
    skipped_duplicates: int


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
        new_tracks = self._filter_duplicates(tracks)
        if len(new_tracks) > 0:
            self._tracks.extend(new_tracks)
            self._tracks.sort(key=lambda t: t.title)

        add_count = len(new_tracks)
        duplicate_count = len(tracks) - len(new_tracks)
        logger.info(
            "Add tracks: %d/%d added (%d duplicates)",
            add_count,
            len(tracks),
            duplicate_count,
        )

        # Get new tracks indices for playback order updates
        new_tracks_indices = self._get_track_indices(new_tracks)

        return AddTracksResult(
            new_tracks_indices,
            add_count=add_count,
            skipped_duplicates=duplicate_count,
        )

    def remove_track_at_index(self, index: int) -> None:
        """Remove track from the playlist.

        Args:
            index: Track's position in the playlist.

        """
        target_path = self._tracks[index].path

        self._tracks = [track for track in self._tracks if track.path != target_path]
        self._track_paths.remove(target_path)


    def get_track_by_index(self, index: int) -> Track:
        """Get track at the specified index.

        Args:
            index: The track index.

        Returns:
            The track at given index.

        """
        return self._tracks[index]

    # -- Protected/Internal methods --
    def _filter_duplicates(self, tracks: Sequence[Track]) -> list[Track]:
        new_tracks = []
        for track in tracks:
            track_path = track.path

            # Skip duplicates
            if track_path in self._track_paths:
                logger.debug("Skipping duplicate file: %s", track.path)
                continue

            new_tracks.append(track)

            self._track_paths.add(track_path)

            logger.debug("Added track '%s' to the playlist.", track.title)

        return new_tracks

    def _get_track_indices(self, tracks: Sequence[Track]) -> list[int]:
        path_to_index = {
            track.path: track_idx for track_idx, track in enumerate(self._tracks)
        }
        return [
            path_to_index[track.path]
            for track in tracks
            if track.path in path_to_index
        ]
