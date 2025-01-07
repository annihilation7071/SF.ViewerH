from typing import Any

from pydantic import BaseModel
from datetime import datetime
from backend.logger_new import get_logger

log = get_logger("templates")


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
    upload_date: str | datetime = None
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

    class Config:
        arbitrary_types_allowed = True

    def _attr(self) -> list[str]:
        return [key for key in self.__dict__.keys() if key.startswith("_") is False]

    def _keys(self):
        return self._attr()


class ProjectTemplateDB(ProjectTemplate):
    dir_name: str
    lib: str
    search_body: str
    active: bool = True

    class Config:
        arbitrary_types_allowed = True

    def model_post_init(self, __context: Any) -> None:
        self.upload_date = datetime.strptime(self.upload_date, "%Y-%m-%dT%H:%M:%S")

        keys = self._keys()
        for key in keys:
            if getattr(self, key) is None:
                raise ProjectTemplateError(f"Attribute `{key}` is not defined")



