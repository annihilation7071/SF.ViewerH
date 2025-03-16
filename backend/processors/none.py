from backend.main_import import *
from backend.utils import *
from backend.db import ProjectBase
from backend import logger

log = logger.get_logger("Processor.none")


def parse(path: Path, template: ProjectBase) -> ProjectBase:
    return template
