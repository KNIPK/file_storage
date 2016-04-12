from file_storage import db, bcrypt


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True, index = True)
    password = db.Column(db.String(120), unique = False, index = True)
    email = db.Column(db.String(120), unique = True, index = True)
    is_active = db.Column(db.Boolean, default = False)

    def __init__(self, username, password, email, email_confirmed = False):
        self.username = username
        self.password = bcrypt.generate_password_hash(password)
        self.email = email
        self.is_active = email_confirmed

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def activate_user(self):
        self.is_active = True

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def __repr__(self):
        return '<User %r>' % self.username
