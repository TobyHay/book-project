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


def get_db_connection() -> psycopg2.extensions.connection:
    '''Gets a connection to the DB specified in the .env'''
    load_dotenv()
    return psycopg2.connect(
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USERNAME'),
        host=os.getenv('DB_HOST'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT')
    )


def get_publishers_tracked_authors(publisher_id: int) -> list[tuple]:
    '''Gets all publishers and their tracked authors from the DB'''
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        sql = '''
            SELECT 
            a.author_id
            FROM publisher as p
            LEFT JOIN author_assignment AS aa ON aa.publisher_id = p.publisher_id
            LEFT JOIN author AS a ON a.author_id = aa.author_id
            where p.publisher_id = %s
            ;
            '''
        cur.execute(sql, (publisher_id,))
        return cur.fetchall()
    finally:
        conn.close()


def get_publisher_ids() -> list[tuple]:
    '''Gets the ids of all publishers'''
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        sql = '''
            SELECT 
            publisher_id
            FROM publisher
            ;
            '''
        cur.execute(sql)
        return cur.fetchall()
    finally:
        conn.close()


def get_publishers_name(publisher_id: int) -> str:
    '''Returns the name for the specified publisher id'''
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        sql = '''
            SELECT 
            publisher_name
            FROM publisher
            WHERE publisher_id = %s
            ;
            '''
        cur.execute(sql, (publisher_id,))
        return cur.fetchone()[0]
    finally:
        conn.close()


def get_publishers_email(publisher_id: int) -> str:
    '''Returns the email for the specified publisher id'''
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        sql = '''
            SELECT 
            publisher_email
            FROM publisher
            WHERE publisher_id = %s
            ;
            '''
        cur.execute(sql, (publisher_id,))
        return cur.fetchone()[0]
    finally:
        conn.close()


def get_avg_rating_difference_since_yesterday(author_id: int) -> int:
    '''gets ratings since yesterday for a given author_id'''
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        sql = '''
            SELECT 
            average_rating - LAG(average_rating) OVER (
                ORDER BY am.date_recorded DESC) avg_change_since_yesterday
            FROM author AS a
            JOIN author_measurement AS am ON a.author_id = am.author_id
            WHERE am.author_id = %s
            ORDER BY am.date_recorded DESC
            LIMIT 2
            ;
            '''
        cur.execute(sql, (author_id,))
        rating_change = cur.fetchall()
        if not rating_change:
            return 'No historical data for this author yet.'
        return rating_change[1][0]
    finally:
        conn.close()


def get_shelved_difference_from_yesterday(author_id: int) -> int:
    '''gets shelved increase since yesterday for a given author_id'''
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        sql = '''
            SELECT 
            shelved_count - LAG(shelved_count) OVER (
                ORDER BY am.date_recorded DESC) shelved_increase_since_yesterday
            FROM author AS a
            JOIN author_measurement AS am ON a.author_id = am.author_id
            WHERE am.author_id = %s
            ORDER BY am.date_recorded DESC
            LIMIT 2
            ;
            '''
        cur.execute(sql, (author_id,))
        shelved_change = cur.fetchall()
        if not shelved_change:
            return 'No historical data for this author yet.'
        return shelved_change[1][0]
    finally:
        conn.close()


def get_todays_date_formatted() -> str:
    '''Returns today's date formatted in y-m-d for use in the email's subject.'''
    return datetime.today().strftime("%Y-%m-%d")


def get_author_info(author_id: int) -> str:
    '''Gets the author's information from their id'''
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        sql = '''
        SELECT author_name, author_image_url
        FROM author
        WHERE author_id = %s
        '''
        cur.execute(sql, (author_id,))
        author_name, image_url = cur.fetchone()
        return author_name, image_url
    finally:
        conn.close()


def generate_author_html_container(author_id: int) -> str:
    '''Generates a html table containing an author'''
    author_name, image_url = get_author_info(author_id)
    daily_shelved = get_shelved_difference_from_yesterday(author_id)
    avg_rating_change = get_avg_rating_difference_since_yesterday(author_id)
    container_html = f'''
        <table width="100%" border="0" cellspacing="0" cellpadding="0"> 
          <tr>
            <td align="left" valign="top" width="150" style="padding: 10px;">
              <img src="{image_url}" width="150" alt="A picture of the author_name" style="display: block; border-radius: 5px;">
            </td>
              <td align="left" valign="top" style="padding: 10px; font-family: Arial, sans-serif;">
              <h3 style="margin: 0 0 10px 0; font-size: 18px; color: #2c3e50;">{author_name}'s engagement:</h3>
              <p style="margin: 0; font-size: 14px; color: #555;"><p style="margin:5px 0 0 0;">
              <strong>Daily Shelved:</strong> {daily_shelved} <br> 
              <strong>Avg Rating Change:</strong> {avg_rating_change}
              </p>
            </td>
          </tr>
        </table>              
        '''
    return container_html


def generate_html_head() -> str:
    '''Generates the html head for the email'''
    html = '''
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Publisher Report Email</title>
    </head>
    '''
    return html


def generate_html_body(publisher_id: int) -> str:
    '''Returns the html body of the email message'''
    publisher_name = get_publishers_name(publisher_id)
    if not publisher_name:
        raise ValueError('No valid publisher for the given id.')

    author_ids = get_publishers_tracked_authors(publisher_id)
    if not author_ids:
        html = f'''<body style="font-family: 'Poppins', Arial, sans-serif; background-color: #f9f9f9; padding: 20px; color: #333333; line-height: 1.5;"> 
        Dear {publisher_name}, 
        <br><br>
        No tracked authors were found. Please add an author on the Bookworm dashboard.'''
        return html + '</body>'

    html_cards = ""
    for id in author_ids:
        id = id[0]
        html_cards = html_cards+generate_author_html_container(id)

    html = f'''
    <body style="font-family: 'Poppins', Arial, sans-serif; background-color: #f9f9f9; padding: 20px; color: #333333; line-height: 1.5;>
      <table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e0e0e0; padding: 20px;">
        <tr>
          <td>
            <p style="font-size: 16px; margin: 0 0 15px 0;">Dear <strong>{publisher_name}</strong>,</p>
            <p style="font-size: 15px; margin: 0 0 20px 0;">The following authors had noteworthy engagement:</p>
      <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #fafafa; border-radius: 6px; overflow: hidden;">
    '''
    html = html + html_cards
    return html + '</body>'


def format_html_email(head: str, body: str) -> str:
    '''Formats the html for an update email'''
    return '<html lang="en">' + head + body + '</html>'


def get_email_subject(publisher_id: int) -> str:
    '''Formats and returns the email subject for a given publisher id'''
    date = get_todays_date_formatted()
    name = get_publishers_name(publisher_id)
    return f'{name}\'s Daily Tracker {date}'


def aws_send_email(email_html: str, publisher_id: int) -> None:
    """Send the specified email HTML using AWS SES."""
    client = boto3.client("ses",
                          region_name="eu-west-2",
                          aws_access_key_id=os.getenv('ACCESS_KEY'),
                          aws_secret_access_key=os.getenv('SECRET_KEY'))
    message = MIMEMultipart()
    message["Subject"] = get_email_subject(publisher_id)
    message["From"] = "trainee.rodrigo.montemayor@sigmalabs.co.uk"
    message["To"] = get_publishers_email(publisher_id)

    body = MIMEText(email_html, 'html')
    message.attach(body)

    client.send_raw_email(
        Source=message["From"],
        Destinations=[message["To"]],
        RawMessage={"Data": message.as_string()}
    )


def send_email_to_publisher(publisher_id: int) -> None:
    '''Sends the update email to the specified author.'''
    html_body = generate_html_body(publisher_id)
    html_head = generate_html_head()
    html_email = format_html_email(html_head, html_body)
    aws_send_email(html_email, publisher_id)


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


def lambda_handler(event: None, context: None) -> None:
    "Lambda handler function allows AWS lambda to utilise the script."
    send_email_to_all_publishers()


def save_test_html(publisher_id: int) -> None:
    '''Saves the HTML to a file for convenient local testing.'''
    html_body = generate_html_body(publisher_id)
    html_head = generate_html_head()
    html_email = format_html_email(html_head, html_body)
    with open('test.html', 'w') as f:
        f.write(html_email)


if __name__ == "__main__":
    save_test_html(1)
    send_email_to_all_publishers()
