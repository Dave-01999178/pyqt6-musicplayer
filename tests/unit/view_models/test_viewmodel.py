import pytest
from PyQt6.QtTest import QSignalSpy

from conftest import volume_viewmodel
from pyqt6_music_player.models import VolumeModel
from pyqt6_music_player.view_models import VolumeViewModel


# ================================================================================
# VOLUME VIEWMODEL UNIT TEST SUMMARY
# 1. Volume viewmodel correctly exposes volume model properties. (Done)
# 2. Refresh method always emit the volume model current volume as signal. (Done)
# 3. Viewmodel should not notify when no model changes. (Done)
# ================================================================================


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

    # Test case: Viewmodel should not notify when no model changes.
    @pytest.mark.parametrize("method_name, value", [
        ("set_volume", 100),
        ("set_mute", False)
    ], ids=["set_volume", "set_mute"])
    def test_viewmodel_should_not_notify_no_when_model_changes(
            self,
            volume_model,
            volume_viewmodel,
            method_name,
            value
    ):
        # --- Arrange ---
        spy_volume = QSignalSpy(volume_model.volume_changed)
        spy_mute = QSignalSpy(volume_model.mute_changed)

        # --- Act ---
        getattr(volume_viewmodel, method_name)(value)

        # --- Assert ---
        assert len(spy_volume) == 0
        assert len(spy_mute) == 0
