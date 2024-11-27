# https://github.com/RicterZ/nhentai

import json
import os
from collections import defaultdict
from backend.processors import general


meta_file = "metadata.json"


def get_project(path: str, lib_name: str, lib_data: dict) -> dict:
    with open('./backend/patt.json', 'r', encoding='utf-8') as f:
        patt = json.load(f)

    _name = os.path.basename(path)

    patt["dir_name"] = _name
    patt["path"] = path
    patt["source_id"] = _name[1:_name.find("]")]
    patt["lib"] = lib_name
    patt["source"] = "nhentai.net"

    files = os.listdir(path)
    files = sorted(files)

    patt["preview_path"] = os.path.join(path, files[0])

    with open(os.path.join(path, meta_file), "r", encoding='utf-8') as f:
        metadata = defaultdict(lambda: False, json.load(f))

    def f(key: str) -> list | str:
        return general.tag_normalizer(metadata[key])

    # noinspection PyTypeChecker
    patt["upload_date"] = general.get_time(metadata["upload_date"], "%Y-%m-%dT%H:%M:%S.%f%z") or "unknown"
    patt["url"] = metadata["URL"] or metadata["url"] or "unknown"
    patt["title"] = metadata["title"]

    patt["subtitle"] = f("subtitle") or ""
    patt["parody"] = f("parody") or ["unknown"]
    patt["character"] = f("character") or ["unknown"]
    patt["tag"] = f("tag") or ["unknown"]
    patt["artist"] = f("artist") or ["unknown"]
    patt["group"] = f("group") or ["unknown"]
    patt["language"] = f("language") or ["unknown"]
    patt["category"] = f("category") or ["unknown"]
    patt["pages"] = f("Pages") or "unknown"

    return patt


def get_projects(lib_name: str, lib_data: dict) -> list:
    projects = general.get_projects(lib_name, lib_data, meta_file, processor=get_project)
    return projects
