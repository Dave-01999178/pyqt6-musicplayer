"""
This module contains unit tests for `VolumeModel` class.
"""
import pytest
from PyQt6.QtTest import QSignalSpy
from pytest_mock import MockerFixture

from pyqt6_music_player.constants import MAX_VOLUME


# ================================================================================
# VOLUME MODEL CLASS UNIT TEST SUMMARY
# 1. Instance variable/properties default values
#    - Verify default values. (Done)

# 2. set_volume method
#    - Handle out of range arguments. (Done)
#    - Update volume when argument is new and valid. (Done)
#    - Store current volume before updating to a new one. (Done)
#    - Set 'mute state' to 'True' when volume reaches '0'. (Done)
#    - Set 'mute state' to 'False' when volume rises above '0'. (Done)
#    - 'volume_changed' signal only emits when current volume changes. (Done)
#    - Method skips when the argument and the current volume are the same. (Done)
#    - 'mute_changed' signal only emits when 'mute state' changes after volume update. (Done)
#    - 'mute_changed' signal should not emit when 'mute state' did not change
#      after volume update. (Done)

# 3. set_mute method
#    - Handle non-boolean arguments. (Done)
#    - Muting sets 'current volume' to '0' and 'mute state' to 'True'. (Done)
#    - Unmuting restores previous volume, and sets 'mute state' to 'False'. (Done)
#    - Muting while volume is at '0' due to volume seek should do nothing. (Done)
#    - Method skips when the argument and the current 'mute state' are the same. (Done)
# ================================================================================


class TestVolumeModelDefaultValues:
    # Test: Verify volume model default values.
    def test_verify_volume_model_default_values(self, volume_model):
        # --- Assert: Verify instance variable default values ---

        assert volume_model.current_volume == MAX_VOLUME
        assert volume_model.previous_volume == MAX_VOLUME
        assert volume_model.is_muted is False


class TestVolumeModelSetVolumeMethod:
    # Test: Handle out of range volume arguments.
    @pytest.mark.parametrize("invalid_value", [-1, 101])
    def test_method_raises_when_argument_is_out_of_range(self, volume_model, invalid_value):

        with pytest.raises(ValueError, match="out of range"):
            volume_model.set_volume(invalid_value)

    # Test: Update current volume when argument is new and valid.
    @pytest.mark.parametrize("new_volume", [66, 33, 0])
    def test_method_updates_current_volume_when_argument_is_valid(self, volume_model, new_volume):
        # --- Act: Set a new volume ---
        volume_model.set_volume(new_volume)

        # --- Assert: Verify that the current volume is updated ---
        assert volume_model.current_volume == new_volume

    # Test: Store current volume before updating volume to a new one.
    @pytest.mark.parametrize("initial_volume, new_volume", [
        (100, 66),
        (66, 33),
        (33, 0),
        (0, 100),
    ], ids=["high_to_med", "med_to_low", "low_to_mute", "mute_to_high"])
    def test_method_stores_current_volume_before_updating_to_new_volume(
            self,
            volume_model_factory,
            initial_volume,
            new_volume
    ):
        # --- Arrange: Prepare volume model with unmuted initial state ---
        #
        # Used factory fixture to create volume model with specific initial state.
        custom_volume_model = volume_model_factory(initial_volume=initial_volume)

        # --- Act: Set a new volume ---
        custom_volume_model.set_volume(new_volume)

        # --- Assert: Verify that the previous volume is stored ---
        assert custom_volume_model._previous_volume == initial_volume

    # Test: Set 'mute state' to 'True' when volume reaches '0'.
    def test_method_sets_muted_flag_to_true_when_volume_reaches_0(self, volume_model):
        # --- Act: Set volume to '0' ---
        volume_model.set_volume(0)

        # --- Assert: Verify that 'mute state' is set to True ---
        assert volume_model.is_muted is True

    # Test: Set 'mute state' to 'False' when volume rises above '0'.
    def test_method_sets_muted_flag_to_false_when_volume_rises_above_0(self, volume_model_factory):
        # --- Arrange: Prepare volume model with muted initial state ---
        initial_volume = 0
        new_volume = 100

        # Used factory fixture to create volume model with specific initial state.
        custom_volume_model = volume_model_factory(initial_volume=initial_volume)

        # --- Act: Set volume to non-zero ---
        custom_volume_model.set_volume(new_volume)

        # --- Assert: Verify that 'mute state' is set to False ---
        assert custom_volume_model.is_muted is False

    # Test: 'volume_changed' signal only emits when current volume changes.
    @pytest.mark.parametrize("initial_volume, new_volume", [
        (100, 66),
        (66, 33),
        (33, 0),
        (0, 1)
    ], ids=["high_to_med", "med_to_low", "low_to_mute", "mute_to_unmute"])
    def test_method_triggers_volume_changed_signal_when_volume_changes(
            self,
            volume_model_factory,
            initial_volume,
            new_volume
    ):
        # --- Arrange:  Prepare volume model with initial volume, and signal spy ---
        #
        # Used factory fixture to create volume model with specific initial state.
        custom_volume_model = volume_model_factory(initial_volume=initial_volume)

        spy_volume = QSignalSpy(custom_volume_model.volume_changed)
        expected_signal_count = 1  # How many times the signal was triggered.

        # --- Act: Change volume ---
        custom_volume_model.set_volume(new_volume)

        # --- Assert: Verify that signals are emitted ---
        # `QSignalSpy` uses a list to hold the emitted arguments e.g. [[signal_val1], [signal_val2]].
        assert len(spy_volume) == expected_signal_count
        assert spy_volume[0] == [new_volume]

    # Test: Method skips when the argument and the current volume are the same.
    @pytest.mark.parametrize("initial_volume, new_volume", [
        (100, 100),
        (0, 0)
    ])
    def test_method_skips_when_argument_and_current_volume_are_the_same(
            self,
            volume_model_factory,
            initial_volume,
            new_volume
    ):
        # --- Arrange ---
        #
        # Used factory fixture to create volume model with specific initial state.
        custom_volume_model = volume_model_factory(initial_volume=initial_volume)

        spy_volume = QSignalSpy(custom_volume_model.volume_changed)
        spy_mute = QSignalSpy(custom_volume_model.mute_changed)

        # --- Act ---
        custom_volume_model.set_volume(new_volume)

        # --- Assert ---
        assert len(spy_volume) == 0
        assert len(spy_mute) == 0

    # Test: 'mute_changed' signal only emits when 'mute state' changes after volume update.
    @pytest.mark.parametrize("initial_volume, new_volume", [(100, 0), (0, 1)])
    def test_muted_changed_signal_emits_when_mute_state_changes_after_volume_update(
            self,
            volume_model_factory,
            initial_volume,
            new_volume
    ):
        # --- Arrange ---
        #
        # Used factory fixture to create volume model with specific initial state.
        custom_volume_model = volume_model_factory(initial_volume=initial_volume)

        spy_mute = QSignalSpy(custom_volume_model.mute_changed)

        expected_signal = (new_volume == 0)
        expected_signal_count = 1  # How many times the signal was triggered.

        # --- Act ---
        custom_volume_model.set_volume(new_volume)

        # --- Assert ---
        assert len(spy_mute) == expected_signal_count
        assert spy_mute[0] == [expected_signal]

    # Test: 'mute_changed' signal should not emit when 'mute state' did not change
    # after volume update.
    def test_mute_changed_signal_should_not_emit_when_no_mute_state_changes_after_volume_update(
            self,
            volume_model_factory,
    ):
        # --- Arrange ---
        initial_volume = 100
        new_volume = 1

        # Used factory fixture to create volume model with specific initial state.
        custom_volume_model = volume_model_factory(initial_volume=initial_volume)

        spy_muted = QSignalSpy(custom_volume_model.mute_changed)

        # --- Act ---
        custom_volume_model.set_volume(new_volume)

        # --- Assert ---
        assert len(spy_muted) == 0


class TestVolumeModelSetMuteMethod:
    # Test: Handle non-boolean arguments.
    @pytest.mark.parametrize("arg", [0, 1, 0.0, 1.0, "True", "False"])
    def test_method_raises_when_argument_is_not_boolean(self, volume_model, arg):
        with pytest.raises(TypeError, match="Invalid argument"):
            volume_model.set_mute(arg)

    # Test: Muting sets 'current volume' to '0' and 'mute state to 'True'.
    def test_method_sets_volume_to_mute_state(self, volume_model):
        # --- Arrange: Prepare expected values ---
        expected_volume = 0
        expected_mute_state = True

        # --- Act: Mute volume ---
        volume_model.set_mute(True)

        # --- Assert: Verify that volume is in mute state ---
        assert volume_model.current_volume == expected_volume
        assert volume_model.is_muted == expected_mute_state

    # Test: Unmuting restores previous volume, and sets 'mute state' to 'False'.
    def test_method_correctly_restores_volume_to_previous_state(self, volume_model_factory):
        # --- Arrange: Prepare expected values ---
        #
        # Used factory fixture to create volume model with specific initial state.
        custom_volume_model = volume_model_factory(initial_mute_state=True)

        # Volume values before muting.
        expected_volume = 100
        expected_mute_state = False

        # --- Act: Mute then unmute volume ---
        custom_volume_model.set_mute(False)

        # --- Assert: Verify that volume is restored to its previous state ---
        assert custom_volume_model.current_volume == expected_volume
        assert custom_volume_model.is_muted == expected_mute_state

    # Test: Muting while volume is at '0' due to volume seek should do nothing.
    def test_method_should_not_mute_when_volume_is_0(self, volume_model_factory):
        # --- Arrange: Prepare expected values and volume model with muted initial state ---
        previous_volume = 100
        expected_volume = 0

        # Used factory fixture to create volume model with specific initial state.
        custom_volume_model = volume_model_factory(initial_volume=previous_volume)

        # --- Act: Attempt to mute while in muted state ---
        #
        # Mute again via `set_mute` to simulate user clicking volume button while at '0' volume.
        custom_volume_model.set_mute(True)

        # --- Assert: Verify that the volume remain the same. ---
        assert custom_volume_model.current_volume == expected_volume
        assert custom_volume_model._previous_volume == previous_volume

    # Test: Method skips when the argument and the current 'mute state' are the same.
    @pytest.mark.parametrize("initial_state, new_state", [(True, True), (False, False)])
    def test_method_skips_when_argument_and_current_volume_state_are_the_same(
            self,
            volume_model_factory,
            initial_state,
            new_state
    ):
        # --- Arrange ---
        #
        # Used factory fixture to create volume model with specific initial state.
        custom_volume_model = volume_model_factory(initial_mute_state=initial_state)

        spy_volume = QSignalSpy(custom_volume_model.volume_changed)
        spy_mute = QSignalSpy(custom_volume_model.mute_changed)

        # --- Act ---
        custom_volume_model.set_mute(new_state)

        # --- Assert ---
        assert len(spy_volume) == 0
        assert len(spy_mute) == 0
