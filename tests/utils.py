from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Type, Sequence, Literal, Any
from unittest.mock import Mock

from mutagen.mp3 import MP3
from mutagen.oggflac import OggFLAC
from mutagen.oggvorbis import OggVorbis

from src.pyqt6_music_player.models import Song


MOCK_AUDIO_DURATION = 123.4  # Mocked audio duration used across tests.


# --------------------------------------------------------------------------------
# Type Aliases and Custom Types.
# --------------------------------------------------------------------------------
type FilePath = str | Path
type SupportedFormat = Literal[".mp3", ".flac", ".ogg", ".wav"]


# --------------------------------------------------------------------------------
# Dataclasses.
# --------------------------------------------------------------------------------
@dataclass(frozen=True)
class FileAddExpectation:
    path: FilePath
    expected: bool
    side_effect: Optional[Type[Exception]] = None  # Optional side effect for invalid files.


@dataclass(frozen=True)
class PathsAndSongs:
    input_paths: list[FilePath]
    fake_resolved_paths: list[type[Exception] | Path]
    fake_songs: list[Song]
    expected_paths: list[Path]


@dataclass(frozen=True)
class FakeSongData:
    path: Path
    title: str = "Fake Title"
    artist: str =  "Fake Artist"
    album: str = "Fake Album"
    duration: float = 0.00

    def to_song(self) -> Song:
        """Convert this fake test data into an actual `Song` object."""
        return Song(
            path=self.path,
            title=self.title,
            artist=self.artist,
            album=self.album,
            duration=self.duration,
        )


# --------------------------------------------------------------------------------
# Test helpers.
# --------------------------------------------------------------------------------
def make_tmp_path(tmp_path, file_name: str, exist=True):
    path = tmp_path / file_name

    if exist:
        path.touch()

    return path


def make_fake_path(path: FilePath) -> Path:
    return Path(path)


def make_fake_song(path: Path, base_data: FakeSongData | None = None):
    data = base_data or FakeSongData(path)
    return data.to_song()


def make_fake_paths_and_songs(files: Sequence[FileAddExpectation]) -> PathsAndSongs:
    input_paths = []
    fake_resolved_paths = []
    fake_songs = []
    expected_paths = []

    for file in files:
        file_path = file.path
        resolved_path = make_fake_path(file_path)

        if file.expected:
            fake_song = make_fake_song(resolved_path)
            fake_songs.append(fake_song)
            expected_paths.append(resolved_path)

        input_paths.append(file_path)
        fake_resolved_paths.append(file.side_effect or resolved_path)

    return PathsAndSongs(
        input_paths=input_paths,
        fake_resolved_paths=fake_resolved_paths,
        fake_songs=fake_songs,
        expected_paths=expected_paths
    )


def make_fake_path_and_song(path: FilePath) -> tuple[Path, Song]:
    path = Path(path)
    fake_resolved_path = make_fake_path(path)
    fake_song = make_fake_song(path)

    return fake_resolved_path, fake_song


def make_fake_audio_object(tags, file_format: SupportedFormat) -> Mock:
    """
    Builds a fake Mutagen audio object for unit testing.

    Args:
        tags: Metadata dictionary containing optional title, artist, and album.
        file_format: Audio format extension (e.g., ".mp3", ".flac", ".ogg") for mock spec.

    Returns:
        Mock: A mock audio object with the specified metadata and a fixed duration.
    """
    spec_map = {
        ".mp3": MP3,
        ".flac": OggFLAC,
        ".ogg": OggVorbis
    }

    id3_frame_map = {
        "title": "TIT2",
        "artist": "TPE1",
        "album": "TALB"
    }

    fake_metadata: dict[str, Any]
    if file_format == ".mp3":
        fake_metadata = {id3_frame_map[tag]: Mock(text=[value]) for tag, value in tags.items()}
    else:
        fake_metadata = {tag: [value] for tag, value in tags.items()}

    spec_to_use = spec_map.get(file_format)

    fake_audio = Mock(spec=spec_to_use)
    fake_audio.get.side_effect = fake_metadata.get
    fake_audio.info.length = MOCK_AUDIO_DURATION

    return fake_audio
