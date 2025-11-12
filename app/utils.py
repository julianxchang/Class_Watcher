def create_chrome_driver():
    from selenium import webdriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless') # Run Chrome in headless mode (commnet this line to see browser)
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def send_confirmation_email(email, courseNumber):
    import resend
    from dotenv import load_dotenv
    import os

    load_dotenv()
    resend.api_key = os.getenv("RESEND_API")

    r = resend.Emails.send({
    "from": "noreply@uciclasswatcher.com",
    "to": email,
    "subject": f"Successfully started watching ICS {courseNumber}",
    "html": f"<p>You will be notified when a spot opens up!<br>Make sure to register as soon as you get the email as you won't be notified again for this course.<br><br>Best of luck!<br><br>- UCI Class Watcher</p>"})


def send_email(classCodes, courseNumber, email):
    import resend
    from dotenv import load_dotenv
    import os

    load_dotenv()
    resend.api_key = os.getenv("RESEND_API")

    r = resend.Emails.send({
    "from": "noreply@uciclasswatcher.com",
    "to": email,
    "subject": f"SPOT OPEN IN ICS {courseNumber}!",
    "html": f"<p>Class code(s): {', '.join(classCodes)}<br>Don't forget to enroll in all coclasses!</p>"})

    print("Email Sent")

    test_email(f"Notified {email} for ICS {courseNumber} - Class Code(s): {', '.join(classCodes)}")

def test_email(message):
    import resend
    from dotenv import load_dotenv
    import os

    load_dotenv()
    resend.api_key = os.getenv("RESEND_API")


    r = resend.Emails.send({
    "from": "noreply@uciclasswatcher.com",
    "to": "uciclasswatcher@gmail.com",
    "subject": "test email",
    "html": "<p>Congrats on sending your <strong>first email</strong>!</p>"})

    print("Email Sent")

def get_watched_courses():
    from app.db import get_db_conn
    conn = get_db_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT course_number FROM users;""")

    rows = cursor.fetchall()
    return [row[0] for row in rows]

def notify_students(found: dict):
    from app.db import get_db_conn
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

        # After notifying, remove users from watching this course
        cursor.execute("""
            DELETE FROM users
            WHERE course_number = %s;
        """, (courseNumber,))

    conn.commit()
    cursor.close()
    conn.close()