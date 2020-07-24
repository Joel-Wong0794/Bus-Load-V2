import os

class Config(object):
    DEBUG = False
    TESTING = False

    SECRET_KEY = "asdsdsaasd"
    DB_NAME = os.environ.get('DB_NAME', None) # For Heroku
    


class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    DB_NAME = "mongodb+srv://admin:Password1!@gisdata-test1.3hzb3.mongodb.net/<dbname>?retryWrites=true&w=majority" # Development TEST DB

class TestingConfig(Config):
    TESTING = True