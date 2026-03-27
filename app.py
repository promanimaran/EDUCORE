"""
app.py — EduCore College Management System
Flask + MySQL | Fully ER-Diagram Based
ER: Department(1→N)Student, Department(1→N)Staff,
    Staff(1→N)Course, Student(M↔N)Course via Enrollment,
    Student(1→N)Marks
"""
from flask import (Flask, render_template, request,
                   redirect, url_for, session, flash, jsonify)
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from functools import wraps
from datetime import date
import os

app = Flask(__name__)
app.secret_key = 'educore_secret_2026'

# ── DB Config ────────────────────────────────────────────────
DB_CONFIG = {
    'host':       'localhost',
    'user':       'root',
    'password':   '1234',       # ← Change to your MySQL password
    'port':       3306,
    'database':   'educore',
    'autocommit': False
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def query(sql, params=None, fetchone=False,
          fetchall=False, commit=False):
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute(sql, params or ())
    result = None
    if fetchone:
        result = cur.fetchone()
    elif fetchall:
        result = cur.fetchall()
    if commit:
        conn.commit()
        result = cur.lastrowid
    cur.close()
    conn.close()
    return result

# ── Auth Decorator ───────────────────────────────────────────
def login_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session or session.get('role') != role:
                flash('Please log in to continue.', 'warning')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return wrapper
    return decorator

# ── Login / Logout ───────────────────────────────────────────
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for(f'{session["role"]}_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role     = request.form.get('role', '')
        table_map = {'admin': 'admin', 'staff': 'staff', 'student': 'student'}
        if role not in table_map:
            flash('Invalid role selected.', 'danger')
            return render_template('login.html')
        # Use correct PK column per table
        user = query(f"SELECT * FROM {table_map[role]} WHERE email=%s",
                     (email,), fetchone=True)
        if user and check_password_hash(user['password'], password):
            session['user_id']    = user[f'{role}_id'] if role != 'admin' else user['admin_id']
            session['user_name']  = user['name']
            session['user_email'] = user['email']
            session['role']       = role
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for(f'{role}_dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

# ═══════════════════════════════════════════════════════════
# ADMIN — Dashboard
# ═══════════════════════════════════════════════════════════
@app.route('/admin/dashboard')
@login_required('admin')
def admin_dashboard():
    stats = {
        'students':    query("SELECT COUNT(*) AS c FROM student  WHERE status='Active'",   fetchone=True)['c'],
        'staff':       query("SELECT COUNT(*) AS c FROM staff    WHERE status='Active'",   fetchone=True)['c'],
        'departments': query("SELECT COUNT(*) AS c FROM department",                       fetchone=True)['c'],
        'courses':     query("SELECT COUNT(*) AS c FROM course   WHERE status='Active'",   fetchone=True)['c'],
        'enrollments': query("SELECT COUNT(*) AS c FROM enrollment WHERE status='Enrolled'", fetchone=True)['c'],
    }
    recent_students = query(
        "SELECT s.roll_no, s.name, d.dept_name, s.created_at "
        "FROM student s LEFT JOIN department d ON s.dept_id=d.dept_id "
        "ORDER BY s.created_at DESC LIMIT 6", fetchall=True)
    dept_stats = query(
        "SELECT d.dept_name, COUNT(s.student_id) AS total "
        "FROM department d LEFT JOIN student s ON d.dept_id=s.dept_id "
        "GROUP BY d.dept_id ORDER BY total DESC", fetchall=True)
    return render_template('admin/dashboard.html',
                           stats=stats,
                           recent_students=recent_students,
                           dept_stats=dept_stats)

# ── Department CRUD ──────────────────────────────────────────
@app.route('/admin/departments')
@login_required('admin')
def admin_departments():
    depts = query(
        "SELECT d.*, "
        "COUNT(DISTINCT s.student_id) AS student_count, "
        "COUNT(DISTINCT st.staff_id)  AS staff_count "
        "FROM department d "
        "LEFT JOIN student s  ON d.dept_id=s.dept_id "
        "LEFT JOIN staff   st ON d.dept_id=st.dept_id "
        "GROUP BY d.dept_id ORDER BY d.dept_name", fetchall=True)
    return render_template('admin/departments.html', departments=depts)

@app.route('/admin/departments/add', methods=['GET', 'POST'])
@login_required('admin')
def admin_add_department():
    if request.method == 'POST':
        f = request.form
        try:
            query("INSERT INTO department (dept_name, code, hod, description) "
                  "VALUES (%s,%s,%s,%s)",
                  (f['dept_name'], f['code'],
                   f.get('hod',''), f.get('description','')), commit=True)
            flash('Department added successfully!', 'success')
            return redirect(url_for('admin_departments'))
        except mysql.connector.IntegrityError as e:
            flash(f'Error: {e.msg}', 'danger')
    return render_template('admin/department_form.html', dept=None, action='Add')

@app.route('/admin/departments/edit/<int:did>', methods=['GET', 'POST'])
@login_required('admin')
def admin_edit_department(did):
    dept = query("SELECT * FROM department WHERE dept_id=%s", (did,), fetchone=True)
    if not dept:
        flash('Department not found.', 'danger')
        return redirect(url_for('admin_departments'))
    if request.method == 'POST':
        f = request.form
        query("UPDATE department SET dept_name=%s, code=%s, hod=%s, description=%s "
              "WHERE dept_id=%s",
              (f['dept_name'], f['code'],
               f.get('hod',''), f.get('description',''), did), commit=True)
        flash('Department updated successfully!', 'success')
        return redirect(url_for('admin_departments'))
    return render_template('admin/department_form.html', dept=dept, action='Edit')

@app.route('/admin/departments/delete/<int:did>', methods=['POST'])
@login_required('admin')
def admin_delete_department(did):
    query("DELETE FROM department WHERE dept_id=%s", (did,), commit=True)
    flash('Department deleted.', 'success')
    return redirect(url_for('admin_departments'))

# ── Student CRUD ─────────────────────────────────────────────
@app.route('/admin/students')
@login_required('admin')
def admin_students():
    students = query(
        "SELECT s.*, d.dept_name FROM student s "
        "LEFT JOIN department d ON s.dept_id=d.dept_id "
        "ORDER BY s.created_at DESC", fetchall=True)
    return render_template('admin/students.html', students=students)

@app.route('/admin/students/add', methods=['GET', 'POST'])
@login_required('admin')
def admin_add_student():
    depts = query("SELECT dept_id, dept_name FROM department ORDER BY dept_name", fetchall=True)
    if request.method == 'POST':
        f = request.form
        try:
            query(
                "INSERT INTO student (roll_no, name, email, password, phone, "
                "dept_id, year, gender, dob, address, admission_year, status) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (f['roll_no'], f['name'], f['email'],
                 generate_password_hash(f['password']),
                 f.get('phone',''),
                 f.get('dept_id') or None,
                 f.get('year', 1),
                 f.get('gender','Male'),
                 f.get('dob') or None,
                 f.get('address',''),
                 f.get('admission_year') or None,
                 f.get('status','Active')), commit=True)
            flash('Student added successfully!', 'success')
            return redirect(url_for('admin_students'))
        except mysql.connector.IntegrityError as e:
            flash(f'Error: {e.msg}', 'danger')
    return render_template('admin/student_form.html',
                           departments=depts, student=None, action='Add')

@app.route('/admin/students/edit/<int:sid>', methods=['GET', 'POST'])
@login_required('admin')
def admin_edit_student(sid):
    student = query("SELECT * FROM student WHERE student_id=%s", (sid,), fetchone=True)
    depts   = query("SELECT dept_id, dept_name FROM department ORDER BY dept_name", fetchall=True)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('admin_students'))
    if request.method == 'POST':
        f = request.form
        pwd_sql, pwd_val = ("", [])
        if f.get('password'):
            pwd_sql = ", password=%s"
            pwd_val = [generate_password_hash(f['password'])]
        params = [f['name'], f['email'], f.get('phone',''),
                  f.get('dept_id') or None, f.get('year', 1),
                  f.get('gender','Male'), f.get('dob') or None,
                  f.get('address',''), f.get('admission_year') or None,
                  f.get('status','Active')] + pwd_val + [sid]
        query(f"UPDATE student SET name=%s, email=%s, phone=%s, dept_id=%s, "
              f"year=%s, gender=%s, dob=%s, address=%s, admission_year=%s, "
              f"status=%s{pwd_sql} WHERE student_id=%s", params, commit=True)
        flash('Student updated successfully!', 'success')
        return redirect(url_for('admin_students'))
    return render_template('admin/student_form.html',
                           departments=depts, student=student, action='Edit')

@app.route('/admin/students/delete/<int:sid>', methods=['POST'])
@login_required('admin')
def admin_delete_student(sid):
    query("DELETE FROM student WHERE student_id=%s", (sid,), commit=True)
    flash('Student deleted.', 'success')
    return redirect(url_for('admin_students'))

@app.route('/admin/students/view/<int:sid>')
@login_required('admin')
def admin_view_student(sid):
    student = query(
        "SELECT s.*, d.dept_name FROM student s "
        "LEFT JOIN department d ON s.dept_id=d.dept_id "
        "WHERE s.student_id=%s", (sid,), fetchone=True)
    enrollments = query(
        "SELECT c.course_name, c.code, e.status, e.enrolled_date "
        "FROM enrollment e JOIN course c ON e.course_id=c.course_id "
        "WHERE e.student_id=%s", (sid,), fetchall=True)
    marks = query(
        "SELECT c.course_name, c.code, m.internal_marks, "
        "m.external_marks, m.total_marks, m.grade "
        "FROM marks m JOIN course c ON m.course_id=c.course_id "
        "WHERE m.student_id=%s ORDER BY c.semester", (sid,), fetchall=True)
    return render_template('admin/student_view.html',
                           student=student,
                           enrollments=enrollments,
                           marks=marks)

# ── Staff CRUD ───────────────────────────────────────────────
@app.route('/admin/staff')
@login_required('admin')
def admin_staff():
    staff = query(
        "SELECT s.*, d.dept_name FROM staff s "
        "LEFT JOIN department d ON s.dept_id=d.dept_id "
        "ORDER BY s.created_at DESC", fetchall=True)
    return render_template('admin/staff.html', staff=staff)

@app.route('/admin/staff/add', methods=['GET', 'POST'])
@login_required('admin')
def admin_add_staff():
    depts = query("SELECT dept_id, dept_name FROM department ORDER BY dept_name", fetchall=True)
    if request.method == 'POST':
        f = request.form
        try:
            query(
                "INSERT INTO staff (name, email, password, phone, dept_id, "
                "designation, gender, joining_date, status) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (f['name'], f['email'],
                 generate_password_hash(f['password']),
                 f.get('phone',''),
                 f.get('dept_id') or None,
                 f.get('designation',''),
                 f.get('gender','Male'),
                 f.get('joining_date') or None,
                 f.get('status','Active')), commit=True)
            flash('Staff added successfully!', 'success')
            return redirect(url_for('admin_staff'))
        except mysql.connector.IntegrityError as e:
            flash(f'Error: {e.msg}', 'danger')
    return render_template('admin/staff_form.html',
                           departments=depts, staff=None, action='Add')

@app.route('/admin/staff/edit/<int:sid>', methods=['GET', 'POST'])
@login_required('admin')
def admin_edit_staff(sid):
    staff_member = query("SELECT * FROM staff WHERE staff_id=%s", (sid,), fetchone=True)
    depts = query("SELECT dept_id, dept_name FROM department ORDER BY dept_name", fetchall=True)
    if not staff_member:
        flash('Staff not found.', 'danger')
        return redirect(url_for('admin_staff'))
    if request.method == 'POST':
        f = request.form
        pwd_sql, pwd_val = ("", [])
        if f.get('password'):
            pwd_sql = ", password=%s"
            pwd_val = [generate_password_hash(f['password'])]
        params = [f['name'], f['email'], f.get('phone',''),
                  f.get('dept_id') or None, f.get('designation',''),
                  f.get('gender','Male'), f.get('joining_date') or None,
                  f.get('status','Active')] + pwd_val + [sid]
        query(f"UPDATE staff SET name=%s, email=%s, phone=%s, dept_id=%s, "
              f"designation=%s, gender=%s, joining_date=%s, status=%s{pwd_sql} "
              f"WHERE staff_id=%s", params, commit=True)
        flash('Staff updated successfully!', 'success')
        return redirect(url_for('admin_staff'))
    return render_template('admin/staff_form.html',
                           departments=depts, staff=staff_member, action='Edit')

@app.route('/admin/staff/delete/<int:sid>', methods=['POST'])
@login_required('admin')
def admin_delete_staff(sid):
    query("DELETE FROM staff WHERE staff_id=%s", (sid,), commit=True)
    flash('Staff deleted.', 'success')
    return redirect(url_for('admin_staff'))

# ── Course CRUD ──────────────────────────────────────────────
@app.route('/admin/courses')
@login_required('admin')
def admin_courses():
    courses = query(
        "SELECT c.*, d.dept_name, s.name AS staff_name "
        "FROM course c "
        "LEFT JOIN department d ON c.dept_id=d.dept_id "
        "LEFT JOIN staff s ON c.staff_id=s.staff_id "
        "ORDER BY c.created_at DESC", fetchall=True)
    return render_template('admin/courses.html', courses=courses)

@app.route('/admin/courses/add', methods=['GET', 'POST'])
@login_required('admin')
def admin_add_course():
    depts      = query("SELECT dept_id, dept_name FROM department ORDER BY dept_name", fetchall=True)
    staff_list = query("SELECT staff_id, name FROM staff WHERE status='Active' ORDER BY name", fetchall=True)
    if request.method == 'POST':
        f = request.form
        try:
            query(
                "INSERT INTO course (course_name, code, dept_id, staff_id, "
                "credits, semester, description, status) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (f['course_name'], f['code'],
                 f.get('dept_id') or None,
                 f.get('staff_id') or None,
                 f.get('credits', 3), f.get('semester', 1),
                 f.get('description',''), f.get('status','Active')), commit=True)
            flash('Course added!', 'success')
            return redirect(url_for('admin_courses'))
        except mysql.connector.IntegrityError as e:
            flash(f'Error: {e.msg}', 'danger')
    return render_template('admin/course_form.html',
                           departments=depts, staff_list=staff_list,
                           course=None, action='Add')

@app.route('/admin/courses/edit/<int:cid>', methods=['GET', 'POST'])
@login_required('admin')
def admin_edit_course(cid):
    course     = query("SELECT * FROM course WHERE course_id=%s", (cid,), fetchone=True)
    depts      = query("SELECT dept_id, dept_name FROM department ORDER BY dept_name", fetchall=True)
    staff_list = query("SELECT staff_id, name FROM staff WHERE status='Active' ORDER BY name", fetchall=True)
    if not course:
        flash('Course not found.', 'danger')
        return redirect(url_for('admin_courses'))
    if request.method == 'POST':
        f = request.form
        query("UPDATE course SET course_name=%s, code=%s, dept_id=%s, staff_id=%s, "
              "credits=%s, semester=%s, description=%s, status=%s "
              "WHERE course_id=%s",
              (f['course_name'], f['code'],
               f.get('dept_id') or None,
               f.get('staff_id') or None,
               f.get('credits', 3), f.get('semester', 1),
               f.get('description',''), f.get('status','Active'), cid), commit=True)
        flash('Course updated!', 'success')
        return redirect(url_for('admin_courses'))
    return render_template('admin/course_form.html',
                           departments=depts, staff_list=staff_list,
                           course=course, action='Edit')

@app.route('/admin/courses/delete/<int:cid>', methods=['POST'])
@login_required('admin')
def admin_delete_course(cid):
    query("DELETE FROM course WHERE course_id=%s", (cid,), commit=True)
    flash('Course deleted.', 'success')
    return redirect(url_for('admin_courses'))

# ── Enrollment Management ────────────────────────────────────
@app.route('/admin/enrollment')
@login_required('admin')
def admin_enrollment():
    enrollments = query(
        "SELECT e.enroll_id, s.name AS student_name, s.roll_no, "
        "c.course_name, c.code, d.dept_name, e.status, e.enrolled_date "
        "FROM enrollment e "
        "JOIN student    s ON e.student_id=s.student_id "
        "JOIN course     c ON e.course_id=c.course_id "
        "LEFT JOIN department d ON c.dept_id=d.dept_id "
        "ORDER BY e.enrolled_date DESC", fetchall=True)
    return render_template('admin/enrollment.html', enrollments=enrollments)

@app.route('/admin/enrollment/add', methods=['GET', 'POST'])
@login_required('admin')
def admin_add_enrollment():
    students = query("SELECT student_id, roll_no, name FROM student WHERE status='Active' ORDER BY name", fetchall=True)
    courses  = query("SELECT course_id, course_name, code FROM course WHERE status='Active' ORDER BY course_name", fetchall=True)
    if request.method == 'POST':
        f = request.form
        try:
            query("INSERT INTO enrollment (student_id, course_id, status) VALUES (%s,%s,%s)",
                  (f['student_id'], f['course_id'], f.get('status','Enrolled')), commit=True)
            flash('Student enrolled successfully!', 'success')
            return redirect(url_for('admin_enrollment'))
        except mysql.connector.IntegrityError:
            flash('Student already enrolled in this course!', 'danger')
    return render_template('admin/enrollment_form.html',
                           students=students, courses=courses)

@app.route('/admin/enrollment/delete/<int:eid>', methods=['POST'])
@login_required('admin')
def admin_delete_enrollment(eid):
    query("DELETE FROM enrollment WHERE enroll_id=%s", (eid,), commit=True)
    flash('Enrollment removed.', 'success')
    return redirect(url_for('admin_enrollment'))

# ── Reports ──────────────────────────────────────────────────
@app.route('/admin/reports')
@login_required('admin')
def admin_reports():
    students = query("SELECT student_id, roll_no, name FROM student ORDER BY name", fetchall=True)
    return render_template('admin/reports.html', students=students)

@app.route('/admin/reports/student/<int:sid>')
@login_required('admin')
def admin_student_report(sid):
    return _student_report(sid, 'admin/student_report.html')

# ═══════════════════════════════════════════════════════════
# STAFF ROUTES
# ═══════════════════════════════════════════════════════════
@app.route('/staff/dashboard')
@login_required('staff')
def staff_dashboard():
    sid     = session['user_id']
    courses = query(
        "SELECT c.*, COUNT(e.enroll_id) AS enrolled "
        "FROM course c LEFT JOIN enrollment e ON c.course_id=e.course_id "
        "WHERE c.staff_id=%s GROUP BY c.course_id", (sid,), fetchall=True)
    pending = query(
        "SELECT COUNT(*) AS c FROM enrollment e "
        "JOIN course c ON e.course_id=c.course_id "
        "WHERE c.staff_id=%s "
        "AND e.student_id NOT IN "
        "(SELECT student_id FROM marks WHERE course_id=c.course_id)",
        (sid,), fetchone=True)['c']
    staff = query(
        "SELECT s.*, d.dept_name FROM staff s "
        "LEFT JOIN department d ON s.dept_id=d.dept_id "
        "WHERE s.staff_id=%s", (sid,), fetchone=True)
    return render_template('staff/dashboard.html',
                           courses=courses,
                           pending_marks=pending,
                           staff=staff)

@app.route('/staff/marks')
@login_required('staff')
def staff_marks():
    courses = query(
        "SELECT * FROM course WHERE staff_id=%s AND status='Active' ORDER BY course_name",
        (session['user_id'],), fetchall=True)
    return render_template('staff/marks.html', courses=courses)

@app.route('/staff/marks/entry/<int:course_id>')
@login_required('staff')
def staff_marks_entry(course_id):
    sid    = session['user_id']
    course = query("SELECT * FROM course WHERE course_id=%s AND staff_id=%s",
                   (course_id, sid), fetchone=True)
    if not course:
        flash('Access denied.', 'danger')
        return redirect(url_for('staff_marks'))
    students = query(
        "SELECT s.student_id, s.name, s.roll_no, "
        "COALESCE(m.internal_marks,0) AS internal_marks, "
        "COALESCE(m.external_marks,0) AS external_marks, "
        "COALESCE(m.grade,'')        AS grade, "
        "COALESCE(m.remarks,'')      AS remarks "
        "FROM enrollment e "
        "JOIN student s ON e.student_id=s.student_id "
        "LEFT JOIN marks m ON m.student_id=s.student_id AND m.course_id=%s "
        "WHERE e.course_id=%s ORDER BY s.name",
        (course_id, course_id), fetchall=True)
    return render_template('staff/marks_entry.html',
                           course=course, students=students)

@app.route('/staff/marks/save', methods=['POST'])
@login_required('staff')
def staff_save_marks():
    sid         = session['user_id']
    course_id   = int(request.form['course_id'])
    student_ids = request.form.getlist('student_ids')
    for stid in student_ids:
        internal = float(request.form.get(f'internal_{stid}', 0) or 0)
        external = float(request.form.get(f'external_{stid}', 0) or 0)
        grade    = request.form.get(f'grade_{stid}', '')
        remarks  = request.form.get(f'remarks_{stid}', '')
        query(
            "INSERT INTO marks (student_id, course_id, internal_marks, "
            "external_marks, grade, remarks, entered_by) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s) "
            "ON DUPLICATE KEY UPDATE internal_marks=%s, external_marks=%s, "
            "grade=%s, remarks=%s, entered_by=%s",
            (int(stid), course_id, internal, external, grade, remarks, sid,
             internal, external, grade, remarks, sid), commit=True)
    flash('Marks saved successfully!', 'success')
    return redirect(url_for('staff_marks_entry', course_id=course_id))

@app.route('/staff/students')
@login_required('staff')
def staff_students():
    sid = session['user_id']
    students = query(
        "SELECT DISTINCT s.*, d.dept_name "
        "FROM student s "
        "JOIN enrollment e ON s.student_id=e.student_id "
        "JOIN course c ON e.course_id=c.course_id "
        "LEFT JOIN department d ON s.dept_id=d.dept_id "
        "WHERE c.staff_id=%s ORDER BY s.name", (sid,), fetchall=True)
    return render_template('staff/students.html', students=students)

@app.route('/staff/profile')
@login_required('staff')
def staff_profile():
    staff = query(
        "SELECT s.*, d.dept_name FROM staff s "
        "LEFT JOIN department d ON s.dept_id=d.dept_id "
        "WHERE s.staff_id=%s", (session['user_id'],), fetchone=True)
    return render_template('staff/profile.html', staff=staff)

# ═══════════════════════════════════════════════════════════
# STUDENT ROUTES
# ═══════════════════════════════════════════════════════════
@app.route('/student/dashboard')
@login_required('student')
def student_dashboard():
    sid     = session['user_id']
    student = query(
        "SELECT s.*, d.dept_name FROM student s "
        "LEFT JOIN department d ON s.dept_id=d.dept_id "
        "WHERE s.student_id=%s", (sid,), fetchone=True)
    enrollments = query(
        "SELECT c.course_name, c.code, e.status "
        "FROM enrollment e JOIN course c ON e.course_id=c.course_id "
        "WHERE e.student_id=%s", (sid,), fetchall=True)
    marks = query(
        "SELECT c.course_name, c.code, m.internal_marks, "
        "m.external_marks, m.total_marks, m.grade "
        "FROM marks m JOIN course c ON m.course_id=c.course_id "
        "WHERE m.student_id=%s", (sid,), fetchall=True)
    return render_template('student/dashboard.html',
                           student=student,
                           enrollments=enrollments,
                           marks=marks)

@app.route('/student/courses')
@login_required('student')
def student_courses():
    courses = query(
        "SELECT c.*, d.dept_name, s.name AS staff_name, e.status AS enroll_status "
        "FROM enrollment e "
        "JOIN course c ON e.course_id=c.course_id "
        "LEFT JOIN department d ON c.dept_id=d.dept_id "
        "LEFT JOIN staff s ON c.staff_id=s.staff_id "
        "WHERE e.student_id=%s ORDER BY c.course_name",
        (session['user_id'],), fetchall=True)
    return render_template('student/courses.html', courses=courses)

@app.route('/student/marks')
@login_required('student')
def student_marks():
    marks = query(
        "SELECT c.course_name AS course, c.code, c.credits, c.semester, "
        "m.internal_marks, m.external_marks, m.total_marks, m.grade, m.remarks "
        "FROM marks m JOIN course c ON m.course_id=c.course_id "
        "WHERE m.student_id=%s ORDER BY c.semester, c.course_name",
        (session['user_id'],), fetchall=True)
    return render_template('student/marks.html', marks=marks)

@app.route('/student/profile')
@login_required('student')
def student_profile():
    student = query(
        "SELECT s.*, d.dept_name FROM student s "
        "LEFT JOIN department d ON s.dept_id=d.dept_id "
        "WHERE s.student_id=%s", (session['user_id'],), fetchone=True)
    return render_template('student/profile.html', student=student)

@app.route('/student/report')
@login_required('student')
def student_report():
    return _student_report(session['user_id'], 'student/report.html')

# ── Shared Report Helper ─────────────────────────────────────
def _student_report(student_id, template):
    student = query(
        "SELECT s.*, d.dept_name FROM student s "
        "LEFT JOIN department d ON s.dept_id=d.dept_id "
        "WHERE s.student_id=%s", (student_id,), fetchone=True)
    marks = query(
        "SELECT c.course_name AS course, c.code, c.credits, c.semester, "
        "m.internal_marks, m.external_marks, m.total_marks, m.grade "
        "FROM marks m JOIN course c ON m.course_id=c.course_id "
        "WHERE m.student_id=%s ORDER BY c.semester, c.course_name",
        (student_id,), fetchall=True)
    total_credits   = sum(r['credits'] for r in marks if r['grade'] not in ('F', None, ''))
    total_marks_sum = sum(float(r['total_marks'] or 0) for r in marks)
    avg_marks       = round(total_marks_sum / len(marks), 2) if marks else 0
    return render_template(template,
                           student=student, marks=marks,
                           total_credits=total_credits,
                           avg_marks=avg_marks,
                           today=date.today().strftime('%d %B %Y'))

# ── API Helpers ──────────────────────────────────────────────
@app.route('/api/staff_by_dept/<int:dept_id>')
def api_staff_by_dept(dept_id):
    staff = query("SELECT staff_id, name FROM staff "
                  "WHERE dept_id=%s AND status='Active'",
                  (dept_id,), fetchall=True)
    return jsonify(staff)

# ── Error Handlers ───────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found.'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error.'), 500

if __name__ == '__main__':
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"\n{'─'*45}")
    print(f"  EduCore College Management System")
    print(f"{'─'*45}")
    print(f"  Local URL   → http://127.0.0.1:5000")
    print(f"  Network URL → http://{local_ip}:5000")
    print(f"{'─'*45}\n")
    app.run(debug=True, host='0.0.0.0', port=5000)