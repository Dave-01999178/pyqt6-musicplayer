from unittest.mock import Mock

from mutagen.mp3 import MP3

from src.pyqt6_music_player.models.song import Song


def make_tmp_path(tmp_path, file_name: str, exist=True):
    path = tmp_path / file_name

    if exist:
        path.touch()

    return path


# Integration test: PlaylistState.add_song -> Song.from_path.
class TestAddSongToFromPath:
    def test_playlist_add_song_to_song_from_path_integration_test(
            self,
            tmp_path,
            mock_song_from_path,
            playlist_state
    ):
        # --- Arrange: Prepare fake song and mock Song.from_path ---
        fake_path = make_tmp_path(tmp_path, "fake_audio.mp3")
        fake_song = Song(
            path=fake_path,
            title="Fake Title",
            artist="Fake Artist",
            album="Fake Album",
            duration=123.4
        )
        mock_song_from_path.return_value = fake_song

        # --- Act: Add the fake audio to playlist ---
        playlist_state.add_song(fake_path)

        # --- Assert: Song object was created and added to playlist ---
        # Verify that `Song.from_path` was called with input path (fake_path).
        mock_song_from_path.assert_called_once_with(fake_path)

        added_song = playlist_state.playlist[0]

        assert added_song == fake_song
        assert added_song.path == fake_song.path


# Integration test: Song.from_path -> get_metadata() helper.
class TestFromPathToGetMetadata:
    def test_song_from_path_to_get_metadata_integration_test(
            self,
            tmp_path,
            mock_mutagen_file,
            song
    ):
        # --- Arrange: Prepare mock audio object and metadata for mutagen.File ---
        input_path = make_tmp_path(tmp_path, "fake_audio.mp3")

        mock_audio = Mock(spec=MP3)
        mock_metadata = {
            "TIT2": Mock(text=["Fake Title"]),
            "TPE1": Mock(text=["Fake Artist"]),
            "TALB": Mock(text=["Fake Album"]),
        }
        mock_audio.get.side_effect = mock_metadata.get
        mock_audio.info.length = 123.4

        # Patch mutagen.File to return the mock audio file
        mock_mutagen_file.return_value = mock_audio

        # --- Act: Create Song from fake path using real `get_metadata` logic ---
        added_song = song.from_path(input_path)

        # --- Assert: Metadata extracted correctly from mock audio ---
        assert added_song.title == "Fake Title"
        assert added_song.artist == "Fake Artist"
        assert added_song.album == "Fake Album"
        assert added_song.duration > 0


# Integration test: PlaylistState.add_song -> Song.from_path -> get_metadata (full flow).
class TestPlaylistStateToGetMetadata:
    def test_playlist_add_song_integration_test(
            self,
            tmp_path,
            mock_mutagen_file,
            playlist_state
    ):
        # --- Arrange: Create fake mp3 audio file and object ---
        input_path = make_tmp_path(tmp_path, "fake_audio.mp3")

        mock_audio = Mock(spec=MP3)
        mock_metadata = {
            "TIT2": Mock(text=["Fake Title"]),
            "TPE1": Mock(text=["Fake Artist"]),
            "TALB": Mock(text=["Fake Album"]),
        }
        mock_audio.get.side_effect = mock_metadata.get
        mock_audio.info.length = 123.4

        mock_mutagen_file.return_value = mock_audio

        # --- Act: Add the audio file to the playlist ---
        playlist_state.add_song(input_path)

        # --- Assert: A `Song` object was created and added to the playlist ---
        mock_mutagen_file.assert_called_once_with(input_path)

        added_song = playlist_state.playlist[0]

        assert isinstance(added_song, Song)
        assert added_song.title == "Fake Title"
        assert added_song.artist == "Fake Artist"
        assert added_song.album == "Fake Album"
        assert added_song.duration > 0

    def test_should_skip_duplicates(
            self,
            tmp_path,
            mock_song_from_path,
            playlist_state
    ):
        # --- Arrange: Create a single valid fake song ---
        input_path = make_tmp_path(tmp_path, "fake.mp3")

        fake_song = Song(
            path=input_path,
            title="Fake Title",
            artist="Fake Artist",
            album="Fake Album",
            duration=123.4
        )
        mock_song_from_path.return_value = fake_song

        # --- Act: Add the same file twice ---
        playlist_state.add_song(input_path)
        playlist_state.add_song(input_path)

        # --- Assert: Song added only once ---
        assert mock_song_from_path.call_count == 1
        assert playlist_state.song_count == 1
        assert playlist_state.playlist[0] == fake_song

    def test_should_skip_invalid_song(
            self,
            tmp_path,
            mock_song_from_path,
            playlist_state
    ):
        # --- Arrange: Prepare mock song factory that fails ---
        invalid_song = make_tmp_path(tmp_path, "invalid.mp3")

        mock_song_from_path.return_value = None  # simulate invalid Song.from_path()

        # --- Act: Try to add invalid song ---
        playlist_state.add_song(invalid_song)

        # --- Assert: Song should be skipped, no playlist updates ---
        mock_song_from_path.assert_called_once_with(invalid_song)

        assert playlist_state.playlist == []
        assert invalid_song not in playlist_state.playlist_set
