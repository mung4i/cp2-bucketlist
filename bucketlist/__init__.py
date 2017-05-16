import os

from flask import Flask
from flask_jwt import JWT
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api


from bucketlist.config import app_config

db = SQLAlchemy()
login_manager = LoginManager()
api = Api()
jwt = JWT()


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

    api.init_app(app)
    db.init_app(app)

    from bucketlist.models import User
    global jwt
    jwt = JWT(app, User.authenticate, User.identity)
    login_manager.init_app(app)
    login_manager.login_message = "You must be logged in to have access"
    login_manager.login_view = "auth.login_api"
    migrate = Migrate(app, db)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    return app
