from sqlmodel import SQLModel, create_engine
from .model import *

url_conn = f'sqlite:///database.db'
motor_db = create_engine(url_conn, echo = False)


if __name__ == '__main__':
    SQLModel.metadata.create_all(motor_db)
