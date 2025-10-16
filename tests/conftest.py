from pathlib import Path
from typing import Sequence

import pytest
from pytest_mock import MockerFixture

from pyqt6_music_player.models import (
    Song,
    PlaylistState,
    VolumeState,
)
from tests.utils import make_fake_path_and_song


@pytest.fixture
def song():
    return Song()


@pytest.fixture
def playlist_state():
    return PlaylistState()


@pytest.fixture
def volume_state():
    return VolumeState()


@pytest.fixture
def mock_path_resolve(mocker: MockerFixture):
    target = "pyqt6_music_player.models.music_player_state.Path.resolve"

    return mocker.patch(target)

@pytest.fixture
def mock_song_from_path(mocker: MockerFixture):
    target = "pyqt6_music_player.models.music_player_state.Song.from_path"

    return mocker.patch(target)


@pytest.fixture
def mock_mutagen_file(mocker: MockerFixture):
    target = "pyqt6_music_player.models.song.mutagen.File"

    return mocker.patch(target)


@pytest.fixture
def mock_get_metadata(mocker: MockerFixture):
    target = "pyqt6_music_player.models.song.get_metadata"

    return mocker.patch(target)


@pytest.fixture
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
