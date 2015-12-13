from flask import Flask
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__, instance_relative_config=True)

app.config.from_object('config')
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
toolbar = DebugToolbarExtension(app)

from models import Employee

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view =  'login'
login_manager.login_message = 'Your session has expired, login again.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(userid):
    return Employee.query.filter(Employee.id==userid).first()

from . import views
