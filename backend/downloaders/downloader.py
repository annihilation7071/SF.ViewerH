from backend.main_import import *
from .error import DownloaderError
from .nhentai import NHentaiDownloader
from .gallerydl import GalleryDLDownloader

log = logger.get_logger("Downloaders.downloader")

downloader_is_working = False


async def _download(url: str, projects: Projects):
    log.debug("_download")
    log.info(f"Downloading: {url}")

    global downloader_is_working

    while downloader_is_working:
        await asyncio.sleep(2)

    downloader_is_working = True

    url, site, id_ = utils.separate_url(url)

    targets = DownloadersTargets.load()
    targets_sites = targets.get_list_sites()
    log.debug(f"_download: targets_sites: {targets_sites}")

    if site not in targets_sites:
        raise DownloaderError(f"Not found setting for {site}")

    target: DownloaderTarget = targets[site]
    log.debug(f"_download: target: site: {target.site}: lib: {target.lib}")
    libs = Libs.load()
    libs_names = libs.get_names()
    log.debug(f"_download: libs: {libs}")

    if target.lib not in libs_names:
        log.exception(f"_download: target.site: {target.lib}")
        log.exception(f"_download: libs_names: {libs_names}")
        raise DownloaderError(f"Not found lib for {site}")

    lib = libs[target.lib]

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
