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
            a.author_id, a.author_name
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


# def generate_html_head(publisher_name:str) ->str:
#     '''DEPRECATED.'''
#     # TODO
#     html = f'''
#     <head>
#         <meta charset="UTF-8">
#             <meta name="viewport" content="width=device-width, initial-scale=1.0">
#         <title>{publisher_name}'s Daily Author Tracking</title>
#     </head>
#     '''
#     return html

def get_image_url_from_author_id() -> str:
    '''Gets the author's image from their id'''
    try:
        conn = get_db_connection()
        sql = '''
        SELECT 
        FROM
        WHERE
        '''
    finally:
        conn.close()

def generate_author_container(author_id:int) -> str:
    ''''''
    image_url = TEST_IMAGE_URL
    daily_shelved = '--'
    avg_rating_change ='--'
    container_html = f'''
        <table width="100%" border="0" cellspacing="0" cellpadding="0"> 
          <tr>
            <td align="left" valign="top" width="150" style="padding: 10px;">
              <img src="{image_url}" width="150" alt="A picture of the author" style="display: block;">
            </td>
            <td align="left" valign="top" style="padding: 10px; font-family: Arial;">
              <h3 style="margin: 0;">Author engagement:</h3>
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
    # TODO
    publisher_name = 'Suzanne collins'
    html = f'''
    <body>
    Dear {publisher_name}, 

    The following authors had noteworthy engagement:
    '''

    html_cards = generate_author_container(2)
    html = html+(html_cards*100)
    return html + '</body>'

def format_html_email(publisher_id:int,head:str,body:str) -> str:
    '''Formats the html for a given publisher'''

    return '<html lang="en">' + body + '</html>'

 
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


def write_to_html_for_test(html:str) -> None:
    with open('test.html', 'w', encoding='utf-8') as f:
        f.write(html)


if __name__ == "__main__":
    body = generate_html_body(2)
    head = 'a' #generate_html_head(2)

    html = (format_html_email(1,head,body))
    write_to_html_for_test(html)
