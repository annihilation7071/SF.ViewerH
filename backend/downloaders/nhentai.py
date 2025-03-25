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

        if proxy := settings.get_proxy():
            log.debug(f"prepare: proxy: {proxy}")
            com = f"nhentai --proxy={settings.get_proxy()}"
            os.system(com)

        if user_agent := settings.get_user_agent():
            log.debug(f"prepare: user_agent: {user_agent}")
            com = f'nhentai --user-agent="{user_agent}"'
            os.system(com)

        if cookies := settings.get_cookies():
            log.debug(f"prepare: cookies: {cookies}")
            com = f'nhentai --cookie="{cookies}"'
            os.system(com)

    async def start(self):
        log.debug("start")
        self.prepare()
        output = self.lib.path.absolute()
        command = f"nhentai --download --id {self.id_} -o {output} --meta"
        process = await utils.run_command(command)

        return process
