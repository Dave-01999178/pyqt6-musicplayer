import pytest
from PyQt6.QtCore import QItemSelectionModel, QModelIndex
from pytest_mock import MockerFixture
from pytestqt.qtbot import QtBot

from pyqt6_music_player.views import PlaylistDisplay

# ================================================================================
# SELECT ITEM FEATURE INTEGRATION TEST SUMMARY
# 1. View to ViewModel
#    - Playlist table row click event should call its corresponding viewmodel commands. (Done)
#
# 2. ViewModel to Model
#    - Viewmodel commands should pass the data from view to corresponding
#      model setter.
# ================================================================================
#
# Test: Playlist table row click event should call its corresponding viewmodel commands.
def test_view_calls_corresponding_viewmodel_command_on_table_row_click(
        qtbot: QtBot,
        mocker: MockerFixture,
        populate_playlist,
        playlist_viewmodel
):
    # --- Arrange ---
    spy = mocker.spy(playlist_viewmodel, "set_selected_index")

    playlist_view_ = PlaylistDisplay(playlist_viewmodel)
    qtbot.addWidget(playlist_view_)

    playlist_window = playlist_view_.playlist_window
    model = playlist_view_.playlist_window.model()

    # Populate the playlist first
    populate_playlist(["song1.mp3", "song2.mp3", "song3.mp3"])

    # Wait until the model actually has data and layout is updated
    qtbot.waitUntil(lambda: model.rowCount() >= 3)

    row_to_select = 1

    # --- Act ---
    playlist_window.setCurrentIndex(model.index(row_to_select, 0))

    # --- Assert ---
    spy.assert_called_once_with(row_to_select)

# Test: Viewmodel commands should pass the data from view to corresponding  model setter.
def test_viewmodel_command_should_pass_data_from_view_to_corresponding_model_setter(
        mocker: MockerFixture,
        playlist_model,
        playlist_viewmodel
):
    # --- Arrange ---
    spy = mocker.spy(playlist_model, "set_selected_index")
    index_arg = 1

    # --- Act ---
    playlist_viewmodel.set_selected_index(index_arg)

    # --- Assert ---
    spy.assert_called_once_with(index_arg)
