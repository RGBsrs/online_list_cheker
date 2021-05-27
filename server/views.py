import os

from datetime import datetime
from flask import Blueprint, flash, request, redirect, url_for, render_template
from flask_login.utils import login_required
from flask_login import current_user
from werkzeug.utils import secure_filename
import uuid
from .services.file_service import read_from_excel, allowed_file
from .models import Ward, Table, User
from .services.table_service import TableService
from .settings import DevelopmentConfig
from . import db, logger


ALLOWED_EXTENSIONS = {"xlsx", "xls"}
ROWS_PER_PAGE = 20
upload_path = DevelopmentConfig.UPLOAD_FOLDER

views = Blueprint("views", __name__)


@views.route("/", methods=["GET"])
#@login_required
def show_tables():
    try:
        table_names = TableService.fetch_all_tables(db.session).all()
        return render_template("index.html", table_names=table_names)
    except Exception as e:
        logger.warning(f"Error when quering all tables: {e}")
    return render_template("index.html")


@views.route("/", methods=["POST"])
@login_required
def change_tables():
    try:
        table_id = request.form["index"]
        return redirect(url_for("views.delete_table", id=table_id))
    except Exception as e:
        logger.warning(f"Error when deliting table: {e}")
    return render_template("index.html")


@views.route("/upload", methods=["GET", "POST"])
@login_required
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("Файл не найден", "warning")
            return redirect(request.url)
        file = request.files["file"]

        # if user does not select file, browser also
        # submit an empty part without filename

        if file.filename == "":
            flash("Файл не выбран", "warning")
            return redirect(request.url)

        if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):
            filename = (
                uuid.uuid4().hex + "." + secure_filename(file.filename).split(".")[-1]
            )
            file.save(os.path.join(upload_path, filename))
            table_data = read_from_excel(os.path.join(upload_path, filename))
            if request.form["description"]:
                description = request.form["description"]
            else:
                description = "default description"
            try:
                t = Table(
                    name=filename,
                    filepath=os.path.join(upload_path, filename),
                    description=description,
                    user_id=current_user.id,
                )
                for record in table_data:
                    w = Ward(record[0], record[1], record[2])
                    t.wards.append(w)
                db.session.add(t)
                db.session.commit()
                return redirect(url_for("views.show_tables"))
            except Exception as e:
                db.session.rollback()
                logger.warning(f"Error when adding table or wards: {e}")
    return render_template("upload.html")


@views.route("/table/<id>", methods=["GET"])
@login_required
def uploaded_file(id):
    page = request.args.get("page", 1, type=int)
    q_string = request.args.get("query-string")
    if q_string:
        q_string = q_string.upper()
        wards = Ward.seek_in_fullname(id, q_string).paginate(
            page=page, per_page=ROWS_PER_PAGE
        )
    else:
        wards = Ward.get_by_table_id(id).paginate(page=page, per_page=ROWS_PER_PAGE)
    return render_template("list.html", wards=wards, id=id)


@views.route("/check/<id>/<page>", methods=["GET", "POST"])
@login_required
def check_record(id, page):
    if request.method == "POST":
        table_id = request.form["index"]
        user = request.form["user_id"]
        try:
            Ward.query.filter(Ward.id == id).update(
                dict(checked=True, ckecked_date=datetime.now(), user_id=user)
            )
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.warning(f"Error when checking ward:{id} :\n {e}")
        w = Ward.query.filter(Ward.id == id).first()
        db.session.close()
        flash(f"{w.fullname} cheked", "succsess")
        if page == "":
            page = 1
        return redirect(url_for("views.uploaded_file", id=table_id, page=page))
    return redirect(url_for("views.show_tables"))


@views.route("/delete/<id>", methods=["POST", "GET"])
@login_required
def delete_table(id):
    if request.method == "GET":
        try:
            Ward.query.filter(Ward.table_id == id).delete()
            Table.query.filter(Table.id == id).delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.warning(f"Errod whed deliting table:{id} \n {e}")
        return redirect(url_for("views.show_tables"))
    return redirect(url_for("views.show_tables"))
