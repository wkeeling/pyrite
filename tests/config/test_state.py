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
    def pickle(self):
        with patch('pyrite.config.state.pickle') as mock_pickle:
            mock_pickle.HIGHEST_PROTOCOL = 1
            yield mock_pickle

    def test_not_initialised(self):
        assert len(state) == 0

    def test_initialise_no_existing_state(self, m_open):
        m_open.side_effect = FileNotFoundError

        state.initialise()

        assert len(state) == 0
        m_open.assert_called_once_with(Path('~', STATE_DIRECTORY, STATE_FILENAME).expanduser(), 'rb')

    def test_initialise_existing_state(self, m_open, pickle):
        pickle.load.return_value = {'test': '12345'}

        state.initialise()

        assert state == {'test': '12345'}
        m_open.assert_called_once_with(Path('~', STATE_DIRECTORY, STATE_FILENAME).expanduser(), 'rb')
        pickle.load.assert_called_once_with(m_open())

    def test_save(self, m_open, pickle):
        state['test'] = '12345'

        state.save()

        m_open.assert_called_once_with(Path('~', STATE_DIRECTORY, STATE_FILENAME).expanduser(), 'wb')
        pickle.dump.assert_called_once_with({'test': '12345'}, m_open(), protocol=pickle.HIGHEST_PROTOCOL)
