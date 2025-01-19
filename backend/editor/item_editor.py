from backend import dep
from backend.utils import tag_normalizer
from backend.modules import logger
from backend.classes.projecte import ProjectE, ProjectEPool
from backend.classes.files import ProjectInfoFile
from sqlalchemy.orm import Session
from backend.modules.filesession import FileSession, FSession

log = logger.get_logger("Editor.item")


class ItemEditorError(Exception):
    pass


edit_types = {
    "edit-tags": "tag",
    "edit-series": "series"
}


def edit(session: Session, fs: FSession, project: ProjectE | ProjectEPool, edit_type: str, data: str, update_priority: bool = True):
    log.debug("item_editor.edit")
    log.debug(f"Edit type: {edit_type}")
    log.debug(f"Data: {data}")

    if edit_type not in edit_types:
        raise ItemEditorError(f"edit_type: {edit_type} not supported")

    items = data.split("\n")
    items = [item for item in items if item != ""]
    items = tag_normalizer(items)
    log.debug(f"Normalized items: {items}")

    if project.lid.startswith("pool_") and type:
        log.debug(f"Project is a pool. Finding projects...")
        return multiple_edit(session, fs, project, edit_type, items)

    setattr(project, edit_types[edit_type], items)

    project.update_(session, fs=fs)

    return project.lid


def multiple_edit(session: Session, fs: FSession, project: ProjectEPool, edit_type: str, items: list):
    log.debug("item_editor.multiple_edit")
    project_items: list = getattr(project, edit_types[edit_type])
    minus = []
    plus = []
    for item in items:
        if item not in project_items:
            plus.append(item)

    for item in items:
        try:
            project_items.remove(item)
        except ValueError:
            continue

    minus = project_items

    log.debug(f"Minus: {minus}")
    log.debug(f"Plus: {plus}")

    log.debug(f"Finding variants....")
    for variant in project.lvariants:
        lid: str = variant.split(":")[0]
        log.debug(f"Variant: {lid}")

        target_project: ProjectE = ProjectE.load_from_db(session, fs, lid)
        data: list = getattr(target_project, edit_types[edit_type])
        log.debug(f"Old data: {data}")

        new_data = data
        for item in plus:
            if item not in new_data:
                new_data.append(item)

        for item in minus:
            if item in new_data:
                new_data.remove(item)

        log.debug(f"New data: {new_data}")

        setattr(target_project, edit_types[edit_type], new_data)
        target_project.update_(session, fs)

    project.update_pool(session, fs)

    log.debug(f"Return: {project.lid}")
    return project.lid
