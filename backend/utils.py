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

    with open('./settings/libs.json', 'r') as f:
        libs = json.load(f)

    for name, data in libs.items():
        if data["active"] is False:
            continue

        proc = import_module(f"backend.processors.{data['processor']}")
        projects += proc.get_projects(name, data)

    for i in range(len(projects)):
        projects[i]["id"] = i

    projects = sorted(projects,
                      key=lambda x: datetime.strptime(x["upload_date"], "%Y-%m-%dT%H:%M:%S"),
                      reverse=True)

    return projects





