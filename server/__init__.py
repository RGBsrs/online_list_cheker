from os import path
from flask import Flask
from flask_login import LoginManager
import logging
from flask_sqlalchemy import SQLAlchemy
from .settings import DevelopmentConfig


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    from .models import Table, Ward, User

    db.init_app(app)
    # init_db(app)

    login_manager = LoginManager()
    login_manager.login_view = "views.show_tables"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    from .views import views
    from .auth import auth
    from .profile import profile

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(profile, url_prefix="/")

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    @app.template_filter("clean_date")
    def clean_date(dt):
        return dt.strftime("%d.%m, в %H:%M")

    @app.cli.command("restart_db")
    def restart_db():
        db.drop_all()
        db.create_all()
        print("DB cleared and created")

    return app


def init_db(app):
    if not path.exists("server/db.sqlite"):
        # db.drop_all(app = app)
        db.create_all(app=app)
        print("DB created")


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
    file_handler = logging.FileHandler("site.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()
