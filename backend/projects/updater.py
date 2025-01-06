from pathlib import Path
import os
from importlib import import_module
from datetime import datetime
from backend import utils, cmdargs
from backend.logger_new import get_logger
from backend.projects.cls import Projects
from backend.upgrade import vinfo
import json
from pydantic import BaseModel
from backend.classes.projecte import ProjectEBase

log = get_logger("putils")


def update_projects(projects: Projects) -> None:
    log.debug("update_projects")
    log.info("Updating projects ...")
    libs = utils.read_libs()

    for lib_name, lib_data in libs.items():
        if lib_data.active is False:
            continue

        log.info(f"Checking {lib_name} ...")
        if cmdargs.args.reindex is True:
            log.warning(f"Deleting all data...")
            cmdargs.args.reindex = False
            projects.delete_all_data()

        with open("./backend/v_info.json", "r", encoding="utf-8") as f:
            v_info = json.load(f)

        projects.clear_old_versions(v_info["info_version"])

        processor = import_module(f"backend.processors.{lib_data.processor}")

        path = lib_data.path
        log.debug(f"Lib path: {path}")
        dirs = get_dirs(path, processor.meta_file)

        dirs_not_in_db, dirs_not_exist = check_dirs(projects, lib_name, dirs)
        log.debug(f"dirs_not_in_db: {len(dirs_not_in_db)}")
        log.debug(f"dirs_not_exist: {len(dirs_not_exist)}")

        if len(dirs_not_exist) > 0:
            log.info(f"Deleting not exist projects...")

        for dir in dirs_not_exist:
            log.debug(f"Deleting {dir} ...")
            projects.delete_by_dir_and_lib(dir, lib_name)

        if len(dirs_not_in_db) > 0:
            log.info(f"Adding new projects...")

        for dir in dirs_not_in_db:
            log.debug(f"Adding {dir} ...")
            project_path = path / dir

            if cmdargs.args.rewrite_v_info is True:
                log.warning(f"Rewriting vinfo {dir}...")
                processor.make_v_info(project_path)

            project = get_v_info(project_path)
            if project is None:
                log.debug(f"vinfo for {dir} not found...")
                log.info(f"Preparing project {dir}...")
                processor.make_v_info(project_path)
                utils.update_vinfo(project_path, ["info_version"], [2])
                vinfo.upgrade(project_path)
                project = get_v_info(project_path)

            project["lib"] = lib_name
            project["dir_name"] = dir
            project["upload_date"] = datetime.strptime(project["upload_date"], "%Y-%m-%dT%H:%M:%S")
            projects.add_project(project)


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


def check_dirs(projects: Projects, lib_name: str, dirs: list[str]) -> tuple:
    log.debug("check_dirs")
    exist_dirs = set(dirs)
    dirs_in_db = set(projects.get_dirs(lib_name))

    dirs_not_in_db = exist_dirs - dirs_in_db

    dirs_not_exist = dirs_in_db - exist_dirs

    return dirs_not_in_db, dirs_not_exist


def get_v_info(path: str | Path) -> dict | None:
    log.debug("get_v_info")
    with open('./backend/v_info.json', 'r', encoding='utf-8') as f:
        v_info = json.load(f)

    if os.path.exists(os.path.join(path, "sf.viewer/v_info.json")):
        with open(os.path.join(path, "sf.viewer/v_info.json"), "r", encoding='utf-8') as f:
            v_info_exist = json.load(f)

        if v_info_exist["info_version"] == v_info["info_version"]:
            return v_info_exist
        else:
            vinfo.upgrade(path)
            return get_v_info(path)

    else:
        return None
