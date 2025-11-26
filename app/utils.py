from dotenv import load_dotenv
import os, time, sib_api_v3_sdk
from app.db import get_db_conn, release_db_conn
import requests

load_dotenv()
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.getenv("BREVO_API")
betterstack_key = os.getenv("BETTERSTACK_API")
heartbeat_api_url = os.getenv("HEARTBEAT_API_URL")
HEARTBEAT_URL = os.getenv("HEARTBEAT_URL")
api = sib_api_v3_sdk.TransactionalEmailsApi(
    sib_api_v3_sdk.ApiClient(configuration)
)
SYSTEM_STATUS_CACHE = {
    "data": None,
    "last_update": 0
}

def send_confirmation_email(email, department, courseNumber):
    mail = sib_api_v3_sdk.SendSmtpEmail(
    sender={"email": "alerts@uciclasswatcher.com", "name": "UCI Class Watcher"},
    to=[{"email": email}],
    subject=f"Successfully started watching {department} {courseNumber}",
    html_content=f"<p>You will be notified when a spot opens up!<br>Make sure to register as soon as you get the email as you won't be notified again for this course.<br><br>Best of luck!<br><br>- UCI Class Watcher</p>",
    )

    api.send_transac_email(mail)

    print(f"Confirmation email sent to {email} for {department} {courseNumber}")

def send_email(classCodes, department, courseNumber, email):
    mail = sib_api_v3_sdk.SendSmtpEmail(
    sender={"email": "alerts@uciclasswatcher.com", "name": "UCI Class Watcher"},
    to=[{"email": email}],
    subject=f"SPOT OPEN IN {department} {courseNumber}!",
    html_content=f"<p>Class code(s): {', '.join(classCodes)}<br>Enroll <a href='https://www.reg.uci.edu/cgi-bin/webreg-redirect.sh'>here</a><br><br>Don't forget to enroll in all coclasses!</p>",
    )

    api.send_transac_email(mail)

    print(f"Email sent to {email} for {department} {courseNumber}")

def contact_message(email, message):
    mail = sib_api_v3_sdk.SendSmtpEmail(
    sender={"email": "alerts@uciclasswatcher.com", "name": "UCI Class Watcher"},
    to=[{"email": "uciclasswatcher@gmail.com"}],
    subject=f"Contact Form Message",
    html_content=f"<p>New message from {email}:<br><p>{message}</p>",
    )

    api.send_transac_email(mail)

def notify_students(found: dict):
    """found is a dictionary where key is department, value is another dictionary where key is course number and value is list of open class codes
    ex. f = {"ICS": {"31": ["12345", "67890"], "32": ["54321"]}, "Math": {"2A": ["11223"]}}
    """
    conn = get_db_conn()
    cursor = conn.cursor()

    for department, courses in found.items():
        for courseNumber, classCodes in courses.items():
            # get the emails of students watching this course
            cursor.execute("""
                SELECT users.email
                FROM watching
                JOIN users ON watching.user_id = users.id
                WHERE watching.department = %s AND watching.course_number = %s;
            """, (department, courseNumber))

            rows = cursor.fetchall()
            for row in rows:
                send_email(classCodes, department, courseNumber, row[0])
                time.sleep(1)

                # update notification table with sent email
                cursor.execute("""
                    INSERT INTO notifications_sent (email, department, course_number, class_codes)
                    VALUES (%s, %s, %s, %s);
                """, (row[0], department, courseNumber, ', '.join(classCodes)))

            # remove all students watching this course
            cursor.execute("""
                DELETE FROM watching
                WHERE department = %s and course_number = %s;
            """, (department, courseNumber))


    conn.commit()
    cursor.close()
    release_db_conn(conn)

def get_watched_department():
    """ Returns a dictionary mapping departments to a set of watched course numbers """
    department_courses = {}

    conn = get_db_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT department, course_number FROM watching;""")
    rows = cursor.fetchall()
    for department, course_number in rows:
        if department in department_courses:
            department_courses[department].add(course_number)
        else:
            department_courses[department] = set([course_number])
    cursor.close()
    release_db_conn(conn)
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
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        html = response.text
        return html
    except requests.RequestException as e:
        print(f"Error fetching department {department}: {e}")
        return None

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
        LIMIT 10;
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
    release_db_conn(conn)

    return stats

def get_dashboard_data(email):
    """Get all dashboard data in a single database connection"""
    conn = get_db_conn()
    cursor = conn.cursor()

    dashboard_data = {
        'watched_classes': [],
        'stats': {},
        'notification_history': []
    }

    # Get watched courses
    cursor.execute("""
        SELECT w.department, w.course_number
        FROM watching w
        JOIN users u ON w.user_id = u.id
        WHERE u.email = %s;
    """, (email,))
    dashboard_data['watched_classes'] = cursor.fetchall()

    # Get user stats - Total notifications
    cursor.execute("""
        SELECT COUNT(*) FROM notifications_sent
        WHERE email = %s;
    """, (email,))
    dashboard_data['stats']['total_notifications'] = cursor.fetchone()[0]

    # Currently watching count
    dashboard_data['stats']['currently_watching'] = len(dashboard_data['watched_classes'])

    # Notifications this week
    cursor.execute("""
        SELECT COUNT(*) FROM notifications_sent
        WHERE email = %s
        AND sent_at >= CURRENT_DATE - INTERVAL '7 days';
    """, (email,))
    dashboard_data['stats']['notifications_this_week'] = cursor.fetchone()[0]

    # Notifications today
    cursor.execute("""
        SELECT COUNT(*) FROM notifications_sent
        WHERE email = %s
        AND sent_at >= CURRENT_DATE;
    """, (email,))
    dashboard_data['stats']['notifications_today'] = cursor.fetchone()[0]

    # Get notification history
    cursor.execute("""
        SELECT department, course_number, class_codes,
               sent_at AT TIME ZONE 'UTC' AT TIME ZONE 'America/Los_Angeles' AS sent_at_la
        FROM notifications_sent
        WHERE email = %s
        ORDER BY sent_at DESC
        LIMIT 10;
    """, (email,))

    for row in cursor.fetchall():
        dashboard_data['notification_history'].append({
            'department': row[0],
            'course_number': row[1],
            'class_codes': row[2],
            'sent_at': row[3]
        })

    cursor.close()
    release_db_conn(conn)

    return dashboard_data

def get_admin_data():
    """Get all admin dashboard data in a single database connection
    Data includes 10 recent notifications and recent entries into watching table"""
    conn = get_db_conn()
    cursor = conn.cursor()

    admin_data = {
        'recent_notifications': [],
        'recent_watching': []
    }

    cursor.execute("""
        SELECT email, department, course_number, class_codes,
               sent_at AT TIME ZONE 'UTC' AT TIME ZONE 'America/Los_Angeles' AS sent_at_la
        FROM notifications_sent
        ORDER BY sent_at DESC
        LIMIT 10;
    """)
    admin_data['recent_notifications'] = cursor.fetchall()

    cursor.execute("""
        SELECT users.email, watching.department, watching.course_number,
               watching.added_at AT TIME ZONE 'UTC' AT TIME ZONE 'America/Los_Angeles' AS added_la
        FROM watching
        JOIN users ON watching.user_id = users.id
        ORDER BY watching.added_at DESC
        LIMIT 10;
    """)
    admin_data['recent_watching'] = cursor.fetchall()

    cursor.close()
    release_db_conn(conn)
    return admin_data

def watching_one_class_and_no_account(email):
    """Returns True if the current user doesn't have an account and is already watching a class"""
    conn = get_db_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM watching w, users u
        WHERE w.user_id = u.id AND u.email = %s AND u.password_hash IS NULL;
    """, (email,))

    count = cursor.fetchone()[0]
    cursor.close()
    release_db_conn(conn)

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
        cursor.close()
        release_db_conn(conn)
        return False
    conn.commit()
    cursor.close()
    release_db_conn(conn)
    return True

def get_last_scrape():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT last_scrape AT TIME ZONE 'UTC' AT TIME ZONE 'America/Los_Angeles'
        FROM system_status
        WHERE id = 1;
    """)
    row = cur.fetchone()
    release_db_conn(conn)
    return row[0].strftime("%Y-%m-%d %I:%M %p") if row else None

def get_system_status():
    try:
        url = heartbeat_api_url
        headers = {"Authorization": f"Bearer {betterstack_key}"}
        data = requests.get(url, headers=headers, timeout=3).json()["data"]
        status = data["attributes"]["status"]

        if status == "up":
            emoji = "🟢"; msg = "All systems operational"
        elif status == "down":
            emoji = "🔴"; msg = "System outage"
        else:
            emoji = "🟡"; msg = "Monitor paused"

        return {
            "status": status,
            "emoji": emoji,
            "message": msg,
            "last_scrape": get_last_scrape() or "N/A"
        }
    except Exception as e:
        print("Failed to get system status:", e)
        return {
            "status": "unknown",
            "emoji": "🟡",
            "message": "Unable to retrieve system status",
            "last_scrape": get_last_scrape() or "N/A"
        }

def update_system_status():
    # send heartbeat
    try:
        requests.get(HEARTBEAT_URL, timeout=5)
        print("Heartbeat sent.")
    except Exception as e:
        print("Failed to send heartbeat:", e)

    # update last scraped time in db
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("UPDATE system_status SET last_scrape = NOW() WHERE id = 1;")
        conn.commit()
        release_db_conn(conn)
        print("Updated last scrape time in database.")
    except Exception as e:
        print("Failed to update last scrape time:", e)