from collections.abc import Sequence
from pathlib import Path

from pyqt6_music_player.core import SUPPORTED_AUDIO_FORMAT, Signal
from pyqt6_music_player.models import Playlist, Track


class PlaylistService:
    """Manage playlist operations.

    Acts as the application layer between the Playlist model and its consumers,
    handling validation, deduplication, and signal emission.

    """

    def __init__(self, playlist_model: Playlist):
        """Initialize PlaylistService.

        Args:
            playlist_model: The playlist model.

        """
        # Model
        self._playlist = playlist_model

        # Signals
        self.tracks_added = Signal()
        self.selection_index_changed = Signal()

    # -- Properties --
    @property
    def track_count(self) -> int:
        """Return the number of tracks in the playlist."""
        return self._playlist.track_count

    @property
    def selected_row(self) -> int | None:
        """Return the currently selected track index."""
        return self._playlist.selected_row

    # -- Public methods --
    def add_tracks(self, paths: Sequence[str]) -> None:
        """Add tracks to the playlist.

        Args:
            paths: A sequence of paths as strings.

        """
        if not paths:
            return

        normalized_paths = self._normalize_to_path(paths)
        valid_tracks = []

        for path in normalized_paths:
            try:
                resolved_path = path.resolve(strict=True)
            except FileNotFoundError:
                continue

            # No duplicates
            if self._playlist.has_track(resolved_path):
                continue

            # Must be a supported format
            if resolved_path.suffix.lower() not in SUPPORTED_AUDIO_FORMAT:
                continue

            track = Track.from_file(resolved_path)

            valid_tracks.append(track)

        add_count = self._playlist.add_tracks(valid_tracks)

        if add_count > 0:
            # Emit new track indices
            new_track_idx = list(range(self.track_count - add_count, self.track_count))

            self.tracks_added.emit(new_track_idx)

    def set_selected_row(self, index: int) -> int | None:
        """Set the selected row index.

        Args:
            index: The row index to select.

        Returns:
            The updated index, or None if invalid or unchanged.

        """
        new_index = self._playlist.set_selected_row(index)

        if new_index is not None:
            self.selection_index_changed.emit(new_index)

        return new_index

    def get_track_by_index(self, index: int) -> Track | None:
        """Get track at the specified index.

        Args:
            index: The track index.

        Returns:
            The track at given index, or None if invalid.

        """
        return self._playlist.get_track_by_index(index)

    # -- Protected/internal methods --
    @staticmethod
    def _normalize_to_path(paths: Sequence[str]) -> list[Path]:
        """Convert valid path string input into a Path object.

        Args:
            paths: A sequence of paths as strings.

        Returns:
            list[Path]: The normalized input as Path objects stored in a list.

        """
        normalized_paths = []

        for path in paths:
            if path in {"", "."}:
                continue

            normalized_path = Path(path)

            # Skip cwd, empty values, or directories
            if normalized_path in {Path(""), Path(".")} or normalized_path.is_dir():
                continue

            normalized_paths.append(normalized_path)

        return normalized_paths
