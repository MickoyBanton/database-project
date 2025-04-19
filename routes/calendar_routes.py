from flask import Blueprint,request, jsonify, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from utils.db import get_db_connection

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/calendar', methods=['POST'])
@jwt_required()
def create_calendar_event():
    try:
        identity = get_jwt_identity()
        content = request.json
        courseId = content['courseId']
        event_date = content['event_date']
        description = content['description']

        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO calendar (course_id, event_date, description) VALUES (%s, %s, %s)",
                       (courseId, event_date, description))
        cnx.commit()
        cursor.close()
        cnx.close()
        return make_response({'message': 'Calendar event is created'}, 201)
    except Exception as e:
        return make_response({'error': f'Calendar event was not created: {str(e)}'}, 400)


@calendar_bp.route('/courses/<course_id>/calendar', methods=['GET'])
@jwt_required()
def get_course_calendar(course_id):
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM calendar WHERE course_id = %s", (course_id,))
        calendar_events = []
        for id, course_id, event_date, description in cursor:
            event = {
                'id': id,
                'course_id': course_id,
                'event_date': str(event_date),
                'description': description
            }
            calendar_events.append(event)
        cursor.close()
        cnx.close()
        return make_response(calendar_events, 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

@calendar_bp.route('/students/<student_id>/calendar/<date>', methods=['GET'])
@jwt_required()
def get_student_calendar_by_date(student_id, date):
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("""
            SELECT c.id, c.event_date, c.description FROM calendar c
            JOIN enrollments e ON e.course_id = c.course_id
            WHERE e.student_id = %s AND c.event_date = %s
        """, (student_id, date))
        events = []
        for id, event_date, description in cursor:
            events.append({
                'id': id,
                'event_date': str(event_date),
                'description': description
            })
        cursor.close()
        cnx.close()
        return make_response(events, 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)