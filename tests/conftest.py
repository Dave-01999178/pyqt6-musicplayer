from pathlib import Path
from typing import Sequence
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from pyqt6_music_player.models import (
    Song,
    PlaylistModel,
    VolumeModel,
)
from pyqt6_music_player.models.player_engine import AudioPlayerController
from pyqt6_music_player.view_models import PlaylistViewModel, PlaybackControlViewModel
from pyqt6_music_player.view_models.viewmodel import VolumeViewModel
from tests.utils import make_fake_path_and_song

# ================================================================================
# DEPENDENCY MOCKS
# ================================================================================
@pytest.fixture
def mock_player_engine():
    return Mock(spec=AudioPlayerController)


@pytest.fixture
def mock_path_resolve(mocker: MockerFixture):
    target = "pyqt6_music_player.models.model.Path.resolve"

    return mocker.patch(target)


@pytest.fixture
def mock_song_from_path(mocker: MockerFixture):
    target = "pyqt6_music_player.models.model.Song.from_path"

    return mocker.patch(target)


@pytest.fixture
def mock_mutagen_file(mocker: MockerFixture):
    target = "pyqt6_music_player.models.song_model.mutagen.File"

    return mocker.patch(target)


@pytest.fixture
def mock_get_metadata(mocker: MockerFixture):
    target = "pyqt6_music_player.models.song_model.get_metadata"

    return mocker.patch(target)


@pytest.fixture
def mock_audio_segment_from_file(mocker: MockerFixture):
    mock_target = "pyqt6_music_player.models.player_engine.AudioSegment.from_file"

    return mocker.patch(mock_target)


# ================================================================================
# SONG
# ================================================================================
@pytest.fixture
def song():
    return Song()


# ================================================================================
# PLAYBACK
# ================================================================================
@pytest.fixture
def playback_viewmodel(playlist_model, mock_player_engine):
    playback_viewmodel = PlaybackControlViewModel(playlist_model, mock_player_engine)

    return playback_viewmodel


# ================================================================================
# PLAYLIST
# ================================================================================
@pytest.fixture
def playlist_model():
    return PlaylistModel()

@pytest.fixture
def playlist_viewmodel(playlist_model):
    return PlaylistViewModel(playlist_model)


# ================================================================================
# VOLUME
# ================================================================================
@pytest.fixture
def volume_model():
    return VolumeModel()


@pytest.fixture
def volume_viewmodel(volume_model, mock_player_engine):
    return VolumeViewModel(volume_model, mock_player_engine)


@pytest.fixture
def volume_model_factory():
    def _create_model(initial_volume: int = 100, initial_mute_state: bool = False):
        volume_model = VolumeModel()
        if initial_mute_state:
            volume_model.set_volume(0)
        else:
            volume_model.set_volume(initial_volume)
        return volume_model
    return _create_model


# ================================================================================
# FACTORY
# ================================================================================
@pytest.fixture
def populate_playlist(playlist_model, mock_path_resolve, mock_song_from_path):
    def _populate(file_paths: Sequence[Path]) -> None:
        if isinstance(file_paths, str):
            raise TypeError("file_paths must be a sequence, not a bare string")

        for path in file_paths:
            initial_song_path, initial_song = make_fake_path_and_song(path)

            # Temporarily mock Path.resolve() and Song.from_path() so the insert succeeds.
            mock_path_resolve.return_value = initial_song_path
            mock_song_from_path.return_value = initial_song

            # Insert the initial song.
            playlist_model.add_song([initial_song_path])

        mock_path_resolve.reset_mock()
        mock_song_from_path.reset_mock()

    return _populate
