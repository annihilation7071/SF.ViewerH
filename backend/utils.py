import os
import json
from importlib import import_module
from datetime import datetime
from collections import defaultdict
import uuid


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


def read_libs() -> dict:
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
    libs = read_libs()

    for name, data in libs.items():
        if data["active"] is False:
            continue

        proc = import_module(f"backend.processors.{data['processor']}")
        proc.get_projects(name, data)


def count_param(param: str, projects: list = None):
    if projects is None:
        projects = get_projects()

    params = defaultdict(int)

    for project in projects:
        for artist in project[param]:
            params[artist] += 1

    return sorted(params.items(), key=lambda item: item[1], reverse=True)


def gen_lid():
    num_1 = int(datetime.now().strftime('%Y%m%d%H%M%S%f'))
    num_2 = int(uuid.uuid4().hex, 16)

    def to_62(num):
        base = 62
        result = ""
        letters = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                   "abcdefghijklmnopqrstuvwxyz"
                   "0123456789")

        while num != 0:
            result += letters[num % base]
            num //= base

        return result[::-1]

    d = to_62(num_1)
    r = to_62(num_2)[0:10]
    return f"{d}_{r}"