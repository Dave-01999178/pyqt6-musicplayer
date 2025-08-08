from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from pyqt6_music_player.config import BUTTON_SIZE_SMALL, VOLUME_HIGH_ICON_PATH
from pyqt6_music_player.views.sliders import VolumeSlider


class VolumeToggle(QPushButton):
    def __init__(self):
        super().__init__()
        self.setFixedSize(*BUTTON_SIZE_SMALL)
        self.setIcon(QIcon(str(VOLUME_HIGH_ICON_PATH)))
        self.setCheckable(True)
        self.volume_popup = VolumePopUp()

        self.clicked.connect(self.toggle_volume_popup)

    def toggle_volume_popup(self):
        if not self.isChecked():
            self.volume_popup.hide()
        else:
            self.show_volume_popup()

    def show_volume_popup(self):
        # Find global position of the button
        button_pos = self.mapToGlobal(QPoint(0, 0))
        popup_width = self.volume_popup.width()
        popup_height = self.volume_popup.height()

        # Position popup above the button, centered horizontally
        x = button_pos.x() + self.width() // 2 - popup_width // 2
        y = button_pos.y() - popup_height - 5  # 5px spacing

        self.volume_popup.move(x, y)
        self.volume_popup.show()


class VolumePopUp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TintedBackground)

        self.slider = VolumeSlider()

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(self.slider, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        self.setFixedSize(40, 120)
