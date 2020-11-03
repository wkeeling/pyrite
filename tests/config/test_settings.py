from pathlib import Path

import pytest

from pyrite.config import settings


class TestSettings:

    @pytest.fixture
    def user_settings(self):
        user_settings = Path('~', settings.SETTINGS_FILENAME).expanduser()
        user_settings.write_text('tab_size: 2')
        yield
        user_settings.unlink()

    def test_initialise_no_user_settings(self):
        settings.initialise()

        assert settings.settings['tab_size'] == 4

    @pytest.mark.usefixtures('user_settings')
    def test_initialise_with_user_settings(self):
        settings.initialise()

        assert settings.settings['tab_size'] == 2
