import re
from flask import Blueprint, render_template, request
from flask.helpers import url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from .models import  User
from . import db, logger


auth = Blueprint('auth', __name__)


@auth.route('/sign-up', methods = ['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        u = User(name = name, email = email, password = generate_password_hash(password, method='sha256'))
        db.session.add(u)
        db.session.commit()
        db.session.close()
        return render_template('index.html')

    return render_template('sign-up.html')