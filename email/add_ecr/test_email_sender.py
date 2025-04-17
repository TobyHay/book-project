'''This script uses pytest to test email_sender.py'''
# pylint: skip-file
import pytest
from unittest.mock import MagicMock, patch
import psycopg2
from email_sender import get_avg_rating_difference_since_yesterday, get_db_connection


@pytest.fixture(scope='module')
def get_mock_conn() -> MagicMock:
    '''Mocks a psycopg2 connect object with a mock cursor method.'''
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn


@patch('email_sender.get_db_connection')
def test_get_avg_rating_no_data(mock_get_db_connection, get_mock_conn: MagicMock) -> None:
    '''tests that the get_avg_rating_difference_since_yesterday returns the 
    expected outcome if there's no data available for a given author.'''
    mock_get_db_connection.return_value = get_mock_conn
    get_mock_conn.cursor.return_value.fetchall.return_value = []
    assert get_avg_rating_difference_since_yesterday(
        1) == 'No historical data for this author yet.'
