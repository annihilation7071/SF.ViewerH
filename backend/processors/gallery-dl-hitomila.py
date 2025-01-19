# https://github.com/mikf/gallery-dl
# --write-info-json

import json
import os
from collections import defaultdict
from backend import utils
from backend.classes.templates import ProjectTemplate
from pathlib import Path
from backend.modules import logger
from datetime import datetime

log = logger.get_logger("Processor.gallery-dl-hitomila")

meta_file = "info.json"


def parse(path: Path, template: ProjectTemplate) -> ProjectTemplate:
    log.debug("gallery-dl-hitomila.parse")
    
    with open(os.path.join(path, meta_file), "r", encoding='utf-8') as f:
        metadata = defaultdict(lambda: False, json.load(f))

    template.source = "hitomi.la"
    template.downloader = "gallery-dl"

    files = os.listdir(path)
    files = [file for file in files if file.startswith("hitomi_")]
    files = sorted(files)
    template.preview = files[0]

    _name = os.path.basename(path)

    # noinspection PyBroadException
    try:
        if metadata["gallery_id"] is not False:
            _id = metadata["gallery_id"]
            template.source_id = str(_id)
        else:
            try:
                _id = _name[0:_name.find(" ")]
                _id = int(_id)
            except Exception as e:
                _id = _name
                _id = int(_id)
                raise e
            template.source_id = str(_id)
    except Exception:
        template.source_id = "unknown"

    template.url = "unknown"
    template.title = metadata["title"] or _name
    template.subtitle = ""
    # noinspection PyTypeChecker
    template.upload_date = utils.to_time(metadata["date"], "%Y-%m-%d %H:%M:%S") or datetime.now()
    template.category = ["unknown"]
    template.series = []

    def f(key: str) -> list | str:
        return utils.tag_normalizer(metadata[key])

    template.parody = f("parody") or ["unknown"]
    template.character = f("characters") or ["unknown"]
    template.tag = f("tags") or ["unknown"]
    template.artist = f("artist") or ["unknown"]
    template.group = f("group") or ["unknown"]
    template.language = [f("language")] or ["unknown"]
    template.pages = f("count") or -1

    return template
