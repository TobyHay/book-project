# pylint: skip-file
import pytest
from extract import get_author_name_from_url


def test_get_author_name_from_basic_url():
    url = './books/153394.Suzanne_Collins'
    assert get_author_name_from_url(url) == 'Suzanne Collins'


def test_get_author_name_from_parameter_url():
    url = './books/153394.Tul_John?parameter'
    assert get_author_name_from_url(url) == 'Tul John'


def test_get_author_name_spaces():
    url = './books/153394.Rodrigo Toby'
    assert get_author_name_from_url(url) == 'Rodrigo Toby'
    

def test_get_authors_books_url():
    pass


def test_get_authors_books_from_parameters_url():
    pass


def test_no_year_published():
    pass