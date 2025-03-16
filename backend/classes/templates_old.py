from sqlalchemy.orm import Session
from backend import dep
from typing import Any
from dateutil import parser
from pydantic import BaseModel, model_validator, ValidationInfo, field_validator
from datetime import datetime
from backend.utils import logger
from backend import utils
from pathlib import Path
from typing import TYPE_CHECKING, Annotated
from backend.classes.db import Project
import re

if TYPE_CHECKING:
    from backend.classes.projecte import ProjectDB, ProjectE

log = logger.get_logger("Classes.templates")


class ProjectTemplateError(Exception):
    pass


class ProjectTemplate(BaseModel):
    info_version: int = None
    lid: str = None
    lvariants: list[str] = None
    source_id: str = None
    source: str = None
    url: str = None
    downloader: str = None
    title: str = None
    subtitle: str = None
    upload_date: datetime = None
    preview: str = None
    parody: list[str] = None
    character: list[str] = None
    tag: list[str] = None
    artist: list[str] = None
    group: list[str] = None
    language: list[str] = None
    category: list[str] = None
    series: list[str] = None
    pages: int = None
    preview_hash: str = None
    episodes: list[str] = None

    class Config:
        arbitrary_types_allowed = True

    @field_validator("lvariants", mode="after")
    @classmethod
    def check_lvariants(cls, v: list[str], info: ValidationInfo) -> list[str]:
        for variant in v:
            if not re.fullmatch(r'^[a-zA-Z\d]*_[a-zA-Z\d]*:[^:]*($|:(p|P|priority))$', variant):
                raise ValueError("Incorrect variants")
        return v

    def attr(self) -> list[str]:
        return [key for key in self.__dict__.keys() if key.startswith("_") is False]

    def keys(self):
        return self.attr()

    @classmethod
    def load_from_json(cls, path: Path):
        log.debug("")
        jdata = utils.read_json(path)

        if isinstance(jdata["category"], str):
            jdata["category"] = [jdata["category"]]
            utils.write_json(path, jdata)

        jdata["upload date"] = parser.parse(jdata["upload_date"])
        model = cls(**jdata)
        # model.check_not_none()
        return model

    @classmethod
    def load_from_project(cls, project: Annotated['ProjectE', 'ProjectDB']):
        log.debug("")
        model = cls()
        for key in project.keys():
            if hasattr(model, key):
                setattr(model, key, project[key])
        model.check_not_none()
        return model

    def check_not_none(self):
        log.debug("")
        for key in self.keys():
            if getattr(self, key) is None:
                raise ProjectTemplateError(f"Attribute '{key}' is not defined")


class ProjectTemplateDB(ProjectTemplate):
    dir_name: str
    lib: str
    search_body: str = None
    active: bool = True
    upload_date: datetime = None

    class Config:
        arbitrary_types_allowed = True

    def model_post_init(self, __context: Any) -> None:
        self.search_body = utils.make_search_body(self)
        log.debug(self)

        self.check_not_none()

    def add_to_db(self, session: Session) -> None:
        log.debug(f"add_to_db: {self.lid}")
        log.info(f"Adding new project: {self.title}")

        try:
            project = Project(**self.model_dump())
            session.add(project)
        except Exception:
            session.rollback()
            log.exception("Error adding project")
            raise








