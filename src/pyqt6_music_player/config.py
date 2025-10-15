from pathlib import Path

# ---------------------------------------------------------------------------
# PATH CONFIGURATION
# ---------------------------------------------------------------------------

# Base directories
BASE_DIR = Path(__file__).resolve().parents[2]
ASSETS_PATH = BASE_DIR / "assets"

# ---------------------------------------------------------------------------
# STYLES
# ---------------------------------------------------------------------------

# QSS
STYLESHEET = BASE_DIR / "styles" / "styles.qss"

# ---------------------------------------------------------------------------
# ICONS
# ---------------------------------------------------------------------------

# Album art
DEFAULT_ALBUM_ART_PATH = ASSETS_PATH / "default_art.png"

# App icon
MUSIC_PLAYER_ICON_PATH = ASSETS_PATH / "mp_icon.svg"

# Playlist / file management
ADD_ICON_PATH = ASSETS_PATH / "add_icon.svg"
REMOVE_ICON_PATH = ASSETS_PATH / "remove_icon.svg"
LOAD_FOLDER_ICON_PATH = ASSETS_PATH / "load_folder_icon.svg"

# Playback controls
REPLAY_ICON_PATH = ASSETS_PATH / "replay_icon.svg"
PREV_ICON_PATH = ASSETS_PATH / "prev_icon.svg"
PREV_ICON_PRESSED_PATH = ASSETS_PATH / "prev_icon_pressed.svg"
PLAY_ICON_PATH = ASSETS_PATH / "play_icon.svg"
PAUSE_ICON_PATH = ASSETS_PATH / "pause_icon.svg"
NEXT_ICON_PATH = ASSETS_PATH / "next_icon.svg"
NEXT_ICON_PRESSED_PATH = ASSETS_PATH / "next_icon_pressed.svg"
REPEAT_ICON_PATH = ASSETS_PATH / "repeat_icon.svg"
REPEAT_ICON_PRESSED_PATH = ASSETS_PATH / "repeat_icon_pressed.svg"

# Volume icons
VOLUME_HIGH_ICON_PATH = ASSETS_PATH / "volume_high.svg"
VOLUME_MEDIUM_ICON_PATH = ASSETS_PATH / "volume_medium.svg"
VOLUME_LOW_ICON_PATH = ASSETS_PATH / "volume_low.svg"
VOLUME_MUTE_ICON_PATH = ASSETS_PATH / "volume_muted.svg"

# ---------------------------------------------------------------------------
# APPLICATION CONFIGURATION
# ---------------------------------------------------------------------------

APP_TITLE = "Music Player"
APP_MIN_SIZE = (325, 475)
APP_DEFAULT_SIZE = (750, 750)

# ---------------------------------------------------------------------------
# WIDGET CONFIGURATION
# ---------------------------------------------------------------------------

EDIT_BUTTON_DEFAULT_SIZE = (120, 40)
PLAYBACK_BUTTON_SMALL = (30, 30)
PLAYBACK_BUTTON_LARGE = (40, 40)
PLAY_ICON_SIZE = (25, 25)

# ---------------------------------------------------------------------------
# SLIDER CONFIGURATION
# ---------------------------------------------------------------------------

VOLUME_RANGE = (0, 100)
VOLUME_DEFAULT = 100

# ---------------------------------------------------------------------------
# STATE DEFAULTS
# ---------------------------------------------------------------------------

DEFAULT_SONG_TITLE = "Song Title"
DEFAULT_SONG_ARTIST = "Song Artist"
DEFAULT_SONG_ALBUM = "Song Album"
DEFAULT_PLAY_STATE = False
DEFAULT_ELAPSED_TIME = 0.0
DEFAULT_SONG_DURATION = 0.0
DEFAULT_VOLUME = 100

# ---------------------------------------------------------------------------
# AUDIO FORMATS & FILE DIALOG
# ---------------------------------------------------------------------------

SUPPORTED_AUDIO_FORMAT = {".mp3", ".wav", ".flac", ".ogg"}
FILE_DIALOG_FILTER = "Audio files (*.mp3 *.wav *.flac *.ogg)"

# ---------------------------------------------------------------------------
# METADATA FALLBACKS
# ---------------------------------------------------------------------------

FALLBACK_METADATA = {
    "title": "Unknown Title",
    "artist": "Unknown Artist",
    "album": "Unknown Album",
    "duration": 0.0,
}
