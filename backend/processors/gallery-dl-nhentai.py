# https://github.com/mikf/gallery-dl
# --write-info-json

import json
import os
from collections import defaultdict
from backend.processors import general
from backend import utils

meta_file = "info.json"


def get_project(path: str, lib_name: dict, lib_date: str) -> dict:
    with open('./backend/project.json', 'r', encoding='utf-8') as f:
        project = json.load(f)

    v_info = general.get_v_info(path)
    if v_info is False:
        make_v_info(path)
        v_info = general.get_v_info(path)

    for k, v in v_info.items():
        project[k] = v

    _name = os.path.basename(path)

    project["dir_name"] = _name
    project["path"] = path
    project["lib"] = lib_name

    files = os.listdir(path)
    files = [file for file in files if file.startswith("nhentai_")]
    files = sorted(files)

    project["preview_path"] = os.path.join(path, files[0])

    return project


def make_v_info(path: str) -> None:
    with open("./backend/v_info.json", "r", encoding='utf-8') as f:
        v_info = json.load(f)

    with open(os.path.join(path, meta_file), "r", encoding='utf-8') as f:
        metadata = defaultdict(lambda: False, json.load(f))

    v_info["lid"] = utils.gen_lid()
    v_info["lvariants"] = []
    v_info["source"] = "nhentai.net"
    v_info["downloader"] = "gallery-dl"

    _name = os.path.basename(path)

    try:
        if metadata["gallery_id"] is not False:
            _id = metadata["gallery_id"]
            v_info["source_id"] = str(_id)
        else:
            try:
                _id = _name[0:_name.find(" ")]
                _id = int(_id)
            except Exception as e:
                _id = _name
                _id = int(_id)
                raise e
            v_info["source_id"] = str(_id)
    except Exception:
        v_info["source_id"] = "unknown"

    v_info["url"] = "unknown"
    v_info["title"] = metadata["title"] or metadata["title_en"] or _name
    v_info["subtitle"] = metadata["title_ja"] or metadata["title_en"] or ""
    if v_info["title"] == v_info["subtitle"]:
        v_info["subtitle"] = ""
    # noinspection PyTypeChecker
    v_info["upload_date"] = general.get_time(metadata["date"]) or "unknown"
    v_info["category"] = ["unknown"]
    v_info["series"] = []

    def f(key: str) -> list | str:
        return general.tag_normalizer(metadata[key])

    v_info["parody"] = f("parody") or ["unknown"]
    v_info["character"] = f("characters") or ["unknown"]
    v_info["tag"] = f("tags") or ["unknown"]
    v_info["artist"] = f("artist") or ["unknown"]
    v_info["group"] = f("group") or ["unknown"]
    v_info["language"] = [f("language")] or ["unknown"]
    v_info["pages"] = f("count") or "unknown"

    with open(os.path.join(path, "v_info.json"), "w", encoding='utf-8') as f:
        json.dump(v_info, f, indent=4)


def get_projects(lib_name: str, lib_data: dict) -> list:
    projects = general.get_projects(lib_name, lib_data, meta_file, processor=get_project)
    return projects
