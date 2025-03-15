from backend.utils import run_command
import os
import json
from backend.utils import logger
from backend.classes.lib import Lib
from backend.classes.dsettings import GalleryDLSettings

log = logger.get_logger("Downloader.gallerydl")


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
        output = os.path.abspath(self.lib.path)
        output += f"\\{self.id_}"
        command = f"gallery-dl --write-info-json --directory={output}"

        settings = GalleryDLSettings.load(site)

        if settings.proxy:
            command += f' --proxy="{settings.proxy}"'

        if settings.user_agent:
            command += f' --user-agent="{settings.user_agent}"'

        if settings.cookies:
            command += f' --cookies="{settings.cookies}"'

        command += f" {self.url}"
        self.command = command
        log.debug(f"command: {command}")

    async def start(self):
        log.debug("start")
        self.prepare()
        process = await run_command(self.command)

        return process
