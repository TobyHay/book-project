'''A script that creates a Streamlit dashboard using book data from the RDS'''
import urllib.request
from os import environ as ENV
import logging
import pandas as pd
import requests
import streamlit as st
import psycopg2
from dotenv import load_dotenv
from bs4 import BeautifulSoup


st.set_page_config(layout="wide")


load_dotenv()


GOODREADS_URL = "https://www.goodreads.com/author/show/"


def connect_to_database() -> psycopg2.connect:
    '''Connects to the postgres database using information from a local env'''

    try:
        connection = psycopg2.connect(database=ENV.get("DB_NAME"),
                                      user=ENV.get("DB_USERNAME"),
                                      password=ENV.get("DB_PASSWORD"),
                                      host=ENV.get("DB_HOST"),
                                      port=ENV.get("DB_PORT"))
        return connection
    except Exception as e:
        raise Exception(f"Error connecting to database: {e}")


def validate_author_url(author_url: str) -> bool:
    '''Checks if author URL contains desired string pattern, and returns 200 status code'''
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )}
    if "www.goodreads.com/author/show/" not in author_url:
        st.write(
            ":x: Incorrect URL format - please review the above instructions and try again.")
        return False
    if requests.get(author_url, headers=headers, timeout=50).status_code != 200:
        st.write(requests.get(author_url, headers=headers, timeout=50).status_code)
        st.write(
            ":x: Unable to reach given URL: please check the URL link works for you in your browser.")
        return False
    return True


def is_author_in_system(author_url: str, conn: psycopg2.connect) -> bool:
    '''Checks if author URL is already in the database'''
    author = pd.read_sql("SELECT author_url FROM author;", conn)
    if author_url in author['author_url']:
        return True
    return False


def infer_author_name(url: str) -> str:
    '''Attempts to extract author name from URL for display purposes'''
    try:
        author_name = " ".join(url.split(".")[-1].split("_"))
        if not author_name.strip():
            raise ValueError("Unknown Author")
        return author_name
    except Exception:
        return "Unknown Author"


def validate_email(email: str) -> bool:
    '''Basic validation checks on user-submitted email address'''
    if "@" not in email:
        return False
    if "." not in email:
        return False
    return True


def get_soup(url: str) -> BeautifulSoup:
    '''Returns a beautifulsoup HTML parser for a given goodreads.com url.'''
    with urllib.request.urlopen(url) as page:
        html = page.read().decode('utf-8')
    return BeautifulSoup(html, "lxml")


def get_author_name(author_soup: BeautifulSoup) -> dict:
    '''gets author name from the soup for the author goodreads page'''
    author_name = author_soup.find("h1", class_="authorName").text
    return author_name.strip()


def get_author_image(author_soup: BeautifulSoup) -> dict:
    '''Gets the author image from the author's goodread page.'''
    return author_soup.find('img', itemprop="image").get('src')


def get_author_data(author_url: str) -> dict:
    '''Scrapes average_rating, rating_count and review_count
      for a given goodreads.com author url.'''
    author_soup: BeautifulSoup = get_soup(author_url)

    author_name = get_author_name(author_soup)
    author_image_url = get_author_image(author_soup)
    author_data = {
        'author_name': author_name,
        'author_url': author_url,
        'author_image_url': author_image_url
    }
    return author_data


def is_valid_url(url: str) -> str:
    '''Checks that the URL is a valid string and that the URL starts with http'''
    if not isinstance(url, str):
        raise ValueError("URL is not a valid string")

    if not url.startswith("http"):
        raise ValueError("Invalid URL")
    return url


def is_valid_image_url(image_url: str) -> str:
    '''Checks that the image URL is valid and returns a .jpg'''
    is_valid_url(image_url)
    if not image_url.endswith(".jpg"):
        raise ValueError("URL is not a jpg image")
    return image_url


def standardise_author_url(url: str) -> str:
    '''Standardises the author url to only include the goodreads url
    and the goodreads author id which is the endpoint'''
    valid_url = is_valid_url(url)
    endpoint = valid_url.split(GOODREADS_URL)[1]
    standardised_endpoint = endpoint.split(".")[0]
    return GOODREADS_URL + standardised_endpoint


def mini_etl(author_url: str, conn: psycopg2.connect):
    '''A mini version of the URL that inserts author information only into the DB'''
    author_data = get_author_data(author_url)
    try:
        is_valid_url(author_url)
        is_valid_image_url(author_data['author_image_url'])
        author_data['author_url'] = standardise_author_url(author_url)

        duplicate_check_query = "SELECT COUNT(*) FROM author WHERE author_url = %s"

        with conn.cursor() as cursor:
            cursor.execute(duplicate_check_query, (author_data['author_url'],))
            result = cursor.fetchone()
            if result[0] > 0:
                return "duplicate"

        insert_query = "INSERT INTO author(author_name, author_url, author_image_url) VALUES (%s, %s, %s)"

        with conn.cursor() as cursor:

            cursor.execute(
                insert_query, (author_data['author_name'], author_data['author_url'], author_data['author_image_url']))
            conn.commit()

        return "success"

    except ValueError as e:
        return f"failure: valueerror: {e}"
    except KeyError as e:
        return f"failure: keyerror: {e}"
    except psycopg2.Error as e:
        return f"failure: database error: {e}"


def summary_cols(conn: psycopg2.connect) -> None:
    '''Simple Streamlit summary statistics'''
    col1, col2, col3 = st.columns(3)

    with col1:

        books = len(pd.read_sql("SELECT * FROM book;", conn))
        books_since_yesterday = len(pd.read_sql(
            "SELECT * FROM book WHERE date_added >= DATE_TRUNC('day', NOW() - INTERVAL '1 day');", conn))

        st.metric("Number of books registered in our database",
                  books, f"{books_since_yesterday} books since yesterday", border=True)

    with col2:

        authors = len(pd.read_sql("SELECT * FROM author;", conn))
        authors_since_yesterday = len(pd.read_sql(
            "SELECT * FROM author WHERE date_added >= DATE_TRUNC('day', NOW() - INTERVAL '1 day');", conn))

        st.metric("Number of authors signed up for tracking",
                  authors, f"{authors_since_yesterday} authors since yesterday", border=True)

    with col3:

        publishers = len(pd.read_sql("SELECT * FROM publisher;", conn))
        publishers_since_yesterday = len(pd.read_sql(
            "SELECT * FROM publisher WHERE date_subscribed >= DATE_TRUNC('day', NOW() - INTERVAL '1 day');", conn))

        st.metric("Number of publishers using the service",
                  publishers, f"{publishers_since_yesterday} publishers since yesterday", border=True)


def author_request_form(conn: psycopg2.connect, logger: logging.Logger) -> None:
    '''Form for requesting author via URL, triggers ETL pipeline'''
    st.write("Please paste your chosen author's URL from GoodReads.com, in the following format: https://www.goodreads.com/author/show/153394.Suzanne_Collins")
    st.write("Note that this page must be the overall author page; .../author/show/... should be in the URL.")
    author_url_input = st.text_input(
        "Paste an author's URL here:", key="Author URL input")

    submitted_author_request = st.form_submit_button(
        'Add this author to the database')

    if submitted_author_request:
        author_name = infer_author_name(author_url_input)
        if "/" in author_name:
            author_name = "author"
        st.write(
            f":hourglass_flowing_sand: Adding {author_name} to the author database...")
        if validate_author_url(author_url_input) is True:
            logger.info(f"PASSED: Valid URL check - {author_url_input}")
            st.write(
                ":hourglass: Loading the author's most up-to-date information...")
            try:
                result = mini_etl(author_url_input, conn)
                if result == "duplicate":
                    logger.info(
                        f"PASSED: Duplicate received - {author_url_input}")
                    st.write(
                        ":pushpin: This author is already in our database! Please enter another one.")
                elif result == "success":
                    st.write(
                        f":white_check_mark: Information loaded - head over to the visualisations page tomorrow for in-depth analysis of {author_name}'s work!")
                else:
                    logger.info(
                        f"FAILED: mini-etl returning error - {author_url_input}")
                    st.write(
                        ":x: Something went wrong when getting author's information - please try again, or contact the devs.")
            except Exception as e:
                st.write(e)
                logger.info(e)
                logger.info(
                    f"FAILED: Pipeline - {author_url_input}")
                st.write(
                    ":x: Something went wrong when getting author's information - please try again, or contact the devs.")


def get_author_choice_id(publisher_author_choice, conn):
    '''Returns the ID of the author chosen by the prospective publisher'''
    author_id = pd.read_sql(
        "SELECT author_id FROM author WHERE author_name = %s", conn, params=(publisher_author_choice, ))['author_id'].iloc[0]
    int_author_id = int(author_id)
    return int_author_id


def get_publisher_id(publisher_email_input, conn):
    '''Returns a publisher ID using email as reference, if assigned, else returns None'''
    query = "SELECT publisher_id FROM publisher WHERE publisher_email = %s"
    with conn.cursor() as cursor:
        cursor.execute(query, (publisher_email_input,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None


def insert_new_publisher(publisher_email_input, publisher_name_input, conn):
    '''Inserts a new publisher into the publisher table'''
    query = "INSERT INTO publisher (publisher_name, publisher_email) VALUES (%s, %s) RETURNING publisher_id"
    with conn.cursor() as cursor:
        cursor.execute(query, (publisher_name_input, publisher_email_input))
        new_publisher_id = cursor.fetchone()[0]
        int_new_publisher_id = int(new_publisher_id)
        conn.commit()
        return int_new_publisher_id


def is_author_already_assigned_to_specific_publisher(publisher_id, author_choice_id, conn):
    '''Checks whether the publisher is already assigned to the requested author'''
    query = "SELECT author_assignment_id FROM author_assignment WHERE publisher_id = %s AND author_id = %s"
    with conn.cursor() as cursor:
        cursor.execute(query, (publisher_id, author_choice_id))
        return cursor.fetchone() is not None


def assign_author_to_publisher(publisher_id, author_choice_id, conn):
    '''Inserts an assignment row into the author_assignment table'''
    query = "INSERT INTO author_assignment (publisher_id, author_id) VALUES (%s, %s)"
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (publisher_id, author_choice_id))
            conn.commit()
            return "success"
    except Exception as e:
        return f"failure - {e}"


def publisher_signup_form(conn: psycopg2.connect, logger: logging.Logger) -> None:
    '''Form for publishers to sign up to author emails'''
    st.write("""Please enter your name, email, and the select one of our tracked authors from the drop-down menu. To subscribe to an email report for multiple authors, please submit the form once for each author URL.""")

    publisher_name_input = st.text_input(
        "Publisher name to receive updates:", key="Publisher name input")
    publisher_name_input = publisher_name_input[:50]

    publisher_email_input = st.text_input(
        "Publisher email to receive updates:", key="Publisher email input")
    publisher_email_input = publisher_email_input[:50]

    list_of_authors = pd.read_sql("SELECT author_name FROM author;", conn)[
        'author_name'].unique()
    publisher_author_choice = st.selectbox(
        "select author", list_of_authors)

    submitted_publisher_submission = st.form_submit_button(
        "Add this author to your mailing list")

    if submitted_publisher_submission:
        if validate_email(publisher_email_input):
            author_choice_id = get_author_choice_id(
                publisher_author_choice, conn)

            publisher_id = get_publisher_id(publisher_email_input, conn)
            if publisher_id:
                if is_author_already_assigned_to_specific_publisher(publisher_id, author_choice_id, conn):
                    st.write(
                        f":pushpin: The address {publisher_email_input} is already subscribed to {publisher_author_choice}! You will receive your next daily report tomorrow morning.")
                    return
            if not publisher_id:
                publisher_id = insert_new_publisher(publisher_email_input,
                                                    publisher_name_input, conn)

            result = assign_author_to_publisher(
                publisher_id, author_choice_id, conn)
            if result == "success":
                st.write(
                    f":white_check_mark: Successfully subscribed {publisher_name_input} ({publisher_email_input}) to {publisher_author_choice}! You will receive your first daily report tomorrow morning.")
            else:
                st.write(
                    ":x: Something went wrong when signing you up - please try again, or contact the devs.")
                st.write(f"Error: {result}")
        else:
            st.write(
                ":x: Invalid email address - please double-check it and try again!")


def streamlit(conn, logger) -> None:
    '''Main Streamlit script for the dashboard'''

    st.title(":books: Publisher Dashboard - Author Tracker! :books:")
    st.write("Welcome to the Publisher Dashboard! On this page, you'll be able to request authors to be tracked and submit email report preferences.")
    st.write("On the next page, summary statistics for some of our most popular authors can be seen. Use our interactive features to learn all about your favourite author!")

    summary_cols(conn)

    st.header("Are you a bookworm? :book: :worm:")
    st.write("Request your favourite book or author to be added to our database! Authors or books added will be included in our summary statistics on the next page, and can be requested for tailored reports below once added.")

    with st.form("Author request form"):
        author_request_form(conn, logger)

    st.header("Calling all publishers! :lower_left_ballpoint_pen:")
    st.write("We'll send you daily updates on authors of your choice - just enter your name, email, and the author you want to track, and we'll do the rest!")

    with st.form("Publisher sign-up form"):
        publisher_signup_form(conn, logger)


if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(filename='dashboard_logging.txt',
                        encoding='utf-8', level=logging.INFO)
    connection = connect_to_database()

    streamlit(connection, logger)

    connection.close()
