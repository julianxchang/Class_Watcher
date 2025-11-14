from dotenv import load_dotenv
import os, time, resend
from app.db import get_db_conn
import requests

def send_confirmation_email(email, courseNumber):
    load_dotenv()
    resend.api_key = os.getenv("RESEND_API")

    r = resend.Emails.send({
    "from": "noreply@uciclasswatcher.com",
    "to": email,
    "subject": f"Successfully started watching ICS {courseNumber}",
    "html": f"<p>You will be notified when a spot opens up!<br>Make sure to register as soon as you get the email as you won't be notified again for this course.<br><br>Best of luck!<br><br>- UCI Class Watcher</p>"})


def send_email(classCodes, courseNumber, email):
    load_dotenv()
    resend.api_key = os.getenv("RESEND_API")

    r = resend.Emails.send({
    "from": "noreply@uciclasswatcher.com",
    "to": email,
    "subject": f"SPOT OPEN IN ICS {courseNumber}!",
    "html": f"<p>Class code(s): {', '.join(classCodes)}<br>Don't forget to enroll in all coclasses!</p>"})

    print(f"Email sent to {email} for ")

def test_email(message):
    load_dotenv()
    resend.api_key = os.getenv("RESEND_API")


    r = resend.Emails.send({
    "from": "noreply@uciclasswatcher.com",
    "to": "uciclasswatcher@gmail.com",
    "subject": "test email",
    "html": "<p>Email was sent to student</p>"})

    print("Email sent to admin")

def notify_students(found: dict):
    conn = get_db_conn()
    cursor = conn.cursor()

    for courseNumber, classCodes in found.items():
        cursor.execute("""
            SELECT email FROM users
            WHERE course_number = %s;
        """, (courseNumber,))

        rows = cursor.fetchall()
        emails = [row[0] for row in rows]

        for email in emails:
            send_email(classCodes, courseNumber, email)
            time.sleep(1)

        # After notifying, remove users from watching this course
        cursor.execute("""
            DELETE FROM users
            WHERE course_number = %s;
        """, (courseNumber,))

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