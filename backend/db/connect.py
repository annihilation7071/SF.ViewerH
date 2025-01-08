from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from backend.logger_new import get_logger
from backend.classes.db import Base

log = get_logger("Connect")


def get_session():
    engine = create_engine(
        f'sqlite:///data/DB/dbv2.db',
        connect_args={'check_same_thread': False}
    )
    Base.metadata.create_all(engine)

    # noinspection PyPep8Naming
    Session = scoped_session(sessionmaker(bind=engine))

    return Session