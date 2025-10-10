from typing import TypedDict, Literal

type SupportedFormat = Literal[".mp3", ".flac", ".ogg", ".wav"]

class SongMetadata(TypedDict, total=False):
    title: str
    artist: str
    album: str
    duration: float
