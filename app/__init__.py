from flask import Flask, render_template, request
from app.db import get_db_conn
from app.utils import send_confirmation_email, contact_message
import re
app = Flask(__name__, template_folder="Templates")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['GET', 'POST'])
def run_code():
    if request.method == 'POST':
        email = request.form.get('email')
        courseNumber = request.form.get('course_number')
        department = request.form.get('department')

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return render_template('index.html', error="Invalid email address")

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

        send_confirmation_email(email, courseNumber)

        conn.commit()
        cursor.close()
        conn.close()

        print(email)
        print(courseNumber)
        print(department)
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

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/sent')
def sent():
    return render_template('sent.html')

if __name__ == "__main__":
    app.run(debug=True, port=8000)