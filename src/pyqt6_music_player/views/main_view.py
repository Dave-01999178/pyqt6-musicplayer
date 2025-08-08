from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QListWidget, QHBoxLayout, QTableWidget, QTableWidgetItem

from pyqt6_music_player.views.cards import NowPlayingCard, PlayerControlCard
from src.pyqt6_music_player.config import APP_DEFAULT_SIZE, APP_TITLE


class MusicPlayerView(QWidget):
    replay_pressed = pyqtSignal()
    prev_pressed = pyqtSignal()
    play_pause_pressed = pyqtSignal()
    next_pressed = pyqtSignal()
    volume_pressed = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.now_playing_card = NowPlayingCard()
        self.player_control_card = PlayerControlCard()

        self._app_configuration()
        self._setup_ui()
        self._connect_signals()

    def _app_configuration(self):
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(*APP_DEFAULT_SIZE)
        self.resize(*APP_DEFAULT_SIZE)

    def _setup_ui(self):
        main_layout = QVBoxLayout()

        main_layout.addWidget(self.now_playing_card, stretch=3)
        main_layout.addWidget(self.player_control_card, stretch=1)

        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(main_layout)


    def _connect_signals(self):
        btn_panel = self.player_control_card.control_button_panel

        for data in btn_panel.buttons.values():
            widget = data["widget"]
            signal_name = data["signal"]

            if not hasattr(self, signal_name):
                raise AttributeError(
                    f"Signal {signal_name} is not defined in {self.__class__.__name__}"
                )

            signal_obj = getattr(self, signal_name)
            widget.clicked.connect(signal_obj)
