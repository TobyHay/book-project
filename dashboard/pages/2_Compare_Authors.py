# pylint: disable=import-error, no-member, too-many-locals
'''A script that creates a Streamlit dashboard using book data scraped online'''
from os import environ as ENV
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
import psycopg2
import plotly.express as px

st.set_page_config(layout="wide")


load_dotenv()


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


def get_authors(connection: psycopg2.connect) -> pd.DataFrame:
    '''Queries the database, returns and merges tables'''
    query = """SELECT * FROM author"""
    return pd.read_sql(query, connection)


def select_author(authors: pd.DataFrame, key: int) -> str:
    author_names = authors['author_name']

    selected_author = st.selectbox(
        f"Select author {key} to see shelved count",
        author_names,
        key=key)
    return selected_author


def get_author_data(author_name: str, connection: psycopg2.connect) -> pd.DataFrame:
    '''Queries the database, returns and merges tables'''
    query = """
    SELECT
        a.*,
        am.author_measurement_id,
        am.rating_count,
        am.average_rating,
        am.date_recorded,
        am.shelved_count,
        am.review_count,
        am.author_id AS am_author_id
    FROM author AS a
    LEFT JOIN author_measurement AS am
    ON a.author_id = am.author_id
    WHERE a.author_name = %s;
    """
    return pd.read_sql(query, connection, params=(author_name,))


def get_author_books(author_name: int, connection: psycopg2.connect) -> pd.DataFrame:
    '''Queries the database, returns and merges tables'''

    book_query = """
    SELECT
        b.*,
        bm.book_measurement_id,
        bm.rating_count,
        bm.average_rating,
        bm.date_recorded,
        bm.review_count,
        bm.book_id AS bm_book_id
    FROM book AS b
    JOIN book_measurement AS bm
    ON b.book_id = bm.book_id
    WHERE b.author_id = (SELECT author_id FROM author WHERE author_name = %s LIMIT 1);
    """

    return pd.read_sql(book_query, connection, params=(author_name,))


def get_change_in_shelved_count(author_name: str, conn: psycopg2.connect) -> pd.DataFrame:
    '''
    Fetches shelved count data and computes daily change for a specific author.
    Returns a dataframe with date, daily change, and author name.
    '''
    shelved_count_query = """
        SELECT
            am.date_recorded,
            am.shelved_count
        FROM author_measurement AS am
        JOIN author AS a ON a.author_id = am.author_id
        WHERE a.author_name = %s
        ORDER BY am.date_recorded ASC
    """
    try:
        df = pd.read_sql(shelved_count_query, conn, params=(author_name,))
        if df.empty:
            return df

        df['daily_change'] = df['shelved_count'].diff().fillna(
            0) 
        df['author_name'] = author_name 

        return df[['date_recorded', 'daily_change', 'author_name']]
    except Exception as e:
        st.error(
            f":x: Error fetching shelved count history for {author_name}: {e}")
        return pd.DataFrame()


def plot_line_shelved_count_over_time(author1: str, author2: str) -> None:
    '''Plots a line graph of daily shelved count changes for two authors.'''

    if author1 == author2:
        st.warning("Please select two unique authors.")
        fig = px.line(title="Please select two unique authors")
        st.plotly_chart(fig)
        return

    author1_change_data = get_change_in_shelved_count(author1, conn)
    author2_change_data = get_change_in_shelved_count(author2, conn)

    df = pd.concat([author1_change_data, author2_change_data],
                   ignore_index=True)

    if df.empty:
        fig = px.line(title="Shelved Count (No Data Available)")
        st.plotly_chart(fig)
        return

    st.markdown('<div style="height: 70px;"></div>', unsafe_allow_html=True)

    fig = px.line(
        df,
        x='date_recorded',
        y='daily_change',
        color='author_name',
        title=f"Daily Shelved Count Change: {author1} VS {author2}",
        labels={
            'date_recorded': 'Date',
            'daily_change': 'Daily Shelved Count Added',
            'author_name': 'Author'
        }
    )

    st.plotly_chart(fig)


def get_author_book_data(connection: psycopg2.connect) -> pd.DataFrame:
    '''Queries the database for all authors and the count of their books'''
    book_query = """SELECT
                    a.author_id,
                    a.author_name,
                    COUNT(b.book_id) AS books
            FROM author AS a
            LEFT JOIN book AS b ON a.author_id = b.author_id
            GROUP BY a.author_id"""

    return pd.read_sql(book_query, connection)


def plot_bar_books_per_author(df: pd.DataFrame) -> None:
    '''Plots bar chart which counts each author's published books'''

    fig = px.bar(df,
                 x='author_name',
                 y='books',
                 title='Books Published Per Author',
                 labels={'author_name': 'Author', 'books': 'Number of Books'},
                 color='books')

    st.plotly_chart(fig)


if __name__ == "__main__":
    try:
        col1, col2 = st.columns([10, 2])

        with col1:
            st.title(":scales: Compare Authors")
        with col2:
            st.image("../assets/bookworm_logo.jpeg", width=500)

        conn = connect_to_database()

        all_authors = get_author_book_data(conn)
        plot_bar_books_per_author(all_authors)

        authors = get_authors(conn)

        left1, right1 = st.columns(2)
        with left1:
            author1 = select_author(authors, 1)
        with right1:
            author2 = select_author(authors, 2)

        plot_line_shelved_count_over_time(author1, author2)

    except Exception as e:
        st.write(f"Error with plotting figure: {e}")
    finally:
        conn.close()
