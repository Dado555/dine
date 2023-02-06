from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SECRET_KEY'] = '59638274f7e63060e5e0c852e861b094'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/site.db'
app.config['WHOOSH_BASE'] = 'whoosh'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from application import routes