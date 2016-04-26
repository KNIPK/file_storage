from file_storage import db, bcrypt


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True, index = True)
    password = db.Column(db.String(120), unique = False, index = True)
    email = db.Column(db.String(120), unique = True, index = True)
    email_confirmed = db.Column(db.Boolean, default = False)
    directories = db.relationship('Directory',backref='owner',lazy='dynamic')

    def __init__(self, username, password, email, email_confirmed = False):
        self.username = username
        self.password = bcrypt.generate_password_hash(password)
        self.email = email
        self.email_confirmed = email_confirmed

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def activate_user(self):
        self.email_confirmed = True

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def is_authenticated(self):
        return True

    def is_active(self):# nazwa do zmiany
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


    def __repr__(self):
        return '<User %r>' % self.username

class Directory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=False, index=True)
    access = db.Column(db.Boolean, default=True)
    password = db.Column(db.String(64), index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    files = db.relationship("File",backref='holder',lazy='dynamic')

    def __init__(self,name,owner_id):
        self.name = name
        self.access = True
        self.owner_id = owner_id
        self.white_list = []
        self.password = None

    def deny(self, password):
        self.access = False
        self.password = bcrypt.generate_password_hash(password)
        self.white_list.append(self.owner_id)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def allow_for_user(self, user):
        self.white_list.append(user)

    def deny_for_user(self, user):
        pass

    def allow_for_all(self):
        self.access = True

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=False, index=True)
    ext = db.Column(db.String(10),unique=False,index=True)
    access = db.Column(db.Boolean, default=True)
    password = db.Column(db.String(64),index = True)
    directory_id = db.Column(db.Integer,db.ForeignKey('directory.id'))

    def __init__(self,filename,directory_id):
        self.name = filename
        self.ext = filename.split(".")[-1]
        self.access = True
        self.directory_id=directory_id
        self.white_list = []
        self.password = None

    def deny(self,password):
        self.access = False
        self.password = bcrypt.generate_password_hash(password)
        self.white_list.append(self.owner_id)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def allow_for_user(self,user):
        self.white_list.append(user)

    def deny_for_user(self, user):
        pass

    def allow_for_all(self):
        self.access = True
