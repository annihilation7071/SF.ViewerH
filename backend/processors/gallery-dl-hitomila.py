# https://github.com/mikf/gallery-dl
# --write-info-json

import json
import os
from collections import defaultdict
from backend.processors import general

meta_file = "info.json"


def get_project(path: str, lib_name: dict, lib_date: str) -> dict:
    with open('./backend/patt.json', 'r', encoding='utf-8') as f:
        patt = json.load(f)

    _name = os.path.basename(path)

    patt["dir_name"] = _name
    patt["path"] = path
    patt["source_id"] = _name[0:_name.find(" ")]
    patt["lib"] = lib_name
    patt["source"] = "hitomi.la"

    files = os.listdir(path)
    files = [file for file in files if file.startswith("hitomi_")]
    files = sorted(files)

    patt["preview_path"] = os.path.join(path, files[0])

    with open(os.path.join(path, meta_file), "r", encoding='utf-8') as f:
        metadata = defaultdict(lambda: False, json.load(f))

    def f(key: str) -> list | str:
        return general.tag_normalizer(metadata[key])

    # noinspection PyTypeChecker
    patt["upload_date"] = general.get_time(metadata["date"], "%Y-%m-%d %H:%M:%S") or "unknown"
    patt["url"] = metadata["URL"] or metadata["url"] or "unknown"
    patt["subtitle"] = ""
    patt["category"] = ["unknown"]
    patt["title"] = metadata["title"]

    patt["parody"] = f("parody") or ["unknown"]
    patt["character"] = f("characters") or ["unknown"]
    patt["tag"] = f("tags") or ["unknown"]
    patt["artist"] = f("artist") or ["unknown"]
    patt["group"] = f("group") or ["unknown"]
    patt["language"] = [f("language")] or ["unknown"]
    patt["pages"] = f("count") or "unknown"

    return patt


def get_projects(lib_name: str, lib_data: dict) -> list:
    projects = general.get_projects(lib_name, lib_data, meta_file, processor=get_project)
    return projects
