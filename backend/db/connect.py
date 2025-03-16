from backend.main_import import *
from backend.utils import *
from backend.db import Project

log = logger.get_logger("DB")


def get_session():
    engine = create_engine(
        'sqlite:///data/DB/dbv4.db',
        connect_args={'check_same_thread': False}
    )

    SQLModel.metadata.create_all(engine)

    # noinspection PyPep8Naming,PyShadowingNames
    Session = scoped_session(sessionmaker(bind=engine))

    return Session

