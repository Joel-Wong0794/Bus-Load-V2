import os

class Config(object):
    DEBUG = False
    TESTING = False

    SECRET_KEY = "asdsdsaasd"
    DB_NAME = os.environ.get('DB_NAME', None) # For Heroku
    DB_COLLECTION = os.environ.get('DB_COLLECTION', None) # For Heroku


class ProductionConfig(Config):
    pass

# Override for Development
class DevelopmentConfig(Config):
    DEBUG = True
    DB_NAME = "mongodb+srv://admin:Password1!@gisdata-test1.3hzb3.mongodb.net/<DB_NAME>?retryWrites=true&w=majority" # Development TEST DB
    DB_COLLECTION = "DEVELOPMENT"

class TestingConfig(Config):
    TESTING = True