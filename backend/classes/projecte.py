from backend import dep
from datetime import datetime
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field
from backend.classes.db import Project
import os
from backend.classes.lib import Lib
from backend.classes.files import ProjectInfoFile, ProjectInfoFileError
import json
from backend.logger_new import get_logger
from backend import utils
from sqlalchemy.orm import Session

log = get_logger("ProjectE")


class DBError(Exception):
    pass


class DBErrorPoolHasNotDir(DBError):
    pass


class ProjectDB(BaseModel):
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

    def attr(self) -> list[str]:
        return [key for key in self.__dict__.keys() if key.startswith("_") is False]

    def keys(self):
        return self.attr()


class ProjectE(ProjectDB):
    lib_data: Lib

    path: Path = None
    preview_path: Path = None
    upload_date_str: str = None
    variants_view: list[str] = None
    flags: list[Path] = None
    lvariants_count: int = None

    class Config:
        arbitrary_types_allowed = True

    def __new__(cls, *args, **kwargs):
        log.debug(args)
        log.debug(kwargs)
        if kwargs["lid"].startswith("pool_") and "pool_mark" not in kwargs:
            log.debug("Returning ProjectEPool object instead ProjectE")
            return ProjectEPool(*args, **kwargs)
        else:
            kw = dict(kwargs)
            kw.pop("pool_mark", None)
            return super().__new__(cls)

    def model_post_init(self, __context: Any) -> None:
        log.debug(f"Initializing {type(self).__name__}")
        self.path = self.lib_data.path / self.dir_name
        files = os.listdir(self.path)

        self._update_preview_and_pages(files)
        self._gen_extra_parameters()

        log.debug(self)

        # with dep.Session() as session:
        #     log.warning(session)
        #     project = session.query(Project).filter_by(_id=1).first()
        #     log.warning(project)

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

            with dep.Session() as session:
                project = session.query(Project).filter_by(lid=self.lid).first()
                project.preview = preview_name
                project.preview_hash = preview_hash
                session.commit()

        if pages != self.pages:
            with dep.Session() as session:
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

    def update_db(self, session: Session, commit: bool = False) -> None:
        log.debug(f"_update_db: {self.lid}")
        self._renew_search_body()

        project = session.query(Project).filter_by(lid=self.lid).first()
        keys_db = project.get_columns()

        for key in self.keys():
            if key in keys_db:
                setattr(project, key, getattr(self, key))

        if commit:
            session.commit()

    def update_vinfo(self) -> None | ProjectInfoFile:
        log.debug(f"_update_vinfo: {self.lid}")
        log.debug(f"_update_vinfo: {self.path}")
        self._renew_search_body()

        if self.lib.startswith("pool_"):
            raise DBError("Cannot update vinfo for pool")

        vpath = self.path / "sf.viewer/v_info.json"

        # Open
        infofile = ProjectInfoFile(path=vpath)
        v_info = infofile.data

        log.debug(f"v_info: {v_info}")

        infofile.save_model("backup")

        try:
            for key in self.keys():
                if hasattr(v_info, key):
                    setattr(v_info, key, getattr(self, key))

            log.debug(f"v_info: {v_info}")

            # Save
            infofile.set(v_info)
            infofile.commit()
            return infofile

        except Exception as e:
            log.exception(str(e))
            raise e

    def soft_update(self, session: Session, only_db: bool = False) -> None:
        log.debug(f"soft_update")
        log.info(f"Updating project: {self.title}")

        try:
            self.update_db(session)
        except Exception as e:
            session.rollback()
            log.exception(f"Failed to update project: {self.title}")
            raise e

        if only_db:
            log.debug(f"vinfo file will not be updated: {self.lid} than flag only_db is True")
            return

        try:
            self.update_vinfo()
        except DBErrorPoolHasNotDir as e:
            log.debug("Updating pool; v_info file will not be updated", exc_info=e)
        except Exception as e:
            session.rollback()
            log.exception(f"Failed to update project: {self.title}")
            raise e

        log.info(f"Update completed: {self.title}")

    def update(self, only_db: bool = False) -> None:
        log.debug(f"update: {self.lid}")

        with dep.Session() as session:
            self.soft_update(session, only_db=only_db)
            session.commit()
            log.info(f"Update commited: {self.title}")

    # def add_to_db(self) -> None:
    #     log.debug("add_to_db")
    #     if self._id is not None:
    #         raise DBError("Cannot add project with specified _id in DB")
    #
    #     self._renew_search_body()
    #     data = {key: getattr(self, key) for key in Project.get_columns(exclude=["_id"])}
    #
    #     with dep.Session() as session:
    #         project = Project(**data)
    #         session.add(project)
    #         session.commit()

    def _renew_search_body(self) -> None:
        log.debug("renew_search_body")
        self.search_body = utils.make_search_body(self)

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


# noinspection PyDataclass
class Template(BaseModel):
    tag: list[str] = Field(default_factory=list)
    language: list[str] = Field(default_factory=list)
    group: list[str] = Field(default_factory=list)
    artist: list[str] = Field(default_factory=list)
    series: list[str] = Field(default_factory=list)
    parody: list[str] = Field(default_factory=list)


class ProjectEPool(ProjectE):
    def __new__(cls, *args, **kwargs):
        kw = dict(kwargs)
        kw["pool_mark"] = True
        return super().__new__(cls, *args, **kw)

    def update_pool(self):

        template = Template()

        for variant in self.lvariants:
            lid = variant.split(":")[0]
            project = dep.projects.get_project_by_lid(lid)

            template.tag = list(set(template.tag) | set(project.tag))
            template.language = list(set(template.language) | set(project.language))
            template.group = list(set(template.group) | set(project.group))
            template.artist = list(set(template.artist) | set(project.artist))
            template.series = list(set(template.series) | set(project.series))
            template.parody = list(set(template.parody) | set(project.parody))

        for key in template.model_dump().keys():
            setattr(self, key, getattr(template, key))

        self.update()
