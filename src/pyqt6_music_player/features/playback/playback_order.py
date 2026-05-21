import random
from dataclasses import dataclass

from pyqt6_music_player.core import OrderMode, Signal


@dataclass
class TracksAddedState:
    order: list[int]
    position: int | None


@dataclass
class TrackRemovedState:
    order: list[int]
    position: int | None
    active_track_removed: bool


@dataclass
class OrderChangedState:
    order: list[int]
    mode: OrderMode
    position: int | None


class PlaybackOrder:
    """Manages the playback order and current position for a track list.

    Supports sequential and shuffled modes. Emits `order_changed` when the
    order is rebuilt or sorted/shuffled.
    """

    track_indices_added = Signal()
    track_index_removed = Signal()
    order_changed = Signal()

    def __init__(self):
        """Initialize PlaybackOrder instance."""
        self._order: list[int] = []
        self._position: int | None = None
        self._mode: OrderMode = OrderMode.SEQUENTIAL

    # -- Properties --
    @property
    def order(self) -> list[int]:
        """The current playback order as a list of track indices."""
        return self._order

    @property
    def position(self) -> int | None:
        """The current position in the playback order.

        Returns:
            The current position in the playback order, or None if playback hasn't
            started.

        """
        return self._position

    @property
    def current_track_index(self) -> int | None:
        """The track index at the current position.

        Returns:
            The track index at the current position, or None if the order is empty
            or playback hasn't started.

        """
        if len(self._order) == 0 or self._position is None:
            return None

        return self._order[self._position]

    # -- Public methods --
    def is_empty(self) -> bool:
        """Return True if the playback order contains no tracks."""
        return len(self._order) == 0

    def is_at_start(self) -> bool:
        """Return True if the current position is at the first track."""
        return self._position == 0

    def is_at_end(self) -> bool:
        """Return True if the current position is at the last track."""
        return self._position == len(self._order) - 1

    def add_indices_to_order(self, track_indices: list[int]) -> TracksAddedState:
        """Add tracks to the playback order, preserving the current mode.

        In sequential mode the order is rebuilt as a sorted range.
        In shuffled mode the existing shuffle is preserved and the new
        tracks are appended at the end.

        Args:
            track_indices: Ascending list of track indices to add.

        """
        track_indices = track_indices.copy()

        if self._mode == OrderMode.SEQUENTIAL:
            self._add_indices_to_sequential_order(track_indices)
            # Keep the position in sync after adding
            if self._position is not None:
                self._resolve_position_after_adding_to_order(track_indices)

        else:
            self._add_indices_to_shuffled_order(track_indices)

        return TracksAddedState(self._order, self._position)

    def remove_index_from_order(self, index: int) -> TrackRemovedState:
        idx_pos = self._order.index(index)
        is_active_track = self._position == idx_pos

        self._order = [
            track_idx - 1 if track_idx > index else track_idx
            for track_idx in self._order
            if track_idx != index
        ]

        self._resolve_position_after_removing_index_from_order(idx_pos)

        return TrackRemovedState(self._order, self._position, is_active_track)

    def move(self, step: int, wrap: bool = False) -> None:
        """Advance the playback position by the given step.

        Args:
            step:  Number of positions to move. Use negative values to move backward.
            wrap:  If True, wraps around at the boundaries of the order.

        """
        if self._position is None:
            position = step

        elif self._position is not None and wrap:
            position = (self._position + step) % len(self._order)

        else:
            position = self._position + step

        self._position = position

    def shuffle_playback_order(self) -> None:
        """Shuffle the playback order.

        If playback is active, the current track is pinned to the front
        and the remaining tracks are shuffled behind it.
        """
        if len(self._order) == 0:
            return   # TODO: Add log or notify user instead of doing nothing

        # No active track - Shuffle the entire order list
        if self._position is None:
            random.shuffle(self._order)

        # Put the active track to the front then shuffle the remaining tracks
        else:
            active_track_index = self._order[self._position]
            remaining_tracks = [
                track_idx
                for track_idx in self._order
                if track_idx != self._order[self._position]
            ]
            random.shuffle(remaining_tracks)

            self._order = [active_track_index, *remaining_tracks]

            # Point to the active track pinned at the front
            self._position = 0

        self._mode = OrderMode.SHUFFLED

        self.order_changed.emit(
            OrderChangedState(
                self._order,
                self._mode,
                self._position,
            ),
        )

    def restore_playback_order(self) -> None:
        """Restore the playback order to sequential (sorted) order."""
        if not self._order:
            return # TODO: Add log or notify user instead of doing nothing

        # Point to the original position of the active track
        #
        # order = [1, 0, 2], pos = 1 -> order = [0, 1, 2], pos = 0
        position = None if self._position is None else self._order[self._position]

        self._order.sort()

        self._mode = OrderMode.SEQUENTIAL

        if position is not None:
            self._position = position

        self.order_changed.emit(
            OrderChangedState(
                self._order,
                self._mode,
                self._position,
            ),
        )

    # -- Protected/internal methods --
    def _add_indices_to_sequential_order(self, new_indices: list[int]) -> None:
        # REBUILD SEQUENTIAL ORDER (OLD + NEW)
        old_order_count = len(self._order)
        new_order_count = old_order_count + len(new_indices)

        # Directly assign the `new_indices` if `self._order` is empty to avoid
        # creating list
        self._order = (
            new_indices if old_order_count == 0 else list(range(new_order_count))
        )

    def _add_indices_to_shuffled_order(self, new_indices: list[int]) -> None:
        # Find where each existing item lands after the new items are inserted.
        # New items occupy specific slots, so existing items must shift around them.
        #
        # Example:
        #
        # order=[1,0], new_indices=[0,1,2]
        # Position 0 → slot 3 (slots 0,1,2 are taken)
        # Position 1 → slot 4 (slots 0,1,2,3 are taken)
        # expected shifted_positions=[3, 4]
        occupied_slots = set(new_indices)
        shifted_positions = []
        shift = 0
        for position in range(len(self._order)):
            candidate = position + shift
            while candidate in occupied_slots:
                shift += 1
                candidate += 1

            shifted_positions.append(candidate)
            occupied_slots.add(candidate)

        # Apply the original shuffle on top of the shifted positions.
        # order[i] tells us which original position maps to slot i in the output,
        # so we look up where that position landed after shifting.
        #
        # Example: order=[1,0], shifted_positions=[3,4]
        # order[0]=1 → shifted_positions[1]=4
        # order[1]=0 → shifted_positions[0]=3
        # result=[4, 3], then append new_indices → [4, 3, 0, 1, 2]
        self._order = [shifted_positions[i] for i in self._order]
        self._order.extend(new_indices)

    def _resolve_position_after_adding_to_order(self, new_indices: list[int]) -> None:
        # Resolves the new position index after new_indices are inserted into
        # a sequential order.
        #
        # No shift needed — position is entirely before the new indices
        if self._position < new_indices[0]:
            return

        # Full shift — position is entirely after the new indices
        if self._position > new_indices[-1]:
            self._position = self._position + len(new_indices)
            return

        # Partial shift — position falls within the range of new indices.
        # Walk each position up to and including the current one, skipping
        # over occupied slots the same way add_to_shuffled_order does.
        occupied = set(new_indices)
        shift = 0
        candidate = self._position
        for pos in range(self._position + 1):
            candidate = pos + shift
            while candidate in occupied:
                candidate += 1
                shift += 1

            occupied.add(candidate)

        self._position = candidate

    def _resolve_position_after_removing_index_from_order(self, index: int) -> None:
        # No active track - position should remain `None`
        if self._position is None:
            return

        # Only track removed - position should become `None`
        if len(self._order) == 0 and index == 0:
            # Set the position to `None` if it is an active track
            if self._position is not None:
                self._position = None
            return

        # Track removed before or after the active track - shift the position down by 1
        # if the track removed was before the active track; else, same position
        self._position = (
            self._position - 1
            if index < self._position
            else self._position
        )
