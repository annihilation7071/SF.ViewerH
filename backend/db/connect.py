from backend.main_import import *
from .project import Project
from .pool_variants import PoolVariant

log = logger.get_logger("DB")


db_version = dep.DB_VERSION


def get_session():
    engine = create_engine(
        f'sqlite:///data/DB/dbv{db_version}.db',
        connect_args={'check_same_thread': False}
    )

    SQLModel.metadata.create_all(engine)

    # noinspection PyPep8Naming,PyShadowingNames
    Session = sessionmaker(bind=engine)

    return Session

