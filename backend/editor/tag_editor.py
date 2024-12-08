import json
import os

from backend.projects import Projects
from backend.processors.general import tag_normalizer

projects = Projects()


def edit(data: str, project):

    tags = data.split("\n")
    print(tags)
    tags = [tag for tag in tags if tag != ""]
    tags = tag_normalizer(tags)
    print(tags)

    # v_info.json
    path = os.path.join(project["path"], "sf.viewer/v_info.json")

    with open(path, "r", encoding="utf-8") as f:
        v_info = json.load(f)

    v_info["tag"] = tags

    with open(path, "w", encoding="utf-8") as f:
        json.dump(v_info, f, indent=4)

    with open(path, "r", encoding="utf-8") as f:
        v_info = json.load(f)

    if v_info["tag"] != tags:
        raise IOError("Failed to update data in v_info.json")

    # DB
    project["tag"] = tags
    projects.update_item(project)

    return

