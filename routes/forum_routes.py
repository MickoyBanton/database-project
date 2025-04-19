from flask import Blueprint,request, jsonify, make_response
from flask_jwt_extended import jwt_required
from utils.db import get_db_connection

forum_bp = Blueprint('forum', __name__)

@forum_bp.route('/courses/<course_id>/forums', methods=['GET'])
@jwt_required()
def get_forums(course_id):
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM forums WHERE course_id = %s", (course_id,))
        forums = []
        for userid, course_id, title in cursor:
            forums.append({ 'userid': userid, 'courseId': course_id, 'title': title})
        cursor.close()
        cnx.close()
        return make_response(forums, 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

@forum_bp.route('/forums', methods=['POST'])
@jwt_required()
def create_forum():
    try:
        content = request.json
        courseId = content['courseId']
        title = content['title']

        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO forums (courseId, title) VALUES (%s, %s)", (courseId, title))
        cnx.commit()
        cursor.close()
        cnx.close()
        return make_response({'message': 'Forum created'}, 201)
    except Exception as e:
        return make_response({'error': str(e)}, 400)


@forum_bp.route('/forums/<forum_id>/threads', methods=['GET'])
@jwt_required()
def get_threads(forum_id):
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("""
            SELECT t.id, t.title, t.created_at, u.userid AS created_by
            FROM threads t
            JOIN users u ON t.created_by = u.id
            WHERE t.forum_id = %s
        """, (forum_id,))
        threads = []
        for id, title, created_at, created_by in cursor:
            thread = {
                'id': id,
                'title': title,
                'created_at': created_at,
                'created_by': created_by
            }
            threads.append(thread)
        cursor.close()
        cnx.close()
        return make_response(jsonify(threads), 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

@forum_bp.route('/forums/<forum_id>/threads', methods=['POST'])
@jwt_required()
def create_thread(forum_id):
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        content = request.json
        title = content['title']
        created_by = content['created_by']  # Typically retrieved from JWT token
        cursor.execute("""
            INSERT INTO threads (forum_id, title, created_by) 
            VALUES (%s, %s, %s)
        """, (forum_id, title, created_by))
        cnx.commit()
        cursor.close()
        cnx.close()
        return make_response({"message": "Thread created successfully."}, 201)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

@forum_bp.route('/threads/<thread_id>/replies', methods=['POST'])
@jwt_required()
def create_reply(thread_id):
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        content = request.json
        reply = content['reply']
        created_by = content['created_by']  # User making the reply
        cursor.execute("""
            INSERT INTO replies (thread_id, reply, created_by) 
            VALUES (%s, %s, %s)
        """, (thread_id, reply, created_by))
        cnx.commit()
        cursor.close()
        cnx.close()
        return make_response({"message": "Reply created successfully."}, 201)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

@forum_bp.route('/threads/<thread_id>/replies', methods=['GET'])
@jwt_required()
def get_replies(thread_id):
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("""
            SELECT r.id, r.reply, r.created_at, u.userid AS created_by
            FROM replies r
            JOIN users u ON r.created_by = u.id
            WHERE r.thread_id = %s
        """, (thread_id,))
        replies = []
        for id, reply, created_at, created_by in cursor:
            reply_obj = {
                'id': id,
                'reply': reply,
                'created_at': created_at,
                'created_by': created_by
            }
            replies.append(reply_obj)
        cursor.close()
        cnx.close()
        return make_response(jsonify(replies), 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)