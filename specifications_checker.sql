-- To ensure that at least 100,000 students are present in Student Table. This should not return a number less than 100,000
SELECT COUNT(UserID) AS StudentCount
FROM Student;

-- To ensure that at least 200 courses are present in Course table. This should not return a number less than 200
SELECT COUNT(CourseID) AS CourseCount
FROM Course;

-- To ensure that no student can do more than 6 courses.
SELECT UserID, COUNT(CourseID) AS CourseCount
FROM Assigned
GROUP BY UserID
HAVING COUNT(CourseID) >= 7;

-- To ensure that a student must be enrolled in at least 3 courses.
SELECT UserID, COUNT(CourseID) AS CourseCount
FROM Assigned
GROUP BY UserID
HAVING COUNT(CourseID) < 3;

-- To ensure that each course must have at least 10 members.
SELECT CourseID, COUNT(UserID) AS StudentCount
FROM Assigned
GROUP BY CourseID
HAVING COUNT(UserID) < 10;

-- To ensure no lecturer can teach more than 5 courses.
SELECT UserID, COUNT(CourseID) AS CourseCount
FROM Teach 
GROUP BY UserID
HAVING COUNT(CourseID) > 5;

--To ensure a lecturer must teach at least 1 course.
SELECT UserID, COUNT(CourseID) AS CourseCount
FROM Teach 
GROUP BY UserID
HAVING COUNT(CourseID) < 1;

-- To ensure that student data is present in both Account and Student table
SELECT s.UserID
FROM Student s
LEFT JOIN Account a ON s.UserID = a.UserID
WHERE a.UserID IS NULL;

-- To ensure that lecturer data is present in both Account and Lecturer table
SELECT l.UserID
FROM Lecturer l
LEFT JOIN Account a ON l.UserID = a.UserID
WHERE a.UserID IS NULL;

-- To ensure that admin data is present in both Account and Admin table
SELECT ad.UserID
FROM Admin ad
LEFT JOIN Account a ON ad.UserID = a.UserID
WHERE a.UserID IS NULL;

-- To ensure that student data is present in both Student and Assigned table.
SELECT s.UserID
FROM Student s
LEFT JOIN Assigned a ON s.UserID = a.UserID
WHERE a.UserID IS NULL;

-- To ensure that lecturer data is present in both Lecturer and Teach table.
SELECT l.UserID
FROM Lecturer l
LEFT JOIN Teach t ON l.UserID = t.UserID
WHERE t.UserID IS NULL;