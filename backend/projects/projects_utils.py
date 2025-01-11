from backend import dep
from pathlib import Path
import os
from importlib import import_module
from backend import utils, cmdargs
from backend import logger
from backend.upgrade import vinfo
from backend.processors import general as general
import json
from dateutil import parser
from sqlalchemy.orm import Session
from backend.classes.templates import ProjectTemplate, ProjectTemplateDB
from backend.classes.files import ProjectInfoFile
from backend.classes.db import Project
from backend.classes.lib import Lib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.projects.projects import Projects

log = logger.get_logger("Projects.updater")


def update_projects(session: Session) -> None:
    log.debug("update_projects")
    log.info("Updating projects ...")

    if cmdargs.args.reindex is True:
        log.warning(f"Deleting all data...")
        cmdargs.args.reindex = False
        dep.projects.delete_all_data_(session)

    for lib in dep.libs.values():
        if lib.active is False:
            continue

        processor_name = lib.processor

        log.info(f"Checking {lib.name} ...")

        with open("./backend/v_info.json", "r", encoding="utf-8") as f:
            v_info_example = json.load(f)

        dep.projects.clear_old_versions_(session, v_info_example["info_version"])

        processor = import_module(f"backend.processors.{lib.processor}")

        path = lib.path
        log.debug(f"Lib path: {path}")
        dirs = get_dirs(path, processor.meta_file)
        log.debug(f"Dirs in lib path: {dirs}")

        dirs_not_in_db, dirs_not_exist = check_dirs(session, lib, dirs)
        log.debug(f"dirs_not_in_db: {len(dirs_not_in_db)}")
        log.debug(dirs_not_in_db)
        log.debug(f"dirs_not_exist: {len(dirs_not_exist)}")
        log.debug(dirs_not_exist)

        for dir in dirs_not_exist:
            log.info(f"Deleting not exist projects...")
            log.debug(f"Deleting {dir} ...")
            dep.projects.delete_by_dir_and_lib_(session, dir, lib)

        if len(dirs_not_in_db) > 0:
            log.info(f"Adding new projects...")

        for dir_name in dirs_not_in_db:
            project_path = path / dir_name
            add_project_dir_to_db(session, lib, project_path, processor_name)


def add_project_dir_to_db(session: Session, lib: Lib, project_path: Path, processor_name: str) -> None:
    log.debug(f"Adding {project_path.name} ...")

    project = get_project_info(project_path)
    if project is None:
        log.debug(f"vinfo for {project_path.name} not found...")
        log.info(f"Preparing project {project_path.name} ...")
        general.make_v_info(project_path, processor_name)
        project = get_project_info(project_path)

    project_to_db = ProjectTemplateDB(
        lib=lib.name,
        dir_name=project_path.name,
        **project.model_dump()
    )

    log.debug(project_to_db)

    project_to_db.add_to_db(session)


def get_dirs(path: Path, meta_file: str) -> list[str]:
    log.debug("get_dirs")
    dirs = []
    if os.path.exists(path) is False:
        os.makedirs(path)
    files = os.listdir(path)
    for file in files:
        if os.path.exists(os.path.join(path, file) + f"/{meta_file}"):
            dirs.append(file)
    return dirs


def check_dirs(session: Session, lib: Lib, dirs: list[str]) -> tuple:
    log.debug("check_dirs")
    exist_dirs = set(dirs)

    dirs_in_db = set(dep.projects.get_dirs_(session, lib.name))

    log.debug(f"dirs found in db: {dirs_in_db}")

    dirs_not_in_db = exist_dirs - dirs_in_db

    dirs_not_exist = dirs_in_db - exist_dirs

    return dirs_not_in_db, dirs_not_exist


def get_project_info(path: Path) -> ProjectTemplate | None:
    log.debug("get_v_info")
    with open('./backend/v_info.json', 'r', encoding='utf-8') as f:
        v_info_example = json.load(f)

    v_info_path = path / "sf.viewer/v_info.json"

    if os.path.exists(v_info_path):

        project_infofile = ProjectInfoFile(path=v_info_path)

        project_info = project_infofile.data

        if project_info.info_version == v_info_example["info_version"]:
            return project_info
        else:
            project_info = vinfo.upgrade(path, project_info)

            project_infofile.set(project_info)
            project_infofile.commit()

            return get_project_info(path)

    else:
        return None
