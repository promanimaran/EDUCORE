-- ============================================================
-- EduCore College Management System
-- Database Schema - ER Diagram Based
-- Relationships:
--   Department (1) → (N) Student
--   Department (1) → (N) Staff
--   Staff     (1) → (N) Course
--   Student   (M) ↔ (N) Course  via enrollment
--   Student   (1) → (N) Marks
-- ============================================================

CREATE DATABASE IF NOT EXISTS educore CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE educore;

-- ── Admin ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS admin (
    admin_id   INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(150) UNIQUE NOT NULL,
    password   VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Department ───────────────────────────────────────────────
-- 1 Department → N Students
-- 1 Department → N Staff
-- 1 Department → N Courses
CREATE TABLE IF NOT EXISTS department (
    dept_id   INT AUTO_INCREMENT PRIMARY KEY,
    dept_name VARCHAR(150) NOT NULL,
    code      VARCHAR(20)  UNIQUE NOT NULL,
    hod       VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Staff ────────────────────────────────────────────────────
-- N Staff → 1 Department  (dept_id FK)
CREATE TABLE IF NOT EXISTS staff (
    staff_id     INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    email        VARCHAR(150) UNIQUE NOT NULL,
    password     VARCHAR(255) NOT NULL,
    phone        VARCHAR(20),
    dept_id      INT,
    designation  VARCHAR(100),
    gender       ENUM('Male','Female','Other') DEFAULT 'Male',
    joining_date DATE,
    status       ENUM('Active','Inactive') DEFAULT 'Active',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES department(dept_id) ON DELETE SET NULL
);

-- ── Student ──────────────────────────────────────────────────
-- N Students → 1 Department  (dept_id FK)
CREATE TABLE IF NOT EXISTS student (
    student_id     INT AUTO_INCREMENT PRIMARY KEY,
    roll_no        VARCHAR(20) UNIQUE NOT NULL,
    name           VARCHAR(100) NOT NULL,
    email          VARCHAR(150) UNIQUE NOT NULL,
    password       VARCHAR(255) NOT NULL,
    phone          VARCHAR(20),
    dept_id        INT,
    year           INT DEFAULT 1,
    gender         ENUM('Male','Female','Other') DEFAULT 'Male',
    dob            DATE,
    address        TEXT,
    admission_year YEAR,
    status         ENUM('Active','Inactive','Graduated') DEFAULT 'Active',
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES department(dept_id) ON DELETE SET NULL
);

-- ── Course ───────────────────────────────────────────────────
-- N Courses → 1 Department  (dept_id FK)
-- N Courses → 1 Staff       (staff_id FK)
CREATE TABLE IF NOT EXISTS course (
    course_id   INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(150) NOT NULL,
    code        VARCHAR(20)  UNIQUE NOT NULL,
    dept_id     INT,
    staff_id    INT,
    credits     INT  DEFAULT 3,
    semester    INT  DEFAULT 1,
    description TEXT,
    status      ENUM('Active','Inactive') DEFAULT 'Active',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id)  REFERENCES department(dept_id) ON DELETE SET NULL,
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id)     ON DELETE SET NULL
);

-- ── Enrollment ───────────────────────────────────────────────
-- M Students ↔ N Courses  (M:N via enrollment)
CREATE TABLE IF NOT EXISTS enrollment (
    enroll_id     INT AUTO_INCREMENT PRIMARY KEY,
    student_id    INT NOT NULL,
    course_id     INT NOT NULL,
    enrolled_date DATE DEFAULT (CURRENT_DATE),
    status        ENUM('Enrolled','Completed','Dropped') DEFAULT 'Enrolled',
    UNIQUE KEY uq_enrollment (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id)  REFERENCES course(course_id)   ON DELETE CASCADE
);

-- ── Marks ────────────────────────────────────────────────────
-- 1 Student → N Marks
-- Marks also linked to Course
CREATE TABLE IF NOT EXISTS marks (
    mark_id        INT AUTO_INCREMENT PRIMARY KEY,
    student_id     INT NOT NULL,
    course_id      INT NOT NULL,
    internal_marks DECIMAL(5,2) DEFAULT 0,
    external_marks DECIMAL(5,2) DEFAULT 0,
    total_marks    DECIMAL(5,2) GENERATED ALWAYS AS (internal_marks + external_marks) STORED,
    grade          VARCHAR(5),
    remarks        TEXT,
    entered_by     INT,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_marks (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id)  REFERENCES course(course_id)   ON DELETE CASCADE,
    FOREIGN KEY (entered_by) REFERENCES staff(staff_id)     ON DELETE SET NULL
);
