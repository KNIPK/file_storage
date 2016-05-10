from flask_wtf import Form
from wtforms import StringField,PasswordField
from wtforms.validators import Length

DIR_MIN_L = 2
DIR_MAX_L = 16
DIR_LENGHT_MESSAGE = "Name must be between %s and %s characters" % (str(DIR_MIN_L),str(DIR_MAX_L))


class DirForm(Form):
    dirname = StringField('name', validators = [Length(DIR_MIN_L, DIR_MAX_L,DIR_LENGHT_MESSAGE)])
    password = PasswordField('password')
