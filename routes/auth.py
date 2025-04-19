from flask import Blueprint,request, jsonify, make_response
from flask_jwt_extended import create_access_token
from utils.db import get_db_connection

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    cnx = get_db_connection()
    cursor = cnx.cursor()
    userid = data['userId']
    password = data['password']
    role = data['role']
    try:
        #Checking if this account was already made
        cursor.execute("SELECT * FROM account WHERE userid = %s", (userid,))
        if cursor.fetchone():
            return make_response(jsonify({"error": "User already exists"}), 409)

        #Creates the new if there are no problems
        cursor.execute("INSERT INTO account (userid, password, AccountType) VALUES (%s, %s, %s)",
                       (userid, password, role))
        cnx.commit()
        cursor.close()
        cnx.close()
        return make_response(jsonify({"message":'User registered successfully'}), 201)
    except Exception as e:
        return make_response(jsonify({"error":str(e)}), 400)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        userid = data['userId']
        password = data['password']
        cursor.execute("SELECT * FROM account WHERE userid = %s AND password = %s", userid, password)
        user = cursor.fetchone()
        cursor.close()
        cnx.close()
        if user:
            token = create_access_token(identity={'id': user['id'], 'role': user['role']})
            return make_response(jsonify(token=token), 200)
        return make_response(jsonify(message='Invalid credentials.Please try again'), 401)
    except Exception as e:
        return make_response(jsonify(error=f"Login failed: {str(e)}"), 400)