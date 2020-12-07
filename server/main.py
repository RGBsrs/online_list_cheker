import os
import re
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from .converter import convert_to_db



ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

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
            flash('No selected file')
            return redirect('/')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('file saved....')
            table = convert_to_db(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            t = Table(filename, os.path.join(app.config['UPLOAD_FOLDER'], filename))
            for record in table:
                w = Ward(record[0],record[1],record[2]) 
                t.wards.append(w)
            db.session.add(t)    
            db.session.commit()
            db.session.close()
            
            return redirect(url_for('uploaded_file'))
    return render_template('upload.html') 


@app.route('/uploads')
def uploaded_file():
    wards = Ward.query.limit(10)
    return render_template('list.html', wards = wards)

if __name__ == '__main__':
    app.run(debug=True)
