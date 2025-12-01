import pytest
from pytestqt.qtbot import QtBot

from pyqt6_music_player.views import IconButton, VolumeControls, VolumeLabel, VolumeSlider


@pytest.mark.parametrize("widget_name, widget_type", [
    ("volume_button", IconButton),
    ("volume_slider", VolumeSlider),
    ("volume_label", VolumeLabel),
])
def test_volume_view(qtbot: QtBot, volume_viewmodel, widget_name, widget_type):
    # --- Arrange ---
    volume_view = VolumeControls(volume_viewmodel)

    qtbot.addWidget(volume_view)

    # --- Assert ---
    widget = getattr(volume_view, widget_name, None)

    assert hasattr(volume_view, widget_name)
    assert isinstance(widget, widget_type)
