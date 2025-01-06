from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
from backend.db.connect import Project
from sqlalchemy.orm import sessionmaker, Session
import os
from backend import utils
from backend.classes.lib import Lib


class ProjectE(BaseModel):
    Session: sessionmaker[Session]
    lib_data: Lib

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

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.path = self.lib_data.path / self.dir_name
        files = os.listdir(self.path)

        self._update_preview_and_pages(files)
        self._gen_extra_parameters()

    def _update_preview_and_pages(self, files: list) -> None:
        preview_name: str = ""

        for file in files:
            if file.startswith("preview") or file.startswith("_preview"):
                preview_name = file
                break

        preview_name = preview_name if preview_name != "" else self.preview
        preview_path = self.path / preview_name

        exts = {".png", ".jpg", ".jpeg", ".gif", ".avif", ".webp",
                ".bmp", ".tif", ".tiff", ".apng",
                ".mng", ".flif", ".bpg", ".jxl", ".qoi", ".hif"}
        pages = len([file for file in files if os.path.splitext(file)[1] in exts])

        if preview_name != self.preview:
            preview_hash = utils.get_imagehash(preview_path)
            utils.update_vinfo(self.path, ["preview", "preview_hash"], [preview_name, preview_hash])

            with self.Session() as session:
                project = session.query(Project).filter_by(lid=self.lid).first()
                project.preview = preview_name
                project.preview_hash = preview_hash
                session.commit()

        if pages != self.pages:
            with self.Session() as session:
                project = session.query(Project).filter_by(lid=self.lid).first()
                project.pages = pages
                session.commit()

        self.preview = preview_name
        self.preview_path = preview_path
        self.pages = pages

    @staticmethod
    def _get_flags_paths(languages: list) -> list:
        exclude = ["rewrite", "translated"]

        flags_path = Path(os.getcwd()) / "data/flags"
        supports = os.listdir(flags_path)
        supports = [os.path.splitext(flag)[0] for flag in supports]
        flags = []

        for language in languages:
            language = language.lower()
            if language in supports:
                path = Path(os.getcwd()) / f"data/flags/{language}.svg"
                flags.append(path)
            else:
                if language not in exclude:
                    path = Path(os.getcwd()) / f"data/flags/unknown.png"
                    flags.append(path)
        return flags

    def _gen_extra_parameters(self) -> None:
        self.upload_date_str = self.upload_date.strftime("%Y-%m-%dT%H:%M:%S")
        self.variants_view = [variant.split(":")[1] for variant in self.lvariants]
        self.flags = self._get_flags_paths(self.language)
        self.lvariants_count = len(self.lvariants)







