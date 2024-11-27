import os
import json
from importlib import import_module
from datetime import datetime


def get_pages(project: dict):
    extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.avif', '.webp']

    path = project['path']

    files = os.listdir(path)

    pages = []

    for file in files:
        if os.path.splitext(file)[1] in extensions:
            pages.append(os.path.join(path, file))

    pages = sorted(pages)
    pages = [{"idx": i, "path": pages[i]} for i in range(len(pages))]

    return pages


def get_projects():
    projects = []

    files = os.listdir("./settings/libs/")
    files = [file for file in files if file.startswith('lib_')]

    libs = {}
    for file in files:
        with open(os.path.join("./settings/libs", file), 'r', encoding="utf-8") as f:
            lib = json.load(f)

        a = len(libs)
        if len(libs.keys() - lib.keys()) > a:
            raise IOError(f"ERROR: Lib files contain the same names")

        libs.update(lib)

    for name, data in libs.items():
        if data["active"] is False:
            continue

        proc = import_module(f"backend.processors.{data['processor']}")
        projects += proc.get_projects(name, data)

    projects = sorted(projects,
                      key=lambda x: datetime.strptime(x["upload_date"], "%Y-%m-%dT%H:%M:%S"),
                      reverse=True)

    for i in range(len(projects)):
        # for key, value in projects[i].items():
        #     print(key, end=" --- :")
        #     print(value)
        projects[i]["id"] = i

    return projects





