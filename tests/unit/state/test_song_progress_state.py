from pyqt6_music_player.config import DEFAULT_ELAPSED_TIME, DEFAULT_TIME_DURATION


def test_song_progress_state_defaults(song_progress_state):
    assert song_progress_state.elapsed_time == DEFAULT_ELAPSED_TIME
    assert song_progress_state.time_remaining == DEFAULT_TIME_DURATION
