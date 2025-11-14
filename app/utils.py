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
    "html": f"<p>Class code(s): {', '.join(classCodes)}<br>Don't forget to enroll in all coclasses!</p>"})

    print(f"Email sent to {email} for {department} {courseNumber}")

def test_email(message):
    r = resend.Emails.send({
    "from": "noreply@uciclasswatcher.com",
    "to": "uciclasswatcher@gmail.com",
    "subject": "test email",
    "html": "<p>Email was sent to student</p>"})

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
                SELECT email FROM users
                WHERE course_number = %s AND department = %s;
            """, (courseNumber, department))

            rows = cursor.fetchall()
            emails = [row[0] for row in rows]

            for email in emails:
                send_email(classCodes, department, courseNumber, email)
                time.sleep(1)

            cursor.execute("""
                DELETE FROM users
                WHERE course_number = %s AND department = %s;
            """, (courseNumber, department))

    conn.commit()
    cursor.close()
    conn.close()

def get_watched_department():
    """ Returns a dictionary mapping departments to a list of watched course numbers """
    department_courses = {}

    conn = get_db_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT department, course_number FROM users;""")
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

def contact_message(message):
    load_dotenv()
    resend.api_key = os.getenv("RESEND_API")

    r = resend.Emails.send({
    "from": "noreply@uciclasswatcher.com",
    "to": "uciclasswatcher@gmail.com",
    "subject": "Contact Form Message",
    "html": f"New message:<br><p>{message}</p>"})