# Enable debugging features
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """
    My configs
    """
    CSRF_ENABLED = True
    SECRET_KEY = os.getenv('SECRET_KEY', 'the-secret-secret-k3y')


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
        os.path.join(basedir, 'bucketlist_test.sqlite')
    SECRET_KEY = os.getenv('SECRET_KEY', 'the-secret-secret-k3y')


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:@localhost/bucketlist_db'
    BASE_URL = "http://127.0.0.1:5000/"
    FRONTEND_URL = "http://localhost:8000"


class ProductionConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False
    BASE_URL = "https://cp2-bucketlist.herokuapp.com"

app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
