from dotenv import load_dotenv
import os, time, resend
from app.db import get_db_conn
import requests

load_dotenv()
resend.api_key = os.getenv("RESEND_API")

def send_confirmation_email(email, department, courseNumber):
    r = resend.Emails.send({
    "from": "noreply@uciclasswatcher.com",
    "to": email,
    "subject": f"Successfully started watching {department} {courseNumber}",
    "html": f"<p>You will be notified when a spot opens up!<br>Make sure to register as soon as you get the email as you won't be notified again for this course.<br><br>Best of luck!<br><br>- UCI Class Watcher</p>"})
    print(f"Confirmation email sent to {email} for {department} {courseNumber}")

def send_email(classCodes, department, courseNumber, email):
    r = resend.Emails.send({
    "from": "noreply@uciclasswatcher.com",
    "to": email,
    "subject": f"SPOT OPEN IN {department} {courseNumber}!",
    "html": f"<p>Class code(s): {', '.join(classCodes)}<br>Enroll <a href='https://www.reg.uci.edu/cgi-bin/webreg-redirect.sh'>here</a><br><br>Don't forget to enroll in all coclasses!</p>"})

    print(f"Email sent to {email} for {department} {courseNumber}")

def test_email(message):
    r = resend.Emails.send({
    "from": "noreply@uciclasswatcher.com",
    "to": "uciclasswatcher@gmail.com",
    "subject": "test email",
    "html": f"<p>{message}</p>"})

    print("Email sent to admin")

def notify_students(found: dict):
    """found is a dictionary where key is department, value is another dictionary where key is course number and value is list of open class codes
    ex. f = {"ICS": {"31": ["12345", "67890"], "32": ["54321"]}, "Math": {"2A": ["11223"]}}
    """
    conn = get_db_conn()
    cursor = conn.cursor()

    for department, courses in found.items():
        for courseNumber, classCodes in courses.items():
            cursor.execute("""
                SELECT users.id, users.email, users.password_hash
                FROM watching
                JOIN users ON watching.user_id = users.id
                WHERE watching.department = %s AND watching.course_number = %s;
            """, (department, courseNumber))

            rows = cursor.fetchall()
            for row in rows:
                send_email(classCodes, department, courseNumber, row[1])
                time.sleep(1)

                # update notification table
                cursor.execute("""
                    INSERT INTO notifications_sent (email, department, course_number, class_codes)
                    VALUES (%s, %s, %s, %s);
                """, (row[1], department, courseNumber, ', '.join(classCodes)))

            cursor.execute("""
                DELETE FROM watching
                WHERE department = %s and course_number = %s;
            """, (department, courseNumber))


    conn.commit()
    cursor.close()
    conn.close()

def get_watched_department():
    """ Returns a dictionary mapping departments to a list of watched course numbers """
    department_courses = {}

    conn = get_db_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT department, course_number FROM watching;""")
    rows = cursor.fetchall()
    for department, course_number in rows:
        if department in department_courses:
            department_courses[department].append(course_number)
        else:
            department_courses[department] = [course_number]
    cursor.close()
    conn.close()
    return department_courses


def fetch_department(department, term="2026-03"):
    url = "https://www.reg.uci.edu/perl/WebSoc"
    payload = {
        "YearTerm": term,
        "ShowComments": "off",
        "Dept": department,
        "CourseNum": "",
        "Division": "ANY",
        "CourseCodes": "",
        "Submit": "Submit",
    }

    response = requests.post(url, data=payload)
    response.raise_for_status()
    html = response.text
    return html

def contact_message(email, message):
    load_dotenv()
    resend.api_key = os.getenv("RESEND_API")

    r = resend.Emails.send({
    "from": "noreply@uciclasswatcher.com",
    "to": "uciclasswatcher@gmail.com",
    "subject": "Contact Form Message",
    "html": f"<p>New message from {email}:<br><p>{message}</p>"})


def get_stats():
    """Returns statistics about the application"""
    conn = get_db_conn()
    cursor = conn.cursor()

    stats = {}

    # Total notifications sent
    cursor.execute("SELECT COUNT(*) FROM notifications_sent;")
    stats['total_notifications'] = cursor.fetchone()[0]

    # Currently watched classes
    cursor.execute("SELECT COUNT(*) FROM watching;")
    stats['current_watchers'] = cursor.fetchone()[0]

    # Most watched courses
    cursor.execute("""
        SELECT department, course_number, COUNT(*) as watch_count
        FROM watching
        GROUP BY department, course_number
        ORDER BY watch_count DESC
        LIMIT 5;
    """)
    stats['top_courses'] = cursor.fetchall()

    # Notifications sent today
    cursor.execute("""
        SELECT COUNT(*) FROM notifications_sent
        WHERE sent_at >= CURRENT_DATE;
    """)
    stats['notifications_today'] = cursor.fetchone()[0]

    # Notifications sent this week
    cursor.execute("""
        SELECT COUNT(*) FROM notifications_sent
        WHERE sent_at >= CURRENT_DATE - INTERVAL '7 days';
    """)
    stats['notifications_this_week'] = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return stats

def watching_one_class(email):
    """Returns True if the current user is watching only one class"""
    conn = get_db_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM watching w, users u
        WHERE w.user_id = u.id AND u.email = %s;
    """, (email,))

    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    return count >= 1

def add_to_watching(email, department, courseNumber) -> bool:
    """
    Adds a class to the user's watching list
    If user does not exist, create the user
    If user is already watching return False
    Returns True if successfully added
    """
    conn = get_db_conn()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (email, password_hash) 
        VALUES (%s, NULL) 
        ON CONFLICT (email) DO NOTHING
        RETURNING id;
    """, (email,))

    result = cursor.fetchone()
    if result:
        user_id = result[0]
    else:
        # User already exists, get their id
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO watching (user_id, department, course_number)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id, department, course_number) DO NOTHING;
    """, (user_id, department, courseNumber))

    # Check if the row was actually inserted
    if cursor.rowcount == 0:
        conn.rollback()
        return False
    conn.commit()
    return True
    cursor.close()
    conn.close()