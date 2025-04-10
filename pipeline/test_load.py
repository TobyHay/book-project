# pylint: skip-file
import pytest
import pandas as pd
import psycopg2
from unittest.mock import MagicMock, patch
from load import connect_to_database, get_database_authors, upload_new_values_to_database, get_author_id, \
    get_database_books, is_valid_port, COLUMN_NAMES_IN_TABLES, get_new_authors_or_books, format_values_to_upload, \
    get_values_to_upload, get_book_id, load_book_or_author_data_into_table, load_measurements_into_table, \
    load_to_database

DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME, DB_PORT = 'test_user', 'test_pass', 'test_host', 'test_name', '5432'


@pytest.fixture(scope='module')
def fake_connection():
    """Creates a magic mock object that acts like the psycopg2 connection object"""
    conn = MagicMock()
    return conn


@pytest.fixture(scope='module')
def fake_cursor(fake_connection):
    return fake_connection.cursor()


@pytest.fixture(scope='module')
def author_info():
    return [
        {
            "author_name": 'test_name',
            "author_url": 'test_url'
        },
        {
            'author_name': 'test_name2',
            "author_url": 'test_url2'
        }]


@pytest.fixture(scope='module')
def formatted_author_info():
    return [
        ('test_name', 'test_url'
         ),
        ('test_name2', 'test_url2'
         )]


@pytest.fixture(scope='module')
def fake_author():
    return {'author_name': 'test_name1',
            'author_url': 'test_url1',
            'books': [
                {'title': 'Book1', 'year_published': '...'},
                {'title': 'Book2', 'year_published': '...'}
            ]}


@pytest.fixture(scope='module')
def book_info():
    return [{'book_title': 'The Hunger Games (The Hunger Games, #1)',
             'big_image_url': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1586722975i/2767052.jpg',
             'small_image_url': 'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1586722975i/2767052._SX50_.jpg',
             'review_count': 237766,
             'year_published': 2008,
             'average_rating': 4.34,
             'rating_count': 9365720,
             'book_url_path': 'https://www.goodreads.com/book/show/6148028-catching-fire'
             },
            {
        'book_title': 'Catching Fire (The Hunger Games, #2)',
        'big_image_url': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1586722941i/6148028.jpg',
        'small_image_url': 'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1586722941i/6148028._SY75_.jpg',
        'review_count': 136598,
        'year_published': 2009,
        'average_rating': 4.34,
        'rating_count': 3882544,
        'book_url_path': 'https://www.goodreads.com/book/show/7260188-mockingjay'
    }]


@patch("load.psycopg2.connect")
def test_connect_to_database(mock_psycopg2_connect, fake_connection):
    mock_psycopg2_connect.return_value = fake_connection
    conn = connect_to_database(
        DB_NAME, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT)
    assert conn == fake_connection


def test_is_valid_port_invalid_port_string():
    with pytest.raises(ValueError) as err:
        DB_PORT = 'test_port'
        is_valid_port(DB_PORT)
    assert err.value.args[0] == 'Invalid Port Number: port number must be an integer'


def test_is_valid_port_invalid_port_float():
    with pytest.raises(ValueError) as err:
        DB_PORT = '53.5'
        is_valid_port(DB_PORT)
    assert err.value.args[0] == 'Invalid Port Number: port number must be an integer'


@patch("load.pd.read_sql")
def test_get_database_authors(mock_read_sql, fake_connection, author_info):
    example_author_return_value = author_info
    mock_read_sql_returns = pd.DataFrame(example_author_return_value)
    mock_read_sql.return_value = mock_read_sql_returns
    authors = get_database_authors(fake_connection)
    assert authors == example_author_return_value
    assert mock_read_sql.call_count == 1
    assert isinstance(authors, list) == True
    assert isinstance(authors[0], dict) == True


def test_upload_new_values_to_database_authors(fake_connection, capsys, formatted_author_info):
    mock_cursor = fake_connection.cursor.return_value
    upload_new_values_to_database(
        formatted_author_info, fake_connection, COLUMN_NAMES_IN_TABLES['author'], 'author')
    captured_output = capsys.readouterr().out
    printed_lines = captured_output.split("\n")
    print(printed_lines)
    assert 'Successfully inserted ' in printed_lines[-2]
    assert mock_cursor.executemany.call_count == 1


@patch("load.pd.read_sql")
def test_get_author_id_one_name_returned(mock_read_sql, fake_connection, fake_author):
    mock_read_sql_returns = pd.DataFrame(
        {"author_id": 1, "author_name": "test_name1", "author_url": "test_url1", "author_image_url": 'test_image_url'}, index=[0])
    mock_read_sql.return_value = mock_read_sql_returns
    author_id = get_author_id(fake_author, fake_connection)
    assert author_id == 1


@patch("load.pd.read_sql")
def test_get_author_id_multiple_names_returned(mock_read_sql, fake_connection, fake_author):

    mock_read_sql_returns = pd.DataFrame(
        {"author_id": [1, 2, 3],
         "author_name": ["test_name1", "test_name2", "test_name3"],
         "author_url": ["test_url1", "test_url2", "test_url3"],
         "author_image_url": ['test_image_url1', 'test_image_url2', 'test_image_url3']}, index=[0, 1, 2])
    mock_read_sql.return_value = mock_read_sql_returns
    author_id = get_author_id(fake_author, fake_connection)
    assert author_id == 1


@patch("load.pd.read_sql")
def test_get_author_id_no_names_returned_or_invalid_name(mock_read_sql, fake_connection):
    author = {'author_name': 'test_name5',
              'author_url': 'test_url5',
              'books': [
                  {'title': 'Book1', 'year_published': '...'},
                  {'title': 'Book2', 'year_published': '...'}
              ]}
    with pytest.raises(ValueError) as err:
        mock_read_sql_returns = pd.DataFrame(
            {"author_id": [1, 2, 3],
             "author_name": ["test_name1", "test_name2", "test_name3"],
             "author_url": ["test_url1", "test_url2", "test_url3"],
             "author_image_url": ['test_image_url1', 'test_image_url2', 'test_image_url3']}, index=[0, 1, 2])
        mock_read_sql.return_value = mock_read_sql_returns
        get_author_id(author, fake_connection)
    assert err.value.args[0] == 'Unable to find author ID with name provided'


@patch("load.pd.read_sql")
def test_get_database_books(mock_read_sql, fake_connection, book_info):
    book_return_value = book_info
    mock_read_sql_returns = pd.DataFrame(book_return_value)
    mock_read_sql.return_value = mock_read_sql_returns
    books = get_database_books(1, fake_connection)
    assert books == book_return_value
    assert mock_read_sql.call_count == 1
    assert isinstance(books, list) == True
    assert isinstance(books[0], dict) == True


def test_get_new_authors_or_books(formatted_author_info):
    author_values = formatted_author_info.append(('test_name3', "test_url3"))
    result = get_new_authors_or_books(author_values, formatted_author_info)
    print(result)
    assert result == [
        ('test_name3', "test_url3")]
