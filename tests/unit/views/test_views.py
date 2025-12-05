import pytest
from PyQt6.QtWidgets import QTableView
from pytestqt.qtbot import QtBot

from pyqt6_music_player.views import (
    IconButton,
    PlaylistDisplay,
    VolumeControls,
    VolumeLabel,
    VolumeSlider
)


# ================================================================================
# PLAYLIST VIEW
# ================================================================================
def test_playlist_widget(qtbot: QtBot, playlist_viewmodel):
    # --- Arrange ---
    playlist_view = PlaylistDisplay(playlist_viewmodel)

    qtbot.addWidget(playlist_view)

    widget_name = "playlist_window"
    widget_class = getattr(playlist_view, widget_name, None)
    expected_widget_type = QTableView

    # --- Assert ---
    assert hasattr(playlist_view, widget_name)
    assert isinstance(widget_class, expected_widget_type)


# ================================================================================
# VOLUME VIEW
# ================================================================================
@pytest.mark.parametrize("widget_name, widget_type", [
    ("volume_button", IconButton),
    ("volume_slider", VolumeSlider),
    ("volume_label", VolumeLabel),
])
def test_volume_widgets(qtbot: QtBot, volume_viewmodel, widget_name, widget_type):
    # --- Arrange ---
    volume_view = VolumeControls(volume_viewmodel)

    qtbot.addWidget(volume_view)

    widget_class = getattr(volume_view, widget_name, None)

    # --- Assert ---
    assert hasattr(volume_view, widget_name)
    assert isinstance(widget_class, widget_type)
