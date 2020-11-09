"""Functionality for manipulating application state.

State differs from settings in that it's not explicitly set by
a user. State is set by the application in response to particular
user actions - e.g. remembering a user's last save location or
window position etc.
"""
import logging
import pickle
from collections import UserDict
from pathlib import Path

STATE_DIRECTORY = '.pyrite_data'
STATE_FILENAME = 'state'

log = logging.getLogger(__name__)


class State(UserDict):
    """Holds the application state.

    Clients should call the `initialise()` method to load previously saved
    application state from disk. To save the current state, call the `save()`
    method.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def initialise(self):
        """Load the state from disk."""

        try:
            with open(Path('~', STATE_DIRECTORY, STATE_FILENAME).expanduser(), 'rb') as f:
                self.data = pickle.load(f)
        except FileNotFoundError:
            pass

    def save(self):
        """Save the current state to disk."""

        with open(Path('~', STATE_DIRECTORY, STATE_FILENAME).expanduser(), 'wb') as f:
            pickle.dump(self.data, f, protocol=pickle.HIGHEST_PROTOCOL)


state: State = State()
