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


TEST_IMAGE_URL ='https://images.gr-assets.com/authors/1630199330p5/153394.jpg'

def get_db_connection() ->psycopg2.extensions.connection:
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
        print(publisher_id,cur.fetchall())
        return cur.fetchall()
    finally:
        conn.close()


def get_publishers_name(publisher_id:int) -> str:
    ''''''
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
        return cur.fetchone()
    finally:
        conn.close()


def get_publishers_email(publisher_id:int) -> str:
    ''''''
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
        return cur.fetchone()
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
        return cur.fetchall()[1][0]
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
        return cur.fetchall()[1][0]
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
        print(sql)
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
    ''''''
    publisher_name = get_publishers_name(publisher_id)
    author_ids = get_publishers_tracked_authors(publisher_id)
    html_cards = ""
    for id in author_ids:
        print(author_ids, id)
        id = id[0]
        html_cards = html_cards+generate_author_html_container(id)

    html = f'''
    <body>
    Dear {publisher_name}, <br><br>The following authors had noteworthy engagement:
    '''
    html = html +html_cards
    return html + '</body>'

def format_html_email(body:str) -> str:
    '''Formats the html for an email'''
    return '<html lang="en">' + body + '</html>'

 
def send_email(email_html: str): # TODO
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


def write_to_html_for_test(html:str) -> None:
    with open('test.html', 'w', encoding='utf-8') as f:
        f.write(html)


if __name__ == "__main__":
    body = generate_html_body(1)
    html = (format_html_email(body))
    write_to_html_for_test(html)
    print(get_avg_rating_difference_since_yesterday(3),'a')