from unittest.mock import patch

import pytest

from pyrite import theme


@pytest.fixture
def settings():
    with patch('pyrite.theme.settings', new=dict()) as mock_settings:
        yield mock_settings


def test_load_active_theme(settings):
    settings['theme'] = 'light'

    assert theme.ttktheme == 'arc'


def test_no_such_theme(settings):
    settings['theme'] = 'foobar'

    assert theme.ttktheme == 'equilux'


def test_no_such_attribute(settings):
    settings['theme'] = 'foobar'

    with pytest.raises(AttributeError):
        theme.abc
