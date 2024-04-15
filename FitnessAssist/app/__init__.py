from flask import Flask
from .extensions import db, login_manager, migrate
from .models import User
from .auth import auth as auth_blueprint
from .routes import main as main_blueprint
import os


def create_app():
    # Initialize the Flask application
    app = Flask(__name__, template_folder='../templates')
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitnessassist.db'

    # Initialize database migration service for SQLAlchemy
    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize the login manager for user authentication
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register the authentication blueprint with a URL prefix
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # Register the main routes blueprint
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint) 

    # Ensure all parts of the app are aware of database tables
    from .models import User

    with app.app_context():
        from . import routes 

    # User loader callback for login_manager to load users
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
