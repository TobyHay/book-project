"""
Script that combines the extraction of book/author data from multiple data sources, converts it to 
a Pandas DataFrame, cleans the book/author data and then uploads the data to the PostgresSQL Database.
"""
import os
import logging
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


def main() -> None:
    """Runs main script where data is extracted, cleaned and uploaded to the database"""

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    author_url = 'https://www.goodreads.com/author/show/153394.Suzanne_Collins?from_search=true&from_srp=true'

    raw_author_data = get_author_data(author_url)
    logger.info("Successfully extracted author data")

    cleaned_author = clean_authors_info([raw_author_data], logger)

    connection = connect_to_database(
        DB_NAME, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT)
    logger.info("Connected to database")

    try:
        load_to_database(
            cleaned_author, connection, COLUMN_NAMES_IN_TABLES)
        logger.info("Successfully loaded data into the database.")
    except Exception as e:
        logger.error(f"{e}")

    finally:
        connection.close()
        logger.info("Disconnected from database successfully")


if __name__ == "__main__":
    main()
