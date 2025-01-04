from sqlalchemy import Column, Integer, String, create_engine, DateTime, Boolean, JSON
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    def get_columns(self):
        # noinspection PyTypeChecker
        columns = [column.name for column in self.__table__.columns]
        return columns

    def to_dict(self) -> dict:
        project = {column: getattr(self, column) for column in self.get_columns()}
        return project


class Project(Base):
    __tablename__ = 'projects'
    _id = Column(Integer, primary_key=True, index=True)
    info_version = Column(Integer)
    lid = Column(String, unique=True, index=True)
    lvariants = Column(JSON)
    source_id = Column(String)
    source = Column(String)
    url = Column(String(length=500))
    downloader = Column(String)
    title = Column(String(length=500))
    subtitle = Column(String(length=500))
    upload_date = Column(DateTime)
    preview = Column(String(length=500))
    parody = Column(JSON)
    character = Column(JSON)
    tag = Column(JSON, index=True)
    artist = Column(JSON, index=True)
    group = Column(JSON)
    language = Column(JSON)
    category = Column(JSON)
    series = Column(JSON)
    pages = Column(Integer)
    dir_name = Column(String(length=500))
    lib = Column(String)
    search_body = Column(String(length=3000))
    active = Column(Boolean, default=True)
    preview_hash = Column(String(length=500))


# class PoolV(Base):
#     __tablename__ = 'pools_v'
#     _id = Column(Integer, primary_key=True)
#     pool_lid = Column(String)
#     updated_date = Column(DateTime)
#     project_lid = Column(String)


def get_session():
    engine = create_engine(f'sqlite:///data/DB/dbv2.db')
    Base.metadata.create_all(engine)

    # noinspection PyPep8Naming
    Session = sessionmaker(bind=engine)
    session = Session()

    return session
