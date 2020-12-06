import os
from flask import Flask, flash, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from .converter import convert_to_db

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

app = Flask(__name__)
BASEDIR = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy(app)

app.config['UPLOAD_FOLDER'] ='uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASEDIR, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TESTING'] = True


app.secret_key = "super secret key"



class Ward(db.Model):
    __tablename__='wards'
    id = db.Column(db.Integer, primary_key=True)
    number= db.Column(db.Integer)
    fullname = db.Column(db.String(100))
    address = db.Column(db.String(150))
    checked = db.Column(db.Boolean, default = False)


    def __init__(self, number = None, fullname = None, address = None, checked = False) -> None:
        self.number = number
        self.fullname = fullname
        self.address = address
        self.checked = checked
    

    def __repr__(self) -> str:
        return f"{self.fullname} адрес: {self.address} отмечен: {self.checked}"

db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('base.html')    

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
            for table1 in table:
                w = Ward(table1[0],table1[1],table1[2]) 
                db.session.add(w)
            db.session.commit()
            db.session.close()
            print('session closed....')
            return redirect('/')
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)
