import pytest
from pytestqt.qtbot import QtBot

from pyqt6_music_player.views import (
    PlaybackControls,
    PlaylistDisplay,
    VolumeControls,
)

# ================================================================================
# PLAYLIST VIEW
# ================================================================================
@pytest.mark.parametrize("widget_name", [
    "replay_button",
    "previous_button",
    "play_pause_button",
    "next_button",
    "repeat_button"
])
def test_playback_widgets(qtbot: QtBot, playback_viewmodel, widget_name):
    # --- Arrange ---
    playback_view = PlaybackControls(playback_viewmodel)

    qtbot.addWidget(playback_view)

    # --- Assert ---
    assert hasattr(playback_view, widget_name)


# ================================================================================
# PLAYLIST VIEW
# ================================================================================
def test_playlist_widgets(qtbot: QtBot, playlist_viewmodel):
    # --- Arrange ---
    playlist_view = PlaylistDisplay(playlist_viewmodel)

    qtbot.addWidget(playlist_view)

    widget_name = "playlist_window"

    # --- Assert ---
    assert hasattr(playlist_view, widget_name)


# ================================================================================
# VOLUME VIEW
# ================================================================================
@pytest.mark.parametrize("widget_name", ["volume_button", "volume_slider", "volume_label"])
def test_volume_widgets(qtbot: QtBot, volume_viewmodel, widget_name):
    # --- Arrange ---
    volume_view = VolumeControls(volume_viewmodel)

    qtbot.addWidget(volume_view)

    # --- Assert ---
    assert hasattr(volume_view, widget_name)
