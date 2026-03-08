import logging
from collections.abc import Sequence
from pathlib import Path

from pyqt6_music_player.models import Track

logger = logging.getLogger(__name__)


class Playlist:
    """Manages playlist tracks and selection state."""

    def __init__(self) -> None:
        """Initialize PlaylistModel."""
        super().__init__()
        self._tracks: list[Track] = []
        self._track_paths: set[Path] = set()
        self._selected_index: int | None = None

    # --- Properties ---
    @property
    def track_count(self) -> int:
        """Return the number of tracks in the playlist."""
        return len(self._tracks)

    @property
    def selected_index(self) -> int | None:
        """Return the currently selected track index."""
        return self._selected_index

    # --- Public methods ---
    def add_tracks(self, tracks: Sequence[Track]) -> int:
        """Add tracks to the playlist.

        Args:
            tracks: Tracks to add.

        Returns:
            Number of tracks added.

        """
        add_count = 0

        for track in tracks:
            track_path = track.path

            # No duplicates
            if track_path in self._track_paths:
                continue

            self._tracks.append(track)
            self._track_paths.add(track_path)

            add_count += 1

        if add_count == 1:
            logger.info("Added track '%s' to the playlist.", tracks[0].title)
        else:
            logger.info("Added %d tracks to playlist.", add_count)

        return add_count

    def get_all_tracks(self) -> list[Track]:
        """Return all tracks in the playlist.

        Returns:
            A list of tracks.

        """
        return self._tracks.copy()

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

    def set_selected_index(self, index: int) -> int | None:
        """Set the selected track index.

        Args:
            index: The row index to select.

        Returns:
            The updated index, or None if invalid or unchanged.

        """
        if not (0 <= index < len(self._tracks)):
            return None

        self._selected_index = index

        return self._selected_index

    def has_track(self, track_path: Path) -> bool:
        """Check if playlist contains a track with the given path.

        Args:
            track_path: Path to check.

        Returns:
            True if track exists in playlist; Otherwise, False.

        """
        return Path(track_path) in self._track_paths

    # TODO: Unused
    def is_valid_index(self, index: int) -> bool:
        """Check if index is within playlist bounds.

        Args:
            index: Index to validate.

        Returns:
            True if index is valid; Otherwise, False

        """
        return 0 <= index < len(self._tracks)
