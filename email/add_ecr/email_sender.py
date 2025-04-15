'''This script sends a report email to the users of the Bookworm dashboard.''' 

import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime 
import boto3
from botocore.exceptions import ClientError
import pandas as pd
import psycopg2

def get_db_connection() ->psycopg2.extensions.connection:
    '''Gets a connection to the DB specified in the .env''' 
    load_dotenv()
    return psycopg2.connect(
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USERNAME'),
        host=os.getenv('DB_HOST'),
        password=os.getenv('DB_PASSWORD'), 
        port=os.getenv('DB_PORT')
    )



def get_publishers_tracked_authors(publisher_id:int) -> list[tuple]:
    '''Gets all publishers  and their tracked authors from the DB'''
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        sql = f'''
            SELECT 
            a.author_id
            FROM publisher as p
            LEFT JOIN author_assignment AS aa ON aa.publisher_id = p.publisher_id
            LEFT JOIN author AS a ON a.author_id = aa.author_id
            where p.publisher_id = {publisher_id}
            ;
            '''
        cur.execute(sql)
        return cur.fetchall()
    finally:
        conn.close()


def get_publisher_ids() -> list[tuple]:
    '''Gets the ids of all publishers'''
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        sql = f'''
            SELECT 
            publisher_id
            FROM publisher
            ;
            '''
        cur.execute(sql)
        return cur.fetchall()
    finally:
            conn.close()


def get_publishers_name(publisher_id:int) -> str:
    '''Returns the name for the specified publisher id'''
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        sql = f'''
            SELECT 
            publisher_name
            FROM publisher
            WHERE publisher_id = {publisher_id}
            ;
            '''
        cur.execute(sql)
        return cur.fetchone()[0]
    finally:
        conn.close()


def get_publishers_email(publisher_id:int) -> str:
    '''Returns the email for the specified publisher id'''
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        sql = f'''
            SELECT 
            publisher_email
            FROM publisher
            WHERE publisher_id = {publisher_id}
            ;
            '''
        cur.execute(sql)
        return cur.fetchone()[0]
    finally:
        conn.close()


def get_avg_rating_difference_since_yesterday(author_id) -> int:
    '''gets ratings since yesterday for a given author_id'''
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        sql = f'''
            SELECT 
            average_rating - LAG(average_rating) OVER (
                ORDER BY am.date_recorded DESC) avg_change_since_yesterday
            FROM author AS a
            JOIN author_measurement AS am ON a.author_id = am.author_id
            WHERE am.author_id = {author_id}
            ORDER BY am.date_recorded DESC
            LIMIT 2
            ;
            '''
        cur.execute(sql)
        rating_change = cur.fetchall()
        if not rating_change:
            return 'No historical data for this author yet.'
        return rating_change[1][0]
    finally:
        conn.close()

def get_shelved_difference_from_yesterday(author_id) -> int:
    '''gets shelved increase since yesterday for a given author_id'''
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        sql = f'''
            SELECT 
            shelved_count - LAG(shelved_count) OVER (
                ORDER BY am.date_recorded DESC) shelved_increase_since_yesterday
            FROM author AS a
            JOIN author_measurement AS am ON a.author_id = am.author_id
            WHERE am.author_id = {author_id}
            ORDER BY am.date_recorded DESC
            LIMIT 2
            ;
            '''
        cur.execute(sql)
        shelved_change = cur.fetchall()
        if not shelved_change:
            return 'No historical data for this author yet.'
        return shelved_change[1][0]
    finally:
        conn.close()

def get_todays_date_formatted() -> str:
    '''Returns today's date formatted in y-m-d for use in the email's subject.'''
    return datetime.today().strftime("%Y-%m-%d")


def get_author_info(author_id:int) -> str:
    '''Gets the author's information from their id'''
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        sql = f'''
        SELECT author_name, author_image_url
        FROM author
        WHERE author_id = {author_id}
        '''
        cur.execute(sql)
        author_name, image_url = cur.fetchone()
        return author_name, image_url
    finally:
        conn.close()

def generate_author_html_container(author_id:int) -> str:
    ''''''
    author_name,image_url = get_author_info(author_id)
    daily_shelved = get_shelved_difference_from_yesterday(author_id)
    avg_rating_change = get_avg_rating_difference_since_yesterday(author_id)
    container_html = f'''
        <table width="100%" border="0" cellspacing="0" cellpadding="0"> 
          <tr>
            <td align="left" valign="top" width="150" style="padding: 10px;">
              <img src="{image_url}" width="150" alt="A picture of the author_name" style="display: block;">
            </td>
            <td align="left" valign="top" style="padding: 10px; font-family: Arial;">
              <h3 style="margin: 0;">{author_name}'s engagement:</h3>
              <p style="margin:5px 0 0 0;">
              Daily Shelved: {daily_shelved} 
              <br> 
              Avg Rating Change: {avg_rating_change}
              </p>
            </td>
          </tr>
        </table>              
        '''
    return container_html

def generate_html_body(publisher_id:int) -> str:
    '''Returns the html body of the email message'''
    publisher_name = get_publishers_name(publisher_id)
    if not publisher_name:
        raise ValueError('No valid publisher for the given id.') 

    author_ids = get_publishers_tracked_authors(publisher_id)
    if not author_ids:
        html = f'<body> Dear {publisher_name}, <br><br>No tracked authors were found. Please add an author on the Bookworm dashboard.'
        return html + '</body>' 

    html_cards = ""
    for id in author_ids:
        id = id[0]
        html_cards = html_cards+generate_author_html_container(id)

    html = f'''
    <body>
    Dear {publisher_name}, <br><br>The following authors had noteworthy engagement:
    '''
    html = html + html_cards
    return html + '</body>'


def format_html_email(body:str) -> str:
    '''Formats the html for an update email''' 
    return '<html lang="en">' + body + '</html>'


def get_email_subject(publisher_id:int) -> str:
    '''Formats and returns the email subject for a given publisher id'''
    date = get_todays_date_formatted()
    name = get_publishers_name(publisher_id)
    return f'{name}\'s Daily Tracker {date}'
    
 
def aws_send_email(email_html: str,publisher_id:int):
    """Send the specified email HTML using AWS SES."""
    client = boto3.client("ses",
                           region_name="eu-west-2",
                           aws_access_key_id=os.getenv('ACCESS_KEY'),
                           aws_secret_access_key=os.getenv('SECRET_KEY'))
    message = MIMEMultipart()
    message["Subject"] = get_email_subject(publisher_id)
    message["From"] = "trainee.rodrigo.montemayor@sigmalabs.co.uk"
    message["To"] = get_publishers_email(publisher_id)

    body = MIMEText(email_html,'html')
    message.attach(body)

    client.send_raw_email(
        Source=message["From"],
        Destinations=[message["To"]],
        RawMessage={"Data": message.as_string()}
    )


def send_email_to_publisher(publisher_id:int) -> None:
    '''Sends the update email to the specified author.'''
    html_body = generate_html_body(publisher_id)
    html_email = format_html_email(html_body)
    send_email_to_publisher(html_email,publisher_id)


def send_email_to_all_publishers() -> None:
    '''Sends an email containing information about their tracked authors
    to all publishers of the bookworm dashboard in our database.''' 
    publisher_ids = get_publisher_ids()
    for id in publisher_ids:

        try:
            send_email_to_publisher(id[0])
        except ClientError as e:
            if e.response['Error']['Code'] == 'MessageRejected':
                print("Message was rejected:", e.response['Error']['Message'])
            else:
                raise e


def lambda_handler(event,context):
    "Lambda handler function allows AWS lambda to utilise the script." 
    send_email_to_all_publishers()
    

if __name__ == "__main__":
    send_email_to_all_publishers()