import pytest
from PyQt6.QtTest import QSignalSpy
from pytest_mock import MockerFixture
from pytestqt.qtbot import QtBot

from pyqt6_music_player.models.player_engine import PlayerEngine
from pyqt6_music_player.view_models import VolumeViewModel
from pyqt6_music_player.views import VolumeControls, VolumeSlider


# ================================================================================
# VOLUME FEATURE INTEGRATION TEST SUMMARY
#
# 1. Model to Viewmodel
#    - Viewmodel notifies when volume changes. (Done)
#    - Viewmodel notifies when mute state changes. (Done)
#
# 2. Viewmodel to Model
#    -  Viewmodel commands should pass the data from view to corresponding
#       model setter. (Done)
#
# 3. Viewmodel to UI
#    - View updates when the viewmodel notifies of volume changes. (Done)
#    - View updates when the ViewModel notifies of mute state changes. (Done)
#
# 4. UI to Viewmodel
#    - Volume slider seek event should call its corresponding viewmodel command. (Done)
#    - Volume button click event should call its corresponding viewmodel command. (Done)
#
# TODO:
#  5. View to Model
#     - Volume slider seek event should update model volume.
#     - Volume button click event should update model mute state.
#  6. Model to View
#     - Volume button icon, label and slider should change when model volume changes.
#     - Volume button icon, label and slider should change when model mute state changes.
#  7. ViewModel to Player engine
#     - Verify that player engine method is called when volume model changes (viewmodel
#       notifies the player engine of model changes).
# ================================================================================


class TestModelViewModelIntegration:
    # Test: Viewmodel notifies when volume changes.
    @pytest.mark.parametrize("initial_volume, new_volume", [(100, 0), (0, 100)])
    def test_viewmodel_notifies_when_volume_changes(
            self,
            mocker: MockerFixture,
            mock_player_engine,
            volume_model_factory,
            initial_volume,
            new_volume
    ):
        # --- Arrange: Prepare volume model, viewmodel and spies ---
        #
        # Observe viewmodel internal method that is responsible for emitting volume updates.
        spy = mocker.spy(VolumeViewModel, "_on_model_volume_changed")

        # Use factory fixture to create volume model with specific initial state.
        # Suffix variable with '_' to resolve 'fixture is not requested' (fixture name collision).
        volume_model_ = volume_model_factory(initial_volume=initial_volume)
        volume_viewmodel_ = VolumeViewModel(volume_model_, mock_player_engine)

        # Observe the viewmodel signal under test.
        spy_volume = QSignalSpy(volume_viewmodel_.volume_changed)

        # --- Act: Emit the new volume as signal ---
        volume_model_.volume_changed.emit(new_volume)

        # --- Assert: Verify that the viewmodel receives and re-emits the signal ---
        spy.assert_called_once_with(volume_viewmodel_, new_volume)

        assert len(spy_volume) == 1
        assert spy_volume[0] == [new_volume]

    # Test: Viewmodel notifies when mute state changes.
    @pytest.mark.parametrize("initial_state, new_state", [(False, True), (True, False)])
    def test_viewmodel_notifies_when_mute_state_changes(
            self,
            mocker: MockerFixture,
            mock_player_engine,
            volume_model_factory,
            initial_state,
            new_state
    ):
        # --- Arrange: Prepare volume model, viewmodel and spies ---
        #
        # Observe viewmodel internal method that is responsible for emitting mute state updates.
        spy_internal_method = mocker.spy(VolumeViewModel, "_on_model_mute_changed")

        # Use factory fixture to create volume model with specific initial state.
        # Suffix variable with '_' to resolve 'fixture is not requested' (fixture name collision).
        volume_model_ = volume_model_factory(initial_mute_state=initial_state)
        volume_viewmodel_ = VolumeViewModel(volume_model_, mock_player_engine)

        # Observe the viewmodel signal under test.
        spy_mute = QSignalSpy(volume_viewmodel_.mute_changed)

        # --- Act: Emit the new state as signal ---
        volume_model_.mute_changed.emit(new_state)

        # --- Assert: Verify that the viewmodel receives and re-emits the signal ---
        spy_internal_method.assert_called_once_with(volume_viewmodel_, new_state)

        assert len(spy_mute) == 1
        assert spy_mute[0] == [new_state]

    # Test: Viewmodel commands should pass the data from view to corresponding model setter.
    @pytest.mark.parametrize("method_name, data", [
        ("set_volume", 100),
        ("set_volume", 0),
        ("set_mute", True),
        ("set_mute", False),
    ])
    def test_viewmodel_command_should_pass_data_from_view_to_corresponding_model_setter(
            self,
            mocker: MockerFixture,
            volume_model,
            volume_viewmodel,
            method_name,
            data,
    ):
        # --- Arrange ---
        #
        # Observe the corresponding model setter method.
        spy = mocker.spy(volume_model, method_name)

        # --- Arrange: Call viewmodel command with a valid argument ---
        getattr(volume_viewmodel, method_name)(data)  # Viewmodel command/method

        # --- Assert: Verify that the model setter method was called ---
        spy.assert_called_once_with(data)


class TestViewModelViewIntegration:
    # Test: View updates when the viewmodel notifies of volume changes.
    @pytest.mark.parametrize("signal_value", [50, 0])
    def test_view_updates_when_viewmodel_notifies_of_volume_changes(
            self,
            qtbot: QtBot,
            volume_viewmodel,
            signal_value
    ):
        # --- Arrange ---
        volume_view = VolumeControls(volume_viewmodel)

        qtbot.addWidget(volume_view)

        # --- Act ---
        getattr(volume_viewmodel, "volume_changed").emit(signal_value)

        # --- Assert ---

        assert volume_view.volume_slider.value() == signal_value
        assert volume_view.volume_label.text() == f"{signal_value}"

    # Test: View updates when the viewmodel notifies of mute state changes.
    def test_view_updates_when_viewmodel_notifies_of_mute_state_changes(
            self,
            qtbot: QtBot,
            volume_viewmodel,
    ):
        # --- Arrange ---
        volume_view = VolumeControls(volume_viewmodel)

        qtbot.addWidget(volume_view)
        expected_volume = 0

        # --- Act ---
        getattr(volume_viewmodel, "mute_changed").emit(True)

        # --- Assert ---

        assert volume_view.volume_slider.value() == expected_volume
        assert volume_view.volume_label.text() == f"{expected_volume}"

    # Test: Volume slider seek event should call its corresponding viewmodel command.
    @pytest.mark.parametrize("new_volume", [50, 1, 0])
    def test_view_calls_viewmodel_command_on_volume_slider_seek(
            self,
            qtbot: QtBot,
            mocker: MockerFixture,
            volume_viewmodel,
            new_volume
    ):
        # --- Arrange ---
        spy = mocker.spy(volume_viewmodel, "set_volume")

        volume_view = VolumeControls(volume_viewmodel)

        qtbot.addWidget(volume_view)

        # --- Act ---
        volume_view.volume_slider.setValue(new_volume)

        # --- Assert ---
        spy.assert_called_once_with(new_volume)

    # Test: Volume button click event should call its corresponding viewmodel command.
    @pytest.mark.parametrize("initial_state, expected_state", [(True, False), (False, True)])
    def test_view_calls_viewmodel_command_on_volume_button_click(
            self,
            qtbot: QtBot,
            mocker: MockerFixture,
            volume_viewmodel,
            initial_state,
            expected_state
    ):
        # --- Arrange ---
        spy = mocker.spy(volume_viewmodel, "set_mute")

        volume_view = VolumeControls(volume_viewmodel)
        volume_view.volume_button.setChecked(initial_state)

        spy.reset_mock()

        qtbot.addWidget(volume_view)

        # --- Act ---
        volume_view.volume_button.click()

        # --- Assert ---
        spy.assert_called_once_with(expected_state)
