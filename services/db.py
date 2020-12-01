from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
import pandas as pd


Base = declarative_base()

class Ward(Base):
    __tablename__='wards'
    id = Column(Integer, primary_key=True)
    number= Column(Integer)
    fullname = Column(String)
    address = Column(String)
    additional_info = Column(String)


engine = create_engine('sqlite:///test.db', echo = False)
Base.metadata.create_all(bind=engine)


def convert_to_db(file_path, table_name):
    if file_path:
        file_type = file_path.split('.')[-1]
        if file_type == "xlsx" or file_type == "xls":
            df = pd.read_excel(file_path, names=['number', 'fullname', 'address', 'additional_info'], header=None)
            df.to_sql(table_name, con=engine, if_exists='replace')
            print(engine.execute(f"SELECT * FROM {table_name}").fetchmany(10))
        else:
            print('not valid file type')

