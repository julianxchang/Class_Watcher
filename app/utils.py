def create_chrome_driver():
    from selenium import webdriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless') # Run Chrome in headless mode (commnet this line to see browser)
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def complete_email(email, courseNumber, duration):
    from email.message import EmailMessage
    import smtplib, ssl
    from dotenv import load_dotenv
    import os
    import time

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "uciclasswatcher@gmail.com"
    receiver_email = "uciclasswatcher@gmail.com"

    load_dotenv()
    password = os.getenv("EMAIL_PASSWORD")


    msg = EmailMessage()
    msg['Subject'] = f"{email} finished watching {courseNumber}"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(f"{email} finished watching ICS {courseNumber}.\nWatch duration: {duration} minute(s)")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server , port, context=context) as server:
        server.login(sender_email, password)
        server.send_message(msg)
        print("Email Sent")

def get_time(): # New York Timezone
    from datetime import datetime
    import pytz

    new_york_tz = pytz.timezone('America/New_York')
    current_time = datetime.now(new_york_tz).strftime('%Y-%m-%d %I:%M:%S %p')

    return current_time


def send_confirmation_email(email, courseNumber):
    from email.message import EmailMessage
    import smtplib, ssl
    from dotenv import load_dotenv
    import os

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "uciclasswatcher@gmail.com"
    receiver_email = email
    load_dotenv()
    password = os.getenv("EMAIL_PASSWORD")


    msg = EmailMessage()
    msg['Subject'] = f"Successfully started watching ICS {courseNumber}"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(f"""You will be notified when a spot opens up!\n
                    Make sure to register as soon as you get the email as you won't be notified again for this course.\n\n
                    Best of luck!\n\n
                    - UCI Class Watcher""")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.send_message(msg)


def send_email(classCodes, courseNumber, email):
    from email.message import EmailMessage
    import smtplib, ssl
    from dotenv import load_dotenv
    import os

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "uciclasswatcher@gmail.com"  # Enter your address
    receiver_email = email  # Enter receiver address

    load_dotenv()
    password = os.getenv("EMAIL_PASSWORD")


    msg = EmailMessage()
    msg['Subject'] = f"SPOT OPEN IN ICS {courseNumber}"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(f"SPOT OPEN IN ICS {courseNumber} AS OF {get_time()}\nClass code(s): {', '.join(classCodes)}\nDon't forget to enroll in all coclasses!")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.send_message(msg)
        print("Email Sent")

    test_email(f"Notified {email} for ICS {courseNumber} - Class Code(s): {', '.join(classCodes)}")

def test_email(message):
    from email.message import EmailMessage
    import smtplib, ssl
    from dotenv import load_dotenv
    import os
    import time

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "uciclasswatcher@gmail.com"
    receiver_email = "uciclasswatcher@gmail.com"

    load_dotenv()
    password = os.getenv("EMAIL_PASSWORD")


    msg = EmailMessage()
    msg['Subject'] = f"test email"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(f"{message}")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.send_message(msg)
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