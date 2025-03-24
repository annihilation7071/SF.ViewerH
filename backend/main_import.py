from backend.modules import *


class SQLModel(SQLModel):
    class Config:
        validate_assignment = True
        allow_arbitrary_types = False


class BaseModel(BaseModel):
    class Config:
        validate_assignment = True
        allow_arbitrary_types = False


from backend import validators
from backend import base_config
from backend.settings import config
from backend import logger
from backend.filesession import FileSession, FSession
from backend.utils import *
from backend.cmdargs import cmdargs
from backend import dep
from backend.user_data import Lib, Libs
from backend.user_data import DownloadersSettings, BaseDownloaderSettings
from backend.user_data import DownloadersTargets, DownloaderTarget
from backend.db import connect
from backend.db import PoolVariantBase, PoolVariant
from backend.user_data import Variants
from backend.db import Project, ProjectBase
from backend.db import DBMetadata
from backend.projects.projects import Projects




