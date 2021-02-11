import os
from datetime import  datetime 
from flask import Flask, flash, request, redirect, url_for, render_template
import logging
from sqlalchemy.orm import query
from werkzeug.utils import secure_filename
import uuid
from .services import read_from_excel, allowed_file
from .settings import DevelopmentConfig


ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
ROWS_PER_PAGE = 20


app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
upload_path = app.config['UPLOAD_FOLDER']


from .models import Ward, Table, db

db.init_app(app)

@app.cli.command("init_db")
def init_db():
    db.drop_all()
    db.create_all()
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


@app.route('/', methods=['GET'])
def show_tables():
    try:
        table_names = db.session.query(Table).all()
        return render_template('index.html', table_names = table_names)
    except Exception as e:
        logger.warning(f'Error when quering all tables: {e}')
    return render_template('index.html')


@app.route('/', methods=['POST'])
def change_tables():  
    try:
        table_id = request.form['index']
        return redirect(url_for('delete_table', id = table_id))
    except Exception as e:
        logger.warning(f'Error when deliting table: {e}')
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Файл не найден', "warning")
            return redirect(request.url)
        file = request.files['file']

        # if user does not select file, browser also
        # submit an empty part without filename

        if file.filename == '':
            flash('Файл не выбран', "warning")
            return redirect(request.url)

        if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):
            filename = uuid.uuid4().hex +'.'+ secure_filename(file.filename).split('.')[-1]
            file.save(os.path.join(upload_path, filename))
            table_data = read_from_excel(os.path.join(upload_path, filename))
            if request.form['description']:
                description = request.form['description']
            else:
                description = 'default description'
            
            t = Table(name = filename, filepath = os.path.join(upload_path, filename), description = description)
            for record in table_data:
                w = Ward(record[0], record[1],record[2]) 
                t.wards.append(w)
            db.session.add(t)    
            db.session.commit()
            db.session.close()
            return redirect(url_for('show_tables'))
    return render_template('upload.html') 


@app.route('/table/<id>', methods=['GET'])
def uploaded_file(id):
    page = request.args.get('page', 1, type=int)
    q_string = request.args.get('query-string')
    if q_string:
        q_string = q_string.upper() 
        wards = Ward.seek_in_fullname(id, q_string).paginate(page=page, per_page=ROWS_PER_PAGE)
    else:
        wards = Ward.get_by_table_id(id).paginate(page=page, per_page=ROWS_PER_PAGE)
    return render_template('list.html', wards = wards, id = id)


@app.route('/check/<id>/<page>', methods=['GET', 'POST'])
def check_record(id, page):
    if request.method == 'POST':
        table_id = request.form['index']
        Ward.query.filter(Ward.id == id).update(dict(checked=True, ckecked_date = datetime.now()))
        db.session.commit() 
        if page == '':
            page = 1
        return redirect(url_for('uploaded_file', id = table_id, page = page))
    return redirect(url_for('show_tables')) 

@app.route('/delete/<id>', methods=['POST', 'GET'])
def delete_table(id):
    if request.method == 'GET':
        Table.query.filter(Table.id == id).delete()
        Ward.query.filter(Ward.table_id == id).delete()
        db.session.commit()
        return redirect(url_for('show_tables'))
    return redirect(url_for('show_tables'))


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


@app.template_filter("clean_date")
def clean_date(dt):
    return dt.strftime("%d.%m, в %H:%M")