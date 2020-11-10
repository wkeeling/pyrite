from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from pyrite.config.state import STATE_DIRECTORY, STATE_FILENAME, state


class TestState:

    @pytest.fixture
    def m_open(self):
        m = mock_open()
        with patch('pyrite.config.state.open', m):
            yield m

    @pytest.fixture
    def path(self):
        with patch('pyrite.config.state.Path', spec=Path) as mock_path:
            yield mock_path

    @pytest.fixture
    def pickle(self):
        with patch('pyrite.config.state.pickle') as mock_pickle:
            mock_pickle.HIGHEST_PROTOCOL = 1
            yield mock_pickle

    def test_not_initialised(self):
        assert len(state) == 0

    def test_initialise_no_existing_state(self, m_open, path):
        m_open.side_effect = FileNotFoundError

        state.initialise()

        assert len(state) == 0
        path.assert_called_once_with('~', STATE_DIRECTORY, STATE_FILENAME)
        path().expanduser.assert_called()
        m_open.assert_called_once_with(path().expanduser(), 'rb')

    def test_initialise_existing_state(self, m_open, path, pickle):
        pickle.load.return_value = {'test': '12345'}

        state.initialise()

        assert state == {'test': '12345'}
        path.assert_called_once_with('~', STATE_DIRECTORY, STATE_FILENAME)
        path().expanduser.assert_called()
        m_open.assert_called_once_with(path().expanduser(), 'rb')
        pickle.load.assert_called_once_with(m_open())

    def test_save(self, m_open, path, pickle):
        state['test'] = '12345'

        state.save()

        path.assert_called_once_with('~', STATE_DIRECTORY, STATE_FILENAME)
        path().expanduser.assert_called()
        path().expanduser().parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        m_open.assert_called_once_with(path().expanduser(), 'wb')
        pickle.dump.assert_called_once_with({'test': '12345'}, m_open(), protocol=pickle.HIGHEST_PROTOCOL)
