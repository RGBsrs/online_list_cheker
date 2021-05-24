from flask import Blueprint, render_template, request, flash
from flask.helpers import url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import redirect

from .models import User
from . import db, logger


auth = Blueprint("auth", __name__)


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists.", category="error")
        elif len(email) < 6:
            flash("Email must be greater than 3 characters.", category="error")
        elif len(name) < 4:
            flash("First name must be greater than 1 character.", category="error")
        elif password1 != password2:
            flash("Passwords don't match.", category="error")
        elif len(password1) < 7:
            flash("Password must be at least 7 characters.", category="error")
        else:
            new_user = User(
                name=name,
                email=email,
                password=generate_password_hash(password1, method="sha256"),
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return render_template("index.html")

    return render_template("sign-up.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.show_tables"))
            else:
                flash("Incorrect password, try again.", category="error")
        else:
            flash("Email does not exist.", category="error")

    return redirect(request.url)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("index.html")


@auth.route("/cmu")
def create_user():
    user = User(
        name="admin",
        email="my@mail.ua",
        password=generate_password_hash("123456", method="sha256"),
    )
    db.session.add(user)
    db.session.commit()
    login_user(user, remember=True)
    return redirect(url_for("views.show_tables"))
