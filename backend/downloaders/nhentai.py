from backend.main_import import *
from backend.user_data import Lib
from .error import DownloaderError

log = logger.get_logger("Downloaders.nhentai")


class NHentaiDownloader:
    def __init__(self, id_: int | str, lib: Lib):
        log.debug("NHentaiDownloader init")
        self.id_ = id_
        self.lib = lib
        self.command = None

    @staticmethod
    def prepare():
        log.debug("prepare")
        settings = DownloadersSettings.load().nhentai

        if settings.get_proxy():
            com = f"nhentai --proxy={settings.get_proxy()}"
            os.system(com)

        if settings.get_user_agent():
            com = f'nhentai --user-agent="{settings.get_user_agent()}"'
            os.system(com)

        if settings.get_cookies():
            com = f'nhentai --cookie="{settings.get_cookies()}"'
            os.system(com)

    async def start(self):
        log.debug("start")
        self.prepare()
        output = os.path.abspath(self.lib.path)
        command = f"nhentai --download --id {self.id_} -o {output} --meta"
        process = await utils.run_command(command)

        return process
