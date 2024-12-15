# https://github.com/mikf/gallery-dl
# --write-info-json

import json
import os
from collections import defaultdict
from backend import utils

meta_file = "info.json"


def make_v_info(path: str) -> None:
    with open("./backend/v_info.json", "r", encoding='utf-8') as f:
        v_info = json.load(f)

    with open(os.path.join(path, meta_file), "r", encoding='utf-8') as f:
        metadata = defaultdict(lambda: False, json.load(f))

    v_info["lid"] = utils.gen_lid()
    v_info["lvariants"] = []
    v_info["source"] = "hitomi.la"
    v_info["downloader"] = "gallery-dl"

    files = os.listdir(path)
    files = [file for file in files if file.startswith("hitomi_")]
    files = sorted(files)
    v_info["preview"] = files[0]

    _name = os.path.basename(path)

    # noinspection PyBroadException
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
    v_info["title"] = metadata["title"] or _name
    v_info["subtitle"] = ""
    # noinspection PyTypeChecker
    v_info["upload_date"] = utils.to_time(metadata["date"], "%Y-%m-%d %H:%M:%S") or "unknown"
    v_info["category"] = ["unknown"]
    v_info["series"] = []

    def f(key: str) -> list | str:
        return utils.tag_normalizer(metadata[key])

    v_info["parody"] = f("parody") or ["unknown"]
    v_info["character"] = f("characters") or ["unknown"]
    v_info["tag"] = f("tags") or ["unknown"]
    v_info["artist"] = f("artist") or ["unknown"]
    v_info["group"] = f("group") or ["unknown"]
    v_info["language"] = [f("language")] or ["unknown"]
    v_info["pages"] = f("count") or "unknown"

    _path = os.path.join(path, "sf.viewer/")
    if os.path.exists(_path) is False:
        os.makedirs(_path)

    with open(os.path.join(_path, "v_info.json"), "w", encoding='utf-8') as f:
        json.dump(v_info, f, indent=4)
