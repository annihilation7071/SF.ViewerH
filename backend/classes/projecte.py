from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
from backend.db.connect import Project
from sqlalchemy.orm import sessionmaker, Session
import os
from backend import utils
from backend.classes.lib import Lib
import json
from backend.logger_new import get_logger

log = get_logger("ProjectE")


class DBError(Exception):
    pass


class ProjectEBase(BaseModel):
    _id: int | None = None
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

    class Config:
        arbitrary_types_allowed = True


class ProjectE(ProjectEBase):
    Session: sessionmaker[Session]
    lib_data: Lib

    path: Path = None
    preview_path: Path = None
    upload_date_str: str = None
    variants_view: list[str] = None
    flags: list[Path] = None
    lvariants_count: int = None

    class Config:
        arbitrary_types_allowed = True

    # noinspection PyPep8Naming,PyShadowingNames
    def __init__(self, Session, lib_data, **kwargs):
        log.debug("Initializing ProjectE")
        super().__init__(Session=Session, lib_data=lib_data, **kwargs)
        self.path = self.lib_data.path / self.dir_name
        files = os.listdir(self.path)

        self._update_preview_and_pages(files)
        self._gen_extra_parameters()

    def _update_preview_and_pages(self, files: list) -> None:
        log.debug("_update_preview_and_pages")
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
        log.debug("_get_flags_paths")
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
        log.debug("_gen_extra_parameters")
        self.upload_date_str = self.upload_date.strftime("%Y-%m-%dT%H:%M:%S")
        self.variants_view = [variant.split(":")[1] for variant in self.lvariants]
        self.flags = self._get_flags_paths(self.language)
        self.lvariants_count = len(self.lvariants)

    def _attr(self) -> list[str]:
        return [key for key in self.__dict__.keys() if key.startswith("_") is False]

    def _keys(self):
        return self._attr()

    def update_db(self) -> None:
        log.debug(f"update_db: {self.lid}")
        with Session() as session:
            project = session.query(Project).filter_by(lid=self.lid).first()
            keys_db = [key for key in project.__dict__.keys() if key.startswith("_") is False]
            keys_pe = self._attr()

            for key in keys_pe:
                if key in keys_db:
                    setattr(project, key, getattr(self, key))

            session.commit()

    def update_vinfo(self) -> None:
        log.debug(f"update_vinfo: {self.lid}")
        if self.lib.startswith("pool_"):
            raise Exception("Cannot update vinfo for pool")

        self._renew_search_body()

        keys_pe = self._attr()

        matches = {
            Path: lambda x: str(x),
            datetime: lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S"),
        }

        vpath = self.path / "sf.viewer/v_info.json"

        # Open
        with open(vpath, "r", encoding="utf-8") as f:
            v_info = json.load(f)

        # Update
        for key in keys_pe:
            if key in v_info:

                value = getattr(self, key)
                if type(value) in matches:
                    value = matches[type(value)](value)

                v_info[key] = value

        # Save
        with open(vpath, "w", encoding="utf-8") as f:
            # noinspection PyTypeChecker
            json.dump(v_info, f, indent=4)

    def add_to_db(self) -> None:
        log.debug("add_to_db")
        if self._id is not None:
            raise DBError("Cannot add project with specified _id in DB")

        self._renew_search_body()
        data = {key: getattr(self, key) for key in Project.get_columns() if key != "_id"}

        with self.Session() as session:
            project = Project(**data)
            session.add(project)
            session.commit()

    def _renew_search_body(self) -> None:
        log.debug("renew_search_body")
        self.search_body = make_search_body(self)

    def get_images(self) -> list[dict[str, Path | int]]:
        extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.avif', '.webp']

        files = os.listdir(self.path)

        pages = []

        for file in files:
            if os.path.splitext(file)[1] in extensions:
                pages.append(Path(self.path) / file)

        pages = sorted(pages, key=lambda x: str(x))
        pages = [{"idx": i, "path": pages[i]} for i in range(len(pages))]

        return pages


def make_search_body(project: dict | ProjectE | Project) -> str:
    include = ["source_id", "source", "url", "downloader", "title", "subtitle",
               "parody", "character", "tag", "artist", "group", "language",
               "category", "series", "lib"]

    search_body = ";;;"

    for k in include:
        if isinstance(project, dict):
            v = project[k]
        elif isinstance(project, ProjectE | Project):
            v = getattr(project, k)
        else:
            raise ValueError("Project must be of type dict or ProjectE")

        if isinstance(v, list):
            for item in v:
                search_body += f"{k}:{item.lower()};;;"
        else:
            search_body += f"{k}:{v};;;"

    return search_body
