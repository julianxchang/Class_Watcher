from flask import render_template, request
from app import app, limiter
from app.db import get_db_conn, release_db_conn
from app.utils import add_to_watching, contact_message, get_stats, add_to_watching, send_confirmation_email, get_dashboard_data, get_admin_data, watching_one_class_and_no_account
import re
from flask_login import current_user, login_required

VALID_DEPARTMENTS = set([
    "AC ENG", "AFAM", "ANATOMY", "ANESTH", "ANTHRO", "ARABIC", "ARMN", "ART",
    "ART HIS", "ARTS", "ARTSHUM", "ASIANAM", "ASL", "BANA", "BATS", "BIO SCI",
    "BIOCHEM", "BME", "CAMPREC", "CBE", "CEM", "CHC/LAT", "CHEM", "CHINESE",
    "CLASSIC", "CLT&THY", "COGS", "COM LIT", "COMPSCI", "CRITISM", "CRM/LAW",
    "CSE", "DANCE", "DATA", "DERM", "DEV BIO", "DRAMA", "EARTHSS", "EAS",
    "ECO EVO", "ECON", "ECPS", "ED AFF", "EDUC", "EECS", "EHS", "ENGLISH",
    "ENGR", "ENGRCEE", "ENGRMAE", "EPIDEM", "ER MED", "EURO ST", "FAM MED",
    "FILIPNO", "FIN", "FLM&MDA", "FRENCH", "GDIM", "GEN&SEX", "GERMAN",
    "GLBL ME", "GLBLCLT", "GREEK", "HEBREW", "HINDI", "HISTORY", "HUMAN",
    "HUMARTS", "I&C SCI", "IN4MATX", "INNO", "INT MED", "INTL ST", "IRAN",
    "ITALIAN", "JAPANSE", "KOREAN", "LATIN", "LAW", "LIT JRN", "LPS", "LSCI",
    "M&MG", "MATH", "MED", "MED ED", "MED HUM", "MGMT", "MGMT EP", "MGMT FE",
    "MGMT HC", "MGMTMBA", "MGMTPHD", "MIC BIO", "MNGE", "MOL BIO", "MPAC",
    "MSE", "MUSIC", "NET SYS", "NEURBIO", "NEUROL", "NUR DNP", "NUR FNP",
    "NUR INF", "NUR SCI", "OB/GYN", "OPHTHAL", "PATH", "PED GEN", "PEDS",
    "PERSIAN", "PHARM", "PHILOS", "PHMD", "PHRMSCI", "PHY SCI", "PHYSICS",
    "PHYSIO", "PLASTIC", "PM&R", "POL SCI", "PORTUG", "PSCI", "PSMD",
    "PUB POL", "PUBHLTH", "RADIO", "REL STD", "ROTC", "RUSSIAN", "SOC SCI",
    "SOCECOL", "SOCIOL", "SPANISH", "SPPS", "STATS", "SURGERY", "SWE",
    "TAGALOG", "TOX", "UCDC", "UNI AFF", "UNI STU", "UPPP", "VIETMSE",
    "VIS STD", "WRITING"
])


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_watch', methods=['GET', 'POST'])
def add_watch():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        department = request.form.get('department')
        courseNumber = request.form.get('course_number').upper()

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return render_template('index.html', error="Invalid email address")

        if department not in VALID_DEPARTMENTS:
            return render_template('index.html', error="Invalid department")

        # if user is not signed up, they can only watch one class
        if watching_one_class_and_no_account(email):
            return render_template('index.html', error="Sign up to watch more than 1 class!")

        if(not add_to_watching(email, department, courseNumber)):
            return render_template('index.html', error="You are already watching this class!")

        print(f"{email} clicked submit with {department} {courseNumber}")

        send_confirmation_email(email, department, courseNumber)

        print(f"{email} started watching {department} {courseNumber}")
        return render_template('landingpage.html', department=department, courseNumber=courseNumber)

    return render_template('index.html')

@app.route('/remove_watch', methods=['POST'])
@login_required
def remove_watch():
    department = request.form.get('department')
    courseNumber = request.form.get('course_number')
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM watching
        WHERE user_id = (SELECT id FROM users WHERE email = %s)
        AND department = %s
        AND course_number = %s
    """, (current_user.email, department, courseNumber))
    conn.commit()
    cur.close()
    release_db_conn(conn)

    data = get_dashboard_data(current_user.email)
    return render_template('dashboard.html', watched_classes=data['watched_classes'], stats=data['stats'], notification_history=data['notification_history'])

@app.route('/send_email', methods=['POST'])
def send_email():
    if request.method == 'POST':
        if request.form.get("phone"):
            return "bot detected", 400
        email = request.form.get('email').lower()
        message = request.form.get('message')
        contact_message(email, message)
        return render_template('sent.html')

@app.route('/changelog')
def changelog():
    return render_template('changelog.html')

@app.route('/contact')
@limiter.limit("5 per hour")
def contact():
    return render_template('contact.html')

@app.route('/sent')
def sent():
    return render_template('sent.html')

@app.route('/stats')
def stats():
    stats_data = get_stats()
    return render_template('stats.html', stats=stats_data)

@app.route('/dashboard')
@login_required
def dashboard():
    email = current_user.email
    if email == "uciclasswatcher@gmail.com":
        admin_data = get_admin_data(email)
        return render_template('admin_dashboard.html', admin_data=admin_data)
    data = get_dashboard_data(email)
    return render_template('dashboard.html', watched_classes=data['watched_classes'], stats=data['stats'], notification_history=data['notification_history'])