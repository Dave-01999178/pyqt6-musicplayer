import random

from pyqt6_music_player.core import (
    OrderChangedEvent,
    OrderMode,
    Signal,
    TrackRemovedEvent,
    TracksAddedEvent,
)


# ==================== PLAYBACK ORDER ====================
class PlaybackOrder:
    """Manages the playback order and position.

    Supports sequential and shuffled modes.
    """

    track_indices_added = Signal()
    track_index_removed = Signal()
    order_changed = Signal()

    def __init__(self):
        self._order: list[int] = []
        self._position: int | None = None
        self._mode: OrderMode = OrderMode.SEQUENTIAL

    # -- Public methods --
    @property
    def order(self) -> list[int]:
        """The playback order.

        Returns:
            List of indices referencing track positions in the playlist, or an
            empty list if the playlist is empty.

        """
        return self._order

    @property
    def position(self) -> int | None:
        """The current position in playback order.

        Returns:
            The current position in the playback order, or None if playback hasn't
            started yet.

        """
        return self._position

    @property
    def current_track_index(self) -> int | None:
        """The track's playlist index at the current position in playback order.

        Returns:
            The index at the current position, or None if the order is empty or
            playback hasn't started.

        """
        if len(self._order) == 0 or self._position is None:
            return None

        return self._order[self._position]

    @property
    def is_empty(self) -> bool:
        """Return True if the playback order is empty; Otherwise, False."""
        return len(self._order) == 0

    @property
    def is_at_start(self) -> bool:
        """Return True if the current position is at the first track."""
        return len(self._order) > 0 and self._position == 0

    @property
    def is_at_end(self) -> bool:
        """Return True if the current position is at the last track."""
        return len(self._order) > 0 and (self._position == len(self._order) - 1)

    def add_indices_to_order(self, indices: list[int]) -> TracksAddedEvent:
        """Add the given indices to playback order.

        In sequential mode, the playback order is rebuilt as a sorted range.
        In shuffled mode, the existing shuffle is preserved and the new tracks are
        appended at the end.

        Args:
            indices: List of track indices to add.

        """
        indices = indices.copy()

        if self._mode == OrderMode.SEQUENTIAL:
            self._add_indices_to_sequential_order(indices)

        else:
            self._add_indices_to_shuffled_order(indices)

        return TracksAddedEvent(self._order, self._position)

    def remove_index_from_order(self, target_index: int) -> TrackRemovedEvent:
        """Remove the target index from the playback order.

        Args:
            target_index: Target index to remove.

        """
        target_index_pos = self._order.index(target_index)
        is_active_track = target_index_pos == self._position
        is_at_end = target_index_pos == len(self._order) - 1

        # Rebuild the order list excluding the target index and decrement the remaining
        # indices by 1 if they are '>' the target index
        self._order = [
            track_idx - 1 if track_idx > target_index else track_idx
            for track_idx in self._order
            if track_idx != target_index
        ]

        self._resolve_position_after_removing_index_from_order(
            target_index_pos,
            is_active_track,
            is_at_end,
        )

        return TrackRemovedEvent(self._order, self._position, is_active_track)

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

    def set_shuffle_enabled(self, enabled: bool) -> None:
        """Enable or disable shuffle mode.

        Args:
            enabled: If True, shuffles the playback order; if False, restores the
                     playback order to its original ascending order.

        """
        if enabled:
            self._shuffle_playback_order()
        else:
            self._sort_playback_order()

        self.order_changed.emit(
            OrderChangedEvent(
                self._order,
                self._position,
            ),
        )

    # -- Protected/internal methods --
    def _shuffle_playback_order(self) -> None:
        if len(self._order) == 0:
            return

        # Shuffle the entire order list if there's no active track.
        if self._position is None:
            random.shuffle(self._order)

        # Pin the active track to the front then shuffle the remaining tracks if an
        # active track exists
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
            OrderChangedEvent(
                self._order,
                self._position,
            ),
        )

    def _sort_playback_order(self) -> None:
        if not self._order:
            return

        # Sort the order list in ascending order
        #
        # Get the original position of the active track before sorting
        # Example: pos = 1, order = [1, {0}, 2] -> pos = 0
        position = None if self._position is None else self._order[self._position]
        if position is not None:
            self._position = position

        self._order.sort()

        self._mode = OrderMode.SEQUENTIAL

    def _add_indices_to_sequential_order(self, indices: list[int]) -> None:
        order_len = len(self._order)
        new_order_count = order_len + len(indices)

        # If the order list is empty, the given indices becomes the order
        # Else, rebuild the order list (old + new)
        self._order = (indices if order_len == 0 else list(range(new_order_count)))

        # Ensure that the position is synced with the active track after adding
        if self._position is not None:
            self._resolve_position_after_adding_to_order(indices)

    def _add_indices_to_shuffled_order(self, new_indices: list[int]) -> None:
        # Find where each existing item lands after the new items are inserted.
        # New items occupy specific slots, so existing items must shift around them.
        #
        # Example:
        #
        # order = [1, 2, 0], new_indices = [0, 1, 2]
        # Position 0 → slot 3 (slots 0, 1, 2 are taken)
        # Position 1 → slot 4 (slots 0, 1, 2, 3 are taken)
        # Position 2 → slot 5 (slots 0, 1, 2, 3, 4 are taken)
        # expected shifted_positions = [3, 4, 5]
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
        # Example: order = [1, 2, 0], shifted_positions = [3, 4, 5]
        # order[0] = 1 → shifted_positions[1] = 4
        # order[1] = 2 → shifted_positions[2] = 5
        # order[2] = 0 → shifted_positions[0] = 3
        # result = [4, 5, 3], then append new_indices → [4, 5, 3, 0, 1, 2]
        self._order = [shifted_positions[i] for i in self._order]
        self._order.extend(new_indices)

    def _resolve_position_after_adding_to_order(self, new_indices: list[int]) -> None:
        # Resolves the new position after new_indices are inserted into
        # a sequential order.
        #
        # No shift needed if the position is entirely before the new indices
        if self._position < new_indices[0]:
            return

        # Shift the position by len(new_indices) if the position is entirely after the
        # new indices
        if self._position > new_indices[-1]:
            self._position = self._position + len(new_indices)
            return

        # Position falls within the range of new indices.
        # Walk each position up to and including the current one, skipping over
        # occupied slots the same way add_to_shuffled_order does.
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

    def _resolve_position_after_removing_index_from_order(
            self,
            removed_pos: int,
            is_active_track: bool,
            is_at_end: bool,
    ) -> None:
        # Position should remain None if there's no active track
        if self._position is None:
            return

        # Reset position to None if the list is now empty and the
        # sole remaining track removed was the active one
        if len(self._order) == 0 and is_active_track:
            self._position = None
            return

        # Decrement the position by 1 if the track removed was before the active track
        # or if the removed track is both the active and endmost track
        self._position = (
            self._position - 1
            if removed_pos < self._position or (is_active_track and is_at_end)
            else self._position
        )
