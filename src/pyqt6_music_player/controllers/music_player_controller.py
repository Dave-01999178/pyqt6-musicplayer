from PyQt6.QtWidgets import QFileDialog

from pyqt6_music_player.config import FILE_DIALOG_FILTER
from pyqt6_music_player.models import MusicPlayerState
from pyqt6_music_player.views import MusicPlayerView


class PlaybackProgressController:
    """Controller for playback progress (timeline slider)."""

    def __init__(self, state: MusicPlayerState, view: MusicPlayerView):
        """
        Initialize playback progress controller.

        Args:
            state: Application state object.
            view: Main music player view.
        """
        self.state = state
        self.view = view
        self._connect_signals()

    def _connect_signals(self):
        """Connect view progress slider signals to handlers."""
        self.view.playback_progress_signals.slider_changed.connect(
            self._handle_slider_change
        )

    def _handle_slider_change(self, value: int):
        """Handle slider change event (seek in track)."""
        print(f"Progress bar moved to {value}.")

class PlaybackControlsController:
    """Controller for playback control buttons (prev, play/pause, next)."""
    def __init__(self, state: MusicPlayerState, view: MusicPlayerView):
        self.state = state
        self.view = view

        self._connect_signals()

    def _connect_signals(self):
        """Connect view playback control signals to handlers."""
        self.view.playback_control_signals.previous_clicked.connect(
            self._handle_previous
        )
        self.view.playback_control_signals.play_pause_clicked.connect(
            self._handle_play_pause
        )
        self.view.playback_control_signals.next_clicked.connect(
            self._handle_next
        )

    def _handle_previous(self):
        """Handle previous button click."""
        print("Previous button clicked.")

    def _handle_play_pause(self):
        """Handle play/pause button click."""
        print("Play/Pause button clicked.")

    def _handle_next(self):
        """Handle next button click."""
        print("Next button clicked.")


class VolumeController:
    """Controller for volume button and slider."""
    def __init__(self, state: MusicPlayerState, view: MusicPlayerView):
        self.state = state
        self.view = view

        self._connect_signals()

    def _connect_signals(self):
        """Connect volume button and slider signals to handlers."""
        self.view.volume_signals.button_clicked.connect(self._handle_button_click)
        self.view.volume_signals.slider_changed.connect(self._handle_slider_change)

    def _handle_button_click(self, is_toggled: bool):
        """
        Handle mute/unmute toggle.

        Args:
            is_toggled: True if the volume button is toggled, Otherwise, False.
        """
        self.state.volume.toggle_mute(is_toggled)

    def _handle_slider_change(self, value: int):
        """
        Handle volume slider change.

        Args:
            value: The new volume value
        """
        self.state.volume.current_volume = value


class NowPlayingMetadataController:
    """Controller for managing now-playing metadata updates."""

    def __init__(self, state: MusicPlayerState, view: MusicPlayerView):
        self.state = state
        self.view = view
        # Future: connect signals for metadata updates


class PlaylistController:
    """Controller for playlist interactions."""

    def __init__(self, state: MusicPlayerState, view: MusicPlayerView):
        self.playlist_state = state.playlist
        self.view = view

        self._connect_signals()

    def _on_add_song_click(self):
        # The `getOpenFileNames()` returns a tuple containing the list of selected filenames and
        # the name of the selected filter. We use `_` to discard the filter name.
        file_paths, _ = QFileDialog.getOpenFileNames(filter=FILE_DIALOG_FILTER)

        if not file_paths:
            return

        self.playlist_state.add_song(file_paths)

    def _connect_signals(self):
        self.view.playlist_manager_signals.add_song_button_clicked.connect(
            self._on_add_song_click
        )
