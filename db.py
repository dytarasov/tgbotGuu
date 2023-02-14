import os

from sqlalchemy import create_engine, Column, Integer, Boolean, String
from sqlalchemy.orm import scoped_session, declarative_base, sessionmaker


engine = create_engine('sqlite:///C:\\Users\\Dima\\PycharmProjects\\tgbotGuu\\data\\dbase.db')

session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = session.query_property()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    fio = Column(String)
    department = Column(String)
    course = Column(Integer)
    group = Column(String)
    user_type = Column(Integer)
    active = Column(Boolean)

class Meets(Base):
    __tablename__ = 'meets'
    id = Column(Integer, primary_key=True,autoincrement=True)
    m_date = Column(String)
    m_time = Column(String)
    professor_id = Column(Integer)
    user_id = Column(Integer)
    m_desc = Column(String)
    create_time = Column(String)
    status = Column(Integer)





Base.metadata.create_all(bind=engine)


