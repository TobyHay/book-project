'''A script that creates a Streamlit dashboard using book data from the RDS'''
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
import altair as alt
import psycopg2

# Streamlit code heree
authors = ["Suzanne Collins", "Toby", "Tul", "Rodrigo", "John"]

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def get_connection():
    conn = psycopg2.connect(
        host="your-db-hostname",
        port="5432",
        database="your-db-name",
        user="your-username",
        password="your-password"
    )
    return conn


def streamlit():
    st.title(":books: Book and Author Tracker - Publisher Dashboard! :books:")
    st.write("Welcome to the Publisher Dashboard! On this page, you'll be able to request authors to be tracked, and submit email report preferences.")
    st.write("On the next page, summary statistics for some of our most popular authors can be seen. Use our interactive features to learn about your favourite author!")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Number of books registered in our database",
                  152, "25 books since yesterday", border=True)
    with col2:
        st.metric("Number of authors signed up for tracking",
                  31, "12 authors since yesterday", border=True)
    with col3:
        st.metric("Number of Publishers using the Book and Author Tracker",
                  11, "3 Publishers since yesterday", border=True)
    st.header("Are you a book worm? :book: :worm:")
    st.write("Request your favourite book or author to be added to our database! Authors or books added will be included in our summary statistics on the next page.")

    with st.form("Author request form"):
        st.write("Please paste an author URL from GoodReads.com, in the following format: https://www.goodreads.com/author/list/153394.Suzanne_Collins")
        chosen_author_url = st.text_input("Author URL:")
        my_color = st.selectbox(
            'Pick a color', ['red', 'orange', 'green', 'blue', 'violet'])
        st.form_submit_button('Submit my picks')

    st.header("Calling all publishers! :lower_left_ballpoint_pen:")
    st.write("We'll send you daily updates on authors of your choice - just enter your email and the author you want to track, and we'll do the rest!")


if __name__ == "__main__":
    streamlit()
