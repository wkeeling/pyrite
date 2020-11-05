"""Functionality for manipulating user settings.

The application ships with default settings that can be overridden on a per-user
basis. Per-user settings are stored in the file .pyrite.settings in a user's
home folder.

To load the settings, clients should call the `initialise()` function which will
expose them via the global variable `settings`.
"""
import logging
from io import BytesIO
from pathlib import Path
from pkgutil import get_data

import yaml

SETTINGS_FILENAME = '.pyrite.settings'

log = logging.getLogger(__name__)

# These are the merged user + default settings
settings: dict = {}

default_settings: dict = {}


def initialise():
    """Load the default settings, applying any user overrides, and expose them
    via the `settings` global.
    """
    default_settings.update(yaml.load(
        BytesIO(get_data(__package__, '.pyrite.defaults')), Loader=yaml.SafeLoader
    ))

    settings_path = Path('~', SETTINGS_FILENAME).expanduser()

    if settings_path.exists():
        user_settings = yaml.load(settings_path.read_bytes())
    else:
        user_settings = {}

    settings.update(default_settings)
    settings.update(user_settings)

    if not user_settings:
        # Write out the user settings file on first load
        save()


def get_boolean(name: str) -> bool:
    val = settings[name]

    if val is True or val is False:
        return val

    log.warning(f'Invalid boolean value: {val}')

    return default_settings[name]


def get_int(name: str) -> int:
    val = settings[name]

    if isinstance(val, int):
        return val

    log.warning(f'Invalid integer value: {val}')

    return default_settings[name]


def get_float(name: str) -> float:
    val = settings[name]

    if isinstance(val, float):
        return val

    log.warning(f'Invalid float value: {val}')

    return default_settings[name]


def save():
    """Save the current settings."""
    settings_path = Path('~', SETTINGS_FILENAME).expanduser()
    yaml.dump(settings, settings_path)
