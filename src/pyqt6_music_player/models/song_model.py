import logging
from dataclasses import dataclass
from pathlib import Path

import mutagen

from pyqt6_music_player.constants import DefaultAudioInfo
from pyqt6_music_player.metadata.metadata_extractor import get_metadata


@dataclass(frozen=True, eq=True)
class Song:
    path: Path | None = None
    title: str = DefaultAudioInfo.title
    artist: str = DefaultAudioInfo.artist
    album: str = DefaultAudioInfo.album
    duration: str | float = DefaultAudioInfo.total_duration
    # album_art: QPixmap

    @classmethod
    def from_path(cls, path: Path):
        # Load audio file.
        try:
            audio = mutagen.File(path)
        except (mutagen.MutagenError, OSError) as e:
            logging.warning("Invalid or unreadable audio file: %s (%s)", path, e)
            return None
        except Exception as e:
            logging.error("Unexpected error while reading %s: %s", path, e)
            return None

        # Extract metadata.
        metadata = get_metadata(audio)

        return cls(
            path=path,
            title=metadata["title"],
            artist=metadata["artist"],
            album=metadata["album"],
            duration=metadata["duration"]
        )


DEFAULT_SONG: Song = Song()
