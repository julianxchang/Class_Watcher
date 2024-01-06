from flask import Flask, render_template, request, url_for
from app.huey import tasks

app = Flask(__name__, template_folder="Templates")

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/run', methods = ['Get', 'POST'])
def run_code():
    if request.method == 'POST':
        email = request.form.get('email')
        courseNumber = request.form.get('course_number')
        run_time = request.form.get('run_time')

        print(email)
        print(courseNumber)
        print(run_time)
        tasks.run_program(email, courseNumber, run_time)
        return render_template('landingpage.html')

@app.route('/home')
def func():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, port=5000)