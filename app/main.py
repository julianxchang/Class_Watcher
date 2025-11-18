from flask import render_template, request
from app import app, limiter
from app.db import get_db_conn
from app.utils import add_to_watching, send_confirmation_email, contact_message, get_stats, watching_one_class, add_to_watching
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

@app.route('/run', methods=['GET', 'POST'])
def run_code():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        department = request.form.get('department')
        courseNumber = request.form.get('course_number').upper()

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return render_template('index.html', error="Invalid email address")

        if department not in VALID_DEPARTMENTS:
            return render_template('index.html', error="Invalid department")

        # if user is not signed up, they can only watch one class
        if not current_user.is_authenticated and watching_one_class(email):
            return render_template('index.html', error="Sign up to watch more than 1 class!")

        if(not add_to_watching(email, department, courseNumber)):
            return render_template('index.html', error="You are already watching this class!")

        send_confirmation_email(email, department, courseNumber)

        print(f"{email} started watching {department} {courseNumber}")
        return render_template('landingpage.html', department=department, courseNumber=courseNumber)

    return render_template('index.html')

@app.route('/send_email', methods=['POST'])
def send_email():
    if request.method == 'POST':
        if request.form.get("phone"):
            return "bot detected", 400
        email = request.form.get('email').lower()
        message = request.form.get('message')
        contact_message(email, message)
        return render_template('sent.html')


@app.route('/home')
def func():
    return render_template('index.html')

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
    return render_template('dashboard.html')