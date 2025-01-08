from backend.utils import tag_normalizer
from backend.projects.cls import Projects
from backend.logger_new import get_logger
from backend.classes.projecte import ProjectE

log = get_logger("item_editor")


class ItemEditorError(Exception):
    pass


edit_types = {
    "edit-tags": "tag",
    "edit-series": "series"
}


def edit(projects: Projects, project: ProjectE, edit_type: str, data: str, update_priority: bool = True):
    log.debug("item_editor.edit")
    log.debug(f"Edit type: {edit_type}")
    log.debug(f"Data: {data}")

    if edit_type not in edit_types:
        raise ItemEditorError(f"edit_type: {edit_type} not supported")

    items = data.split("\n")
    items = [item for item in items if item != ""]
    items = tag_normalizer(items)
    log.debug(f"Normalized items: {items}")

    if project.lid.startswith("pool_"):
        log.debug(f"Project is a pool. Finding projects...")
        multiple_edit(projects, project, edit_type, items)
        projects.update_priority(project)
        return

    setattr(project, edit_types[edit_type], items)
    project.update()

    return


def multiple_edit(projects: Projects, project: ProjectE, edit_type: str, items: list):
    log.debug("item_editor.multiple_edit")
    project_items: list = project[edit_types[edit_type]]
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
        target_project = projects.get_project_by_lid(lid)
        data: list = target_project[edit_types[edit_type]]
        log.debug(f"Old data: {data}")

        new_data = data
        for item in plus:
            if item not in new_data:
                new_data.append(item)

        for item in minus:
            if item in new_data:
                new_data.remove(item)

        log.debug(f"New data: {new_data}")
        edit(projects, target_project, edit_type, "\n".join(new_data), update_priority=False)
