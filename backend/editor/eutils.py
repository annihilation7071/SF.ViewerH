import os
import json


def update_data(projects, project: dict, target: str | list, new_data, multiple: bool = False):
    # v_info.json
    path = os.path.join(project["path"], "sf.viewer/v_info.json")

    if multiple is False:
        target = [target]
        new_data = [new_data]

    with open(path, "r", encoding="utf-8") as f:
        v_info = json.load(f)

    for i in range(0, len(target)):
        v_info[target[i]] = new_data[i]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(v_info, f, indent=4)

    with open(path, "r", encoding="utf-8") as f:
        v_info = json.load(f)

    for i in range(0, len(target)):
        if v_info[target[i]] != new_data[i]:
            raise IOError("Failed to update data in v_info.json")

    # DB
    for i in range(0, len(target)):
        project[target[i]] = new_data[i]
    projects.update_item(project)