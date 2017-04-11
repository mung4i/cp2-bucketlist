import os


from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


from config import app_config


db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_name):
    if os.getenv('FLASK_CONFIG') == "production":
        app = Flask(__name__)
        app.config.update(
            SECRET_KEY=os.environ['SECRET_KEY'],
            SQLALCHEMY_DATABASE_URI=os.environ['DATABASE_URL']
        )
    else:
        app = Flask(__name__, instance_relative_config=True)
        app.config.from_object(app_config[config_name])
        app.config.from_pyfile('config.py')

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_message = "You must be logged in to have access"
    login_manager.login_view = "auth.login"

    migrate = Migrate(app, db)

    from app import models

    @app.route('/')
    def hello_world():
        return 'Hello World!'

    return app
