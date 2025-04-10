"""
Script that combines the extraction of book/author data from multiple data sources, converts it to 
a Pandas DataFrame, cleans the book/author data and then uploads the data to the PostgresSQL Database.
"""
from os import environ as env
import pandas as pd
import psycopg2
import logging
from dotenv import load_dotenv
from extract import get_author_data
from transform import
from load import connect_to_database, load_to_database, COLUMN_NAMES_IN_TABLES


# def get_plant_data_from_api(url_for_data: str) -> pd.DataFrame:
#     """Returns a dataframe containing all the plant data taken from the plant API"""
#     plant_data = fetch_data_batch(url_for_data)
#     return pd.DataFrame(plant_data)


def main() -> None:
    """Runs main script where data is extracted, cleaned and uploaded to the database"""
    load_dotenv()
    logger = create_logger()

    # plant_data = get_plant_data_from_api(URL)
    # logger.info("Data retrieval from API complete.")

    # cleaned_plant_data = clean_plant_data_values(plant_data)

    connection = connect_to_database()
    logger.info("Connected to database")

    try:
        load_to_database(
            connection, 'author_data from transform', logger)
        logger.info("Successfully loaded data into the database.")
    except Exception as e:
        logger.error(f"{e}")

    finally:
        connection.close()
        logger.info("Disconnected from database successfully")


if __name__ == "__main__":
    main()
