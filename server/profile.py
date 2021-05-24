from flask import Blueprint, render_template, request, flash
from flask_login import login_required
from .models import User

profile = Blueprint("profile", __name__)


@login_required
@profile.route("/profile/<id>", methods=["GET", "POST"])
def user_profile(id):
    user = User.get_user(int(id))
    return render_template("profile.html", user=user)
