import os
import json
from importlib import import_module
from datetime import datetime
from collections import defaultdict


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


def read_libs():
    files = os.listdir("./settings/libs/")
    files = [file for file in files if file.startswith('libs_') and file.endswith('.json') and file != "libs_example.json"]

    libs = {}
    for file in files:
        with open(os.path.join("./settings/libs", file), 'r', encoding="utf-8") as f:
            lib = json.load(f)

        a = len(libs)
        if len(libs.keys() - lib.keys()) > a:
            raise IOError(f"ERROR: Libs files contain the same names")

        libs.update(lib)

    return libs


def get_projects():
    projects = []
    lids = {}

    libs = read_libs()

    for name, data in libs.items():
        if data["active"] is False:
            continue

        proc = import_module(f"backend.processors.{data['processor']}")
        projects += proc.get_projects(name, data)

    projects = sorted(projects,
                      key=lambda x: datetime.strptime(x["upload_date"], "%Y-%m-%dT%H:%M:%S"),
                      reverse=True)

    for i in range(len(projects)):
        projects[i]["id"] = i
        lids[projects[i]["lid"]] = i

    with open("./data/index/lids.json", "w", encoding="utf-8") as f:
        json.dump(lids, f)

    return projects


def count_param(param: str, projects: list = None):
    if projects is None:
        projects = get_projects()

    params = defaultdict(int)

    for project in projects:
        for artist in project[param]:
            params[artist] += 1

    return sorted(params.items(), key=lambda item: item[1], reverse=True)


def gen_lid():
    number = int(datetime.now().strftime('%Y%m%d%H%M%S%f'))

    base = 64
    result = ""
    letters = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
               "abcdefghijklmnopqrstuvwxyz"
               "0123456789"
               "-_")

    while number != 0:
        result += letters[number % base]
        number //= base

    return result[::-1]
