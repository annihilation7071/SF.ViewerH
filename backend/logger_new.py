import logging
import os
import threading
from logging.handlers import SocketHandler, RotatingFileHandler
from pathlib import Path
import sys
import asyncio

SOCKET_HANDLER = SocketHandler('127.0.0.1', 19996)
SOCKET_HANDLER.setLevel(logging.DEBUG)


def get_logger(name: str):
    if logging.Logger.manager.loggerDict.get(name):
        return logging.Logger.manager.loggerDict.get(name)

    formatter = logging.Formatter(f"%(asctime)s %(levelname)-8s: {name}: %(message)s")

    file_handler = RotatingFileHandler(filename=f"./logs/{name}.log", mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)

    # noinspection PyShadowingNames
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    log.addHandler(SOCKET_HANDLER)
    log.addHandler(file_handler)
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



