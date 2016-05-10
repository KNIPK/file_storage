from flask_wtf import Form
from wtforms import StringField
from wtforms.fields.html5 import EmailField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, Length, EqualTo

USER_MIN_L = 5
USER_MAX_L = 16
USER_LENGHT_MESSAGE = "Login powinien zawierać od %s do %s znaków" % (str(USER_MIN_L), str(USER_MAX_L))
PASS_MIN_L = 6
PASS_MAX_L = 16
PASS_LENGHT_MESSAGE = "Hasło powinno zawierać od %s do %s znaków" % (str(PASS_MIN_L), str(PASS_MAX_L))

PASS_CONFIRM_MESSAGE = "The retyped password does not match your password"


class RegisterForm(Form):
    username = StringField('name', validators = [Length(USER_MIN_L, USER_MAX_L, USER_LENGHT_MESSAGE)])
    password = PasswordField('pass', validators = [Length(PASS_MIN_L, PASS_MAX_L, PASS_LENGHT_MESSAGE)])
    confirm = PasswordField('confirm',validators = [EqualTo('password',PASS_CONFIRM_MESSAGE)])
    email = EmailField('mail', validators = [DataRequired("Puste pole: email")])


class LoginForm(Form):
    username = StringField('name', validators = [Length(USER_MIN_L, USER_MAX_L, USER_LENGHT_MESSAGE)])
    password = PasswordField('pass', validators = [Length(PASS_MIN_L, PASS_MAX_L, PASS_LENGHT_MESSAGE)])


class ChangeEmailForm(Form):
    email = EmailField('newEmail', validators = [DataRequired("Puste pole: email")])
    password = PasswordField('pass', validators = [Length(PASS_MIN_L, PASS_MAX_L, PASS_LENGHT_MESSAGE)])


class ChangePasswordForm(Form):
    old_password = PasswordField('old_pass', validators = [Length(PASS_MIN_L, PASS_MAX_L, PASS_LENGHT_MESSAGE)])
    password = PasswordField('pass', validators = [Length(PASS_MIN_L, PASS_MAX_L, PASS_LENGHT_MESSAGE)])
    confirm = PasswordField('confirm',
                            validators = [Length(PASS_MIN_L, PASS_MAX_L, PASS_LENGHT_MESSAGE), EqualTo('password')])


class ResetPasswordForm(Form):
    password = PasswordField('pass', validators = [Length(PASS_MIN_L, PASS_MAX_L, PASS_LENGHT_MESSAGE)])
    confirm = PasswordField('confirm',
                            validators = [Length(PASS_MIN_L, PASS_MAX_L, PASS_LENGHT_MESSAGE), EqualTo('password')])
