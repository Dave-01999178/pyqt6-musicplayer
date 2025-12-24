from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from pyqt6_music_player.models import AudioPlayerController, AudioPlayerWorker


# ================================================================================
# AUDIO PLAYER WORKER
# ================================================================================
class TestAudioPlayerWorker:
    # Note: We directly assert the protected instance variables here because we don't want
    # to pollute the class under test with property getters just to access their value
    # for this test.
    @pytest.mark.parametrize("instance_variables, expected_values", [
        ("_chunk_size", 1024),
        ("_frame_position", 0),
        ("_is_paused", False),
        ("_is_running", False),
        ("_pa", None),
        ("_stream", None),
    ])
    def test_audio_player_worker_default_instance_variable_values(
            self,
            instance_variables,
            expected_values
    ):
        # --- Arrange ---
        audio_data = Mock()
        audio_player_worker_ = AudioPlayerWorker(audio_data)

        # --- Assert ---
        assert hasattr(audio_player_worker_, instance_variables)
        assert getattr(audio_player_worker_, instance_variables) == expected_values

    @pytest.mark.parametrize("running_state, paused_state, expected_value", [
        (True, True, True),
        (True, False, False),
        (False, False, False),
        (False, True, False),
    ], ids=[
        "worker_running_and_paused",
        "worker_running_and_unpaused",
        "worker_not_running_and_unpaused",
        "worker_not_running_and_paused"
    ])
    def test_is_paused_property_returns_correct_value(
            self,
            running_state,
            paused_state,
            expected_value
    ):
        # --- Arrange ---
        audio_data = Mock()
        audio_player_worker_ = AudioPlayerWorker(audio_data)

        setattr(audio_player_worker_, "_running", running_state)
        setattr(audio_player_worker_, "_paused", paused_state)

        # --- Assert ---
        assert audio_player_worker_.is_paused == expected_value


# ================================================================================
# AUDIO PLAYER CONTROLLER
# ================================================================================
class TestAudioPlayerController:
    def test_start_method_should_initialize_worker_and_thread(self, mocker: MockerFixture):
        # --- Arrange ---
        mock_audio_data = Mock()
        mock_thread_object = Mock()

        mock_thread = mocker.patch("pyqt6_music_player.models.player_engine.QThread")
        mocker.patch("pyqt6_music_player.models.player_engine.AudioPlayerWorker")
        mock_thread.return_value = mock_thread_object

        audio_player_controller = AudioPlayerController()

        # --- Act ---
        audio_player_controller.start(mock_audio_data)

        # --- Assert ---
        assert audio_player_controller._worker_thread is not None
        assert audio_player_controller._worker is not None

        audio_player_controller._worker.moveToThread.assert_called_once_with(mock_thread_object)
        audio_player_controller._worker_thread.start.assert_called_once()
