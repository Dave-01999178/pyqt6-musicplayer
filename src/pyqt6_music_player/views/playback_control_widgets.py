"""
Custom PyQt6 button widgets for consistent UI components.

This module provides button widgets for managing music playback, such as play/pause,
next/previous track, and repeat functionality.
"""
from pathlib import Path

from pyqt6_music_player.config import (
    NAVIGATION_BUTTON_ICON_SIZE,
    NAVIGATION_BUTTON_SIZE,
    NEXT_ICON_PATH,
    PLAY_ICON_PATH,
    PLAY_PAUSE_BUTTON_ICON_SIZE,
    PLAY_PAUSE_BUTTON_SIZE,
    PREV_ICON_PATH,
    REPEAT_ICON_PATH,
    REPLAY_ICON_PATH
)
from pyqt6_music_player.views import IconButton


class ReplayButton(IconButton):
    """Replay button."""
    def __init__(
            self,
            icon: Path = REPLAY_ICON_PATH,
            icon_size: tuple[int, int] = NAVIGATION_BUTTON_ICON_SIZE,
            widget_size: tuple[int, int] = NAVIGATION_BUTTON_SIZE,
            object_name: str | None = None
    ):
        """
        Initializes ReplayButton instance.

        Args:
            icon: Icon image path. Defaults to 'replay' icon.
            icon_size: Width and height of the icon.
                       Defaults to `NAVIGATION_BUTTON_ICON_SIZE` (15, 15).
            widget_size: ReplayButton instance width and height.
                         Defaults to `NAVIGATION_BUTTON_SIZE` (30, 30).
            object_name: ReplayButton instance object name, useful for QSS styling.
                         Defaults to None.
        """
        super().__init__(
            icon_path=icon,
            icon_size=icon_size,
            widget_size=widget_size,
            object_name=object_name,
        )


class PreviousButton(IconButton):
    """Previous button."""
    def __init__(
            self,
            icon: Path = PREV_ICON_PATH,
            icon_size: tuple[int, int] = NAVIGATION_BUTTON_ICON_SIZE,
            widget_size: tuple[int, int] = NAVIGATION_BUTTON_SIZE,
            object_name: str | None = None
    ):
        """
        Initializes PreviousButton instance.

        Args:
            icon: Icon image path. Defaults to 'previous' icon.
            icon_size: Width and height of the icon.
                       Defaults to `NAVIGATION_BUTTON_ICON_SIZE` (15, 15).
            widget_size: PreviousButton instance width and height.
                         Defaults to `NAVIGATION_BUTTON_SIZE` (30, 30).
            object_name: PreviousButton instance object name, useful for QSS styling.
                         Defaults to None.
        """
        super().__init__(
            icon_path=icon,
            icon_size=icon_size,
            widget_size=widget_size,
            object_name=object_name,
        )


class PlayPauseButton(IconButton):
    """A custom play/pause button."""
    def __init__(
            self,
            icon: Path = PLAY_ICON_PATH,
            icon_size: tuple[int, int] = PLAY_PAUSE_BUTTON_ICON_SIZE,
            widget_size: tuple[int, int] = PLAY_PAUSE_BUTTON_SIZE,
            object_name: str | None = "playPauseBtn"
    ):
        """
        Initializes PlayPauseButton instance.

        Args:
            icon: Icon image path. Defaults to 'play' icon.
            icon_size: Width and height of the icon.
                       Defaults to `PLAY_PAUSE_BUTTON_ICON_SIZE` (25, 25).
            widget_size: PlayPauseButton instance width and height.
                         Defaults to `PLAY_PAUSE_BUTTON_SIZE` (40, 40).
            object_name: PlayPauseButton instance object name, useful for QSS styling.
                         Defaults to None.
        """
        super().__init__(
            icon_path=icon,
            icon_size=icon_size,
            widget_size=widget_size,
            object_name=object_name
        )


class NextButton(IconButton):
    """Next button."""
    def __init__(
            self,
            icon: Path = NEXT_ICON_PATH,
            icon_size: tuple[int, int] = NAVIGATION_BUTTON_ICON_SIZE,
            widget_size: tuple[int, int] = NAVIGATION_BUTTON_SIZE,
            object_name: str | None = None
    ):
        """
        Initializes NextButton instance.

        Args:
            icon: Icon image path. Defaults to 'next' icon.
            icon_size: Width and height of the icon.
                       Defaults to `NAVIGATION_BUTTON_ICON_SIZE` (15, 15).
            widget_size: NextButton instance width and height.
                         Defaults to `NAVIGATION_BUTTON_SIZE` (30, 30).
            object_name: NextButton instance object name, useful for QSS styling.
                         Defaults to None.
        """
        super().__init__(
            icon_path=icon,
            icon_size=icon_size,
            widget_size=widget_size,
            object_name=object_name,
        )


class RepeatButton(IconButton):
    """Repeat button."""
    def __init__(
            self,
            icon: Path = REPEAT_ICON_PATH,
            icon_size: tuple[int, int] = NAVIGATION_BUTTON_ICON_SIZE,
            widget_size: tuple[int, int] = NAVIGATION_BUTTON_SIZE,
            object_name: str | None = None
    ):
        """
        Initializes RepeatButton instance.

        Args:
            icon: Icon image path. Defaults to 'repeat' icon.
            icon_size: Width and height of the icon.
                       Defaults to `NAVIGATION_BUTTON_ICON_SIZE` (15, 15).
            widget_size: RepeatButton instance width and height.
                         Defaults to `NAVIGATION_BUTTON_SIZE` (30, 30).
            object_name: RepeatButton instance object name, useful for QSS styling.
                         Defaults to None.
        """
        super().__init__(
            icon_path=icon,
            icon_size=icon_size,
            widget_size=widget_size,
            object_name=object_name,
        )
