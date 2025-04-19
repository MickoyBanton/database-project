from flask import Blueprint,request, jsonify, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from utils.db import get_db_connection

assignment_bp = Blueprint('assignment', __name__)

@assignment_bp.route('/assignments/<assignment_id>/submit', methods=['POST'])
@jwt_required()
def submit_assignment(assignment_id):
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        content = request.json
        student_id = content['student_id']
        file_url = content['file_url']
        cursor.execute("""
            INSERT INTO submissions (assignment_id, student_id, file_url) 
            VALUES (%s, %s, %s)
        """, (assignment_id, student_id, file_url))
        cnx.commit()
        cursor.close()
        cnx.close()
        return make_response({"message": "Assignment submitted successfully."}, 201)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

@assignment_bp.route('/assignments/<assignment_id>/grade', methods=['POST'])
@jwt_required()
def grade_assignment(assignment_id):
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        content = request.json
        lecturer_id = content['lecturer_id']
        student_id = content['student_id']
        grade = content['grade']
        cursor.execute("""
            INSERT INTO grades (assignment_id, student_id, lecturer_id, grade) 
            VALUES (%s, %s, %s, %s)
        """, (assignment_id, student_id, lecturer_id, grade))
        cnx.commit()
        cursor.close()
        cnx.close()
        return make_response({"message": "Grade submitted successfully."}, 201)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

@assignment_bp.route('/assignments/<assignment_id>/grades', methods=['GET'])
@jwt_required()
def get_grades(assignment_id):
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("""
            SELECT g.student_id, g.grade, u.userid AS student_name
            FROM grades g
            JOIN users u ON g.student_id = u.id
            WHERE g.assignment_id = %s
        """, (assignment_id,))
        grades = []
        for student_id, grade, student_name in cursor:
            grades.append({'student_name': student_name, 'grade': grade})
        cursor.close()
        cnx.close()
        return make_response(jsonify(grades), 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)