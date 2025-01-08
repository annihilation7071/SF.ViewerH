import json
import os
from backend import utils
import asyncio
from icecream import ic
from backend.downloaders.nhentai import NHentaiDownloader
from backend.downloaders.gallerydl import GalleryDLDownloader
from backend.projects.cls import Projects
from backend.projects.updater import update_projects
ic.configureOutput(includeContext=True)

downloader_is_working = False


# async def run_command(command: str):
#     process = await asyncio.create_subprocess_shell(command)
#     await process.wait()
#     return process


async def _download(url: str, projects: Projects):
    ic()
    global downloader_is_working

    while downloader_is_working:
        await asyncio.sleep(2)

    downloader_is_working = True

    url, site, id_ = utils.separate_url(url)

    if os.path.exists("./settings/download/download_targets.json"):
        with open("./settings/download/download_targets.json", "r", encoding="utf-8") as f:
            targets = json.load(f)
    else:
        with open("./settings/download/download_targets_default.json", "r", encoding="utf-8") as f:
            targets = json.load(f)

    if site not in targets:
        raise Exception(f"Not found setting for {site} in download_targets.json")

    libs = utils.read_libs()

    if targets[site] not in libs:
        raise Exception(f"Not found lib for {site}")

    target = targets[site]
    settings = getattr(libs, targets[site])

    match libs[targets[site]]["processor"]:

        case "nhentai":
            downloader = NHentaiDownloader(id_=id_, settings=settings)
            process = await downloader.start()

        case "gallery-dl-nhentai" | "gallery-dl-hitomila":
            downloader = GalleryDLDownloader(id_=id_,
                                             settings=settings,
                                             site=site,
                                             url=url)

            process = await downloader.start()

        case _:
            raise Exception(f"Unknown site: {site}")

    if process.returncode == 0:
        ic()
        update_projects(projects)
    else:
        downloader_is_working = False
        raise RuntimeError(f"Command failed with return code: {process.returncode}")

    downloader_is_working = False


async def download(url: str, projects: Projects):
    global downloader_is_working

    try:
        await _download(url, projects)
    finally:
        downloader_is_working = False


