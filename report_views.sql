-- All courses that have 50 or more students
CREATE VIEW Courses_With_50_Or_More_Students AS
SELECT a.CourseID, c.CourseName, COUNT(a.UserID) AS StudentCount
FROM Assigned a
INNER JOIN Course c
ON a.CourseID = c.CourseID
GROUP BY a.CourseID, c.CourseName
HAVING COUNT(a.UserID) >= 50;

-- All students that do 5 or more courses.
CREATE VIEW Students_Enrolled_In_5_Or_More_Courses  AS 
SELECT a.UserID, s.FirstName, s.LastName, COUNT(a.CourseID) AS CourseCount
FROM Assigned a
INNER JOIN Student s
ON a.UserID = s.UserID
GROUP BY a.UserID, s.FirstName, s.LastName
HAVING COUNT(a.CourseID) >= 5; 

-- All lecturers that teach 3 or more courses.
CREATE VIEW Lecturers_Teaching_3_Or_More_Courses  AS 
SELECT t.UserID, l.FirstName, l.LastName, COUNT(t.CourseID) AS CourseCount
FROM Teach t
INNER JOIN Lecturer l
ON t.UserID = l.UserID
GROUP BY t.UserID, l.LastName, l.FirstName
HAVING COUNT(t.CourseID) >= 3;

-- The 10 most enrolled courses
CREATE VIEW Top_10_Most_Enrolled_Courses AS
SELECT a.CourseID, c.CourseName, COUNT(a.UserID) AS NumEnrolled
FROM Assigned a
INNER JOIN Course c 
ON a.CourseID = c.CourseID
GROUP BY a.CourseID, c.CourseName
ORDER BY NumEnrolled DESC
LIMIT 10;

-- The top 10 students with the highest overall averages
CREATE OR REPLACE VIEW Top10StudentsByAverage AS
SELECT s.UserID, s.FirstName, s.LastName, ROUND(AVG(g.Grade), 2) AS AverageGrade
FROM Student s
JOIN SubmitAssignment sa ON s.UserID = sa.UserID
JOIN Grading g ON sa.SubmissionID = g.SubmissionID
GROUP BY s.UserID, s.FirstName, s.LastName
ORDER BY AverageGrade DESC
LIMIT 10;

