'''This module explores cleaning and transforming the data received from extract.py
and converting it into a valid format for loading into the database'''

# Drop collections/bundles ?
# Drop 0 ratings / Drop average rating 0 - What about new authors?


def clean_authors_info(authors: list[dict]) -> list[dict]:
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
    try:
        author['author_name'] = is_valid_author_name(author['author_name'])

        author['average_rating'] = is_valid_float(author['average_rating'])
        author['rating_count'] = is_valid_int(author['rating_count'])
        author['review_count'] = is_valid_int(author['review_count'])

        author['shelved_count'] = is_valid_int(author['shelved_count'])
        author['goodreads_followers'] = is_valid_int(
            author['goodreads_followers'])

        author['author_url'] = is_valid_url(author['author_url'])
        author['author_image'] = is_valid_image_url(author['author_image'])

        return author
    except Exception as e:
        print(f"Invalid Author: {e}")
        return None


def validate_book(book: dict) -> dict:
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
        print(f"Invalid Book: {e}")
        return None


def is_valid_author_name(name):
    return name


def is_valid_book_title(title):
    if not isinstance(title, str):
        raise Exception("Book title is not a valid string")
    return title


# TODO: Numbers can't be 0 or negative
def is_valid_int(value: str) -> int:
    # Checks if the number has commas and if they are placed correctly
    str_value = str(value)
    if ',' in str_value:
        chunks = str_value.split(',')

        if not 1 <= len(chunks[0]) <= 3:
            raise Exception(f"Invalid commas in number")

        for chunk in chunks[1:]:
            if len(chunk) != 3:
                raise Exception(f"Invalid commas in number: {chunk}")

        str_value = ''.join(chunks)

    # Checks the number is a valid number
    number = int(str_value)

    # Checks the number is not negative
    if number < 0:
        raise Exception(f"invalid number")

    return number


def is_valid_float(value: str) -> float:
    # Checks the decimal is placed correctly
    str_value = str(value)
    if '.' in str_value:
        chunks = str_value.split('.')
        if len(chunks) != 2:
            raise Exception(f"Invalid decimal in float")

        if len(chunks[0]) == 0 or len(chunks[1]) == 0:
            raise Exception(f"Missing number either side of decimal")

        float_str = f"{str(is_valid_int(chunks[0]))}.{chunks[1]}"

    else:
        raise Exception("Invalid float (missing decimal point)")

    # Checks the number is a valid float (and rounds to 2dp)
    return round(float(float_str), 2)


def is_valid_year(year: str) -> int:
    yeat_str = str(year)
    if len(yeat_str) != 4:
        raise Exception("Invalid year (must be 4 digits)")
    return is_valid_int(year)


def is_valid_url(url):
    if not isinstance(url, str):
        raise Exception("URL is not a valid string")

    if not url.startswith("http"):
        raise Exception("Invalid URL")
    return url


def is_valid_image_url(image_url):
    if not isinstance(image_url, str):
        raise Exception("URL is not a valid string")

    if not image_url.startswith("http"):
        raise Exception("Invalid URL")
    return image_url


if __name__ == "__main__":

    author_data = [{
        "author_name": "Suzanne Collins",
        "author_url": "https://www.goodreads.com/author/show/153394.Suzanne_Collins?from_search=true&from_srp=true",
        "average_rating": "4.28",
        "rating_count": "18603497",
        "review_count": "716574",
        "goodreads_followers": "112666",
        "shelved_count": "26364555",
        "author_image": "https://images.gr-assets.com/authors/1630199330p5/153394.jpg",
        "books": [
            {
                "book_title": "The Hunger Games (The Hunger Games, #1)",
                "big_image_url": "https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1586722975i/2767052.jpg",
                "small_image_url": "https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1586722975i/2767052._SX50_.jpg",
                "review_count": "237,766",
                "year_published": "2008",
                "average_rating": "4.34",
                "rating_count": "9365720"
            },
            {
                "book_title": "Catching Fire (The Hunger Games, #2)",
                "big_image_url": "https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1586722941i/6148028.jpg",
                "small_image_url": "https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1586722941i/6148028._SY75_.jpg",
                "review_count": "136,598",
                "year_published": "2009",
                "average_rating": "4.34",
                "rating_count": "3882544"
            }]
    }]

    cleaned_authors = clean_authors_info(author_data)

    for author in cleaned_authors:
        for info in author:
            print(f"{info}: {author[info]}")

        for book in author['books']:
            print()
            print(book)
