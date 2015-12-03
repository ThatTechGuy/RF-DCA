from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
toolbar = DebugToolbarExtension(app)

from app import views, models
