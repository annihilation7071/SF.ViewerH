from backend.utils import tag_normalizer
from backend.editor import eutils


def edit(projects, project, edit_type, data: str):
    edit_types = {
        "edit-tags": "tag",
        "edit-series": "series"
    }

    if edit_type not in edit_types:
        raise ValueError(f"edit_type: {edit_type} not supported")

    items = data.split("\n")
    items = [tag for tag in items if tag != ""]
    items = tag_normalizer(items)

    eutils.update_data(projects, project, edit_types[edit_type], items)

    return
