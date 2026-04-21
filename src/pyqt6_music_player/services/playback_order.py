import random
from dataclasses import dataclass

from pyqt6_music_player.core import OrderMode
from pyqt6_music_player.core.signals import Signal


@dataclass
class ChangeOrderResult:
    new_order: list[int]
    order_mode: OrderMode


class PlaybackOrder:
    order_changed = Signal()
    position_changed = Signal()

    def __init__(self):
        self._order: list[int] = []
        self._position: int | None = None
        self._mode: OrderMode = OrderMode.SEQUENTIAL

    # -- Properties --
    @property
    def order(self) -> list[int]:
        return self._order

    @property
    def position(self) -> int | None:
        return self._position

    @property
    def current_track_index(self) -> int | None:
        if len(self._order) == 0 or self._position is None:
            return None

        return self._order[self._position]

    # -- Public methods --
    def is_empty(self) -> bool:
        return len(self._order) == 0

    def is_at_start(self) -> bool:
        return self._position == 0

    def is_at_end(self) -> bool:
        return self._position == len(self._order) - 1

    def add_to_playback_order(self, track_indices: list[int]) -> None:
        if self._mode == OrderMode.SEQUENTIAL:
            self._rebuild_sequential_order(track_indices)
        else:
            pass  # TODO: To be implemented

    def _rebuild_sequential_order(self, track_indices: list[int]) -> None:
        # Rebuild playback order
        if not self._order:
            self._order = track_indices

        else:
            new_order_count = len(self._order) + len(track_indices)
            new_playback_order = list(range(new_order_count))

            self._order = new_playback_order

        self.order_changed.emit(ChangeOrderResult(self._order, self._mode))

        # Sync position
        if self._position is not None:
            shift = 0
            for idx in track_indices:
                if idx > self._position + shift:
                    break

                shift += 1

            self._set_position(self._position + shift)

    def _rebuild_shuffled_order(self, track_index: int):
        # Rebuild playback order
        track_index = [track_index]  # Temporary until batch removal is implemented
        if self._order == track_index:
            self._order = []
            return

        new_playback_order = []
        i = 0
        shift = 0
        for idx in self._order:
            if idx == track_index[i]:
                if i < len(track_index) - 1:
                    i += 1
                shift += 1
                continue

            new_playback_order.append(idx - shift)

        self._order = new_playback_order

        # Sync position
        pos_shift = 0
        for idx in track_index:
            if idx > self._position:
                break

            pos_shift += 1

        self._position -= pos_shift

    def move(self, step: int, wrap=False) -> None:
        if self._position is None:
            position = step

        elif self._position is not None and wrap:
            position = (self._position + step) % len(self._order)

        else:
            position = self._position + step

        self._set_position(position)

    def get_track_index_by_position(self, index_position: int) -> int | None:
        if len(self._order) == 0:
            return None

        return self._order[index_position]

    def shuffle_playback_order(self) -> None:
        if len(self._order) == 0:
            return   # TODO: Add log or notify user instead of doing nothing

        # No active track - Shuffle the entire order list
        if self._position is None:
            random.shuffle(self._order)

        # Put the active track to the front then shuffle the remaining tracks
        else:
            remaining_tracks = [
                track_idx
                for track_idx in self._order
                if track_idx != self._position
            ]
            random.shuffle(remaining_tracks)

            self._order = [self._position, *remaining_tracks]

        self._mode = OrderMode.SHUFFLED

        self.order_changed.emit(ChangeOrderResult(self._order, self._mode))

        # Sync position
        if self._position is not None:
            # Point to the active track pinned at the front
            self._set_position(0)

    def restore_playback_order(self) -> None:
        if not self._order:
            return # TODO: Add log or notify user instead of doing nothing

        position = self._order[self._position] if self._position is not None else None

        self._order.sort()

        self._mode = OrderMode.SEQUENTIAL

        self.order_changed.emit(ChangeOrderResult(self._order, self._mode))

        # Sync position
        if position is not None:
            self._set_position(position)

    def _set_position(self, index: int) -> None:
        self._position = index

        self.position_changed.emit(self._position)
