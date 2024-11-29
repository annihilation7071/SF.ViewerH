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

        if "csrftoken" in params and\
            "sessionid" in params and\
            "cf_clearence" in params:
            com = f'nhentai --cookie="csrftoken={params["csrftoken"]}; sessionid={params["sessionid"]}; cf_clearence={params["cf_clearence"]}"'
            os.system(com)

        print(command)
        os.system(command)



