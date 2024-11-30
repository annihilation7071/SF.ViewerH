# https://github.com/RicterZ/nhentai

import json
import os
from collections import defaultdict
from backend.processors import general
from backend import utils


meta_file = "metadata.json"


def get_project(path: str, lib_name: str, lib_data: dict) -> dict:
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
    project["source"] = "nhentai.net"

    files = os.listdir(path)
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
    v_info["downloader"] = "nhentai"
    
    _name = os.path.basename(path)

    try:

        _id = _name[1:_name.find("]")]
        _id = int(_id)
        v_info["source_id"] = str(_id)
    except Exception:
        v_info["source_id"] = metadata["URL"].split("/")[-1] or metadata["url"].split("/")[-1] or "unknown"
            
    v_info["url"] = metadata["URL"] or metadata["url"] or "unknown"
    v_info["title"] = metadata["title"] or _name
    v_info["subtitle"] = metadata["subtitle"] or ""
    # noinspection PyTypeChecker
    v_info["upload_date"] = general.get_time(metadata["upload_date"], "%Y-%m-%dT%H:%M:%S.%f%z") or "unknown"
    v_info["series"] = []

    def f(key: str) -> list | str:
        return general.tag_normalizer(metadata[key])
    
    v_info["parody"] = f("parody") or ["unknown"]
    v_info["character"] = f("character") or ["unknown"]
    v_info["tag"] = f("tag") or ["unknown"]
    v_info["artist"] = f("artist") or ["unknown"]
    v_info["group"] = f("group") or ["unknown"]
    v_info["language"] = f("language") or ["unknown"]
    v_info["category"] = f("category") or ["unknown"]
    v_info["pages"] = f("Pages") or "unknown"

    with open(os.path.join(path, "v_info.json"), "w", encoding='utf-8') as f:
        json.dump(v_info, f, indent=4)


def get_projects(lib_name: str, lib_data: dict) -> list:
    projects = general.get_projects(lib_name, lib_data, meta_file, processor=get_project)
    return projects







