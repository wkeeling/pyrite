"""Functionality for manipulating application settings."""
import logging
from io import BytesIO
from collections import defaultdict, UserDict
from pathlib import Path
from pkgutil import get_data
from typing import List

import yaml

SETTINGS_FILENAME = '.pyrite.settings'

log = logging.getLogger(__name__)


class Settings(UserDict):
    """Holds the application wide settings.

    The application ships with default settings that can be overridden on a per-user
    basis. Per-user settings are stored in the file .pyrite.settings in a user's
    home folder. Call the `initialise()` method to load the settings.

    Clients can register listeners (callables) when they want to be informed of
    changes to particular settings.
    """

    def __init__(self):
        super().__init__()

        self.default_settings: dict = {}

        # Setting listeners are held in a list against a setting name.
        # When that setting changes, all listeners are notified with the
        # new value.
        self.listeners: dict = defaultdict(List[callable])

    def initialise(self):
        """Load the settings applying any user overrides."""
        self.default_settings.update(yaml.load(
            BytesIO(get_data(__package__, '.pyrite.defaults')), Loader=yaml.SafeLoader
        ))

        settings_path = Path('~', SETTINGS_FILENAME).expanduser()

        if settings_path.exists():
            user_settings = yaml.load(settings_path.read_bytes())
        else:
            user_settings = {}

        self.data.update(self.default_settings)
        self.data.update(user_settings)

        if not user_settings:
            # Write out the user settings file on first load
            self.save()

    def get_boolean(self, name: str) -> bool:
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

    def get_int(self, name: str) -> int:
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

    def get_float(self, name: str) -> float:
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

    def __setitem__(self, key, value):
        existing = self.data.get(key)
        if value != existing:
            for listener in self.listeners.get(key, []):
                listener(value)
        super().__setitem__(key, value)

    def save(self):
        """Save the settings to the user's home folder."""
        settings_path = Path('~', SETTINGS_FILENAME).expanduser()
        yaml.dump(self.data, settings_path)

    def add_listener(self, name: str, listener: callable):
        """Add a setting listener.

        Args:
            name: The name of the setting to listen for changes.
            listener: A callable that will receive the new setting value.
        """
        self.listeners[name].append(listener)


settings: Settings = Settings()
