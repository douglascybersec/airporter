from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate 
from flask_bootstrap import Bootstrap
from config import Config
from flask_mail import Mail

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate() 
bootstrap = Bootstrap()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    mail.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        from .routes import init_routes
        init_routes(app)
        db.create_all()

    return app
