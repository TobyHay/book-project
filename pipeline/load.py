'''This module loads data provided by transform.py to the RDS database'''

import os
import sys
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_USERNAME = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_HOST = os.environ.get("DB_HOST")
COLUMN_NAMES_IN_TABLES = {
    'book': ["author_id", "book_title", 'year_published',
             "small_image_url",
             "big_image_url", "book_url_path"],
    'author': ['author_name', 'author_url', 'author_image_url'],
    'author_measurement': ["rating_count", "average_rating",
                           "author_id", "shelved_count",
                           "review_count"],
    'book_measurement': ['book_id',
                         'rating_count', 'average_rating',
                         'review_count']
}


def connect_to_database(db_name: str, db_username: str,
                        db_password: str, db_host: str,
                        db_port: str) -> psycopg2.connect:
    """Connects to the postgres database using information from a local env"""
    try:
        is_valid_port(db_port)
    except ValueError as err:
        print(err)

    try:
        conn = psycopg2.connect(database=db_name,
                                user=db_username,
                                password=db_password,
                                host=db_host,
                                port=db_port)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit()


def is_valid_port(port_number: str) -> bool:
    """Validates if a given port is an integer that is valid"""
    if port_number.isdecimal() and '.' not in port_number:
        return True
    raise ValueError('Invalid Port Number: port number must be an integer')


def get_database_authors(conn: psycopg2.connect) -> list[dict]:
    """Queries the database for all author
    returns list of dict of all authors in database"""

    query = 'SELECT author_name, author_url, author_image_url FROM author'
    authors_df = pd.read_sql(query, conn)
    return authors_df.to_dict(orient='records')


def get_database_books_by_author(author_id_for_books: int,
                                 conn: psycopg2.connect) -> list[dict]:
    """Queries the database for all books
    returns list of dict of all books in database"""

    query = '''
    SELECT * FROM book
    WHERE author_id = %s'''

    books_df = pd.read_sql(query, conn, params=(author_id_for_books,))
    return books_df.to_dict(orient='records')


def author_match(author: dict, database_author: dict) -> bool:
    """Compares the current author to the selected author from the database
    and returns True if they have the same author url"""

    if author['author_url'] == database_author['author_url']:
        return True
    return False


def get_new_authors_or_books(new_values: list[dict],
                             database_values: list[dict], table_name: str,
                             conn: psycopg2.connect) -> list[tuple]:
    """
    Filters either the author or books by the values already 
    present in the database. In the case of the author, authors to be updated 
    are also considered (changed author_image_url)
    """
    if table_name == 'book':
        return [new_book for new_book in new_values
                if new_book not in database_values]

    new_authors = []
    for author in new_values:
        is_new = True
        for i, database_author in enumerate(database_values):
            if author_match(author, database_author):
                is_new = False
        if is_new:
            new_authors.append(author)
    return new_authors


def extract_values_from_cleaned_data(values_to_format: list[dict],
                                     column_names: list[str]) -> list[dict]:
    """Returns the necessary data values based on the specified columns passed in"""
    extracted_values_list = []
    for row in values_to_format:
        extracted_values = {}
        for column_name in column_names:
            extracted_values[column_name] = row[column_name]
        extracted_values_list.append(extracted_values)
    return extracted_values_list


def format_values_to_upload(values_to_format: list[dict],
                            column_names: list[str]) -> list[tuple]:
    """Returns the data values to be uploaded in the correct format (list[tuple])"""
    values_to_upload = []
    for row_values in values_to_format:
        row_to_upload = [row_values[column] for column in column_names]
        values_to_upload.append(tuple(row_to_upload))
    return values_to_upload


def get_values_to_upload(cleaned_data: list[dict], table_name: str,
                         conn: psycopg2.connect,
                         db_values: list[dict] = None) -> list[tuple]:
    """Returns the values that would be uploaded to the database"""

    values_to_upload = get_new_authors_or_books(
        cleaned_data, db_values, table_name, conn)

    if len(values_to_upload) == 0:
        print(f'No {table_name} values to upload to database.')
    return values_to_upload


def upload_new_values_to_database(values_to_upload: list[tuple], conn: psycopg2.connect,
                                  column_names: list[str], table_name: str) -> None:
    """Loads new values (authors/books) that aren't currently in the database into the RDS"""
    cursor = conn.cursor()

    column_count_dict = {
        6: '''VALUES (%s, %s, %s, %s, %s, %s)''',
        3: '''VALUES (%s, %s, %s)''',
        5: '''VALUES (%s, %s, %s, %s, %s)''',
        4: '''VALUES (%s, %s, %s, %s)''',
    }

    query = f'''
    INSERT INTO {table_name} ({', '.join(column_names)})'''
    query += column_count_dict[len(column_names)]

    result_message =\
        f'''Successfully inserted {len(values_to_upload)} new {table_name}s into the database.'''
    try:
        cursor.executemany(query, values_to_upload)
        conn.commit()
        print(result_message)
    except Exception as e:
        print(f"Error inserting {table_name}s to database: {e}")
        sys.exit()
    finally:
        cursor.close()


def get_author_id(author: dict, conn: psycopg2.connect) -> int:
    """Returns an author id for a given author passed in"""
    query = '''
    SELECT * from author
    WHERE author_name = %s'''

    authors_df = pd.read_sql(query, conn, params=(
        author['author_name'], ))
    db_authors = authors_df.to_dict(orient='records')

    if len(db_authors) == 1:
        return db_authors[0]['author_id']

    if len(db_authors) > 1:
        for db_author in db_authors:
            if db_author['author_url'] == author['author_url']:
                return db_author['author_id']

    raise ValueError("Unable to find author ID with name provided")


def get_book_id(book_info: dict, conn: psycopg2.connect) -> int:
    """Returns a book id based on the book passed in"""
    query = '''
    SELECT * from book
    WHERE book_title = %s AND book_url_path = %s'''

    books_df = pd.read_sql(query, conn, params=(
        book_info['book_title'], book_info['book_url_path']))
    db_books = books_df.to_dict(orient='records')

    if len(db_books) == 1:
        return db_books[0]['book_id']

    raise ValueError("Unable to find author ID with name provided")


def load_book_or_author_data_into_table(cleaned_data: list[dict], table_name: str,
                                        column_names: list[str], conn: psycopg2.connect,
                                        author_id: int = None) -> None:
    """Loads either the book or author data into the database"""
    if table_name == 'author':
        db_values = get_database_authors(conn)
    elif table_name == 'book':
        db_values = get_database_books_by_author(author_id, conn)
    else:
        raise ValueError("Invalid table given here.")

    formatted_values_for_comparison = []
    for data_values in [cleaned_data, db_values]:
        formatted_values_for_comparison.append(extract_values_from_cleaned_data(
            data_values, column_names))

    new_filtered_data = get_values_to_upload(
        formatted_values_for_comparison[0], table_name,
        conn, formatted_values_for_comparison[1])

    if new_filtered_data:
        formatted_values = format_values_to_upload(
            new_filtered_data, column_names)
        upload_new_values_to_database(
            formatted_values, conn, column_names, table_name)


def load_measurements_into_table(cleaned_data: list[dict],
                                 connection: psycopg2.connect,
                                 table_name: str,
                                 column_names: list[str]) -> None:
    """Loads the book/author measurement data into the database"""
    measurements_to_upload = format_values_to_upload(
        cleaned_data, column_names)
    upload_new_values_to_database(
        measurements_to_upload, connection, column_names, table_name)


def load_to_database(author_data: list[dict], connection: psycopg2.connect,
                     column_names: dict) -> None:
    """Loads all the tables in the database with the relevant data in order"""
    # author table
    load_book_or_author_data_into_table(
        author_data, 'author', column_names['author'], connection)

    for author in author_data:
        author_id = get_author_id(author, connection)
        for book in author['books']:
            book['author_id'] = author_id

        # book table
        load_book_or_author_data_into_table(
            author['books'], 'book', column_names['book'], connection, author_id)

        # author measurement table
        author['author_id'] = author_id
        load_measurements_into_table(
            [author], connection, 'author_measurement',
            column_names['author_measurement'])

        # book_measurement table
        for book in author['books']:
            book_id = get_book_id(book, connection)
            book['book_id'] = book_id

            load_measurements_into_table(
                [book], connection, 'book_measurement',
                column_names['book_measurement'])


def main() -> None:
    """Runs the functions required to upload all the data to the RDS"""
    db_connection = connect_to_database(
        DB_NAME, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT)

    # Example author and book data
    author_list = \
        [{'author_name': 'Suzanne Collins',
          'author_url':
            'https://www.goodreads.com/author/show/153394',
          'average_rating': 4.28,
          'rating_count': 18603497,
          'review_count': 716574,
          'goodreads_followers': 112666,
          'shelved_count': 26364555,
          'author_image_url':
            'https://images.gr-assets.com/authors/1630199330p5/153394.jpg',
          'books': [
              {'book_title': 'The Hunger Games (The Hunger Games, #1)',
               'big_image_url':
               'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1586722975i/2767052.jpg',
               'small_image_url':
               'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1586722975i/2767052._SX50_.jpg',
               'review_count': 237766,
               'year_published': 2008,
               'average_rating': 4.34,
               'rating_count': 9365720,
               'book_url_path': 'https://www.goodreads.com/book/show/6148028-catching-fire'
               },
              {
                  'book_title': 'Catching Fire (The Hunger Games, #2)',
                  'big_image_url':
                  'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1586722941i/6148028.jpg',
                  'small_image_url':
                  'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1586722941i/6148028._SY75_.jpg',
                  'review_count': 136598,
                  'year_published': 2009,
                  'average_rating': 4.34,
                  'rating_count': 3882544,
                  'book_url_path': 'https://www.goodreads.com/book/show/7260188-mockingjay'
              }
          ]}
         ]
    new_author = [{'author_name': 'J.K. Rowling', 'author_url': 'https://www.goodreads.com/author/show/1077326.J_K_Rowling', 'average_rating': 4.46, 'rating_count': 39332467, 'review_count': 922525, 'goodreads_followers': 230760, 'shelved_count': 58361859, 'author_image_url': 'https://images.gr-assets.com/authors/1596216614p5/1077326.jpg', 'books': [{'book_title': 'Harry Potter and the Sorcerer’s Stone (Harry Potter, #1)', 'book_url_path': 'https://www.goodreads.com/book/show/42844155-harry-potter-and-the-sorcerer-s-stone', 'big_image_url': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1598823299i/42844155.jpg', 'small_image_url': 'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1598823299i/42844155._SX50_.jpg', 'review_count': 180344, 'year_published': 1997, 'average_rating': 4.47, 'rating_count': 10876683}, {'book_title': 'Harry Potter and the Prisoner of Azkaban (Harry Potter, #3)', 'book_url_path': 'https://www.goodreads.com/book/show/5.Harry_Potter_and_the_Prisoner_of_Azkaban', 'big_image_url': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1630547330i/5.jpg', 'small_image_url': 'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1630547330i/5._SY75_.jpg', 'review_count': 95065, 'year_published': 1999, 'average_rating': 4.58, 'rating_count': 4585773}, {'book_title': 'Harry Potter and the Chamber of Secrets (Harry Potter, #2)', 'book_url_path': 'https://www.goodreads.com/book/show/15881.Harry_Potter_and_the_Chamber_of_Secrets', 'big_image_url': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1474169725i/15881.jpg', 'small_image_url': 'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1474169725i/15881._SY75_.jpg', 'review_count': 89961, 'year_published': 1998, 'average_rating': 4.43, 'rating_count': 4272242}, {'book_title': 'Harry Potter and the Deathly Hallows (Harry Potter, #7)', 'book_url_path': 'https://www.goodreads.com/book/show/58613224-harry-potter-and-the-deathly-hallows', 'big_image_url': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1627042661i/58613224.jpg', 'small_image_url': 'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1627042661i/58613224._SY75_.jpg', 'review_count': 93664, 'year_published': 2007, 'average_rating': 4.62, 'rating_count': 3953751}, {
        'book_title': 'Harry Potter and the Goblet of Fire (Harry Potter, #4)', 'book_url_path': 'https://www.goodreads.com/book/show/58613424-harry-potter-and-the-goblet-of-fire', 'big_image_url': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1627044952i/58613424.jpg', 'small_image_url': 'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1627044952i/58613424._SY75_.jpg', 'review_count': 78441, 'year_published': 2000, 'average_rating': 4.57, 'rating_count': 3999710}, {'book_title': 'Harry Potter and the Order of the Phoenix (Harry Potter, #5)', 'book_url_path': 'https://www.goodreads.com/book/show/58613451-harry-potter-and-the-order-of-the-phoenix', 'big_image_url': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1627045351i/58613451.jpg', 'small_image_url': 'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1627045351i/58613451._SY75_.jpg', 'review_count': 72089, 'year_published': 2003, 'average_rating': 4.5, 'rating_count': 3631399}, {'book_title': 'Harry Potter and the Half-Blood Prince (Harry Potter, #6)', 'book_url_path': 'https://www.goodreads.com/book/show/58613345-harry-potter-and-the-half-blood-prince', 'big_image_url': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1627043894i/58613345.jpg', 'small_image_url': 'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1627043894i/58613345._SY75_.jpg', 'review_count': 65211, 'year_published': 2005, 'average_rating': 4.58, 'rating_count': 3509003}, {'book_title': 'Harry Potter and the Cursed Child: Parts One and Two (Harry Potter, #8)', 'book_url_path': 'https://www.goodreads.com/book/show/29056083-harry-potter-and-the-cursed-child', 'big_image_url': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1470082995i/29056083.jpg', 'small_image_url': 'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1470082995i/29056083._SY75_.jpg', 'review_count': 76039, 'year_published': 2016, 'average_rating': 3.48, 'rating_count': 1094261}, {'book_title': 'The Tales of Beedle the Bard (Hogwarts Library, #3)', 'book_url_path': 'https://www.goodreads.com/book/show/3950967-the-tales-of-beedle-the-bard', 'big_image_url': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1630876355i/3950967.jpg', 'small_image_url': 'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1630876355i/3950967._SX50_.jpg', 'review_count': 19409, 'year_published': 2008, 'average_rating': 4.03, 'rating_count': 504198}]}]

    try:
        load_to_database(author_list, db_connection, COLUMN_NAMES_IN_TABLES)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit()
    finally:
        db_connection.close()


if __name__ == "__main__":
    main()
