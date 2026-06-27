from typing import Protocol

from pyqt6_music_player.track import Track

from .playback_order_events import TrackRemovedEvent, TracksAddedEvent
from .signals import Signal


class PlaybackOrderProtocol(Protocol):
    order_changed: Signal

    @property
    def is_at_start(self) -> bool: ...

    @property
    def is_at_end(self) -> bool: ...

    @property
    def is_empty(self) -> bool: ...

    @property
    def position(self) -> int | None: ...

    @property
    def current_track_index(self) -> int | None: ...

    def add_indices_to_order(self, indices: list[int]) -> TracksAddedEvent: ...

    def remove_index_from_order(self, index: int) -> TrackRemovedEvent: ...

    def move(self, step: int, wrap: bool = False) -> None: ...

    def set_shuffle_enabled(self, enabled: bool) -> None: ...


class PlaylistServiceProtocol(Protocol):
    active_track_removed: Signal

    def get_track_by_index(self, index: int) -> Track: ...
