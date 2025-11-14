from pathlib import Path

import numpy as np
import pytest
from pydub.exceptions import CouldntDecodeError

from pyqt6_music_player.models.player_engine import AudioData
from tests.utils import make_fake_audio_segment

# TODO: Replace with dummy test file.
temp_test_audio = Path(r"C:\Users\dave_\Music\Factory Background.mp3")


# ================================================================================
# `AudioData.from_file` unit tests.
# ================================================================================
class TestAudioDataFromFile:
    # Test case: File loading and decoding error handling.
    @pytest.mark.parametrize("exception_class, exception_msg, expected_log_msg", [
        (CouldntDecodeError, "Error while decoding stream.", "Failed to decode file"),
        (FileNotFoundError, "No such file or directory.", "Failed to decode file"),
        (Exception, "An unexpected error occurred.", "Failed to decode file"),
    ], ids=[
        "ffmpeg_or_pydub_failure",
        "file_existence_issue",
        "unexpected_errors"
    ])
    def test_handles_and_logs_exceptions_during_audio_loading_and_decoding(
            self,
            caplog,
            mock_audio_segment_from_file,
            exception_class,
            exception_msg,
            expected_log_msg
    ):
        # --- Arrange ---
        mock_audio_segment_from_file.side_effect = exception_class(exception_msg)

        # --- Act ---
        with caplog.at_level("ERROR"):
            audio_data = AudioData.from_file(temp_test_audio)

        # --- Assert ---
        mock_audio_segment_from_file.assert_called_once_with(temp_test_audio)

        assert expected_log_msg in caplog.text
        assert audio_data is None


    # Test case: Store required data from `AudioSegment`.
    @pytest.mark.parametrize("channels, sample_width", [
        (1, 1),
        (1, 2),
        (1, 4),
        (2, 1),
        (2, 2),
    ])
    def test_correctly_stores_required_audio_data(
            self,
            mock_audio_segment_from_file,
            channels,
            sample_width
    ):
        # --- Arrange ---
        fake_audio_segment = make_fake_audio_segment(channels=channels, sample_width=sample_width)

        mock_audio_segment_from_file.return_value = fake_audio_segment

        expected_default_frame_rate = 44100

        # --- Act ---
        audio_data = AudioData.from_file(temp_test_audio)

        # --- Assert ---
        assert audio_data.channels == channels
        assert audio_data.frame_rate == expected_default_frame_rate
        assert audio_data.sample_width == sample_width


    # Test case: Normalize and store samples array (Numpy array).
    @pytest.mark.parametrize("channels, sample_width", [
        (1, 1),
        (1, 2),
        (1, 4),
        (2, 1),
        (2, 2),
    ], ids=[
        "mono_8_bit",
        "mono_16_bit",
        "mono_32_bit",
        "stereo_16_bit",
        "stereo_32_bit"
    ])
    def test_normalize_and_store_samples(
            self,
            mock_audio_segment_from_file,
            channels,
            sample_width
    ):
        # --- Arrange ---
        fake_audio_segment = make_fake_audio_segment(channels=channels, sample_width=sample_width)

        mock_audio_segment_from_file.return_value = fake_audio_segment

        # --- Act ---
        audio_data = AudioData.from_file(temp_test_audio)

        # --- Assert ---
        samples = audio_data.normalized_samples

        assert isinstance(samples, np.ndarray)
        assert samples.shape == (len(samples), channels)
        assert np.issubdtype(samples.dtype, np.float32)
        assert np.all((-1.0 <= samples) & (samples <= 1.0))
