from backend.utils import run_command
import os
import json
from backend import logger
from backend.classes.lib import Lib

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

        if os.path.exists("./settings/download/config_gallery-dl.json"):
            with open("./settings/download/config_gallery-dl.json", "r", encoding="utf-8") as f:
                params = json.load(f)

        if site in params and "proxy" in params[site]:
            log.debug(f"proxy: {params[site]['proxy']}")
            com = f' --proxy="{params[site]["proxy"]}"'
            command += com
        elif "proxy" in params["all"]:
            log.debug(f"proxy: {params['all']['proxy']}")
            com = f' --proxy="{params["all"]["proxy"]}"'
            command += com

        if site in params and "user-agent" in params[site]:
            log.debug(f"user-agent: {params[site]['user-agent']}")
            com = f' --user-agent="{params[site]["user-agent"]}"'
            command += com
        elif "user-agent" in params["all"]:
            log.debug(f"user-agent: {params['all']['user-agent']}")
            com = f' --user-agent="{params["all"]["user-agent"]}"'
            command += com

        if site in params and "cookies" in params[site]:
            if params[site]["cookies"] is not None and params[site]["cookies"] != "E:\\example\\cookies_file.txt":
                log.debug(f"cookies: {params[site]['cookies']}")
                com = f' --cookies="{params[site]["cookies"]}"'
                command += com

        command += f" {self.url}"
        self.command = command
        log.debug(f"command: {command}")

    async def start(self):
        log.debug("start")
        self.prepare()
        process = await run_command(self.command)

        return process
