from typing import TypedDict, Literal, cast
from unittest.mock import Mock

import pytest
from mutagen.mp3 import MP3
from mutagen.oggflac import OggFLAC
from mutagen.oggvorbis import OggVorbis

from pyqt6_music_player.config import FALLBACK_METADATA
from src.pyqt6_music_player.infra.metadata_extractor import (
    extract_id3_tags,
    extract_generic_tags
)


type SupportedFormat = Literal[".mp3", ".flac", ".ogg", ".wav"]

MOCK_AUDIO_DURATION = 123.4  # Mocked audio duration used across tests.


class SongMetadata(TypedDict, total=False):
    title: str
    artist: str
    album: str
    duration: float


def make_fake_audio_object(tags: SongMetadata, file_format: SupportedFormat) -> Mock:
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

    if file_format == ".mp3":
        fake_metadata = {id3_frame_map[tag]: Mock(text=[value]) for tag, value in tags.items()}
    else:
        fake_metadata = {tag: [value] for tag, value in tags.items()}

    spec_to_use = spec_map.get(file_format)

    fake_audio = Mock(spec=spec_to_use)
    fake_audio.get.side_effect = fake_metadata.get
    fake_audio.info.length = MOCK_AUDIO_DURATION

    return fake_audio


# ------------------------------------------------------------------------------------------
class TestExtractID3TagsHelper:

    # Test case: Assigning fallback values for missing tag.
    @pytest.mark.parametrize("missing_tag", [
        "title",
        "artist",
        "album"
    ], ids=["missing_title_mp3", "missing_artist_mp3", "missing_album_mp3"])
    def test_extract_id3_tags_helper_assigns_fallback_value_for_missing_tags(self, missing_tag):
        # --- Arrange: Create fake mp3 audio object with missing descriptive tags. ---
        input_metadata: SongMetadata = {
            tag: f"Fake {tag}"
            for tag in {"title", "artist", "album"}
            if tag != missing_tag
        }

        fake_mp3_audio_object = make_fake_audio_object(input_metadata, ".mp3")

        # --- Act: Attempt to extract tags from fake mp3 audio object. ---
        extracted_tags = extract_id3_tags(fake_mp3_audio_object)

        # --- Assert: A fallback value is assigned to the missing tag. ---
        assert extracted_tags.get(missing_tag) == FALLBACK_METADATA.get(missing_tag)

    # Test case: Assigning fallback values for all missing tags.
    def test_extract_id3_tags_helper_assigns_fallback_value_for_all_missing_tags(self):
        # --- Arrange: Create fake mp3 audio object with all descriptive tags missing. ---
        input_metadata: SongMetadata = {}

        fake_mp3_audio_object = make_fake_audio_object(input_metadata, ".mp3")

        # --- Act: Attempt to extract tags from fake mp3 audio object. ---
        extracted_tags = extract_id3_tags(fake_mp3_audio_object)

        # --- Assert: Fallback values are assigned to all missing tags. ---
        assert extracted_tags.get("title") == FALLBACK_METADATA.get("title")
        assert extracted_tags.get("artist") == FALLBACK_METADATA.get("artist")
        assert extracted_tags.get("album") == FALLBACK_METADATA.get("album")

    # Test case: Extract and return values from present tags.
    def test_extract_id3_tags_helper_extracts_and_returns_values_from_present_tags(self):
        # --- Arrange: Create fake mp3 audio object with complete descriptive tags. ---
        input_metadata: SongMetadata = {
            "title": "Fake Title",
            "artist": "Fake Artist",
            "album": "Fake Album",
        }

        fake_mp3_audio_object = make_fake_audio_object(input_metadata, ".mp3")

        # --- Act: Attempt to extract tags from fake mp3 audio object. ---
        extracted_tags = extract_id3_tags(fake_mp3_audio_object)

        # --- Assert: Extracted tag values matches input metadata. ---
        assert extracted_tags.get("title") == input_metadata.get("title")
        assert extracted_tags.get("artist") == input_metadata.get("artist")
        assert extracted_tags.get("album") == input_metadata.get("album")
        assert extracted_tags.get("duration") == MOCK_AUDIO_DURATION


# ------------------------------------------------------------------------------------------
class TestExtractGenericTagsHelper:
    # Test case: Assigning fallback values for missing tag.
    @pytest.mark.parametrize("missing_tag, file_format", [
        # .flac
        ("title", ".flac"),
        ("artist", ".flac"),
        ("album", ".flac"),

        # .ogg
        ("title", ".ogg"),
        ("artist", ".ogg"),
        ("album", ".ogg"),
    ], ids=[
        "missing_title_flac",
        "missing_artist_flac",
        "missing_album_flac",
        "missing_title_ogg",
        "missing_artist_ogg",
        "missing_album_ogg",
    ])
    def test_extract_generic_tags_helper_assigns_fallback_value_for_missing_tags(
            self,
            missing_tag,
            file_format
    ):
        # --- Arrange: Create fake generic audio object with missing descriptive tags. ---
        input_metadata: SongMetadata = {
            tag: f"Fake {tag}"
            for tag in {"title", "artist", "album"}
            if tag != missing_tag
        }

        fake_generic_audio_object = make_fake_audio_object(
            input_metadata,
            cast(SupportedFormat, file_format)
        )  # Used `cast` to silence type-checker false positive for `file_format`.

        # --- Act: Attempt to extract tags from fake generic audio object. ---
        extracted_tags = extract_generic_tags(fake_generic_audio_object)

        # --- Assert: A fallback value is assigned to the missing tag. ---
        assert extracted_tags.get(missing_tag) == FALLBACK_METADATA.get(missing_tag)

    # Test case: Assigning fallback values for all missing tags.
    @pytest.mark.parametrize("file_format", [
        ".flac",
        ".ogg",
        ".wav"
    ], ids=["missing_all_flac", "missing_all_ogg", "missing_all_wav"])
    def test_extract_generic_tags_helper_assigns_fallback_value_for_all_missing_tags(
            self,
            file_format
    ):
        # --- Arrange: Create fake generic audio object with all descriptive tags missing. ---
        input_metadata: SongMetadata = {}

        fake_generic_audio_object = make_fake_audio_object(
            input_metadata,
            cast(SupportedFormat, file_format)
        )  # Used `cast` to silence type-checker false positive for `file_format`.

        # --- Act: Attempt to extract tags from fake generic audio object. ---
        extracted_tags = extract_generic_tags(fake_generic_audio_object)

        # --- Assert: Fallback values are assigned to all missing tags. ---
        assert extracted_tags.get("title") == FALLBACK_METADATA.get("title")
        assert extracted_tags.get("artist") == FALLBACK_METADATA.get("artist")
        assert extracted_tags.get("album") == FALLBACK_METADATA.get("album")

    # Test case: Extract and return values from present tags.
    @pytest.mark.parametrize("file_format", [".flac", ".ogg"])
    def test_extract_generic_tags_helper_extracts_and_returns_values_from_present_tags(
            self,
            file_format
    ):
        # --- Arrange: Create fake generic audio object with complete descriptive tags. ---
        input_metadata: SongMetadata = {
            "title": "Fake Title",
            "artist": "Fake Artist",
            "album": "Fake Album",
        }

        fake_generic_audio_object = make_fake_audio_object(
            input_metadata,
            cast(SupportedFormat, file_format)
        )  # Used `cast` to silence type-checker false positive for `file_format`.

        # --- Act: Attempt to extract tags from fake generic audio object. ---
        extracted_tags = extract_generic_tags(fake_generic_audio_object)

        # --- Assert: Extracted tag values matches input metadata. ---
        assert extracted_tags.get("title") == input_metadata.get("title")
        assert extracted_tags.get("artist") == input_metadata.get("artist")
        assert extracted_tags.get("album") == input_metadata.get("album")
        assert extracted_tags.get("duration") == MOCK_AUDIO_DURATION
