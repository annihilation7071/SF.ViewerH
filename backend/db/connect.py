from sqlalchemy import Column, Integer, String, create_engine, DateTime, Boolean, JSON
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from backend.logger_new import get_logger

log = get_logger("Connect")


class Base(DeclarativeBase):
    def get_columns(self):
        log.debug(f"Base.get_columns")
        # noinspection PyTypeChecker
        columns = [column.name for column in self.__table__.columns]
        log.debug(f"columns")
        return columns

    def to_dict(self, exclude: list = None) -> dict:
        if exclude is None:
            exclude = []
        project = {column: getattr(self, column) for column in self.get_columns() if column not in exclude}
        return project


class Project(Base):
    __tablename__ = 'projects'
    _id = Column(Integer, primary_key=True, index=True, nullable=False)
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

    @classmethod
    def get_columns(cls, exclude: list = None) -> list:
        log.debug(f"Project.get_columns")
        if exclude is None:
            exclude = []
        columns = [column.name for column in cls.__table__.columns if column not in exclude]
        return columns


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

    return Session
