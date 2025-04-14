# pylint: skip-file
import pytest
from bs4 import BeautifulSoup
from unittest.mock import patch
import extract


@pytest.fixture
def mock_book_page_soup():
    '''Simulates the soup for the HTML for a goodreads book page used for testing.'''
    with open('./test_book_page.html', 'r', encoding="utf-8") as f:
        html_content = f.read()
    return BeautifulSoup(html_content, "lxml")


@pytest.fixture
def mock_book_list_page_soup():
    '''Simulates the soup for the HTML for a goodreads book list page used for testing.'''
    with open('./test_book_list.html', 'r', encoding="utf-8") as f:
        html_content = f.read()
    return BeautifulSoup(html_content, "lxml")


@pytest.fixture
def mock_book_list_page_containers_sliced(mock_book_list_page_soup):
    '''Gets a list of the html for the top 2 book containers in the 
    goodreads author's book list page.'''
    return mock_book_list_page_soup.find_all("tr")[:1]


@pytest.fixture
def mock_book_list_page_container_soup(mock_book_list_page_containers_sliced):
    return mock_book_list_page_containers_sliced[0]


@pytest.fixture
def mock_author_page_soup():
    '''Simulates the soup for the HTML for a goodreads author page used for testing.'''
    with open('./test_author_page.html', 'r', encoding="utf-8") as f:
        html_content = f.read()
    return BeautifulSoup(html_content, "lxml")


def test_get_authors_books_url(mock_author_page_soup):
    '''Tests 'get_author_books()' retrieves the correct 
    content from a mock soup of an author page'''
    result = extract.get_authors_books_url(mock_author_page_soup)
    assert result == 'https://www.goodreads.com/author/list/153394.Suzanne_Collins?page=1&per_page=10'


def test_get_author_name(mock_author_page_soup):
    '''Tests 'get_author_name()' retrieves the correct content from
    a mock soup of an author page'''
    result = extract.get_author_name(mock_author_page_soup)
    assert result == 'Suzanne Collins'


def test_get_follower_count(mock_author_page_soup):
    ''''''
    result = extract.get_author_follower_count(mock_author_page_soup)
    assert result == '112,779'


def test_get_author_aggregate_data(mock_author_page_soup):
    ''''''
    result = extract.get_author_aggregate_data(mock_author_page_soup)
    assert result == {
        'average_rating': '4.28',
        'rating_count': '18,624,440',
        'review_count': '719,914',
        'goodreads_followers': '112,779'
    }


def test_get_book_small_image_url(mock_book_list_page_container_soup):
    '''Tests 'get_book_small_image_url' retrieves the correct content 
    from a mock soup of a html container for a book from the book list html.'''
    result = extract.get_book_small_image_url(
        mock_book_list_page_container_soup)
    assert result == 'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1586722975i/2767052._SX50_.jpg'


def test_get_book_title(mock_book_list_page_container_soup):
    '''Tests 'get_book_title' retrieves the correct content from a mock soup of
    a html container for a book from the book list html.'''
    result = extract.get_book_title(
        mock_book_list_page_container_soup)
    assert result == 'The Hunger Games (The Hunger Games, #1)'


def test_get_book_aggregate_data(mock_book_list_page_container_soup):
    '''Tests 'get_book_aggregate_data' retrieves the correct content
      from a html container for a book from the book list html.'''
    result = extract.get_book_aggregate_data(
        mock_book_list_page_container_soup)
    assert result == {'average_rating': ' 4.34',
                      'rating_count': '9,369,265'}


def test_get_year_published(mock_book_list_page_container_soup):
    '''Tests 'get_year_published' retrieves the correct content
      from a html container for a book from the book list html'''
    result = extract.get_year_published(mock_book_list_page_container_soup)
    assert result == '2008'


def test_get_individual_book_data(mock_book_list_page_container_soup):
    '''Tests 'get_individual_book_data' retrieves the correct content
    from a html container for a book from the book list html'''
    result = extract.get_individual_book_data(
        mock_book_list_page_container_soup)
    assert result == {
        'average_rating': ' 4.34',
        'big_image_url': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1586722975i/2767052.jpg',
        'book_title': 'The Hunger Games (The Hunger Games, #1)',
        'book_url_path': 'https://www.goodreads.com/book/show/2767052-the-hunger-games',
        'rating_count': '9,369,265',
        'review_count': '238,340',
        'small_image_url': 'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1586722975i/2767052._SX50_.jpg',
        'year_published': '2008'
    }
