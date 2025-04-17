'''A script that creates a Streamlit dashboard using book data from the RDS'''
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
        connection = psycopg2.connect(database=ENV.get("DB_NAME"),
                                      user=ENV.get("DB_USERNAME"),
                                      password=ENV.get("DB_PASSWORD"),
                                      host=ENV.get("DB_HOST"),
                                      port=ENV.get("DB_PORT"))
        return connection
    except Exception as e:
        raise Exception(f"Error connecting to database: {e}")

def validate_email(email: str) -> bool:
    '''Basic validation checks on user-submitted email address'''
    if "@" not in email:
        return False
    if "." not in email:
        return False
    return True


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


def is_author_already_assigned_to_specific_publisher(publisher_id, author_choice_id, conn):
    '''Checks whether the publisher is already assigned to the requested author'''
    query = "SELECT author_assignment_id FROM author_assignment WHERE publisher_id = %s AND author_id = %s"
    with conn.cursor() as cursor:
        cursor.execute(query, (publisher_id, author_choice_id))
        return cursor.fetchone() is not None


def insert_new_publisher(publisher_email_input, publisher_name_input, conn):
    '''Inserts a new publisher into the publisher table'''
    query = "INSERT INTO publisher (publisher_name, publisher_email) VALUES (%s, %s) RETURNING publisher_id"
    with conn.cursor() as cursor:
        cursor.execute(query, (publisher_name_input, publisher_email_input))
        new_publisher_id = cursor.fetchone()[0]
        int_new_publisher_id = int(new_publisher_id)
        conn.commit()
        return int_new_publisher_id
    


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




def publisher_signup_form(conn: psycopg2.connect) -> None:
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
        "Select author:", list_of_authors)

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
                        f":pushpin: The address {publisher_email_input} is already subscribed to {publisher_author_choice}!")
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


def remove_email_query(remove_email_name, conn):
        query = "DELETE FROM publisher WHERE publisher_email = %s"
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (remove_email_name, ))
                conn.commit()
                return "success"
        except Exception as e:
            return f"failure - {e}"

def email_is_publisher(publisher_email_removal_input, conn):
    query = "SELECT publisher_id FROM publisher WHERE publisher_email = %s"
    with conn.cursor() as cursor:
        cursor.execute(query, (publisher_email_removal_input,))
        result = cursor.fetchone()
        if result:
            return True
        return False

def remove_author_assignment_query(publisher_email_removal_input, conn):
    query = "SELECT publisher_id FROM publisher WHERE publisher_email = %s"
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (publisher_email_removal_input,))
            result = cursor.fetchone()
            if not result:
                return "failure - no such publisher"
            publisher_id = result[0]

        query2 = "DELETE FROM author_assignment WHERE publisher_id = %s"
        with conn.cursor() as cursor:
            cursor.execute(query2, (publisher_id,))
            conn.commit()
            return "success"
    except Exception as e:
        return f"failure - {e}"


    

def publisher_removal_form(conn: psycopg2.connect) -> None:
    st.write("""Please the email that you would like to remove from the mailing list.""")

    publisher_email_removal_input = st.text_input(
    "Email to remove from mailing list:", key="Publisher email removal input")

    publisher_email_removal_input = publisher_email_removal_input[:50]
    submitted_publisher_removal= st.form_submit_button(
        "Remove email from mailing list")

    if submitted_publisher_removal:
        if validate_email(publisher_email_removal_input):
            if email_is_publisher(publisher_email_removal_input, conn):
                result_author_assignment = remove_author_assignment_query(publisher_email_removal_input, conn)
                result_publisher = remove_email_query(publisher_email_removal_input, conn)
                if result_publisher == "success" and result_author_assignment == "success":
                    st.write(
                        f":white_check_mark: Successfully unsubscribed {publisher_email_removal_input} from all correspondence - we're sorry to see you go! If something wasn't quite right with the quality of our service, or you have any feedback for us, please email trainee.john.adibpour@sigmalabs.co.uk.")
                else:
                    st.write(
                        ":x: Something went wrong when unsubscribing this email address - please try again, or contact the devs.")
                    st.write(f"Error: {result_publisher}")
            else:
                st.write(":x: No publisher by this address in our database - please double-check it and try again.")

        else:
            st.write(
                ":x: Invalid email address - please double-check it and try again.")






def streamlit(conn):
    col1, col2 = st.columns([10, 2])

    with col1:
        st.title(":envelope_with_arrow: Sign Up For Emails")
    with col2:
        st.image("../assets/bookworm_logo_with_words.jpeg", width=500)

    

    st.header("Calling all publishers! :lower_left_ballpoint_pen:")
    st.write("We'll send you daily updates on authors of your choice - just enter your name, email, and the author you want to track, and we'll do the rest!")

    with st.form("Publisher sign-up form"):
        publisher_signup_form(conn)
    
    st.write("Email removal form:")

    with st.form("Remove publisher from sign-up list"):
        publisher_removal_form(conn)



if __name__ == "__main__":
    connection = connect_to_database()
    streamlit(connection)


