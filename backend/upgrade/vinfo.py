import json


def upgrade(path: str, old_vinfo: dict):
    with open('./backend/v_info.json', 'r', encoding='utf-8') as f:
        v_info = json.load(f)

    if old_vinfo["info_version"] == 2:
        pass

