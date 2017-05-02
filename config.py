# Enable debugging features
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """
    My configs
    """
    # DEBUG = False
    # TESTING = False
    CSRF_ENABLED = True


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:////' + basedir + '/tests' + \
        '/bucketlist_test.sqlite'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:////' + basedir + '/bucketlist' + \
        '/bucketlist.sqlite'


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
