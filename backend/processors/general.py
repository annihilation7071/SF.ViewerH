import json
import os
from datetime import datetime


def get_dirs(path: str, meta_file: str) -> list[str]:
    dirs = []
    if os.path.exists(path) is False:
        os.makedirs(path)
    files = os.listdir(path)
    for file in files:
        if os.path.exists(os.path.join(path, file) + f"/{meta_file}"):
            dirs.append(file)
    return dirs


def get_index(index_path: str, dirs: list[str]) -> bool | dict:

    with open(index_path, "r", encoding="utf-8") as f:
        index = json.load(f)

    if len(index["projects"]) != len(dirs):
        return False

    for directory in dirs:
        if directory not in index["projects"]:
            return False

    return index


def write_index(index_path: str, projects: list) -> None:

    index = {"info_version": projects[0]["info_version"],
             "projects": {project["dir_name"]: project for project in projects}}

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=4)


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
    projects = []
    dirs = get_dirs(path, meta_file)

    index_path = f"./data/index/{lib_name}.json"

    if os.path.exists(index_path):
        print(f"Index file for {lib_name}: exist")
        index = get_index(index_path, dirs)
        if index is not False:

            with open("./backend/v_info.json", "r", encoding="utf-8") as f:
                current_info_version = json.load(f)["info_version"]

            if index["info_version"] != current_info_version:
                print(f"Index file for {lib_name}: INCORRECT VERSION")
            else:
                projects = list(index["projects"].values())
                print(f"Index file for {lib_name}: correct\n"
                      f"Using existing index file for {lib_name}")
                return projects
        else:
            print(f"Index file for {lib_name}: INCORRECT")

    print(f"Creating index file for {lib_name}")
    percent = 0

    for i in range(0, len(dirs)):

        if i + 1 == len(dirs):
            print(f"Indexing files for {lib_name}: 100%")
        else:
            if i >= len(dirs) * percent/100:
                print(f"Indexing files for {lib_name}: {percent}%")
                while i / len(dirs) > percent/100:
                    percent += 10

        directory = dirs[i]
        project = processor(os.path.join(path, directory), lib_name, lib_data)
        projects.append(project)

    if len(projects) > 0:
        write_index(index_path, projects)

    print(f"Indexing files for {lib_name}: created")

    return projects


def get_v_info(path: str) -> dict | bool:
    with open('./backend/v_info.json', 'r', encoding='utf-8') as f:
        v_info = json.load(f)

    if os.path.exists(os.path.join(path, "v_info.json")):
        with open(os.path.join(path, "v_info.json"), "r", encoding='utf-8') as f:
            v_info_exist = json.load(f)

        if v_info_exist["info_version"] == v_info["info_version"]:
            return v_info_exist
        else:
            raise IOError("v_info version is not corrected")

    else:
        return False

