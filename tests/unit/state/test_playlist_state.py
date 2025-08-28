from pathlib import Path, WindowsPath

import pytest

from src.pyqt6_music_player.config import DEFAULT_CURRENT_SONG
from tests.utils import make_existing_files, make_missing_files


# --- Default values test ---
#
# Instance attribute default values
def test_playlist_state_defaults(playlist_state):
    assert playlist_state.current_song == DEFAULT_CURRENT_SONG
    assert playlist_state.playlist == []


# --- `add_song()` method argument tests ---
#
# Empty arguments.
@pytest.mark.parametrize("empty_path, expected_count", [("", 0), ([], 0)])
def test_add_song_method_should_not_append_empty_paths(playlist_state, empty_path, expected_count):
    playlist_state.add_song(empty_path)

    assert playlist_state.song_count == expected_count


# String paths argument (existing string paths).
@pytest.mark.parametrize("file_names, expected_count", [
    (["dummy_file.mp3"], 1),
    (["dummy_file_1.mp3", "dummy_file_2.mp3"], 2)
])
def test_add_song_method_should_accept_and_convert_valid_and_existing_str_path_to_abs_path(
        tmp_path,
        playlist_state,
        file_names,
        expected_count
):
    # Arrange: Create real files under `tmp_path` and prepare expected resolved Paths.
    file_paths, expected_playlist = make_existing_files(tmp_path, file_names, as_str=True)

    # Act: Add the existing string paths to the playlist.
    playlist_state.add_song(file_paths)

    # Assert:
    # - The correct number of songs were added.
    # - The playlist contains the resolved Paths.
    # - Every entry is a WindowsPath object.
    assert playlist_state.song_count == expected_count
    assert playlist_state.playlist == expected_playlist
    assert all(isinstance(path, WindowsPath) for path in playlist_state.playlist)


# String paths argument (non-existent string paths).
@pytest.mark.parametrize("file_names", [
    ["dummy_file.mp3"],
    (["dummy_file_1.mp3", "dummy_file_2.mp3"])
])
def test_add_song_method_should_not_append_to_list_when_str_path_does_not_exist(
        tmp_path,
        playlist_state,
        file_names
):
    # Arrange: Build string paths under tmp_path, but not created (no `.touch()`).
    # `expected_playlist` should be empty because nothing exists.
    non_existent_paths, expected_playlist = make_missing_files(tmp_path, file_names, as_str=True)

    # Act: Attempt to add the non-existent string paths to the playlist.
    playlist_state.add_song(non_existent_paths)

    # Assert:
    # - No songs should be added (count == 0)
    # - Playlist remains empty ([])
    assert playlist_state.song_count == 0
    assert expected_playlist == []
    assert playlist_state.playlist == expected_playlist


# Path object arguments (existing Path).
@pytest.mark.parametrize("file_names, expected_count", [
    ([Path("dummy_file.mp3")], 1),
    ([Path("dummy_file_1.mp3"), Path("dummy_file_2.mp3")], 2)
])
def test_add_song_method_should_accept_and_convert_valid_and_existing_path_to_abs_path(
        tmp_path,
        playlist_state,
        file_names,
        expected_count
):
    # Arrange: Create real files under `tmp_path` and prepare expected resolved Paths.
    file_paths, expected_playlist = make_existing_files(tmp_path, file_names)

    # Act: Add the existing `Path` to the playlist.
    playlist_state.add_song(file_paths)

    # Assert:
    # - The correct number of songs were added.
    # - The playlist contains the resolved Paths.
    # - Every entry is a WindowsPath object.
    assert playlist_state.song_count == expected_count
    assert playlist_state.playlist == expected_playlist
    assert all(isinstance(path, WindowsPath) for path in playlist_state.playlist)


# Path object arguments (non-existent Path).
@pytest.mark.parametrize("file_names", [
    [Path("dummy_file.mp3")],
    [Path("dummy_file_1.mp3"), Path("dummy_file_2.mp3")]
])
def test_add_song_method_should_not_append_to_list_when_path_does_not_exist(
        tmp_path,
        playlist_state,
        file_names
):
    # Arrange: Build string paths under tmp_path, but not created (no `.touch()`).
    # `expected_playlist` should be empty because nothing exists.
    file_paths, expected_playlist = make_missing_files(tmp_path, file_names)

    # Act: Attempt to add the non-existent `Path` to the playlist.
    playlist_state.add_song(file_paths)

    # Assert:
    # - No songs should be added (count == 0)
    # - Playlist remains empty ([])
    assert playlist_state.song_count == 0
    assert expected_playlist == []
    assert playlist_state.playlist == expected_playlist


# Mixed list (valid elements).
@pytest.mark.parametrize("valid_list, expected_count", [
    (["dummy_file.mp3", "dummy_file_1.wav"], 2),
    ([Path("dummy_file.wav"), Path("dummy_file_1.flac")], 2),
    (["dummy_file.flac", Path("dummy_file_1.ogg")], 2)
])
def test_add_song_method_should_accept_mixed_list_with_only_valid_elements(
        tmp_path,
        playlist_state,
        valid_list,
        expected_count
):
    file_paths, expected_playlist = make_existing_files(tmp_path, valid_list)

    playlist_state.add_song(file_paths)

    assert playlist_state.song_count == expected_count
    assert playlist_state.playlist == expected_playlist
    assert all(isinstance(path, WindowsPath) for path in playlist_state.playlist)


# Mixed list (invalid elements).
@pytest.mark.parametrize("invalid_list", [
    [{"dummy_file.mp3"}],
    [("dummy_file_3.wav", "dummy_file_4.flac")],
    [123],
    [True],
], ids=["set", "tuple", "int", "bool"])
def test_add_song_raises_typeerror_when_list_contains_invalid_types(playlist_state, invalid_list):
    with pytest.raises(TypeError, match="Unsupported type in list."):
        playlist_state.add_song(invalid_list)


# Invalid types.
@pytest.mark.parametrize("invalid_type_arg", [
    "dummy_file.mp3",
    123,
    True,
    {"file": "dummy_file_1.wav"},
    {"dummy_file_2.flac"},
    ("dummy_file_3.ogg", "dummy_file_4.ogg"),
    Path("dummy_file_5.mp3")
], ids=[
    "str",
    "integers",
    "bool",
    "dict",
    "set",
    "tuple",
    "Path"
])
def test_add_song_raises_typeerror_when_not_a_list(
        playlist_state,
        invalid_type_arg
):
    with pytest.raises(TypeError, match="Expected list"):
        playlist_state.add_song(invalid_type_arg)


# --- Duplicate string paths and path tests ---
@pytest.mark.parametrize("file_names, expected_count", [
    (["dummy_file.mp3", "dummy_file.mp3"], 1),
    ([Path("dummy_file.wav"), Path("dummy_file.wav")], 1),
    (["dummy_file.flac", Path("dummy_file.flac")], 1)
])
def test_playlist_should_not_add__valid_and_existing_duplicate_path(
        tmp_path,
        playlist_state,
        file_names,
        expected_count
):
    # Arrange
    file_paths, _ = make_existing_files(tmp_path, file_names)
    expected_playlist = [Path(tmp_path / file_names[0]).resolve()]

    # Act
    playlist_state.add_song(file_paths)

    # Assert
    assert playlist_state.song_count == expected_count
    assert playlist_state.playlist == expected_playlist


# --- File suffix (file extension) validation tests ---
@pytest.mark.parametrize("file_names", [
    ["dummy_file.txt", "dummy_file_1.exe"],
    [Path("dummy_file.jpg"), Path("dummy_file_1.png")],
    ["dummy_file.py", Path("dummy_file_1.json")]
])
def test_add_song_should_ignore_files_with_unsupported_suffix(tmp_path, playlist_state, file_names):
    file_paths, _ = make_existing_files(tmp_path, file_names)

    playlist_state.add_song(file_paths)

    assert playlist_state.song_count == 0
    assert playlist_state.playlist == []


@pytest.mark.parametrize("file_names, expected_files, expected_count", [
    (["dummy_file.mp3", "dummy_file_1.wav"], ["dummy_file.mp3", "dummy_file_1.wav"], 2),
    ([Path("dummy_file.flac"), Path("dummy_file_1.jpg")], [Path("dummy_file.flac")], 1),
    (["dummy_file.png", Path("dummy_file_1.ogg")], [Path("dummy_file_1.ogg")], 1)
])
def test_add_song_method_should_add_files_with_supported_suffix(
        tmp_path,
        playlist_state,
        file_names,
        expected_files,
        expected_count
):
    # Arrange
    file_paths, _ = make_existing_files(tmp_path, file_names)
    expected_playlist = [Path(tmp_path / file).resolve() for file in expected_files]

    # Act
    playlist_state.add_song(file_paths)

    # Assert
    assert playlist_state.song_count == expected_count
    assert playlist_state.playlist == expected_playlist
