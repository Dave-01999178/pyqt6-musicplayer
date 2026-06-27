from dataclasses import dataclass


@dataclass
class OrderChangedEvent:
    """Emitted by PlaybackOrder after the order is shuffled or sorted."""

    order: list[int]
    position: int | None


@dataclass
class TracksAddedEvent:
    """Emitted by PlaybackOrder after tracks are added."""

    order: list[int]
    position: int | None


@dataclass
class TrackRemovedEvent:
    """Emitted by PlaybackOrder after a track is removed."""

    order: list[int]
    position: int | None
    active_track_removed: bool
