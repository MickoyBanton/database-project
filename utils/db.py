#This function is used to connect to the database
import os

import mysql.connector

import dotenv

dotenv.load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')
HOSTNAME = os.getenv('HOST')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
DATABASE = os.getenv('DATABASE')

db_config = {
    "host": HOSTNAME,
    "user": USER,
    "password": PASSWORD,
    "database": DATABASE,
}

def get_db_connection():
    return mysql.connector.connect(**db_config)
