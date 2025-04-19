-- Superclass
CREATE TABLE Account (
    UserID PRIMARY KEY,
    Password VARCHAR(100) NOT NULL,
    AccountType VARCHAR(9) NOT NULL CHECK (AccountType IN ('Student', 'Lecturer', 'Admin'))
);

-- Subclasses
CREATE TABLE Student (
    UserID INT PRIMARY KEY REFERENCES Account(UserID),
    StudentName VARCHAR(100),
    FinalAverage DECIMAL(5,2)
);

CREATE TABLE Lecturer (
    UserID INT PRIMARY KEY REFERENCES Account(UserID),
    LecturerName VARCHAR(100)
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
    CourseID INT,
    UserID INT,
    PRIMARY KEY (CourseID, UserID),
    FOREIGN KEY (CourseID) REFERENCES Course(CourseID),
    FOREIGN KEY (UserID) REFERENCES Student(UserID),
);

-- Lecturer-Course Assignment
CREATE TABLE Teach (
    CourseID INT,
    UserID INT,
    PRIMARY KEY (CourseID, UserID),
    FOREIGN KEY (CourseID) REFERENCES Course(CourseID),
    FOREIGN KEY (UserID) REFERENCES Lecturer(UserID),
);

-- Assignments
CREATE TABLE Assignment (
    AssignmentID INT PRIMARY KEY AUTO_INCREMENT,
    CourseID INT,
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
    SectionItem TEXT
    FOREIGN KEY SectionID REFERENCES Section(SectionID)
);


-- Discussion Forum
CREATE TABLE DiscussionForum (
    ForumID INT PRIMARY KEY AUTO_INCREMENT,
    CourseID INT,
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
    CourseID INT,
    Title VARCHAR(200),
    DueDate DATE,
    FOREIGN KEY (CourseID) REFERENCES Course(CourseID)
);
