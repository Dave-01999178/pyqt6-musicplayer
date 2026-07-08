from mutagen import FileType
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.wave import WAVE


def extract_id3_art(audio_file: MP3 | WAVE) -> bytes | None:
    """Extract embedded album art from an ID3-tagged (MP3/WAV) file.

    Args:
        audio_file: The mutagen ID3-tagged file to extract art from.

    Returns:
        The raw album art bytes, or None if no APIC frame is present.

    """
    attached_pics = audio_file.tags.getall("APIC")
    if not attached_pics:
        return None
    return attached_pics[0].data


def extract_flac_art(audio_file: FLAC) -> bytes | None:
    """Extract embedded album art from a FLAC file.

    Args:
        audio_file: The mutagen FLAC file to extract art from.

    Returns:
        The raw album art bytes, or None if no picture is embedded.

    """
    pictures = audio_file.pictures
    if not pictures:
        return None
    return pictures[0].data


def extract_album_art(audio_file: FileType) -> bytes | None:
    """Extract embedded album art from a supported audio file.

    Dispatches to the format-specific extractor based on the file's
    concrete type. Returns None if the format is not supported or the
    file has no embedded art.

    Args:
        audio_file: The mutagen file object to extract art from.

    Returns:
        The raw album art bytes, or None if the format is unsupported
        or the file has no embedded art.

    """
    if isinstance(audio_file, MP3 | WAVE):
        return extract_id3_art(audio_file)

    if isinstance(audio_file, FLAC):
        return extract_flac_art(audio_file)

    return None
