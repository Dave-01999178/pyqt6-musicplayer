import random
from dataclasses import dataclass

from pyqt6_music_player.core import PlaybackMode
from pyqt6_music_player.services import PlaylistService


# ----- NAVIGATION OUTCOME TYPES -----
@dataclass
class NoTrackLoaded:
    """No playback order or position is set."""

    pass


@dataclass
class TrackIndex:
    """A valid track index was resolved."""

    index: int


@dataclass
class StartBoundary:
    """Position is at the first track in the playback order."""

    pass


@dataclass
class EndBoundary:
    """Position is at the last track in the playback order."""

    pass


# ----- TYPE ALIAS -----
type NavigationOutcome = NoTrackLoaded | TrackIndex | StartBoundary | EndBoundary


# ================================================================================
# TRACK NAVIGATOR
# ================================================================================
class TrackNavigator:
    """Resolve next and previous track indices based on the current playback mode."""

    def __init__(self, playlist_service: PlaylistService):
        """Initialize TrackNavigator."""
        self._playlist_service = playlist_service
        self._playback_order: list[int] = []  # Ordered list of track indices
        self._position: int | None = None  # Current position in playback order
        self._playback_mode: PlaybackMode = PlaybackMode.NORMAL

        self._playlist_service.tracks_added.connect(self._on_track_added)

    # --- Public methods ---
    def get_next_track_index(self) -> NavigationOutcome:
        """Return the next track index, or a navigation outcome."""
        if not self._playback_order or self._position is None:
            return NoTrackLoaded()

        if self._position >= len(self._playback_order) - 1:
            return EndBoundary()

        self._position += 1

        return TrackIndex(self._playback_order[self._position])

    def get_previous_track_index(self) -> NavigationOutcome:
        """Return the previous track index, or a navigation outcome."""
        if not self._playback_order or self._position is None:
            return NoTrackLoaded()

        if self._position == 0:
            return StartBoundary()

        self._position -= 1

        return TrackIndex(self._playback_order[self._position])

    def set_playback_order_position(self, index: int) -> None:
        """Sync the position pointer to the given track index.

        Called by PlaybackService when a track is played directly
        (e.g. via mouse click) to keep the navigator in sync.

        Args:
            index: The current track index.

        """
        if not (0 <= index < len(self._playback_order)):
            return

        # Find the position of the track index in the playback order.
        # Necessary because playback order index != track index in shuffle mode.
        self._position = next(
            (
                idx_pos
                for idx_pos, track_idx in enumerate(self._playback_order)
                if track_idx == index
            ),
            self._position,  # Retain current position if track index is not found
        )

    def set_playback_mode(self, playback_mode: PlaybackMode) -> None:
        """Switch playback mode and rebuild the playback order.

        Args:
            playback_mode: The new playback mode to set.

        """
        if playback_mode == PlaybackMode.SHUFFLE:
            self._shuffle_playback_order()

        else:
            self._reset_playback_order()

        self._playback_mode = playback_mode

    # --- Protected/Internal methods ---
    def _reset_playback_order(self) -> None:
        if not self._playback_order:
            return

        # Restore sequential playback order and realign the position pointer
        # because position pointer tracks a position in the playback order list,
        # not a track index directly.
        #
        # Example:
        #     Shuffle on:  order=[0, 2, |1|], position=2
        #     Shuffle off: order=[0, |1|, 2], position=1
        #
        # Resolve actual track index before sorting, since position != track index
        self._position = self._playback_order[self._position]

        self._playback_order.sort()

    def _shuffle_playback_order(self) -> None:
        if not self._playback_order:
            return

        # Shuffle the playback order.
        if self._position is None:
            # No active track, shuffle everything
            random.shuffle(self._playback_order)

        # Shuffle all excluding the active track
        else:
            track_index = self._playback_order[self._position]
            remaining_tracks = [
                idx for idx in self._playback_order if idx != track_index
            ]

            # Pin current track at front so playback continues from it
            self._playback_order = [track_index, *remaining_tracks]

        self._position = 0

    def _on_track_added(self, new_track_idx: list[int]) -> None:
        # Update the playback order when tracks are added to the playlist.
        #
        # Build the playback order list on first insert
        if not self._playback_order:
            self._playback_order = new_track_idx

        # Append new indices to the end of the existing order (temporary approach)
        else:
            self._playback_order.extend(new_track_idx)
