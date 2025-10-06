import logging
from dataclasses import dataclass
from pathlib import Path

import mutagen

from src.pyqt6_music_player.config import (
    DEFAULT_SONG_ALBUM,
    DEFAULT_SONG_ARTIST,
    DEFAULT_SONG_DURATION,
    DEFAULT_SONG_TITLE,
)
from src.pyqt6_music_player.infra.metadata_extractor import get_metadata


@dataclass(frozen=True, eq=True)
class Song:
    path: Path | None = None
    title: str = DEFAULT_SONG_TITLE
    artist: str = DEFAULT_SONG_ARTIST
    album: str = DEFAULT_SONG_ALBUM
    duration: float = DEFAULT_SONG_DURATION
    # album_art: QPixmap

    @classmethod
    def from_path(cls, path: Path):
        try:
            audio = mutagen.File(path)
        except Exception as e:
            logging.warning("Invalid audio file: %s, %s", path, e)
            return None

        if audio is None:
            logging.warning("Corrupted or unreadable audio file: %s", path)
            return None

        metadata = get_metadata(audio)

        return cls(
            path=path,
            title=metadata["title"],
            artist=metadata["artist"],
            album=metadata["album"],
            duration=metadata["duration"]
        )


DEFAULT_SONG: Song = Song()
