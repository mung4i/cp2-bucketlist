# Enable debugging features
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """
    My configs
    """
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'the-secret-secret-k3y'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_ECHO = True


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
