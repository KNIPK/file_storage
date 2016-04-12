from migrate.versioning import api
from file_storage.config import SQLALCHEMY_DATABASE_URI
from file_storage.config import SQLALCHEMY_MIGRATE_REPO
from file_storage import db
import os.path

db.create_all()

if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
	api.create(SQLALCHEMY_MIGRATE_REPO,'datebase repository')
	api.version_control(SQLALCHEMY_DATABASE_URI,SQLALCHEMY_MIGRATE_REPO)
else:
	api.version_control(SQLALCHEMY_DATABASE_URI,SQLALCHEMY_MIGRATE_REPO,api.version(SQLALCHEMY_MIGRATE_REPO))

