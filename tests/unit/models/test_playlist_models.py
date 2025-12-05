from pathlib import Path

import pytest

from pyqt6_music_player.models import Song
from tests.utils import (
    make_fake_path,
    make_fake_path_and_song,
    make_fake_paths_and_songs,
    FileAddExpectation
)


# ================================================================================
# PLAYLIST MODEL UNIT TEST SUMMARY
# 1. `add_song` method (single input)
#    - Reject directory-like paths. (Done)
#    - Reject non-existent file. (Done)
#      - Audio file.
#      - Non-audio file.
#    - Adding valid audio file. (Done)
#    - Reject invalid audio files e.g. corrupted, malformed, unreadable file contents,
#      or exceptions. (Done)
#    - Reject non-audio file. (Done)
#    - File path variations and case-insensitive extension handling. (Done)
#    - Reject duplicate audio file. (Done)
#
# 2. `add_song` method (batch input)
#    - Adding new audio files.
#      - Unique files. (Done)
#      - Present and missing. (Done)
#      - Present audio and non-audio. (Done)
#      - Duplicates within input. (Done)
#    - Adding audio files along with invalid inputs. (Done)
#
# 3. `set_current_index` method
#    - Handle non-integer argument. (Done)
#    - Handle out of range integer argument. (Done)
# ================================================================================


# ================================================================================
# PLAYLIST `ADD_SONG` METHOD UNIT TESTS.
# ================================================================================
#
# --- Single input ---
class TestAddSongMethodSingleInput:
    # Test: Reject directory-like paths.
    @pytest.mark.parametrize("dir_like_input", [
        # Empty path -> resolves to CWD (should be skipped).
        "",
        Path(""),

        # Dot path -> explicitly the CWD (should be skipped).
        ".",
        Path(".")
    ], ids=["str_cwd_like", "path_cwd_like", "str_cwd", "path_cwd"])
    def test_rejects_directory_like_inputs(
            self,
            playlist_model,
            mock_path_resolve,
            mock_song_from_path,
            dir_like_input
    ):
        # --- Act: Attempt to add directory-like paths. ---
        playlist_model.add_song(dir_like_input)

        # --- Assert: Verify that the input was rejected during input path normalization. ---
        mock_path_resolve.assert_not_called()
        mock_song_from_path.assert_not_called()

        assert playlist_model.playlist == []
        assert playlist_model.playlist_set == set()

    # Test: Reject non-existent file.
    @pytest.mark.parametrize("missing_file", [
        # Audio files with supported format (should not be added).
        "path/to/song.mp3",
        Path("path/to/audio.flac"),

        # Non-audio files (should not be added).
        "path/to/corel.CDR",
        Path("path/to/photoshop.psd"),
    ], ids=["str_supported", "path_supported", "str_unsupported", "path_unsupported"])
    def test_rejects_non_existent_file(
            self,
            playlist_model,
            mock_path_resolve,
            mock_song_from_path,
            missing_file
    ):
        # --- Arrange: Simulate `Path.resolve()` raising FileNotFoundError ---
        mock_path_resolve.side_effect = FileNotFoundError

        # --- Act: Attempt to add non-existent file. ---
        playlist_model.add_song(missing_file)

        # --- Assert: Verify that the non-existent file was rejected. ---
        #
        # `Path.resolve()` should always be called per attempted add.
        mock_path_resolve.assert_called_once()

        # `Song.from_path()` should not be called as the path couldn't be resolved
        # (FileNotFoundError).
        mock_song_from_path.assert_not_called()

        assert playlist_model.playlist == []
        assert playlist_model.playlist_set == set()

    # Test case: Adding valid audio file.
    @pytest.mark.parametrize("audio_file", [
        "path/to/sound.ogg",
        Path("path/to/music.wav"),
    ], ids=["str", "path"])
    def test_adds_valid_audio_file(
            self,
            playlist_model,
            mock_path_resolve,
            mock_song_from_path,
            audio_file
    ):
        # --- Arrange: Mock dependencies, prepare fake resolved path, and `Song` object. ---
        fake_resolved_path, fake_song = make_fake_path_and_song(audio_file)

        mock_path_resolve.return_value = fake_resolved_path
        mock_song_from_path.return_value = fake_song

        # --- Act: Add the audio file. ---
        playlist_model.add_song(audio_file)

        # --- Assert: Verify that the audio file was added. ---
        #
        # `Path.resolve()` should always be called per attempted add.
        mock_path_resolve.assert_called_once()

        # `Song.from_path()` should always be called per valid/expected file.
        mock_song_from_path.assert_called_once_with(fake_resolved_path)

        # Verify that a new Song object containing the resolved input path was created
        # and added to playlist.
        added_song = playlist_model.playlist[0].path

        assert added_song == fake_resolved_path
        assert added_song in playlist_model.playlist_set

    # Test: Reject invalid audio files e.g. corrupted, malformed, unreadable file contents,
    # or exceptions.
    def test_rejects_invalid_audio_files(
            self,
            playlist_model,
            mock_path_resolve,
            mock_song_from_path,
    ):
        # --- Arrange: Mock dependencies, and prepare fake resolved path ---
        fake_resolved_path = make_fake_path("path/to/invalid.mp3")

        mock_path_resolve.return_value = fake_resolved_path

        # `Song.from_path` returns None when the audio file is invalid.
        mock_song_from_path.return_value = None

        # --- Act: Attempt to add the invalid audio file ---
        playlist_model.add_song(fake_resolved_path)

        # --- Assert: Verify that the invalid audio file was rejected. ---
        #
        # `Path.resolve()` and `Song.from_path` should always be called per attempted add.
        mock_path_resolve.assert_called_once()
        mock_song_from_path.assert_called_once_with(fake_resolved_path)

        # Verify that the playlist remain unchanged.
        assert playlist_model.playlist == []
        assert playlist_model.playlist_set == set()


    # Test: Reject non-audio file.
    @pytest.mark.parametrize("non_audio_file", [
        "path/to/main.py",
        Path("path/to/resume.pdf"),
    ], ids=["str", "path"])
    def test_rejects_non_audio_file(
            self,
            playlist_model,
            mock_path_resolve,
            mock_song_from_path,
            non_audio_file
    ):
        # --- Arrange: Mock dependencies, and prepare fake resolved path. ---
        fake_resolved_path = Path(non_audio_file)

        mock_path_resolve.return_value = fake_resolved_path

        # --- Act: Attempt to add non-audio file. ---
        playlist_model.add_song(non_audio_file)

        # -- Assert: Verify that the non-audio file was rejected. ---
        #
        # `Path.resolve()` should always be called per attempted add.
        mock_path_resolve.assert_called_once()

        # Verify that file was handled in `Playlist.add_song()`, and `Song.from_path()`
        # is not called.
        mock_song_from_path.assert_not_called()

        assert playlist_model.playlist == []
        assert playlist_model.playlist_set == set()

    # Test: File path variations and case-insensitive extension handling.
    @pytest.mark.parametrize("audio_file", [
        # Strings (all should be added).
        "path/to/song.mp3",  # Lowercase.
        "path/to/AUDIO.FLAC",  # Uppercase.
        "path/to/sound.OGG",  # Uppercase file extension.
        "path/to/My music(2).wav",  # Spaces and numbers.
        "path/to/My_song-@2025!.mp3",  # Special characters (_, -, @, !).

        # Path objects (all should be added).
        Path("path/to/song.mp3"),  # Lowercase
        Path("path/to/AUDIO.FLAC"),  # Uppercase
        Path("path/to/sound.OGG"),  # Uppercase file extension.
        Path("path/to/My music(2).wav"),  # Spaces and numbers.
        Path("path/to/My_song-@2025!.mp3"),  # Special characters (_, -, @, !).
    ], ids=[
        "str_lower",
        "str_upper",
        "str_upper_ext",
        "str_spaces_and_numbers",
        "str_special_chars",
        "path_lower",
        "path_upper",
        "path_upper_ext",
        "path_spaces_and_numbers",
        "path_special_chars",
    ])
    def test_add_song_accepts_valid_varied_paths_and_extension_cases(
            self,
            playlist_model,
            mock_path_resolve,
            mock_song_from_path,
            audio_file
    ):
        # --- Arrange: Mock dependencies, and prepare fake resolved path and `Song` object. ---
        fake_resolved_path, fake_song = make_fake_path_and_song(audio_file)

        mock_path_resolve.return_value = fake_resolved_path
        mock_song_from_path.return_value = fake_song

        # --- Act: Add the audio file with different but valid case and characters. ---
        playlist_model.add_song(audio_file)

        # --- Assert: Verify that the audio file was added. ---
        #
        # `Path.resolve()` should always be called per attempted add.
        mock_path_resolve.assert_called_once()

        # `Song.from_path()` should always be called per valid/expected file.
        mock_song_from_path.assert_called_once_with(fake_resolved_path)

        # Verify that a new Song object containing the resolved input path was created
        # and added to playlist.
        added_song = playlist_model.playlist[0].path

        assert added_song == fake_resolved_path
        assert added_song in playlist_model.playlist_set

    # Test: Reject duplicate audio file.
    @pytest.mark.parametrize("duplicate_audio_file", [
        "path/to/initial.mp3",  # # Lowercase.
        Path("path/to/INITIAL.MP3"),  # Uppercase
        "path/to/INITIAL.mp3",  # Uppercase filename.
        Path("path/to/initial.MP3"),  # Uppercase extension
    ], ids=["str_lowercase", "path_uppercase", "str_upper_filename", "path_upper_ext"])
    def test_add_song_rejects_duplicate_song(
            self,
            populate_playlist,
            playlist_model,
            mock_path_resolve,
            mock_song_from_path,
            duplicate_audio_file
    ):
        # --- Arrange: Mock dependencies, and prepare fake resolved path and `Song` object. ---
        fake_resolved_path, fake_song = make_fake_path_and_song(duplicate_audio_file)

        # Insert the initial song into the playlist through `populate_playlist` fixture since
        # playlist has no direct setter.
        initial_audio_files = [Path("path/to/initial.mp3")]

        populate_playlist(initial_audio_files)

        mock_path_resolve.return_value = fake_resolved_path  # Return the new input.

        # --- Act: Attempt to add a duplicate audio file. ---
        playlist_model.add_song(duplicate_audio_file)

        # --- Assert: Verify that the duplicate audio file was rejected. ---
        #
        # `Path.resolve()` should always be called per attempted add.
        mock_path_resolve.assert_called_once()

        # Duplicate audio file was handled in `Playlist.add_song`
        # and `Song.from_path` is not called.
        mock_song_from_path.assert_not_called()

        # Verify that the playlist only contains the initial song.
        playlist_path = [curr_song.path for curr_song in playlist_model.playlist]

        assert playlist_path == initial_audio_files


# --- Batch inputs ---
class TestAddSongMethodBatchInput:
    # Test: Adding new audio files.
    @pytest.mark.parametrize("files", [
        # Present unique audio files (all should be added).
        [
            FileAddExpectation("path/to/song.mp3", True),
            FileAddExpectation(Path("path/to/audio.flac"), True),
            FileAddExpectation("path/to/sound.ogg", True),
            FileAddExpectation(Path("path/to/music.wav"), True),
        ],

        # Present and missing audio files.
        [
            FileAddExpectation("path/to/song.mp3", True),
            FileAddExpectation(Path("path/to/audio.flac"), False, FileNotFoundError),
        ],

        # Audio and Non-audio files (only audio files should be added).
        [
            FileAddExpectation("path/to/song.mp3", True),
            FileAddExpectation(Path("path/to/audio.flac"), True),
            FileAddExpectation("path/to/presentation.pptx", False),
            FileAddExpectation(Path("path/to/photo.png"), False),
        ],

        # Duplicates within the input (only one should be added).
        [
            FileAddExpectation("path/to/sound.ogg", True),
            FileAddExpectation(Path("path/to/music.wav"), True),
            FileAddExpectation(Path("path/to/sound.ogg"), False),
        ],
    ], ids=[
        "multiple_unique_audio",
        "present_and_missing_audio",
        "present_audio_and_non_audio",
        "duplicates_within_input"
    ])
    def test_add_song_accepts_only_unique_audio_files_from_batch_input(
            self,
            playlist_model,
            mock_path_resolve,
            mock_song_from_path,
            files
    ):
        # --- Arrange: Mock dependencies and prepare test data. ---
        test_data = make_fake_paths_and_songs(files)

        input_paths = test_data.input_paths
        resolved_input_paths = test_data.fake_resolved_paths
        fake_songs = test_data.fake_songs
        expected_paths = test_data.expected_paths

        mock_path_resolve.side_effect = resolved_input_paths
        mock_song_from_path.side_effect = fake_songs

        # --- Act: Attempt to add multiple files. ---
        playlist_model.add_song(input_paths)

        # --- Assert: Verify that only valid/expected files are added. ---
        #
        # `Path.resolve()` should always be called per attempted add.
        assert mock_path_resolve.call_count == len(input_paths)

        # `Song.from_path` should always be called per expected/valid files.
        assert mock_song_from_path.call_count == len(expected_paths)

        # Verify that the playlist only contains the expected files.
        playlist_paths = [curr_song.path for curr_song in playlist_model.playlist]

        assert playlist_paths == expected_paths

    # Test case: Adding audio files along with invalid inputs.
    @pytest.mark.parametrize("files", [
        # Audio files and directory-like inputs.
        [
            FileAddExpectation("path/to/song.mp3", True),
            FileAddExpectation(Path("path/to/audio.flac"), True),
            FileAddExpectation("", False),
            FileAddExpectation(Path("."), False)
        ],
    ])
    def test_add_song_rejects_invalid_inputs_from_batch_input(
            self,
            playlist_model,
            mock_path_resolve,
            mock_song_from_path,
            files
    ):
        # --- Arrange: Mock dependencies and prepare test data. ---
        test_data = make_fake_paths_and_songs(files)

        input_paths = test_data.input_paths
        fake_resolved_paths = test_data.fake_resolved_paths
        fake_songs = test_data.fake_songs
        expected_paths = test_data.expected_paths

        mock_path_resolve.side_effect = fake_resolved_paths
        mock_song_from_path.side_effect = fake_songs

        # --- Act: Attempt to add multiple files. ---
        playlist_model.add_song(input_paths)

        # --- Assert: Verify that only valid/expected files are added. ---
        #
        # `Path.resolve` was only called per expected files and directory-like inputs are rejected
        # during input path normalization.
        assert mock_path_resolve.call_count == len(expected_paths)

        # `Song.from_path` should always be called per expected/valid files.
        assert mock_song_from_path.call_count == len(expected_paths)

        # Verify that the playlist only contains the expected files.
        playlist_paths = [curr_song.path for curr_song in playlist_model.playlist]

        assert playlist_paths == expected_paths


class TestSetSelectedIndexMethod:
    # Test: Handle non-integer argument.
    @pytest.mark.parametrize("arg", ["0", "1.0", True, False])
    def test_raises_when_index_arg_is_not_integer(self, populate_playlist, playlist_model, arg):
        # --- Arrange ---
        songs = ["song1.mp3", "song2.mp3", "song3.mp3"]

        populate_playlist(songs)

        # --- Act & Assert ---
        with pytest.raises(TypeError, match="Index must be an integer."):
            playlist_model.set_selected_index(arg)

    # Test: Handle out of range integer argument.
    def test_should_update_current_index_when_index_arg_is_in_range(
            self,
            populate_playlist,
            playlist_model,
    ):
        # --- Arrange ---
        songs = ["song1.mp3", "song2.mp3", "song3.mp3"]

        populate_playlist(songs)

        selected_index = 3

        # --- Act ---
        playlist_model.set_selected_index(selected_index)

        # --- Assert ---
        assert playlist_model._current_index is None

        assert playlist_model.selected_song is None

    # Test: Should not update current index when playlist is empty.
    def test_should_not_update_current_index_when_playlist_is_empty(
            self,
            populate_playlist,
            playlist_model,
    ):
        # --- Arrange ---
        selected_index = 1

        # --- Act ---
        playlist_model.set_selected_index(selected_index)

        # --- Assert ---
        assert playlist_model._current_index is None

        assert playlist_model.selected_song is None

    # Test: Update current index when index arg is integer and in range.
    @pytest.mark.parametrize("songs, index_arg", [
        (["song1.mp3", "song2.mp3", "song3.mp3"], 0),
        (["song1.mp3", "song2.mp3", "song3.mp3"], 1),
        (["song1.mp3", "song2.mp3", "song3.mp3"], 2),
    ])
    def test_should_update_current_index_when_index_arg_is_out_of_range(
            self,
            populate_playlist,
            playlist_model,
            songs,
            index_arg
    ):
        # --- Arrange ---
        populate_playlist(songs)

        # --- Act ---
        playlist_model.set_selected_index(index_arg)

        # --- Assert ---
        assert playlist_model._current_index == index_arg

        assert playlist_model.selected_song is not None
        assert isinstance(playlist_model.selected_song, Song)
