from backend.main_import import *
from backend.upgrade.vinfo import upgrade

log = logger.get_logger("Processor.general")

meta_file = "metadata.json"


def make_v_info(session: Session, fs: FSession, path: Path, processor_name: str) -> None:
    log.debug("make_v_info")
    log.info(f"Processing: {path}")
    template = ProjectBase(
        lid=utils.gen_lid(),
        info_version=2
    )

    template._path = path

    log.debug(f"path: {template._path}")

    processor = import_module(f"backend.processors.{processor_name}")
    template = processor.parse(path, template)

    vinfo_path = path / "sf.viewer/v_info.json"

    template = upgrade(session, path, template)

    log.debug("Writing vinfo to project")

    template.prolect_file_save()

