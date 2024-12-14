import os
import json


def update_data(projects, project: dict, target: str, new_data):
    # v_info.json
    path = os.path.join(project["path"], "sf.viewer/v_info.json")

    with open(path, "r", encoding="utf-8") as f:
        v_info = json.load(f)

    v_info[target] = new_data

    with open(path, "w", encoding="utf-8") as f:
        json.dump(v_info, f, indent=4)

    with open(path, "r", encoding="utf-8") as f:
        v_info = json.load(f)

    if v_info[target] != new_data:
        raise IOError("Failed to update data in v_info.json")

    # DB
    project[target] = new_data
    projects.update_item(project)