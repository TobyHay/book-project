"""
Script that combines the extraction of book/author data from multiple data sources, converts it to 
a Pandas DataFrame, cleans the book/author data and then uploads the data to the PostgresSQL Database.
"""
from os import environ as env
import pandas as pd
import psycopg2
import logging
from dotenv import load_dotenv
from extract import get_author_data, URL
from transform import clean_plant_data_values
from load import connect_to_database, load_to_database, COLUMN_NAMES_IN_TABLES


def get_plant_data_from_api(url_for_data: str) -> pd.DataFrame:
    """Returns a dataframe containing all the plant data taken from the plant API"""
    plant_data = fetch_data_batch(url_for_data)
    return pd.DataFrame(plant_data)


def load_tables_in_database_with_data(conn: psycopg2.connect,
                                      cleaned_data: pd.DataFrame,
                                      log: logging.Logger) -> None:
    """Loads all the data into the database table by table"""
    populate_botanists(cleaned_data, conn, log)
    botanist_info = get_botanist_info(conn)
    cleaned_data = add_botanist_ids(cleaned_data, botanist_info)

    populate_origin(cleaned_data, conn, log)
    origin_info = get_origin_info(conn)
    cleaned_data = add_origin_ids(cleaned_data, origin_info)

    populate_plants(cleaned_data, conn, log)

    populate_sensor_readings(cleaned_data, conn, log)
    reading_info = get_reading_info(conn)
    cleaned_data = add_reading_ids(cleaned_data, reading_info)

    populate_alert_recordings(cleaned_data, conn, log)


def main() -> None:
    """Runs main script where data is extracted, cleaned and uploaded to the database"""
    load_dotenv()
    logger = create_logger()

    plant_data = get_plant_data_from_api(URL)
    logger.info("Data retrieval from API complete.")

    cleaned_plant_data = clean_plant_data_values(plant_data)

    connection = connect_to_database()
    logger.info("Connected to database")

    try:
        load_to_database(
            'unknown', cleaned_plant_data, logger)
        logger.info("Successfully loaded data into the database.")
    except Exception as e:
        logger.error(f"{e}")

    finally:
        connection.close()
        logger.info("Disconnected from database successfully")


if __name__ == "__main__":
    main()
