from flask import Blueprint,request, jsonify, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from utils.db import get_db_connection

course_bp = Blueprint('course', __name__)

#Only allows admin to create courses
@course_bp.route('/create_course', methods=['POST'])
@jwt_required()
def create_course():
    identity = get_jwt_identity()
    if identity['role'] != 'admin':
        return make_response(jsonify(message='Unauthorized'), 403)
    data = request.get_json()
    cnx = get_db_connection()
    cursor = cnx.cursor()
    courseName = data['CourseName']
    courseId = data['courseId']
    lecturerid = data['lecturer_id']
    try:
        cursor.execute("INSERT INTO courses (courseName, courseId, lecturer_id) VALUES (%s, %s, %s)",
                    (courseName, courseId, lecturerid))
        cnx.commit()
        cursor.close()
        cnx.close()
        return make_response(jsonify(message='Course created'), 201)
    except Exception as e:
        return make_response(jsonify(error=f"Course was not created: {str(e)}"), 400)

@course_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_courses():
    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM courses")
        courses = cursor.fetchall()
        cursor.close()
        cnx.close()
        return make_response(jsonify(courses), 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

@course_bp.route('/get_student/<student_id>/courses', methods=['GET'])
@jwt_required()
def get_student_courses(student_id):
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.* FROM courses c
            JOIN enrollments e ON e.course_id = c.id
            WHERE e.student_id = %s
        """, (student_id,))
        courses = cursor.fetchall()
        cursor.close()
        cnx.close()
        return make_response(jsonify(courses), 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

@course_bp.route('/lecturers/<lecturerid>/courses', methods=['GET'])
@jwt_required()
def get_lecturer_courses(lecturerid):
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM courses WHERE lecturerid = %s", (lecturerid,))
        courses = cursor.fetchall()
        cursor.close()
        cnx.close()
        return make_response(courses, 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)


@course_bp.route('/courses/<courseId>/enroll', methods=['POST'])
@jwt_required()
def enroll_course(courseId):
    try:
        identity = get_jwt_identity()
        if identity['role'] != 'student':
            return make_response({'message': 'Only students can enroll'}, 403)

        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO enrollments (student_id, course_id) VALUES (%s, %s)",
                       (identity['id'], courseId))
        cnx.commit()
        cursor.close()
        cnx.close()
        return make_response({'message': 'Enrolled successfully'}, 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)


@course_bp.route('/courses/<courseId>/members', methods=['GET'])
@jwt_required()
def get_course_members(courseId):
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.id, u.userid, u.role FROM users u
            JOIN enrollments ON e.student_id = u.id
            WHERE e.courseId = %s
        """, (courseId,))
        members = cursor.fetchall()
        cursor.close()
        cnx.close()
        return make_response(members, 200)
    except Exception as e:
        return make_response({'error':f"Could not get course members: {str(e)}"}, 400)
