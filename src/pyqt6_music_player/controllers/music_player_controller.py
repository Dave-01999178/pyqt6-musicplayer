from PyQt6.QtWidgets import QFileDialog

from pyqt6_music_player.constant import FILE_DIALOG_FILTER
from pyqt6_music_player.models import PlaylistModel, VolumeSettings
from pyqt6_music_player.views import PlayerbarView, PlaylistManagerView


class PlaylistManagerController:
    def __init__(self, playlist_model: PlaylistModel, playlist_manager_view: PlaylistManagerView):
        """
        Initialize PlaylistManagerController instance.

        Args:
            playlist_model: The app's playlist model.
            playlist_manager_view: The playlist manager subview.
        """
        self.playlist_state = playlist_model
        self.playlist_manager_view = playlist_manager_view

        self._connect_signals()

    def _connect_signals(self):
        self.playlist_manager_view.add_song_button_clicked.connect(self._on_add_song_click)

    def _on_add_song_click(self):
        # The `getOpenFileNames()` returns a tuple containing the list of selected filenames and
        # the name of the selected filter. We use `_` to discard the filter name.
        file_paths, _ = QFileDialog.getOpenFileNames(filter=FILE_DIALOG_FILTER)

        if not file_paths:
            return

        self.playlist_state.add_song(file_paths)


class PlaybackProgressController:
    def __init__(self, player_bar_view: PlayerbarView):
        """
        Initialize PlaybackProgressController instance.

        Args:
            player_bar_view: The player bar subview.
        """
        self.view = player_bar_view

        self._connect_signals()

    def _connect_signals(self):
        self.view.playback_slider_moved.connect(self._handle_slider_change)

    # Placeholder handler to confirm widget to controller connection.
    def _handle_slider_change(self, value: int):
        print(f"Progress bar moved to {value}.")


class PlaybackControlController:
    """Manages the interaction between playback control buttons and backend logic (models)."""
    def __init__(self, player_bar_view: PlayerbarView):
        """
        Initialize the controller.
        """
        self.view = player_bar_view

        self._connect_signals()

    def _connect_signals(self):
        """Connect playback control buttons signal to their event handlers."""
        self.view.replay_button_clicked.connect(self._handle_replay_button_click)
        self.view.previous_button_clicked.connect(self._handle_previous_button_click)
        self.view.play_pause_button_clicked.connect(self._handle_play_pause_button_click)
        self.view.next_button_clicked.connect(self._handle_next_button_click)
        self.view.repeat_button_clicked.connect(self._handle_repeat_button_clicked)

    # Placeholder handlers to confirm widget to controller connection.
    def _handle_replay_button_click(self):
        print("Replay button clicked.")

    def _handle_previous_button_click(self):
        """Handle previous button click event."""
        print("Previous button clicked.")

    def _handle_play_pause_button_click(self):
        """Handle play/pause button click event."""
        print("Play/Pause button clicked.")

    def _handle_next_button_click(self):
        """Handle next button click event."""
        print("Next button clicked.")

    def _handle_repeat_button_clicked(self):
        print("Repeat button clicked.")


class VolumeControlController:
    """Manages the interaction between volume widgets and backend logic (models)."""
    def __init__(self, volume_settings: VolumeSettings, player_bar_view: PlayerbarView):
        """
        Initialize the controller.
        """
        self.volume_settings = volume_settings
        self.view = player_bar_view

        self._connect_signals()

    def _connect_signals(self):
        """Connect volume widgets signal to their event handlers."""
        # Widget actions to VolumeSettings updates.
        self.view.volume_button_toggled.connect(self._handle_button_click)
        self.view.volume_slider_moved.connect(self._handle_slider_change)

        # VolumeSettings changes to widget updates.
        self.volume_settings.volume_changed.connect(self._update_volume_widgets)

    def _handle_button_click(self, is_toggled: bool):
        """
        Handle volume button toggle event (mute/unmute).

        Args:
            is_toggled: True if the volume button is toggled/muted; Otherwise, False.
        """
        self.volume_settings.toggle_mute(is_toggled)

    def _handle_slider_change(self, new_volume: int):
        """
        Handle volume slider change event (seeking).

        Args:
            new_volume: The new volume value after seeking.
        """
        self.volume_settings.current_volume = new_volume

    def _update_volume_widgets(self, new_volume):
        volume_widgets = self.view.volume_controls

        volume_widgets.volume_button.update_button_icon(new_volume)
        volume_widgets.volume_slider.setValue(new_volume)
        volume_widgets.volume_label.setText(str(new_volume))
