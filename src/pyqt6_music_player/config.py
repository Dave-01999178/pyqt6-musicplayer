from pathlib import Path

# Absolute path to the project root
BASE_DIR = Path(__file__).resolve().parents[2]

# Assets path
ASSETS_PATH = BASE_DIR/"assets"

# Paths
STYLESHEET_PATH = BASE_DIR/"styles/styles.qss"

REPLAY_ICON_PATH = ASSETS_PATH/"replay_icon.svg"
REPLAY_ICON_PRESSED_PATH = ASSETS_PATH/"replay_icon_pressed.svg"
PREV_ICON_PATH = ASSETS_PATH/"prev_icon.svg"
PREV_ICON_PRESSED_PATH = ASSETS_PATH/"prev_icon_pressed.svg"
PLAY_ICON_PATH = ASSETS_PATH/"play_icon.svg"
PAUSE_ICON_PATH = ASSETS_PATH/"pause_icon.svg"
NEXT_ICON_PATH = ASSETS_PATH/"next_icon.svg"
NEXT_ICON_PRESSED_PATH = ASSETS_PATH/"next_icon_pressed.svg"
VOLUME_HIGH_ICON_PATH = ASSETS_PATH/"volume_high.svg"
VOLUME_MED_ICON_PATH = ASSETS_PATH/"volume_medium.svg"
VOLUME_LOW_ICON_PATH = ASSETS_PATH/"volume_low.svg"
VOLUME_MUTED_ICON_PATH = ASSETS_PATH/"volume_muted.svg"

DEFAULT_ALBUM_ART_PATH = ASSETS_PATH/"default_art.png"

# Main app configuration
APP_TITLE = "Music Player"
APP_MIN_SIZE = (325, 475)
APP_DEFAULT_SIZE = (375, 525)

# Widgets configuration
BUTTON_SIZE_SMALL = (30, 30)
BUTTON_SIZE_LARGE = (40, 40)
PLAY_ICON_SIZE = (20, 20)

# Slider config
VOLUME_RANGE = (0, 100)
VOLUME_DEFAULT = 100
