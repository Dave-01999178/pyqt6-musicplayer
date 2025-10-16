from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE

from pyqt6_music_player.config import FALLBACK_METADATA


type AudioFile = MP3 | FLAC | OggVorbis | WAVE
type NonMP3Audio = FLAC | OggVorbis | WAVE
type MetadataDict = dict[str, str | float]


def extract_id3_tags(mp3_audio: MP3, defaults=FALLBACK_METADATA) -> MetadataDict:
    """
    Extracts ID3 metadata tags from an MP3 audio file.

    This function retrieves text-based metadata fields (title, artist, album) stored in ID3 frames
    (e.g., TIT2, TPE1, TALB). If a specific frame is missing or empty, a fallback value from
    `defaults` is used.

    Args:
        mp3_audio: A mutagen.mp3.MP3 audio object containing ID3 tags.
        defaults: A dictionary of fallback metadata values to use when a tag is missing.

    Returns:
        MetadataDict: A dictionary that contains metadata tags (title, artist, album and duration)
                      as keys and their corresponding values as values.
    """
    def _get_text(tag, default):
        """Helper function for safely extracting `text` values from ID3 frames."""
        frame = mp3_audio.get(tag)

        if frame and hasattr(frame, "text") and frame.text:
            return frame.text[0]
        return default

    return {
        "title": _get_text("TIT2", defaults["title"]),
        "artist": _get_text("TPE1", defaults["artist"]),
        "album": _get_text("TALB", defaults["album"]),
        "duration": getattr(mp3_audio.info, "length", defaults["duration"]),
    }


def extract_generic_tags(audio: NonMP3Audio, defaults=FALLBACK_METADATA) -> MetadataDict:
    """
    Extracts standard metadata tags from a non-MP3 audio file.

    This function retrieves metadata tags stored in formats such as FLAC, Ogg, or WAV.
    If a tag is missing, a fallback value from `defaults` is used.

    Args:
        audio: A non-mp3 mutagen audio object (e.g. FLAC, OggVorbis, or WAVE).
        defaults: A dictionary of fallback metadata values to use when a tag is missing.

    Returns:
        MetadataDict: A dictionary that contains metadata tags (title, artist, album and duration)
                      as keys and their corresponding values as values.
    """
    return {
        "title": audio.get("title", [defaults["title"]])[0],
        "artist": audio.get("artist", [defaults["artist"]])[0],
        "album": audio.get("album", [defaults["album"]])[0],
        "duration": getattr(audio.info, "length", defaults["duration"]),
    }


def get_metadata(audio: AudioFile) -> MetadataDict:
    """
    Orchestrates metadata extraction for a given audio file.

    Determines the correct extraction method based on the audio file type.

    Args:
        audio: An audio object returned by `mutagen.File` (e.g. MP3, FLAC, OggVorbis, or WAVE).

    Returns:
        MetadataDict: A dictionary that contains metadata tags (title, artist, album and duration)
                      as keys and their corresponding values as values.
    """
    if isinstance(audio, MP3):
        return extract_id3_tags(audio)

    return extract_generic_tags(audio)
