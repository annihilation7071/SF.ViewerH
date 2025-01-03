from backend.utils import run_command
import os
import json
from icecream import ic
ic.configureOutput(includeContext=True)


class NHentaiDownloader:
    def __init__(self, id_: int | str, target: dict):
        self.id_ = id_
        self.target = target
        self.command = None

    @staticmethod
    def prepare():
        if os.path.exists("./settings/download/config_nhentai.json"):
            with open("./settings/download/config_nhentai.json", "r", encoding="utf-8") as f:
                params = json.load(f)

        if "proxy" in params:
            ic()
            com = f"nhentai --proxy={params['proxy']}"
            os.system(com)

        if "useragent" in params:
            ic()
            com = f"nhentai --user-agent={params['useragent']}"
            os.system(com)

        if "csrftoken" in params and \
                "sessionid" in params and \
                "cf_clearance" in params:
            ic()
            com = f'nhentai --cookie="csrftoken={params["csrftoken"]}; sessionid={params["sessionid"]}; cf_clearence={params["cf_clearance"]}"'
            os.system(com)

    async def start(self):
        ic()
        self.prepare()
        output = os.path.abspath(self.target["path"])
        command = f"nhentai --download --id {self.id_} -o {output}"
        process = await run_command(command)

        return process
