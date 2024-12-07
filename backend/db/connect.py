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


def temp_add_to_db(session):
    all_projects = utils.get_projects()

    def f(x):
        if isinstance(x, list):
            return ";;;".join(x)
        else:
            try:
                d = datetime.strptime(x, '%Y-%m-%dT%H:%M:%S')
                print(d)
                return d
            except:
                print(x)
                pass
            return x

    lids = {}
    for project in all_projects:
        if project["lid"] not in lids:
            lids[project["lid"]] = project
        else:
            print(project["lid"], project)
            print(lids[project["lid"]])

    for project in all_projects:
        project = {k: f(v) for k, v in project.items()}

        search_body = ";;;".join([project["lid"], project["source"], project["url"], project["downloader"],
                                  project["title"], project["subtitle"], project["parody"], project["character"],
                                  project["tag"], project["artist"], project["group"], project["language"],
                                  project["category"], project["series"]])

        row = Project(info_version=project["info_version"],
                      lid=project["lid"],
                      lvariants=project["lvariants"],
                      source_id=project["source_id"],
                      source=project["source"],
                      url=project["url"],
                      downloader=project["downloader"],
                      title=project["title"],
                      subtitle=project["subtitle"],
                      upload_date=project["upload_date"],
                      preview=project["preview"],
                      parody=project["parody"],
                      character=project["character"],
                      tag=project["tag"],
                      artist=project["artist"],
                      group=project["group"],
                      language=project["language"],
                      category=project["category"],
                      series=project["series"],
                      pages=project["pages"],
                      dir_name=project["dir_name"],
                      lib=project["lib"],
                      search_body=search_body
                      )

        session.add(row)
        session.commit()
