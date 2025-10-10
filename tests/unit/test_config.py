from pathlib import Path

import pytest

from src.pyqt6_music_player import config

# Collect all asset path constants in one list
ASSET_PATHS = [
    getattr(config, constant)
    for constant in dir(config)
    if constant.endswith("_PATH") and constant != "ASSETS_PATH"
]


def test_stylesheet_path_exist():
    stylesheet_path = config.STYLESHEET

    assert stylesheet_path.exists()
    assert stylesheet_path.is_file()


@pytest.mark.parametrize("path", ASSET_PATHS, ids=lambda p: p.name)
def test_asset_path_exists(path: Path):
    assert path.exists()
    assert path.is_file()
