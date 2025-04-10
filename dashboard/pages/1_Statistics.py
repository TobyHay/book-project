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
    author_query = """
    SELECT a.*, am.* 
    FROM author AS a
    LEFT JOIN author_measurement AS am
    ON a.author_id = am.author_id
    WHERE a.author_name = %s;
    """
    return pd.read_sql(author_query, connection, params=(author_name,))


def get_author_books(id: int, connection: psycopg2.connect) -> pd.DataFrame:
    '''Queries the database, returns and merges tables'''

    book_query = """
    SELECT b.*, bm.*
    FROM book AS b
    JOIN book_measurement AS bm
    ON b.book_id = bm.book_id
    WHERE b.author_id = %s;
    """

    return pd.read_sql(book_query, connection, params=(id,))


def select_book(books) -> str:
    book_titles = books['book_title']

    book_titles = ["Harry Potter 1", "Harry Potter 2"]
    selected_book = st.selectbox(
        "Select a book for ratings over time", book_titles)
    return selected_book


def plot_line_shelved_count_over_time(df: pd.DataFrame) -> None:
    '''Plots line graph for Author's shelved count over time'''

    # Mock Data
    df = pd.DataFrame({
        'date_recorded': pd.date_range(start='2023-01-01', periods=10, freq='D'),
        'shelved_count': [3, 4, 2, 5, 4, 3, 4, 3, 5, 4], })

    fig = px.line(df,
                  x='date_recorded',
                  y='shelved_count',
                  title="Shelved Count Over Time",
                  labels={'date_recorded': 'Date',
                          'shelved_count': 'Shelved Count'},)

    fig.update_traces(name='Shelved Count',
                      selector=dict(name='shelved_count'))

    st.plotly_chart(fig)


@st.cache_data(ttl=60)
def plot_pie_book_ratings(df: pd.DataFrame) -> None:
    '''Plots pie chart for the proportions of an Author's book ratings'''

    # df['date_recorded'] = pd.to_datetime(df['date_recorded'])
    df_sorted = df.sort_values(
        by=['book_id', 'date_recorded'], ascending=[True, False])

    df_new_values = df_sorted.groupby(
        'book_id').first().reset_index()

    # Mock Data
    data = {
        'ratings': ['1-2', '0-1', '2-3', '3-4', '4-5'],
        'count': [45, 120, 75, 60, 100]}
    df = pd.DataFrame(data)
    df = df.sort_values(by='ratings')

    rating_order = ['0-1', '1-2', '2-3', '3-4', '4-5']

    fig = px.pie(df,
                 names='ratings',
                 values='count',
                 color='count',
                 title='Proportion of Boook Ratings',
                 color_discrete_sequence=px.colors.sequential.Blues_r,
                 category_orders={'ratings': rating_order})

    st.plotly_chart(fig)


def plot_line_ratings_over_time(book: str) -> None:
    '''Plots line graph for Author's Daily & Average Ratings over time'''

    # Mock Data
    df = pd.DataFrame({
        'date': pd.date_range(start='2023-01-01', periods=10, freq='D'),
        'daily_rating': [3, 4, 2, 5, 4, 3, 4, 3, 5, 4],
        'average_rating': [3.5, 3.8, 3.4, 3.7, 3.6, 3.5, 3.7, 3.6, 3.9, 3.8]})

    fig = px.line(df,
                  x='date',
                  y=['daily_rating', 'average_rating'],
                  title="Ratings Over Time",
                  labels={'date': 'Date'})

    fig.update_traces(name='Daily Rating', selector=dict(name='daily_rating'))
    fig.update_traces(name='Average Rating',
                      selector=dict(name='average_rating'))

    fig.update_layout(
        legend=dict(
            orientation='h',
            y=1.15,
            title=None))

    st.plotly_chart(fig)


def plot_bar_books_per_author() -> None:
    '''Plots bar chart which counts each author's published books'''

    # Mock Data
    data = {
        'author': ['J.K. Rowling', 'George R.R. Martin', 'J.R.R. Tolkien', 'Agatha Christie', 'Stephen King',
                   'Isaac Asimov', 'Margaret Atwood', 'Haruki Murakami', 'Dan Brown', 'J.D. Salinger'],
        'books': [7, 5, 4, 12, 21, 20, 12, 15, 25, 1]}

    df = pd.DataFrame(data)
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
    author_id = int(author_data['author_id'].iloc[:, 0])
    author_books = get_author_books(author_id, conn)

    left1, right1 = st.columns(2)
    with left1:
        plot_line_shelved_count_over_time(author_data)
    with right1:
        plot_pie_book_ratings(author_books)

    left2, right2 = st.columns(2)
    with left2:
        book = select_book(author_books)
        plot_line_ratings_over_time(book)
    with right2:
        # Summary Stats
        st.write("Top authors of the week:")

        plot_bar_books_per_author()
        # TODO Too many authors, may clutter graph (what about top 10?)

    st.write(authors)

    st.write(author_books)
