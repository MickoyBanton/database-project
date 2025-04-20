from flask import Flask, request, make_response, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import mysql.connector


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
jwt = JWTManager(app)

db_config = {
    "host": "127.0.0.1",
    "user": "shop_user",
    "password": "shop876",
    "database": "shoppers"
}


#This function is used to connect to the database
def get_db_connection():
    return mysql.connector.connect(**db_config)


@app.route('/')
def welcome():
    return "Welcome to OURVLE!"


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    cnx = get_db_connection()
    cursor = cnx.cursor()
    userid = data['userId']
    password = data['password']
    role = data['role']
    try:
        #Checking if this account was already made
        cursor.execute("SELECT * FROM users WHERE userid = %s", (userid,))
        if cursor.fetchone():
            return make_response(jsonify({"error": "User already exists"}), 409)
        
        #Creates the new if there are no problems
        cursor.execute("INSERT INTO users (userid, password, role) VALUES (%s, %s, %s)", 
                       (userid, password, role))
        cnx.commit()
        cursor.close()
        cnx.close()
        return make_response(jsonify({"message":'User registered successfully'}), 201)
    except Exception as e:
        return make_response(jsonify({"error":str(e)}), 400)

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        userid = data['userId']
        password = data['password']
        cursor.execute("SELECT * FROM users WHERE userid = %s AND password = %s", userid, password)
        user = cursor.fetchone()
        cursor.close()
        cnx.close()
        if user:
            token = create_access_token(identity={'id': user['id'], 'role': user['role']})
            return make_response(jsonify(token=token), 200)
        return make_response(jsonify(message='Invalid credentials.Please try again'), 401)
    except Exception as e:
        return make_response(jsonify(error=f"Login failed: {str(e)}"), 400)

#Only allows admin to create courses
@app.route('/create_course', methods=['POST'])
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
    
@app.route('/courses', methods=['GET'])
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

@app.route('/get_student/<student_id>/courses', methods=['GET'])
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
    
@app.route('/lecturers/<lecturerid>/courses', methods=['GET'])
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


@app.route('/courses/<courseId>/enroll', methods=['POST'])
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


@app.route('/courses/<courseId>/members', methods=['GET'])
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

@app.route('/courses/<course_id>/calendar', methods=['GET'])
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

@app.route('/students/<student_id>/calendar/<date>', methods=['GET'])
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

@app.route('/calendar', methods=['POST'])
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

@app.route('/courses/<course_id>/forums', methods=['GET'])
@jwt_required()
def get_forums(courseId):
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM forums WHERE course_id = %s", (course_id,))
        forums = []
        for userid, course_id, title in cursor:
            forums.append({ 'userid': userid, 'courseId': courseId, 'title': title })
        cursor.close()
        cnx.close()
        return make_response(forums, 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

@app.route('/forums', methods=['POST'])
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


@app.route('/forums/<forum_id>/threads', methods=['GET'])
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

@app.route('/forums/<forum_id>/threads', methods=['POST'])
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

@app.route('/threads/<thread_id>/replies', methods=['POST'])
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

@app.route('/threads/<thread_id>/replies', methods=['GET'])
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

@app.route('/assignments/<assignment_id>/submit', methods=['POST'])
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

@app.route('/assignments/<assignment_id>/grade', methods=['POST'])
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

@app.route('/assignments/<assignment_id>/grades', methods=['GET'])
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

@app.route('/reports/top_10_courses', methods=['GET'])
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

@app.route('/reports/top_10_students', methods=['GET'])
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


    
if __name__ == '__main__':
    app.run(port=5000)