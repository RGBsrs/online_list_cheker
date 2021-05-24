from datetime import datetime
from datetime import timezone
from sqlalchemy.sql import func
from . import db
from flask_login import UserMixin


class Table(db.Model):
    __tablename__ = "table"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))
    filepath = db.Column(db.String(200))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    wards = db.relationship(
        "Ward",
        backref=db.backref("Table", lazy="joined"),
        lazy="select",
        cascade="all, delete-orphan",
    )

    def __init__(
        self, name=None, description="default", filepath=None, user_id=None
    ) -> None:
        self.name = name
        self.description = description
        self.filepath = filepath
        self.date_created = datetime.now()
        self.user_id = user_id

    def __repr__(self) -> str:
        return f"Таблиця: {self.name}"


class Ward(db.Model):
    __tablename__ = "wards"
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    fullname = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(150))
    checked = db.Column(db.Boolean, default=False)
    ckecked_date = db.Column(db.DateTime)

    table_id = db.Column(db.Integer, db.ForeignKey("table.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(self, number=None, fullname=None, address=None, checked=False) -> None:
        self.number = number
        self.fullname = fullname
        self.address = address
        self.checked = checked
        self.ckecked_date = None

    def __repr__(self) -> str:
        return f"{self.fullname} адрес: {self.address} отмечен: {self.checked}"

    @classmethod
    def seek_in_fullname(cls, id: int, query_string: str):
        q_set = (
            cls.query.filter(cls.table_id == id)
            .filter(cls.fullname.like(f"%{ query_string }%"))
            .order_by(cls.id)
        )
        return q_set

    @classmethod
    def get_by_table_id(cls, id: int):
        q_set = cls.query.filter(cls.table_id == id).order_by(cls.id)
        return q_set


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    registration_date = db.Column(db.DateTime(timezone=True), default=func.now())
    is_admin = db.Column(db.Boolean, default=False)

    tables = db.relationship(
        "Table", backref=db.backref("User", lazy="joined"), lazy="select"
    )

    wards = db.relationship(
        "Ward", backref=db.backref("User", lazy="joined"), lazy="select"
    )

    def __init__(self, name=None, email=None, password=None) -> None:
        self.name = name
        self.email = email
        self.password = password

    @classmethod
    def get_user(cls, id: int):
        return cls.query.filter(cls.id == id).first()

    # def get_token(self, expire_time=24):
    #     expire_delta = timedelta(expire_time)
    #     token = create_access_token(
    #         identity=self.id, expires_delta=expire_delta)
    #     return token
