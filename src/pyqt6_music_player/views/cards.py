from PyQt6.QtWidgets import QFrame, QSizePolicy, QVBoxLayout

from pyqt6_music_player.views.panels import ControlButtonPanel, NowPlayingPanel, PlaybackPanel


class PlayerControlCard(QFrame):
    def __init__(self):
        super().__init__()
        self.playback_panel = PlaybackPanel()
        self.control_button_panel = ControlButtonPanel()

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("playerControlFrame")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout()
        layout.addWidget(self.playback_panel)
        layout.addWidget(self.control_button_panel)

        self.setLayout(layout)


class NowPlayingCard(QFrame):
    def __init__(self):
        super().__init__()
        self.now_playing_panel = NowPlayingPanel()

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("nowPlayingFrame")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout()
        layout.addWidget(self.now_playing_panel)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)
