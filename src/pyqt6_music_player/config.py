from pathlib import Path

# ================================================================================
# PATH CONFIGURATION
# ================================================================================
#
# Base directories
BASE_DIR = Path(__file__).resolve().parents[2]
ASSETS_PATH = BASE_DIR / "assets"

# ================================================================================
# STYLES
# ================================================================================
#
# QSS path
STYLESHEET = BASE_DIR / "styles" / "styles.qss"

# ================================================================================
# ICONS PATH
# ================================================================================
#
# Album art
ALBUM_ART_PLACEHOLDER = ASSETS_PATH / "default_art.png"

# App icon
MUSIC_PLAYER_ICON_PATH = ASSETS_PATH / "mp_icon.svg"

# Manage playlist icons
ADD_ICON_PATH = ASSETS_PATH / "add_icon.svg"
REMOVE_ICON_PATH = ASSETS_PATH / "remove_icon.svg"
LOAD_FOLDER_ICON_PATH = ASSETS_PATH / "load_folder_icon.svg"

# Playback control icons
REPLAY_ICON_PATH = ASSETS_PATH / "replay_icon.svg"
PREV_ICON_PATH = ASSETS_PATH / "prev_icon.svg"
PREV_ICON_PRESSED_PATH = ASSETS_PATH / "prev_icon_pressed.svg"
PLAY_ICON_PATH = ASSETS_PATH / "play_icon.svg"
PAUSE_ICON_PATH = ASSETS_PATH / "pause_icon.svg"
NEXT_ICON_PATH = ASSETS_PATH / "next_icon.svg"
NEXT_ICON_PRESSED_PATH = ASSETS_PATH / "next_icon_pressed.svg"
REPEAT_ICON_PATH = ASSETS_PATH / "repeat_icon.svg"
REPEAT_ICON_PRESSED_PATH = ASSETS_PATH / "repeat_icon_pressed.svg"

# Volume control icons
HIGH_VOLUME_ICON_PATH = ASSETS_PATH / "volume_high.svg"
MEDIUM_VOLUME_ICON_PATH = ASSETS_PATH / "volume_medium.svg"
LOW_VOLUME_ICON_PATH = ASSETS_PATH / "volume_low.svg"
MUTED_VOLUME_ICON_PATH = ASSETS_PATH / "volume_muted.svg"


# ================================================================================
# APPLICATION CONFIGURATION
# ================================================================================
APP_TITLE = "Music Player"
APP_MIN_SIZE = (325, 475)
APP_DEFAULT_SIZE = (750, 750)


# ================================================================================
# WIDGET CONFIGURATION
# ================================================================================
SMALL_BUTTON = (30, 30)
SMALL_ICON = (15, 15)

MEDIUM_BUTTON = (40, 40)
MEDIUM_ICON = (20, 20)

RECTANGLE_MEDIUM = (120, 40)


# ================================================================================
# SLIDER CONFIGURATION
# ================================================================================
VOLUME_RANGE = (0, 100)
