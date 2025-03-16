import json
import os
from backend import dep
from backend import utils
import asyncio
from backend.downloaders.nhentai import NHentaiDownloader
from backend.downloaders.gallerydl import GalleryDLDownloader
from backend.downloaders.error import DownloaderError
from backend.projects.projects import Projects
# from backend.projects.projects_utils import update_projects
from backend import logger
from backend.classes.dsettings import NhentaiSettings, GalleryDLSettings
from backend import utils
from pathlib import Path

log = logger.get_logger("Downloader.main")

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

    targets = utils.read_json(Path("./settings/download/download_targets.json"))

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
            downloader = NHentaiDownloader(id_=id_,
                                           lib=lib)

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
        dep.projects.update_projects()
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
