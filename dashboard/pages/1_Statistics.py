# pylint: disable=import-error, no-member, too-many-locals
'''A script that creates a Streamlit dashboard using book data scraped online'''
from os import environ as ENV
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
import psycopg2
import plotly.express as px

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


def select_author(authors: pd.DataFrame) -> str:
    author_names = authors['author_name']

    selected_author = st.selectbox(
        "Select an author to see long-term shelved count and rating analytics", author_names)
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


def select_book(author_name: str, books: pd.DataFrame) -> str:
    book_titles = books['book_title']

    selected_book = st.selectbox(
        f"Select a book from {author_name} for ratings over time", book_titles)
    return selected_book


def plot_line_shelved_count_over_time(df: pd.DataFrame) -> None:
    '''Plots line graph for Author's shelved count over time'''

    fig = px.line(df,
                  x='date_recorded',
                  y='shelved_count',
                  title="Shelved Count Over Time",
                  labels={'date_recorded': 'Date',
                          'shelved_count': 'Shelved Count'},)

    fig.update_traces(name='Shelved Count',
                      selector=dict(name='shelved_count'))

    st.plotly_chart(fig)


def convert_to_range(rating: int) -> str:
    if 0 <= rating <= 1:
        return '0-1'
    if 1 < rating <= 2:
        return '1-2'
    if 2 < rating <= 3:
        return '2-3'
    if 3 < rating <= 4:
        return '3-4'
    if 4 < rating <= 5:
        return '4-5'
    raise ValueError("Invalid rating, does not fit between 0 and 5")


@st.cache_data(ttl=60)
def plot_pie_book_ratings(df: pd.DataFrame) -> None:
    '''Plots pie chart for the proportions of an Author's book ratings'''

    df_sorted = df.sort_values(
        by=['book_id', 'date_recorded'], ascending=[True, False])

    df_latest_ratings = df_sorted.groupby('book_id').first().reset_index()

    df_latest_ratings['rating'] = df_latest_ratings['average_rating'].apply(
        convert_to_range)

    df_rating_counts = df_latest_ratings['rating'].value_counts(
    ).reset_index()

    df_rating_counts.columns = ['rating', 'count']
    rating_order = ['4-5', '3-4', '2-3', '1-2', '0-1']

    fig = px.pie(df_rating_counts,
                 names='rating',
                 values='count',
                 color='count',
                 title='Proportion of Book Ratings',
                 color_discrete_sequence=px.colors.sequential.Blues_r,
                 category_orders={'rating': rating_order})

    st.plotly_chart(fig)


def plot_line_ratings_over_time(book: str, df: pd.DataFrame) -> None:
    '''Plots line graph for Author's Daily over time'''

    df_book = df.loc[df['book_title'] == book]

    fig = px.line(df_book,
                  x='date_recorded',
                  y='rating_count',
                  title="Ratings Over Time",
                  labels={'date_recorded': 'Date'})

    fig.update_traces(name='Daily Rating', selector=dict(name='daily_rating'))
    fig.update_traces(name='Average Rating',
                      selector=dict(name='average_rating'))

    fig.update_layout(
        legend=dict(
            orientation='h',
            y=1.15,
            title=None))

    st.plotly_chart(fig)


def plot_line_avg_ratings_over_time(book: str, df: pd.DataFrame) -> None:
    '''Plots line graph for Author's Average Ratings over time'''

    df_book = df.loc[df['book_title'] == book]

    fig = px.line(df_book,
                  x='date_recorded',
                  y='average_rating',
                  title="Ratings Over Time",
                  labels={'date_recorded': 'Date'})

    fig.update_traces(name='Daily Rating', selector=dict(name='daily_rating'))
    fig.update_traces(name='Average Rating',
                      selector=dict(name='average_rating'))

    fig.update_layout(
        legend=dict(
            orientation='h',
            y=1.15,
            title=None))

    st.plotly_chart(fig)


def plot_bar_books_per_author(df: pd.DataFrame) -> None:
    '''Plots bar chart which counts each author's published books'''

    fig = px.bar(df,
                 x='author',
                 y='books',
                 title='Books Published Per Author',
                 labels={'author': 'Author', 'books': 'Number of Books'},
                 color='books')

    st.plotly_chart(fig)


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    conn = connect_to_database()

    authors = get_authors(conn)
    selected_author = select_author(authors)

    author_data = get_author_data(selected_author, conn)
    author_books = get_author_books(selected_author, conn)

    left1, right1 = st.columns(2)
    with left1:
        plot_line_shelved_count_over_time(author_data)
    with right1:
        plot_pie_book_ratings(author_books)
    book = select_book(selected_author, author_books)
    left2, right2 = st.columns(2)

    with left2:
        plot_line_ratings_over_time(book, author_books)

    with right2:

        plot_line_avg_ratings_over_time(book, author_books)

    st.write("Top authors of the week:")

    plot_bar_books_per_author()
