import os
import dotenv

from flask import Flask
from flask_jwt_extended import JWTManager
from utils.db import get_db_connection
from routes import register_blueprints

dotenv.load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = SECRET_KEY
jwt = JWTManager(app)

register_blueprints(app)

def test_connection():
    if get_db_connection():
        print("Connection established")
        return True
    else:
        print("Connection failed")
        return False

@app.route('/')
def welcome():
    return "Welcome to OURVLE!"

if __name__ == '__main__':
    if test_connection():
        app.run(port=5000)