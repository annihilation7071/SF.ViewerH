import logging
from logging.handlers import SocketHandler, RotatingFileHandler

SOCKET_HANDLER = SocketHandler('127.0.0.1', 19996)


def get_logger(name: str, level: int = 1) -> logging.Logger:
    file_handler = RotatingFileHandler(filename=f"./logs/{name}.log", mode="w", encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_handler.setFormatter(formatter)

    # noinspection PyShadowingNames
    log = logging.getLogger(name)
    log.setLevel(level)
    log.addHandler(SOCKET_HANDLER)
    log.addHandler(file_handler)
    return log


if __name__ == '__main__':
    log = get_logger("Root logger")

    log.debug("A DEBUG Message")
    log.info("An INFO")
    log.warning("A WARNING")
    log.error("An ERROR")
    log.critical("A message of CRITICAL severity")

    try:
        x = 5/0
    except ZeroDivisionError:
        log.exception("An exception occurred")
        raise



