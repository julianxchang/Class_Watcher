from flask import render_template, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from app import app
from werkzeug.security import generate_password_hash, check_password_hash
from .utils import get_user_stats

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():

    if current_user.is_authenticated:
        user_stats = get_user_stats(current_user.email)
        return render_template('dashboard.html', stats=user_stats)

    email = request.form.get('email').lower()
    password = request.form.get('password')
    # remember = True if request.form.get('remember') else False

    user = User.get_by_email(email)

    if not user or not check_password_hash(user.password, password):
        return render_template('login.html', error='Please check your login details and try again.')

    login_user(user)
    user_stats = get_user_stats(email)
    return render_template('dashboard.html', stats=user_stats)

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email').lower()
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    # check if email already exists in db
    user = User.get_by_email(email)

    if user:
        return render_template('signup.html', error = "Email address already exists. Please log in instead.")
    if password != confirm_password:
        return render_template('signup.html', error = "Passwords do not match. Please try again.")

    User.create(email=email, password_hash=generate_password_hash(password))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('index.html')