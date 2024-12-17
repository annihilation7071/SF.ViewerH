import json
import os

from backend import utils

allowed_sites = {
    "nhentai.net",
    "hitomi.la"
}


def download(url):
    separate_url = url.split('//')
    separate_url = [separate_url[0]] + separate_url[1].split('/')
    print(separate_url)
    protocol = separate_url[0]
    site = separate_url[1]
    address = separate_url[2:]
    if site not in allowed_sites:
        print(f"Site {site} not allowed")
        return

    with open("./settings/download/download_targets.json", "r", encoding="utf-8") as f:
        targets = json.load(f)

    if site not in targets:
        print(f"Not found setting for {site} in download_targets.json")

    libs = utils.read_libs()

    if targets[site] not in libs:
        print(f"Not found lib for {site}")

    if site == "nhentai.net":
        if libs[targets[site]]["processor"] == "nhentai":
            output = os.path.abspath(libs[targets[site]]["path"])
            command = f"nhentai --download --id {address[1]} -o {output}"

            if os.path.exists("./settings/download/config_nhentai.json"):
                with open("./settings/download/config_nhentai.json", "r", encoding="utf-8") as f:
                    params = json.load(f)

            if "proxy" in params:
                com = f"nhentai --proxy={params['proxy']}"
                os.system(com)

            if "useragent" in params:
                com = f"nhentai --user-agent={params['useragent']}"
                os.system(com)

            print(params)
            if "csrftoken" in params and \
                    "sessionid" in params and \
                    "cf_clearance" in params:
                com = f'nhentai --cookie="csrftoken={params["csrftoken"]}; sessionid={params["sessionid"]}; cf_clearence={params["cf_clearance"]}"'
                os.system(com)

            print(command)
            os.system(command)
        elif libs[targets[site]]["processor"] == "gallery-dl-nhentai":
            output = os.path.abspath(libs[targets[site]]["path"])
            _id: str = address[1]
            output += f"\\{_id}"
            command = f"gallery-dl --write-info-json --directory={output}"

            if os.path.exists("./settings/download/config_gallery-dl.json"):
                with open("./settings/download/config_gallery-dl.json", "r", encoding="utf-8") as f:
                    params = json.load(f)

            if "nhentai.net" in params and "proxy" in params["nhentai.net"]:
                com = f' --proxy="{params["nhentai.net"]["proxy"]}"'
                command += com
            elif "proxy" in params["all"]:
                com = f' --proxy="{params["all"]["proxy"]}"'
                command += com

            if "nhentai.net" in params and "user-agent" in params["nhentai.net"]:
                com = f' --user-agent="{params["nhentai.net"]["user-agent"]}"'
                command += com
            elif "user-agent" in params["all"]:
                com = f' --user-agent="{params["all"]["user-agent"]}"'
                command += com

            if "nhentai.net" in params and "cookies" in params["nhentai.net"]:
                if params["nhentai.net"]["cookies"] is not None and params["nhentai.net"]["cookies"] != "E:\\example\\cookies_file.txt":
                    com = f' --cookies="{params["nhentai.net"]["cookies"]}"'
                    command += com

            url = f"{protocol}//{site}/{address[0]}/{address[1]}.html"
            command += f" {url}"

            print(command)
            os.system(command)

    elif site == "hitomi.la":
        output = os.path.abspath(libs[targets[site]]["path"])

        _id: str = address[1][address[1].rfind("-") + 1:].replace('#1', '').replace(".html", "")

        output += f"\\{_id}"

        command = f"gallery-dl --write-info-json --directory={output}"

        if os.path.exists("./settings/download/config_gallery-dl.json"):
            with open("./settings/download/config_gallery-dl.json", "r", encoding="utf-8") as f:
                params = json.load(f)

        if "hitomi.la" in params and "proxy" in params["hitomi.la"]:
            com = f' --proxy="{params["hitomi.la"]["proxy"]}"'
            command += com
        elif "proxy" in params["all"]:
            com = f' --proxy="{params["all"]["proxy"]}"'
            command += com

        if "hitomi.la" in params and "user-agent" in params["hitomi.la"]:
            com = f' --user-agent="{params["hitomi.la"]["user-agent"]}"'
            command += com
        elif "user-agent" in params["all"]:
            com = f' --user-agent="{params["all"]["user-agent"]}"'
            command += com

        if "hitomi.la" in params and "cookies" in params["hitomi.la"]:
            if params["hitomi.la"]["cookies"] is not None and params["hitomi.la"]["cookies"] != "E:\\example\\cookies_file.txt":
                com = f' --cookies="{params["hitomi.la"]["cookies"]}"'
                command += com

        url = f"{protocol}//{site}/{address[0]}/{_id}.html"
        command += f" {url}"

        print(command)
        os.system(command)
