from pyqt6_music_player.config import DEFAULT_SONG_TITLE, DEFAULT_SONG_ARTIST


def test_metadata_state_defaults(metadata_state):
    assert metadata_state.song_title == DEFAULT_SONG_TITLE
    assert metadata_state.song_artist == DEFAULT_SONG_ARTIST
    