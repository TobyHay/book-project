"""
Test python script to be converted into a Docker image and 
be pushed to the relevant ECR repository created by the 
terraform/main.tf using step 1

This should be replaced with the python script you want to
upload to one of the lambda functions
"""

import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import boto3
import pandas as pd
import psycopg2

def get_db_connection() ->psycopg2.connection:
    load_dotenv()
    return psycopg2.connect(
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USERNAME'),
        host=os.getenv('DB_HOST'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT')
    )


def get_publishers_tracked_data() -> pd.DataFrame:
    '''Gets data from all publisher's tracked authors from the DB'''
    try:
        conn = get_db_connection()
        sql = '''
            SELECT publisher_email, publisher_name,
            author_name,author_url,
            book_title,book_url_path
            FROM publisher as p
            JOIN author_assignment AS aa ON aa.publisher_id = p.publisher_id
            lEFT JOIN author AS a ON a.author_id = aa.author_id
            LEFT JOIN book AS b ON a.author_id = b.author_ud
            '''
        return pd.read_sql(sql,conn)
    finally:
        conn.close()


def generate_html_head(publisher_name:str):
    '''Generates a html head for a personalised email based on publisher name.'''
    # TODO
    html = f'''
    <head>
        <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{publisher_name}'s Daily Author Tracking</title>
    </head>
    '''
    return html

def generate_html_body():
    ''''''
    # TODO
    html = '''
    <body>
    </body>
    '''
    return html

def format_html_email(head:str,body:str) -> str:
    ''''''# TODO
    return '<html lang="en">' + head + body + '</html>'


def send_email(contents: dict):
    """Send an email using AWS SES."""
    client = boto3.client("ses", region_name="eu-west-2")
    message = MIMEMultipart()
    message["Subject"] = contents["subject"]
    message["From"] = "trainee.hadia.fadlelmawla@sigmalabs.co.uk"
    message["To"] = "trainee.hadia.fadlelmawla@sigmalabs.co.uk"

    body = MIMEText(contents["body"], "plain")
    message.attach(body)

    client.send_raw_email(
        Source=message["From"],
        Destinations=[message["To"]],
        RawMessage={"Data": message.as_string()}
    )


def lambda_handler():
    "Example function in this script"
    print("This script has been uploaded correctly.")


if __name__ == "__main__":
    print('a')
