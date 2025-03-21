from backend.modules import *


class SQLModel(SQLModel):
    class Config:
        validate_assignment = True
        allow_arbitrary_types = False


class BaseModel(BaseModel):
    class Config:
        validate_assignment = True
        allow_arbitrary_types = False


from backend import logger
from backend.filesession import FileSession, FSession
from backend.utils import *
from backend.cmdargs import cmdargs
from backend import dep
from backend.classes import Lib
from backend.db import connect
from backend.db import PoolVariantBase, PoolVariant
from backend.user_data import Variants
from backend.db import Project, ProjectBase
from backend.db import DBMetadata
from backend.projects.projects import Projects




