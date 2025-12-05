from pathlib import Path

import pytest
from PyQt6.QtTest import QSignalSpy

from pyqt6_music_player.models import VolumeModel, PlaylistModel
from pyqt6_music_player.view_models import VolumeViewModel, PlaylistViewModel
from tests.utils import FakeSongData


# ================================================================================
# 1. PLAYLIST VIEWMODEL UNIT TEST SUMMARY
#    - Playlist viewmodel correctly exposes volume model properties. (Done)
#    - Playlist viewmodel correctly formats song duration before displaying. (Done)
#
# 2. VOLUME VIEWMODEL UNIT TEST SUMMARY
#    - Volume viewmodel correctly exposes volume model properties. (Done)
#    - Refresh method always emit the volume model current volume as signal. (Done)
# ================================================================================
#
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
