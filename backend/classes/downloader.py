from pydantic import BaseModel
from datetime import datetime


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
    dir_name: str = None
    lib: str = None
    search_body: str = None
    active: bool = None
    preview_hash: str = None

    class Config:
        arbitrary_types_allowed = True