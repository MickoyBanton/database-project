using System.Text;

namespace SQLCreator
{
    internal class Program
    {
        static Random rand = new Random();

        static Table studentsTable = new Table("Student", "UserID", "FirstName", "LastName");
        readonly static int STUDENTS = 100000;
        static int studentsCreated = 0;
        static int minCoursePerStudent = 3;
        static int maxCoursePerStudent = 6;
        static string[] studentQueries = new string[STUDENTS];

        static Table coursesTable = new Table("Course", "CourseID", "CourseName");
        readonly static int COURSES = 500;
        static int coursesCreated = 0;
        static string[] courseNames = new string[COURSES];
        static string[] courseQueries = new string[COURSES];
        static Dictionary<int, (int maxStudents, int currentStudents)> courseEnrolments = new Dictionary<int, (int, int)>();
        readonly static int LIMCOURSEMIN = 30;
        readonly static int LIMCOURSEMAX = 49;
        static List<int> availableCourses = new List<int>();

        static Table eventsTable = new Table("CalendarEvents", "EventID", "CourseID", "Title", "DueDate");
        static int eventsCreated = 0;
        readonly static int EVENTSMIN = 0;
        readonly static int EVENTSMAX = 2;
        static List<string> eventQueries = new List<string>();

        static Table forumTable = new Table("DiscussionForum", "ForumID", "CourseID", "Title", "Question");
        static int forumsCreated = 0;
        readonly static int MINFORUMS = 0;
        readonly static int MAXFORUMS = 4;
        static List<string> forumQueries = new List<string>();

        static Table threadTable = new Table("DiscussionThread", "ThreadID", "ForumID", "UserID", "Message", "ParentThreadId");
        static int threadsCreated = 0;
        readonly static int MINTHREADS = 0;
        readonly static int MAXTHREADS = 2;
        static List<string> threadQueries = new List<string>();

        static Table sectionsTable = new Table("Section", "SectionID", "CourseID", "SectionName");
        readonly static int MINSECTIONS = 1;
        readonly static int MAXSECTIONS = 4;
        static int sectionsCreated = 0;
        static List<string> sectionQueries = new List<string>();

        static Table sectionItemsTable = new Table("SectionItems", "ItemID", "SectionID", "SectionItem", "FileType");
        static int sectionItemsCreated = 0;
        static List<string> sectionItemQueries = new List<string>();

        static Table submissionTable = new Table("SubmitAssignment", "SubmissionID", "UserID", "AssignmentID", "SubmissionDate");
        static int submissionsMade = 0;
        static List<string> submissionQueries = new List<string>();

        static Table assignmentsTable = new Table("Assignment", "AssignmentID", "CourseID", "AssignmentTitle", "Date");
        static int assignmentsCreated = 0;
        static string[] assignmentQueries = new string[COURSES];

        static Table gradeTable = new Table("Grading", "SubmissionID", "Grade");
        static List<string> gradeQueries = new List<string>();

        static Table assignedTable = new Table("Assigned", "CourseID", "UserID");
        static List<string> assignedQueries = new List<string>();
        static int assignedTracker = 0;
        readonly static int MINASSIGNMENTS = 10;
        static int currentAssignments = 0;

        static Table lecturersTable = new Table("Lecturer", "UserID", "firstName", "lastName");
        readonly static int LECTURERS = 211;
        static int lecturersCreated = 0;
        static int[] lecturerIds = new int[LECTURERS];
        static string[] lecturerQueries = new string[LECTURERS];

        static Table teachTable = new Table("Teach", "CourseID", "UserID");
        static List<string> teachQueries = new List<string>();
        static int teachTracker = 0;

        static Table adminsTable = new Table("Admin", "UserID");
        readonly static int ADMINS = 5;
        static int adminsCreated = 0;
        static string[] adminQueries = new string[ADMINS];

        static Table accountsTable = new Table("Account", "UserID", "Password", "accountType");
        static int accountsCreated = 0;
        static string[] accountQueries = new string[STUDENTS + LECTURERS + ADMINS];

        static FirstInsertFlags firstInsertFlags = new FirstInsertFlags();

        static void Main(string[] args)
        {
            Console.WriteLine("Generating SQL Queries...");
            CreateQueries();
            Console.WriteLine("Generated SQL Queries");

            Console.WriteLine("Printing SQL Queries...");
            Print(accountQueries);
            Print(studentQueries);
            Print(lecturerQueries);
            Print(adminQueries);
            Print(courseQueries);
            Print(assignedQueries);
            Print(teachQueries);
            Print(assignmentQueries);
            Print(submissionQueries);
            Print(gradeQueries);
            Print(sectionQueries);
            Print(sectionItemQueries);
            Print(forumQueries);
            Print(threadQueries);
            Console.WriteLine("Complete");

            // start creating the sql file

            Console.WriteLine("Creating new SQL file...");
            Console.Write("filename: ");
            string fileName = (Console.ReadLine() ?? "sqlfile") + ".sql";

            Console.WriteLine("Creating file...");
            CreateSQLFile(fileName);
            Console.WriteLine($"File created: {fileName}");

            // start writing to the sql file

            Console.WriteLine("Saving queries to file...");

            string accountInserts = Table.flattenInsertQueries(accountQueries);
            WriteQueriesToSqlFile(fileName, accountsTable, accountInserts);

            string studentInserts = Table.flattenInsertQueries(studentQueries);
            WriteQueriesToSqlFile(fileName, studentsTable, studentInserts);

            string lecturerInserts = Table.flattenInsertQueries(lecturerQueries);
            WriteQueriesToSqlFile(fileName, lecturersTable, lecturerInserts);

            string adminInserts = Table.flattenInsertQueries(adminQueries);
            WriteQueriesToSqlFile(fileName, adminsTable, adminInserts);

            string courseInserts = Table.flattenInsertQueries(courseQueries);
            WriteQueriesToSqlFile(fileName, coursesTable, courseInserts);

            string assignedInserts = Table.flattenInsertQueries(assignedQueries.ToArray());
            WriteQueriesToSqlFile(fileName, assignedTable, assignedInserts);

            string teachInserts = Table.flattenInsertQueries(teachQueries.ToArray());
            WriteQueriesToSqlFile(fileName, teachTable, teachInserts);

            string assignmentInserts = Table.flattenInsertQueries(assignmentQueries.ToArray());
            WriteQueriesToSqlFile(fileName, assignmentsTable, assignmentInserts);

            string submissionInserts = Table.flattenInsertQueries(submissionQueries.ToArray());
            WriteQueriesToSqlFile(fileName, submissionTable, submissionInserts);

            string gradeInserts = Table.flattenInsertQueries(gradeQueries.ToArray());
            WriteQueriesToSqlFile(fileName, gradeTable, gradeInserts);

            string sectionInserts = Table.flattenInsertQueries(sectionQueries.ToArray());
            WriteQueriesToSqlFile(fileName, sectionsTable, sectionInserts);

            string sectionItemInserts = Table.flattenInsertQueries(sectionItemQueries.ToArray());
            WriteQueriesToSqlFile(fileName, sectionItemsTable, sectionItemInserts);

            string forumInserts = Table.flattenInsertQueries(forumQueries.ToArray());
            WriteQueriesToSqlFile(fileName, forumTable, forumInserts);

            // do not flatten thread isnerts
            WriteQueriesToSqlFile(fileName, threadTable, threadQueries.ToArray());

            string eventInserts = Table.flattenInsertQueries(eventQueries.ToArray());
            WriteQueriesToSqlFile(fileName, eventsTable, eventInserts);

            Console.WriteLine("Queries saved");
        }

        private static void CreateQueries()
        {
            for (int i = 0; i < ADMINS; i++)
            {
                CreateAdmin();
            }

            for (int i = 0; i < LECTURERS; i++)
            {
                CreateLecturer();
            }

            for (int i = 0; i < COURSES; i++)
            {
                CreateCourse();
            }

            for (int i = 0; i < STUDENTS; i++)
            {
                CreateStudent();
            }
        }

        private static void CreateAdmin()
        {
            int adminId = CreateAccount("admin");

            if (adminsCreated < 1)
                adminQueries[adminsCreated] = adminsTable.generateInsertQuery(adminId.ToString());
            else
                adminQueries[adminsCreated] = adminsTable.generateInsertValues(adminId.ToString());

            adminsCreated++;
        }

        private static void CreateStudent()
        {
            // No student can do more than 6 courses
            // A student must be enrolled in at least 3 courses.

            int studentId = CreateAccount("student");
            string first = Helper.GenerateFirstName();
            string last = Helper.GenerateLastName();

            if (studentsCreated < 1)
            {
                studentQueries[studentsCreated] = studentsTable.generateInsertQuery(studentId.ToString(), first, last);
            }
            else
            {
                studentQueries[studentsCreated] = studentsTable.generateInsertValues(studentId.ToString(), first, last);
            }

            studentsCreated++;

            // assign student to a 3-6 number of courses
            int courseAmount = rand.Next(minCoursePerStudent, maxCoursePerStudent+1);

            if (currentAssignments < MINASSIGNMENTS)
            {
                for (int i = 0; i < courseAmount; i++)
                {
                    if (assignedTracker > COURSES - 1)
                    {
                        assignedTracker = 0;
                        currentAssignments++;
                    }

                    int courseId = assignedTracker + 1;
                    AssignStudentToCourse(courseId, studentId);
                    assignedTracker++;

                    if (rand.Next(0, 5) < 2)
                    {
                        SubmitAssignment(studentId, courseId);
                    }
                }
            }
            else
            {
                var randomCourses = Helper.GetRandomUniqueItems(availableCourses, courseAmount);

                for (int i = 0; i < randomCourses.Length; i++)
                {
                    int courseId = randomCourses[i];
                    AssignStudentToCourse(courseId, studentId);

                    if (rand.Next(0, 5) < 2)
                    {
                        SubmitAssignment(studentId, courseId);
                    }
                }
            }
        }

        private static int CreateAccount(string accountType)
        {
            int accountId = accountsCreated + 1;

            if (accountsCreated < 1)
                accountQueries[accountsCreated] = accountsTable.generateInsertQuery(accountId.ToString(), Helper.GeneratePassword(), accountType);
            else
                accountQueries[accountsCreated] = accountsTable.generateInsertValues(accountId.ToString(), Helper.GeneratePassword(), accountType);

            accountsCreated++;
            return accountId;
        }

        private static void CreateCourse()
        {
            int courseId = coursesCreated + 1;
            int maxEnrolment;

            if (coursesCreated < 1)
                maxEnrolment = 100000;
            else
                maxEnrolment = rand.Next(10) < 2 ? rand.Next(LIMCOURSEMIN, LIMCOURSEMAX + 1) : 100000;

            courseEnrolments[courseId] = (maxEnrolment, 0);
            courseNames[coursesCreated] = Helper.GenerateCourseName(courseNames);
            
            if (coursesCreated < 1)
                courseQueries[coursesCreated] = coursesTable.generateInsertQuery(courseId.ToString(), courseNames[coursesCreated]);
            else
                courseQueries[coursesCreated] = coursesTable.generateInsertValues(courseId.ToString(), courseNames[coursesCreated]);

            coursesCreated++;
            availableCourses.Add(courseId);

            if (teachTracker > LECTURERS - 1)
                teachTracker = 0;

            AssignLecturerToCourse(courseId, lecturerIds[teachTracker]);
            teachTracker++;

            CreateAssignment(courseId);

            string[] sections = Helper.GenerateSectionNames(MINSECTIONS, MAXSECTIONS);

            foreach (var sectionName in sections)
            {
                CreateSection(courseId, sectionName);
            }

            int forums = rand.Next(MINFORUMS, MAXFORUMS + 1);

            for (int i = 0; i < forums; i++)
            {
                CreateForum(courseId);
            }

            int events = rand.Next(EVENTSMIN, EVENTSMAX + 1);

            for (int i = 0; i < events; i++)
            {
                CreateEvent(courseId);
            }
        }

        private static void CreateLecturer()
        {
            int lecturerId = CreateAccount("lecturer");

            if (lecturersCreated < 1)
                lecturerQueries[lecturersCreated] = lecturersTable.generateInsertQuery(lecturerId.ToString(), Helper.GenerateFirstName(), Helper.GenerateLastName());
            else
                lecturerQueries[lecturersCreated] = lecturersTable.generateInsertValues(lecturerId.ToString(), Helper.GenerateFirstName(), Helper.GenerateLastName());

            lecturerIds[lecturersCreated] = lecturerId;
            lecturersCreated++;
        }

        private static void AssignStudentToCourse(int CourseId, int UserId)
        {
            if (!firstInsertFlags.Student)
            {
                assignedQueries.Add(assignedTable.generateInsertQuery(CourseId.ToString(), UserId.ToString()));
                firstInsertFlags.Student = true;
            }
            else
                assignedQueries.Add(assignedTable.generateInsertValues(CourseId.ToString(), UserId.ToString()));

            var enrolment = courseEnrolments[CourseId];
            courseEnrolments[CourseId] = (enrolment.maxStudents, enrolment.currentStudents+1);

            if (courseEnrolments[CourseId].currentStudents >= enrolment.maxStudents)
                availableCourses.Remove(CourseId);
        }

        private static void AssignLecturerToCourse(int CourseId, int UserId)
        {
            if (!firstInsertFlags.Lecturer)
            {
                teachQueries.Add(teachTable.generateInsertQuery(CourseId.ToString(), UserId.ToString()));
                firstInsertFlags.Lecturer = true;
            }
            else
                teachQueries.Add(teachTable.generateInsertValues(CourseId.ToString(), UserId.ToString()));
        }

        private static void CreateAssignment(int CourseId)
        {
            int assignmentId = assignmentsCreated + 1;
            string title = Helper.GenerateAssignmentTitle();
            string dateString = Helper.DateFromToday(1, 21);

            if (assignmentsCreated < 1)
            {
                assignmentQueries[assignmentsCreated] = assignmentsTable.generateInsertQuery(assignmentId.ToString(),
                CourseId.ToString(), title, dateString);
            }
            else
            {
                assignmentQueries[assignmentsCreated] = assignmentsTable.generateInsertValues(assignmentId.ToString(),
                CourseId.ToString(), title, dateString);
            }

            assignmentsCreated++;
        }

        private static void SubmitAssignment(int UserId, int AssignmentId)
        {
            int submissionId = submissionsMade + 1;
            string submissionDate = Helper.DateFromToday(11, 25);

            if (submissionsMade < 1)
            {
                submissionQueries.Add(submissionTable.generateInsertQuery(submissionId.ToString(), UserId.ToString(), 
                AssignmentId.ToString(), submissionDate));
            }
            else
            {
                submissionQueries.Add(submissionTable.generateInsertValues(submissionId.ToString(), UserId.ToString(), 
                AssignmentId.ToString(), submissionDate));
            }

            CreateGrade(submissionId);

            submissionsMade++;
        }

        private static void CreateGrade(int SubmissionId)
        {
            int grade = Helper.GenerateRandomNumber(101);

            if (!firstInsertFlags.Grades)
            {
                firstInsertFlags.Grades = true;
                gradeQueries.Add(gradeTable.generateInsertQuery(SubmissionId.ToString(), grade.ToString()));
            }
            else
            {
                gradeQueries.Add(gradeTable.generateInsertValues(SubmissionId.ToString(), grade.ToString()));
            }
        }

        private static void CreateSection(int CourseId, string sectionName)
        {
            int sectionId = sectionsCreated + 1;

            if (sectionsCreated < 1)
            {
                sectionQueries.Add(sectionsTable.generateInsertQuery(sectionId.ToString(), 
                CourseId.ToString(), sectionName));
            }
            else
            {
                sectionQueries.Add(sectionsTable.generateInsertValues(sectionId.ToString(), 
                CourseId.ToString(), sectionName));
            }

            sectionsCreated++;

            var sectionItems = Helper.GenerateSectionItems();

            foreach (var item in sectionItems)
            {
                AddItemToSection(sectionId, item.item, item.fileType);
            }
        }

        private static void AddItemToSection(int SectionId, string sectionItem, string fileType)
        {
            int sectionItemId = sectionItemsCreated + 1;
            
            if (sectionItemsCreated < 1)
            {
                sectionItemQueries.Add(sectionItemsTable.generateInsertQuery(sectionItemId.ToString(),
                SectionId.ToString(), sectionItem, fileType));
            }
            else
            {
                sectionItemQueries.Add(sectionItemsTable.generateInsertValues(sectionItemId.ToString(),
                SectionId.ToString(), sectionItem, fileType));
            }

            sectionItemsCreated++;
        }

        private static void CreateForum(int CourseId)
        {
            int forumId = forumsCreated + 1;
            var dTitle = Helper.GenerateForumTitle();
            var dQuestion = Helper.GenerateForumQuestion();

            if (forumsCreated < 1)
            {
                forumQueries.Add(forumTable.generateInsertQuery(forumId.ToString(),
                CourseId.ToString(), dTitle, dQuestion));
            }
            else
            {
                forumQueries.Add(forumTable.generateInsertValues(forumId.ToString(),
                CourseId.ToString(), dTitle, dQuestion));
            }

            forumsCreated++;

            // for each forum, we create a random amount of threads

            int threads = rand.Next(MINTHREADS, MAXTHREADS + 1);

            for (int i = 0; i < threads; i++)
            {
                var userId = rand.Next(ADMINS + LECTURERS + 1, STUDENTS);
                AddThread(forumId, userId);
            }
        }

        private static void AddThread(int ForumId, int UserId, string ParentThreadId = "-empty-", int nest = 0)
        {
            int threadId = threadsCreated + 1;
            string message = Helper.GenerateThreadMessage();

            string[] queryValues = {threadId.ToString(),
                ForumId.ToString(), UserId.ToString(), message, ParentThreadId};

            if (threadsCreated < 1)
                threadQueries.Add(threadTable.generateInsertQuery(queryValues));
            else
                threadQueries.Add(threadTable.generateInsertQuery(queryValues));

            threadsCreated++;

            if (nest < 2)
            {
                if (rand.Next(3) < 1)
                {
                    AddThread(ForumId, rand.Next(500, 12000), threadId.ToString(), nest + 1);
                }
            }
        }

        private static void CreateEvent(int CourseId)
        {
            int eventId = eventsCreated + 1;
            string eventTitle = Helper.GenerateEventTitle();
            string dueDate = Helper.DateFromToday(10, 30);

            string[] queryValues = {eventId.ToString(), CourseId.ToString(), eventTitle, dueDate};

            if (eventsCreated < 1)
                eventQueries.Add(eventsTable.generateInsertQuery(queryValues));
            else
                eventQueries.Add(eventsTable.generateInsertValues(queryValues));

            eventsCreated++;
        }

        private static void Print(string[] items)
        {
            foreach (var item in items)
            {
                Console.WriteLine(item);
            }
        }

        private static void Print(List<string> items)
        {
            foreach (var item in items)
            {
                Console.WriteLine(item);
            }
        }

        private static void Print(string item)
        {
            Console.WriteLine(item);
        }
    
        private static void CreateSQLFile (string fileName)
        {
            string sqlFileName = fileName;
            var stream = File.Create(sqlFileName);
            stream.Close();
        }

        private static bool WriteQueriesToSqlFile(string fileName, Table table, params string[] queries)
        {
            if (!File.Exists(fileName))
            {
                Console.WriteLine("Cannot find SQL File.");
                return false;
            }

            try
            {
                StringBuilder sb = new StringBuilder();

                string lineSeparator = new string('-', 60);
                string headerComment = $"--  {table.Name} TABLE Insert Queries";

                sb.AppendLine(Environment.NewLine + lineSeparator);
                sb.AppendLine(headerComment);
                sb.AppendLine(lineSeparator);
                sb.AppendLine();

                foreach (var query in queries)
                {
                    sb.AppendLine(query);
                }

                sb.AppendLine();
                sb.AppendLine(lineSeparator);

                using (StreamWriter sw = new StreamWriter(fileName, true))
                {
                    sw.Write(sb.ToString());
                }

                Console.WriteLine($"Saved {table.Name} queries to file");
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"An error occurred while trying to save the queries for the {table.Name} TABLE.\n{ex.Message}");
                return false;
            }
        }

    }

    class Table
    {
        private string name, insertQuery;
        private string[] fields;

        public string Name
        {
            get { return name; }
        }

        public Table(string tableName, params string[] fields)
        {
            this.name = tableName;
            this.fields = fields;

            string columns = "`" + string.Join("`, `", fields) + '`';
            string values = string.Join("?, ", fields) + "?";

            this.insertQuery = $"INSERT INTO `{tableName}` ({columns}) VALUES ({values});";
        }

        public string generateInsertQuery(params string[] values)
        {
            var columns = new List<string>();
            var formattedValues = new List<string>();

            for (int i = 0; i < values.Length; i++)
            {
                if (values[i] != "-empty-")
                {
                    columns.Add($"`{fields[i]}`");
                    formattedValues.Add($"'{values[i]}'");
                }
            }

            string columnsJoined = string.Join(", ", columns);
            string valuesJoined = string.Join(", ", formattedValues);

            return $"INSERT INTO `{name}` ({columnsJoined}) VALUES ({valuesJoined});";
        }

        public string generateInsertValues(params string[] values)
        {
            var formattedValues = new List<string>();

            for (int i = 0; i < values.Length; i++)
            {
                if (values[i] != "-empty-")
                {
                    formattedValues.Add($"'{values[i]}'");
                }
            }

            return $"({string.Join(", ", formattedValues)})";
        }

        public static string flattenInsertQueries(string[] queries)
        {
            if (queries == null || queries.Length == 0)
                return string.Empty;

            string header = queries[0].Trim().TrimEnd(';');

            List<string> values = new List<string>();

            int valuesIndex = header.IndexOf("VALUES", StringComparison.OrdinalIgnoreCase);

            if (valuesIndex == -1)
                throw new FormatException("First query does not contain a VALUES clause.");

            string firstValue = header.Substring(valuesIndex + "VALUES".Length).Trim();
            string baseInsert = header.Substring(0, valuesIndex + "VALUES".Length).Trim();

            values.Add(firstValue);

            for (int i = 1; i < queries.Length; i++)
            {
                values.Add(queries[i].Trim().TrimEnd(';'));
            }

            // join them into one SQL statement
            return $"{baseInsert} {string.Join(",\n", values)};";
        }

    }

    class Helper
    {
        private static Random rand = new Random();

        public static string GenerateFirstName()
        {
            string consonants = "BCDFGHJKLMNPQRSTVWXYZ".ToLower();
            string vowels = "AEIOU".ToLower();

            int length = rand.Next(4, 8);
            char[] name = new char[length];

            for (int i = 0; i < length; i++)
            {
                if (i % 2 == 0)
                    name[i] = consonants[rand.Next(consonants.Length)];
                else
                    name[i] = vowels[rand.Next(vowels.Length)];
            }

            name[0] = char.ToUpper(name[0]);

            return new string(name);
        }

        public static string GenerateLastName()
        {
            string[] prefixes = { "Ander", "Robin", "Hender", "John", "Carl", "Thomp", "Eric", "Steven", "Morr", "Wil" };
            string[] middleParts = { "der", "ing", "berg", "ford", "stone", "sen", "ham", "don", "rick", "man" };
            string[] suffixes = { "son", "man", "berg", "field", "ham", "well", "ton", "worth" };

            string prefix = prefixes[rand.Next(prefixes.Length)];
            string middle = middleParts[rand.Next(middleParts.Length)];
            string suffix = suffixes[rand.Next(suffixes.Length)];

            return prefix + middle + suffix;
        }

        public static string GenerateCourseName(string[] existingCourses)
        {
            string[] levels = { "Beginner", "Intermediate", "Advanced", "Expert", "Professional" };

            string[] descriptors = 
            {
                "Fundamentals", "Introduction", "Advanced Concepts", "Applications",
                "Principles", "Techniques", "Theory", "Methods", "Strategies",
                "Analysis", "Development", "Essentials", "Perspectives"
            };

            string[] adjectives = { "Modern", "Theoretical", "Digital", "Global", "Practical" };

            string[] subjects =
            {
                "Computer Science", "Mathematics", "Physics", "Biology", "Chemistry",
                "Business", "Psychology", "Economics", "History", "Sociology",
                "Engineering", "Philosophy", "Political Science", "Statistics",
                "Environmental Science", "Marketing", "Finance", "Linguistics",
                "Data Science", "Cybersecurity"
            };

            string newCourse;

            do
            {
                string level = levels[rand.Next(levels.Length)];
                string descriptor = descriptors[rand.Next(descriptors.Length)];
                string adjective = adjectives[rand.Next(adjectives.Length)];
                string subject = subjects[rand.Next(subjects.Length)];
                newCourse = $"{level} {descriptor} of {adjective} {subject}";
            }
            while (existingCourses.Contains(newCourse)); 

            return newCourse;
        }

        public static string GenerateCourseCode(string[] existingCodes)
        {
            string letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
            string newCode;

            do
            {
                char[] code = new char[8];

                for (int i = 0; i < 4; i++)
                {
                    code[i] = letters[rand.Next(letters.Length)];
                }

                code[4] = (char)('1' + rand.Next(3));

                for (int i = 5; i < 8; i++)
                {
                    code[i] = (char)('0' + rand.Next(10));
                }

                newCode = new string(code);
            }
            while (existingCodes.Contains(newCode));

            return newCode;
        }

        public static T[] GetRandomUniqueItems<T>(IList<T> inputList, int count = 5)
        {
            if (inputList.Count < count)
                throw new ArgumentException("List must contain at least " + count + " elements.");

            // Create a list of indices
            List<int> indices = Enumerable.Range(0, inputList.Count).ToList();

            // Shuffle the indices
            for (int i = indices.Count - 1; i > 0; i--)
            {
                int j = rand.Next(i + 1);
                (indices[i], indices[j]) = (indices[j], indices[i]);
            }

            // Use the first 'count' shuffled indices to get unique items
            T[] selected = new T[count];
            for (int i = 0; i < count; i++)
            {
                selected[i] = inputList[indices[i]];
            }

            return selected;
        }

        public static string GeneratePassword(int length = 5)
        {
            const string upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
            const string lower = "abcdefghijklmnopqrstuvwxyz";
            const string digits = "0123456789";
            string allChars = upper + lower + digits;

            char[] password = new char[length];

            for (int i = 0; i < length; i++)
            {
                password[i] = allChars[rand.Next(allChars.Length)];
            }

            return new string(password);
        }

        public static int GenerateRandomNumber(int maxExclusive)
        {
            return rand.Next(maxExclusive);
        }

        public static string DateFromToday(int min, int max)
        {
            DateTime date = DateTime.Now.Add(TimeSpan.FromDays(rand.Next(min, max)));
            string dateString = date.ToString("yyyy-MM-dd");

            return dateString;
        }

        public static string[] GenerateSectionNames(int min, int max)
        {
            int num = rand.Next(min, max + 1);
            var sectionNames = new string[num];

            for (int i = 0; i < sectionNames.Length; i++)
            {
                sectionNames[i] = $"Topic {(char)('A' + i)}";
            }

            return sectionNames;
        }

        public static (string item, string fileType)[] GenerateSectionItems()
        {
            var fileGroups = new List<(string item, string fileType)>
            {
                ("Chapter Notes PDF", "Files"),
                ("Lab Instructions", "Files"),
                ("Reading Material", "Files"),
                ("Syllabus Document", "Files"),
                ("Lecture Recording Link", "Links"),
                ("Reference Website", "Links"),
                ("Assignment Upload Portal", "Links"),
                ("Supplementary Video", "Links"),
                ("Lecture Slides – Week 1", "Slides"),
                ("Exam Review Slides", "Slides"),
                ("Topic Summary Slides", "Slides")
            };

            Shuffle(fileGroups.ToArray());

            int amount = GenerateRandomNumber(fileGroups.Count) + 1;
            return fileGroups.Take(amount).ToArray();
        }


        public static void Shuffle<T>(T[] array)
        {
            for (int i = array.Length - 1; i > 0; i--)
            {
                int j = rand.Next(i + 1); // 0 <= j <= i
                (array[i], array[j]) = (array[j], array[i]); // swap
            }
        }

        public static string GenerateForumTitle()
        {
            string[] starters = {
                "Let's Talk About",
                "Understanding",
                "The Future of",
                "Challenges in",
                "Insights on",
                "Exploring",
                "The Importance of",
                "Is There a Need for",
                "Debating",
                "How Do We Approach"
            };

            string[] topics = {
                "Digital Privacy",
                "Online Learning",
                "Artificial Intelligence",
                "Sustainable Development",
                "Cybersecurity",
                "Mental Health in Education",
                "Open Source Software",
                "Social Media Influence",
                "Climate Change Solutions",
                "Virtual Reality in Classrooms"
            };

            string start = starters[rand.Next(starters.Length)];
            string topic = topics[rand.Next(topics.Length)];

            return $"{start} {topic}";
        }


        public static string GenerateForumQuestion()
        {
            string[] openers = {
                "What are your thoughts on",
                "How can we address",
                "Do you agree with the idea that",
                "In what ways can we improve",
                "Should we be concerned about",
                "How is the current approach to",
                "What role does society play in",
                "Is technology helping or hurting",
                "How do you see the future of",
                "Why is it important to consider"
            };

            string[] topics = {
                "online privacy?",
                "AI replacing human jobs?",
                "mental health in academic settings?",
                "the rise of remote learning?",
                "climate responsibility in tech companies?",
                "social media's effect on communication?",
                "open access to educational content?",
                "data security in mobile apps?",
                "renewable energy in schools?",
                "cyberbullying on youth development?"
            };

            string opener = openers[rand.Next(openers.Length)];
            string topic = topics[rand.Next(topics.Length)];

            return $"{opener} {topic}";
        }


        public static string GenerateThreadMessage()
        {
            string[] messages = {
                "I completely agree with the original post.",
                "That's an interesting point — I hadn't considered it from that angle.",
                "Can someone clarify what was meant by this?",
                "I think it really depends on the context.",
                "Great insight! Here's what I found in a related article...",
                "I respectfully disagree — here's why.",
                "Has anyone experienced this personally?",
                "Let’s break this down step by step.",
                "This reminds me of a case we studied last semester.",
                "Could we explore this idea from a global perspective?"
            };

            return messages[rand.Next(messages.Length)];
        }


        public static string GenerateEventTitle()
        {
            string[] types = {
                "Assignment Due",
                "Project Presentation",
                "Midterm Exam",
                "Group Meeting",
                "Submission Deadline",
                "Final Review",
                "Lab Report Due",
                "Guest Lecture",
                "Class Debate",
                "Quiz Day"
            };

            string[] topics = {
                "on AI Ethics",
                "for Module 3",
                "on Data Structures",
                "– Literature Review",
                "for Chemistry Lab",
                "– Final Project",
                "on Marketing Strategy",
                "in Cybersecurity",
                "on Climate Policy",
                "for Week 5 Content"
            };

            string type = types[rand.Next(types.Length)];
            string topic = topics[rand.Next(topics.Length)];

            return $"{type} {topic}";
        }


        public static string GenerateAssignmentTitle()
        {
            string[] types = {
                "Research Paper",
                "Final Report",
                "Design Project",
                "Data Analysis",
                "Case Study",
                "Coding Assignment",
                "Presentation Slides",
                "Lab Submission",
                "Reflective Essay",
                "Exam Preparation Sheet"
            };

            return types[rand.Next(types.Length)];
        }

    }

    class FirstInsertFlags
    {
        public bool Lecturer { get; set; } = false;
        public bool Student { get; set; } = false;
        public bool Grades { get; set; } = false;
    }
}
