from flask_sqlalchemy import SQLAlchemy
import os

# Initialize the db without an app object yet
db = SQLAlchemy()

# Move the PEPPER constant here
PEPPER = os.environ.get('SECURITY_PEPPER', 'a-very-safe-fallback')