from dataclasses import dataclass

from pyqt6_music_player.core import PlaybackOrderProtocol, RepeatMode


# ==================== NAVIGATION OUTCOMES ====================
class NoTrackLoaded:
    """The playlist is empty."""

    pass


class NoActiveTrack:
    """Tracks exist but none is currently active, there's no position to move from."""

    pass


class StartBoundary:
    """Position is at the first track in the playback order."""

    pass


class EndBoundary:
    """Position is at the last track in the playback order."""

    pass


class RepeatCurrent:
    """Repeat current track."""

    pass


@dataclass(frozen=True)
class TrackIndex:
    """A valid track index was resolved."""

    index: int


type NavigationOutcome = (
        NoTrackLoaded |
        NoActiveTrack |
        TrackIndex |
        StartBoundary |
        EndBoundary |
        RepeatCurrent
)


NO_TRACK_LOADED = NoTrackLoaded()
NO_ACTIVE_TRACK = NoActiveTrack()
START_BOUNDARY = StartBoundary()
END_BOUNDARY = EndBoundary()
REPEAT_CURRENT = RepeatCurrent()


# ==================== PLAYBACK NAVIGATOR ====================
class PlaybackNavigator:
    """Resolve next and previous track indices based on the current playback mode."""

    def __init__(self, playback_order: PlaybackOrderProtocol):
        """Initialize PlaybackNavigator.

        Args:
            playback_order: Domain model maintaining the ordered list of track
                            indices, current position, and sequential or shuffled
                            mode.

        """
        self._playback_order = playback_order
        self._repeat_mode: RepeatMode = RepeatMode.OFF

    @property
    def current_position(self) -> int | None:
        """The current position in the playback order.

        Returns:
            The current position in the playback order, or None if playback
            hasn't started.

        """
        return self._playback_order.position

    # -- Public methods --
    def resolve_track_index(self) -> NavigationOutcome:
        """Resolve the track index to begin playback.

        Returns:
            ``NoTrackLoaded`` if the playlist is empty.
            ``TrackIndex`` of the selected track, or first track if none is selected.

        """
        if self._playback_order.is_empty:
            return NO_TRACK_LOADED

        if self._playback_order.position is None:
            self._playback_order.move(0)

        return TrackIndex(self._playback_order.current_track_index)

    def resolve_auto_advance_index(self) -> NavigationOutcome:
        """Resolve the next track index for autoplay.

        Returns:
            ``NoTrackLoaded`` if the playlist is empty or no track is active.
            ``RepeatCurrent`` if repeat mode is ONE.
            ``EndBoundary`` if repeat mode is OFF and the active track is last.
            ``TrackIndex`` of the next track otherwise.

        """
        if self._playback_order.is_empty:
            return NO_TRACK_LOADED

        # Repeat OFF
        if self._repeat_mode == RepeatMode.OFF:
            if self._playback_order.is_at_end:
                return END_BOUNDARY

            self._playback_order.move(1)

        # Repeat ONE
        elif self._repeat_mode == RepeatMode.ONE:
            return REPEAT_CURRENT

        # Repeat ALL
        elif self._repeat_mode == RepeatMode.ALL:
            self._playback_order.move(1, wrap=True)

        return TrackIndex(self._playback_order.current_track_index)

    def resolve_next_track_index(self) -> NavigationOutcome:
        """Resolve the next track index.

        Returns:
            ``NoTrackLoaded`` if the playlist is empty or no track is active.
            ``EndBoundary`` if repeat mode is OFF and ONE, and the active track is last.
            ``TrackIndex`` of the next track otherwise.

        """
        if self._playback_order.is_empty:
            return NO_TRACK_LOADED

        if self._playback_order.position is None:
            return NO_ACTIVE_TRACK

        # Repeat OFF and ONE
        if self._repeat_mode in {RepeatMode.OFF, RepeatMode.ONE}:
            if self._playback_order.is_at_end:
                return END_BOUNDARY

            self._playback_order.move(1)

        # Repeat ALL
        elif self._repeat_mode == RepeatMode.ALL:
            self._playback_order.move(1, wrap=True)

        return TrackIndex(self._playback_order.current_track_index)

    def resolve_previous_track_index(self) -> NavigationOutcome:
        """Resolve the previous track index.

        Returns:
            ``NoTrackLoaded`` if the playlist is empty or no track is active.
            ``StartBoundary`` if the active track is first.
            ``TrackIndex`` of the previous track otherwise.

        """
        if self._playback_order.is_empty:
            return NO_TRACK_LOADED

        if self._playback_order.position is None:
            return NO_ACTIVE_TRACK

        # Repeat OFF and ONE
        if self._repeat_mode in {RepeatMode.OFF, RepeatMode.ONE}:
            if self._playback_order.is_at_start:
                return START_BOUNDARY

            self._playback_order.move(-1)

        # Repeat ALL
        elif self._repeat_mode == RepeatMode.ALL:
            self._playback_order.move(-1, wrap=True)

        return TrackIndex(self._playback_order.current_track_index)

    def set_repeat_mode(self, repeat_mode: RepeatMode) -> None:
        """Set the repeat mode.

        Args:
            repeat_mode: The repeat mode to apply (OFF, ONE, or ALL).

        """
        self._repeat_mode = repeat_mode

    def set_shuffle_enabled(self, enabled: bool) -> None:
        """Enable or disable shuffle mode.

        Args:
            enabled: If True, enables shuffle; if False, disables it.

        """
        self._playback_order.set_shuffle_enabled(enabled)
