'''This library assumes that the measurement for today (9am ish) has already finished.'''

"""
TODO:
- Implement aggregate data calcs for the email summary
- Implement html generator
- Implement author link
"""

import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime 
import boto3
import pandas as pd
import psycopg2

def get_db_connection() ->psycopg2.extensions.connection:
    load_dotenv()
    return psycopg2.connect(
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USERNAME'),
        host=os.getenv('DB_HOST'),
        password=os.getenv('DB_PASSWORD'), 
        port=os.getenv('DB_PORT')
    )


def get_publishers_tracked_authors(n_of_days_of_data:int=2) -> dict:
    '''Gets all publishers  and their tracked authors from the DB'''
    try:
        conn = get_db_connection()
        
        # sql = f'''
        #     SELECT publisher_name, publisher_email,
        #     a.author_id, author_name, author_url, author_image_url,
        #     shelved_count, average_rating
        #     FROM publisher as p
        #     LEFT JOIN author_assignment AS aa ON aa.publisher_id = p.publisher_id
        #     LEFT JOIN author AS a ON a.author_id = aa.author_id
        #     LEFT JOIN author_measurement AS am ON a.author_id = am.author_id
        #     WHERE am.date_recorded > (now() - '{n_of_days_of_data} days'::interval)
        #     ;
            # '''
        #              # WHERE clause makes it scaleable vs getting all data BUT only allows for values vs ytday


        sql = f'''
            SELECT publisher_name, publisher_email,
            a.author_id
            FROM publisher as p
            LEFT JOIN author_assignment AS aa ON aa.publisher_id = p.publisher_id
            LEFT JOIN author AS a ON a.author_id = aa.author_id
            ;
            '''
        return pd.read_sql(sql,conn)
    finally:
        conn.close()



def get_avg_rating_change_since_yesterday(author_id,tracked_authors:pd.DataFrame) -> int:
    '''gets ratings since yesterday for a given author_id'''
    return 


def get_todays_date_formatted() -> str:
    '''Returns today's date formatted in y-m-d for use in the email's subject.'''
    return datetime.today().strftime("%Y-%m-%d")


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
    Dear {publisher_name}, 


    </body>
    '''
    return html

def format_html_email(head:str,body:str) -> str:
    ''''''# TODO
    return '<html lang="en">' + head + body + '</html>'

 
def send_email(email_html: str):
    """Send an email using AWS SES. requires AWS CLI?"""
    client = boto3.client("ses", region_name="eu-west-2")
    message = MIMEMultipart()
    message["Subject"] = NotImplementedError
    message["From"] = "trainee.rodrigo.montemayor@sigmalabs.co.uk"
    message["To"] = "trainee.rodrigo.montemayor@sigmalabs.co.uk"

    body = MIMEText(email_html,param_html='?')
    message.attach(body)

    client.send_raw_email(
        Source=message["From"],
        Destinations=[message["To"]],
        RawMessage={"Data": message.as_string()} # Should this be RawMessage? shouldnt it be html?
    )


def lambda_handler():
    "Example function in this script"
    print("This script has been uploaded correctly.")


if __name__ == "__main__":
    print()
    df = get_publishers_tracked_authors()
    # df = (author_aggregates(df))

    print(df)
