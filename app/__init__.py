import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resgen_db.db'
    app.config['SECRET_KEY'] = os.environ.get('DB_SECRET_KEY')

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # import to create table on a first run
    from .models import User, UserDetails, Resumes
    with app.app_context():
        db.create_all()

    # Import and register blueprints
    from .routes import main_blueprint
    app.register_blueprint(main_blueprint)

    return app
