import json
import os
from datetime import datetime


def get_dirs(path: str, meta_file: str) -> list[str]:
    dirs = []
    files = os.listdir(path)
    for file in files:
        if os.path.exists(os.path.join(path, file) + f"/{meta_file}"):
            dirs.append(file)
    return dirs


def get_index(index_path: str, dirs: list[str]) -> bool | dict:

    with open(index_path, "r", encoding="utf-8") as f:
        index = json.load(f)

    if len(index) != len(dirs):
        return False

    for directory in dirs:
        if directory not in index:
            return False

    return index


def write_index(index_path: str, projects: list) -> None:

    index = {project["dir_name"]: project for project in projects}

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


def get_time(str_time: str, format: str) -> str | bool:
    try:
        date = datetime.strptime(str_time, format)
        return date.strftime("%Y-%m-%dT%H:%M:%S")
    except Exception as e:
        print(e)
        return False


def get_projects(lib_name: str, lib_data: dict, meta_file: str, processor) -> list:

    path = lib_data["path"]
    projects = []
    dirs = get_dirs(path, meta_file)

    index_path = f"./data/index/{lib_name}.json"

    if os.path.exists(index_path):
        print(f"Index file for {lib_name}: exist")
        index = get_index(index_path, dirs)
        if index is not False:
            projects = list(index.values())
            print(f"Index file for {lib_name}: correct\n"
                  f"Using existing index file for {lib_name}")
            return projects
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

    write_index(index_path, projects)
    print(f"Indexing files for {lib_name}: created")

    return projects

