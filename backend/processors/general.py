import json
import os
from datetime import datetime
from backend import cmdargs, logger, utils
from backend.projects import Projects
from importlib import import_module

projects = Projects()


def get_dirs(path: str, meta_file: str) -> list[str]:
    dirs = []
    if os.path.exists(path) is False:
        os.makedirs(path)
    files = os.listdir(path)
    for file in files:
        if os.path.exists(os.path.join(path, file) + f"/{meta_file}"):
            dirs.append(file)
    return dirs


def check_dirs(lib_name: str, dirs: list[str]) -> tuple:
    exist_dirs = set(dirs)
    dirs_in_db = set(projects.get_dirs(lib_name))

    dirs_not_in_db = exist_dirs - dirs_in_db
    logger.log(f"Directories not in DB: {len(dirs_not_in_db)}")
    dirs_not_exist = dirs_in_db - exist_dirs
    logger.log(f"Directories in DB but not exist: {len(dirs_not_exist)}")

    return dirs_not_in_db, dirs_not_exist


def get_time(str_time: str | int, format: str = None) -> str | bool:
    if isinstance(str_time, str) and format is None:
        raise IOError("Format must be specified")

    target_format = "%Y-%m-%dT%H:%M:%S"

    if isinstance(str_time, str):
        try:
            date = datetime.strptime(str_time, format)
            return date.strftime(target_format)
        except Exception as e:
            print(e)
            return False
    elif isinstance(str_time, int):
        date = datetime.fromtimestamp(1566440093)
        return date.strftime(target_format)


def get_projects() -> None:
    libs = utils.read_libs()

    for lib_name, lib_data in libs.items():
        if lib_data["active"] is False:
            continue

        logger.log(f"Processing: {lib_name}")
        if cmdargs.args.reindex is True:
            cmdargs.args.reindex = False
            projects.delete_all_data()
            logger.log(f"Deleted all data")

        with open("./backend/v_info.json", "r", encoding="utf-8") as f:
            v_info = json.load(f)

        projects.clear_old_versions(v_info["info_version"])

        processor = import_module(f"backend.processors.{lib_data['processor']}")

        path = lib_data["path"]
        dirs = get_dirs(path, processor.meta_file)

        dirs_not_in_db, dirs_not_exist = check_dirs(lib_name, dirs)

        for dir in dirs_not_exist:
            projects.delete_by_dir_and_lib(dir, lib_name)

        for dir in dirs_not_in_db:
            project_path = str(os.path.join(path, dir))

            if cmdargs.args.rewrite_v_info is True:
                processor.make_v_info(project_path)

            project = get_v_info(project_path)
            if project is None:
                processor.make_v_info(project_path)
                project = get_v_info(project_path)

            project["lib"] = lib_name
            project["dir_name"] = dir
            projects.add_project(project)


def get_v_info(path: str) -> dict | None:
    with open('./backend/v_info.json', 'r', encoding='utf-8') as f:
        v_info = json.load(f)

    print(os.path.join(path, "./sf.viewer/v_info.json"))

    if os.path.exists(os.path.join(path, "./sf.viewer/v_info.json")):
        with open(os.path.join(path, "./sf.viewer/v_info.json"), "r", encoding='utf-8') as f:
            v_info_exist = json.load(f)

        if v_info_exist["info_version"] == v_info["info_version"]:
            return v_info_exist
        else:
            raise IOError("v_info version is not corrected")

    else:
        return None

