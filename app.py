from flask import Flask, request, make_response, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from  flask_cors import CORS, cross_origin
import json
import mysql.connector


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
jwt = JWTManager(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

db_config = {
    "host": "127.0.0.1",
    "user": "group1",
    "password": "12345",
    "database": "OURVLE"
}

from flask_jwt_extended import create_access_token, decode_token


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
    first_name = data['first_name']
    last_name = data['last_name']
    password = data['password']
    account_type = data['AccountType']
    try:
        #Creates the new if there are no problems
        cursor.execute("INSERT INTO account (Password, AccountType) VALUES (%s, %s)", (password, account_type))

        acc_id = cursor.lastrowid

        cursor.execute(f"INSERT INTO {account_type} (UserID, FirstName, LastName)"
                        " VALUES (%s, %s, %s)",
                        (acc_id, first_name, last_name))

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
        UserID = data.get('UserID')
        password = data.get('password')
        cursor.execute("SELECT * FROM account WHERE UserID = %s AND password = %s", (UserID, password))
        user = cursor.fetchone()
        cursor.close()
        cnx.close()

        print(user)

        if user:
            token = create_access_token(identity=json.dumps({"id": user.get('UserID'), "role": user['AccountType']}))
            return make_response(jsonify(token=token), 200)
        
        return make_response(jsonify(message='Invalid credentials.Please try again'), 401)
    
    except Exception as e:
       return make_response(jsonify(error=f"Login failed: {str(e)}"), 400)
    

#Only allows admin to create courses
@app.route('/create_course', methods=['POST'])
@jwt_required()
def create_course():
    jwt_id = get_jwt_identity()
    identity = json.loads(jwt_id)
    
    if identity['role'] != 'admin':
        return make_response(jsonify(message='Unauthorized'), 403)

    data = request.get_json()
    cnx = get_db_connection()
    cursor = cnx.cursor()
    courseName = data['CourseName']
    lecturerid = data['lecturer_id']

    #check to see if lecturer is teaching more than 4 courses
    try:
        cursor.execute("SELECT COUNT(CourseID) FROM teach WHERE UserID = %s GROUP BY UserID", (lecturerid,))
        CourseCount = cursor.fetchone()

        if CourseCount and CourseCount[0] >= 5:
            return make_response(jsonify(error=f"Course was not created. Lecturer {lecturerid} is assigned to 5 courses.:"), 400)
    except:
        return make_response(jsonify(error=f"Course was not created: {str(e)}"), 400)

    try:
        cursor.execute("INSERT INTO course (CourseName) VALUES (%s)", (courseName,))
        cnx.commit()

        courseId = cursor.lastrowid
        print(courseId)
        cursor.execute("INSERT INTO teach (CourseID, UserID) VALUES (%s, %s)",
                       (courseId, lecturerid))
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
        cursor.execute("SELECT * FROM course")
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
            SELECT c.* FROM course c
            JOIN assigned a ON a.CourseID = c.CourseID
            WHERE a.UserID = %s
        """, (student_id,))

        courses = cursor.fetchall()
        cursor.close()
        cnx.close()

        return make_response(jsonify(courses), 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)
    
@app.route('/lecturers/<lecturer_id>/courses', methods=['GET'])
@jwt_required()
def get_lecturer_courses(lecturer_id):
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""SELECT c.* FROM course c 
                       JOIN teach t ON t.CourseID = c.CourseID
                       WHERE t.UserID = %s""", (lecturer_id,))
        courses = cursor.fetchall()
        cursor.close()
        cnx.close()

        return make_response(jsonify(courses), 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)


@app.route('/courses/<courseId>/enroll', methods=['POST'])
@jwt_required()
def enroll_course(courseId):
    try:
        jwt_id = get_jwt_identity()
        print(jwt_id)
        identity = json.loads(jwt_id)

        cnx = get_db_connection()
        cursor = cnx.cursor()

        if identity['role'] != 'student':
            return make_response({'message': 'Only students can enroll'}, 403)
        
        #check to see if a student is doing more than 5 courses
        cursor.execute(f"SELECT COUNT(CourseID) FROM Assigned WHERE UserID = {identity['id']} GROUP BY UserID")
        CourseCount = cursor.fetchone()

        course_count = CourseCount[0]

        if course_count > 5:
            return make_response(jsonify(error=f"Course was not enrolled. Student {identity['id']} is assigned to 6 courses."), 400)
    
        cursor.execute("INSERT INTO assigned (CourseID, UserID) VALUES (%s, %s)",
                       (courseId, identity['id']))
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
            SELECT s.UserID, s.FirstName, s.LastName FROM student s
            JOIN assigned a ON a.UserID = s.UserID
            WHERE a.courseId = %s
        """, (courseId,))
        students = cursor.fetchall()

        cursor.execute("""
                    SELECT l.UserID, l.FirstName, l.LastName FROM lecturer l
                    JOIN teach t ON t.UserID = l.UserID
                    WHERE t.courseId = %s
                """, (courseId,))
        lecturers = cursor.fetchall()

        cursor.close()
        cnx.close()
        return make_response(jsonify({"students": students,
                                      "lecturer": lecturers}), 200)
    except Exception as e:
        return make_response({'error':f"Could not get course members: {str(e)}"}, 400)

@app.route('/courses/<course_id>/calendar', methods=['GET'])
@jwt_required()
def get_course_calendar(course_id):
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM calendarevents WHERE CourseID = %s", (course_id,))
        calendar_events = cursor.fetchall()

        cursor.close()
        cnx.close()
        return make_response(jsonify(calendar_events), 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

@app.route('/students/<student_id>/calendar/<date>', methods=['GET'])
@jwt_required()
def get_student_calendar_by_date(student_id, date):
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.EventID, c.DueDate, c.Title FROM calendarevents c
            JOIN assigned a ON a.CourseID = c.CourseId
            WHERE a.UserID = %s AND c.DueDate = %s
        """, (student_id, date))
        events = cursor.fetchall()
        cnx.close()

        return make_response(jsonify(events), 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

@app.route('/calendar', methods=['POST'])
@jwt_required()
def create_calendar_event():
    jwt_id = get_jwt_identity()
    identity = json.loads(jwt_id)

    if identity['role'] != 'lecturer':
        return make_response({'message': 'Only lecturers can create calendar events'}, 403)

    try:
        content = request.json
        courseId = content['courseId']
        event_date = content['event_date']
        title = content['title']

        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO calendarevents (CourseID, Title, DueDate) VALUES (%s, %s, %s)",
                       (courseId, title, event_date))
        cnx.commit()
        cursor.close()
        cnx.close()

        return make_response({'message': 'Calendar event is created'}, 201)
    except Exception as e:
        return make_response({'error': f'Calendar event was not created: {str(e)}'}, 400)

@app.route('/courses/<course_id>/forums', methods=['GET'])
@jwt_required()
def get_forums(course_id):
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM discussionforum WHERE CourseID = %s",(course_id,))
        forums = cursor.fetchall()
        cursor.close()
        cnx.close()

        return make_response(jsonify(forums), 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

@app.route('/forums', methods=['POST'])
@jwt_required()
def create_forum():

    jwt_id = get_jwt_identity()
    identity = json.loads(jwt_id)

    # only lecturer can create a forum
    if identity['role'] != 'lecturer':
        return make_response({'message': 'Only lecturers can create calendar events'}, 403)

    try:

        content = request.json
        courseId = content['courseId']
        title = content['title']
        question = content['question']

        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO discussionforum (CourseID, Title, Question) VALUES (%s, %s, %s)", (courseId, title, question))
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
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.ThreadID, t.ParentThreadId, t.ForumID, t.UserID AS created_by, t.Message
            FROM discussionthread t
            JOIN account a ON t.UserID = a.UserID
            WHERE t.ForumID = %s
        """, (forum_id,))
        threads = cursor.fetchall()
        cursor.close()
        cnx.close()

        return make_response(jsonify(threads), 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

#get all top level threads
@app.route('/forums/<forum_id>/threads', methods=['POST'])
@jwt_required()
def create_thread(forum_id):
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        content = request.json
        message = content['message']
        parent_id = content.get('parent_id')
        identity = json.loads(get_jwt_identity())
        created_by = identity.get('id') 
        
        cursor.execute("""
            INSERT INTO discussionthread (ForumID, UserID, Message, ParentThreadId)
            VALUES (%s, %s, %s, %s)
        """, (forum_id, created_by, message, parent_id))
        cnx.commit()
        cursor.close()
        cnx.close()

        return make_response({"message": "Thread created successfully."}, 201)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

#create replies
@app.route('/threads/<thread_id>/replies', methods=['POST'])
@jwt_required()
def create_reply():
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        content = request.json
        message = content['message']
        parent_id = content.get('parent_id')
        identity = json.loads(get_jwt_identity())
        created_by = identity.get('id')

        cursor.execute("""
            INSERT INTO discussionthread (UserID, Message, ParentThreadId)
            VALUES (%s, %s, %s)
        """, (created_by, message, parent_id))

        cnx.commit()
        cursor.close()
        cnx.close()
        return make_response({"message": "Reply created successfully."}, 201)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

#get all replies
@app.route('/threads/<thread_id>/replies', methods=['GET'])
@jwt_required()
def get_replies(thread_id):
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.ThreadID, r.Message, r.UserID AS created_by
            FROM discussionthread r
            JOIN account a ON r.UserID = a.UserID
            WHERE r.ParentThreadId = %s
        """, (thread_id,))
        replies = cursor.fetchall()
        cursor.close()
        cnx.close()

        return make_response(jsonify(replies), 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

@app.route('/assignments/<assignment_id>/submit', methods=['POST'])
@jwt_required()
def submit_assignment(assignment_id):
    jwt_id = get_jwt_identity()
    identity = json.loads(jwt_id)
    if identity['role'] != 'student':
        return make_response({'error': 'Only students can submit assignments'}, 401)
    try:
        student_id = identity.get('id')
        cnx = get_db_connection()
        cursor = cnx.cursor()
        content = request.json
        submission_date = content['submission_date']

        cursor.execute("""
            INSERT INTO submitassignment (UserID, AssignmentID, SubmissionDate) 
            VALUES (%s, %s, %s)
        """, (student_id, assignment_id, submission_date))
        cnx.commit()
        cursor.close()
        cnx.close()

        return make_response({"message": "Assignment submitted successfully."}, 201)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

@app.route('/assignments/<submission_id>/grade', methods=['POST'])
@jwt_required()
def grade_submission(submission_id):
    jwt_id = get_jwt_identity()
    identity = json.loads(jwt_id)
    if identity['role'] != 'lecturer':
        return make_response({'error': 'Only lecturers can grade assignments'}, 401)

    try:
        lecturer_id = identity.get('id')
        cnx = get_db_connection()
        cursor = cnx.cursor()
        content = request.json
        grade = content['grade']

        cursor.execute("""
            INSERT INTO grading (SubmissionID, UserID, Grade)
            VALUES (%s, %s, %s)
        """, (submission_id, lecturer_id, grade))
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
        cursor = cnx.cursor(dictionary=True)

        cursor.execute("""
            SELECT s.SubmissionID, g.grade, s.UserID AS student_name
            FROM grading g
            JOIN submitassignment s ON g.SubmissionID = s.SubmissionID
            WHERE s.AssignmentID = %s
        """, (assignment_id,))
        grades = cursor.fetchall()
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
        cursor.execute("SELECT * FROM top_10_most_enrolled_courses")
        courses = cursor.fetchall()
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
        cursor.execute("SELECT * FROM top_10_highest_average")
        students = cursor.fetchall()
        cursor.close()
        cnx.close()
        return make_response(jsonify(students), 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

@app.route('/reports/up-50-students', methods=['GET'])
@jwt_required()
def up_50_students():
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM courses_with_50_or_more_students")
        courses = cursor.fetchall()
        cursor.close()
        cnx.close()
        return make_response(jsonify(courses), 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

@app.route('/reports/up-5-courses', methods=['GET'])
@jwt_required()
def up_5_courses():
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM students_enrolled_in_5_or_more_courses")
        students = cursor.fetchall()
        cursor.close()
        cnx.close()
        return make_response(jsonify(students), 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

@app.route('/reports/up-3-courses', methods=['GET'])
@jwt_required()
def up_3_courses():
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM lecturers_teaching_3_or_more_courses")
        lecturers = cursor.fetchall()
        cursor.close()
        cnx.close()
        return make_response(jsonify(lecturers), 200)
    except Exception as e:
        return make_response({'error': str(e)}, 400)
    
if __name__ == '__main__':
    app.run(port=5000)