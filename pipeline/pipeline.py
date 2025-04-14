"""
Script that combines the extraction of book/author data from multiple data sources, converts it to 
a Pandas DataFrame, cleans the book/author data and then uploads the data to the PostgresSQL Database.
"""
import warnings
import os
import logging
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from extract import get_author_data
from transform import clean_authors_info
from load import connect_to_database, load_to_database, COLUMN_NAMES_IN_TABLES


load_dotenv()
DB_USERNAME = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_HOST = os.environ.get("DB_HOST")


def get_author_urls(conn: psycopg2.connect) -> list[str]:
    """Queries the database for all author
    returns list of dict of all authors in database"""

    query = 'SELECT author_url FROM author'
    authors_df = pd.read_sql(query, conn)
    return authors_df.to_dict(orient='list')['author_url']


def run_pipeline(author_url: str, conn: psycopg2.connect, log: logging.Logger) -> None:
    """Runs main script where data is extracted, cleaned and uploaded to the database"""

    raw_author_data = get_author_data(author_url)
    log.info("Successfully extracted author data")

    cleaned_author = clean_authors_info([raw_author_data], log)

    load_to_database(
        cleaned_author, conn, COLUMN_NAMES_IN_TABLES)
    log.info("Successfully loaded data into the database.")


def handler(event=None, context=None) -> dict:
    '''Lambda handler function that runs the pipeline
    returns status code of 200 if successful and 500 if an error is raised'''
    warnings.filterwarnings("ignore", category=UserWarning,
                            message="pandas only supports SQLAlchemy connectable")
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    connection = None
    try:
        connection = connect_to_database(
            DB_NAME, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT)
        logger.info("Connected to database")

        authors = get_author_urls(connection)
        for author in authors:
            run_pipeline(author, connection, logger)

        return {"statusCode": 200}

    except Exception as e:
        logger.error("Error: %s", e)
        return {"statusCode": 500}

    finally:
        if connection:
            connection.close()
        logger.info("Disconnected from database successfully")


if __name__ == "__main__":
    handler()
