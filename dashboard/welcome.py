'''A script that creates a Streamlit dashboard using book data from the RDS'''
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd
import requests
import streamlit as st
import altair as alt
import psycopg2


load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def get_connection() -> psycopg2.connect:
    '''Returns a psycopg2 connection to the RDS using env vars'''
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USERNAME,
        password=DB_PASSWORD
    )
    return conn


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


def pipeline(author_url: str, conn: psycopg2.connect) -> bool:
    '''ETL script for single author URL - uploads all author/book info to RDS'''
    pass


def streamlit(conn: psycopg2.connect) -> None:
    st.title(":books: Book and Author Tracker - Publisher Dashboard! :books:")
    st.write("Welcome to the Publisher Dashboard! On this page, you'll be able to request authors to be tracked and submit email report preferences.")
    st.write("On the next page, summary statistics for some of our most popular authors can be seen. Use our interactive features to learn about your favourite author!")
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
        st.metric("Number of publishers using the Book and Author Tracker",
                  publishers, f"{publishers_since_yesterday} publishers since yesterday", border=True)
    st.header("Are you a bookworm? :book: :worm:")
    st.write("Request your favourite book or author to be added to our database! Authors or books added will be included in our summary statistics on the next page.")

    with st.form("Author request form"):
        st.write("Please paste your chosen author's URL from GoodReads.com, in the following format: https://www.goodreads.com/author/show/153394.Suzanne_Collins Please note that this page must be the overall author page; .../author/show/... should be in the URL.")
        author_url_input = st.text_input(
            "Paste an author's URL here:", key="Author URL input")
        submitted_author_request = st.form_submit_button(
            'Add this author to the database')

        if submitted_author_request:
            try:
                author_name = " ".join(
                    author_url_input.split(".")[-1].split("_"))
            except Exception:
                author_name = "Unknown Author"
            # Change author name
            finally:
                st.write(
                    f":hourglass_flowing_sand: Adding {author_name} to the author database...")
                if validate_author_url(author_url_input) == True:
                    if is_author_in_system(author_url_input, conn) == True:
                        st.write("Author is already in the system!")
                    else:
                        st.write(
                            ":hourglass: Loading the author's most up-to-date information...")
                        try:
                            pipeline(author_url_input, conn)
                            st.write(
                                f":white_check_mark: Information loaded - head over to the visualisations page for in-depth analysis of {author_name}'s work!")

                        except Exception as e:
                            st.write(
                                ":x: Something went wrong when getting author's information - please try again, or contact the devs.")

                    # Check if author already in DB
                    # Check if GoodReads.com/URL requests.gets a valid 200 response. Otherwise, print ("Cannot find author with that URL. Double check or try another.")
                    # ETL script taking in Author URL:
                    # INSERTING INTO author VALUES author_url, author_name, author_image, (author_id and author_date_added would auto-generate)
                    # INSERTING INTO book VALUES (all books associated with author)
                    # INSERTING INTO author_measurement (single author_measurement at current time)
                    #  INSERTING INTO book_measurement VALUES (single book_measurement for all books at current time)
                    # import pipeline script's function

    st.header("Calling all publishers! :lower_left_ballpoint_pen:")
    st.write("We'll send you daily updates on authors of your choice - just enter your name, email, and the author you want to track, and we'll do the rest!")
    with st.form("Publisher sign-up form"):
        st.write("Please enter your name, email, and the select one of our tracked authors from the drop-down menu. To subscribe to an email report for multiple authors, please submit the form once for each author URL.")
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
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO publisher (publisher_name, publisher_email) VALUES (%s, %s) RETURNING publisher_id", (publisher_name_input, publisher_email_input))
            new_publisher_id = cursor.fetchone()[0]
            int_new_publisher_id = int(new_publisher_id)

            author_id = pd.read_sql(
                "SELECT author_id FROM author WHERE author_name = %s", conn, params=(publisher_author_choice, ))['author_id'].iloc[0]
            int_author_id = int(author_id)
            cursor.execute(
                "INSERT INTO author_assignment (author_id, publisher_id) VALUES (%s, %s)", (int_author_id, int_new_publisher_id))
            conn.commit()
            st.write(
                f":white_check_mark: Successfully subscribed {publisher_name_input} ({publisher_email_input}) to {publisher_author_choice}! You will receive your first daily report tomorrow morning.")


if __name__ == "__main__":
    conn = get_connection()
    streamlit(conn)
