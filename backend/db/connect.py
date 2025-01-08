from sqlalchemy import Column, Integer, String, create_engine, DateTime, Boolean, JSON
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from backend.logger_new import get_logger
from backend.db import classes

log = get_logger("Connect")


def get_session():
    engine = create_engine(
        f'sqlite:///data/DB/dbv2.db',
        connect_args={'check_same_thread': False}
    )
    classes.Base.metadata.create_all(engine)

    # noinspection PyPep8Naming
    Session = sessionmaker(bind=engine)

    return Session