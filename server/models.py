from sqlalchemy import Column, Integer, String, Boolean
from .db import Base

class Ward(Base):
    __tablename__='wards'
    id = Column(Integer, primary_key=True)
    number= Column(Integer)
    fullname = Column(String)
    address = Column(String)
    checked = Column(Boolean, default = False)


    def __init__(self, number = None, fullname = None, address = None, checked = False) -> None:
        self.number = number
        self.fullname = fullname
        self.address = address
        self.checked = checked
    

    def __repr__(self) -> str:
        return f"{self.fullname} адрес: {self.address} отмечен: {self.checked}"


