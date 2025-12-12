from pathlib import Path
from unittest.mock import Mock

import pytest
from PyQt6.QtTest import QSignalSpy
from pytest_mock import MockerFixture

from pyqt6_music_player.models import VolumeModel, PlaylistModel
from pyqt6_music_player.view_models import VolumeViewModel, PlaylistViewModel, PlaybackControlViewModel
from tests.utils import FakeSongData


# ================================================================================
# VIEWMODEL UNIT TEST SUMMARY
#
# 1. PLAYBACK
#    - Playback viewmodel `play_pause` method.
#      - Start playback logic branch. (Done)
#      - Pause playback logic branch. (Done)
#      - Resume playback logic branch. (Done)
#
# 2. PLAYLIST
#    - Playlist viewmodel correctly exposes volume model properties. (Done)
#    - Playlist viewmodel correctly formats song duration before displaying. (Done)
#
# 2. VOLUME
#    - Volume viewmodel correctly exposes volume model properties. (Done)
#    - Refresh method always emit the volume model current volume as signal. (Done)
# ================================================================================
#
# --- Playback Viewmodel ---
class TestPlaybackViewModel:
    def test_playback_viewmodel_evaluates_start_playback_logic_branch_on_first_play(
            self,
            mocker:MockerFixture,
            playback_viewmodel,
            mock_player_engine
    ):
        # --- Arrange: Prepare viewmodel, and mock dependencies. ---
        playlist_model_ = PlaylistModel()
        playback_viewmodel_ = PlaybackControlViewModel(playlist_model_, mock_player_engine)

        mock_player_engine.worker = Mock()
        mock_player_engine.worker_thread = Mock()
        mock_player_engine.frame_position = 0  # Frame position at 0 means we're just starting.
        mock_player_engine.frame_length = 100
        mock_qtimer = mocker.patch("pyqt6_music_player.view_models.viewmodel.QTimer.singleShot")

        # --- Act: Pass argument `True` to simulate play signal. ---
        playback_viewmodel_.play_pause(True)

        # --- Assert: Verify that `play` method was queued. ---
        mock_qtimer.assert_called_once_with(0, mock_player_engine.play)

    def test_playback_viewmodel_evaluates_pause_logic_branch_on_pause(
            self,
            mocker:MockerFixture,
            playback_viewmodel,
            mock_player_engine
    ):
        # --- Arrange: Prepare viewmodel, and mock dependencies. ---
        playlist_model_ = PlaylistModel()
        playback_viewmodel_ = PlaybackControlViewModel(playlist_model_, mock_player_engine)

        mock_player_engine.worker = Mock()
        mock_player_engine.worker_thread = Mock()
        mock_player_engine.frame_position = 50  # Frame position != 0 before pausing means playing.
        mock_player_engine.frame_length = 100
        mock_qtimer = mocker.patch("pyqt6_music_player.view_models.viewmodel.QTimer.singleShot")

        # --- Act: Pass argument `False` to simulate pause signal. ---
        playback_viewmodel_.play_pause(False)

        # --- Assert: Verify that `pause` method was queued. ---
        mock_qtimer.assert_called_once_with(0, mock_player_engine.pause)

    def test_playback_viewmodel_evaluates_resume_logic_branch_on_resume(
            self,
            mocker:MockerFixture,
            playback_viewmodel,
            mock_player_engine
    ):
        # --- Arrange: Prepare viewmodel, and mock dependencies. ---
        playlist_model_ = PlaylistModel()
        playback_viewmodel_ = PlaybackControlViewModel(playlist_model_, mock_player_engine)

        mock_player_engine.worker = Mock()
        mock_player_engine.worker_thread = Mock()
        mock_player_engine.frame_position = 50  # Frame position != 0 before playing means paused.
        mock_player_engine.frame_length = 100
        mock_qtimer = mocker.patch("pyqt6_music_player.view_models.viewmodel.QTimer.singleShot")

        # --- Act: Pass argument `True` to simulate play signal. ---
        playback_viewmodel_.play_pause(True)

        # --- Assert: Verify that `resume` method was queued. ---
        mock_qtimer.assert_called_once_with(0, mock_player_engine.resume)


# --- Playlist ViewModel ---
class TestPlaylistViewModel:
    # Test: Playlist viewmodel correctly exposes volume model properties.
    def test_playlist_viewmodel_exposes_playlist_model_properties(self, playlist_viewmodel):
        # --- Arrange ---
        playlist_model_ = PlaylistModel()
        playlist_viewmodel_ = PlaylistViewModel(playlist_model_)

        # --- Assert ---
        assert playlist_viewmodel_.playlist == playlist_model_.playlist

    # Test: Playlist viewmodel correctly formats song duration before displaying.
    def test_viewmodel_formats_song_duration_before_displaying(self, playlist_viewmodel):
        # --- Arrange ---
        fake_song = FakeSongData(
            path=Path("path/to/fake.mp3"),
            title="Does",
            artist="not",
            album="matter",
            duration=123.45
        ).to_song()

        # --- Act ---
        formatted_duration = playlist_viewmodel.format_duration(fake_song.duration)

        # --- Assert ---
        assert formatted_duration != 123.45
        assert formatted_duration == "02:03"


# --- Volume ViewModel ---
class TestVolumeViewModel:
    # Test: Volume viewmodel correctly exposes volume model properties.
    def test_viewmodel_correctly_exposes_model_properties(self, mock_player_engine):
        # --- Arrange ---
        volume_model_ = VolumeModel()
        volume_viewmodel_ = VolumeViewModel(volume_model_, mock_player_engine)

        # --- Assert ---
        assert volume_viewmodel_.current_volume == volume_model_.current_volume
        assert volume_viewmodel_.is_muted == volume_model_.is_muted

    # Test: Refresh method always emit the volume model current volume as signal.
    def test_refresh_method_always_emits(self, volume_model, volume_viewmodel):
        # --- Arrange ---
        spy_volume = QSignalSpy(volume_viewmodel.volume_changed)

        # --- Act ---
        volume_viewmodel.refresh()
        volume_viewmodel.refresh()

        # --- Assert ---
        assert len(spy_volume) == 2
        assert all(signal_value[0] == volume_model.current_volume for signal_value in spy_volume)
