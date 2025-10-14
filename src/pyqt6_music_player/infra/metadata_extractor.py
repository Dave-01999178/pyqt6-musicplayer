from mutagen.mp3 import MP3

from pyqt6_music_player.config import FALLBACK_METADATA


def extract_id3_tags(audio, defaults=FALLBACK_METADATA):
    def _get_text(tag, default):
        frame = audio.get(tag)

        if frame and hasattr(frame, "text") and frame.text:
            return frame.text[0]
        return default

    return {
        "title": _get_text("TIT2", defaults["title"]),
        "artist": _get_text("TPE1", defaults["artist"]),
        "album": _get_text("TALB", defaults["album"]),
        "duration": getattr(audio.info, "length", defaults["duration"]),
    }


def extract_generic_tags(audio, defaults=FALLBACK_METADATA):
    return {
        "title": audio.get("title", [defaults["title"]])[0],
        "artist": audio.get("artist", [defaults["artist"]])[0],
        "album": audio.get("album", [defaults["album"]])[0],
        "duration": getattr(audio.info, "length", defaults["duration"]),
    }


def get_metadata(audio):
    if isinstance(audio, MP3):
        return extract_id3_tags(audio)

    return extract_generic_tags(audio)
