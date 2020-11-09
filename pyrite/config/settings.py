"""Functionality for manipulating application settings."""
import logging
from collections import UserDict
from io import BytesIO
from pathlib import Path
from pkgutil import get_data

import yaml

SETTINGS_FILENAME = '.pyrite.settings'

log = logging.getLogger(__name__)


class Settings(UserDict):
    """Holds the application wide settings.

    The application ships with default settings that can be overridden on a per-user
    basis. Per-user settings are stored in the file .pyrite.settings in a user's
    home folder. Call the `initialise()` method to load the settings from disk.

    Clients can register listeners (callables) when they want to be informed of
    changes to the settings.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.default_settings: dict = {}

        # Settings listeners
        self.listeners: list = []

    def initialise(self):
        """Load the settings applying any user overrides."""
        self.default_settings.update(yaml.load(
            BytesIO(get_data(__package__, '.pyrite.defaults')), Loader=yaml.SafeLoader
        ))

        try:
            user_settings = yaml.load(
                Path('~', SETTINGS_FILENAME).expanduser().read_bytes(), Loader=yaml.SafeLoader
            ) or {}
        except FileNotFoundError:
            user_settings = {}

        self.data.update(self.default_settings)
        self.data.update(user_settings)

        if not user_settings:
            # Write out the user settings file on first load
            self.save()

    def getboolean(self, name: str) -> bool:
        """Convenience method for retrieving a boolean value.

        If the value is not a boolean value (invalid), then the default
        value for the setting will be returned.

        Args:
            name: The name of the setting.
        Returns: A boolean value.
        """
        val = settings[name]

        if val is True or val is False:
            return val

        log.warning(f'Invalid boolean value: {val}')

        return self.default_settings[name]

    def getint(self, name: str) -> int:
        """Convenience method for retrieving an integer value.

        If the value is not a integer value (invalid), then the default
        value for the setting will be returned.

        Args:
            name: The name of the setting.
        Returns: An integer value.
        """
        val = settings[name]

        if isinstance(val, int):
            return val

        log.warning(f'Invalid integer value: {val}')

        return self.default_settings[name]

    def getfloat(self, name: str) -> float:
        """Convenience method for retrieving a float value.

        If the value is not a float value (invalid), then the default
        value for the setting will be returned.

        Args:
            name: The name of the setting.
        Returns: A float value.
        """
        val = settings[name]

        if isinstance(val, float):
            return val

        log.warning(f'Invalid float value: {val}')

        return self.default_settings[name]

    def on_save(self, listener: callable):
        """Add a listener to be invoked on settings save.

        Args:
            listener: A no-args callable.
        """
        self.listeners.append(listener)

    def save(self):
        """Save the settings to the user's home folder.

        Any registered listeners are invoked after the save has completed.
        """
        with open(Path('~', SETTINGS_FILENAME).expanduser(), 'wt') as out:
            yaml.dump(self.data, out)

        for listener in self.listeners:
            listener()


settings: Settings = Settings()
