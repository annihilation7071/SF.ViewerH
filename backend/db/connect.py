import os

from sqlalchemy import Column, Integer, String, create_engine, DateTime, ForeignKey, text, MetaData
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime
from backend import utils
from dataclasses import dataclass


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = 'projects'
    _id = Column(Integer, primary_key=True)
    info_version = Column(Integer)
    lid = Column(String, unique=True)
    lvariants = Column(String(length=3000))
    source_id = Column(String)
    source = Column(String)
    url = Column(String(length=500))
    downloader = Column(String)
    title = Column(String(length=500))
    subtitle = Column(String(length=500))
    upload_date = Column(DateTime)
    preview = Column(String(length=500))
    parody = Column(String(length=500))
    character = Column(String(length=500))
    tag = Column(String)
    artist = Column(String(length=500))
    group = Column(String)
    language = Column(String)
    category = Column(String)
    series = Column(String(length=3000))
    pages = Column(Integer)
    dir_name = Column(String(length=500))
    lib = Column(String)
    search_body = Column(String(length=3000))


def get_session():
    engine = create_engine(f'sqlite:///data/DB/dbv1.db')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    return session



