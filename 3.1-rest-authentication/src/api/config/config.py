import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    #SQLALCHEMY_DATABASE_URI =  <Production DB URL>
    #SQLALCHEMY_DATABASE_URI = "mysql+pymysql://<db_url>:<port>/<db_name>"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'crud_api_db.sqlite')


class DevelopmentConfig(Config):
    DEBUG = True
    #SQLALCHEMY_DATABASE_URI = "mysql+pymysql://<db_url>:<port>/<db_name>"

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'crud_api_db.sqlite')
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    TESTING = True
    #SQLALCHEMY_DATABASE_URI = "mysql+pymysql://<db_url>:<port>/<db_name>"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'crud_api_db.sqlite')
    SQLALCHEMY_ECHO = False
