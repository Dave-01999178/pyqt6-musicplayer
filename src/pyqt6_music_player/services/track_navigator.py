import random
from dataclasses import dataclass

from pyqt6_music_player.core import RepeatMode, ShuffleMode
from pyqt6_music_player.services import PlaylistService


# ==================== NAVIGATION OUTCOME TYPES ====================
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

@dataclass
class RepeatCurrent:
    """Repeat current track."""

    pass


type NavigationOutcome = (
        NoTrackLoaded | TrackIndex | StartBoundary | EndBoundary | RepeatCurrent
)


# ==================== TRACK NAVIGATOR ====================
class TrackNavigator:
    """Resolve next and previous track indices based on the current playback mode."""

    def __init__(self, playlist_service: PlaylistService):
        """Initialize TrackNavigator.

        Args:
            playlist_service: Service managing playlist state and operations.

        """
        self._playlist_service = playlist_service
        self._playback_order: list[int] = []  # Ordered list of track indices
        self._position: int | None = None  # Current position in playback order
        self._repeat_mode: RepeatMode = RepeatMode.OFF
        self._shuffle_mode: ShuffleMode = ShuffleMode.OFF

        self._playlist_service.tracks_added.connect(self._on_track_added)

    # -- Public methods --
    def resolve_initial_track_index(self) -> NavigationOutcome:
        """Resolve the track index to begin playback.

        Returns:
            ``NoTrackLoaded`` if the playlist is empty.
            ``TrackIndex`` of the selected track, or first track if none is selected.
        """
        if self._playlist_service.track_count == 0:
            return NoTrackLoaded()

        selected_row = self._playlist_service.selected_row

        # Default to first track if none is selected
        return TrackIndex(selected_row or 0)

    def resolve_auto_advance_index(self) -> NavigationOutcome:
        """Resolve the next track index for autoplay.

        Returns:
            ``NoTrackLoaded`` if the playlist is empty or no track is active.
            ``RepeatCurrent`` if repeat mode is ONE.
            ``EndBoundary`` if repeat mode is OFF and the current track is last.
            ``TrackIndex`` of the next track otherwise.

        """
        if not self._playback_order or self._position is None:
            return NoTrackLoaded()

        is_end_boundary = self._position >= len(self._playback_order) - 1
        if self._repeat_mode == RepeatMode.OFF:
            if is_end_boundary:
                return EndBoundary()

            self._position += 1

            return TrackIndex(self._playback_order[self._position])

        if self._repeat_mode == RepeatMode.ONE:
            return RepeatCurrent()

        self._position = (self._position + 1) % len(self._playback_order)

        return TrackIndex(self._playback_order[self._position])

    def resolve_next_track_index(self) -> NavigationOutcome:
        """Resolve the next track index.

        Returns:
            ``NoTrackLoaded`` if the playlist is empty or no track is active.
            ``EndBoundary`` if repeat mode is OFF and ONE, and the current track is last.
            ``TrackIndex`` of the next track otherwise.

        """
        if not self._playback_order or self._position is None:
            return NoTrackLoaded()

        is_end_boundary = self._position >= len(self._playback_order) - 1
        if self._repeat_mode in {RepeatMode.OFF, RepeatMode.ONE} and is_end_boundary:
            return EndBoundary()

        self._position = (self._position + 1) % len(self._playback_order)

        return TrackIndex(self._playback_order[self._position])

    def resolve_previous_track_index(self) -> NavigationOutcome:
        """Resolve the previous track index.

        Returns:
            ``NoTrackLoaded`` if the playlist is empty or no track is active.
            ``StartBoundary`` if the current track is first.
            ``TrackIndex`` of the previous track otherwise.

        """
        if not self._playback_order or self._position is None:
            return NoTrackLoaded()

        if self._position == 0:
            return StartBoundary()

        self._position -= 1

        return TrackIndex(self._playback_order[self._position])

    def set_repeat_mode(self, repeat_mode: RepeatMode) -> None:
        """Set the repeat mode.

        Args:
            repeat_mode: The repeat mode to apply (OFF, ONE, or ALL).

        """
        self._repeat_mode = repeat_mode

    def set_shuffle_mode(self, shuffle_mode: ShuffleMode) -> None:
        """Set the shuffle mode and reorder the playback order accordingly.

        Enabling shuffle randomizes the playback order while pinning the active
        track at the front. Disabling restores sequential order.

        Args:
            shuffle_mode: The shuffle mode to apply (ON or OFF).

        """
        if shuffle_mode == ShuffleMode.ON:
            self._shuffle_playback_order()
        else:
            self._reset_playback_order()

        self._shuffle_mode = shuffle_mode

    def set_playback_order_position(self, index: int) -> None:
        """Sync the position pointer to the given track index.

        Called by PlaybackService when a track is played directly
        (e.g. via mouse click) to keep the navigator in sync.

        Args:
            index: The current track index.

        """
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

    # -- Protected/Internal methods --
    def _reset_playback_order(self) -> None:
        if not self._playback_order or self._position is None:
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

            random.shuffle(remaining_tracks)

            # Pin current track at front so playback continues from it
            self._playback_order = [track_index, *remaining_tracks]

        self._position = 0

        print(self._playback_order)

    def _on_track_added(self, new_track_idx: list[int]) -> None:
        # Update the playback order when tracks are added to the playlist.
        #
        # Build the playback order list on first insert
        if not self._playback_order:
            self._playback_order = new_track_idx

        # Append new indices to the end of the existing order (temporary approach)
        else:
            self._playback_order.extend(new_track_idx)
