from backend.utils import tag_normalizer
from backend.editor import eutils
from backend.projects.cls import Projects
from icecream import ic
ic.configureOutput(includeContext=True)

edit_types = {
    "edit-tags": "tag",
    "edit-series": "series"
}


def edit(projects: Projects, project: dict, edit_type: str, data: str, update_priority: bool = True):
    ic()

    if edit_type not in edit_types:
        raise ValueError(f"edit_type: {edit_type} not supported")

    items = data.split("\n")
    items = [item for item in items if item != ""]
    items = tag_normalizer(items)

    if project["lid"].startswith("pool_"):
        multiple_edit(projects, project, edit_type, items)
        projects.update_priority(project)
        return

    eutils.update_data(projects, project, edit_types[edit_type], items, update_priority=update_priority)

    return


def multiple_edit(projects: Projects, project: dict, edit_type: str, items: list):
    ic()
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

    for variant in project["lvariants"]:
        lid: str = variant.split(":")[0]
        target_project = projects.get_project_by_lid(lid)
        new_data: list = target_project[edit_types[edit_type]]

        for item in plus:
            if item not in new_data:
                new_data.append(item)

        for item in minus:
            if item in new_data:
                new_data.remove(item)

        edit(projects, target_project, edit_type, "\n".join(new_data), update_priority=False)

