from typing import TypedDict

from mutagen import FileType
from mutagen.mp3 import MP3

from pyqt6_music_player.constants import AudioMetadataFallback


# ================================================================================
# TYPED DICT
# ================================================================================
class AudioInfoDict(TypedDict):
    title: str
    artist: str
    album: str
    duration: float


# ================================================================================
# METADATA EXTRACTOR FUNCTIONS
# ================================================================================
def extract_id3_tags(
        mp3_audio: MP3,
        defaults: type[AudioMetadataFallback] = AudioMetadataFallback
) -> AudioInfoDict:
    """
    Extracts ID3 metadata tags from an MP3 audio file.

    This function retrieves text-based metadata fields (title, artist, album) stored in ID3 frames
    (e.g., TIT2, TPE1, TALB). If a specific frame is missing or empty, a fallback value from
    `defaults` is used.

    Args:
        mp3_audio: A mutagen.mp3.MP3 audio object containing ID3 tags.
        defaults: A dataclass that contains fallback values for the missing metadata tags.

    Returns:
        AudioInfoDict: A dictionary that contains metadata tags (title, artist, album and duration)
                       as keys and their corresponding values as values.
    """
    def _get_text(tag: str, default: str):
        """Helper function for safely extracting `text` values from ID3 frames."""
        frame = mp3_audio.get(tag)

        if frame and hasattr(frame, "text") and frame.text:
            return frame.text[0]
        return default

    return {
        "title": _get_text("TIT2", defaults.title),
        "artist": _get_text("TPE1", defaults.artist),
        "album": _get_text("TALB", defaults.album),
        "duration": mp3_audio.info.length,  # type: ignore  # always present for valid files.
    }


def extract_generic_tags(
        audio: FileType,
        defaults: type[AudioMetadataFallback] = AudioMetadataFallback
) -> AudioInfoDict:
    """
    Extracts standard metadata tags from a non-MP3 audio file.

    This function retrieves metadata tags stored in formats such as FLAC, Ogg, or WAV.
    If a tag is missing, a fallback value from `defaults` is used.

    Args:
        audio: A non-mp3 mutagen audio object (e.g. FLAC, OggVorbis, or WAVE).
        defaults: A dataclass that contains fallback values for the missing metadata tags.

    Returns:
        AudioInfoDict: A dictionary that contains metadata tags (title, artist, album and duration)
                       as keys and their corresponding values as values.
    """
    def _get_value(tag: str, default: str):
        value = audio.get(tag)

        if value is None:
            return default

        return value[0]

    return {
        "title": _get_value("title", defaults.title),
        "artist": _get_value("artist", defaults.artist),
        "album": _get_value("album", defaults.album),
        "duration": audio.info.length,  # type: ignore  # always present for valid files.
    }


def get_metadata(audio: FileType) -> AudioInfoDict:
    """
    Orchestrates metadata extraction for a given audio file.

    Determines the correct extraction method based on the audio file type.

    Args:
        audio: An audio object returned by `mutagen.File` (e.g. MP3, FLAC, OggVorbis, or WAVE).

    Returns:
        AudioInfoDict: A dictionary that contains metadata tags (title, artist, album and duration)
                       as keys and their corresponding values as values.
    """
    if isinstance(audio, MP3):
        return extract_id3_tags(audio)

    return extract_generic_tags(audio)
