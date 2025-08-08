from pyqt6_music_player.views.main_view import MusicPlayerView


class MusicPlayerController:

    def __init__(self, view: MusicPlayerView):
        self.view = view

        self._connect_signals()

    def _handle_replay_button(self):
        print("Replay button clicked.")

    def _handle_prev_button(self):
        print("Prev button clicked.")

    def _handle_play_pause_button(self):
        print("PlayPause button clicked.")

    def _handle_next_button(self):
        print("Next button clicked.")

    def _handle_volume_button(self):
        print("Volume button clicked.")

    def _connect_signals(self):
        btn_panel = self.view.player_control_card.control_button_panel

        for name, data in btn_panel.buttons.items():
            signal_name = data["signal"]
            handler_name = f"_handle_{name}_button"

            if not hasattr(self, handler_name):
                raise AttributeError(
                    f"No handler method '{handler_name}' found in {self.__class__.__name__}"
                )

            signal_obj = getattr(self.view, signal_name)
            handler = getattr(self, handler_name)
            signal_obj.connect(handler)
