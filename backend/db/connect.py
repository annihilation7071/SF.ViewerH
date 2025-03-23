import sqlmodel

from backend.main_import import *
from .project import Project
from .pool_variants import PoolVariant
from .metadata import DBMetadata

log = logger.get_logger("DB")


db_version = base_config.DB_VERSION


def get_session():
    engine = create_engine(
        f'sqlite:///data/DB/dbv{db_version}.db',
        connect_args={'check_same_thread': False}
    )

    SQLModel.metadata.create_all(engine)

    # noinspection PyPep8Naming,PyShadowingNames
    Session = sessionmaker(bind=engine,
                           class_=sqlmodel.Session)

    return Session

