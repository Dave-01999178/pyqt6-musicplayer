import logging
from collections.abc import Sequence
from pathlib import Path

from pyqt6_music_player.core import Signal
from pyqt6_music_player.models import Track

logger = logging.getLogger(__name__)


class Playlist:
    """Manages playlist tracks."""

    def __init__(self) -> None:
        """Initialize PlaylistModel."""
        super().__init__()
        self._tracks: list[Track] = []
        self._track_paths: set[Path] = set()

        self._playlist_position: int | None = None

        self.playlist_changed = Signal()

    # --- Properties ---
    @property
    def track_count(self) -> int:
        """Return the number of tracks in the playlist."""
        return len(self._tracks)

    @property
    def selected_row(self) -> int | None:
        """Return the currently selected row index."""
        return self._playlist_position

    # --- Public methods ---
    def add_tracks(self, tracks: Sequence[Track]) -> None:
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

        self.playlist_changed.emit()

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

    def set_position(self, index: int) -> int:
        """Set current playlist position.

        Args:
            index: New position index.

        Returns:
            Updated playlist position.

        """
        self._playlist_position = index

        return self._playlist_position

    def sync_position(self, index: int) -> None:
        """Sync position without triggering updates (internal use only).

        Silently updates the internal position state. Used internally
        when the view selection changes to keep the model in sync
        without emitting signals (prevents feedback loops).

        Args:
            index: Position index to sync.

        """
        if index == self._playlist_position:
            return

        self._playlist_position = index

    def has_track(self, track_path: Path) -> bool:
        """Check if playlist contains a track with the given path.

        Args:
            track_path: Path to check.

        Returns:
            True if track exists in playlist; Otherwise, False.

        """
        return Path(track_path) in self._track_paths
