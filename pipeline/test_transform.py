# pylint: skip-file
import pytest
import logging
from copy import deepcopy
from transform import (is_valid_int,
                       is_valid_float,
                       is_valid_year,
                       is_valid_url,
                       validate_author,
                       validate_book,
                       clean_authors_info)

log = logging.getLogger()


PERFECTLY_FORMATTED_BOOK = {
    "book_title": "Catching Fire",
    'book_url_path': 'https://www.goodreads.com/book/show/6148028-catching-fire',
    "big_image_url": "https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1586722941i/6148028.jpg",
    "small_image_url": "https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1586722941i/6148028._SY75_.jpg",
    "review_count": 136598,
    "year_published": 2009,
    "average_rating": 4.34,
    "rating_count": 3882544
}

PERFECTLY_FORMATTED_AUTHOR = {
    "author_name": "Suzanne Collins",
    "average_rating": 4.28,
    "rating_count": 18603497,
    "review_count": 716574,
    "goodreads_followers": 112666,
    "shelved_count": 26364555,
    "author_url": "https://www.goodreads.com/author/show/153394.Suzanne_Collins?from_search=true&from_srp=true",
    "author_image_url": "https://images.gr-assets.com/authors/1630199330p5/153394.jpg",
    "books": []
}


VALID_BOOK_1 = {
    "book_title": "The Hunger Games (The Hunger Games, #1)",
    'book_url_path': 'https://www.goodreads.com/book/show/2767052-the-hunger-games',
    "big_image_url": "https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1586722975i/2767052.jpg",
    "small_image_url": "https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1586722975i/2767052._SX50_.jpg",
    "review_count": "237,766",
    "year_published": "2008",
    "average_rating": "4.34",
    "rating_count": "9365720"
}

VALID_BOOK_2 = {
    "book_title": "Catching Fire (The Hunger Games, #2)",
    'book_url_path': 'https://www.goodreads.com/book/show/6148028-catching-fire',
    "big_image_url": "https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1586722941i/6148028.jpg",
    "small_image_url": "https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1586722941i/6148028._SY75_.jpg",
    "review_count": "136,598",
    "year_published": "2009",
    "average_rating": "4.34",
    "rating_count": "3882544"
}

VALID_AUTHOR_DATA = {
    "author_name": "Suzanne Collins",
    "author_url": "https://www.goodreads.com/author/show/153394.Suzanne_Collins?from_search=true&from_srp=true",
    "average_rating": "4.28",
    "rating_count": "18603497",
    "review_count": "716574",
    "goodreads_followers": "112666",
    "shelved_count": "26364555",
    "author_image_url": "https://images.gr-assets.com/authors/1630199330p5/153394.jpg",
    "books": [VALID_BOOK_1, VALID_BOOK_2]
}


# Test Integers
@pytest.mark.parametrize("valid_value, output", [
    ("123", 123),
    (123, 123),
    ("1,234", 1234)])
def test_valid_integers(valid_value, output):
    assert is_valid_int(valid_value) == output


@pytest.mark.parametrize("invalid_values", [
    None, "", "String", "12.34", "1234,567", "-1234"])
def test_invalid_integers(invalid_values):
    with pytest.raises(Exception):
        is_valid_int(invalid_values)


# Test Floats
@pytest.mark.parametrize("valid_value, output", [
    ("123.4", 123.4),
    (123.4, 123.4),
    ("1,234.5", 1234.5),
    (123.456, 123.46)])
def test_valid_floats(valid_value, output):
    assert is_valid_float(valid_value) == output


@pytest.mark.parametrize("invalid_values", [
    None, "", "String", "1234,567.89", "-1234.5", -123.45])
def test_invalid_floats(invalid_values):
    with pytest.raises(Exception):
        is_valid_float(invalid_values)


# Test Year
@pytest.mark.parametrize("valid_year, output", [
    ("1987", 1987),
    (2000, 2000)])
def test_valid_years(valid_year, output):
    assert is_valid_year(valid_year) == output


@pytest.mark.parametrize("invalid_year", [
    None, "", "String", "0", "19876", 19876])
def test_invalid_years(invalid_year):
    with pytest.raises(Exception):
        is_valid_year(invalid_year)


# Test URLs
@pytest.mark.parametrize("valid_url", [
    "https://www.goodreads.com/author/show/153394.Suzanne_Collins?from_search=true&from_srp=true",
    "https://images.gr-assets.com/authors/1630199330p5/153394.jpg"])
def test_valid_url(valid_url):
    assert is_valid_url(valid_url) is not None


@pytest.mark.parametrize("invalid_url", [
    None,
    "String",
    "htt://images.gr-assets.com/authors/1630199330p5/153394.jpg"])
def test_invalid_url(invalid_url):
    with pytest.raises(Exception):
        is_valid_url(invalid_url)


# Test Book Cleaning
def test_perfectly_formatted_book():
    book_copy = deepcopy(PERFECTLY_FORMATTED_BOOK)
    assert validate_book(book_copy, log) == PERFECTLY_FORMATTED_BOOK


def test_valid_book():
    book_copy = deepcopy(VALID_BOOK_1)
    assert validate_book(book_copy, log) is not None


def test_invalid_book():
    book_copy = deepcopy(VALID_BOOK_1)
    book_copy['review_count'] = None
    assert validate_book(book_copy, log) is None


# Test Author Cleaning
def test_perfectly_formatted_author():
    author_copy = deepcopy(PERFECTLY_FORMATTED_AUTHOR)
    assert validate_author(author_copy, log) == PERFECTLY_FORMATTED_AUTHOR


def test_valid_author():
    author_copy = deepcopy(VALID_AUTHOR_DATA)
    assert validate_author(author_copy, log) is not None


def test_invalid_author():
    author_copy = deepcopy(VALID_AUTHOR_DATA)
    author_copy['review_count'] = None
    assert validate_author(author_copy, log) is None


# Test Main Function
def test_clean_authors():
    author_copy = deepcopy(VALID_AUTHOR_DATA)
    assert clean_authors_info([author_copy], log) is not None
