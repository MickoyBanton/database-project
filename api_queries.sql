-- Register user
-- Check if user exists
SELECT * FROM Account WHERE UserID = {userid};

-- Insert into Account
INSERT INTO Account (UserID, Password, AccountType) VALUES ('{userid}', '{password}', '{accountType}');

-- Check if student exists
SELECT * 
FROM Student 
WHERE UserID = {userid};

-- If student
INSERT INTO Student (UserID, FirstName, LastName,FinalAverage) VALUES ('{userid}', '{firstName}', '{lastName}', NULL);

-- Check if lecturer exists
SELECT * 
FROM Lecturer 
WHERE UserID = {userid};

-- If lecturer
INSERT INTO Lecturer (UserID, LecturerName) VALUES ('{userid}', '{lecturerName}');

--Login User
--To know if it is student or lecturer and to see if the credentials are correct
SELECT UserID, Password, AccountType
FROM Account
WHERE UserID = '{userid}' AND Password = '{password}' AND AccountType = 'Student' OR AccountType = 'Lecturer';

-- Creating a  Course
--- Check admin
SELECT UserID FROM Account WHERE UserID = '{current_user_id}' AND AccountType = 'Admin';

-- Check if course exists
SELECT CourseID FROM Course WHERE CourseID = '{newcourseID}';

-- Insert course
INSERT INTO Course (CourseID, CourseName) VALUES ('{newcourseID}', '{courseName}');


--Retrieve all the courses
SELECT CourseName
FROM Course;


--Retrieve courses for a particular student
SELECT Course.CourseName
FROM Assigned
JOIN Course ON Assigned.CourseID = Course.CourseID
WHERE Assigned.UserID = '{userID}';

--Retrieve courses taught by a particular lecturer
SELECT Course.CourseName
FROM Teach
JOIN Course ON Teach.CourseID = Course.CourseID
WHERE Teach.UserID = '{userID}';

-- Students should be able to register for a course
-- check if user is student
SELECT UserID 
FROM Account 
WHERE UserID = '{current_user_id}' AND AccountType = 'Student';

--check if student is already registerd in the course
SELECT UserID, CourseID
FROM Assigned
WHERE UserID = '{current_user_id}' AND CourseID = '{new_course_id}';

-- Register if not already registered
INSERT INTO Assigned (CourseID, UserID) VALUES ('{courseID}', '{userID}');


--Should return members of a particular course
SELECT  l.FirstName, l.LastName, s.FirstName, s.LastName
FROM Course c
INNER JOIN Teach t ON c.CourseID = t.CourseID
INNER JOIN Lecturer l ON t.UserID = l.UserID
INNER JOIN Assigned a ON c.CourseID = a.CourseID
INNER JOIN Student s ON a.UserID = s.UserID
WHERE c.CourseID = '{courseID}';

--Should be able to retrieve all calendar events for a particular course.
SELECT ce.*
FROM CalendarEvents ce
INNER JOIN Course c ON ce.CourseID = c.CourseID
WHERE c.CourseID = '{courseID}';

--Should be able to retrieve all calendar events for a particular date for a particular student.
SELECT ce.EventID, ce.Title, ce.DueDate, c.CourseName
FROM CalendarEvents ce
JOIN Course c ON ce.CourseID = c.CourseID
JOIN Assigned a ON c.CourseID = a.CourseID
WHERE a.UserID = '{studentUserID}' AND ce.DueDate = '{date}';

--Should be able to create calendar event for a course
--Check to see if the user is a lecturer
SELECT userID
FROM Account
WHERE UserID= '{current_user_id}' AND AccountType = 'Lecturer';

INSERT INTO CalendarEvents (EventID, CourseID, Title, DueDate) VALUES ('{eventID}', '{courseID}', '{title}', '{dueDate}');

--Should be able to retrieve all the forums for a particular course
SELECT Title, Question 
FROM DiscussionForum 
WHERE CourseID = '{courseID}';

--Should be able to create a forum for a particular course
--Check to see if the user is a lecturer
SELECT userID
FROM Account
WHERE UserID= '{current_user_id}' AND AccountType = 'Lecturer';

--Create forum
INSERT INTO DiscussionForum (ForumID, CourseID, Title, Question) VALUES ('{forumID}', '{courseID}', '{title}', '{question}');

--Should be able to retrieve all the discussion threads for a particular forum
SELECT Message, Title
FROM DiscussionThread
WHERE ForumID = {fourmID_entered};

--Should be able to add a new discussion thread to a forum. Each discussion thread should have a title and the post that started the thread.
INSERT INTO DiscussionForum (ForumID, CourseID, Title, Question) VALUES ("1","comp333", 'Presentation', 'Remember your presentation');

-- Should be able to add a new discussion thread to a forum. Each discussion thread should have a title and the post that started the thread.
INSERT INTO DiscussionThread (ThreadID, ForumID, UserID, Message, ParentThreadId) VALUES ('1', '1', '2',"I thought you said it is cancelled.",NULL);

-- Creating a  Course Content
-- check if user is lecturer
SELECT userID
FROM Account
WHERE UserID= {current_user_id} AND AccountType = 'Lecturer';

--Check if lecturer belongs to the course
SELECT CourseID
FROM Teach
WHERE CourseID = '{current_course_id}' AND UserID = '{user_id_entered}';

--Add section Item
INSERT INTO SectionItems (ItemID, SectionID, SectionItem, FileType) VALUES ('{itemID}', '{sectionID}', '{content}','{filetype}');

--Should be able to retrieve all the course content for a particular course
--Check if user is lecturer or student
SELECT UserID 
FROM Account 
WHERE UserID = '{current_user_id}' AND (AccountType = 'Student' OR AccountType = 'Lecturer');


--Check if user is lecturer or student belongs to the course
SELECT a.UserID
FROM Assigned a
JOIN Teach t ON a.CourseID = t.CourseID
WHERE a.UserID = '{current_user_id}' OR t.UserID = '{current_user_id}';

--Retrive Course Material
SELECT c.CourseName, s.SectionName, si.ItemID, si.SectionItem, si.FileType
FROM Course c
JOIN Section s ON c.CourseID = s.CourseID
JOIN SectionItems si ON s.SectionID = si.SectionID
WHERE c.CourseID = {courseID};

--A student can submit assignments for a course
--Check if user is a student
SELECT userID
FROM Account
WHERE UserID= {current_user_id} AND AccountType = 'Student';

--check if student belongs to the course
SELECT CourseID
FROM Assigned
WHERE CourseID = '{current_course_id}' AND UserID = '{user_id_entered}';

--Submiting Asignment
INSERT INTO SubmitAssignment (SubmissionID, UserID, AssignmentID, SubmissionDate) VALUES ('{submissionID}', '{userID}', '{assignmentID}', '{date}');

-- A lecturer can submit a grade for a particular student for that assignment
--Check if user is lecturer
SELECT userID
FROM Account
WHERE UserID= {current_user_id} AND AccountType = 'Lecturer';

--Check if lecturer belongs to the course
SELECT CourseID
FROM Teach
WHERE CourseID = '{current_course_id}' AND UserID = '{user_id_entered}';

--Grading Assignemnt
INSERT INTO Grading (SubmissionID, UserID, Grade) VALUES ('{submissionID}', '{lecturerID}', '{grade}');

--Each grade a student gets goes to their final average
UPDATE Student
SET FinalAverage = (
    SELECT AVG(g.Grade)
    FROM SubmitAssignment sa
    JOIN Grading g ON sa.SubmissionID = g.SubmissionID
    WHERE sa.UserID = Student.UserID
); 


--All courses that have 50 or more students
CREATE VIEW Courses_With_50_Or_More_Students AS
SELECT a.CourseID, c.CourseName, COUNT(a.UserID) AS StudentCount
FROM Assigned a
INNER JOIN Course c 
ON a.CourseID = c.CourseID
GROUP BY a.CourseID, c.CourseName
HAVING COUNT(a.UserID) >= 50;


--All students that do 5 or more courses.
CREATE VIEW Students_Enrolled_In_5_Or_More_Courses  AS 
SELECT a.UserID, s.FirstName, s.LastName, COUNT(a.CourseID) AS CourseCount
FROM Assigned a
INNER JOIN Student s
ON a.UserID = s.UserID
GROUP BY a.UserID, s.FirstName, s.LastName
HAVING COUNT(a.CourseID) >= 5; 

--All lecturers that teach 3 or more courses.
CREATE VIEW Lecturers_Teaching_3_Or_More_Courses  AS 
SELECT t.UserID, l.LecturerName, COUNT(t.CourseID) AS CourseCount
FROM Teach t
INNER JOIN Lecturer l
ON t.UserID = l.UserID
GROUP BY t.UserID, l.LecturerName
HAVING COUNT(t.CourseID) >= 3;

--The 10 most enrolled courses
CREATE VIEW Top_10_Most_Enrolled_Courses AS
SELECT a.CourseID, c.CourseName, COUNT(a.UserID) AS NumEnrolled
FROM Assigned a
INNER JOIN Course c 
ON a.CourseID = c.CourseID
GROUP BY a.CourseID, c.CourseName
ORDER BY NumEnrolled DESC
LIMIT 10;

--The top 10 students with the highest overall averages
CREATE VIEW Top_10_Highest_Average AS
SELECT FirstName, LastName, FinalAverage
FROM student
ORDER BY FinalAverage DESC
LIMIT 10;