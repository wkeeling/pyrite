import logging
from importlib import import_module

from pyrite import settings

log = logging.getLogger(__name__)

DEFAULT_THEME = 'dark'


def __getattr__(name):
    """Intercept lookups of theme attributes and load from the currently
    active theme based on user settings.

    Client code can reference theme attributes with:

        >>> from pyrite import theme
        >>> t = theme.attribute  # Will transparently use the active theme
    """
    try:
        theme = import_module(name=f".{settings['theme']}", package='pyrite.theme')
    except ModuleNotFoundError:
        log.error(f"Invalid theme: '{settings['theme']}', falling back to '{DEFAULT_THEME}'")
        theme = import_module(name=f'.{DEFAULT_THEME}', package='pyrite.theme')

    return getattr(theme, name)
