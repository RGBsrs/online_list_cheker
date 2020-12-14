from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from datetime import datetime
from .main import app

db = SQLAlchemy(app)


class Table(db.Model):
    __tablename__= 'table'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    filepath = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime,nullable=False)
    wards = db.relationship('Ward', lazy= "dynamic", primaryjoin = "Table.id == Ward.table_id", cascade="all, delete")

    def __init__(self, name = None, description= 'default', filepath = None) -> None:
        self.name = name
        self.description = description
        self.filepath = filepath
        self.date_created = datetime.utcnow()

    def __repr__(self) -> str:
        return f"Таблиця: {self.name}"


class Ward(db.Model):
    __tablename__='wards'
    id = db.Column(db.Integer, primary_key=True)
    number= db.Column(db.Integer)
    fullname = db.Column(db.String(100), nullable = False)
    address = db.Column(db.String(150))
    checked = db.Column(db.Boolean, default = False)

    table_id = db.Column(db.Integer, db.ForeignKey('table.id', ondelete ='CASCADE'), nullable=False)
    table = db.relationship('Table', back_populates = 'wards' )


    def __init__(self, number = None, fullname = None, address = None, checked = False) -> None:
        self.number = number
        self.fullname = fullname
        self.address = address
        self.checked = checked
    

    def __repr__(self) -> str:
        return f"{self.fullname} адрес: {self.address} отмечен: {self.checked}"



def init_db():
    db.create_all()