from flask_wtf import Form
from wtforms import StringField
from wtforms.fields.html5 import EmailField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, Length, EqualTo


class RegisterForm(Form):
    username = StringField('name', validators = [Length(min = 5, max = 16)])
    password = PasswordField('pass', validators = [Length(min = 5, max = 16)])
    confirm = PasswordField('confirm', validators = [Length(min = 5, max = 16), EqualTo('password')])
    email = EmailField('mail', validators = [DataRequired()])


class LoginForm(Form):
    username = StringField('name', validators = [DataRequired(), Length(min = 4, max = 16)])
    password = PasswordField('pass', validators = [DataRequired(), Length(min = 6, max = 16)])
