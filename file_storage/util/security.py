from itsdangerous import URLSafeTimedSerializer

from file_storage import app

ts = URLSafeTimedSerializer(app.config['SECRET_KEY'])
