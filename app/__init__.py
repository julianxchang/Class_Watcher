from flask import Flask
from flask_login import LoginManager
import os
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

app = Flask(__name__, template_folder="Templates")
app.config['SECRET_KEY'] = os.environ.get('APP_SECRET_KEY')


# Set up login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Set up rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

from app.models import User

@login_manager.user_loader
def user(user_id):
    return User.get(user_id)

from app import main
from app import auth