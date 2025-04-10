# pylint: skip-file
import pytest
from bs4 import BeautifulSoup
import extract


@pytest.fixture
def mock_book_page_soup():
    '''
    Simulates the soup for the HTML for a goodreads book page used for testing.
    '''
    with open('test_book_page.html', 'r', encoding="utf-8") as f:
        html_content = f.read()
    return BeautifulSoup(html_content, "lxml")


@pytest.fixture
def mock_book_list_page_soup():
    '''
    Simulates the soup for the HTML for a goodreads book list page used for testing.
    '''
    with open('test_book_list.html', 'r', encoding="utf-8") as f:
        html_content = f.read()
    return BeautifulSoup(html_content, "lxml")


@pytest.fixture
def mock_author_page_soup():
    '''
    Simulates the soup for the HTML for a goodreads author page used for testing.
    '''
    with open('test_author_page.html', 'r', encoding="utf-8") as f:
        html_content = f.read()
    return BeautifulSoup(html_content, "lxml")


def test_get_authors_books_url(mock_author_page_soup):
    '''
    Tests 'get_author_books()' retrieves the correct content from
    a mock soup of an author page
    '''
    result = extract.get_authors_books_url(mock_author_page_soup)
    assert result == 'https://www.goodreads.com/author/list/153394.Suzanne_Collins?page=1&per_page=100'


def test_get_author_name(mock_author_page_soup):
    '''
    Tests 'get_author_name()' retrieves the correct content from
    a mock soup of an author page
    '''
    result = extract.get_author_name(mock_author_page_soup)
    assert result == 'Suzanne Collins'


def test_get_follower_count(mock_author_page_soup):
    '''

    '''
    result = extract.get_author_follower_count(mock_author_page_soup)
    assert result == '112,779'


def test_get_author_aggregate_data(mock_author_page_soup):
    '''

    '''
    result = extract.get_author_aggregate_data(mock_author_page_soup)
    assert result == {
        'average_rating': '4.28',
        'rating_count': '18,624,440',
        'review_count': '719,914',
        'goodreads_followers': '112,779'
    }


def test_get_book_small_image_url(mock_book_page_soup):
    '''

    '''
    result = (mock_book_page_soup)
