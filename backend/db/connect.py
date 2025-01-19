from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from backend.modules import logger
from backend.classes.db import Base

log = logger.get_logger("DB")


def get_session():
    engine = create_engine(
        f'sqlite:///data/DB/dbv4.db',
        connect_args={'check_same_thread': False}
    )
    Base.metadata.create_all(engine)

    # noinspection PyPep8Naming
    Session = scoped_session(sessionmaker(bind=engine))

    return Session