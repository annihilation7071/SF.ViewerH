import json
import os
from backend import utils
from backend.classes.templates import ProjectTemplate
from pathlib import Path
from backend.modules import logger
from backend.modules.filesession import FSession
from backend.upgrade.vinfo import upgrade
from importlib import import_module
from backend.classes.files import ProjectInfoFile

log = logger.get_logger("Processor.general")

meta_file = "metadata.json"


def make_v_info(fs: FSession, path: Path, processor_name: str) -> None:
    log.debug("make_v_info")
    log.info(f"Processing: {path}")
    template = ProjectTemplate()
    template.info_version = 2
    template.lid = utils.gen_lid()
    template.lvariants = []

    processor = import_module(f"backend.processors.{processor_name}")
    template = processor.parse(path, template)

    vinfo_path = path / "sf.viewer/v_info.json"

    template = upgrade(path, template)

    log.debug("Writing vinfo to project")

    project_info_file = ProjectInfoFile(
        path=vinfo_path,
        template=template,
    )

    project_info_file.create(fs)

