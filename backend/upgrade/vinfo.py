import json
from backend import utils
from pathlib import Path
from backend.classes.templates import ProjectTemplate
from backend.logger_new import get_logger

log = get_logger("vinfo_upgrader")


class VInfoUpgrageError(Exception):
    pass


def upgrade(project_path: Path, template_: ProjectTemplate = None, force_write=False) -> None | ProjectTemplate:
    log.debug("upgrade")
    if project_path:
        log.debug(project_path)
    if template_:
        log.debug(template_)

    vinfo_path = Path(project_path) / 'sf.viewer/v_info.json'
    upgraded = False

    if template_ is None:
        log.debug("Loading data into template from path.")

        with open(vinfo_path, 'r', encoding='utf-8') as f:
            old_vinfo = json.load(f)

        template = ProjectTemplate(**old_vinfo)
    else:
        template = template_

    if template.info_version == 2:
        log.debug("Current version is 2. Upgrading to 3.")
        template = upgrade_to_3(project_path, template)
        upgraded = True

    if upgraded is False:
        log.debug("Upgrading not need.")
        if template_:
            log.debug("Returning template without changes.")
            return template
        return

    if template_ is None or force_write is True:
        log.debug("Writing data into json file.")
        data = template.model_dump_json()
        with open(vinfo_path, 'w', encoding='utf-8') as f:
            # noinspection PyTypeChecker
            json.dump(json.loads(data), f, ensure_ascii=False, indent=4)
    else:
        log.debug("Returning template.")
        return template


def upgrade_to_3(project_path: Path, template: ProjectTemplate) -> ProjectTemplate:
    log.debug("Upgrading to v3.")

    preview_path = project_path / template.preview

    template.preview_hash = utils.get_imagehash(preview_path)
    log.debug(template.preview_path)

    template.info_version = 3

    log.debug(f"Upgrade to version 3 completed")
    return template