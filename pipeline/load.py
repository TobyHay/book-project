'''This module explores loading information provided by transform.py to the RDS database'''

import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def connect_to_database() -> psycopg2.connect:
    '''Connects to the postgres database using information from a local env'''
    db_username = os.environ.get("DB_USERNAME")
    db_password = os.environ.get("DB_PASSWORD")
    db_port = os.environ.get("DB_PORT")
    db_name = os.environ.get("DB_NAME")
    db_host = os.environ.get("DB_HOST")

    try:
        conn = psycopg2.connect(database=db_name,
                                user=db_username,
                                password=db_password,
                                host=db_host,
                                port=db_port)
        return conn
    except Exception as e:
        raise Exception(f"Error connecting to database: {e}")


def get_database_authors(conn: psycopg2.connect) -> list[dict]:
    '''Queries the databse for all author
    returns list of dict of all authors in database'''

    query = 'SELECT name, author_url FROM author'
    authors_df = pd.read_sql(query, conn)
    return authors_df.to_dict(orient='records')


def upload_authors(author_info: list[dict], conn: psycopg2.connect) -> None:
    '''Loads given authors into database'''
    cursor = conn.cursor()

    values = [(author['name'], author['author_url'])
              for author in author_info]
    query = '''
    INSERT INTO author (name, author_url)
    VALUES (%s, %s, %s)'''
    try:
        cursor.executemany(query, values)
        conn.commit()
    except Exception as e:
        raise Exception(f"Error inserting authors to database: {e}")
    finally:
        cursor.close()


def get_author_id(author: dict, conn: psycopg2.connect) -> int:
    query = '''
    SELECT * from author
    WHERE name = %s'''

    authors_df = pd.read_sql(query, conn, params=(author['name'],))
    db_authors = authors_df.to_dict(orient='records')

    if len(db_authors) == 1:
        return db_authors[0]['author_id']

    if len(db_authors) > 1:
        for db_author in db_authors:
            if db_author['author_url'] == author['author_url']:
                return db_author['author_id']
    else:
        raise Exception("Unable to find author ID with name provided")


def get_database_books(id: int, conn: psycopg2.connect) -> list[dict]:
    '''Queries the databse for all books
    returns list of dict of all books in database'''

    query = '''
    SELECT title, release_date, image_url FROM book
    WHERE author_id = %s'''

    books_df = pd.read_sql(query, conn, params=(id,))
    return books_df.to_dict(orient='records')


def upload_books(book_info: list[dict], conn: psycopg2.connect) -> None:
    '''Loads given books into database'''
    cursor = conn.cursor()

    values = [(book['author_id'],
               book['title'],
               book['release_date'],
               book['image_url'])
              for book in book_info]
    query = '''
    INSERT INTO book (author_id, title, release_date, image_url)
    VALUES (%s, %s, %s, %s)'''
    try:
        cursor.executemany(query, values)
        conn.commit()
    except Exception as e:
        raise Exception(f"Error inserting books to database: {e}")
    finally:
        cursor.close()


def upload_author_measurement(rating_info: list[dict], conn: psycopg2.connect) -> None:
    '''Loads author rating information into database'''
    cursor = conn.cursor()

    values = [(rating['rating_count'],
               rating['average_rating'],
               rating['date_recorded'],
               rating['author_id'],
               rating['shelved_count'],
               rating['review_count'])
              for rating in rating_info]
    query = '''
    INSERT INTO author_measurement (rating_count,
                                    average_rating,
                                    date_recorded,
                                    author_id,
                                    shelved_count,
                                    review_count)
    VALUES (%s, %s, %s, %s, %s, %s)'''
    try:
        cursor.executemany(query, values)
        conn.commit()
    except Exception as e:
        raise Exception(f"Error inserting books to database: {e}")
    finally:
        cursor.close()


if __name__ == "__main__":
    connection = connect_to_database()

    # Example author and book data
    # Replace with data taken from transform.py
    book_data = [
        {'title': 'Book1', 'release_date': '...'},
        {'title': 'Book2', 'release_date': '...'}
    ]

    author_data = [{'name': 'Author Name',
                    'author_url': '....',
                    'books': [book_data]}]

    db_authors = get_database_authors(connection)

    new_authors = [author for author in author_data
                   if author not in db_authors]
    upload_authors(new_authors, connection)

    for author in author_data:
        author_id = get_author_id(author, connection)

        db_books = get_database_books(author_id, connection)
        new_books = [book for book in author['books']
                     if book not in db_books]
        upload_books(new_books, connection)

    # Include author_measurement
    # Include book_measurement
