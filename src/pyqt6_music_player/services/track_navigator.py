from dataclasses import dataclass

from pyqt6_music_player.core import RepeatMode, ShuffleMode
from pyqt6_music_player.services import PlaybackOrder


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

    def __init__(self, playback_order: PlaybackOrder):
        """Initialize TrackNavigator.
        """
        self._playback_order = playback_order
        self._repeat_mode: RepeatMode = RepeatMode.OFF
        self._shuffle_mode = ShuffleMode.OFF

    # -- Public methods --
    def resolve_track_index(self) -> NavigationOutcome:
        """Resolve the track index to begin playback.

        Returns:
            ``NoTrackLoaded`` if the playlist is empty.
            ``TrackIndex`` of the selected track, or first track if none is selected.
        """
        if self._playback_order.is_empty():
            return NoTrackLoaded()

        if self._playback_order.is_at_end():
            return EndBoundary()

        # TODO: Default to first track if none is selected
        if self._playback_order.position is not None:
            pass

        track_index = 0

        self._playback_order.move(track_index)

        return TrackIndex(track_index)

    def resolve_auto_advance_index(self) -> NavigationOutcome:
        """Resolve the next track index for autoplay.

        Returns:
            ``NoTrackLoaded`` if the playlist is empty or no track is active.
            ``RepeatCurrent`` if repeat mode is ONE.
            ``EndBoundary`` if repeat mode is OFF and the current track is last.
            ``TrackIndex`` of the next track otherwise.

        """
        if self._playback_order.is_empty():
            return NoTrackLoaded()

        # Repeat OFF
        if self._repeat_mode == RepeatMode.OFF:
            if self._playback_order.is_at_end():
                return EndBoundary()

            self._playback_order.move(1)

        # Repeat ONE
        elif self._repeat_mode == RepeatMode.ONE:
            return RepeatCurrent()

        # Repeat ALL
        else:
            self._playback_order.move(1, wrap=True)

        return TrackIndex(self._playback_order.current_track_index)

    def resolve_next_track_index(self) -> NavigationOutcome:
        """Resolve the next track index.

        Returns:
            ``NoTrackLoaded`` if the playlist is empty or no track is active.
            ``EndBoundary`` if repeat mode is OFF and ONE, and the current track is last.
            ``TrackIndex`` of the next track otherwise.

        """
        if self._playback_order.is_empty():
            return NoTrackLoaded()

        if self._repeat_mode in {RepeatMode.OFF, RepeatMode.ONE}:
            if self._playback_order.is_at_end():
                return EndBoundary()

            self._playback_order.move(1)

        else:
            self._playback_order.move(1, wrap=True)

        return TrackIndex(self._playback_order.current_track_index)

    def resolve_previous_track_index(self) -> NavigationOutcome:
        """Resolve the previous track index.

        Returns:
            ``NoTrackLoaded`` if the playlist is empty or no track is active.
            ``StartBoundary`` if the current track is first.
            ``TrackIndex`` of the previous track otherwise.

        """
        if self._playback_order.is_empty():
            return NoTrackLoaded()

        if self._repeat_mode in {RepeatMode.OFF, RepeatMode.ONE}:
            if self._playback_order.is_at_start():
                return StartBoundary()

            self._playback_order.move(-1)

        else:
            self._playback_order.move(-1, wrap=True)

        return TrackIndex(self._playback_order.current_track_index)

    def set_repeat_mode(self, repeat_mode: RepeatMode) -> None:
        """Set the repeat mode.

        Args:
            repeat_mode: The repeat mode to apply (OFF, ONE, or ALL).

        """
        self._repeat_mode = repeat_mode

    def set_shuffle_mode(self, shuffle_mode: ShuffleMode) -> None:
        """Set the shuffle mode.

        Args:
            shuffle_mode: The shuffle mode to apply (ON or OFF).

        """
        self._shuffle_mode = shuffle_mode

        if self._shuffle_mode == ShuffleMode.OFF:
            self._playback_order.restore_playback_order()
        else:
            self._playback_order.shuffle_playback_order()
