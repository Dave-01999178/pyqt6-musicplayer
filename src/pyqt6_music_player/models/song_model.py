import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Self

import mutagen

from pyqt6_music_player.constants import DefaultAudioInfo
from pyqt6_music_player.metadata.metadata_extractor import get_metadata


@dataclass(frozen=True, eq=True)
class Song:
    """
    Represents an audio track with metadata.

    Attributes:
        path: Filesystem path to the audio file.
        title: Track title.
        artist: Track artist.
        album: Album name.
        duration: Track duration in seconds (float).
    """
    path: Path | None = None
    title: str = DefaultAudioInfo.title
    artist: str = DefaultAudioInfo.artist
    album: str = DefaultAudioInfo.album
    duration: str | float = DefaultAudioInfo.total_duration
    # album_art: QPixmap

    @classmethod
    def from_path(cls, path: Path) -> Self | None:
        """
        Creates a Song instance from an audio file.

        Returns:
            A Song instance containing the audio file path and its metadata,
            or None if the file cannot be read or contains invalid audio data.
        """
        # --- Load audio file. ---
        try:
            audio = mutagen.File(path)
        except (mutagen.MutagenError, OSError) as e:
            logging.warning("Invalid or unreadable audio file: %s (%s)", path, e)
            return None
        except Exception as e:
            logging.error("Unexpected error while reading %s: %s", path, e)
            return None

        # --- Extract metadata. ---
        metadata = get_metadata(audio)

        return cls(
            path=path,
            title=metadata["title"],
            artist=metadata["artist"],
            album=metadata["album"],
            duration=metadata["duration"]
        )


DEFAULT_SONG: Song = Song()
