from backend.utils import run_command
import os
import json
from backend import logger
from backend.classes.lib import Lib

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
        if os.path.exists("./settings/download/config_nhentai.json"):
            with open("./settings/download/config_nhentai.json", "r", encoding="utf-8") as f:
                params = json.load(f)

        if "proxy" in params:
            log.debug(f"proxy: {params['proxy']}")
            com = f"nhentai --proxy={params['proxy']}"
            os.system(com)

        if "useragent" in params:
            log.debug(f"useragent: {params['useragent']}")
            com = f"nhentai --user-agent={params['useragent']}"
            os.system(com)

        if "csrftoken" in params and \
                "sessionid" in params and \
                "cf_clearance" in params:
            log.debug(f"csrftoken: {params['csrftoken']}")
            log.debug(f"sessionid: {params['sessionid']}")
            log.debug(f"cf_clearance: {params['cf_clearance']}")
            com = f'nhentai --cookie="csrftoken={params["csrftoken"]}; sessionid={params["sessionid"]}; cf_clearence={params["cf_clearance"]}"'
            os.system(com)

    async def start(self):
        log.debug("start")
        self.prepare()
        output = os.path.abspath(self.lib.path)
        command = f"nhentai --download --id {self.id_} -o {output}"
        process = await run_command(command)

        return process
