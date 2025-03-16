from backend.main_import import *
from backend.utils import *
from backend.filesession import FileSession



def libs_settings():
    data = {
        "download-default-nhentai": {
            "active": True,
            "processor": "nhentai",
            "path": ".\\downloads\\default-nhentai"
        },
        "download-default-gallery-dl-hitomila": {
            "active": True,
            "processor": "gallery-dl-hitomila",
            "path": ".\\downloads\\default-gallery-dl-hitomila"
        },
        "download-default-gallery-dl-nhentai": {
            "active": False,
            "processor": "gallery-dl-nhentai",
            "path": ".\\downloads\\default-gallery-dl-nhentai"
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

        utils.write_json(path, exist_data)


def dowloaders_settings():
    data = {
        "general": {
            "proxy": None,
            "user_agent": None
        },
        "nhentai": {
            "proxy": None,
            "user_agent": None,
            "cookies": None
        },
        "gallery-dl-general": {
            "proxy": None,
            "user_agent": None
        },
        "gallery-dl-(nhentai.net)": {
            "proxy": None,
            "user_agent": None,
            "cookies": None
        },
        "gallery-dl-(hitomi.la)": {
            "proxy": None,
            "user_agent": None,
            "cookies": None
        }
    }

    path = Path("./settings/download/settings.json")

    if path.exists() is False:
        path.parent.mkdir(parents=True, exist_ok=True)
        utils.write_json(path, data)

    else:
        exist_data = utils.read_json(path)

        for downloader in data.keys():
            if downloader not in exist_data:
                exist_data[downloader] = data[downloader]
            else:
                for property_ in data[downloader].keys():
                    if property_ not in exist_data[downloader]:
                        exist_data[downloader][property_] = data[downloader][property_]

        utils.write_json(path, exist_data)


def downloaders_targets():
    data = {
        "nhentai.net": "download-default-nhentai",
        "hitomi.la": "download-default-gallery-dl-hitomila"
    }

    path = Path("./settings/download/download_targets.json")

    if path.exists() is False:
        path.parent.mkdir(parents=True, exist_ok=True)
        utils.write_json(path, data)
    else:
        exist_data = utils.read_json(path)

        for site in data.keys():
            if site not in exist_data:
                exist_data[site] = data[site]

        utils.write_json(path, exist_data)


def init():
    libs_settings()
    dowloaders_settings()
    downloaders_targets()

