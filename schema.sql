CREATE DATABASE IF NOT EXISTS OURVLE;
USE OURVLE;

-- Superclass
CREATE TABLE Account (
    UserID INT PRIMARY KEY AUTO_INCREMENT,
    Password VARCHAR(100) NOT NULL,
    AccountType VARCHAR(9) NOT NULL CHECK (AccountType IN ('Student', 'Lecturer', 'Admin'))
);

-- Subclasses
CREATE TABLE Student (
    UserID INT PRIMARY KEY REFERENCES Account(UserID),
    FirstName VARCHAR(100),
    LastName VARCHAR(100),
    FinalAverage DECIMAL(5,2)
);

CREATE TABLE Lecturer (
    UserID INT PRIMARY KEY REFERENCES Account(UserID),
    FirstName VARCHAR(100),
    LastName VARCHAR(100)
);

CREATE TABLE Admin (
    UserID INT PRIMARY KEY REFERENCES Account(UserID)
);

-- Course Table
CREATE TABLE Course (
    CourseID SERIAL PRIMARY KEY,
    CourseName VARCHAR(100) NOT NULL
);

-- Student-Course Assignment
CREATE TABLE Assigned (
    CourseID BIGINT UNSIGNED,
    UserID INT,
    PRIMARY KEY (CourseID, UserID),
    FOREIGN KEY (CourseID) REFERENCES Course(CourseID),
    FOREIGN KEY (UserID) REFERENCES Student(UserID)
);

-- Lecturer-Course Assignment
CREATE TABLE Teach (
    CourseID BIGINT UNSIGNED,
    UserID INT,
    PRIMARY KEY (CourseID, UserID),
    FOREIGN KEY (CourseID) REFERENCES Course(CourseID),
    FOREIGN KEY (UserID) REFERENCES Lecturer(UserID)
);

-- Assignments
CREATE TABLE Assignment (
    AssignmentID INT PRIMARY KEY AUTO_INCREMENT,
    CourseID BIGINT UNSIGNED,
    AssignmentTitle VARCHAR(200),
    Date DATE,
    FOREIGN KEY (CourseID) REFERENCES Course(CourseID)
);

-- Student Submissions
CREATE TABLE SubmitAssignment (
    SubmissionID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT,
    AssignmentID INT,
    SubmissionDate DATE,
    FOREIGN KEY (UserID) REFERENCES Student(UserID),
    FOREIGN KEY (AssignmentID) REFERENCES Assignment(AssignmentID)
);

-- Grading
CREATE TABLE Grading (
    SubmissionID INT PRIMARY KEY REFERENCES SubmitAssignment(SubmissionID),
    UserID INT,
    Grade DECIMAL(5,2),
    FOREIGN KEY (UserID) REFERENCES Lecturer(UserID)
);

-- Section Table
CREATE TABLE Section (
    SectionID INT PRIMARY KEY AUTO_INCREMENT,
    CourseID INT REFERENCES Course(CourseID),
    UserID INT REFERENCES Lecturer(UserID),
    SectionName VARCHAR(100)
);

-- Section Items
CREATE TABLE SectionItems (
    ItemID SERIAL PRIMARY KEY,
    SectionID INT,
    SectionItem TEXT,
    FileType VARCHAR(9) NOT NULL CHECK (FileType IN ('Links', 'Files', 'Slides')),
    FOREIGN KEY (SectionID) REFERENCES Section(SectionID)
);


-- Discussion Forum
CREATE TABLE DiscussionForum (
    ForumID INT PRIMARY KEY AUTO_INCREMENT,
    CourseID BIGINT UNSIGNED,
    Title VARCHAR(200),
    Question TEXT,
    FOREIGN KEY (CourseID) REFERENCES Course(CourseID)
);

CREATE TABLE DiscussionThread (
    ThreadID INT PRIMARY KEY AUTO_INCREMENT,
    ForumID INT,
    UserID INT,
    Message TEXT,
    ParentThreadId INT,
    FOREIGN KEY (ForumId) REFERENCES DiscussionForum(ForumId),
    FOREIGN KEY (UserId) REFERENCES Account(UserId)
);

-- Calendar Events
CREATE TABLE CalendarEvents (
    EventID INT PRIMARY KEY AUTO_INCREMENT,
    CourseID BIGINT UNSIGNED,
    Title VARCHAR(200),
    DueDate DATE,
    FOREIGN KEY (CourseID) REFERENCES Course(CourseID)
);


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
GROUP BY t.UserID, l.FirstName, l.LastName
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
CREATE VIEW Top_10_Highest_Average AS
SELECT FirstName, LastName, FinalAverage
FROM student
ORDER BY FinalAverage DESC
LIMIT 10;