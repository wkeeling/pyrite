"""Functionality for manipulating user settings.

The application ships with default settings that can be overridden on a per-user
basis. Per-user settings are stored in the file .pyrite.settings in a user's
home folder. Overriding is done automatically when the settings are loaded.

To load the settings, clients should call the `initialise()` function which will
expose them via the global variable `settings`.
"""
from collections import ChainMap
from io import BytesIO
from pathlib import Path
from pkgutil import get_data

import yaml

SETTINGS_FILENAME = '.pyrite.settings'

# Global variable that holds the initialised per-user settings
settings: ChainMap = ChainMap()


def initialise():
    default_settings = yaml.load(
        BytesIO(get_data(__package__, '.pyrite.defaults')), Loader=yaml.SafeLoader
    )

    settings_path = Path('~', SETTINGS_FILENAME).expanduser()

    if settings_path.exists():
        user_settings = yaml.load(settings_path.read_bytes())
    else:
        user_settings = {}

    settings.maps = [user_settings, default_settings]

