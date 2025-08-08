from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QWidget

from pyqt6_music_player.config import PREV_ICON_PATH, PREV_ICON_PRESSED_PATH, BUTTON_SIZE_SMALL, NEXT_ICON_PATH, \
    NEXT_ICON_PRESSED_PATH, REPLAY_ICON_PATH, REPLAY_ICON_PRESSED_PATH
from pyqt6_music_player.views.buttons import (
    PlayPauseButton,
    IconButton,
)
from pyqt6_music_player.views.labels import (
    AlbumArtLabel,
    ElapsedTimeLabel,
    PerformerLabel,
    SongTitleLabel,
    TotalDurationLabel,
)
from pyqt6_music_player.views.sliders import PlaybackProgressBar
from pyqt6_music_player.views.volume import VolumeToggle


class NowPlayingPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.song_title = SongTitleLabel()
        self.performer_label = PerformerLabel()
        self.album_art = AlbumArtLabel()

        layout = QVBoxLayout()

        layout.addWidget(self.album_art, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.song_title)
        layout.addWidget(self.performer_label)

        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(5)


        self.setLayout(layout)


class PlaybackPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.playback_progress = PlaybackProgressBar()
        self.elapsed_time = ElapsedTimeLabel()
        self.total_duration = TotalDurationLabel()

        layout = QGridLayout()

        layout.addWidget(self.playback_progress, 0, 0, 1, 4)
        layout.addWidget(self.elapsed_time, 1, 0, 1, 1)
        layout.addWidget(self.total_duration, 1, 3, 1, 1)

        layout.setSpacing(0)

        self.setLayout(layout)


class ControlButtonPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.buttons = {
            "replay": {
                "widget": IconButton(REPLAY_ICON_PATH, BUTTON_SIZE_SMALL, REPLAY_ICON_PRESSED_PATH),
                "signal": "replay_pressed"
            },
            "prev": {
                "widget": IconButton(PREV_ICON_PATH, BUTTON_SIZE_SMALL, PREV_ICON_PRESSED_PATH),
                "signal": "prev_pressed"
            },
            "play_pause": {
                "widget": PlayPauseButton(),
                "signal": "play_pause_pressed"
            },
            "next": {
                "widget": IconButton(NEXT_ICON_PATH, BUTTON_SIZE_SMALL, NEXT_ICON_PRESSED_PATH),
                "signal": "next_pressed"
            },
            "volume": {
                "widget": VolumeToggle(),
                "signal": "volume_pressed"
            }
        }

        layout = QHBoxLayout()
        for data in self.buttons.values():
            layout.addWidget(data["widget"])

        self.setLayout(layout)
