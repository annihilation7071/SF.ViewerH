import logging
import os
from logging.handlers import SocketHandler, RotatingFileHandler
from pathlib import Path

socket_handler = SocketHandler('127.0.0.1', 19996)
socket_handler.setLevel(logging.DEBUG)


def get_logger(name: str) -> logging.Logger:
    if logging.Logger.manager.loggerDict.get(name):
        return logging.Logger.manager.loggerDict.get(name)

    formatter = logging.Formatter(f"%(asctime)s %(levelname)-8s: {name}: %(message)s")

    file_handler = RotatingFileHandler(filename=f"./logs/{name}.log", mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    file_handler_2 = RotatingFileHandler(filename=f"./logs/All.log", mode="w", encoding="utf-8")
    file_handler_2.setFormatter(formatter)
    file_handler_2.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)

    # noinspection PyShadowingNames
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    log.addHandler(socket_handler)
    log.addHandler(file_handler)
    log.addHandler(file_handler_2)
    log.addHandler(stream_handler)

    return log


# def log_exception(exc_type, exc_value, exc_tb):
#     # noinspection PyShadowingNames
#     log = get_logger("General")
#
#     log.error("Exception", exc_info=(exc_type, exc_value, exc_tb))
#
#
# def thread_exceprion_hook(args):
#     log_exception(args.exc_type, args.exc_value, args.exc_traceback)
#
#
# def handle_async_exception(loop, context):
#     exc = context.get('exception')
#     if exc:
#         log_exception(type(exc), exc, exc.__traceback__)
#     else:
#         log.exception(f"Async exception: {context['message']}")


if __name__ == '__main__':
    os.chdir(Path(os.getcwd()).parent)

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



