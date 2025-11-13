from flask import Flask, render_template, request
from app.db import get_db_conn
from app.utils import send_confirmation_email
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

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return render_template('index.html', error="Invalid email address")

        conn = get_db_conn()
        cursor = conn.cursor()

        # first check if user already requested to watch this class
        cursor.execute("""
            SELECT * FROM users
            WHERE email = %s AND course_number = %s;
        """, (email, courseNumber))

        if cursor.fetchone() is not None:
            cursor.close()
            conn.close()
            return render_template('error.html')

        # insert into db
        cursor.execute("""
            INSERT INTO users (email, course_number)
            VALUES (%s, %s);
        """, (email, courseNumber))

        send_confirmation_email(email, courseNumber)

        conn.commit()
        cursor.close()
        conn.close()

        print(email)
        print(courseNumber)
        return render_template('landingpage.html')

    return render_template('index.html')

@app.route('/home')
def func():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, port=8000)