import json
import os
from backend import utils
from importlib import import_module
import asyncio
from icecream import ic

downloader_is_working = False


async def run_command(command: str):
    process = await asyncio.create_subprocess_shell(command)
    await process.wait()
    return process


async def download(url: str):
    ic()
    global downloader_is_working

    while downloader_is_working:
        await asyncio.sleep(2)

    downloader_is_working = True

    projects = import_module('backend.projects.cls').Projects()
    update_projects = import_module('backend.projects.putils').update_projects
    url, site, id_ = utils.separate_url(url)

    if os.path.exists("./settings/download/download_targets.json"):
        with open("./settings/download/download_targets.json", "r", encoding="utf-8") as f:
            targets = json.load(f)
    else:
        with open("./settings/download/download_targets_default.json", "r", encoding="utf-8") as f:
            targets = json.load(f)

    if site not in targets:
        print(f"Not found setting for {site} in download_targets.json")

    libs = utils.read_libs()

    if targets[site] not in libs:
        print(f"Not found lib for {site}")

    if site == "nhentai.net":
        if libs[targets[site]]["processor"] == "nhentai":
            output = os.path.abspath(libs[targets[site]]["path"])
            command = f"nhentai --download --id {id_} -o {output}"

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

            process = await run_command(command)

            if process.returncode == 0:
                ic()
                update_projects(projects)
            else:
                downloader_is_working = False
                raise RuntimeError(f"Command failed with return code: {process.returncode}")

            # result = subprocess.run(command, check=True, shell=True)
            # if result.returncode == 0:
            #     update_projects(projects)

        elif libs[targets[site]]["processor"] == "gallery-dl-nhentai":
            output = os.path.abspath(libs[targets[site]]["path"])
            output += f"\\{id_}"
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

            command += f" {url}"

            print(command)

            process = await run_command(command)

            if process.returncode == 0:
                ic()
                update_projects(projects)
            else:
                downloader_is_working = False
                raise RuntimeError(f"Command failed with return code: {process.returncode}")

            # result = subprocess.run(command, check=True, shell=True)
            # if result.returncode == 0:
            #     update_projects(projects)

    elif site == "hitomi.la":
        output = os.path.abspath(libs[targets[site]]["path"])

        output += f"\\{id_}"

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

        command += f" {url}"

        print(command)

        process = await run_command(command)

        if process.returncode == 0:
            ic()
            update_projects(projects)
        else:
            downloader_is_working = False
            raise RuntimeError(f"Command failed with return code: {process.returncode}")

    downloader_is_working = False
