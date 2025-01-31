from backend.utils import run_command
import os
import json
from backend.modules import logger
from backend.classes.lib import Lib
from backend.classes.dsettings import NhentaiSettings

log = logger.get_logger("Downloader.nhentai")


class NHentaiDownloader:
    def __init__(self, id_: int | str, lib: Lib):
        log.debug("NHentaiDownloader init")
        self.id_ = id_
        self.lib = lib
        self.command = None

    @staticmethod
    def prepare():
        log.debug("prepare")
        settings = NhentaiSettings.load()

        if settings.proxy:
            com = f"nhentai --proxy={settings.proxy}"
            os.system(com)

        if settings.user_agent:
            com = f"nhentai --user-agent={settings.user_agent}"
            os.system(com)

        if settings.cookies:
            com = f'nhentai --cookie="{settings.cookies}"'
            os.system(com)

    async def start(self):
        log.debug("start")
        self.prepare()
        output = os.path.abspath(self.lib.path)
        command = f"nhentai --download --id {self.id_} -o {output}"
        process = await run_command(command)

        return process
