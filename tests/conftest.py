import pytest

from pyqt6_music_player.models.music_player_state import VolumeState, MetadataState, SongProgressState


@pytest.fixture
def metadata_state():
    return MetadataState()


@pytest.fixture
def song_progress_state():
    return SongProgressState()


@pytest.fixture
def volume_state():
    return VolumeState()
