import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config():
    DEBUG = False
    TESTING = False
    SECRET_KEY = "B\xb2?.\xdf\x9f\xa7m\xf8\x8a%,\xf7\xc4\xfa\x91"
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024

    IMAGE_UPLOADS = "/home/username/app/app/static/images/uploads"

    SESSION_COOKIE_SECURE = True

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    ENV ='development'

    UPLOAD_FOLDER = os.path.join(BASEDIR,'uploads')
    IMAGE_UPLOADS = "/home/username/projects/my_app/app/static/images/uploads"

    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Ghjws733@localhost/online-checker'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_SECURE = False

