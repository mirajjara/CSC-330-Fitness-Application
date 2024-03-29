from flask import Flask
from .extensions import db, login_manager
from .extensions import db, migrate
from .auth import auth as auth_blueprint

def create_app():
    app = Flask(__name__, template_folder='../templates')
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitnessassist.db'

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint) 

    from .models import User

    with app.app_context():
        from . import routes 

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
