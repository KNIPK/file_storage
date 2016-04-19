from flask import Flask
from flask_bootstrap import Bootstrap
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

UPLOAD_FOLDER = 'c:/flask_uploads/'
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
Bootstrap(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

bcrypt = Bcrypt(app)

lm = LoginManager(app)
lm.login_view = "signin"
lm.login_message = "Musisz sie zalogować"


from .views import user_zone
from file_storage import models
from .views import files_zone