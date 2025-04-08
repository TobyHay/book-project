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

    # select everything but ID
    query = 'SELECT * FROM authors'

    authors_df = pd.read_sql(query, conn)
    return authors_df.to_dict(orient='records')


def get_database_info(conn: psycopg2.connect) -> list[dict]:
    '''Queries the databse for all books
    returns list of dict of all books in database'''

    # select everything but ID
    query = 'SELECT * FROM books'

    books_df = pd.read_sql(query, conn)
    return books_df.to_dict(orient='records')


def upload_author(author_info: list[dict], conn: psycopg2.connect) -> None:
    '''Loads given authors into database'''
    cursor = conn.cursor()

    # Add real column names to VALUES & QUERY
    values = [(author['col1'], author['col2']) for author in author_info]
    query = '''
    INSERT INTO authors (col1, col2, ...)
    VALUES (%s, %s, %s)'''
    try:
        cursor.executemany(query, values)
        conn.commit()
    except Exception as e:
        raise Exception(f"Error inserting authors to database: {e}")
    finally:
        cursor.close()


def upload_books(book_info: list[dict], conn: psycopg2.connect) -> None:
    '''Loads given books into database'''
    cursor = conn.cursor()

    # Add real column names to VALUES & QUERY
    values = [(book['col1'], book['col2']) for book in book_info]
    query = '''
    INSERT INTO books (col1, col2, ...)
    VALUES (%s, %s, %s)'''
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
    author_data = [{'col1': 'Author Name', 'col2': 'Bio', 'col3': 'Year'}]
    book_data = [
        {'col1': 'Book1', 'col2': 'Author1'},
        {'col1': 'Book2', 'col2': 'Author2'}
    ]

    db_authors = get_database_authors(connection)
    new_authors = [author for author in author_data
                   if author not in db_authors]
    upload_author(new_authors, connection)

    db_books = get_database_info(connection)
    new_books = [book for book in book_data
                 if book not in db_books]
    upload_books(new_books, connection)
