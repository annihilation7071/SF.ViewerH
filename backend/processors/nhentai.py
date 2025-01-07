# https://github.com/RicterZ/nhentai

import json
import os
from collections import defaultdict
from backend import utils
from backend.classes.templates import ProjectTemplate
from pathlib import Path
from backend.logger_new import get_logger
from datetime import datetime

log = get_logger("Processor.nhentai")

meta_file = "metadata.json"


def parse(path: Path, template: ProjectTemplate) -> ProjectTemplate:
    log.debug("nhentai.parse")

    with open(os.path.join(path, meta_file), "r", encoding='utf-8') as f:
        metadata = defaultdict(lambda: False, json.load(f))

    template.source = "nhentai.net"
    template.downloader = "nhentai"

    files = os.listdir(path)
    files = sorted(files)
    template.preview = files[0]
    
    _name = os.path.basename(path)

    # noinspection PyBroadException
    try:

        _id = _name[1:_name.find("]")]
        _id = int(_id)
        template.source_id = str(_id)
    except Exception:
        # noinspection PyUnresolvedReferences
        template.source_id = metadata["URL"].split("/")[-1] or metadata["url"].split("/")[-1] or "unknown"
            
    template.url = metadata["URL"] or metadata["url"] or "unknown"
    template.title = metadata["title"] or _name
    template.subtitle = metadata["subtitle"] or ""
    # noinspection PyTypeChecker
    template.upload_date = utils.to_time(metadata["upload_date"], "%Y-%m-%dT%H:%M:%S.%f%z") or datetime.now()
    template.series = []

    def f(key: str) -> list | str:
        return utils.tag_normalizer(metadata[key])
    
    template.parody = f("parody") or ["unknown"]
    template.character = f("character") or ["unknown"]
    template.tag = f("tag") or ["unknown"]
    template.artist = f("artist") or ["unknown"]
    template.group = f("group") or ["unknown"]
    template.language = f("language") or ["unknown"]
    template.category = f("category") or ["unknown"]
    template.pages = f("Pages") or -1

    return template
