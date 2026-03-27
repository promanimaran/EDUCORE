"""
seed_db.py — Seeds hashed passwords into EduCore database.
Run AFTER schema.sql and sample_data.sql have been imported.
Usage: python seed_db.py
"""
import mysql.connector
from werkzeug.security import generate_password_hash

DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': '1234',        # ← Change to your MySQL password
    'port':     3306,
    'database': 'educore'
}

def seed():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur  = conn.cursor()

    admin_pass   = generate_password_hash('admin123')
    staff_pass   = generate_password_hash('password123')
    student_pass = generate_password_hash('password123')

    cur.execute("UPDATE admin   SET password=%s", (admin_pass,))
    cur.execute("UPDATE staff   SET password=%s", (staff_pass,))
    cur.execute("UPDATE student SET password=%s", (student_pass,))

    conn.commit()
    cur.close()
    conn.close()

    print("\n✅ EduCore database seeded successfully!")
    print("─" * 45)
    print("  Admin   → admin@educore.edu   / admin123")
    print("  Staff   → ramesh@educore.edu  / password123")
    print("  Student → aarav@student.edu   / password123")
    print("─" * 45)

if __name__ == '__main__':
    seed()
