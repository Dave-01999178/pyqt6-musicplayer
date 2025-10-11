from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Type, Optional

import pytest

from src.pyqt6_music_player.models.song import Song


FilePath = str | Path


# --- Helpers ---
@dataclass(frozen=True)
class FileAddExpectation:
    path: FilePath
    expected: bool
    side_effect: Optional[Type[Exception]] = None  # Optional side effect for invalid files.


@dataclass(frozen=True)
class PathsAndSongs:
    input_paths: list[FilePath]
    fake_resolved_paths: list[type[Exception] | Path]
    fake_songs: list[Song]
    expected_paths: list[Path]


@dataclass(frozen=True)
class FakeSongData:
    path: Path
    title: str = "Fake Title"
    artist: str =  "Fake Artist"
    album: str = "Fake Album"
    duration: float = 0.00

    def to_song(self) -> Song:
        """Convert this fake test data into an actual `Song` object."""
        return Song(
            path=self.path,
            title=self.title,
            artist=self.artist,
            album=self.album,
            duration=self.duration,
        )


def make_fake_path(path: FilePath) -> Path:
    return Path(path)


def make_fake_song(path: Path, base_data: FakeSongData | None = None):
    data = base_data or FakeSongData(path)
    return data.to_song()


def make_fake_paths_and_songs(files: Sequence[FileAddExpectation]) -> PathsAndSongs:
    input_paths = []
    fake_resolved_paths = []
    fake_songs = []
    expected_paths = []

    for file in files:
        file_path = file.path
        resolved_path = make_fake_path(file_path)

        if file.expected:
            fake_song = make_fake_song(resolved_path)
            fake_songs.append(fake_song)
            expected_paths.append(resolved_path)

        input_paths.append(file_path)
        fake_resolved_paths.append(file.side_effect or resolved_path)

    return PathsAndSongs(
        input_paths=input_paths,
        fake_resolved_paths=fake_resolved_paths,
        fake_songs=fake_songs,
        expected_paths=expected_paths
    )


def make_fake_path_and_song(path: FilePath) -> tuple[Path, Song]:
    path = Path(path)
    fake_resolved_path = make_fake_path(path)
    fake_song = make_fake_song(path)

    return fake_resolved_path, fake_song


def populate_playlist(playlist_state, mock_path_resolve, mock_song_from_path):
    def _populate(file_paths: Sequence[Path]) -> None:
        if isinstance(file_paths, str):
            raise TypeError("file_paths must be a sequence, not a bare string")

        for path in file_paths:
            initial_song_path, initial_song = make_fake_path_and_song(path)

            # Temporarily mock Path.resolve() and Song.from_path() so the insert succeeds.
            mock_path_resolve.return_value = initial_song_path
            mock_song_from_path.return_value = initial_song

            # Insert the initial song.
            playlist_state.add_song(initial_song_path)

        mock_path_resolve.reset_mock()
        mock_song_from_path.reset_mock()

    return _populate


# ------------------------------ PlaylistState.add_song unit tests ------------------------------
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
        # --- Act ---
        # Attempt to add directory like input.
        playlist_state.add_song(dir_like_input)

        # --- Assert ---
        mock_path_resolve.assert_not_called()
        mock_song_from_path.assert_not_called()

        # The playlist remains empty.
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
        # --- Arrange ---
        # Simulate missing files by mocking `Path.resolve()` to raise FileNotFound error.
        mock_path_resolve.side_effect = FileNotFoundError

        # --- Act ---
        # Attempt to add the files.
        playlist_state.add_song(missing_file)

        # --- Assert ---
        # `Path.resolve()` should always be called per attempted add.
        mock_path_resolve.assert_called_once()

        # `Song.from_path` should not be called as the path couldn't be resolved (FileNotFound).
        mock_song_from_path.assert_not_called()

        # The playlist should remain empty.
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
        # --- Arrange ---
        # Prepare fake resolved path and Song for mocks.
        resolved_input_path, fake_song = make_fake_path_and_song(audio_file)

        # Simulate input path resolution by mocking `Path.resolve()` to return `resolved_input_path`.
        mock_path_resolve.return_value = resolved_input_path

        # Simulate `Song` object creation by mocking `Song.from_path` to return `fake_song`.
        mock_song_from_path.return_value = fake_song

        # --- Act ---
        # Attempt to add the files.
        playlist_state.add_song(audio_file)

        # --- Assert ---
        # `Path.resolve()` should always be called per attempted add.
        mock_path_resolve.assert_called_once()

        # `Song.from_path()` should always be called per valid/expected file.
        mock_song_from_path.assert_called_once_with(resolved_input_path)

        # Verify that the resolved input path was stored in `Song` and added to the playlist.
        added_song = playlist_state.playlist[0].path

        assert playlist_state.song_count == 1
        assert added_song == resolved_input_path
        assert added_song in playlist_state.playlist_set


    # Test case: Adding invalid audio files
    # (e.g. Corrupted, malformed, unreadable file contents or Exceptions).
    def test_add_song_rejects_invalid_audio_files(
            self,
            playlist_state,
            mock_path_resolve,
            mock_song_from_path,
    ):
        input_path = make_fake_path("path/to/invalid.mp3")

        # Simulate input path resolution by mocking `Path.resolve()` to return `input_path`.
        mock_path_resolve.return_value = input_path

        # Simulate invalid audio files by mocking `Song.from_path` to return None.
        # `Song.from_path` returns None when the audio file is invalid.
        mock_song_from_path.return_value = None

        # --- Act ---
        playlist_state.add_song(input_path)

        # --- Assert ---
        mock_path_resolve.assert_called_once()
        mock_song_from_path.assert_called_once()

        # The invalid audio file is not added and the playlist remain empty.
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
        # --- Arrange ---
        # Prepare fake resolved path for mock.
        resolved_input_path = Path(non_audio_file)

        # Simulate input path resolution by mocking `Path.resolve()` to return `resolved_input_path`.
        mock_path_resolve.return_value = resolved_input_path

        # --- Act ---
        # Attempt to add the file.
        playlist_state.add_song(non_audio_file)

        # -- Assert ---

        # `Path.resolve()` should always be called per attempted add.
        mock_path_resolve.assert_called_once()

        # `Song.from_path` was not called.
        mock_song_from_path.assert_not_called()

        # The playlist remains empty.
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
        # --- Arrange ---
        # Prepare fake resolved path and Song for mocks.
        resolved_input_path, fake_song = make_fake_path_and_song(audio_file)

        # Simulate input path resolution by making `mock_path_resolve` return `resolved_input_path`.
        mock_path_resolve.return_value = resolved_input_path

        # Simulate `Song` object creation by making `mock_song_from_path` return `fake_song`.
        mock_song_from_path.return_value = fake_song

        # --- Act ---
        # Attempt to add the file
        playlist_state.add_song(audio_file)

        # --- Assert ---
        # `Path.resolve()` should always be called per attempted add.
        mock_path_resolve.assert_called_once()

        # `Song.from_path()` should always be called per valid/expected file.
        mock_song_from_path.assert_called_once_with(resolved_input_path)

        # Verify that the resolved input path was stored in `Song` and added to the playlist.
        added_song = playlist_state.playlist[0].path

        assert playlist_state.song_count == 1
        assert added_song == resolved_input_path
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
            playlist_state,
            mock_path_resolve,
            mock_song_from_path,
            duplicate_audio_file
    ):
        # --- Arrange ---
        # Prepare fake resolved path and Song for mocks.
        resolved_input_path, fake_song = make_fake_path_and_song(duplicate_audio_file)

        # Insert the initial song into the playlist through `populate_playlist` fixture since playlist
        # has no direct setter.
        initial_audio_files = [Path("path/to/initial.mp3")]
        populate_playlist(initial_audio_files, mock_path_resolve, mock_song_from_path)

        # Simulate input path resolution by making `mock_path_resolve` return `resolved_input_path`.
        mock_path_resolve.return_value = resolved_input_path

        # --- Act ---
        playlist_state.add_song(duplicate_audio_file)

        # --- Assert ---
        mock_path_resolve.assert_called_once()
        mock_song_from_path.assert_not_called()

        playlist_path = [curr_song.path for curr_song in playlist_state.playlist]

        assert playlist_state.song_count == len(initial_audio_files)
        assert playlist_path == initial_audio_files


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
        # --- Arrange ---
        # Prepare the test data.
        test_data = make_fake_paths_and_songs(files)

        input_paths = test_data.input_paths
        resolved_input_paths = test_data.fake_resolved_paths
        fake_songs = test_data.fake_songs
        expected_paths = test_data.expected_paths

        # Simulate input path resolution by making `mock_path_resolve` return `resolved_input_paths`.
        mock_path_resolve.side_effect = resolved_input_paths

        # Simulate `Song` object creation by making `mock_song_from_path` return `fake_song`.
        mock_song_from_path.side_effect = fake_songs

        # --- Act ---
        # Attempt to add the files
        playlist_state.add_song(input_paths)

        # --- Assert ---
        assert mock_path_resolve.call_count == len(input_paths)
        assert mock_song_from_path.call_count == len(expected_paths)

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
        # --- Arrange ---
        test_data = make_fake_paths_and_songs(files)

        input_paths = test_data.input_paths
        fake_resolved_paths = test_data.fake_resolved_paths
        fake_songs = test_data.fake_songs
        expected_paths = test_data.expected_paths

        mock_path_resolve.side_effect = fake_resolved_paths
        mock_song_from_path.side_effect = fake_songs

        # --- Act ---
        playlist_state.add_song(input_paths)

        # --- Assert ---
        assert mock_path_resolve.call_count == len(expected_paths)
        assert mock_song_from_path.call_count == len(expected_paths)

        playlist_paths = [curr_song.path for curr_song in playlist_state.playlist]

        assert playlist_paths == expected_paths
