from pathlib import Path
from backend.modules.filesession import FileSession
import os
from backend import utils


def libs():
    data = {
        "download-default-nhentai": {
            "active": True,
            "processor": "nhentai",
            "path": ".\\downloads\\nhentai"
        },
        "download-default-gallery-dl-hitomila": {
            "active": True,
            "processor": "gallery-dl-hitomila",
            "path": ".\\downloads\\gallery-dl-hitomila"
        },
        "download-default-gallery-dl-nhentai": {
            "active": False,
            "processor": "gallery-dl-nhentai",
            "path": ".\\downloads\\gallery-dl-nhentai"
        }
    }

    path = Path("./settings/libs/libs_default.json")

    if path.exists() is False:
        path.parent.mkdir(parents=True, exist_ok=True)

        utils.write_json(path, data)

    else:
        exist_data = utils.read_json(path)

        for key in data.keys():
            if key not in exist_data:
                exist_data[key] = data[key]


def init():
    libs()

