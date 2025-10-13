import pytest


# --------------------------------------------------------------------------------
# Volume state defaults unit tests
# --------------------------------------------------------------------------------

def test_should_return_volume_state_default_values(volume_state):
    """Ensure that the volume state"""
    assert volume_state.current_volume == 100
    assert volume_state.previous_volume == 100


# --------------------------------------------------------------------------------
# Volume update unit tests.
# --------------------------------------------------------------------------------

def test_current_volume_updates_when_assigning_new_value(volume_state):
    # Arrange: Ensure that the current volume starts at default value '100'.
    assert volume_state.current_volume == 100

    new_value = 50

    # Act: Assign a new value.
    volume_state.current_volume = new_value

    # Assert: The current volume is updated to the newly assigned value.
    assert volume_state.current_volume == new_value


@pytest.mark.parametrize("invalid_min_input", [-1, -100, -1_000, -10_000])
def test_current_volume_should_not_go_below_minimum_volume_limit_when_input_is_less_than_0(
        volume_state,
        invalid_min_input
):
    # Arrange: Ensure that the current volume starts at default value '100'.
    assert volume_state.current_volume == 100

    expected_value = 0

    # Act: Assign a value that's less than '0' (minimum volume limit).
    volume_state.current_volume = invalid_min_input

    # Assert: The volume is clamped to the minimum limit (0).
    assert volume_state.current_volume == expected_value


@pytest.mark.parametrize("invalid_max_input", [101, 1_000, 10_000, 100_000])
def test_current_volume_should_not_exceed_maximum_volume_limit_when_input_is_greater_than_100(
        volume_state,
        invalid_max_input
):
    # Arrange: Set the starting volume to '0'.
    expected_value = 100

    volume_state.current_volume = 0

    # Act: Assign a value that's greater than '100' (maximum volume limit).
    volume_state.current_volume = invalid_max_input

    # Assert: The volume is clamped to the maximum limit (100).
    assert volume_state.current_volume == expected_value


@pytest.mark.parametrize("invalid_input", ["50", 75.5, "abc", True])
def test_current_volume_setter_should_raise_an_error_when_input_is_not_an_integer(
        volume_state,
        invalid_input
):
    with pytest.raises(TypeError, match="The input must be an integer between 0 and 100."):
        volume_state.current_volume = invalid_input


@pytest.mark.parametrize("current_volume", [33, 66, 100])
def test_current_volume_updates_to_0_when_muted(volume_state, current_volume):
    # Arrange: Set the starting volume.
    volume_state.current_volume = current_volume

    # Act: Simulate mute toggle by passing `True` in `toggle_mute()` method.
    volume_state.toggle_mute(True)

    # Assert: The current volume is muted (0) and the previous volume is preserved.
    assert volume_state.previous_volume == current_volume
    assert volume_state.current_volume == 0


@pytest.mark.parametrize("previous_volume", [33, 66, 100])
def test_current_volume_set_to_previous_after_unmuting(volume_state, previous_volume):
    # Arrange: Set the starting volume.
    volume_state.current_volume = previous_volume

    # Act:
    # Simulate mute and unmute toggle by calling `toggle_mute()` method twice with True and False.
    volume_state.toggle_mute(True)
    volume_state.toggle_mute(False)

    # Assert: The current volume is restored to the previous value after unmuting.
    assert volume_state.previous_volume == 0
    assert volume_state.current_volume == previous_volume
