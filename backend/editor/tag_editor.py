import json
import os
from backend.processors.general import tag_normalizer


def edit(lid: str, data: str, projects):
    print(lid, data)

    with open("./data/index/lids.json", "r", encoding="utf-8") as f:
        lids = json.load(f)

    project = projects[lids[lid]]

    tags = data.split("\n")
    tags = tag_normalizer(tags)


    # v_info.json
    path = os.path.join(project["path"], "v_info.json")

    with open(path, "r", encoding="utf-8") as f:
        v_info = json.load(f)

    v_info["tag"] = tags

    with open(path, "w", encoding="utf-8") as f:
        json.dump(v_info, f, indent=4)

    with open(path, "r", encoding="utf-8") as f:
        v_info = json.load(f)

    if v_info["tag"] != tags:
        raise IOError("Failed to update data in v_info.json")

    # index
    lib = project["lib"] + ".json"
    path = os.path.join("./data/index", lib)
    print(lib)
    print(project)

    with open(path, "r", encoding="utf-8") as f:
        index = json.load(f)

    print(index)

    index["projects"][project["dir_name"]]["tag"] = tags

    with open(path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=4)

    # open_projects
    project["tag"] = tags

    return

