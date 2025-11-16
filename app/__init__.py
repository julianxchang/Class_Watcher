from flask import Flask, render_template, request
from app.db import get_db_conn
from app.utils import send_confirmation_email, contact_message, get_stats
import re

app = Flask(__name__, template_folder="Templates")

VALID_DEPARTMENTS = frozenset([
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
        email = request.form.get('email')
        department = request.form.get('department')
        courseNumber = request.form.get('course_number').upper()

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return render_template('index.html', error="Invalid email address")

        if department not in VALID_DEPARTMENTS:
            return render_template('index.html', error="Invalid department")

        conn = get_db_conn()
        cursor = conn.cursor()

        # first check if user already requested to watch this class
        cursor.execute("""
            SELECT * FROM users
            WHERE email = %s AND course_number = %s AND department = %s;
        """, (email, courseNumber, department))

        if cursor.fetchone() is not None:
            cursor.close()
            conn.close()
            return render_template('error.html')

        # insert into db
        cursor.execute("""
            INSERT INTO users (email, course_number, department)
            VALUES (%s, %s, %s);
        """, (email, courseNumber, department))

        send_confirmation_email(email, department, courseNumber)

        conn.commit()
        cursor.close()
        conn.close()

        print(email)
        print(department, courseNumber)
        return render_template('landingpage.html')

    return render_template('index.html')

@app.route('/send_email', methods=['POST'])
def send_email():
    if request.method == 'POST':
        message = request.form.get('message')
        contact_message(message)
        return render_template('sent.html')


@app.route('/home')
def func():
    return render_template('index.html')

@app.route('/changelog')
def changelog():
    return render_template('changelog.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/sent')
def sent():
    return render_template('sent.html')

@app.route('/stats')
def stats():
    stats_data = get_stats()
    return render_template('stats.html', stats=stats_data)

if __name__ == "__main__":
    app.run(debug=True, port=8000)