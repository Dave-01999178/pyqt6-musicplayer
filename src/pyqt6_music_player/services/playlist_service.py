from pathlib import Path
from typing import Sequence

from pyqt6_music_player.core import SUPPORTED_AUDIO_FORMAT, Signal
from pyqt6_music_player.models import Playlist, Track


class PlaylistService:
    def __init__(self, playlist_model: Playlist):
        # Model
        self._playlist = playlist_model

        # Signals
        self.tracks_added = Signal()
        self.selection_index_changed = Signal()

    # --- Public methods ---
    def add_tracks(self, paths: Sequence[str]) -> None:
        """Command for adding tracks to the playlist.

        Supported extensions: .mp3, .wav, .flac, .ogg

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
            # Emit add count, and the new track count.
            self.tracks_added.emit(add_count, self._playlist.track_count)

        return

    def set_selected_index(self, index: int) -> int | None:
        """Model selected index setter.

        Args:
            index: The selected row index in playlist.

        Returns:
            The updated index or None if the given index is invalid.

        """
        new_index = self._playlist.set_selected_index(index)

        if new_index is not None:
            self.selection_index_changed.emit(new_index)

        return new_index

    def get_track_count(self) -> int:
        """Return the number of tracks in the playlist."""
        return self._playlist.track_count

    def get_track_by_index(self, index: int) -> Track | None:
        """Get track at the specified index.

        Args:
            index: The track index.

        Returns:
            The track at given index, or None if invalid.

        """
        return self._playlist.get_track_by_index(index)

    def get_selected_index(self) -> int:
        """Return the currently selected track index."""
        return self._playlist.selected_index

    # --- Protected/internal methods ---
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
