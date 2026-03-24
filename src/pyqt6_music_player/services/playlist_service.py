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
        self.playlist_changed = Signal()
        self.playlist_model_position_changed = Signal()

        self._playlist.playlist_changed.connect(self._on_playlist_changed)

    def _on_playlist_changed(self) -> None:
        self.playlist_changed.emit()

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

        self._playlist.add_tracks(valid_tracks)

    def set_playlist_position(self, index: int) -> int:
        """Set playlist position and notify view of changes.

        Updates the internal position and emits a signal to trigger
        delegate active row updates in the UI.

        Args:
            index: Target position index in playlist.

        Returns:
            New playlist model position index, or None if invalid.

        """
        new_index = self._playlist.set_position(index)

        self.playlist_model_position_changed.emit(new_index)

        return new_index

    def sync_playlist_model_position(self, index: int) -> None:
        """Sync playlist position without triggering view updates.

        Used internally when the view selection changes to keep the
        model in sync without emitting signals (prevents feedback loops).

        Args:
            index: Position index to sync to.

        """
        self._playlist.sync_position(index)

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
