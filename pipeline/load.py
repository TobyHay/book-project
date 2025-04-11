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


def is_new_author(author: dict, database_author: dict) -> bool:
    """Returns a boolean of True if an author is new (not in the database), 
    otherwise false"""
    if author['author_name'] != database_author['author_name'] and \
            author['author_url'] != database_author['author_url']:
        return True
    return False


def update_image_url_of_author(authors_to_be_updated: list[dict],
                               conn: psycopg2.connect) -> None:
    """Updates an existing author with the new author image url"""
    for author in authors_to_be_updated:
        author_id = get_author_id(author, conn)
        author['author_id'] = author_id

    cursor = conn.cursor()
    query = """UPDATE author
            SET author_image_url = %s
            WHERE author_id = %s;"""
    authors_to_be_updated = format_values_to_upload(
        authors_to_be_updated, ['author_image_url', 'author_id'])

    try:
        cursor.executemany(
            query, authors_to_be_updated)
        conn.commit()
    except Exception as err:
        print(err)
    finally:
        cursor.close()


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

    update_authors = []
    new_authors = []
    for author in new_values:
        for i, database_author in enumerate(database_values):
            if not is_new_author(author, database_author) and \
                    author['author_image_url'] != database_author['author_image_url']:
                update_authors.append(author)

            if is_new_author(author, database_author) and \
                    author not in update_authors and i == len(database_values)-1:
                new_authors.append(author)

    if update_authors:
        update_image_url_of_author(update_authors, conn)

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
        upload_new_values_to_database(
            new_filtered_data, conn, column_names, table_name)


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
            'https://www.goodreads.com/author/show/153394.Suzanne_Collins?from_search=true&from_srp=true',
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

    try:
        load_to_database(author_list, db_connection, COLUMN_NAMES_IN_TABLES)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit()
    finally:
        db_connection.close()


if __name__ == "__main__":
    main()
