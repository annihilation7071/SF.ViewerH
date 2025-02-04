import logging
import os
from logging.handlers import SocketHandler, RotatingFileHandler
from pathlib import Path
import shutil
from dataclasses import dataclass


@dataclass
class Settings:
    path: str = "./logs"

    filehandler_separated: bool = True
    filehandler_separated_level: int = logging.DEBUG

    filehandler_all: bool = True
    filehandler_all_level: int = logging.DEBUG

    streamhandler: bool = True
    streamhandler_level: int = logging.INFO

    sockethandler: bool = True
    sockethandler_settings: str = '127.0.0.1:19996'
    sockethandler_level: int = logging.DEBUG


settings = Settings()

__init = False
__path: Path | None = None
__socket_handler: logging.Handler | None = None


def init():
    global __path
    global __socket_handler
    global __init

    if settings.filehandler_separated or settings.filehandler_all:
        __path = Path(settings.path)
        Path(__path).mkdir(parents=True, exist_ok=True)
        files = os.listdir(__path)

        for file in files:
            if file != ".gitkeep":
                try:
                    shutil.rmtree(__path / file, ignore_errors=True)
                except:
                    os.remove(__path / file)

    if settings.sockethandler:
        ip = settings.sockethandler_settings.split(":")[0]
        port = int(settings.sockethandler_settings.split(":")[1])
        __socket_handler = SocketHandler(ip, port)
        __socket_handler.setLevel(settings.sockethandler_level)

    __init = True


def get_logger(name: str) -> logging.Logger:
    if not __init:
        init()

    if logging.Logger.manager.loggerDict.get(name):
        return logging.Logger.manager.loggerDict.get(name)

    formatter = logging.Formatter(f"%(asctime)s %(levelname)-8s: {name}: %(message)s")

    # noinspection PyShadowingNames
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    if settings.sockethandler:
        log.addHandler(__socket_handler)

    if settings.filehandler_separated:
        path = __path / f"{name}.log"
        file_handler = RotatingFileHandler(filename=path, mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(settings.filehandler_separated_level)
        log.addHandler(file_handler)

    if settings.filehandler_all:
        path = __path / f"All.log"
        file_handler_all = RotatingFileHandler(filename=path, mode="a", encoding="utf-8")
        file_handler_all.setFormatter(formatter)
        file_handler_all.setLevel(settings.filehandler_all_level)
        log.addHandler(file_handler_all)

    if settings.streamhandler:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(settings.streamhandler_level)
        log.addHandler(stream_handler)

    return log


# def log_exception(exc_type, exc_value, exc_tb):
#     # noinspection PyShadowingNames
#     log = logger.get_logger("General")
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


# if __name__ == '__main__':
#     os.chdir(Path(os.getcwd()).parent)
#
#     log = get_logger("Root logger")
#
#     log.debug("A DEBUG Message")
#     log.info("An INFO")
#     log.warning("A WARNING")
#     log.error("An ERROR")
#     log.critical("A message of CRITICAL severity")
#
#     try:
#         x = 5/0
#     except ZeroDivisionError:
#         log.exception("An exception occurred")
#         raise



