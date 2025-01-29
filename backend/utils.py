import os
from backend.classes.lib import Lib
import json
from datetime import datetime
import uuid
from PIL import Image
import imagehash
from pathlib import Path
import asyncio
from backend.modules import logger
from backend.classes.templates import ProjectTemplate, ProjectTemplateDB
from backend.classes.db import Project
from backend.classes.templates import ProjectTemplate
from typing import TYPE_CHECKING, Annotated
from importlib import import_module
from backend.modules.filesession import FileSession, FSession

if TYPE_CHECKING:
    from backend.classes.projecte import ProjectE


log = logger.get_logger("Utils")


def get_pages(project: 'ProjectE'):
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


def read_libs_old(check: bool = True, only_active: bool = True) -> dict:
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

    if only_active:
        non_active = []
        for key, value in libs.items():
            if value['active'] is False:
                non_active.append(key)

        for key in non_active:
            libs.pop(key)

    if check:
        for key, value in libs.items():
            if os.path.exists(os.path.abspath(value['path'])) is False:
                raise IOError(f"ERROR: libs dir {os.path.abspath(value['path'])} does not exist")

    return libs


def read_libs(check: bool = True, only_active: bool = True) -> dict[str, Lib]:
    libsdir = Path("./settings/libs").absolute()
    files = os.listdir(libsdir)
    files = [file for file in files if file.startswith('libs_') and file.endswith('.json') and file != "libs_example.json"]

    libs = {}
    for file in files:
        libfile = libsdir / file
        with open(libfile, 'r', encoding="utf-8") as f:
            lib = json.load(f)

        a = len(libs)
        if len(libs.keys() - lib.keys()) > a:
            raise IOError(f"ERROR: Libs files contain the same names")

        libs.update({key: Lib(name=key, libfile=libfile, **value) for key, value in lib.items()})

    if only_active:
        non_active = []
        for key, value in libs.items():
            if value.active is False:
                non_active.append(key)

        for key in non_active:
            libs.pop(key)

    if check:
        for key, value in libs.items():
            if os.path.exists(os.path.abspath(value.path)) is False:
                raise IOError(f"ERROR: libs dir {os.path.abspath(value.path)} does not exist")

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


def to_time(str_time: str, format: str = None) -> datetime | bool:
    log.debug("to_time")
    if isinstance(str_time, str) and format is None:
        raise IOError("Format must be specified")

    # target_format = "%Y-%m-%dT%H:%M:%S"

    if isinstance(str_time, str):
        try:
            date = datetime.strptime(str_time, format)
            return date
        except Exception as e:
            log.error(e)
            return False
    # elif isinstance(str_time, int):
    #     date = datetime.fromtimestamp(1566440093)
    #     return date


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
    log.debug("get_imagehash")
    realpatch_original = os.path.realpath
    os.path.realpath = os.path.abspath

    image = Image.open(path)
    hash_ = str(imagehash.phash(image))
    log.debug(f"hash: {hash_}")

    os.path.realpath = realpatch_original

    return hash_


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

        url = f"{protocol}//{site}/{address[0]}/{id_}.html"

        log.debug(f"url: {url}, site: {site}, id_: {id_}")
        return url, site, id_

    if site == "nhentai.net":
        id_ = address[1]
        url = f"{protocol}//{site}/{address[0]}/{id_}"

        log.debug(f"url: {url}, site: {site}, id_: {id_}")
        return url, site, id_


def get_visible_pages(current_page, total_pages):
    if total_pages <= 15:
        return list(range(1, total_pages + 1))

    # Start pagination
    visible_pages = []
    if current_page > 7:
        visible_pages.append(1)
        # noinspection PyUnresolvedReferences
        visible_pages.append('...')

    # Center pagination
    start_page = max(1, current_page - 7)
    end_page = min(total_pages, start_page + 15 - 1)

    if end_page == total_pages:
        start_page = max(1, total_pages - 15 + 1)

    visible_pages.extend(range(start_page, end_page + 1))

    # End pagination
    if end_page < total_pages:
        visible_pages.append('...')
        visible_pages.append(total_pages)

    return visible_pages


async def run_command(command: str):
    process = await asyncio.create_subprocess_shell(command)
    await process.wait()
    return process


def make_search_body(project: Annotated[dict, 'ProjectE', Project, ProjectTemplateDB]) -> str:
    include = ["source_id", "source", "url", "downloader", "title", "subtitle",
               "parody", "character", "tag", "artist", "group", "language",
               "category", "series", "lib"]

    search_body = ";;;"

    for k in include:
        # noinspection PyPep8Naming,PyShadowingNames
        ProjectE = import_module("backend.classes.projecte").ProjectE
        if isinstance(project, dict):
            v = project[k]
        elif isinstance(project, ProjectE | Project | ProjectTemplate):
            v = getattr(project, k)
        else:
            raise ValueError("Project must be of type dict or ProjectE")

        if isinstance(v, list):
            for item in v:
                search_body += f"{k}:{item.lower()};;;"
        else:
            search_body += f"{k}:{v};;;"

    return search_body


def write_json(path: Path, data: dict | list | ProjectTemplate, fs: FSession = None) -> None:
    log.debug("write_json")

    def f(fs_: FSession):
        try:
            if isinstance(data, list | dict):
                with fs_.open(path, 'w', encoding="utf-8") as f:
                    # noinspection PyTypeChecker
                    json.dump(data, f, indent=4, ensure_ascii=False)
            elif isinstance(data, ProjectTemplate):
                with fs_.open(path, 'w', encoding="utf-8") as f:
                    # noinspection PyTypeChecker
                    json.dump(json.loads(data.model_dump_json()), f, indent=4, ensure_ascii=False)
            else:
                raise TypeError(f"Unsupported type {type(data)}")
        except:
            log.exception("Failed to write json")
            raise

    if fs is None:
        with FileSession() as fs:
            f(fs)
    else:
        f(fs)


def read_json(path: Path) -> dict | list | ProjectTemplate:
    with open(path, 'r', encoding="utf-8") as f:
        data = json.load(f)

    return data


def separate_priority(variants: list) -> tuple[list[list[str]], list[list[str]]]:
    priority = []
    non_priority = []
    for variant in variants:
        variant = variant.split(":")
        if len(variant) == 3:
            if variant[2] in ["priority", "p"]:
                priority.append(variant)
            else:
                raise Exception(f"Unknown marker {variant[2]}")
        else:
            non_priority.append(variant)

    return priority, non_priority


def truncate_text(text: str, max_len: int) -> str:
    if len(text) > max_len:
        return text[:max_len-3] + "..."
    else:
        return text