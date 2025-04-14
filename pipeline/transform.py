'''This module explores cleaning and transforming the data received from extract.py
and converting it into a valid format for loading into the database'''

import logging

EXPECTED_KEYS = 9


def clean_authors_info(authors: list[dict], log: logging.Logger) -> list[dict]:
    '''Validates and filters each author and their books, returning only valid entries'''
    valid_authors_list = []

    for author in authors:
        valid_author = validate_author(author, log)
        if valid_author:
            valid_authors_list.append(valid_author)

            valid_books_list = []

            for book in author['books']:
                valid_book = validate_book(book, log)
                if valid_book:
                    valid_books_list.append(valid_book)

            author['books'] = valid_books_list
    return valid_authors_list


def validate_author(author: dict, log: logging.Logger) -> dict:
    '''Validates the values of an author dictionary and returns the cleaned author data'''

    try:
        if len(author) != EXPECTED_KEYS:
            raise ValueError(f"Unexpected number of keys: {len(author)}")
        # Drop 0 ratings / Drop average rating 0 - What about new authors?
        author['average_rating'] = is_valid_rating(author['average_rating'])
        author['rating_count'] = is_valid_int(author['rating_count'])
        author['review_count'] = is_valid_int(author['review_count'])

        author['shelved_count'] = is_valid_int(author['shelved_count'])
        author['goodreads_followers'] = is_valid_int(
            author['goodreads_followers'])

        author['author_url'] = standardise_author_url(author['author_url'])
        author['author_image_url'] = is_valid_image_url(
            author['author_image_url'])

        for key, value in author.items():
            if value is None:
                raise ValueError(f"Missing value for '{key}'")

        return author
    except ValueError as e:
        log.error("Invalid Author %s: %s", author['author_name'], e)
        return None


def validate_book(book: dict, log: logging.Logger) -> dict:
    '''Validates all values associated to keys in the given book dictionary'''

    try:
        book['book_title'] = is_valid_book_title(book['book_title'])
        book['year_published'] = is_valid_year(book['year_published'])

        book['average_rating'] = is_valid_rating(book['average_rating'])
        book['review_count'] = is_valid_int(book['review_count'])
        book['rating_count'] = is_valid_int(book['rating_count'])

        book['book_url_path'] = is_valid_url(book['book_url_path'])
        book['big_image_url'] = is_valid_image_url(book['big_image_url'])
        book['small_image_url'] = is_valid_image_url(book['small_image_url'])

        return book
    except ValueError as e:
        log.error("Invalid Book %s: %s", book['book_title'], e)
        return None


def is_valid_book_title(title: str) -> str:
    '''Confirms the book title is a valid string
    and ensures that the book provided is not a collection of books'''

    invalid_words = ("box set", "boxset", "book set")
    if not isinstance(title, str):
        raise ValueError("Book title is not a valid string")

    for word in invalid_words:
        if word in title.lower():
            raise ValueError("Book title is a collection, not an individual")
    return title


def is_valid_int(value: str) -> int:
    '''
    Checks the provided string can be converted into a valid integer
    and checks the number is not negative

    This removes any commas from the string,
    as long as they follow the standard structure for numbers
    '''
    # Checks if the number has commas and if they are placed correctly
    str_value = str(value)
    if ',' in str_value:
        chunks = str_value.split(',')

        if not 1 <= len(chunks[0]) <= 3:
            raise ValueError("Invalid commas in number")

        for chunk in chunks[1:]:
            if len(chunk) != 3:
                raise ValueError(f"Invalid commas in number: {chunk}")

        str_value = ''.join(chunks)

    number = int(str_value)
    if number < 0:
        raise ValueError("Invalid number (number can't be negative)")
    return number


def is_valid_float(value: str) -> float:
    '''
    Checks the provided string can be converted into a valid float
    And checks the chunk of numbers to the left of the decimal is formatted as a valid integer
    This returns a float rounded to 2dp
    '''
    # Checks the decimal is placed correctly
    str_value = str(value)
    if '.' in str_value:
        chunks = str_value.split('.')
        if len(chunks) != 2:
            raise ValueError("Invalid decimal in float")

        if len(chunks[0]) == 0 or len(chunks[1]) == 0:
            raise ValueError(
                "Invalid float (missing number either side of decimal)")

        float_str = f"{str(is_valid_int(chunks[0]))}.{chunks[1]}"

    else:
        raise ValueError("Invalid float (missing decimal point)")

    # Checks the number is a valid float (and rounds to 2dp)
    return round(float(float_str), 2)


def is_valid_rating(rating: str) -> float:
    '''Checks the rating is between 0 and 5'''
    number = is_valid_float(rating)

    if number < 0:
        raise ValueError("Invalid rating (can't be less than 0)")

    if number > 5:
        raise ValueError("Invalid rating (can't be greater than 5)")
    return number


def is_valid_year(year: str) -> int:
    '''Checks the year provided is a valid 4 digit number'''
    year_str = str(year)
    if not year_str.isnumeric():
        raise ValueError("Invalid year (not a valid int)")

    if len(year_str) != 4:
        raise ValueError("Invalid year (must be 4 digits)")
    return is_valid_int(year)


def is_valid_url(url: str) -> str:
    '''Checks that the URL is a valid string and that the URL starts with http'''
    if not isinstance(url, str):
        raise ValueError("URL is not a valid string")

    if not url.startswith("http"):
        raise ValueError("Invalid URL")
    return url


def standardise_author_url(url):
    goodreads_url = "https://www.goodreads.com/author/show/"
    valid_url = is_valid_url(url)
    endpoint = valid_url.split(goodreads_url)[1]
    standardised_endpoint = endpoint.split(".")[0]
    return goodreads_url + standardised_endpoint


def is_valid_image_url(image_url: str) -> str:
    '''Checks that the image URL is valid and returns a .jpg'''
    is_valid_url(image_url)
    if not image_url.endswith(".jpg"):
        raise ValueError("URL is not a jpg image")
    return image_url


if __name__ == "__main__":
    example_author_data = {'author_name': 'Suzanne Collins',
                           'author_url': 'https://www.goodreads.com/author/show/153394.Suzanne_Collins?from_search=true&from_srp=true',
                           'average_rating': '4.28',
                           'rating_count': '18,627,481',
                           'review_count': '720,399',
                           'goodreads_followers': '112,797',
                           'shelved_count': '26,364,555',
                           'author_image_url': 'https://images.gr-assets.com/authors/1630199330p5/153394.jpg',
                           'books': [
                               {'book_title': 'The Hunger Games (The Hunger Games, #1)', 'book_url_path': 'https://www.goodreads.com/book/show/2767052-the-hunger-games', 'big_image_url': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1586722975i/2767052.jpg',
                                'small_image_url': 'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1586722975i/2767052._SX50_.jpg', 'review_count': '238,133', 'year_published': '2008', 'average_rating': ' 4.34', 'rating_count': '9,369,399'},
                               {'book_title': 'Catching Fire (The Hunger Games, #2)', 'book_url_path': 'https://www.goodreads.com/book/show/6148028-catching-fire', 'big_image_url': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1586722941i/6148028.jpg',
                                'small_image_url': 'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1586722941i/6148028._SY75_.jpg', 'review_count': '136,824', 'year_published': '2009', 'average_rating': ' 4.34', 'rating_count': '3,884,823'},
                               {'book_title': 'Mockingjay (The Hunger Games, #3)', 'book_url_path': 'https://www.goodreads.com/book/show/7260188-mockingjay', 'big_image_url': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1586722918i/7260188.jpg',
                                'small_image_url': 'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1586722918i/7260188._SY75_.jpg', 'review_count': '140,877', 'year_published': '2010', 'average_rating': ' 4.10', 'rating_count': '3,483,487'}
                           ]}

    log = logging.getLogger()
    cleaned_authors = clean_authors_info([example_author_data], log)

    for cleaned_author in cleaned_authors:
        for info in cleaned_author:
            print(f"{info}: {cleaned_author[info]}")

        for cleaned_book in cleaned_author['books']:
            print()
            print(cleaned_book)
