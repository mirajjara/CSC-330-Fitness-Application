from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate


db = SQLAlchemy()  # This will be used for all database operations.
login_manager = LoginManager()  # Initialize LoginManager for authentication.
migrate = Migrate()  # Initialize Migrate for db migrations

