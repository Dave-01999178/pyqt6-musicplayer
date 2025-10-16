from pathlib import Path

import pytest

from tests.utils import (
    make_fake_path,
    make_fake_path_and_song,
    make_fake_paths_and_songs,
    FileAddExpectation
)


# --------------------------------------------------------------------------------
# PlaylistState.add_song method unit tests.
# --------------------------------------------------------------------------------
#
# --- Single input ---
class TestAddSongSingleInput:

    # Test case: Directory-like input handling.
    @pytest.mark.parametrize("dir_like_input", [
        # Empty inputs -> resolves to CWD (should be skipped).
        "",
        Path(""),

        # Directory-like inputs -> explicitly the CWD (should be skipped).
        ".",
        Path(".")
    ], ids=["str_cwd_like", "path_cwd_like", "str_cwd", "path_cwd"])
    def test_add_song_rejects_directory_like_inputs(
            self,
            playlist_state,
            mock_path_resolve,
            mock_song_from_path,
            dir_like_input
    ):
        # --- Act: Attempt to add directory like input. ---
        playlist_state.add_song(dir_like_input)

        # --- Assert: The directory like input should be rejected. ---
        # Verify that `Path.resolve` and `Song.from_path` was not called because input
        # was rejected during input path normalization.
        mock_path_resolve.assert_not_called()
        mock_song_from_path.assert_not_called()

        # Verify that the playlist remain unchanged.
        assert playlist_state.song_count == 0
        assert playlist_state.playlist == []
        assert playlist_state.playlist_set == set()


    # Test case: Adding a non-existent file.
    @pytest.mark.parametrize("missing_file", [
        # Audio files with supported format (should not be added).
        "path/to/song.mp3",
        Path("path/to/audio.flac"),

        # Non-audio files (should not be added).
        "path/to/corel.CDR",
        Path("path/to/photoshop.psd"),
    ], ids=["str_supported", "path_supported", "str_unsupported", "path_unsupported"])
    def test_add_song_rejects_non_existent_files(
            self,
            playlist_state,
            mock_path_resolve,
            mock_song_from_path,
            missing_file
    ):
        # --- Arrange: Prepare Path.resolve mock. ---
        mock_path_resolve.side_effect = FileNotFoundError

        # --- Act: Attempt to add non-existent file. ---
        playlist_state.add_song(missing_file)

        # --- Assert: The non-existent file should be rejected. ---
        # `Path.resolve()` should always be called per attempted add.
        mock_path_resolve.assert_called_once()

        # `Song.from_path` should not be called as the path couldn't be resolved
        # (FileNotFoundError).
        mock_song_from_path.assert_not_called()

        # Verify that the playlist remain unchanged.
        assert playlist_state.song_count == 0
        assert playlist_state.playlist == []
        assert playlist_state.playlist_set == set()


    # Test case: Adding an audio file.
    @pytest.mark.parametrize("audio_file", [
        "path/to/sound.ogg",
        Path("path/to/music.wav"),
    ], ids=["str", "path"])
    def test_add_song_adds_initial_audio_file_with_supported_format_to_empty_playlist(
            self,
            playlist_state,
            mock_path_resolve,
            mock_song_from_path,
            audio_file
    ):
        # --- Arrange: Prepare fake resolved path and Song for mock dependencies. ---
        fake_resolved_path, fake_song = make_fake_path_and_song(audio_file)

        mock_path_resolve.return_value = fake_resolved_path
        mock_song_from_path.return_value = fake_song

        # --- Act: Add the audio file. ---
        playlist_state.add_song(audio_file)

        # --- Assert: The valid audio file should be added. ---
        # `Path.resolve()` should always be called per attempted add.
        mock_path_resolve.assert_called_once()

        # `Song.from_path()` should always be called per valid/expected file.
        mock_song_from_path.assert_called_once_with(fake_resolved_path)

        # Verify that a new Song object containing the resolved input path was created
        # and added to playlist.
        added_song = playlist_state.playlist[0].path

        assert playlist_state.song_count == 1
        assert added_song == fake_resolved_path
        assert added_song in playlist_state.playlist_set


    # Test case: Adding invalid audio files
    # (e.g. Corrupted, malformed, unreadable file contents or Exceptions).
    def test_add_song_rejects_invalid_audio_files(
            self,
            playlist_state,
            mock_path_resolve,
            mock_song_from_path,
    ):
        # --- Arrange: Prepare fake resolved path ---
        fake_resolved_path = make_fake_path("path/to/invalid.mp3")

        mock_path_resolve.return_value = fake_resolved_path

        # `Song.from_path` returns None when the audio file is invalid.
        mock_song_from_path.return_value = None

        # --- Act: Attempt to add the invalid audio file ---
        playlist_state.add_song(fake_resolved_path)

        # --- Assert: The invalid audio file should be rejected. ---
        # `Path.resolve()` and `Song.from_path` should always be called per attempted add.
        mock_path_resolve.assert_called_once()
        mock_song_from_path.assert_called_once_with(fake_resolved_path)

        # Verify that the playlist remain unchanged.
        assert playlist_state.song_count == 0
        assert playlist_state.playlist == []
        assert playlist_state.playlist_set == set()


    # Test case: Adding a non-audio file.
    @pytest.mark.parametrize("non_audio_file", [
        "path/to/main.py",
        Path("path/to/resume.pdf"),
    ], ids=["str", "path"])
    def test_add_song_rejects_initial_non_audio_file(
            self,
            playlist_state,
            mock_path_resolve,
            mock_song_from_path,
            non_audio_file
    ):
        # --- Arrange: Prepare fake resolved path and mock Path.resolve. ---
        fake_resolved_path = Path(non_audio_file)

        mock_path_resolve.return_value = fake_resolved_path

        # --- Act: Attempt to add non-audio file. ---
        playlist_state.add_song(non_audio_file)

        # -- Assert: The non-audio file should be rejected. ---
        # `Path.resolve()` should always be called per attempted add.
        mock_path_resolve.assert_called_once()

        # Non-audio file was handled in `Playlist.add_song` and `Song.from_path` was not called.
        mock_song_from_path.assert_not_called()

        # Verify that the playlist remain unchanged.
        assert playlist_state.song_count == 0
        assert playlist_state.playlist == []
        assert playlist_state.playlist_set == set()


    # Test case: File path variations and case-insensitive extension handling.
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
    ])
    def test_add_song_accepts_valid_varied_paths_and_extension_cases(
            self,
            playlist_state,
            mock_path_resolve,
            mock_song_from_path,
            audio_file
    ):
        # --- Arrange: Prepare fake resolved path and Song for mock dependencies. ---
        fake_resolved_path, fake_song = make_fake_path_and_song(audio_file)

        mock_path_resolve.return_value = fake_resolved_path
        mock_song_from_path.return_value = fake_song

        # --- Act: Attempt to add the files with different cases. ---
        playlist_state.add_song(audio_file)

        # --- Assert: The audio files with valid cases should be added. ---
        # `Path.resolve()` should always be called per attempted add.
        mock_path_resolve.assert_called_once()

        # `Song.from_path()` should always be called per valid/expected file.
        mock_song_from_path.assert_called_once_with(fake_resolved_path)

        # Verify that a new Song object containing the resolved input path was created
        # and added to playlist.
        added_song = playlist_state.playlist[0].path

        assert playlist_state.song_count == 1
        assert added_song == fake_resolved_path
        assert added_song in playlist_state.playlist_set

    # Test case: Adding a duplicate audio file.
    @pytest.mark.parametrize("duplicate_audio_file", [
        "path/to/initial.mp3",  # # Lowercase.
        Path("path/to/INITIAL.MP3"),  # Uppercase
        "path/to/INITIAL.mp3",  # Uppercase filename.
        Path("path/to/initial.MP3"),  # Uppercase extension
    ], ids=["str_lowercase", "path_uppercase", "str_upper_filename", "path_upper_ext"])
    def test_add_song_rejects_duplicate_song(
            self,
            populate_playlist,
            playlist_state,
            mock_path_resolve,
            mock_song_from_path,
            duplicate_audio_file
    ):
        # --- Arrange: Prepare fake resolved path and Song for mock dependencies. ---
        resolved_input_path, fake_song = make_fake_path_and_song(duplicate_audio_file)

        # Insert the initial song into the playlist through `populate_playlist` fixture since playlist
        # has no direct setter.
        initial_audio_files = [Path("path/to/initial.mp3")]

        populate_playlist(initial_audio_files)

        # `return_value` for new input.
        mock_path_resolve.return_value = resolved_input_path

        # --- Act: Attempt to add duplicate audio files. ---
        playlist_state.add_song(duplicate_audio_file)

        # --- Assert: The duplicate audio file should be rejected. ---
        # `Path.resolve()` should always be called per attempted add.
        mock_path_resolve.assert_called_once()

        # Duplicate audio file was handled in `Playlist.add_song`
        # and `Song.from_path` was not called.
        mock_song_from_path.assert_not_called()

        # Verify that the playlist only contains the initial song.
        playlist_path = [curr_song.path for curr_song in playlist_state.playlist]

        assert playlist_state.song_count == len(initial_audio_files)
        assert playlist_path == initial_audio_files


# --- Batch inputs ---
class TestAddSongBatchInput:
    # Test case: Adding new files.
    @pytest.mark.parametrize("files", [
        # Existing unique audio files (all should be added).
        [
            FileAddExpectation("path/to/song.mp3", True),
            FileAddExpectation(Path("path/to/audio.flac"), True),
            FileAddExpectation("path/to/sound.ogg", True),
            FileAddExpectation(Path("path/to/music.wav"), True),
        ],

        # Existing and missing audio files.
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
        "existing_and_missing_audio",
        "existing_audio_and_non_audio",
        "duplicates_within_input"
    ])
    def test_add_song_accepts_only_unique_audio_files_from_batch_input(
            self,
            playlist_state,
            mock_path_resolve,
            mock_song_from_path,
            files
    ):
        # --- Arrange: Prepare the test data. ---
        test_data = make_fake_paths_and_songs(files)

        input_paths = test_data.input_paths
        resolved_input_paths = test_data.fake_resolved_paths
        fake_songs = test_data.fake_songs
        expected_paths = test_data.expected_paths

        mock_path_resolve.side_effect = resolved_input_paths
        mock_song_from_path.side_effect = fake_songs

        # --- Act: Attempt to add multiple inputs. ---
        playlist_state.add_song(input_paths)

        # --- Assert: Only the valid/expected files should be added. ---
        # `Path.resolve()` should always be called per attempted add.
        assert mock_path_resolve.call_count == len(input_paths)

        # `Song.from_path` should always be called per expected/valid files.
        assert mock_song_from_path.call_count == len(expected_paths)

        # Verify that the playlist only contains the expected files.
        playlist_paths = [curr_song.path for curr_song in playlist_state.playlist]

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
            playlist_state,
            mock_path_resolve,
            mock_song_from_path,
            files
    ):
        # --- Arrange: Prepare the test data. ---
        test_data = make_fake_paths_and_songs(files)

        input_paths = test_data.input_paths
        fake_resolved_paths = test_data.fake_resolved_paths
        fake_songs = test_data.fake_songs
        expected_paths = test_data.expected_paths

        mock_path_resolve.side_effect = fake_resolved_paths
        mock_song_from_path.side_effect = fake_songs

        # --- Act: Attempt to add multiple inputs. ---
        playlist_state.add_song(input_paths)

        # --- Assert ---
        # `Path.resolve` was only called per expected files and directory-like inputs are rejected
        # during input path normalization.
        assert mock_path_resolve.call_count == len(expected_paths)

        # `Song.from_path` should always be called per expected/valid files.
        assert mock_song_from_path.call_count == len(expected_paths)

        # Verify that the playlist only contains the expected files.
        playlist_paths = [curr_song.path for curr_song in playlist_state.playlist]

        assert playlist_paths == expected_paths
