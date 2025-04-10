"""
Test python script to be converted into a Docker image and 
be pushed to the relevant ECR repository created by the 
terraform/main.tf using step 1

This should be replaced with the python script you want to
upload to one of the lambda functions
"""
from dotenv import load_dotenv
import psycopg2

def get_db_connection() ->psycopg2.connection:
    load_dotenv()
    return psycopg2.connect(
        database=,
        user=,
        host=,
        password=,
        port=
    )


def handler():
    "Example function in this script"
    print("This script has been uploaded correctly.")


if __name__ == "__main__":
    handler()
