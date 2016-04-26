import os

basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = 'moithos key'

SALT_CONFIRM_EMAIL = 'email-confirm-key'
SALT_RESET_PASSWORD = 'reset-password'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir + '/db', 'db_repository')

MAIL_SERVER = 'smtp.gmail.com'
MAIL_DEBUG = True
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'knitestmail@gmail.com'
MAIL_PASSWORD = 'filemanager'
MAIL_DEFAULT_SENDER = 'knitestmail@gmail.com'

UPLOAD_FOLDER = 'file_storage/upload_storage'


EXT_DIC = {
    'txt':'text',#txt
    'jpg':'image',#images
    'JPG':'image',
    'png': 'image',
    'jpeg': 'image',
    'gif': 'image',
    'bmp': 'image',
    'pdf':'pdf',#pdf
    'zip':'archive',#archives
    'rar':'archive',
    'iso':'archive',
    'sda':'archive',
    'doc':'word',#word
    'docm':'word',
    'docx':'word',
    'dot':'word',
    'dotm':'word',
    'dotx':'word',
    'avi':'video',#video
    'flv': 'video',
    'wmv': 'video',
    'mov': 'video',
    'mp4': 'video',
    'mp3':'audio',#sound
    'wav': 'audio',
    'wma': 'audio',
    'm4a': 'audio',
    'cpp':'code',#code
    'html': 'code',
    'css': 'code',
    'js': 'code',
    'py': 'code',

}