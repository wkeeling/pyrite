from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from pyrite.config.settings import SETTINGS_FILENAME, Settings, settings


class TestInitialise:

    @pytest.fixture
    def yaml(self):
        with patch('pyrite.config.settings.yaml') as mock_yaml:
            with patch('pyrite.config.settings.Path'):
                yield mock_yaml

    @pytest.fixture
    def save(self):
        with patch('pyrite.config.settings.settings.save') as mock_save:
            yield mock_save

    def test_not_initialised(self):
        assert len(settings) == 0

    def test_initialise_no_user_settings(self, yaml, save):
        yaml.load.side_effect = [
            {'tab_size': 4}, {}
        ]
        settings.initialise()

        assert settings['tab_size'] == 4
        save.assert_called_once_with()

    def test_initialise_with_user_settings(self, yaml, save):
        yaml.load.side_effect = [
            {'tab_size': 4}, {'tab_size': 2}
        ]
        settings.initialise()

        assert settings['tab_size'] == 2
        assert save.call_count == 0

    def test_initialise_empty_user_settings(self, yaml, save):
        yaml.load.side_effect = [
            {'tab_size': 4}, None
        ]
        settings.initialise()

        assert settings['tab_size'] == 4
        save.assert_called_once_with()


class TestSave:

    @pytest.fixture
    def yaml(self):
        with patch('pyrite.config.settings.yaml') as mock_yaml:
            yield mock_yaml

    def test_save(self, yaml):
        m = mock_open()
        with patch('pyrite.config.settings.settings', new=Settings()) as mock_settings:
            with patch('pyrite.config.settings.open', m):
                mock_settings.update({'test_attr': 'yes'})

                settings.save()

                m.assert_called_once_with(Path('~', SETTINGS_FILENAME).expanduser(), 'wt')
                yaml.dump.assert_called_once_with(settings, m())

    def test_invokes_listeners(self):
        mock = Mock()
        settings.on_save(mock.listener1)
        settings.on_save(mock.listener2)
        m = mock_open()

        with patch('pyrite.config.settings.open', m):
            settings.save()

        mock.listener1.assert_called_once_with()
        mock.listener2.assert_called_once_with()


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

    def test_getboolean(self, yaml):
        yaml.load.side_effect = [
            {'test_bool': True}, {}
        ]
        settings.initialise()

        assert settings.getboolean('test_bool') is True

    def test_getboolean_invalid(self, yaml, log):
        yaml.load.side_effect = [
            {'test_bool': True}, {'test_bool': 'foo'}
        ]
        settings.initialise()

        assert settings.getboolean('test_bool') is True
        log.warning.assert_called()

    def test_getint(self, yaml):
        yaml.load.side_effect = [
            {'test_int': 5}, {}
        ]
        settings.initialise()

        assert settings.getint('test_int') == 5

    def test_getint_invalid(self, yaml, log):
        yaml.load.side_effect = [
            {'test_int': 5}, {'test_int': 'foo'}
        ]
        settings.initialise()

        assert settings.getint('test_int') == 5
        log.warning.assert_called()

    def test_getfloat(self, yaml):
        yaml.load.side_effect = [
            {'test_float': 5.0}, {}
        ]
        settings.initialise()

        assert settings.getfloat('test_float') == 5.0

    def test_getfloat_invalid(self, yaml, log):
        yaml.load.side_effect = [
            {'test_float': 5.0}, {'test_float': 'foo'}
        ]
        settings.initialise()

        assert settings.getfloat('test_float') == 5.0
        log.warning.assert_called()
