import json
from backend import utils
from pathlib import Path
from icecream import ic
ic.configureOutput(includeContext=True)


def upgrade(project_path: str | Path) -> None:
    ic(f"Path received for upgrade: {project_path}")

    vinfo_path = Path(project_path) / 'sf.viewer/v_info.json'

    with open('./backend/v_info.json', 'r', encoding='utf-8') as f:
        v_info = json.load(f)

    with open(vinfo_path, 'r', encoding='utf-8') as f:
        old_vinfo = json.load(f)

    if old_vinfo["info_version"] == 2:
        ic(f"Current version is 2")
        upgrade_to_3(vinfo_path)


def upgrade_to_3(vinfo_path: str | Path) -> None:
    ic(f"Upgrade to version 3")
    with open(vinfo_path, 'r', encoding='utf-8') as f:
        vinfo = json.load(f)

    project_path = Path(vinfo_path).parent.parent
    preview_path = project_path / vinfo["preview"]

    vinfo["preview_hash"] = utils.get_imagehash(preview_path)
    vinfo["info_version"] = 3

    with open(vinfo_path, 'w', encoding='utf-8') as f:
        json.dump(vinfo, f, indent=4)
    ic(f"Upgrade to version 3 completed")