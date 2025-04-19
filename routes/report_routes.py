from flask import Blueprint,request, jsonify, make_response
from flask_jwt_extended import jwt_required
from utils.db import get_db_connection

report_bp = Blueprint('report', __name__)

@report_bp.route('/reports/top_10_courses', methods=['GET'])
@jwt_required()
def top_10_courses():
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("""
            SELECT course_id, COUNT(*) AS num_students
            FROM enrollments
            GROUP BY course_id
            ORDER BY num_students DESC
            LIMIT 10
        """)
        courses = []
        for course_id, num_students in cursor:
            courses.append({'course_id': course_id, 'num_students': num_students})
        cursor.close()
        cnx.close()
        return make_response(jsonify(courses), 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

@report_bp.route('/reports/top_10_students', methods=['GET'])
@jwt_required()
def top_10_students():
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("""
            SELECT student_id, AVG(grade) AS avg_grade
            FROM grades
            GROUP BY student_id
            ORDER BY avg_grade DESC
            LIMIT 10""")
        students = []
        for student_id, avg_grade in cursor:
            students.append({'student_id': student_id, 'avg_grade': avg_grade})
        cursor.close()
        cnx.close()
        return make_response(jsonify(students), 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)
