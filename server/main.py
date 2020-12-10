# -*- coding: utf-8 -*-
import os
from flask import Flask, flash, request, redirect, url_for, render_template, render_template_string
from flask.templating import render_template_string
from werkzeug.utils import secure_filename
from .services import read_from_excel, allowed_file
from .settings import DevelopmentConfig


ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
ROWS_PER_PAGE = 20


app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
upload_path = app.config['UPLOAD_FOLDER']

from .models import Ward, Table, db, init_db


init_db()


@app.route('/', methods=['GET','POST'])
def home():
    if request.method == 'GET':
        table_names = Table.query.all()
        return render_template('index.html', table_names = table_names)    
    if request.method == 'POST':
        table_id = request.form['index']
        return redirect(url_for('delete_table', id = table_id))
    return render_template('upload.html')


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
        if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):
            filename = secure_filename(file.filename)
            file.save(os.path.join(upload_path, filename))
            table_data = read_from_excel(os.path.join(upload_path, filename))
            t = Table(name = filename, filepath = os.path.join(upload_path, filename))
            for record in table_data:
                w = Ward(record[0], record[1],record[2]) 
                t.wards.append(w)
            db.session.add(t)    
            db.session.commit()
            db.session.close()
            
            return redirect('/')
    return render_template('upload.html') 


@app.route('/uploads/<id>', methods=['GET', 'POST'])
def uploaded_file(id):
    page = request.args.get('page', 1, type=int)
    wards = Ward.query.filter(Ward.table_id == Table.query.filter_by(id = id).first().id).paginate(page=page, per_page=ROWS_PER_PAGE)
    if request.method == 'GET':
        return render_template('list.html', wards = wards, id = id)
    elif request.method == 'POST':
        ward_id = request.form['index']
        Ward.query.filter(Ward.id == ward_id).update(dict(checked=True))
        db.session.commit()
        return redirect(request.url)   
    return render_template('list.html', wards = wards, id = id)

@app.route('/delete/<id>', methods=['POST', 'GET'])
def delete_table(id):
    if request.method == 'GET':
        Table.query.filter(Table.id == id).delete()
        Ward.query.filter(Ward.table_id == id).delete()
        db.session.commit()
        return redirect('/')
    return redirect('/')