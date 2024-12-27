from pathlib import Path
import os
from importlib import import_module
from icecream import ic
from datetime import datetime
from backend import utils, cmdargs
from backend.logger import log
from backend.projects.cls import Projects
from backend.upgrade import vinfo
import json


def update_projects(projects: Projects) -> None:
    libs = utils.read_libs()

    for lib_name, lib_data in libs.items():
        if lib_data["active"] is False:
            continue

        log(f"Processing: {lib_name}")
        if cmdargs.args.reindex is True:
            cmdargs.args.reindex = False
            projects.delete_all_data()
            log(f"Deleted all data")

        with open("./backend/v_info.json", "r", encoding="utf-8") as f:
            v_info = json.load(f)

        projects.clear_old_versions(v_info["info_version"])

        processor = import_module(f"backend.processors.{lib_data['processor']}")

        path = lib_data["path"]
        dirs = get_dirs(path, processor.meta_file)

        dirs_not_in_db, dirs_not_exist = check_dirs(projects, lib_name, dirs)

        for dir in dirs_not_exist:
            log(f"Dir not exist: {dir}", "check-dirs")
            projects.delete_by_dir_and_lib(dir, lib_name)

        for dir in dirs_not_in_db:
            project_path = str(os.path.join(path, dir))

            if cmdargs.args.rewrite_v_info is True:
                processor.make_v_info(project_path)

            project = get_v_info(project_path)
            if project is None:
                processor.make_v_info(project_path)
                utils.update_vinfo(project_path, ["info_version"], [2])
                vinfo.upgrade(project_path)
                project = get_v_info(project_path)

            project["lib"] = lib_name
            project["dir_name"] = dir
            project["upload_date"] = datetime.strptime(project["upload_date"], "%Y-%m-%dT%H:%M:%S")
            projects.add_project(project)


def get_dirs(path: str, meta_file: str) -> list[str]:
    dirs = []
    if os.path.exists(path) is False:
        os.makedirs(path)
    files = os.listdir(path)
    for file in files:
        if os.path.exists(os.path.join(path, file) + f"/{meta_file}"):
            dirs.append(file)
    return dirs


def check_dirs(projects: Projects, lib_name: str, dirs: list[str]) -> tuple:
    exist_dirs = set(dirs)
    dirs_in_db = set(projects.get_dirs(lib_name))

    dirs_not_in_db = exist_dirs - dirs_in_db
    log(f"Directories not in DB: {len(dirs_not_in_db)}")
    dirs_not_exist = dirs_in_db - exist_dirs
    log(f"Directories in DB but not exist: {len(dirs_not_exist)}")

    return dirs_not_in_db, dirs_not_exist


def get_v_info(path: str | Path) -> dict | None:
    ic(f"Getting vinfo from {path}")
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