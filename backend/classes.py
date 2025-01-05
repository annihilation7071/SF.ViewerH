from datetime import datetime
from pathlib import Path
from pydantic import BaseModel


class ProjectE(BaseModel):
    _id: int
    info_version: int
    lid: str
    lvariants: list[str]
    source_id: str
    source: str
    url: str
    downloader: str
    title: str
    subtitle: str
    upload_date: datetime
    preview: str
    parody: list[str]
    character: list[str]
    tag: list[str]
    artist: list[str]
    group: list[str]
    language: list[str]
    category: list[str]
    series: list[str]
    pages: int
    dir_name: str
    lib: str
    search_body: str
    active: bool
    preview_hash: str

    path: Path = None
    preview_path: Path = None
    upload_date_str: str = None
    variants_view: list[str] = None
    flags: list[Path] = None
    lvariants_count: int = None