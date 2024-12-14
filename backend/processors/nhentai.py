# https://github.com/RicterZ/nhentai

import json
import os
from collections import defaultdict
from backend.processors import general
from backend import utils

meta_file = "metadata.json"


def make_v_info(path: str) -> None:
    with open("./backend/v_info.json", "r", encoding='utf-8') as f:
        v_info = json.load(f)

    with open(os.path.join(path, meta_file), "r", encoding='utf-8') as f:
        metadata = defaultdict(lambda: False, json.load(f))

    v_info["lid"] = utils.gen_lid()
    v_info["lvariants"] = []
    v_info["source"] = "nhentai.net"
    v_info["downloader"] = "nhentai"

    files = os.listdir(path)
    files = sorted(files)
    v_info["preview"] = files[0]
    
    _name = os.path.basename(path)

    # noinspection PyBroadException
    try:

        _id = _name[1:_name.find("]")]
        _id = int(_id)
        v_info["source_id"] = str(_id)
    except Exception:
        # noinspection PyUnresolvedReferences
        v_info["source_id"] = metadata["URL"].split("/")[-1] or metadata["url"].split("/")[-1] or "unknown"
            
    v_info["url"] = metadata["URL"] or metadata["url"] or "unknown"
    v_info["title"] = metadata["title"] or _name
    v_info["subtitle"] = metadata["subtitle"] or ""
    # noinspection PyTypeChecker
    v_info["upload_date"] = general.get_time(metadata["upload_date"], "%Y-%m-%dT%H:%M:%S.%f%z") or "unknown"
    v_info["series"] = []

    def f(key: str) -> list | str:
        return utils.tag_normalizer(metadata[key])
    
    v_info["parody"] = f("parody") or ["unknown"]
    v_info["character"] = f("character") or ["unknown"]
    v_info["tag"] = f("tag") or ["unknown"]
    v_info["artist"] = f("artist") or ["unknown"]
    v_info["group"] = f("group") or ["unknown"]
    v_info["language"] = f("language") or ["unknown"]
    v_info["category"] = f("category") or ["unknown"]
    v_info["pages"] = f("Pages") or "unknown"

    _path = os.path.join(path, "./sf.viewer/")
    if os.path.exists(_path) is False:
        os.makedirs(_path)

    with open(os.path.join(_path, "v_info.json"), "w", encoding='utf-8') as f:
        json.dump(v_info, f, indent=4)
