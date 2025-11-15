from unittest.mock import Mock

from mutagen.mp3 import MP3

from pyqt6_music_player.models import Song
from tests.utils import make_tmp_path


# ================================================================================
# PlaylistState.add_song -> Song.from_path integration test.
# ================================================================================
class TestAddSongToFromPath:
    def test_playlist_add_song_to_song_from_path_integration(
            self,
            tmp_path,
            mock_song_from_path,
            playlist_model
    ):
        # --- Arrange: Prepare fake file, and `Song` for mock `Song.from_path` ---
        fake_file = make_tmp_path(tmp_path, "fake_audio.mp3")
        fake_song = Song(
            path=fake_file,
            title="Fake Title",
            artist="Fake Artist",
            album="Fake Album",
            duration=123.4
        )

        # Patch `Song.from_path` to return the fake `Song` object.
        mock_song_from_path.return_value = fake_song

        # --- Act: Create and add `Song` object from fake audio file to the playlist ---
        playlist_model.add_song(fake_file)

        # --- Assert: Song object was created and added to playlist ---
        # Verify that the `Song.from_path` was called with input path (fake_file).
        mock_song_from_path.assert_called_once_with(fake_file)

        added_song = playlist_model.playlist[0]

        assert added_song == fake_song
        assert added_song.path == fake_song.path
        assert added_song.path in playlist_model.playlist_set


# ================================================================================
# Song.from_path -> get_metadata helper integration test
# ================================================================================
class TestFromPathToGetMetadata:
    def test_song_from_path_to_get_metadata_integration(
            self,
            tmp_path,
            mock_mutagen_file,
            song
    ):
        # --- Arrange: Prepare fake audio object and metadata for mock `mutagen.File` ---
        fake_file = make_tmp_path(tmp_path, "fake_audio.mp3")

        mock_audio = Mock(spec=MP3)
        mock_metadata = {
            "TIT2": Mock(text=["Fake Title"]),
            "TPE1": Mock(text=["Fake Artist"]),
            "TALB": Mock(text=["Fake Album"]),
        }
        mock_audio.get.side_effect = mock_metadata.get
        mock_audio.info.length = 123.4

        # Patch `mutagen.File` to return the mock audio object.
        mock_mutagen_file.return_value = mock_audio

        # --- Act: Create Song from `fake_file` using real `get_metadata` logic ---
        added_song = song.from_path(fake_file)

        # --- Assert: Metadata extracted correctly from mock audio object ---
        assert added_song.title == "Fake Title"
        assert added_song.artist == "Fake Artist"
        assert added_song.album == "Fake Album"
        assert added_song.duration > 0


# ================================================================================
# PlaylistState.add_song -> Song.from_path -> get_metadata integration test (full flow).
# ================================================================================
class TestPlaylistStateToGetMetadata:
    def test_playlist_add_song_to_get_metadata_integration(
            self,
            tmp_path,
            mock_mutagen_file,
            playlist_model
    ):
        # --- Arrange: Create fake mp3 audio file and object ---
        fake_file = make_tmp_path(tmp_path, "fake_audio.mp3")

        mock_audio = Mock(spec=MP3)
        mock_audio.get.side_effect = {
            "TIT2": Mock(text=["Fake Title"]),
            "TPE1": Mock(text=["Fake Artist"]),
            "TALB": Mock(text=["Fake Album"]),
        }.get

        mock_audio.info = Mock()
        mock_audio.info.length = 123.4

        mock_mutagen_file.return_value = mock_audio

        # --- Act: Create and add `Song` object from fake audio file to the playlist ---
        playlist_model.add_song(fake_file)

        # --- Assert: A `Song` object was created and added to the playlist ---
        mock_mutagen_file.assert_called_once_with(fake_file)

        added_song = playlist_model.playlist[0]

        assert isinstance(added_song, Song)
        assert added_song.title == "Fake Title"
        assert added_song.artist == "Fake Artist"
        assert added_song.album == "Fake Album"
        assert added_song.duration > 0

    def test_playlist_add_song_should_skip_duplicates(
            self,
            tmp_path,
            mock_song_from_path,
            playlist_model
    ):
        # --- Arrange: Create a single valid fake song ---
        fake_file = make_tmp_path(tmp_path, "fake.mp3")

        fake_song = Song(
            path=fake_file,
            title="Fake Title",
            artist="Fake Artist",
            album="Fake Album",
            duration=123.4
        )

        mock_song_from_path.return_value = fake_song

        # --- Act: Add the same file twice ---
        playlist_model.add_song(fake_file)
        playlist_model.add_song(fake_file)

        # --- Assert: Song added only once ---
        assert mock_song_from_path.call_count == 1
        assert playlist_model.playlist[0] == fake_song

    def test_playlist_add_song_should_skip_invalid_files(
            self,
            tmp_path,
            mock_song_from_path,
            playlist_model
    ):
        # --- Arrange: Prepare mock song factory that fails ---
        invalid_audio_file = make_tmp_path(tmp_path, "invalid.mp3")

        mock_song_from_path.return_value = None  # simulate invalid Song.from_path()

        # --- Act: Try to add the invalid audio file ---
        playlist_model.add_song(invalid_audio_file)

        # --- Assert: Invalid audio file should be skipped, no playlist updates ---
        mock_song_from_path.assert_called_once_with(invalid_audio_file)

        assert playlist_model.playlist == []
        assert invalid_audio_file not in playlist_model.playlist_set
