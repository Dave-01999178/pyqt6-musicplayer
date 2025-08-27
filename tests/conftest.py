import pytest
from pytestqt.qtbot import QtBot

from pyqt6_music_player.controllers.music_player_controller import PlaybackProgressController, VolumeController, \
    PlaybackControlsController, NowPlayingMetadataController, PlaylistController
from pyqt6_music_player.models.music_player_state import VolumeState, MetadataState, PlaybackProgressState, \
    PlaylistState, MusicPlayerState
from pyqt6_music_player.views.music_player_view import MusicPlayerView


@pytest.fixture
def playlist_state():
    return PlaylistState()


@pytest.fixture
def metadata_state():
    return MetadataState()


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
def music_player(qtbot: QtBot, playlist_state, volume_state, metadata_state, playback_progress_state):
    state = MusicPlayerState(
        playlist=playlist_state,
        volume=volume_state,
        metadata=metadata_state,
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
