import os
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = 'moithos key'



SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir+'/db', 'db_repository')

MAIL_SERVER = 'smtp.gmail.com'
MAIL_DEBUG = True
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'knitestmail@gmail.com'
MAIL_PASSWORD = 'filemanager'
MAIL_DEFAULT_SENDER = 'knitestmail@gmail.com'
