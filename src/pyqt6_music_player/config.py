from pathlib import Path

# Absolute path to the project root
BASE_DIR = Path(__file__).resolve().parents[2]

# Assets path
ASSETS_PATH = BASE_DIR/"assets"

# Paths
STYLESHEET_PATH = BASE_DIR/"styles/styles.qss"

ADD_ICON_PATH = ASSETS_PATH/"add_icon.svg"
REMOVE_ICON_PATH = ASSETS_PATH/"remove_icon.svg"
LOAD_FOLDER_ICON_PATH = ASSETS_PATH/"load_folder_icon.svg"
REPLAY_ICON_PATH = ASSETS_PATH/"replay_icon.svg"
PREV_ICON_PATH = ASSETS_PATH/"prev_icon.svg"
PREV_ICON_PRESSED_PATH = ASSETS_PATH/"prev_icon_pressed.svg"
PLAY_ICON_PATH = ASSETS_PATH/"play_icon.svg"
PAUSE_ICON_PATH = ASSETS_PATH/"pause_icon.svg"
NEXT_ICON_PATH = ASSETS_PATH/"next_icon.svg"
NEXT_ICON_PRESSED_PATH = ASSETS_PATH/"next_icon_pressed.svg"
REPEAT_ICON_PATH = ASSETS_PATH/"repeat_icon.svg"
REPEAT_ICON_PRESSED_PATH = ASSETS_PATH/"repeat_icon_pressed.svg"
VOLUME_HIGH_ICON_PATH = ASSETS_PATH/"volume_high.svg"
VOLUME_MEDIUM_ICON_PATH = ASSETS_PATH/"volume_medium.svg"
VOLUME_LOW_ICON_PATH = ASSETS_PATH/"volume_low.svg"
VOLUME_MUTE_ICON_PATH = ASSETS_PATH/"volume_muted.svg"

DEFAULT_ALBUM_ART_PATH = ASSETS_PATH/"default_art.png"

# Main app configuration
APP_TITLE = "Music Player"
APP_MIN_SIZE = (325, 475)
APP_DEFAULT_SIZE = (750, 750)  # Old (375, 525)

# Widgets configuration
EDIT_BUTTON_DEFAULT_SIZE = (120, 40)
PLAYBACK_BUTTON_SMALL = (30, 30)
PLAYBACK_BUTTON_LARGE = (40, 40)
PLAY_ICON_SIZE = (25, 25)

# Slider config
VOLUME_RANGE = (0, 100)
VOLUME_DEFAULT = 100

# Default values: playlist state
DEFAULT_CURRENT_SONG = None

# State default
DEFAULT_SONG_TITLE = "Song Title"
DEFAULT_SONG_ARTIST = "Artist"
DEFAULT_PLAY_STATE = False
DEFAULT_ELAPSED_TIME = "0:00"
DEFAULT_TIME_DURATION = "0:00"
DEFAULT_VOLUME = 100

# Initial supported audio formats.
SUPPORTED_AUDIO_FORMAT = {".mp3", ".wav", ".flac", ".ogg"}

# File filter
FILE_DIALOG_FILTER = "Audio files (*.mp3 *.wav *.flac *.ogg)"

# Default metadata
FALLBACK_METADATA = {
    "title": "Unknown Title",
    "artist": "Unknown Artist",
    "album": "Unknown Album",
    "duration": 0.0,
}
