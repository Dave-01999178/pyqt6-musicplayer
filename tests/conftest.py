import pytest
from pytest_mock import MockerFixture
from pytestqt.qtbot import QtBot

from src.pyqt6_music_player.controllers.music_player_controller import (
    PlaylistController,
    VolumeController,
    NowPlayingMetadataController,
    PlaybackControlsController,
    PlaybackProgressController,
)
from src.pyqt6_music_player.models.music_player_state import (
    MusicPlayerState,
    PlaybackProgressState,
    PlaylistState,
    VolumeState
)
from src.pyqt6_music_player.models.song import Song
from src.pyqt6_music_player.views.music_player_view import MusicPlayerView


@pytest.fixture
def song():
    return Song()


@pytest.fixture
def playlist_state():
    return PlaylistState()


@pytest.fixture
def song_progress_state():
    return PlaybackProgressState()


@pytest.fixture
def volume_state():
    return VolumeState()


@pytest.fixture
def playback_progress_state():
    return PlaybackProgressState()


@pytest.fixture
def music_player(qtbot: QtBot, playlist_state, volume_state, playback_progress_state):
    state = MusicPlayerState(
        playlist=playlist_state,
        volume=volume_state,
        playback_progress=playback_progress_state
    )

    view = MusicPlayerView(state)

    controllers = [
        PlaybackProgressController(state, view),
        PlaybackControlsController(state, view),
        VolumeController(state, view),
        NowPlayingMetadataController(state, view),
        PlaylistController(state, view),
    ]

    qtbot.addWidget(view)

    yield state, view, controllers


@pytest.fixture
def mock_path_resolve(mocker: MockerFixture):
    target = "src.pyqt6_music_player.models.music_player_state.Path.resolve"

    return mocker.patch(target)

@pytest.fixture
def mock_song_from_path(mocker: MockerFixture):
    target = "pyqt6_music_player.models.music_player_state.Song.from_path"

    return mocker.patch(target)


@pytest.fixture
def mock_mutagen_file(mocker: MockerFixture):
    target = "src.pyqt6_music_player.models.song.mutagen.File"

    return mocker.patch(target)

@pytest.fixture
def mock_get_metadata(mocker: MockerFixture):
    target = "src.pyqt6_music_player.models.song.get_metadata"

    return mocker.patch(target)
