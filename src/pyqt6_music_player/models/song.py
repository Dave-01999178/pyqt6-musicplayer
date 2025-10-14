import logging
from dataclasses import dataclass, fields
from pathlib import Path

import mutagen

from pyqt6_music_player.config import (
    DEFAULT_SONG_ALBUM,
    DEFAULT_SONG_ARTIST,
    DEFAULT_SONG_DURATION,
    DEFAULT_SONG_TITLE,
)
from pyqt6_music_player.infra.metadata_extractor import get_metadata


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

    @classmethod
    def get_metadata_fields(cls) -> list[str]:
        """Returns the metadata fields as list of strings."""
        return [f.name for f in fields(cls) if f.name != "path"]  # type: ignore

    def formatted_duration(self):
        """
        Returns audio duration in format (mm:ss) if it's less than hour else (hh:mm:ss).
        """
        int_total_duration = int(self.duration)
        secs_in_hr = 3600
        secs_in_min = 60

        hours, remainder = divmod(int_total_duration, secs_in_hr)
        minutes, seconds = divmod(remainder, secs_in_min)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        return f"{minutes:02d}:{seconds:02d}"


DEFAULT_SONG: Song = Song()
