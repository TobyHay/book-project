'''A script that creates a Streamlit dashboard "add author" page'''
import urllib.request
from os import environ as ENV
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
        conn = psycopg2.connect(database=ENV.get("DB_NAME"),
                                user=ENV.get("DB_USERNAME"),
                                password=ENV.get("DB_PASSWORD"),
                                host=ENV.get("DB_HOST"),
                                port=ENV.get("DB_PORT"))
        return conn
    except Exception as e:
        raise Exception(f"Error connecting to database: {e}")
    
def validate_email(email: str) -> bool:
    '''Basic validation checks on user-submitted email address'''
    if "@" not in email:
        return False
    if "." not in email:
        return False
    return True

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


def infer_author_name(url: str) -> str:
    '''Attempts to extract author name from URL for display purposes'''
    try:
        author_name = " ".join(url.split(".")[-1].split("_"))
        if not author_name.strip():
            raise ValueError("Unknown Author")
        return author_name
    except Exception:
        return "Unknown Author"

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

def author_request_form(conn: psycopg2.connect) -> None:
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
            st.write(
                ":hourglass: Loading the author's most up-to-date information...")
            try:
                result = mini_etl(author_url_input, conn)
                if result == "duplicate":
                    st.write(
                        ":pushpin: This author is already in our database! Please enter another one.")
                elif result == "success":
                    st.write(
                        f":white_check_mark: Information loaded - head over to the visualisations page tomorrow for in-depth analysis of {author_name}'s work!")
                else:
                    st.write(
                        ":x: Something went wrong when getting author's information - please try again, or contact the devs.")
            except Exception as e:
                st.write(e)
                st.write(
                    ":x: Something went wrong when getting author's information - please try again, or contact the devs.")


def streamlit(conn):
    
    col1, col2 = st.columns([10, 2])

    with col1:
        st.title(":bust_in_silhouette: Add Authors")
    with col2:
        st.image("../assets/bookworm_logo.jpeg", width=250)

    st.header("Are you a bookworm? :book:")
    st.write("Request your favourite book or author to be added to our database! Authors or books added will be included in our summary statistics on the next page, and can be requested for tailored reports below once added.")

    with st.form("Author request form"):
        author_request_form(conn)


if __name__ == "__main__":
    connection = connect_to_database()
    streamlit(connection)