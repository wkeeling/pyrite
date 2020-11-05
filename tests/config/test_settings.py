from pathlib import Path
from unittest.mock import patch

import pytest

from pyrite.config import settings


class TestInitialise:

    @pytest.fixture
    def yaml(self):
        with patch('pyrite.config.settings.yaml') as mock_yaml:
            with patch('pyrite.config.settings.Path'):
                yield mock_yaml

    @pytest.fixture
    def save(self):
        with patch('pyrite.config.settings.save') as mock_save:
            yield mock_save

    def test_not_initialised(self):
        assert len(settings.settings) == 0

    def test_initialise_no_user_settings(self, yaml, save):
        yaml.load.side_effect = [
            {'tab_size': 4}, {}
        ]
        settings.initialise()

        assert settings.settings['tab_size'] == 4
        save.assert_called_once_with()

    def test_initialise_with_user_settings(self, yaml, save):
        yaml.load.side_effect = [
            {'tab_size': 4}, {'tab_size': 2}
        ]
        settings.initialise()

        assert settings.settings['tab_size'] == 2
        assert save.call_count == 0


class TestSave:

    @pytest.fixture
    def yaml(self):
        with patch('pyrite.config.settings.yaml') as mock_yaml:
            yield mock_yaml

    def test_save(self, yaml):
        with patch('pyrite.config.settings.settings', new=dict()) as mock_settings:
            mock_settings.update({'test_attr': 'yes'})

            settings.save()

            yaml.dump.assert_called_once_with(
                settings.settings, Path('~', settings.SETTINGS_FILENAME).expanduser()
            )


class TestGetters:

    @pytest.fixture
    def yaml(self):
        with patch('pyrite.config.settings.yaml') as mock_yaml:
            with patch('pyrite.config.settings.Path'):
                yield mock_yaml

    @pytest.fixture
    def log(self):
        with patch('pyrite.config.settings.log') as mock_log:
            yield mock_log

    def test_get_boolean(self, yaml):
        yaml.load.side_effect = [
            {'test_bool': True}, {}
        ]
        settings.initialise()

        assert settings.get_boolean('test_bool') is True

    def test_get_boolean_invalid(self, yaml, log):
        yaml.load.side_effect = [
            {'test_bool': True}, {'test_bool': 'foo'}
        ]
        settings.initialise()

        assert settings.get_boolean('test_bool') is True
        log.warning.assert_called()

    def test_get_int(self, yaml):
        yaml.load.side_effect = [
            {'test_int': 5}, {}
        ]
        settings.initialise()

        assert settings.get_int('test_int') == 5

    def test_get_int_invalid(self, yaml, log):
        yaml.load.side_effect = [
            {'test_int': 5}, {'test_int': 'foo'}
        ]
        settings.initialise()

        assert settings.get_int('test_int') == 5
        log.warning.assert_called()

    def test_get_float(self, yaml):
        yaml.load.side_effect = [
            {'test_float': 5.0}, {}
        ]
        settings.initialise()

        assert settings.get_float('test_float') == 5.0

    def test_get_float_invalid(self, yaml, log):
        yaml.load.side_effect = [
            {'test_float': 5.0}, {'test_float': 'foo'}
        ]
        settings.initialise()

        assert settings.get_float('test_float') == 5.0
        log.warning.assert_called()
