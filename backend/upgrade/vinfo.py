from backend import utils
from pathlib import Path
from backend import logger

log = logger.get_logger("Upgrader")


class VInfoUpgrageError(Exception):
    pass


# def upgrade(project_path: Path, template_: ProjectTemplate = None) -> None | ProjectTemplate:
#     log.debug("upgrade")
#     if project_path:
#         log.debug(project_path)
#     if template_:
#         log.debug(template_)
#
#     vinfo_path = Path(project_path) / 'sf.viewer/v_info.json'
#     info_file = None
#     upgraded = False
#
#     if template_ is None:
#         log.debug("Loading data into template from path.")
#
#         info_file = ProjectInfoFile(path=vinfo_path)
#         template = info_file.data
#     else:
#         template = template_
#
#     if template.info_version == 2:
#         log.debug("Current version is 2. Upgrading to 3.")
#         template = upgrade_to_3(project_path, template)
#         upgraded = True
#
#     if template.info_version == 3:
#         log.debug("Current version is 3. Upgrading to 4.")
#         template = upgrade_to_4(template)
#         upgraded = True
#
#     if upgraded is False:
#         log.debug("Upgrading not need.")
#         if template_:
#             log.debug("Returning template without changes.")
#             return template
#         return
#
#     if template_ is None:
#         log.debug("Writing data into json file.")
#         info_file.set(template)
#         info_file.commit()
#     else:
#         log.debug("Returning template.")
#         return template
#
#
# def upgrade_to_3(project_path: Path, template: ProjectTemplate) -> ProjectTemplate:
#     log.debug("Upgrading to v3.")
#
#     preview_path = project_path / template.preview
#
#     template.preview_hash = utils.get_imagehash(preview_path)
#     log.debug(template.preview_hash)
#
#     template.info_version = 3
#
#     log.debug(f"Upgrade to version 3 completed")
#     return template
#
#
# def upgrade_to_4(template: ProjectTemplate) -> ProjectTemplate:
#     log.debug("Upgrading to v4.")
#
#     template.episodes = []
#     log.debug(template.preview_hash)
#
#     template.info_version = 4
#
#     log.debug(f"Upgrade to version 4 completed")
#     return template