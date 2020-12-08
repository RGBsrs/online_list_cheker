import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from .converter import convert_to_db



ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
ROWS_PER_PAGE = 20


app = Flask(__name__)
from .models import Ward, Table, db, init_db


BASEDIR = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASEDIR,'uploads')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASEDIR, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TESTING'] = True


app.secret_key = "super secret key"


init_db()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def home():
    if request.method == 'GET':
        table_names = Table.query.all()
    return render_template('index.html', table_names = table_names)    


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        flash('file ....')
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return redirect('/upload')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            table = convert_to_db(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            t = Table(name = filename, filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename))
            for record in table:
                w = Ward(record[0],record[1],record[2]) 
                t.wards.append(w)
            db.session.add(t)    
            db.session.commit()
            db.session.close()
            
            return redirect('/')
    return render_template('upload.html') 


@app.route('/uploads/<id>', methods=['GET', 'POST'])
def uploaded_file(id):
    page = request.args.get('page', 1, type=int)
    wards = Ward.query.filter(Ward.table_id == Table.query.filter_by(id = id).first().id ).paginate(page=page, per_page=ROWS_PER_PAGE)
    return render_template('list.html', wards = wards, id = id)

if __name__ == '__main__':
    app.run(debug=True)
