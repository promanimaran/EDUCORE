-- ============================================================
-- EduCore - Sample Data
-- ============================================================
USE educore;

-- Admin (password seeded via seed_db.py)
INSERT INTO admin (name, email, password) VALUES
('Super Admin', 'admin@educore.edu', 'PLACEHOLDER');

-- Departments
INSERT INTO department (dept_name, code, hod, description) VALUES
('Computer Science',        'CS',  'Dr. Ramesh Kumar',  'Computer Science and Engineering'),
('Electronics',             'ECE', 'Dr. Priya Sharma',  'Electronics and Communication Engineering'),
('Mechanical Engineering',  'ME',  'Dr. Suresh Patel',  'Mechanical Engineering'),
('Civil Engineering',       'CE',  'Dr. Ananya Singh',  'Civil Engineering'),
('Business Administration', 'MBA', 'Dr. Venkat Rao',    'Business Administration');

-- Staff
INSERT INTO staff (name, email, password, phone, dept_id, designation, gender, joining_date, status) VALUES
('Dr. Ramesh Kumar',  'ramesh@educore.edu',  'PLACEHOLDER', '9876543210', 1, 'Professor',           'Male',   '2015-06-01', 'Active'),
('Dr. Priya Sharma',  'priya@educore.edu',   'PLACEHOLDER', '9876543211', 1, 'Associate Professor', 'Female', '2017-07-15', 'Active'),
('Mr. Suresh Patel',  'suresh@educore.edu',  'PLACEHOLDER', '9876543212', 2, 'Assistant Professor', 'Male',   '2019-08-01', 'Active'),
('Ms. Ananya Singh',  'ananya@educore.edu',  'PLACEHOLDER', '9876543213', 3, 'Lecturer',            'Female', '2020-01-10', 'Active'),
('Dr. Venkat Rao',    'venkat@educore.edu',  'PLACEHOLDER', '9876543214', 4, 'Professor',           'Male',   '2013-05-20', 'Active');

-- Students
INSERT INTO student (roll_no, name, email, password, phone, dept_id, year, gender, dob, address, admission_year, status) VALUES
('CS2021001',  'Aarav Mehta',    'aarav@student.edu',   'PLACEHOLDER', '9123456701', 1, 3, 'Male',   '2003-04-12', '12 MG Road, Chennai',     2021, 'Active'),
('CS2021002',  'Diya Nair',      'diya@student.edu',    'PLACEHOLDER', '9123456702', 1, 3, 'Female', '2003-08-22', '45 Anna Salai, Chennai',   2021, 'Active'),
('CS2021003',  'Rohan Gupta',    'rohan@student.edu',   'PLACEHOLDER', '9123456703', 1, 3, 'Male',   '2002-11-05', '78 T Nagar, Chennai',      2021, 'Active'),
('ECE2021001', 'Kavya Reddy',    'kavya@student.edu',   'PLACEHOLDER', '9123456704', 2, 3, 'Female', '2003-02-18', '23 Adyar, Chennai',        2021, 'Active'),
('ECE2021002', 'Arjun Pillai',   'arjun@student.edu',   'PLACEHOLDER', '9123456705', 2, 3, 'Male',   '2002-07-30', '56 Velachery, Chennai',    2021, 'Active'),
('ME2021001',  'Sneha Iyer',     'sneha@student.edu',   'PLACEHOLDER', '9123456706', 3, 3, 'Female', '2003-01-14', '90 Tambaram, Chennai',     2021, 'Active'),
('CE2022001',  'Kiran Joshi',    'kiran@student.edu',   'PLACEHOLDER', '9123456707', 4, 2, 'Male',   '2004-06-09', '11 Porur, Chennai',        2022, 'Active'),
('MBA2022001', 'Lakshmi Prasad', 'lakshmi@student.edu', 'PLACEHOLDER', '9123456708', 5, 2, 'Female', '2001-09-25', '34 Besant Nagar, Chennai', 2022, 'Active');

-- Courses
INSERT INTO course (course_name, code, dept_id, staff_id, credits, semester, description, status) VALUES
('Data Structures and Algorithms', 'CS301',  1, 1, 4, 3, 'Core DSA course',              'Active'),
('Database Management Systems',    'CS401',  1, 2, 4, 4, 'RDBMS and SQL',                'Active'),
('Operating Systems',              'CS302',  1, 1, 3, 3, 'OS design fundamentals',       'Active'),
('Digital Electronics',            'ECE201', 2, 3, 4, 2, 'Logic gates and circuits',     'Active'),
('Signals and Systems',            'ECE301', 2, 3, 3, 3, 'Signal processing',            'Active'),
('Engineering Mechanics',          'ME201',  3, 4, 4, 2, 'Statics and dynamics',         'Active'),
('Structural Analysis',            'CE301',  4, 5, 4, 3, 'Analysis of structures',       'Active'),
('Business Economics',             'MBA101', 5, 2, 3, 1, 'Micro and macroeconomics',     'Active');

-- Enrollment (M:N — Student ↔ Course)
INSERT INTO enrollment (student_id, course_id, enrolled_date, status) VALUES
(1,1,'2023-07-01','Enrolled'),(1,2,'2023-07-01','Enrolled'),(1,3,'2023-07-01','Enrolled'),
(2,1,'2023-07-01','Enrolled'),(2,2,'2023-07-01','Enrolled'),
(3,1,'2023-07-01','Enrolled'),(3,3,'2023-07-01','Enrolled'),
(4,4,'2023-07-01','Enrolled'),(4,5,'2023-07-01','Enrolled'),
(5,4,'2023-07-01','Enrolled'),(5,5,'2023-07-01','Enrolled'),
(6,6,'2023-07-01','Enrolled'),
(7,7,'2023-07-01','Enrolled'),
(8,8,'2023-07-01','Enrolled');

-- Marks
INSERT INTO marks (student_id, course_id, internal_marks, external_marks, grade, entered_by) VALUES
(1,1,38,55,'A',1),(1,2,35,60,'A+',2),(1,3,30,45,'B',1),
(2,1,40,58,'A+',1),(2,2,32,50,'B+',2),
(3,1,28,42,'B',1),(3,3,25,38,'C',1),
(4,4,36,54,'A',3),(4,5,33,49,'B+',3),
(5,4,39,57,'A+',3),(5,5,31,47,'B+',3),
(6,6,34,52,'A',4),
(7,7,37,56,'A',5),
(8,8,40,60,'A+',2);
