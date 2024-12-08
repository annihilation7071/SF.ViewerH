import json
import os
from datetime import datetime
from backend import cmdargs
from backend.projects import Projects

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
    dirs_not_exist = dirs_in_db - exist_dirs

    return dirs_not_in_db, dirs_not_exist


def tag_normalizer(tags: str | list | int):
    if isinstance(tags, int):
        return tags

    with open('./data/aliases.json', 'r') as f:
        aliases = json.load(f)

    def normalize(tag: str):
        new_tag = tag.lower()
        new_tag = new_tag.replace("♀", "")
        new_tag = new_tag.replace("♂", "")
        new_tag = new_tag.replace("\r", "")
        new_tag = new_tag.replace("\n", "")
        new_tag = new_tag.strip()
        if new_tag in aliases:
            return aliases[new_tag]
        else:
            return new_tag

    if isinstance(tags, str):
        return normalize(tags)
    elif isinstance(tags, list):
        new_tags = []
        for tag in tags:
            new_tags.append(normalize(tag))
        return new_tags


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


def get_projects(lib_name: str, lib_data: dict, meta_file: str, processor) -> list:

    path = lib_data["path"]
    dirs = get_dirs(path, meta_file)

    dirs_not_in_db, dirs_not_exist = check_dirs(lib_name, dirs)

    for dir in dirs_not_exist:
        projects.delete_by_dir_and_lib(dir, lib_name)

    for dir in dirs_not_in_db:
        project = processor(os.path.join(path, dir), lib_name, lib_data)
        projects.add_project(project)


def get_v_info(path: str) -> dict | bool:
    with open('./backend/v_info.json', 'r', encoding='utf-8') as f:
        v_info = json.load(f)

    if os.path.exists(os.path.join(path, "./sf.viewer/v_info.json")):
        with open(os.path.join(path, "./sf.viewer/v_info.json"), "r", encoding='utf-8') as f:
            v_info_exist = json.load(f)

        if v_info_exist["info_version"] == v_info["info_version"]:
            return v_info_exist
        else:
            raise IOError("v_info version is not corrected")

    else:
        return False

