from PyQt6.QtWidgets import QFileDialog

from pyqt6_music_player.config import FILE_DIALOG_FILTER
from pyqt6_music_player.models import MusicPlayerState
from pyqt6_music_player.views import MusicPlayerView


class PlaybackProgressController:
    """Manages the interaction between playback slider and backend logic (models)."""
    def __init__(self, app_state: MusicPlayerState, view: MusicPlayerView):
        """
        Initialize the controller.

        Args:
            app_state: The app's state object.
            view: The app's main view.
        """
        self.state = app_state
        self.view = view
        self._connect_signals()

    def _connect_signals(self):
        """Connect playback slider signal to slider change event handler."""
        self.view.playback_progress_signals.slider_changed.connect(
            self._handle_slider_change
        )

    def _handle_slider_change(self, value: int):
        """Handle slider change event (seeking)."""
        print(f"Progress bar moved to {value}.")


class PlaybackControlsController:
    """Manages the interaction between playback control buttons and backend logic (models)."""
    def __init__(self, app_state: MusicPlayerState, view: MusicPlayerView):
        """
        Initialize the controller.

        Args:
            app_state: The app's state object.
            view: The app's main view.
        """
        self.state = app_state
        self.view = view

        self._connect_signals()

    def _connect_signals(self):
        """Connect playback control buttons signal to their event handlers."""
        self.view.playback_control_signals.previous_clicked.connect(
            self._handle_previous_button_click
        )
        self.view.playback_control_signals.play_pause_clicked.connect(
            self._handle_play_pause_button_click
        )
        self.view.playback_control_signals.next_clicked.connect(
            self._handle_next_button_click
        )

    def _handle_previous_button_click(self):
        """Handle previous button click event."""
        print("Previous button clicked.")

    def _handle_play_pause_button_click(self):
        """Handle play/pause button click event."""
        print("Play/Pause button clicked.")

    def _handle_next_button_click(self):
        """Handle next button click event."""
        print("Next button clicked.")


class VolumeController:
    """Manages the interaction between volume widgets and backend logic (models)."""
    def __init__(self, app_state: MusicPlayerState, view: MusicPlayerView):
        """
        Initialize the controller.

        Args:
            app_state: The app's state object.
            view: The app's main view.
        """
        self.state = app_state
        self.view = view

        self._connect_signals()

    def _connect_signals(self):
        """Connect volume widgets signal to their event handlers."""
        self.view.volume_signals.button_clicked.connect(self._handle_button_click)
        self.view.volume_signals.slider_changed.connect(self._handle_slider_change)

    def _handle_button_click(self, is_toggled: bool):
        """
        Handle volume button toggle event (mute/unmute).

        Args:
            is_toggled: True if the volume button is toggled/muted, Otherwise, False.
        """
        self.state.volume.toggle_mute(is_toggled)

    def _handle_slider_change(self, new_volume: int):
        """
        Handle volume slider change event (seeking).

        Args:
            new_volume: The new volume value after seeking.
        """
        self.state.volume.current_volume = new_volume


class NowPlayingMetadataController:
    """Controller for managing now-playing metadata updates."""

    def __init__(self, app_state: MusicPlayerState, view: MusicPlayerView):
        self.state = app_state
        self.view = view
        # Future: connect signals for metadata updates


class PlaylistController:
    """Manages the interaction between playlist widgets and backend logic (models)."""
    def __init__(self, app_state: MusicPlayerState, view: MusicPlayerView):
        """
        Initialize the controller.

        Args:
            app_state: The app's state object.
            view: The app's main view.
        """
        self.playlist_state = app_state.playlist
        self.view = view

        self._connect_signals()

    def _connect_signals(self):
        """Connect playlist widgets signal to their event handlers."""
        self.view.playlist_manager_signals.add_song_button_clicked.connect(
            self._on_add_song_click
        )

    def _on_add_song_click(self):
        """Handle add song button click event."""
        # The `getOpenFileNames()` returns a tuple containing the list of selected filenames and
        # the name of the selected filter. We use `_` to discard the filter name.
        file_paths, _ = QFileDialog.getOpenFileNames(filter=FILE_DIALOG_FILTER)

        if not file_paths:
            return

        self.playlist_state.add_song(file_paths)
