'''This module explores cleaning and transforming the data received from extract.py
and converting it into a valid format for loading into the database'''

import logging

log = logging.getLogger()


def clean_authors_info(authors: list[dict]) -> list[dict]:
    '''Validates and filters each author and their books, returning only valid entries'''
    valid_authors_list = []

    for author in authors:
        valid_author = validate_author(author)
        if valid_author:
            valid_authors_list.append(valid_author)

            valid_books_list = []

            for book in author['books']:
                valid_book = validate_book(book)
                if valid_book:
                    valid_books_list.append(valid_book)

            author['books'] = valid_books_list
    return valid_authors_list


def validate_author(author: dict) -> dict:
    '''Validates the values of an author dictionary and returns the cleaned author data'''
    expected_keys = 9
    if len(author) != expected_keys:
        raise ValueError(f"Unexpected number of keys: {len(author)}")

    try:
        author['author_name'] = is_valid_author_name(author['author_name'])

        # Drop 0 ratings / Drop average rating 0 - What about new authors?
        author['average_rating'] = is_valid_float(author['average_rating'])
        author['rating_count'] = is_valid_int(author['rating_count'])
        author['review_count'] = is_valid_int(author['review_count'])

        author['shelved_count'] = is_valid_int(author['shelved_count'])
        author['goodreads_followers'] = is_valid_int(
            author['goodreads_followers'])

        author['author_url'] = is_valid_url(author['author_url'])
        author['author_image'] = is_valid_image_url(author['author_image'])

        for key, value in author.items():
            if value is None:
                raise ValueError(f"Missing value for '{key}'")

        return author
    except Exception as e:
        log.error("Invalid Author %s: %s", author['author_name'], e)
        return None


def validate_book(book: dict) -> dict:
    '''Validates all values associated to keys in the given book dictionary'''

    try:
        book['book_title'] = is_valid_book_title(book['book_title'])
        book['year_published'] = is_valid_year(book['year_published'])

        book['average_rating'] = is_valid_float(book['average_rating'])
        book['review_count'] = is_valid_int(book['review_count'])
        book['rating_count'] = is_valid_int(book['rating_count'])

        book['big_image_url'] = is_valid_image_url(book['big_image_url'])
        book['small_image_url'] = is_valid_image_url(book['small_image_url'])

        return book
    except Exception as e:
        log.error("Invalid Book %s: %s", book['book_title'], e)
        return None


def is_valid_author_name(name):
    '''Does absolutely nothing'''
    return name


def is_valid_book_title(title):
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
    And checks the number is not negative
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
    number = round(float(float_str), 2)
    if number < 5:
        raise ValueError("Invalid rating (can't be greater than 5)")
    return


def is_valid_year(year: str) -> int:
    '''Checks the year provided is a valid 4 digit number'''
    year_str = str(year)
    if not year_str.isnumeric():
        raise ValueError("Invalid year (not a valid int)")

    if len(year_str) != 4:
        raise ValueError("Invalid year (must be 4 digits)")
    return is_valid_int(year)


def is_valid_url(url):
    '''Checks that the URL is a valid string and that the URL starts with http'''
    if not isinstance(url, str):
        raise ValueError("URL is not a valid string")

    if not url.startswith("http"):
        raise ValueError("Invalid URL")
    return url


def is_valid_image_url(image_url):
    '''Checks that the image URL is valid and returns a .jpg'''
    is_valid_url(image_url)
    if not image_url.endswith(".jpg"):
        raise ValueError("URL is not a jpg image")
    return image_url


if __name__ == "__main__":

    author_data = [{
        "author_name": "Suzanne Collins",
        "author_url": "https://www.goodreads.com/author/show/...",
        "average_rating": "4.28",
        "rating_count": "18,603497",
        "review_count": "716574",
        "goodreads_followers": "112666",
        "shelved_count": "26364555",
        "author_image": "https://images.gr-assets.com/authors/...jpg",
        "books": [
            {
                "book_title": "The Hunger Games (The Hunger Games, #1)",
                "big_image_url": "https://images-na.ssl-images-amazon.com...jpg",
                "small_image_url": "https://images-na.ssl-images-amazon.com...jpg",
                "review_count": "237,766",
                "year_published": "2008",
                "average_rating": "4.34",
                "rating_count": "9365720"
            },
            {
                "book_title": "Catching Fire (The Hunger Games, #2)",
                "big_image_url": "https://images-na.ssl-images-amazon.com...jpg",
                "small_image_url": "https://images-na.ssl-images-amazon.com...jpg",
                "review_count": "136,598",
                "year_published": "2009",
                "average_rating": "4.34",
                "rating_count": "3882544"
            }]
    }]

    cleaned_authors = clean_authors_info(author_data)

    for cleaned_author in cleaned_authors:
        for info in cleaned_author:
            print(f"{info}: {cleaned_author[info]}")

        for cleaned_book in cleaned_author['books']:
            print()
            print(cleaned_book)
