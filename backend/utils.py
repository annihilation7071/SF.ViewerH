import os
import json
from datetime import datetime
import uuid
from PIL import Image
import imagehash
from pathlib import Path
from icecream import ic
ic.configureOutput(includeContext=True)

def get_pages(project: dict):
    extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.avif', '.webp']

    path = project['path']

    files = os.listdir(path)

    pages = []

    for file in files:
        if os.path.splitext(file)[1] in extensions:
            pages.append(os.path.join(path, file))

    pages = sorted(pages)
    pages = [{"idx": i, "path": pages[i]} for i in range(len(pages))]

    return pages


def read_libs() -> dict:
    files = os.listdir("./settings/libs/")
    files = [file for file in files if file.startswith('libs_') and file.endswith('.json') and file != "libs_example.json"]

    libs = {}
    for file in files:
        with open(os.path.join("./settings/libs", file), 'r', encoding="utf-8") as f:
            lib = json.load(f)

        a = len(libs)
        if len(libs.keys() - lib.keys()) > a:
            raise IOError(f"ERROR: Libs files contain the same names")

        libs.update(lib)

    return libs


def gen_lid():
    num_1 = int(datetime.now().strftime('%Y%m%d%H%M%S%f'))
    num_2 = int(uuid.uuid4().hex, 16)

    def to_62(num):
        base = 62
        result = ""
        letters = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                   "abcdefghijklmnopqrstuvwxyz"
                   "0123456789")

        while num != 0:
            result += letters[num % base]
            num //= base

        return result[::-1]

    d = to_62(num_1)
    r = to_62(num_2)[0:10]
    return f"{d}_{r}"


def str_to_list(str_list: str, separator=";;;") -> list:
    items = str_list.split(separator)
    items = [item for item in items if len(item) > 0]
    return items


def list_to_str(list_str: list) -> str:
    result = ";;;".join(list_str)
    return result


def tag_normalizer(tags: str | list | int, lower: bool = True, ali: bool = True):
    if isinstance(tags, int):
        return tags

    aliases = get_aliases()

    # noinspection PyShadowingNames
    def normalize(tag: str) -> str:
        if lower is True:
            new_tag = tag.lower()
        else:
            new_tag = tag
        new_tag = new_tag.replace("♀", "")
        new_tag = new_tag.replace("♂", "")
        new_tag = new_tag.replace("\r", "")
        new_tag = new_tag.replace("\n", "")
        new_tag = new_tag.strip()
        if ali is True and new_tag in aliases:
            return aliases[new_tag]
        else:
            return new_tag

    if isinstance(tags, str):
        return normalize(tags)
    elif isinstance(tags, list):
        new_tags = []
        for tag in tags:
            new_tag = normalize(tag)
            if new_tag != "":
                new_tags.append(new_tag)
        return new_tags


def to_time(str_time: str | int, format: str = None) -> str | bool:
    if isinstance(str_time, str) and format is None:
        raise IOError("Format must be specified")

    target_format = "%Y-%m-%dT%H:%M:%S"

    if isinstance(str_time, str):
        try:
            date = datetime.strptime(str_time, format)
            return date.strftime(target_format)
        except Exception as e:
            print(e)
            return False
    elif isinstance(str_time, int):
        date = datetime.fromtimestamp(1566440093)
        return date.strftime(target_format)


def get_aliases():
    files = os.listdir("./settings/aliases/")
    files = [file for file in files if (file.startswith("aliases") and file.endswith(".json"))]

    aliases = {}
    for file in files:
        with open(os.path.join("./settings/aliases/", file), 'r', encoding="utf-8") as f:
            aliases_file = json.load(f)

        a = len(aliases)
        if len(aliases.keys() - aliases_file.keys()) > a:
            raise IOError(f"ERROR: Aliases files contain the same names")

        aliases.update(aliases_file)

    return aliases


def get_imagehash(path: str | Path) -> str:
    realpatch_original = os.path.realpath
    os.path.realpath = os.path.abspath

    image = Image.open(path)
    hash_ = str(imagehash.phash(image))
    ic(f"Hash for {path}: {hash_}")

    os.path.realpath = realpatch_original

    return hash_


def update_vinfo(project_path: str | Path, keys: list, values: list):
    path = Path(project_path)
    path = path / "sf.viewer/v_info.json"

    with open(path, 'r', encoding="utf-8") as f:
        vinfo = json.load(f)

    for i in range(len(keys)):
        if keys[i] in vinfo:
            vinfo[keys[i]] = values[i]
        else:
            raise IOError(f"ERROR: Key {keys[i]} not in vinfo")

    with open(path, 'w', encoding="utf-8") as f:
        json.dump(vinfo, f, indent=4)


def separate_url(url: str):
    allowed_sites = {
        "nhentai.net",
        "hitomi.la"
    }

    url = url.split('//')
    url = [url[0]] + url[1].split('/')
    print(url)
    protocol = url[0]
    site = url[1]
    address = url[2:]

    if site not in allowed_sites:
        raise Exception(f"{site} is not allowed")

    # 'https://hitomi.la/cg/city-no.109-futago-hen-ichi-%E4%B8%AD%E6%96%87-1401507.html'

    if site == "hitomi.la":
        id_ = address[1].split("-")[-1].split(".")[0]

        url = f"{protocol}://{site}/{address[0]}/{id_}.html"

        return url, site, id_

    if site == "nhentai.net":
        id_ = address[1]
        url = f"{protocol}://{site}/{address[0]}/{id_}"

        return url, site, id_