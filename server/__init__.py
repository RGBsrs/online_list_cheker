from flask import Flask
import logging
from flask_sqlalchemy import SQLAlchemy
from .settings import DevelopmentConfig


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    
    from .models import Table, Ward
    db.init_app(app)

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()
    
    @app.template_filter("clean_date")
    def clean_date(dt):
        return dt.strftime("%d.%m, в %H:%M")
    
    return app


def init_db(app):
    db.create_all(app = app)
    print("DB created")

def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    file_handler = logging.FileHandler('site.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()