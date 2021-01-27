from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from datetime import datetime
from .main import app

db = SQLAlchemy(app)


class Table(db.Model):
    __tablename__= 'table'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))
    filepath = db.Column(db.String(100))
    date_created = db.Column(db.DateTime)

    wards = db.relationship(
        'Ward',
        backref = db.backref('Table', lazy = 'joined'),
        lazy = 'select')

    def __init__(self, name = None, description= 'default', filepath = None) -> None:
        self.name = name
        self.description = description
        self.filepath = filepath
        self.date_created = datetime.now()

    def __repr__(self) -> str:
        return f"Таблиця: {self.name}"


class Ward(db.Model):
    __tablename__='wards'
    id = db.Column(db.Integer, primary_key=True)
    number= db.Column(db.Integer)
    fullname = db.Column(db.String(100), nullable = False)
    address = db.Column(db.String(150))
    checked = db.Column(db.Boolean, default = False)
    ckecked_date = db.Column(db.DateTime)

    table_id = db.Column(db.Integer, db.ForeignKey('table.id'))


    def __init__(self, number = None, fullname = None, address = None, checked = False) -> None:
        self.number = number
        self.fullname = fullname
        self.address = address
        self.checked = checked
        self.ckecked_date = None

    def __repr__(self) -> str:
        return f"{self.fullname} адрес: {self.address} отмечен: {self.checked}"
    
    @classmethod
    def seek_in_fullname(cls, id: int, query_string: str):
        q_set = cls.query.filter(cls.table_id == id).filter(cls.fullname.like(f'%{ query_string }%')).order_by(cls.id)
        return q_set

    @classmethod
    def get_by_table_id(cls, id: int):
        q_set = cls.query.filter(cls.table_id == id)
        return q_set

    
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    tables = db.relationship('Video', backref='user', lazy=True)
    wards = db.relationship('Ward', backref='user', lazy=True)

    # def get_token(self, expire_time=24):
    #     expire_delta = timedelta(expire_time)
    #     token = create_access_token(
    #         identity=self.id, expires_delta=expire_delta)
    #     return token
