import os
import json
from datetime import datetime
import uuid


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

    with open('./data/aliases.json', 'r') as f:
        aliases = json.load(f)

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
    files = os.listdir("./data/aliases/")
    files = [file for file in files if (file.startswith("aliases") and file.startswith(".json"))]

    with open('./data/aliases.json', 'r') as f:
        aliases = json.load(f)
