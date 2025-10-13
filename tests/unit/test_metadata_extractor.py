from typing import cast

import pytest

from src.pyqt6_music_player.config import FALLBACK_METADATA
from src.pyqt6_music_player.infra.metadata_extractor import (
    extract_id3_tags,
    extract_generic_tags
)
from tests.utils import make_fake_audio_object, SupportedFormat, MOCK_AUDIO_DURATION


# --------------------------------------------------------------------------------
# ID3 Tags unit tests.
# --------------------------------------------------------------------------------

class TestExtractID3TagsHelper:
    # Test case: Assigning fallback values for missing tag.
    @pytest.mark.parametrize("missing_tag", [
        "title",
        "artist",
        "album"
    ], ids=["missing_title_mp3", "missing_artist_mp3", "missing_album_mp3"])
    def test_extract_id3_tags_helper_assigns_fallback_value_for_missing_tags(self, missing_tag) -> None:
        # --- Arrange: Create fake mp3 audio object with missing descriptive tags. ---
        input_metadata = {
            tag: f"Fake {tag}"
            for tag in ["title", "artist", "album"]
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
        input_metadata = {}

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
        input_metadata = {
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


# --------------------------------------------------------------------------------
# Generic Tags unit tests.
# --------------------------------------------------------------------------------

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
        input_metadata = {
            tag: f"Fake {tag}"
            for tag in ["title", "artist", "album"]
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
        input_metadata = {}

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
        input_metadata = {
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
