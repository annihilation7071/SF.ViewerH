import json
import os
from backend import utils
import asyncio
from backend.downloaders.nhentai import NHentaiDownloader
from backend.downloaders.gallerydl import GalleryDLDownloader
from backend.downloaders.error import DownloaderError
from backend.projects.cls import Projects
from backend.projects.updater import update_projects
from backend.logger_new import get_logger

log = get_logger("Downloader")

downloader_is_working = False


# async def run_command(command: str):
#     process = await asyncio.create_subprocess_shell(command)
#     await process.wait()
#     return process


async def _download(url: str, projects: Projects):
    log.debug("_download")
    log.info(f"Downloading: {url}")

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
        raise DownloaderError(f"Not found setting for {site} in download_targets.json")

    libs = utils.read_libs()
    log.debug(f"libs: {libs.keys()}")

    if targets[site] not in libs:
        raise DownloaderError(f"Not found lib for {site}")

    target = targets[site]
    lib = libs[target]

    match lib.processor:

        case "nhentai":
            downloader = NHentaiDownloader(id_=id_, lib=lib)
            process = await downloader.start()

        case "gallery-dl-nhentai" | "gallery-dl-hitomila":
            downloader = GalleryDLDownloader(id_=id_,
                                             lib=lib,
                                             site=site,
                                             url=url)

            process = await downloader.start()

        case _:
            raise Exception(f"Unknown site: {site}")

    if process.returncode == 0:
        log.info(f"Download successful: {url}")
        update_projects(projects)
    else:
        downloader_is_working = False
        e = DownloaderError(f"Command failed with return code: {process.returncode}")
        log.exception(f"Download failed: {url}", exc_info=e)
        raise e

    downloader_is_working = False


async def download(url: str, projects: Projects):
    log.debug("download")
    global downloader_is_working

    try:
        await _download(url, projects)
    finally:
        downloader_is_working = False


