from backend.main_import import *
from backend.user_data import Lib
from .error import DownloaderError

log = logger.get_logger("Downloaders.gallerydl")


class GalleryDLDownloader:
    def __init__(self, id_: int | str, lib: Lib, site: str, url: str):
        self.command = None
        self.url = url
        self.id_ = id_
        self.lib = lib
        self.site = site

    def prepare(self):
        log.debug("prepare")
        site = self.site
        output = self.lib.path.absolute() / self.id_
        command = f"gallery-dl --write-info-json --directory={output}"

        settings = (
            DownloadersSettings.load()
            .get_gallery_dl_downloader_by_site_name(site)
        )

        if proxy := settings.get_proxy():
            log.debug(f"prepare: proxy: {proxy}")
            command += f' --proxy="{proxy}"'

        if user_agent := settings.get_user_agent():
            log.debug(f"prepare: user_agent: {user_agent}")
            command += f' --user-agent="{user_agent}"'

        if cookies := settings.get_cookies():
            log.debug(f"prepare: cookies: {cookies}")
            command += f' --cookies="{cookies}"'

        command += f" {self.url}"
        self.command = command
        log.debug(f"command: {command}")

    async def start(self):
        log.debug("start")
        self.prepare()
        process = await utils.run_command(self.command)

        return process
