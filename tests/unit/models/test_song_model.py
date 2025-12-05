from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest.mock import Mock

import pytest

from pyqt6_music_player.constants import DefaultAudioInfo
from pyqt6_music_player.models.song_model import Song
from tests.utils import FakeSongData


# --------------------------------------------------------------------------------
# Song model unit tests
# --------------------------------------------------------------------------------

class TestSong:
    # Test case: Ensure `Song` dataclass is immutable.
    def test_song_is_immutable(self, song):
        with pytest.raises(FrozenInstanceError):
            song.title = "New Title"


    # Test case: `Song` metadata default values.
    def test_song_default_values(self, song):
        assert song.path is None
        assert song.title == DefaultAudioInfo.title
        assert song.artist == DefaultAudioInfo.artist
        assert song.album == DefaultAudioInfo.album
        assert song.duration == DefaultAudioInfo.total_duration


    # Test case: File doesn’t exist or can’t be opened (e.g. FileNotFoundError, PermissionError).
    def test_from_path_returns_none_on_mutagen_exception(self, song, mock_mutagen_file):
        # --- Arrange: Prepare input path and mock. ---
        input_path = Path("path/to/broken.flac")

        # Simulate missing or cannot be opened file by mocking `mutagen.File` to raise an error.
        mock_mutagen_file.side_effect = Exception("cannot decode")

        # --- Act: Attempt to extract metadata from audio. ---
        curr_song = song.from_path(input_path)

        # --- Assert: `Song` should not be created. ---
        mock_mutagen_file.assert_called_once_with(input_path)

        assert curr_song is None


    # Test case: Valid audio file with complete descriptive tags.
    def test_song_from_path_returns_song_with_extracted_metadata(
            self,
            song,
            mock_mutagen_file,
            mock_get_metadata
    ):
        # --- Arrange: Prepare input path, fake metadata, and mock dependencies ---
        input_path = Path("path/to/valid.mp3")
        input_metadata = {
            "title": "Fake Title",
            "artist": "Fake Artist",
            "album": "Fake Album",
            "duration": 123.4
        }

        mock_mutagen_file.return_value = Mock()
        mock_get_metadata.return_value = input_metadata

        # --- Act: Attempt to build the Song instance using input path and metadata. ---
        curr_song = song.from_path(input_path)

        # --- Assert: A Song instance was successfully created with the input metadata. ---
        # `mutagen.File` should be called per Song creation attempt.
        mock_mutagen_file.assert_called_once_with(input_path)

        # `get_metadata` should be called per valid audio files.
        mock_get_metadata.assert_called_once_with(mock_mutagen_file.return_value)

        assert isinstance(curr_song, Song)
        assert curr_song.path == input_path
        assert curr_song.title == input_metadata.get("title")
        assert curr_song.artist == input_metadata.get("artist")
        assert curr_song.album == input_metadata.get("album")
        assert curr_song.duration == input_metadata.get("duration")

    # Test case: Valid audio file with missing descriptive tags.
    @pytest.mark.parametrize("input_metadata", [
        # Missing title.
        {
            "title": "Unknown Title",
            "artist": "Fake artist",
            "album": "Fake album",
            "duration": 123.4
        },

        # Missing artist.
        {
            "title": "Fake Title",
            "artist": "Unknown Artist",
            "album": "Fake album",
            "duration": 123.4
        },

        # Missing album.
        {
            "title": "Fake Title",
            "artist": "Fake artist",
            "album": "Unknown album",
            "duration": 123.4
        },

        # Missing all
        {
            "title": "Unknown Title",
            "artist": "Unknown Artist",
            "album": "Unknown album",
            "duration": 123.4
        }
    ], ids=["missing_title", "missing_artist", "missing_album", "missing_all"])
    def test_song_from_path_handles_missing_metadata_gracefully(
            self,
            song,
            mock_mutagen_file,
            mock_get_metadata,
            input_metadata
    ):
        # --- Arrange: Prepare input path, and mock dependencies. ---
        input_path = Path("path/to/valid.mp3")

        mock_mutagen_file.return_value = Mock()
        mock_get_metadata.return_value = input_metadata

        # --- Act: Attempt to build Song from incomplete metadata. ---
        curr_song = song.from_path(input_path)

        # --- Assert: A Song instance with fallback values for missing tags was created. ---
        # External dependencies are called correctly.
        mock_mutagen_file.assert_called_once_with(input_path)
        mock_get_metadata.assert_called_once_with(mock_mutagen_file.return_value)

        assert isinstance(curr_song, Song)
        assert curr_song.path == input_path
        assert curr_song.title == input_metadata.get("title")
        assert curr_song.artist == input_metadata.get("artist")
        assert curr_song.album == input_metadata.get("album")
        assert curr_song.duration == input_metadata.get("duration")
