import json
import os
from collections import defaultdict
from backend import utils
from backend.classes.templates import ProjectTemplate
from pathlib import Path
from backend.logger_new import get_logger
from backend.upgrade.vinfo import upgrade
from importlib import import_module

log = get_logger("Processor.general")

meta_file = "metadata.json"


def make_v_info(path: Path, processor_name: str) -> None:
    log.debug("make_v_info")
    log.info(f"Processing: {path}")
    template = ProjectTemplate()
    template.info_version = 2
    template.lid = utils.gen_lid()
    template.lvariants = []

    processor = import_module(f"backend.processors.{processor_name}")
    template = processor.parse(path, template)

    _path = path / "sf.viewer/"
    if os.path.exists(_path) is False:
        os.makedirs(_path)

    template = upgrade(path, template)

    log.debug("Writing vinfo to project")
    data = template.model_dump_json()
    vinfo_path = _path / "v_info.json"
    with open(vinfo_path, "w", encoding="utf-8") as f:
        # noinspection PyTypeChecker
        json.dump(json.loads(data), f, ensure_ascii=False, indent=4)
